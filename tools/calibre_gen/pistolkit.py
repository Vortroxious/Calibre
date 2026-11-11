"""
Building blocks for handguns (mm, bore axis at y=0, muzzle towards -Z).

Grip parts are authored upright in the grip's own frame and raked by `A` degrees about the grip pivot `gp`, the way
the magazine bone is, so a pistol's grip, straps, panels and magazine all share one angle.
"""
from __future__ import annotations

import math

from .core import Bone
from .parts import arc, serrations
from .common import moving


def raked(A, gp):
    return dict(rot=(A, 0, 0), pivot=gp)


# ------------------------------------------------------------------------------------------------
# frame
# ------------------------------------------------------------------------------------------------
def grip_frame(body: Bone, gp, A, hw, y_bot, z_f, z_b, mat, y_top=None, hump=0.0, flare=True, front="plain",
               back="plain", strap_mat=None):
    """Grip core with rounded front and back straps, optional palm hump, strap texture and a flared mag well."""
    r = raked(A, gp)
    yt = gp[1] if y_top is None else y_top
    H = yt - y_bot
    sm = strap_mat or mat
    body.box(-hw, hw, y_bot, yt, z_f + 2.2, z_b - 2.2, mat, **r)
    body.box(-hw + 2.6, hw - 2.6, y_bot, yt, z_f, z_f + 2.4, mat, **r)                 # rounded front strap
    body.box(-hw + 1.2, hw - 1.2, y_bot, yt, z_f + 1.0, z_f + 2.4, mat, **r)
    body.box(-hw + 2.6, hw - 2.6, y_bot, yt, z_b - 2.4, z_b, mat, **r)                 # rounded back strap
    body.box(-hw + 1.2, hw - 1.2, y_bot, yt, z_b - 2.4, z_b - 1.0, mat, **r)
    if hump:
        body.box(-hw + 3, hw - 3, y_bot + H * 0.08, y_bot + H * 0.5, z_b, z_b + hump, mat, **r)
        body.box(-hw + 3.6, hw - 3.6, y_bot + H * 0.18, y_bot + H * 0.4, z_b + hump, z_b + hump * 1.6, mat, **r)
    for where, z0, z1 in (("front", z_f - 0.5, z_f), ("back", z_b, z_b + 0.5)):
        style = front if where == "front" else back
        if style == "grooves":
            n = max(4, int(H // 12))
            for i in range(n):
                y = y_bot + 8 + i * (H - 22) / n
                body.box(-hw + 3.4, hw - 3.4, y, y + 3.2, z0, z1, sm, **r)
        elif style == "checker":
            n = max(4, int(H // 13))
            for i in range(n):
                y = y_bot + 8 + i * (H - 22) / n
                body.box(-hw + 3.4, hw - 3.4, y, y + 2.4, z0, z1, sm, **r)
            for x in (-hw * 0.4, 0, hw * 0.4):
                body.box(x - 1, x + 1, y_bot + 8, yt - 14, z0 - 0.02, z1 + 0.02, sm, **r)
        elif style == "finger":
            for i in range(2):
                y = yt - 30 - i * 26
                body.box(-hw + 2.6, hw - 2.6, y - 4, y, z_f - 2.6, z_f, mat, **r)
    if flare:
        body.box(-hw - 1.2, hw + 1.2, y_bot, y_bot + 5, z_f - 1.2, z_b + 1.6, mat, **r)
        body.box(-hw + 2, hw - 2, y_bot - 0.6, y_bot, z_f + 4, z_b - 4, "rubber", **r)        # mag well mouth


def grip_panels(body: Bone, gp, A, hw, y0, y1, z0, z1, mat, style="checker", proud=1.6, screws=True, line_mat=None,
                screw_mat="steel"):
    """
    Side panels on both sides of the grip. style: 'smooth' | 'checker' (raised grid) | 'diamond' (checkered with plain
    diamonds round the screws, 1911 style) | 'stipple' (rows of pips) | 'grooves' (horizontal bands).
    """
    r = raked(A, gp)
    lm = line_mat or mat
    H, D = y1 - y0, z1 - z0
    for sx in (-1, 1):
        xa, xb = sorted((sx * hw, sx * (hw + proud)))
        body.box(xa, xb, y0, y1, z0, z1, mat, **r)
        xs = sorted((sx * (hw + proud), sx * (hw + proud + 0.45)))
        if style in ("checker", "diamond"):
            n = max(4, int(H // 11))
            for i in range(n):
                y = y0 + 6 + i * (H - 12) / n
                body.box(xs[0], xs[1], y, y + 1.4, z0 + 3, z1 - 3, lm, **r)
            for k in range(1, 5):
                z = z0 + D * k / 5
                body.box(xs[0] - 0.02, xs[1] + 0.02, y0 + 6, y1 - 6, z - 0.7, z + 0.7, lm, **r)
        elif style == "stipple":
            ny, nz = max(3, int(H // 16)), 3
            for i in range(ny):
                for k in range(nz):
                    y = y0 + 6 + i * (H - 14) / (ny - 1 if ny > 1 else 1)
                    z = z0 + 5 + k * (D - 14) / (nz - 1)
                    body.box(xs[0], xs[1], y, y + 4, z, z + 4, lm, **r)
        elif style == "grooves":
            n = max(4, int(H // 12))
            for i in range(n):
                y = y0 + 5 + i * (H - 10) / n
                body.box(xs[0], xs[1], y, y + 3, z0 + 2, z1 - 2, lm, **r)
        if screws:
            pos = [(y0 + H * 0.2, z0 + D * 0.5), (y1 - H * 0.2, z0 + D * 0.5)]
            for y, z in pos:
                if style == "diamond":
                    c = _rk(gp, A, (0, y, z))
                    xd = sorted((sx * (hw + proud), sx * (hw + proud + 0.7)))
                    body.box(xd[0], xd[1], c[1] - 5, c[1] + 5, c[2] - 5, c[2] + 5, mat, rot=(A + 45, 0, 0),
                             pivot=(0, c[1], c[2]))
                xq = sorted((sx * (hw + proud), sx * (hw + proud + 0.9)))
                body.box(xq[0], xq[1], y - 2.6, y + 2.6, z - 2.6, z + 2.6, screw_mat, **r)
                xq = sorted((sx * (hw + proud + 0.9), sx * (hw + proud + 1.1)))
                body.box(xq[0], xq[1], y - 0.5, y + 0.5, z - 2.4, z + 2.4, "rubber", **r)


def _rk(gp, A, p):
    """Where a point of the upright grip frame ends up after the rake (used as the pivot of further-rotated pieces)."""
    a = math.radians(A)
    dy, dz = p[1] - gp[1], p[2] - gp[2]
    return (p[0], gp[1] + dy * math.cos(a) - dz * math.sin(a), gp[2] + dy * math.sin(a) + dz * math.cos(a))


def guard(body: Bone, zf, zr, y_top, y_bot, mat, w=7.0, th=3.6, style="round", y_rear=None):
    """
    Trigger guard as one bent bar from the frame at zf, round the trigger, back up to the grip at zr.
    style: 'round' | 'square' (flat front, tight corners) | 'hook' (square with a finger hook at the front).
    """
    yr = y_bot + (y_top - y_bot) * 0.45 if y_rear is None else y_rear
    if style == "round":
        c = min((y_top - y_bot) * 0.55, (zr - zf) * 0.3)
        pts = [(zf, y_top + 1)] + arc(zf + c, y_bot + c, c, c, 180, 270, 4)
        c2 = min(c, 8.0)
        pts += arc(zr - c2, y_bot + c2, c2, c2, 270, 340, 3) + [(zr + 1.5, yr)]
    else:
        c = 4.0
        pts = [(zf, y_top + 1)] + arc(zf + c, y_bot + c, c, c, 180, 270, 2)
        pts += arc(zr - 6, y_bot + 6, 6, 6, 270, 340, 2) + [(zr + 1.5, yr)]
    out = body.path(pts, w, th, mat)
    if style == "hook":
        body.box(-w / 2, w / 2, y_bot - th / 2, y_bot + 6, zf - 4.5, zf - 1, mat)
        for i in range(3):
            body.box(-w / 2 + 0.6, w / 2 - 0.6, y_top - 10 - i * 5, y_top - 8 - i * 5, zf - 2.4, zf - 1.8, "rubber")
    return out


# ------------------------------------------------------------------------------------------------
# slide
# ------------------------------------------------------------------------------------------------
def slide_shell(slide: Bone, zf, zr, y0, y1, hw, mat, ch=3.0, rib=True):
    """Slide body with bevelled top edges and a flat sighting rib."""
    slide.chamfer_box(-hw, hw, y0, y1, zf, zr, mat, ch=ch, edges="top")
    if rib:
        slide.box(-hw + ch + 1.2, hw - ch - 1.2, y1, y1 + 0.6, zf + 3, zr - 3, mat)


def port(slide: Bone, hw, y1, z0, z1, y_low, hood_mat="steel_light", extractor=True, bore_y=0.0):
    """Ejection port on the right wrapping over the top, with the barrel hood showing and the extractor behind it."""
    slide.box(-1.5, hw + 0.3, y_low, y1 + 0.75, z0, z1, "rubber")
    slide.box(0.5, hw - 2.6, y_low + 2.5, y1 + 0.5, z0 + 1.5, z1 - 3, hood_mat)             # barrel hood
    slide.box(2.5, hw - 4.5, y1 + 0.4, y1 + 0.9, z1 - 9, z1 - 5, "rubber")                   # loaded-chamber notch
    if extractor:
        slide.box(hw, hw + 0.7, y_low - 1.5, y_low + 2.5, z1 - 3, z1 + 17, "steel")
        slide.box(hw, hw + 0.9, y_low - 0.8, y_low + 1.8, z1 + 12, z1 + 15, "rubber")


def muzzle_face(slide: Bone, zf, d, y=0.0, rod_y=None, rod_d=6.0):
    """Barrel hole in the slide's front face, and the recoil-spring guide end under it."""
    slide.cyl((0, y, zf - 0.2), d + 2.4, 0.5, "rubber", sides=16)
    if rod_y is not None:
        slide.cyl((0, rod_y, zf - 0.25), rod_d + 1.6, 0.5, "rubber", sides=8)
        slide.cyl((0, rod_y, zf - 0.5), rod_d, 0.6, "steel", sides=8)


def rear_plate(slide: Bone, zr, hw, y0, y1, mat="polymer", pin=True):
    slide.box(-hw + 3.2, hw - 3.2, y0 + 2, y1 - 3.5, zr, zr + 0.8, mat)
    if pin:
        slide.box(-1.6, 1.6, (y0 + y1) / 2 - 1.6, (y0 + y1) / 2 + 1.6, zr + 0.8, zr + 1.2, "steel")


def sights(slide: Bone, z_front, z_rear, top, front_h=5.5, rear_h=6.0, style="dot", mat="steel_dark", rear_w=16.0,
           dot="sight_white", front_on=None, front_top=None):
    """
    Front blade (ramped at the back) + dovetailed rear with a square notch.
    style: 'dot' (3 dots) | 'plain' | 'outline' (dot front, U outline rear, Glock) | 'target' (taller adjustable rear).
    """
    fw = 3.4
    fb = front_on or slide                                # the front sight may sit on another part (a fixed barrel)
    ft = top if front_top is None else front_top
    fb.box(-fw / 2 - 1.8, fw / 2 + 1.8, ft, ft + 1.2, z_front - 1, z_front + 9, mat)                 # base
    fb.box(-fw / 2, fw / 2, ft + 1.2, ft + front_h, z_front, z_front + 5, mat)
    fb.box(-fw / 2, fw / 2, ft + 1.2, ft + front_h * 0.62, z_front + 5, z_front + 8, mat)            # ramp step
    hw = rear_w / 2
    zr0 = z_rear - 8
    slide.box(-hw, hw, top, top + rear_h * 0.42, zr0, z_rear, mat)                                   # dovetail body
    slide.box(-hw, -2.0, top + rear_h * 0.42, top + rear_h, zr0 + 1.5, z_rear, mat)                  # ears
    slide.box(2.0, hw, top + rear_h * 0.42, top + rear_h, zr0 + 1.5, z_rear, mat)
    slide.box(-hw + 1, hw - 1, top + rear_h * 0.42, top + rear_h * 0.7, zr0, zr0 + 1.5, mat)         # front slope
    if style == "target":
        slide.box(-hw - 1.5, hw + 1.5, top, top + 2.2, zr0 - 10, zr0, mat)                           # elevation base
        slide.box(-2, 2, top + 2.2, top + 3.2, zr0 - 7, zr0 - 3, "steel")                            # screw
        slide.box(hw, hw + 2.2, top + 2.5, top + rear_h - 0.5, z_rear - 6, z_rear - 1.5, "steel")    # windage screw
    if style in ("dot", "outline"):
        fb.box(-0.9, 0.9, ft + front_h - 2.6, ft + front_h - 0.9, z_front + 4.95, z_front + 5.15, dot)
    if style == "dot":
        for x in (-hw * 0.6, hw * 0.6):
            slide.box(x - 0.9, x + 0.9, top + rear_h - 2.9, top + rear_h - 1.2, z_rear - 0.05, z_rear + 0.15, dot)
    elif style == "outline":
        slide.box(-3.2, -2.2, top + rear_h * 0.45, top + rear_h - 0.6, z_rear - 0.05, z_rear + 0.15, dot)
        slide.box(2.2, 3.2, top + rear_h * 0.45, top + rear_h - 0.6, z_rear - 0.05, z_rear + 0.15, dot)
        slide.box(-3.2, 3.2, top + rear_h * 0.45 - 1, top + rear_h * 0.45, z_rear - 0.05, z_rear + 0.15, dot)


# ------------------------------------------------------------------------------------------------
# barrel, hammer, trigger, controls, magazine
# ------------------------------------------------------------------------------------------------
def barrel_assy(body: Bone, z_muzzle, z_breech, d=14.0, y=0.0, mat="steel_light", rod_y=-7.0, rod_len=None,
                chamber=True):
    """Static barrel with crown and bore, chamber block, and the guide rod with its recoil spring underneath."""
    b = body.bone("barrel", pivot=(0, y, z_breech))
    L = z_breech - z_muzzle
    b.cyl((0, y, z_muzzle + L / 2), d, L, mat)
    b.cyl((0, y, z_muzzle - 0.2), d * 0.8, 0.5, mat, sides=8)
    b.cyl((0, y, z_muzzle - 0.5), d * 0.48, 0.4, "rubber", sides=8)
    if chamber:
        b.box(-d / 2 - 0.6, d / 2 + 0.6, y - d / 2 - 2, y + d / 2 + 0.8, z_breech - 34, z_breech, mat)     # chamber block
        b.box(-d / 2 + 2, d / 2 - 2, y - d / 2 - 8, y - d / 2 - 2, z_breech - 30, z_breech - 14, mat)      # lower lug
    if rod_y is not None:
        rl = rod_len or L * 0.62
        b.cyl((0, rod_y, z_muzzle + 2 + rl / 2), 5.0, rl, "steel", sides=8)
        n = int(rl // 7)
        for i in range(n):
            z = z_muzzle + 5 + i * 7
            b.box(-3.8, 3.8, rod_y - 3.8, rod_y + 3.8, z, z + 1.6, "steel_dark")                            # spring coils
    return b


def hammer(body: Bone, pivot, mat="steel", style="spur", cocked=28.0, w=7.0):
    """`hammer` bone, drawn cocked (leaning back by `cocked` degrees). style: 'spur' | 'ring' | 'bobbed'."""
    h = body.bone("hammer", pivot=pivot)
    px, py, pz = pivot
    r = dict(rot=(cocked, 0, 0), pivot=pivot)
    h.box(-w / 2, w / 2, py - 5, py + 13, pz - 3, pz + 4, mat, **r)                         # body
    h.box(-w / 2 + 1, w / 2 - 1, py + 4, py + 12, pz - 4.2, pz - 3, "steel_dark", **r)       # striking face
    if style == "spur":
        h.box(-w / 2 - 0.6, w / 2 + 0.6, py + 10, py + 15, pz + 2, pz + 12, mat, **r)
        for i in range(3):
            h.box(-w / 2, w / 2, py + 15, py + 15.5, pz + 4 + i * 2.6, pz + 5.2 + i * 2.6, "steel_dark", **r)
    elif style == "ring":
        h.box(-w / 2, w / 2, py + 11, py + 14, pz + 1, pz + 13, mat, **r)
        h.box(-w / 2, w / 2, py + 3, py + 6, pz + 3, pz + 13, mat, **r)
        h.box(-w / 2, w / 2, py + 5, py + 12, pz + 10, pz + 13, mat, **r)
        h.box(-w / 2 + 0.8, w / 2 - 0.8, py + 6, py + 11, pz + 4.5, pz + 10, "rubber", **r)
    else:
        h.box(-w / 2, w / 2, py + 11, py + 14, pz + 1, pz + 7, mat, **r)
    return h


def trigger(body: Bone, pivot, mat="steel_dark", length=20.0, style="curved", safety_blade=False, w=6.0):
    """`trigger` bone: curved two-piece blade, or the straight sliding 1911 kind."""
    t = body.bone("trigger", pivot=pivot)
    px, py, pz = pivot
    if style == "straight":
        t.box(-w / 2, w / 2, py - length, py, pz - 4, pz + 3, mat)
        t.box(-w / 2 + 1, w / 2 - 1, py - length + 3, py - 3, pz - 4.5, pz - 4, "rubber")
        for i in range(3):
            t.box(-1.2, 1.2, py - length + 4 + i * 5, py - length + 7 + i * 5, pz - 4.8, pz - 4.4, "rubber")
    else:
        # hangs from the pivot leaning a little forward; the lower half hooks further forward (a 'J' towards the muzzle)
        t.box(-w / 2, w / 2, py - length * 0.55, py, pz - 2.8, pz + 2.4, mat, rot=(6, 0, 0), pivot=pivot)
        jy, jz = py - length * 0.5 * math.cos(math.radians(6)), pz - length * 0.5 * math.sin(math.radians(6))
        t.box(-w / 2, w / 2, jy - length * 0.52, jy + 1.5, jz - 2.8, jz + 2.2, mat, rot=(24, 0, 0), pivot=(0, jy, jz))
        if safety_blade:
            t.box(-1.1, 1.1, jy - length * 0.42, jy + 3, jz - 3.8, jz - 2.2, mat, rot=(20, 0, 0), pivot=(0, jy, jz))
    return t


def control(body: Bone, name, pivot, boxes, press=None, turn=None):
    """A small control as its own bone (slide_stop, safety, mag_release, decocker, takedown): boxes = [(x0, x1, y0, y1,
    z0, z1, mat), ...]. press / turn say how it moves when worked."""
    b = body.bone(name, pivot=pivot)
    for x0, x1, y0, y1, z0, z1, mat in boxes:
        b.box(x0, x1, y0, y1, z0, z1, mat)
    if press is not None or turn is not None:
        moving(body.model, name, pos=press, rot=turn)
    return b


def pistol_mag(m, gp, A, top_y, bot_y, z0, z1, width, body_mat="steel_dark", base_mat="polymer", round_d=9.0,
               round_len=29.0, bumper=5.0, holes=5, double=True):
    """Pistol magazine (its own bone, raked like the grip): tube, baseplate, witness holes showing brass, feed lips,
    follower and the top rounds."""
    mag = m["gun"].bone("magazine", pivot=gp, rot=(A, 0, 0))
    hw = width / 2
    zc = (z0 + z1) / 2
    mag.box(-hw, hw, bot_y + bumper, top_y, z0, z1, body_mat)
    mag.box(-hw + 1.6, hw - 1.6, bot_y + bumper + 6, top_y - 8, z0 - 0.6, z0, body_mat)                 # front rib
    mag.box(-hw - 1.6, hw + 1.6, bot_y, bot_y + bumper, z0 - 2.5, z1 + 3, base_mat)                     # baseplate
    mag.box(-hw - 0.8, hw + 0.8, bot_y - 1.6, bot_y, z0 - 1, z1 + 1.5, base_mat)
    mag.box(-2.5, 2.5, bot_y - 2.2, bot_y - 1.6, zc - 2.5, zc + 2.5, "steel")                           # plate pin
    if holes:
        H = top_y - bot_y - bumper
        for i in range(holes):
            y = top_y - 16 - i * (H - 30) / max(1, holes - 1)
            mag.box(-2.2, 2.2, y - 2, y + 2, z1, z1 + 0.5, "rubber")                                    # rear witness holes
            if i < holes - 1:
                mag.box(-1.5, 1.5, y - 1.3, y + 1.3, z1 + 0.3, z1 + 0.7, "brass")
            for sx in (-1, 1):
                mag.box(sx * hw - 0.3, sx * hw + 0.3, y - 1.5, y + 1.5, z1 - 9, z1 - 6, "rubber")
    lip = max(1.6, round_d * 0.42)
    mag.box(-hw, -hw + 1.5, top_y, top_y + lip, zc - 4, z1, "steel")                                    # feed lips
    mag.box(hw - 1.5, hw, top_y, top_y + lip, zc - 4, z1, "steel")
    mag.box(-hw + 1.7, hw - 1.7, top_y - 3, top_y - 0.2, z0 + 1, z1 - 1, "polymer_tan")                 # follower
    if double and width >= round_d * 1.7:
        mag.round_((-round_d * 0.2, top_y + round_d / 2 - 1, zc - 2), round_len, round_d)
        mag.round_((round_d * 0.24, top_y - round_d * 0.32, zc - 1.4), round_len, round_d, detail=1)
    else:
        mag.round_((0, top_y + round_d / 2 - 1, zc - 2), round_len, round_d)
    return mag


# ------------------------------------------------------------------------------------------------
# revolvers
# ------------------------------------------------------------------------------------------------
def rev_cylinder(m, cy, n, d, length, z0, chamber_r, case_d, case_len, mat="steel", flutes=True, speedloader=True,
                 crane_pivot=None, parent="gun", rod_len=None, crane=True, bullet="copper", rim=0.8, cases=True):
    """
    Swing-out cylinder with its crane, ejector, cartridges and speedloader. z0 = front face, the rear face is at
    z0 + length; the top chamber lines up with the bore when chamber_r == -cy.
    Bones: crane > cylinder > rounds, brass;  crane > ejector, speedloader.  (crane=False: a fixed-axis single
    action: `cylinder` hangs straight off `parent` and there is no ejector star or speedloader.)
    """
    zr = z0 + length
    if crane:
        cr = m[parent].bone("crane", pivot=crane_pivot or (-9, cy - 18, 0))
        px, py, _ = cr.pivot
        cr.box(px - 3.5, px + 3.5, py - 4, cy - d * 0.2, z0 - 9, z0 - 1, mat)                 # yoke arm
        cr.cyl((px, py, z0 - 22), 8, 44, mat, sides=8)                                         # yoke barrel / pivot
        cyl = cr.bone("cylinder", pivot=(0, cy, 0))
    else:
        cr = None
        cyl = m[parent].bone("cylinder", pivot=(0, cy, 0))
    cyl.cyl((0, cy, z0 + length / 2), d, length, mat)
    cyl.cyl((0, cy, z0 - 0.4), d * 0.5, 1.0, mat, sides=16)                                    # front gas ring
    for i in range(n):
        a = math.radians(90 + 360 / n * i)
        ca, sa = math.cos(a), math.sin(a)
        x, y = ca * chamber_r, cy + sa * chamber_r
        cyl.cyl((x, y, z0 - 0.15), case_d + 1.6, 0.5, "rubber", sides=8)                       # chamber mouth
        nx, ny = ca * (d / 2 - 0.5), cy + sa * (d / 2 - 0.5)
        cyl.bc((nx, ny, zr - 7), (3.2, 1.4, 5), "rubber", rot=(0, 0, math.degrees(a) - 90))    # stop notch
        if flutes:
            f = math.radians(90 + 360 / n * (i + 0.5))
            fx, fy = math.cos(f) * (d / 2 - 1.3), cy + math.sin(f) * (d / 2 - 1.3)
            cyl.bc((fx, fy, z0 + length * 0.36), (d * 0.24, 3.0, length * 0.66), "steel_dark",
                   rot=(0, 0, math.degrees(f) - 90))
    rounds = cyl.bone("rounds", pivot=(0, cy, 0))
    brass = cyl.bone("brass", pivot=(0, cy, 0)) if cases else None
    for i in range(n):
        a = math.radians(90 + 360 / n * i)
        x, y = math.cos(a) * chamber_r, cy + math.sin(a) * chamber_r
        rounds.cyl((x, y, zr + 0.5), case_d + rim, 1.5, "brass", sides=8)                      # rims
        rounds.cyl((x, y, zr + 1.2), case_d * 0.42, 0.5, "steel_light", sides=8)               # primers
        rounds.cyl((x, y, z0 - 0.5), case_d * 0.84, 0.6, bullet, sides=8)                      # bullet noses
        if cases:
            brass.cyl((x, y, zr - case_len / 2), case_d, case_len, "brass", sides=8)
    if not crane:
        return None, cyl
    ej = cr.bone("ejector", pivot=(0, cy, 0))
    rl = rod_len or length * 2.4
    ej.cyl((0, cy, z0 - rl / 2), 6.5, rl, "steel_light", sides=8)
    ej.cyl((0, cy, z0 - rl + 4), 9, 9, "steel_light", sides=8)                                 # knurled tip
    ej.cyl((0, cy, zr - 0.8), d * 0.56, 2.0, "steel_light", sides=16)                          # extractor star
    ej.cyl((0, cy, zr + 0.5), 7, 1.2, "steel", sides=8)                                        # ratchet
    if speedloader:
        sl = cr.bone("speedloader", pivot=(0, cy, 0))
        sl.cyl((0, cy, zr + 14), d * 1.02, 10, "polymer", sides=16)
        sl.cyl((0, cy, zr + 24), d * 0.42, 12, "polymer", sides=8)
        sl.cyl((0, cy, zr + 31), d * 0.5, 3, "alloy", sides=8)
        for i in range(n):
            a = math.radians(90 + 360 / n * i)
            x, y = math.cos(a) * chamber_r, cy + math.sin(a) * chamber_r
            sl.round_((x, y, zr - case_len / 2 + 6), case_len + 8, case_d, detail=1)
    return cr, cyl


def rev_grip(body: Bone, gp, A, y_bot, z_f, z_b, strap_mat, wood, hw=7.0, proud=8.0, flare=5.0, style="checker",
             line_mat=None, medallion="brass", wrap_front=True, y_top=None):
    """Revolver stocks on a grip strap: two scales swelling towards the butt, checkered, with medallion and screw."""
    r = raked(A, gp)
    yt = gp[1] if y_top is None else y_top
    H = yt - y_bot
    lm = line_mat or wood
    body.box(-hw, hw, y_bot, yt + 12, z_f, z_b, strap_mat, **r)                                # the steel strap, up into the frame
    body.box(-hw + 1.5, hw - 1.5, y_bot, yt, z_f - 0.8, z_f, strap_mat, **r)
    body.box(-hw + 1.5, hw - 1.5, y_bot, yt, z_b, z_b + 0.8, strap_mat, **r)
    ym = y_bot + H * 0.5
    for sx in (-1, 1):
        xa, xb = sorted((sx * hw, sx * (hw + proud)))
        body.box(xa, xb, ym, yt + 3, z_f - 0.5, z_b + 0.5, wood, **r)                          # upper scale
        body.box(xa, xb, y_bot - 2, ym, z_f - flare, z_b + flare * 0.7, wood, **r)             # butt swell
        xo = sorted((sx * (hw + proud), sx * (hw + proud + 1.4)))
        body.box(xo[0], xo[1], ym + 2, yt - 10, z_f + 3, z_b - 3, wood, **r)                   # rounded outer face
        body.box(xo[0], xo[1], y_bot + 2, ym, z_f - flare + 4, z_b + flare * 0.7 - 4, wood, **r)
        xs = sorted((sx * (hw + proud + 1.4), sx * (hw + proud + 1.85)))
        if style == "checker":
            n = max(4, int(H * 0.6 // 9))
            for i in range(n):
                y = y_bot + 8 + i * (H * 0.62) / n
                body.box(xs[0], xs[1], y, y + 1.4, z_f + 2, z_b - 2, lm, **r)
            for k in range(1, 5):
                z = z_f + (z_b - z_f) * k / 5
                body.box(xs[0] - 0.02, xs[1] + 0.02, y_bot + 8, y_bot + 8 + H * 0.62, z - 0.7, z + 0.7, lm, **r)
        elif style == "grooves":
            for i in range(3):
                y = yt - H * (0.3 + 0.24 * i)
                body.box(xs[0], xs[1], y - 4, y, z_f - flare * 0.5, z_f + 10, lm, **r)
        zc = (z_f + z_b) / 2
        if medallion:
            body.box(xs[0], xs[1] + sx * 0.3, yt - 22, yt - 13, zc - 4.5, zc + 4.5, medallion, **r)
        body.box(xs[0], xs[1] + sx * 0.5, ym - 2.6, ym + 2.6, zc - 2.6, zc + 2.6, "steel", **r)   # stock screw
        xq = sorted((sx * (hw + proud + 2.3), sx * (hw + proud + 2.5)))
        body.box(xq[0], xq[1], ym - 0.5, ym + 0.5, zc - 2.4, zc + 2.4, "rubber", **r)
    if wrap_front:
        body.box(-hw, hw, y_bot - 2, ym - 4, z_f - flare, z_f, wood, **r)                      # wood under the guard
    body.box(-hw - proud + 2, hw + proud - 2, y_bot - 3.4, y_bot - 2, z_f - flare + 3, z_b + flare * 0.7 - 3, wood, **r)
