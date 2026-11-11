"""Building blocks for long guns (mm, bore axis at y=0, muzzle towards -Z): sights, stocks, small receiver details."""
from __future__ import annotations

import math

from .core import Bone
from .parts import arc
from .common import moving


def slot(b: Bone, x, y0, y1, z0, z1, depth=0.5):
    """Dark slot / cut on a side face (x = surface, its sign picks the side)."""
    sx = 1 if x >= 0 else -1
    xs = sorted((x - sx * 0.3, x + sx * depth))
    return b.box(xs[0], xs[1], y0, y1, z0, z1, "rubber")


def top_slot(b: Bone, y, x0, x1, z0, z1, depth=0.5):
    return b.box(x0, x1, y - 0.3, y + depth, z0, z1, "rubber")


def ribs(b: Bone, hw, y0, y1, zs, w, mat, proud=0.45):
    """Pressed stiffening ribs standing off both sides of a stamped receiver."""
    for z in zs:
        b.box(-hw - proud, hw + proud, y0, y1, z, z + w, mat)


def ring_sight(b: Bone, z, y0, mat, r=11.0, depth=14.0, post_h=None, base_w=18.0, th=2.6):
    """HK-style front sight: a ring hood on a base with the post inside."""
    yc = y0 + r + 2
    b.box(-base_w / 2, base_w / 2, y0 - 2, y0 + 3, z - depth / 2, z + depth / 2, mat)
    n = 8
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        am = (a0 + a1) / 2
        L = 2 * r * math.tan(math.pi / n) + 0.6
        cx, cy = math.sin(am) * r, yc + math.cos(am) * r
        b.box(cx - L / 2, cx + L / 2, cy - th / 2, cy + th / 2, z - depth / 2, z + depth / 2, mat,
              rot=(0, 0, -math.degrees(am)), pivot=(cx, cy, z))
    ph = post_h or r
    b.box(-1.1, 1.1, y0 + 2, y0 + 2 + ph, z - 1.1, z + 1.1, mat)
    return yc


def eared_sight(b: Bone, z, y0, h, mat, w=16.0, depth=12.0, post=True, lean=8.0):
    """Front (or rear) sight protected by two ears that lean outwards (AK, Uzi, M1 carbine)."""
    b.box(-w / 2, w / 2, y0, y0 + 3, z - depth / 2, z + depth / 2, mat)
    for sx in (-1, 1):
        x = sx * (w / 2 - 1.5)
        b.box(x - 1.5, x + 1.5, y0 + 2, y0 + h, z - depth / 2 + 1, z + depth / 2 - 1, mat, rot=(0, 0, -sx * lean),
              pivot=(x, y0 + 2, z))
    if post:
        b.box(-1.1, 1.1, y0 + 3, y0 + h * 0.86, z - 1.1, z + 1.1, mat)


def drum_sight(b: Bone, z, y0, mat, d=20.0, w=14.0, gap=3.4):
    """HK rotary rear sight: base and a drum split down the middle, so the eye looks through the slot between the
    halves. The line of sight is at y0 + 3 + d * 0.55."""
    b.box(-w / 2 - 2, w / 2 + 2, y0, y0 + 3, z - 16, z + 14, mat)
    yc = y0 + 3 + d * 0.3
    for sx in (-1, 1):
        x = sx * (gap / 2 + (w / 2 - gap / 2) / 2)
        b.cyl((x, yc, z), d, w / 2 - gap / 2, mat, axis="x")
        b.cyl((sx * (w / 2 + 1), yc, z), d * 0.5, 2, "steel", axis="x", sides=8)
    b.box(-gap / 2, gap / 2, y0 + 3, yc + d * 0.12, z - d * 0.4, z + d * 0.4, mat)                 # floor of the slot
    b.box(w / 2 + 2, w / 2 + 4.5, y0 + 1, y0 + 6, z - 4, z + 4, "steel")                           # windage screw
    return yc + d * 0.25


