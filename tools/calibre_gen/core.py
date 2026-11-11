"""
Core of the Calibre asset generator.

Everything is authored in GeckoLib *render space*, in millimetres:
  +X = right, +Y = up, +Z = back (towards the shooter); barrels point to -Z.
Rotations are in degrees and use the same convention GeckoLib's PoseStack uses
(Rz * Ry * Rx, right handed):
  +rx = muzzle up, +ry = muzzle left, +rz = cant left (top of gun to the left).

Conversion to the Bedrock/GeckoLib JSON conventions happens only at export time
(see GeckoLib BakedModelFactory / BakedAnimationsAdapter):
  geometry:  origin.x = -(x1)  pivot.x = -px   rot = (-rx, -ry, rz)
  animation: pos = (-x, y, z)  rot = (-rx, -ry, rz)
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

import numpy as np

MM = 0.1  # millimetres -> model units (1 unit = 1 cm, GeckoLib divides by 16)


def r6(v):
    return float(round(float(v), 4))


# ----------------------------------------------------------------------------------------------
# Math helpers
# ----------------------------------------------------------------------------------------------
def rot_x(a):
    a = math.radians(a)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)


def rot_y(a):
    a = math.radians(a)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)


def rot_z(a):
    a = math.radians(a)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def euler_mat(r):
    """GeckoLib order: mulPose(Z) then (Y) then (X) => M = Rz Ry Rx"""
    return rot_z(r[2]) @ rot_y(r[1]) @ rot_x(r[0])


def mat_euler(m):
    """Inverse of euler_mat (M = Rz Ry Rx). Returns degrees (rx, ry, rz)."""
    sy = -m[2, 0]
    sy = max(-1.0, min(1.0, sy))
    ry = math.asin(sy)
    if abs(sy) < 0.99999:
        rx = math.atan2(m[2, 1], m[2, 2])
        rz = math.atan2(m[1, 0], m[0, 0])
    else:
        rx = math.atan2(-m[1, 2], m[1, 1])
        rz = 0.0
    return np.degrees([rx, ry, rz])


def affine(rot3=None, trans=None):
    m = np.eye(4)
    if rot3 is not None:
        m[:3, :3] = rot3
    if trans is not None:
        m[:3, 3] = trans
    return m


def T(v):
    return affine(trans=np.asarray(v, dtype=float))


def S(v):
    m = np.eye(4)
    m[0, 0], m[1, 1], m[2, 2] = v
    return m


def lit(n_y):
    """Baked brightness of a facet from the vertical part of its normal: matches the flat-face table at the extremes
    (up 1.07, sides ~0.98, down 0.86), so a run of facets shades smoothly from a side face into a top face."""
    return 0.98 + (0.09 if n_y >= 0 else 0.12) * float(n_y)


# canonical frame of a shape that runs along one axis: (u, v, w) with w the long axis
_RP = {
    "z": np.eye(3),
    "y": np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float),     # u->x, v->-z, w->y
    "x": np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], dtype=float),     # u->-z, v->y, w->x
}
_CANON_FACE = {
    "z": {"+u": "east", "-u": "west", "+v": "up", "-v": "down", "+w": "south", "-w": "north"},
    "y": {"+u": "east", "-u": "west", "+v": "north", "-v": "south", "+w": "up", "-w": "down"},
    "x": {"+u": "north", "-u": "south", "+v": "up", "-v": "down", "+w": "east", "-w": "west"},
}


# ----------------------------------------------------------------------------------------------
# Geometry
# ----------------------------------------------------------------------------------------------
@dataclass
class Cube:
    x0: float
    y0: float
    z0: float
    x1: float
    y1: float
    z1: float
    mat: str
    rot: tuple = (0.0, 0.0, 0.0)
    pivot: tuple | None = None
    inflate: float = 0.0
    uv: dict = field(default_factory=dict)
    # faces painted without the bevel outline (polygon end caps, the inner pieces of tapered shapes)
    plain: tuple = ()
    # faces buried inside a compound shape (the wide faces of polygon slabs): packed as one texel, so they cost no atlas
    hidden: tuple = ()
    # baked brightness per face for facets of curved shapes (by their true normal), overriding the per-face table
    light: dict = field(default_factory=dict)

    @property
    def size(self):
        return (self.x1 - self.x0, self.y1 - self.y0, self.z1 - self.z0)

    @property
    def center(self):
        return ((self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2, (self.z0 + self.z1) / 2)


class Bone:
    def __init__(self, model, name, parent=None, pivot=(0, 0, 0), rot=(0, 0, 0)):
        self.model = model
        self.name = name
        self.parent = parent
        self.pivot = tuple(float(v) for v in pivot)
        self.rot = tuple(float(v) for v in rot)
        self.cubes: list[Cube] = []
        self.children: list[Bone] = []

    # -- hierarchy --
    def bone(self, name, pivot=None, rot=(0, 0, 0)):
        if pivot is None:
            pivot = self.pivot
        return self.model._add_bone(name, self, pivot, rot)

    # -- primitives (mm, render space) --
    def box(self, x0, x1, y0, y1, z0, z1, mat, rot=None, pivot=None, inflate=0.0):
        xa, xb = sorted((x0, x1))
        ya, yb = sorted((y0, y1))
        za, zb = sorted((z0, z1))
        c = Cube(xa, ya, za, xb, yb, zb, mat, tuple(rot) if rot else (0, 0, 0),
                 tuple(pivot) if pivot else None, inflate)
        self.cubes.append(c)
        return c

    def bc(self, c, s, mat, rot=None, pivot=None, inflate=0.0):
        """Box from centre + size."""
        x, y, z = c
        w, h, d = s
        return self.box(x - w / 2, x + w / 2, y - h / 2, y + h / 2, z - d / 2, z + d / 2, mat,
                        rot=rot, pivot=pivot if pivot else (c if rot else None), inflate=inflate)

    def cyl(self, c, d, length, mat, axis="z", sides=None, d2=None, steps=None):
        """
        Regular polygon prism with flat-to-flat diameter d. A 2n-gon is exactly the union of n rectangles of width d
        and thickness d*tan(pi/2n), each rotated by pi/n about the axis, so the silhouette is clean (no star points).
        The end caps of the pieces are inset by a hair so they never z-fight, and painted without outlines; the wide
        faces are buried inside the prism and take no atlas space.
        sides: None picks by size (octagon under 12 mm, 16-gon under 40 mm, 24-gon above); 8 / 16 / 24 force one.
        d2: diameter at the far (+axis) end -> a cone in `steps` stepped sections.
        """
        if d2 is not None and abs(d2 - d) > 0.5:
            out = []
            x, y, z = c
            steps = steps or max(3, min(8, int(abs(d2 - d) / 1.6) + 1))
            seg = length / steps
            for k in range(steps):
                dk = d + (d2 - d) * (k + 0.5) / steps
                off = -length / 2 + seg * (k + 0.5)
                ck = (x, y, z + off) if axis == "z" else ((x + off, y, z) if axis == "x" else (x, y + off, z))
                out += self.cyl(ck, dk, seg + 0.05, mat, axis=axis, sides=sides)
            return out
        auto = 8 if d < 7 else (16 if d < 16 else (24 if d < 34 else 32))
        if sides is None:
            sides = auto
        elif sides == 12:                       # callers that asked for "the round one" get as round as the size wants
            sides = max(16, auto)
        if d < 3.5 or sides <= 4:
            s = (d, d, length) if axis == "z" else ((length, d, d) if axis == "x" else (d, length, d))
            return [self.bc(c, s, mat)]
        n = 4 if sides <= 8 else (8 if sides <= 16 else (12 if sides <= 24 else 16))
        t = d * math.tan(math.pi / (2 * n))
        caps = {"z": ("north", "south"), "x": ("east", "west"), "y": ("up", "down")}[axis]
        inner = {"z": ("up", "down"), "x": ("up", "down"), "y": ("north", "south")}[axis]
        out = []
        for k in range(n):
            ang = 180.0 / n * k
            ln = max(0.2, length - 0.06 * k)
            sa, ca = math.sin(math.radians(ang)), math.cos(math.radians(ang))
            if axis == "z":
                s, r = (d, t, ln), (0, 0, ang)
                light = {"east": lit(sa), "west": lit(-sa)}
            elif axis == "x":
                s, r = (ln, t, d), (ang, 0, 0)
                light = {"south": lit(-sa), "north": lit(sa)}
            else:
                s, r = (d, ln, t), (0, ang, 0)
                light = {"east": 0.98 + 0.05 * ca, "west": 0.98 - 0.05 * ca}
            cube = self.bc(c, s, mat, rot=r if ang else None, pivot=c if ang else None)
            # a tube reads as one smooth surface: no outlines on the facets, each lit by its own normal
            cube.plain = FACES if n > 4 else caps
            cube.hidden = inner
            cube.light = light
            out.append(cube)
        return out

    def tube(self, c, d, length, mat, bore=None, axis="z", sides=None, ends="front"):
        """A cyl with a dark bore showing at one or both ends ('front' = the -axis end, 'back', 'both')."""
        out = self.cyl(c, d, length, mat, axis=axis, sides=sides)
        bd = bore or d * 0.55
        x, y, z = c
        for sgn, name in ((-1, "front"), (1, "back")):
            if ends not in (name, "both"):
                continue
            off = sgn * (length / 2 + 0.25)
            ck = (x, y, z + off) if axis == "z" else ((x + off, y, z) if axis == "x" else (x, y + off, z))
            out += self.cyl(ck, bd, 0.6, "rubber", axis=axis, sides=8 if bd < 12 else 16)
        return out

    def obox(self, c, size, R, mat):
        """Oriented box: centre c, size along its own axes, orientation matrix R."""
        x, y, z = (float(v) for v in c)
        sx, sy, sz = size
        if np.allclose(R, np.eye(3), atol=1e-7):
            return self.box(x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2, mat)
        rot = tuple(float(v) for v in mat_euler(R))
        return self.box(x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2, mat, rot=rot,
                        pivot=(x, y, z))

    def rbox(self, x0, x1, y0, y1, z0, z1, mat, r=3.0, axis="z", edges="all", rot=None, pivot=None, facets=None):
        """
        Box with rounded long edges: the four edges that run along `axis`. edges: 'all', 'top' / 'hi' (the two on the
        high side of the shape's v axis: +Y for axis z or x, the front for axis y) or 'bottom' / 'lo'.
        Each rounded corner is a fan of flat facets tangent to the fillet, lit by their own normals and painted without
        outlines, over a buried filler. rot / pivot tilt the whole shape (a raked grip, a sloped comb).
        """
        xa, xb = sorted((x0, x1))
        ya, yb = sorted((y0, y1))
        za, zb = sorted((z0, z1))
        if axis == "z":
            U, V, W = (xa, xb), (ya, yb), (za, zb)
        elif axis == "y":
            U, V, W = (xa, xb), (-zb, -za), (ya, yb)
        else:
            U, V, W = (-zb, -za), (ya, yb), (xa, xb)
        r = min(r, (U[1] - U[0]) / 2 - 0.2, (V[1] - V[0]) / 2 - 0.2)
        Ro = euler_mat(rot) if rot else np.eye(3)
        piv = np.asarray(pivot if pivot else ((xa + xb) / 2, (ya + yb) / 2, (za + zb) / 2), dtype=float)
        Rp = _RP[axis]
        fn = _CANON_FACE[axis]

        def plain_box(u0, u1, v0, v1, w0, w1):
            if axis == "z":
                e = (u0, u1, v0, v1, w0, w1)
            elif axis == "y":
                e = (u0, u1, w0, w1, -v1, -v0)
            else:
                e = (w0, w1, v0, v1, -u1, -u0)
            return self.box(*e, mat, rot=rot, pivot=tuple(piv) if rot else None)

        if r < 0.8:
            return [plain_box(U[0], U[1], V[0], V[1], W[0], W[1])]
        hi = edges in ("all", "top", "hi")
        lo = edges in ("all", "bottom", "lo")
        k = facets or (1 if r < 2.2 else (2 if r < 4.5 else 3))
        wide = plain_box(U[0], U[1], V[0] + (r if lo else 0), V[1] - (r if hi else 0), W[0], W[1])
        narrow = plain_box(U[0] + r, U[1] - r, V[0], V[1], W[0] + 0.03, W[1] - 0.03)
        wide.hidden = ((fn["+v"],) if hi else ()) + ((fn["-v"],) if lo else ())
        narrow.hidden = (fn["+u"], fn["-u"])
        narrow.plain = (fn["+u"], fn["-u"], fn["+w"], fn["-w"])
        out = [wide, narrow]
        delta = 45.0 / k
        rr = r * math.cos(math.radians(delta)) if k > 1 else r / math.sqrt(2)
        wt = 2 * rr * math.tan(math.radians(delta)) + (0.3 if k > 1 else 0.0)
        th = 0.42 * r if k > 1 else r / math.sqrt(2)
        Lw = W[1] - W[0] - 0.12
        wc = (W[0] + W[1]) / 2
        corners = ([(1, 1), (-1, 1)] if hi else []) + ([(1, -1), (-1, -1)] if lo else [])
        for su, sv in corners:
            cu = (U[1] - r) if su > 0 else (U[0] + r)
            cv = (V[1] - r) if sv > 0 else (V[0] + r)
            if k > 1:                                           # buried filler under the fan
                f = plain_box(*sorted((cu - su * 0.3, cu + su * 0.68 * r)), *sorted((cv - sv * 0.3, cv + sv * 0.68 * r)),
                              W[0] + 0.05, W[1] - 0.05)
                f.plain = FACES
                f.hidden = tuple(x for x in FACES if x not in (fn["+w"], fn["-w"]))
                out.append(f)
            for i in range(k):
                th_deg = (i + 0.5) * 90.0 / k
                ct, st = math.cos(math.radians(th_deg)), math.sin(math.radians(th_deg))
                n = np.array([su * ct, sv * st, 0.0])
                T = np.array([cu, cv, wc]) + rr * n
                cen = T - n * th / 2
                phi = -su * sv * (90.0 - th_deg)
                R = Ro @ Rp @ rot_z(phi)
                cw = piv + Ro @ (Rp @ cen - piv)
                cube = self.obox(cw, (wt, th, Lw), R, mat)
                outer = "up" if sv > 0 else "down"
                cube.plain = FACES
                cube.hidden = tuple(x for x in FACES if x not in (outer, "north", "south"))
                nw = R @ np.array([0.0, 1.0 if sv > 0 else -1.0, 0.0])
                cube.light = {outer: lit(nw[1])}
                out.append(cube)
        return out

    def chamfer_box(self, x0, x1, y0, y1, z0, z1, mat, ch=3.0, edges="top"):
        """A box running along Z with its long top and / or bottom edges rounded over (see rbox)."""
        return self.rbox(x0, x1, y0, y1, z0, z1, mat, r=ch, axis="z", edges=edges)

    def path(self, pts, width, thick, mat, x=0.0, overlap=0.6):
        """
        A bar bent along a polyline in the side (z, y) plane: pts = [(z, y), ...], `width` across X, `thick` in the
        plane. One box per span, turned to follow it and overlapped a little at the joints: trigger guards, lever
        loops, wire stocks, curved backstraps, sling loops.
        """
        out = []
        for (z0, y0), (z1, y1) in zip(pts, pts[1:]):
            L = math.hypot(z1 - z0, y1 - y0)
            if L < 0.2:
                continue
            mz, my = (z0 + z1) / 2, (y0 + y1) / 2
            ang = math.degrees(math.atan2(-(y1 - y0), z1 - z0))
            flat = abs(ang) < 0.01 or abs(abs(ang) - 180) < 0.01
            out.append(self.box(x - width / 2, x + width / 2, my - thick / 2, my + thick / 2,
                                mz - L / 2 - overlap, mz + L / 2 + overlap, mat,
                                rot=None if flat else (ang, 0, 0), pivot=None if flat else (x, my, mz)))
        return out

    def profile(self, x0, x1, top, bot, mat):
        """
        Side silhouette extruded across X: `top` and `bot` are polylines [(z, y), ...] over the same z range (z
        ascending). Each span between breakpoints becomes a `taper`, so stocks, grips and receivers follow the real
        outline instead of one straight wedge.
        """
        def at(line, z):
            for (za, ya), (zb, yb) in zip(line, line[1:]):
                if za - 1e-6 <= z <= zb + 1e-6:
                    return ya + (yb - ya) * (z - za) / max(1e-6, zb - za)
            return line[-1][1] if z > line[-1][0] else line[0][1]

        zs = sorted({round(z, 3) for z, _ in top} | {round(z, 3) for z, _ in bot})
        out = []
        for za, zb in zip(zs, zs[1:]):
            if zb - za < 0.5:
                continue
            out += self.taper(x0, x1, za, zb, at(top, za), at(top, zb), at(bot, za), at(bot, zb), mat)
        return out

    def taper(self, x0, x1, z0, z1, top0, top1, bot0, bot1, mat, plain=True, round=None):
        """
        A solid whose side profile is a trapezoid: top edge from (z0, top0) to (z1, top1), bottom edge from (z0, bot0)
        to (z1, bot1), vertical front/back. Built from a slab along each edge plus axis-aligned fillers, so stocks,
        butts and handguards get straight sloped lines instead of stair steps.
        """
        L = z1 - z0
        a_top = math.degrees(math.atan2(top0 - top1, L))      # positive x-rotation drops the +z end
        a_bot = math.degrees(math.atan2(bot0 - bot1, L))
        h_min = min(top0 - bot0, top1 - bot1)
        # thin edge slabs: a thick slab's square end pokes past the vertical end of a steep taper
        tt = tb = min(7.0, max(2.0, h_min * 0.5 + 0.5))
        lt = L / math.cos(math.radians(a_top))
        lb = L / math.cos(math.radians(a_bot))
        xa, xb = sorted((x0, x1))
        x0, x1 = xa, xb
        rd = round
        if rd is None:                       # stocks, butts and fore-ends get their long edges rounded over
            rd = min(4.5, (x1 - x0) * 0.2, h_min * 0.3) if (x1 - x0) >= 14 else 0.0
        rd = min(rd, tt - 1.5)
        if rd < 1.5:
            rd = 0.0
        cubes = []
        c = self.box(x0 + rd, x1 - rd, top0 - tt, top0, z0, z0 + lt, mat, rot=(a_top, 0, 0), pivot=(0, top0, z0))
        cubes.append(c)
        c = self.box(x0 + 0.15 + rd, x1 - 0.15 - rd, bot0, bot0 + tb, z0, z0 + lb, mat, rot=(a_bot, 0, 0),
                     pivot=(0, bot0, z0))
        cubes.append(c)
        if rd:
            k = 2
            delta = 45.0 / k
            rr = rd * math.cos(math.radians(delta))
            wt = 2 * rr * math.tan(math.radians(delta)) + 0.3
            th = 0.42 * rd
            for sv, y_edge, ang, ln, tk in ((1, top0, a_top, lt, tt), (-1, bot0, a_bot, lb, tb)):
                P = np.array([0.0, y_edge, z0])
                Rx_ = rot_x(ang)
                inset = 0.0 if sv > 0 else 0.15
                # the full-width slab, set back by the fillet radius
                ys = sorted((y_edge - sv * tk, y_edge - sv * rd))
                c = self.box(x0 + inset, x1 - inset, ys[0], ys[1], z0, z0 + ln, mat, rot=(ang, 0, 0), pivot=tuple(P))
                cubes.append(c)
                for su in (1, -1):
                    cu = (x1 - inset - rd) if su > 0 else (x0 + inset + rd)
                    cv = y_edge - sv * rd
                    fu = sorted((cu - su * 0.3, cu + su * 0.68 * rd))
                    fv = sorted((cv - sv * 0.3, cv + sv * 0.68 * rd))
                    f = self.box(fu[0], fu[1], fv[0], fv[1], z0 + 0.05, z0 + ln - 0.05, mat, rot=(ang, 0, 0),
                                 pivot=tuple(P))
                    f.hidden = ("up", "down", "east", "west")
                    cubes.append(f)
                    for i in range(k):
                        th_deg = (i + 0.5) * 90.0 / k
                        ct, st = math.cos(math.radians(th_deg)), math.sin(math.radians(th_deg))
                        n = np.array([su * ct, sv * st, 0.0])
                        cen = np.array([cu, cv, z0 + ln / 2]) + rr * n - n * th / 2
                        phi = -su * sv * (90.0 - th_deg)
                        R = Rx_ @ rot_z(phi)
                        cw = P + Rx_ @ (cen - P)
                        cube = self.obox(cw, (wt, th, ln - 0.12), R, mat)
                        outer = "up" if sv > 0 else "down"
                        cube.hidden = tuple(x for x in FACES if x not in (outer, "north", "south"))
                        nw = R @ np.array([0.0, float(sv), 0.0])
                        cube.light = {outer: lit(nw[1])}
                        cubes.append(cube)

        def top(z):
            return top0 + (top1 - top0) * (z - z0) / L

        def bot(z):
            return bot0 + (bot1 - bot0) * (z - z0) / L

        # fill the gap between the two slabs where the shape gets taller than tt + tb
        steps = 48
        zs = [z0 + L * i / steps for i in range(steps + 1)]
        i = 0
        while i < steps:
            z = zs[i]
            if top(z) - tt <= bot(z) + tb + 0.2 and top(zs[i + 1]) - tt <= bot(zs[i + 1]) + tb + 0.2:
                i += 1
                continue
            j = i + 1
            best = None
            while j <= steps:
                seg = zs[i:j + 1]
                lo_need = max(top(q) - tt for q in seg)             # filler must reach up to here
                hi_need = min(bot(q) + tb for q in seg)             # and down to here
                lo_ok = max(bot(q) for q in seg) + 0.2 + rd         # without poking out below
                hi_ok = min(top(q) for q in seg) - 0.2 - rd         # or above (or through the rounded edges)
                y0, y1 = max(lo_ok, hi_need - 0.5), min(hi_ok, lo_need + 0.5)
                if y1 - y0 < 0.5 or y0 > hi_need or y1 < lo_need:
                    break
                best = (seg[0], seg[-1], y0, y1)
                j += 1
            if best is None:
                i += 1
                continue
            za, zb, y0, y1 = best
            cubes.append(self.box(x0 + 0.3, x1 - 0.3, y0, y1, za, zb, mat))
            i = max(i + 1, j - 1)
        if plain:
            # keep the outline only along the silhouette (top of the top slab, underside of the bottom slab), so the
            # pieces read as one smooth part
            for q in cubes:
                q.plain = FACES
            cubes[0].plain = tuple(f for f in FACES if f != "up")
            cubes[1].plain = tuple(f for f in FACES if f != "down")
        return cubes

    def rail(self, z0, z1, y, x=0.0, width=21.0, mat="steel_dark", side="top", slots=True):
        """Picatinny rail. side: top/bottom/left/right. y is the rail base surface."""
        z0, z1 = sorted((z0, z1))
        h = 3.0
        if side == "top":
            self.box(x - width / 2, x + width / 2, y, y + h, z0, z1, mat)
            if slots:
                z = z0 + 2.5
                while z + 5.2 < z1:
                    self.box(x - width / 2 - 0.4, x + width / 2 + 0.4, y + h, y + h + 2.2, z, z + 5.2, mat)
                    z += 10.0
        elif side == "bottom":
            self.box(x - width / 2, x + width / 2, y - h, y, z0, z1, mat)
            if slots:
                z = z0 + 2.5
                while z + 5.2 < z1:
                    self.box(x - width / 2 - 0.4, x + width / 2 + 0.4, y - h - 2.2, y - h, z, z + 5.2, mat)
                    z += 10.0
        else:
            sgn = 1 if side == "right" else -1
            xs = x + sgn * h
            self.box(x, xs, y - width / 2, y + width / 2, z0, z1, mat)
            if slots:
                z = z0 + 2.5
                while z + 5.2 < z1:
                    self.box(xs, xs + sgn * 2.2, y - width / 2 - 0.4, y + width / 2 + 0.4, z, z + 5.2, mat)
                    z += 10.0

    def round_(self, c, length, d, case="brass", tip="copper", axis="z", detail=2):
        """
        A cartridge lying along -Z (bullet forward), centred on c. Long thin cartridges are bottlenecked (shoulder +
        neck), short ones straight-walled. detail 2 adds the rim, extractor groove and primer; detail 1 is for
        belts and stacks where dozens are visible.
        """
        x, y, z = c
        bottleneck = length / d > 3.6
        zb = z + length / 2                                   # case head
        if bottleneck:
            body = length * 0.52
            sh = length * 0.06
            neck = length * 0.1
            self.cyl((x, y, zb - body / 2), d, body, case, sides=8)
            self.cyl((x, y, zb - body - sh / 2), d * 0.84, sh + 0.05, case, sides=8)
            self.cyl((x, y, zb - body - sh - neck / 2), d * 0.68, neck + 0.05, case, sides=8)
            b0 = zb - body - sh - neck
            bl = length - body - sh - neck
            bd = d * 0.62
        else:
            body = length * 0.62
            self.cyl((x, y, zb - body / 2), d, body, case, sides=8)
            b0 = zb - body
            bl = length - body
            bd = d * 0.9
        self.cyl((x, y, b0 - bl * 0.3), bd, bl * 0.6 + 0.05, tip, sides=8)          # bullet shank
        self.cyl((x, y, b0 - bl * 0.8), bd * 0.62, bl * 0.4, tip, sides=8)          # ogive
        if detail >= 2:
            self.cyl((x, y, zb - 0.35), d * 1.06 if not bottleneck else d, 0.9, case, sides=8)    # rim
            self.cyl((x, y, zb + 0.2), d * 0.42, 0.5, "steel_light", sides=8)                      # primer

    def shell12(self, c, length=70.0, d=19.0):
        x, y, z = c
        self.cyl((x, y, z), d, length * 0.8, "shell_red", sides=8)
        self.cyl((x, y, z + length * 0.4), d + 1, length * 0.2, "brass", sides=8)
        self.cyl((x, y, z + length * 0.5 - 0.2), d + 2, 1.2, "brass", sides=8)                       # rim
        self.cyl((x, y, z + length * 0.5 + 0.5), d * 0.3, 0.5, "steel_light", sides=8)              # primer
        self.cyl((x, y, z - length * 0.4 - 0.3), d * 0.7, 0.6, "rubber", sides=8)                   # crimp


class Model:
    def __init__(self, name):
        self.name = name
        self.bones: dict[str, Bone] = {}
        self.order: list[Bone] = []
        self.root = self._add_bone("root", None, (0, 0, 0), (0, 0, 0))
        self.meta: dict = {}
        # how small controls move when worked: bone -> {"pos": .., "rot": ..} (see common.moving / auto_moving_parts)
        self.moves: dict = {}
        self.tex_w = 0
        self.tex_h = 0

    def _add_bone(self, name, parent, pivot, rot):
        if name in self.bones:
            raise ValueError(f"{self.name}: duplicate bone {name}")
        b = Bone(self, name, parent, pivot, rot)
        if parent:
            parent.children.append(b)
        self.bones[name] = b
        self.order.append(b)
        return b

    def __getitem__(self, item) -> Bone:
        return self.bones[item]

    def has(self, name):
        return name in self.bones

    # ------------------------------------------------------------------------------------------
    def rest_matrix(self, bone_name, pose=None):
        """4x4 bone matrix (render space, mm) for a pose dict {bone: (pos, rot, scale)}"""
        chain = []
        b = self.bones[bone_name]
        while b:
            chain.append(b)
            b = b.parent
        m = np.eye(4)
        for b in reversed(chain):
            m = m @ bone_local_matrix(b, pose.get(b.name) if pose else None)
        return m

    def socket(self, name):
        """Rest position of a bone pivot in render space (mm)"""
        m = self.rest_matrix(name)
        p = m @ np.array([*self.bones[name].pivot, 1.0])
        return [r6(v) for v in p[:3]]

    def warp_z(self, pts):
        """
        Re-proportion the finished model along the bore: pts = [(z_old, z_new), ...] is a piecewise-linear map
        (slope 1 outside the outer points). Straight parts stretch; parts set at an angle (grips, curved magazines)
        move rigidly with their pivot. Bone pivots, sockets and the eye point follow. Call it last in a gun builder.
        """
        pts = sorted(pts)

        def f(z):
            if z <= pts[0][0]:
                return z + pts[0][1] - pts[0][0]
            if z >= pts[-1][0]:
                return z + pts[-1][1] - pts[-1][0]
            for (za, fa), (zb, fb) in zip(pts, pts[1:]):
                if za <= z <= zb:
                    return fa + (fb - fa) * (z - za) / (zb - za)

        for b in self.order:
            b.pivot = (b.pivot[0], b.pivot[1], f(b.pivot[2]))
            for c in b.cubes:
                if c.rot[0] or c.rot[1]:
                    pz = c.pivot[2] if c.pivot else c.center[2]
                    dz = f(pz) - pz
                    c.z0 += dz
                    c.z1 += dz
                    if c.pivot:
                        c.pivot = (c.pivot[0], c.pivot[1], c.pivot[2] + dz)
                else:
                    c.z0, c.z1 = sorted((f(c.z0), f(c.z1)))
                    if c.pivot:
                        c.pivot = (c.pivot[0], c.pivot[1], f(c.pivot[2]))
        for k in ("muzzle", "eject", "sight"):
            if k in self.meta:
                v = self.meta[k]
                self.meta[k] = [v[0], v[1], f(v[2])]
        io = self.meta.get("integral_optic")
        if io and "eye" in io:
            io["eye"] = [io["eye"][0], io["eye"][1], f(io["eye"][2])]
        return f

    def length(self, skip=()):
        """Overall length along the bore at rest (true corners, so raked grips and angled stocks count), ignoring the
        arms and the bones in `skip` (and their children)."""
        lo, hi = 1e9, -1e9
        for b in self.order:
            p, bad = b, False
            while p:
                if p.name.startswith("arm_") or p.name in skip:
                    bad = True
                p = p.parent
            if bad or not b.cubes:
                continue
            bm = self.rest_matrix(b.name)
            for c in b.cubes:
                cm = bm @ cube_matrix(c)
                for x in (c.x0, c.x1):
                    for y in (c.y0, c.y1):
                        for z in (c.z0, c.z1):
                            zz = float((cm @ np.array([x, y, z, 1.0]))[2])
                            lo, hi = min(lo, zz), max(hi, zz)
        return hi - lo

    def bounds(self):
        lo = np.array([1e9] * 3)
        hi = -lo
        for b in self.order:
            for c in b.cubes:
                lo = np.minimum(lo, [c.x0, c.y0, c.z0])
                hi = np.maximum(hi, [c.x1, c.y1, c.z1])
        return lo, hi


def bone_local_matrix(b: Bone, anim=None):
    pos = np.zeros(3)
    rot = np.array(b.rot, dtype=float)
    scl = np.ones(3)
    if anim is not None:
        p, r, s = anim
        pos = np.asarray(p, dtype=float)
        rot = rot + np.asarray(r, dtype=float)
        scl = np.asarray(s, dtype=float)
    piv = np.asarray(b.pivot)
    return T(pos) @ T(piv) @ affine(euler_mat(rot)) @ S(scl) @ T(-piv)


def cube_matrix(c: Cube):
    if not any(c.rot):
        return np.eye(4)
    piv = np.asarray(c.pivot if c.pivot else c.center, dtype=float)
    return T(piv) @ affine(euler_mat(c.rot)) @ T(-piv)


# ----------------------------------------------------------------------------------------------
# Texture packing + export
# ----------------------------------------------------------------------------------------------
FACES = ("north", "south", "east", "west", "up", "down")


def face_dims(c: Cube):
    sx, sy, sz = c.size
    return {
        "north": (sx, sy), "south": (sx, sy),
        "east": (sz, sy), "west": (sz, sy),
        "up": (sx, sz), "down": (sx, sz),
    }


def pack_uv(model: Model, density=1.0, max_size=2048):
    """Shelf-pack every face of every cube. Picks the highest texel density that fits. Buried faces take one texel."""
    faces = []
    for b in model.order:
        for c in b.cubes:
            for f, (w, h) in face_dims(c).items():
                faces.append((c, f, w, h))
    d = density
    while True:
        for width in (256, 512, 1024, 2048):
            if width > max_size:
                break
            rects = []
            for c, f, w, h in faces:
                if f in c.hidden:
                    rects.append((c, f, 1, 1))
                    continue
                pw = max(1, int(math.ceil(w * d - 1e-6)))
                ph = max(1, int(math.ceil(h * d - 1e-6)))
                rects.append((c, f, pw, ph))
            order = sorted(range(len(rects)), key=lambda i: (-rects[i][3], -rects[i][2]))
            x = y = shelf_h = 0
            placed = {}
            ok = True
            for i in order:
                c, f, pw, ph = rects[i]
                if pw > width:
                    ok = False
                    break
                if x + pw > width:
                    y += shelf_h
                    x = 0
                    shelf_h = 0
                placed[i] = (x, y)
                x += pw
                shelf_h = max(shelf_h, ph)
            total_h = y + shelf_h
            if ok and total_h <= width:
                h2 = 16
                while h2 < total_h:
                    h2 *= 2
                for i, (px, py) in placed.items():
                    c, f, pw, ph = rects[i]
                    c.uv[f] = (px, py, pw, ph)
                model.tex_w, model.tex_h = width, h2
                model.meta["texel_density"] = d
                return
        d *= 0.88


def export_geo(model: Model, path):
    bones = []
    for b in model.order:
        jb = {"name": b.name, "pivot": [r6(-b.pivot[0] * MM), r6(b.pivot[1] * MM), r6(b.pivot[2] * MM)]}
        if b.parent:
            jb["parent"] = b.parent.name
        if any(b.rot):
            jb["rotation"] = [r6(-b.rot[0]), r6(-b.rot[1]), r6(b.rot[2])]
        cubes = []
        for c in b.cubes:
            sx, sy, sz = c.size
            jc = {
                "origin": [r6(-c.x1 * MM), r6(c.y0 * MM), r6(c.z0 * MM)],
                "size": [r6(sx * MM), r6(sy * MM), r6(sz * MM)],
            }
            if any(c.rot):
                piv = c.pivot if c.pivot else c.center
                jc["pivot"] = [r6(-piv[0] * MM), r6(piv[1] * MM), r6(piv[2] * MM)]
                jc["rotation"] = [r6(-c.rot[0]), r6(-c.rot[1]), r6(c.rot[2])]
            if c.inflate:
                jc["inflate"] = r6(c.inflate * MM)
            uv = {}
            for f in FACES:
                u, v, w, h = c.uv[f]
                if f in ("up", "down"):
                    # Blockbench convention: up/down faces are stored flipped
                    uv[f] = {"uv": [u + w, v + h], "uv_size": [-w, -h]}
                else:
                    uv[f] = {"uv": [u, v], "uv_size": [w, h]}
            jc["uv"] = uv
            cubes.append(jc)
        if cubes:
            jb["cubes"] = cubes
        bones.append(jb)
    lo, hi = model.bounds()
    ext = float(max(np.max(np.abs(lo)), np.max(np.abs(hi)))) * MM / 16.0
    geo = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": f"geometry.calibre.{model.name}",
                "texture_width": model.tex_w,
                "texture_height": model.tex_h,
                "visible_bounds_width": math.ceil(ext * 2 + 2),
                "visible_bounds_height": math.ceil(ext * 2 + 2),
                "visible_bounds_offset": [0, 0, 0],
            },
            "bones": bones,
        }],
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(geo, fh, separators=(",", ":"))


# ----------------------------------------------------------------------------------------------
# Animation
# ----------------------------------------------------------------------------------------------
def _ease_fn(name):
    n = name.lower()
    pi = math.pi

    def back(t, s=1.70158):
        return t * t * ((s + 1) * t - s)

    def bounce_out(t):
        if t < 1 / 2.75:
            return 7.5625 * t * t
        if t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + .75
        if t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + .9375
        t -= 2.625 / 2.75
        return 7.5625 * t * t + .984375

    base = {
        "sine": lambda t: 1 - math.cos(t * pi / 2),
        "quad": lambda t: t * t,
        "cubic": lambda t: t ** 3,
        "quart": lambda t: t ** 4,
        "quint": lambda t: t ** 5,
        "expo": lambda t: 0 if t == 0 else 2 ** (10 * t - 10),
        "circ": lambda t: 1 - math.sqrt(max(0.0, 1 - t * t)),
        "back": back,
        "bounce": lambda t: 1 - bounce_out(1 - t),
    }
    if n in ("linear", "lin"):
        return lambda t: t
    if n == "step":
        return lambda t: 0.0 if t < 1 else 1.0
    if n == "smooth":
        return lambda t: t * t * (3 - 2 * t)
    if n == "smoother":
        return lambda t: t * t * t * (t * (t * 6 - 15) + 10)
    for prefix, mode in (("inout", "inout"), ("in", "in"), ("out", "out")):
        if n.startswith(prefix) and n[len(prefix):] in base:
            f = base[n[len(prefix):]]
            if mode == "in":
                return f
            if mode == "out":
                return lambda t, f=f: 1 - f(1 - t)
            return lambda t, f=f: f(2 * t) / 2 if t < 0.5 else 1 - f(2 - 2 * t) / 2
    raise ValueError(f"unknown ease {name}")


_EASE_CACHE = {}


def ease(name, t):
    f = _EASE_CACHE.get(name)
    if f is None:
        f = _EASE_CACHE[name] = _ease_fn(name)
    return f(min(1.0, max(0.0, t)))


HOLD = object()
CHANNELS = ("pos", "rot", "scale")
DEFAULTS = {"pos": np.zeros(3), "rot": np.zeros(3), "scale": np.ones(3)}


class Track:
    def __init__(self, channel):
        self.channel = channel
        self.keys = []  # (t, value | HOLD, ease)

    def add(self, t, value, ease_name):
        # keep sorted; replace exact time
        for i, (kt, kv, _) in enumerate(self.keys):
            if abs(kt - t) < 1e-6:
                if value is HOLD and kv is not HOLD:
                    return   # "stay where you are" at the end of a move: keep that move's target
                self.keys[i] = (t, value, ease_name)
                return
        self.keys.append((t, value, ease_name))
        self.keys.sort(key=lambda k: k[0])


class Grab:
    """While active, `bone` keeps the relationship it had to `target` at time t0."""

    def __init__(self, bone, target, t0, t1, fade_in, fade_out):
        self.bone, self.target, self.t0, self.t1 = bone, target, t0, t1
        self.fade_in, self.fade_out = fade_in, fade_out
        self.rel = None
        self.solving = False

    def weight(self, t):
        if t < self.t0 - self.fade_in or t > self.t1 + self.fade_out:
            return 0.0
        if t < self.t0:
            return ease("inoutsine", (t - (self.t0 - self.fade_in)) / max(1e-6, self.fade_in))
        if t > self.t1:
            return 1.0 - ease("inoutsine", (t - self.t1) / max(1e-6, self.fade_out))
        return 1.0


class Anim:
    def __init__(self, model: Model, name, length, loop=False, rest=None):
        self.model = model
        self.name = name
        self.length = float(length)
        self.loop = loop
        self.tracks: dict[tuple[str, str], Track] = {}
        self.layers = []  # (bone, channel, fn(t)->vec3)
        self.grabs: list[Grab] = []
        self.sounds = []  # (t, sound)
        self.events = []  # (t, name)
        self.rest = rest or {}  # bone -> {"pos":..,"rot":..,"scale":..} default values for this anim
        self.hidden = set()  # bones hidden for the whole animation unless keyed
        self._memo = {}

    # ---------------- authoring ----------------
    def _track(self, bone, ch):
        if bone not in self.model.bones:
            raise KeyError(f"{self.model.name}/{self.name}: no bone {bone}")
        k = (bone, ch)
        if k not in self.tracks:
            self.tracks[k] = Track(ch)
        return self.tracks[k]

    def default(self, bone, ch):
        r = self.rest.get(bone, {})
        if ch in r:
            return np.asarray(r[ch], dtype=float)
        return DEFAULTS[ch]

    def key(self, bone, t, pos=None, rot=None, scale=None, e="inoutsine"):
        for ch, v in (("pos", pos), ("rot", rot), ("scale", scale)):
            if v is not None:
                if isinstance(v, (int, float)) and ch == "scale":
                    v = (v, v, v)
                self._track(bone, ch).add(t, np.asarray(v, dtype=float), e)
        return self

    def mv(self, bone, t0, t1, pos=None, rot=None, scale=None, e="inoutsine", rel=False):
        """Hold current value at t0, then ease to the target at t1."""
        for ch, v in (("pos", pos), ("rot", rot), ("scale", scale)):
            if v is None:
                continue
            if isinstance(v, (int, float)) and ch == "scale":
                v = (v, v, v)
            tr = self._track(bone, ch)
            tr.add(t0, HOLD, "linear")
            if rel:
                tr.add(t1, ("REL", np.asarray(v, dtype=float), t0), e)
            else:
                tr.add(t1, np.asarray(v, dtype=float), e)
        return self

    def to_rest(self, bone, t0, t1, e="inoutsine", channels=("pos", "rot")):
        for ch in channels:
            tr = self._track(bone, ch)
            tr.add(t0, HOLD, "linear")
            tr.add(t1, self.default(bone, ch), e)

    def hide(self, bone, t0=None, t1=None):
        """Scale a bone to 0 (optionally only between t0..t1)."""
        if t0 is None:
            self.hidden.add(bone)
            return
        tr = self._track(bone, "scale")
        tr.add(max(0.0, t0 - 1e-3), np.ones(3), "linear")
        tr.add(t0, np.zeros(3), "linear")
        tr.add(t1, np.zeros(3), "linear")
        tr.add(t1 + 1e-3, np.ones(3), "linear")

    def show(self, bone, t0, t1=None):
        """Bone is hidden except between t0 and t1."""
        tr = self._track(bone, "scale")
        tr.add(0.0, np.zeros(3), "linear")
        tr.add(max(0.0, t0 - 1e-3), np.zeros(3), "linear")
        tr.add(t0, np.ones(3), "linear")
        if t1 is not None:
            tr.add(t1, np.ones(3), "linear")
            tr.add(t1 + 1e-3, np.zeros(3), "linear")

    def spring(self, bone, ch, t0, impulse, freq=9.0, damp=7.0, dur=None):
        """Additive damped oscillation (follow-through / settle)."""
        imp = np.asarray(impulse, dtype=float)
        dur = dur if dur is not None else min(1.2, 6.0 / damp)

        def fn(t):
            if t < t0 or t > t0 + dur:
                return np.zeros(3)
            x = t - t0
            fade = 1.0 if x < dur * 0.7 else max(0.0, 1 - (x - dur * 0.7) / (dur * 0.3))
            return imp * math.exp(-damp * x) * math.sin(2 * math.pi * freq * x) * fade

        self.layers.append((bone, ch, fn))

    def kick(self, bone, ch, t0, amount, attack=0.03, recover=0.25, e_out="outcubic"):
        """Additive quick impulse + recovery (e.g. recoil)."""
        amt = np.asarray(amount, dtype=float)

        def fn(t):
            if t < t0 or t > t0 + attack + recover:
                return np.zeros(3)
            x = t - t0
            if x < attack:
                return amt * ease("outquad", x / attack)
            return amt * (1 - ease(e_out, (x - attack) / recover))

        self.layers.append((bone, ch, fn))

    def shake(self, bone, ch, t0, t1, amp, freq=14.0, seed=0):
        amp = np.asarray(amp, dtype=float)
        rng = np.random.default_rng(seed)
        ph = rng.uniform(0, 2 * math.pi, 3)
        fr = freq * rng.uniform(0.8, 1.25, 3)

        def fn(t):
            if t < t0 or t > t1:
                return np.zeros(3)
            env = math.sin(math.pi * (t - t0) / (t1 - t0))
            return amp * env * np.sin(2 * math.pi * fr * (t - t0) + ph)

        self.layers.append((bone, ch, fn))

    def wave(self, bone, ch, amp, period, phase=0.0):
        """Looping sine (idle breathing). Period should divide the animation length."""
        amp = np.asarray(amp, dtype=float)
        self.layers.append((bone, ch, lambda t: amp * math.sin(2 * math.pi * (t / period) + phase)))

    def grab(self, bone, target, t0, t1, fade_in=0.06, fade_out=0.06):
        self.grabs.append(Grab(bone, target, t0, t1, fade_in, fade_out))

    def at_hand(self, bone, t, hand="arm_left", grip=(0.0, 24.0, -28.0), rot=(0, 0, 0), e="linear"):
        """Key `bone` so that its pivot sits in `hand` at time t (grip = offset in the hand's parent space).
        Use it for items that arrive from the pouch, so a following grab keeps them in the fingers."""
        item = self.model.bones[bone]
        h = self.model.bones[hand]
        hm = self._free_pose_matrix(hand, t, use_final=False)
        hp = self._free_pose_matrix(h.parent.name, t, use_final=False) if h.parent else np.eye(4)
        world = hm @ np.array([*h.pivot, 1.0]) + hp @ np.array([*grip, 0.0])
        pm = self._free_pose_matrix(item.parent.name, t, use_final=False) if item.parent else np.eye(4)
        local = np.linalg.inv(pm) @ world
        pos = local[:3] - np.asarray(item.pivot)
        self.key(bone, t, pos=pos, rot=rot, e=e)
        self._memo.clear()
        return pos

    def pin(self, bone, t, e="inoutsine"):
        """Key the bone's current *final* (grab-resolved) pose at t, so it stays put once a grab lets go."""
        p = self._final_channel(bone, "pos", t)
        r = self._final_channel(bone, "rot", t)
        self.key(bone, t, pos=p, rot=r, e=e)
        self._memo.clear()
        return p, r

    def sound(self, t, name):
        self.sounds.append((round(t, 3), name))

    def event(self, t, name):
        self.events.append((round(t, 3), name))

    # ---------------- evaluation ----------------
    def _free(self, bone, ch, t):
        tr = self.tracks.get((bone, ch))
        base = self.default(bone, ch)
        if tr is None or not tr.keys:
            v = base
        else:
            keys = tr.keys
            if t <= keys[0][0]:
                v = self._resolve(bone, ch, 0, base)
            elif t >= keys[-1][0]:
                v = self._resolve(bone, ch, len(keys) - 1, base)
            else:
                i = 0
                while keys[i + 1][0] < t:
                    i += 1
                a = self._resolve(bone, ch, i, base)
                if keys[i + 1][1] is HOLD:
                    v = a  # a HOLD key means "stay where you are until here"
                else:
                    b = self._resolve(bone, ch, i + 1, base)
                    t0, t1 = keys[i][0], keys[i + 1][0]
                    u = (t - t0) / (t1 - t0) if t1 > t0 else 1.0
                    v = a + (b - a) * ease(keys[i + 1][2], u)
        for lb, lch, fn in self.layers:
            if lb == bone and lch == ch:
                v = v + fn(t)
        return v

    def _resolve(self, bone, ch, idx, base):
        key = ("res", bone, ch, idx)
        if key in self._memo:
            return self._memo[key]
        tr = self.tracks[(bone, ch)]
        t, v, _ = tr.keys[idx]
        if v is HOLD:
            if idx == 0:
                # value before the first key: rest, or constrained value
                out = self._final_channel(bone, ch, t - 1e-5, skip_track=True)
            else:
                out = self._final_channel(bone, ch, t - 1e-5)
        elif isinstance(v, tuple) and len(v) == 3 and isinstance(v[0], str) and v[0] == "REL":
            out = self._final_channel(bone, ch, v[2]) + v[1]
        else:
            out = v
        self._memo[key] = out
        return out

    def _final_channel(self, bone, ch, t, skip_track=False):
        if skip_track:
            v = self.default(bone, ch)
        else:
            v = self._free(bone, ch, t)
        if ch == "scale":
            return v
        grabs = [g for g in self.grabs if g.bone == bone and not g.solving and g.weight(t) > 0]
        if not grabs:
            return v
        p, r = self._constrained(grabs[0], t)
        w = grabs[0].weight(t)
        c = p if ch == "pos" else r
        if ch == "rot":
            # shortest-arc blend of euler components
            d = (c - v + 180) % 360 - 180
            return v + d * w
        return v + (c - v) * w

    def pose(self, t):
        """Final pose dict {bone: (pos, rot, scale)}"""
        out = {}
        for b in self.model.order:
            hidden = b.name in self.hidden and (b.name, "scale") not in self.tracks
            out[b.name] = (self._final_channel(b.name, "pos", t),
                           self._final_channel(b.name, "rot", t),
                           np.zeros(3) if hidden else self._final_channel(b.name, "scale", t))
        return out

    def _free_pose_matrix(self, bone_name, t, use_final=True):
        chain = []
        b = self.model.bones[bone_name]
        while b:
            chain.append(b)
            b = b.parent
        m = np.eye(4)
        for bb in reversed(chain):
            if use_final:
                anim = (self._final_channel(bb.name, "pos", t), self._final_channel(bb.name, "rot", t), np.ones(3))
            else:
                anim = (self._free(bb.name, "pos", t), self._free(bb.name, "rot", t), np.ones(3))
            m = m @ bone_local_matrix(bb, anim)
        return m

    def _constrained(self, g: Grab, t):
        key = ("con", id(g), round(t, 6))
        if key in self._memo:
            return self._memo[key]
        bone = self.model.bones[g.bone]
        if g.rel is None:
            # relationship at grab start, using the *free* follower and final target
            g.solving = True
            mt = self._free_pose_matrix(g.target, g.t0)
            pm = self._free_pose_matrix(bone.parent.name, g.t0) if bone.parent else np.eye(4)
            mf = pm @ bone_local_matrix(bone, (self._free(g.bone, "pos", g.t0), self._free(g.bone, "rot", g.t0), np.ones(3)))
            g.rel = np.linalg.inv(mt) @ mf
            g.solving = False
        tc = min(max(t, g.t0), g.t1)
        mt = self._free_pose_matrix(g.target, tc)
        desired = mt @ g.rel
        pm = self._free_pose_matrix(bone.parent.name, tc) if bone.parent else np.eye(4)
        local = np.linalg.inv(pm) @ desired
        # local = T(pos) T(piv) R T(-piv)  => translation = pos + piv - R piv
        rmat = local[:3, :3]
        piv = np.asarray(bone.pivot)
        pos = local[:3, 3] - piv + rmat @ piv
        rot = mat_euler(rmat) - np.asarray(bone.rot)
        self._memo[key] = (pos, rot)
        return pos, rot

    # ---------------- baking ----------------
    def bake(self, rate=120.0, tol_pos=0.12, tol_rot=0.15):
        n = max(2, int(round(self.length * rate)) + 1)
        times = np.linspace(0.0, self.length, n)
        animated = set(b for b, _ in self.tracks) | set(b for b, _, _ in self.layers) | set(g.bone for g in self.grabs) | self.hidden
        # bones with a rest override are animated too
        animated |= set(self.rest.keys())
        result = {}
        for bname in self.model.bones:
            if bname not in animated:
                continue
            chans = {}
            for ch in CHANNELS:
                has = (bname, ch) in self.tracks or any(l[0] == bname and l[1] == ch for l in self.layers) \
                      or (ch != "scale" and any(g.bone == bname for g in self.grabs)) \
                      or (ch in self.rest.get(bname, {})) or (ch == "scale" and bname in self.hidden)
                if not has:
                    continue
                if ch == "scale" and bname in self.hidden and (bname, ch) not in self.tracks:
                    chans[ch] = [(0.0, np.zeros(3), "linear")]
                    continue
                vals = np.array([self._final_channel(bname, ch, t) for t in times])
                tol = tol_rot if ch == "rot" else (tol_pos if ch == "pos" else 0.002)
                keep = rdp_keep(times, vals, tol)
                # step changes (show/hide) must stay exact: keep explicit step keys
                tr = self.tracks.get((bname, ch))
                frames = []
                if ch == "scale" and tr:
                    # scale tracks are authored with step semantics; export keys directly
                    for ki, (kt, kv, ke) in enumerate(tr.keys):
                        val = self._resolve(bname, ch, ki, self.default(bname, ch))
                        frames.append((kt, val, "linear"))
                elif ch == "rot" and _turn_shifts(vals)[1]:
                    frames = _wrapped_frames(times, vals, tol)
                else:
                    for i in keep:
                        frames.append((times[i], vals[i], "linear"))
                chans[ch] = frames
            result[bname] = chans
        return result

    def export_json(self):
        baked = self.bake()
        bones = {}
        for bname, chans in baked.items():
            jb = {}
            for ch, frames in chans.items():
                out_key = {"pos": "position", "rot": "rotation", "scale": "scale"}[ch]
                if len(frames) == 1 or all(np.allclose(frames[0][1], f[1], atol=1e-4) for f in frames):
                    v = frames[0][1]
                    jb[out_key] = conv_anim(ch, v)
                    continue
                kd = {}
                for (t, v, e) in frames:
                    entry = {"vector": conv_anim(ch, v)}
                    kd[f"{max(0.0, t):.4f}".rstrip("0").rstrip(".") or "0"] = entry
                jb[out_key] = kd
            bones[bname] = jb
        out = {"animation_length": r6(self.length), "bones": bones}
        if self.loop:
            out["loop"] = True
        if self.sounds:
            out["sound_effects"] = {f"{t:.3f}": {"effect": f"calibre:{s}"} for t, s in self.sounds}
        return out


def conv_anim(ch, v):
    if ch == "pos":
        return [r6(-v[0] * MM), r6(v[1] * MM), r6(v[2] * MM)]
    if ch == "rot":
        return [r6(-v[0]), r6(-v[1]), r6(v[2])]
    return [r6(v[0]), r6(v[1]), r6(v[2])]


TURN_GAP = 0.0002  # s between the two keys of a whole-turn switch


def _turn_shifts(vals):
    """Rotation axes that end on a whole turn (a spin flourish ending at -720 deg must not unwind into the next
    animation). Returns (shift array, split indices): from the half-way point of the spin on, the values are
    offset by the whole turn, which is the same orientation."""
    n = len(vals)
    shift = np.zeros_like(vals)
    splits = set()
    for ax in range(vals.shape[1]):
        end = vals[-1, ax]
        w = round(end / 360.0) * 360.0
        if w == 0 or abs(end - w) > 20.0:
            continue
        idx = np.nonzero(np.sign(w) * vals[:, ax] >= abs(w) / 2.0)[0]
        if not len(idx) or idx[0] == 0:
            continue
        j = int(idx[0])
        shift[j:, ax] = w
        splits.add(j)
    return shift, sorted(splits)


def _wrapped_frames(times, vals, tol):
    shift, splits = _turn_shifts(vals)
    bounds = [0, *splits, len(times) - 1]
    keep = set()
    for a, b in zip(bounds, bounds[1:]):
        if b > a:
            keep.update(a + k for k in rdp_keep(times[a:b + 1], vals[a:b + 1], tol))
    frames = []
    for i in sorted(keep):
        if i in splits:
            tj = round(float(times[i]), 4)
            frames.append((tj - TURN_GAP, vals[i] - shift[i - 1], "linear"))
            frames.append((tj, vals[i] - shift[i], "linear"))
        else:
            frames.append((times[i], vals[i] - shift[i], "linear"))
    return frames


def rdp_keep(times, vals, tol):
    """Ramer-Douglas-Peucker on a vector-valued curve; returns kept indices."""
    n = len(times)
    keep = {0, n - 1}
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        ta, tb = times[a], times[b]
        va, vb = vals[a], vals[b]
        seg = times[a + 1:b]
        u = ((seg - ta) / (tb - ta))[:, None]
        interp = va + (vb - va) * u
        err = np.max(np.abs(vals[a + 1:b] - interp), axis=1)
        i = int(np.argmax(err))
        if err[i] > tol:
            m = a + 1 + i
            keep.add(m)
            stack.append((a, m))
            stack.append((m, b))
    return sorted(keep)


def export_anims(model: Model, anims: list[Anim], path):
    data = {"format_version": "1.8.0", "animations": {}}
    for a in anims:
        data["animations"][f"animation.{model.name}.{a.name}"] = a.export_json()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(data, fh, separators=(",", ":"))