def flip_sight(b: Bone, z, y0, mat, w=14.0, h=12.0, gap=3.2):
    """Two-position L flip rear sight between protective ears; the standing leaf has an open U notch.
    The line of sight is at y0 + h - 3."""
    b.box(-w / 2 - 3, w / 2 + 3, y0, y0 + 2.5, z - 9, z + 9, mat)
    for sx in (-1, 1):
        b.box(sx * (w / 2 + 3) - 1.2, sx * (w / 2 + 3) + 1.2, y0, y0 + h, z - 8, z + 8, mat)
        xs = sorted((sx * gap / 2, sx * (w / 2 - 1)))
        b.box(xs[0], xs[1], y0 + 2.5, y0 + h - 1, z - 1.2, z + 1.2, mat)                            # leaf posts
    b.box(-gap / 2, gap / 2, y0 + 2.5, y0 + h - 5, z - 1.2, z + 1.2, mat)                          # notch floor
    b.box(-w / 2 + 1, w / 2 - 1, y0 + 2.5, y0 + 5, z + 1.2, z + 8, mat)                              # folded leaf
    return y0 + h - 3


def tangent_sight(b: Bone, z0, z1, y0, mat, w=12.0, h=8.0):
    """Tangent leaf rear sight: stepped base, leaf lying forward, slider with its buttons, notch at the rear."""
    b.box(-w / 2 - 2, w / 2 + 2, y0, y0 + 3, z0, z1, mat)
    b.box(-w / 2, w / 2, y0 + 3, y0 + 5.5, z0 + 2, z1 - 2, mat)
    zs = z0 + (z1 - z0) * 0.55
    b.box(-w / 2 - 3.5, w / 2 + 3.5, y0 + 3, y0 + 7.5, zs - 4, zs + 4, "steel")
    b.box(-w / 2, -1.6, y0 + 5.5, y0 + h, z1 - 5, z1 - 2, mat)
    b.box(1.6, w / 2, y0 + 5.5, y0 + h, z1 - 5, z1 - 2, mat)
    for i in range(4):
        z = z0 + 6 + i * (z1 - z0 - 16) / 4
        b.box(w / 2 - 0.2, w / 2 + 0.25, y0 + 3.6, y0 + 5, z, z + 1.2, "white")


def peep(b: Bone, z, y0, y1, mat, w=8.0, hole=4.0, depth=3.0, hole_y=None):
    """A leaf with a real square hole in it (so the view through it is open). Returns the hole's centre height."""
    hy = hole_y if hole_y is not None else y1 - hole / 2 - 2
    b.box(-w / 2, -hole / 2, y0, y1, z - depth / 2, z + depth / 2, mat)
    b.box(hole / 2, w / 2, y0, y1, z - depth / 2, z + depth / 2, mat)
    b.box(-hole / 2, hole / 2, y0, hy - hole / 2, z - depth / 2, z + depth / 2, mat)
    b.box(-hole / 2, hole / 2, hy + hole / 2, y1, z - depth / 2, z + depth / 2, mat)
    return hy


def aperture_sight(b: Bone, z, y0, mat, w=18.0, h=12.0, hole=4.0):
    """Peep rear sight with protective wings and a windage knob. The line of sight is at y0 + h - 4.5."""
    b.box(-w / 2, w / 2, y0, y0 + 3, z - 10, z + 10, mat)
    for sx in (-1, 1):
        b.box(sx * w / 2 - (2.4 if sx > 0 else 0), sx * w / 2 + (2.4 if sx < 0 else 0), y0 + 3, y0 + h, z - 8, z + 8, mat)
    peep(b, z, y0 + 3, y0 + h - 1.5, mat, w=8, hole=hole, hole_y=y0 + h - 4.5)
    b.cyl((w / 2 + 3.5, y0 + 6, z), 9, 5, "steel", axis="x", sides=8)
    return y0 + h - 4.5


def rod_stock(stock: Bone, z0, z1, x_off, y, mat, butt_y0, butt_y1, butt_hw=18.0, rod=6.0, pad="rubber", cross=True):
    """Retractable stock: two rods along the sides, a butt plate with a rubber pad."""
    for sx in (-1, 1):
        stock.box(sx * x_off - rod / 2, sx * x_off + rod / 2, y - rod / 2, y + rod / 2, z0, z1, mat)
    stock.box(-butt_hw, butt_hw, butt_y0, butt_y1, z1 - 2, z1 + 8, mat)
    stock.box(-butt_hw - 1, butt_hw + 1, butt_y0 - 3, butt_y1 + 2, z1 + 8, z1 + 17, pad)
    for i in range(4):
        yy = butt_y0 + (butt_y1 - butt_y0) * (i + 0.5) / 4
        stock.box(-butt_hw + 2, butt_hw - 2, yy - 2, yy + 2, z1 + 17, z1 + 17.6, "polymer")
    if cross:
        stock.box(-x_off, x_off, y - rod / 2 + 0.5, y + rod / 2 - 0.5, z1 - 8, z1 - 2, mat)


def selector(body: Bone, pivot, mat="steel", length=20.0, side=-1, marks=True, turn=(-50, 0, 0), name="selector"):
    """Fire selector lever on a side face (pivot.x = the surface): axle, lever pointing forward, optional S/E/F dots."""
    px, py, pz = pivot
    b = body.bone(name, pivot=pivot)
    xs = sorted((px, px + side * 3.2))
    b.cyl((px + side * 1.6, py, pz), 9, 3.2, mat, axis="x", sides=8)
    b.box(xs[0], xs[1], py - 3, py + 3, pz - length, pz + 2, mat)
    xk = sorted((px + side * 3.2, px + side * 5))
    b.box(xk[0], xk[1], py - 3.6, py + 3.6, pz - length, pz - length + 7, mat)
    if marks:
        for i, col in enumerate(("white", "sight_orange", "sight_orange")):
            a = math.radians(-8 - i * 26)
            body.box(*sorted((px, px + side * 0.4)), py + math.sin(a) * (length + 6) - 1.2,
                     py + math.sin(a) * (length + 6) + 1.2, pz - math.cos(a) * (length + 6) - 1.2,
                     pz - math.cos(a) * (length + 6) + 1.2, col)
    moving(body.model, name, rot=turn)
    return b


def paddle(body: Bone, pivot, mat="steel_dark", w=16.0, h=10.0, d=10.0, name="mag_release", press=(0, 0, 3)):
    """Paddle magazine release hanging behind the magazine well."""
    px, py, pz = pivot
    b = body.bone(name, pivot=pivot)
    b.box(px - w / 2, px + w / 2, py - h, py, pz - 1.5, pz + 1.5, mat)
    b.box(px - w / 2 + 1, px + w / 2 - 1, py - h - 2, py - h + 2, pz, pz + d, mat)
    for i in range(3):
        b.box(px - w / 2 + 2, px + w / 2 - 2, py - h - 2.4, py - h - 2, pz + 2 + i * 2.6, pz + 3.2 + i * 2.6, "rubber")
    moving(body.model, name, pos=press)
    return b


def button(body: Bone, name, pivot, d=8.0, mat="steel_dark", proud=2.0, press=None):
    """Round push button on a side face (pivot.x = the surface, its sign picks the side)."""
    px, py, pz = pivot
    sx = 1 if px >= 0 else -1
    b = body.bone(name, pivot=pivot)
    b.cyl((px + sx * proud / 2, py, pz), d, proud, mat, axis="x", sides=8)
    moving(body.model, name, pos=press or (-sx * 1.5, 0, 0))
    return b


def stock_solid(stock: Bone, hw, top, bot, mat, pad="rubber", pad_th=10.0, plate="steel_dark"):
    """Solid stock from a side profile (top / bottom polylines [(z, y)]), with a butt plate and pad at the rear."""
    stock.profile(-hw, hw, top, bot, mat)
    z1 = top[-1][0]
    yt, yb = top[-1][1], bot[-1][1]
    stock.box(-hw - 0.5, hw + 0.5, yb - 1, yt + 1, z1 - 1, z1 + 2, plate)
    if pad:
        stock.box(-hw - 1, hw + 1, yb - 2, yt + 2, z1 + 2, z1 + 2 + pad_th, pad)
        for i in range(4):
            yy = yb + (yt - yb) * (i + 0.5) / 4
            stock.box(-hw + 2, hw - 2, yy - 2, yy + 2, z1 + 2 + pad_th, z1 + 2.6 + pad_th, "polymer")
