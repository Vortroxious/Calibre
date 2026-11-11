"""Reusable gun part builders (mm, render space, barrel towards -Z, bore axis at y=0)."""
from __future__ import annotations

import math

from .core import Bone

METAL_MAGS = ("steel_dark", "steel", "steel_parked", "alloy", "alloy_grey", "stainless", "steel_light")


def arc(zc, yc, rz, ry, a0, a1, n=6):
    """Points [(z, y)] on an ellipse centred (zc, yc): angle 0 = +z (rear), 90 = up, 180 = -z (front), 270 = down."""
    return [(zc + rz * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             yc + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# ------------------------------------------------------------------------------------------------
# small fittings
# ------------------------------------------------------------------------------------------------
def pins(b: Bone, half_w, pts, d=5.0, mat="steel", proud=0.5):
    """Cross pins showing on both sides of a receiver: pts = [(y, z), ...]."""
    for y, z in pts:
        for sx in (-1, 1):
            b.bc((sx * (half_w + proud / 2), y, z), (proud, d, d), mat)
            b.bc((sx * (half_w + proud / 2 + 0.05), y, z), (proud, d * 0.7, d * 0.7), mat, rot=(45, 0, 0))


def screw(b: Bone, x, y, z, d=5.0, mat="steel", proud=0.5):
    """Slotted screw head on a side face (x is the surface; the sign of x picks the side)."""
    sx = 1 if x >= 0 else -1
    b.bc((x + sx * proud / 2, y, z), (proud, d, d), mat)
    b.bc((x + sx * (proud + 0.1), y, z), (0.25, d * 0.2, d * 0.9), "rubber")


def serrations(b: Bone, half_w, y0, y1, z0, z1, n=8, mat="steel", proud=0.25, sides=(-1, 1), slant=0.0):
    """Row of thin vertical ribs on the sides of a slide or bolt."""
    step = (z1 - z0) / n
    for i in range(n):
        z = z0 + step * i
        for sx in sides:
            b.box(sx * half_w - proud, sx * half_w + proud, y0, y1, z, z + step * 0.45, mat,
                  rot=(slant, 0, 0) if slant else None, pivot=(0, (y0 + y1) / 2, z) if slant else None)


def vents(b: Bone, half_w, y0, y1, z0, z1, n=6, fill=0.55, mat="rubber", sides=(-1, 1), proud=0.4):
    """Row of dark slots along Z on the sides of a handguard / jacket."""
    step = (z1 - z0) / n
    for i in range(n):
        z = z0 + step * i + step * (1 - fill) / 2
        for sx in sides:
            b.box(sx * half_w - proud, sx * half_w + proud, y0, y1, z, z + step * fill, mat)


def sling_swivel(b: Bone, x, y, z, along="z", drop=10.0, w=14.0, mat="steel"):
    """Stud with a hanging D-ring. (x, y, z) is the point on the underside it hangs from."""
    b.bc((x, y - 2, z), (5, 4, 5), mat)
    if along == "z":
        b.box(x - 1.2, x + 1.2, y - drop, y - 2, z - w / 2, z - w / 2 + 2, mat)
        b.box(x - 1.2, x + 1.2, y - drop, y - 2, z + w / 2 - 2, z + w / 2, mat)
        b.box(x - 1.2, x + 1.2, y - drop - 2, y - drop, z - w / 2, z + w / 2, mat)
    else:
        b.box(x - w / 2, x - w / 2 + 2, y - drop, y - 2, z - 1.2, z + 1.2, mat)
        b.box(x + w / 2 - 2, x + w / 2, y - drop, y - 2, z - 1.2, z + 1.2, mat)
        b.box(x - w / 2, x + w / 2, y - drop - 2, y - drop, z - 1.2, z + 1.2, mat)


def side_swivel(b: Bone, x, y, z, h=16.0, mat="steel"):
    """Sling loop standing off a side face (x = surface, sign picks the side), for side-slung rifles."""
    sx = 1 if x >= 0 else -1
    b.box(x, x + sx * 4, y - h / 2, y - h / 2 + 2, z - 3, z + 3, mat)
    b.box(x, x + sx * 4, y + h / 2 - 2, y + h / 2, z - 3, z + 3, mat)
    b.box(x + sx * 3, x + sx * 5, y - h / 2, y + h / 2, z - 3, z + 3, mat)


def ejection_port(b: Bone, x, y0, y1, z0, z1, lip_mat=None, depth=0.4):
    """Dark recess on a side face with a thin raised lip above and below (x = surface, sign picks the side)."""
    sx = 1 if x >= 0 else -1
    xa, xb = sorted((x - sx * 6, x + sx * depth))
    b.box(xa, xb, y0, y1, z0, z1, "rubber")
    if lip_mat:
        xl = sorted((x, x + sx * (depth + 0.5)))
        b.box(xl[0], xl[1], y1, y1 + 1.5, z0 - 2, z1 + 2, lip_mat)
        b.box(xl[0], xl[1], y0 - 1.5, y0, z0 - 2, z1 + 2, lip_mat)


# ------------------------------------------------------------------------------------------------
# furniture
# ------------------------------------------------------------------------------------------------
def pistol_grip(b: Bone, top_z, top_y=-22.0, length=90.0, width=28.0, depth=34.0, angle=-20.0, mat="polymer",
                checker=True):
    """AR/AK-style rifle pistol grip hanging from (0, top_y, top_z), raked back by `angle`."""
    piv = (0, top_y, top_z)
    r = dict(rot=(angle, 0, 0), pivot=piv)
    hw, hd = width / 2, depth / 2
    b.box(-hw, hw, top_y - length, top_y, top_z - hd, top_z + hd, mat, **r)
    b.box(-hw + 1, hw - 1, top_y - length + 6, top_y - 14, top_z + hd, top_z + hd + 5, mat, **r)       # palm swell
    b.box(-hw + 3, hw - 3, top_y - length + 16, top_y - 30, top_z + hd + 5, top_z + hd + 7.5, mat, **r)
    b.box(-hw - 1, hw + 1, top_y - length - 4, top_y - length, top_z - hd - 2, top_z + hd + 5, mat, **r)  # base flare
    b.box(-hw + 4, hw - 4, top_y - length - 5.2, top_y - length - 4, top_z - hd + 4, top_z + hd - 2, "rubber", **r)  # plug
    b.box(-hw + 1, hw - 1, top_y - 12, top_y, top_z + hd, top_z + hd + 8, mat, **r)                   # beavertail web
    for i in range(3):                                                                               # finger rests
        y = top_y - 26 - i * (length - 40) / 3
        b.box(-hw + 2, hw - 2, y - 5, y, top_z - hd - 2.2, top_z - hd, mat, **r)
    if checker:
        n = max(4, int((length - 30) // 11))
        for i in range(n):
            y = top_y - 20 - i * (length - 34) / n
            b.box(-hw - 0.5, hw + 0.5, y - 3.2, y, top_z - hd + 4, top_z + hd - 3, mat, **r)
    for sx in (-1, 1):                                                                               # grip screw
        b.box(sx * hw - 0.3, sx * hw + 0.3 + sx * 0.5, top_y - 13, top_y - 8, top_z - 2.5, top_z + 2.5, "steel", **r)


def trigger_group(m, body: Bone, z, y_top=-22.0, guard_depth=30.0, guard_len=62.0, guard_mat="alloy", width=8.0,
                  trig_mat="steel_dark"):
    """Trigger guard (one bar bent round the trigger) + `trigger` bone with a curved blade. z = trigger pivot z."""
    yb = y_top - guard_depth
    zf, zr = z - guard_len * 0.55, z + guard_len * 0.45
    c = min(9.0, guard_depth * 0.36, guard_len * 0.2)
    pts = [(zf + 2, y_top + 1)] + arc(zf + 2 + c, yb + c, c, c, 180, 270, 3) + arc(zr - 2 - c, yb + c, c, c, 270, 330, 2)
    pts.append((zr + 1, min(y_top, yb + c + 8)))
    body.path(pts, width, 4.0, guard_mat)
    trig = body.bone("trigger", pivot=(0, y_top - 2, z))
    p = (0, y_top - 2, z)
    trig.box(-2.5, 2.5, y_top - 14, y_top - 2, z - 2.6, z + 2.2, trig_mat, rot=(5, 0, 0), pivot=p)
    jy, jz = y_top - 2 - 11 * math.cos(math.radians(5)), z - 11 * math.sin(math.radians(5))
    trig.box(-2.5, 2.5, jy - 11, jy + 1.5, jz - 2.6, jz + 2.0, trig_mat, rot=(22, 0, 0), pivot=(0, jy, jz))   # hooked tip
    return trig


# ------------------------------------------------------------------------------------------------
# barrels and muzzle devices
# ------------------------------------------------------------------------------------------------
def barrel(b: Bone, z0, z1, d=16.0, mat="steel", y=0.0, crown=True):
    """Barrel tube. The muzzle (the -Z end) gets a recessed crown and a dark bore; a muzzle device simply covers it."""
    zc = (z0 + z1) / 2
    out = b.cyl((0, y, zc), d, abs(z1 - z0), mat)
    if crown:
        zm = min(z0, z1)
        b.cyl((0, y, zm - 0.3), d * 0.82, 0.6, mat, sides=8 if d < 12 else 16)
        b.cyl((0, y, zm - 0.75), d * 0.5, 0.5, "rubber", sides=8)
    return out


def flash_hider_a2(b: Bone, z, d=20.0, length=55.0, y=0.0, mat="steel_dark"):
    """Birdcage: slots over the top half only, closed bottom, crush washer behind."""
    zc = z - length / 2
    b.cyl((0, y, zc), d, length, mat)
    b.cyl((0, y, z - 2), d + 2.4, 3.2, "steel")                                    # crush washer
    b.cyl((0, y, z - length + 3), d * 0.9, 6.2, mat)                                # front taper
    b.cyl((0, y, z - length - 0.3), d * 0.5, 0.6, "rubber", sides=8)                # bore
    sl = length * 0.5
    for ang in (-72, -36, 0, 36, 72):
        b.box(-1.5, 1.5, y + d / 2 - 2.6, y + d / 2 + 0.35, z - length + 8, z - length + 8 + sl, "rubber",
              rot=(0, 0, ang), pivot=(0, y, zc))
    for ang in (90, -90):                                                           # wrench flats
        b.box(-3, 3, y + d / 2 - 0.4, y + d / 2 + 0.3, z - 12, z - 5, "steel", rot=(0, 0, ang), pivot=(0, y, zc))


def muzzle_brake(b: Bone, z, d=26.0, length=60.0, ports=3, mat="steel_dark", w=None, y=0.0):
    w = w or d
    b.chamfer_box(-w / 2, w / 2, y - d / 2, y + d / 2, z - length, z, mat, ch=min(4.0, d * 0.16), edges="all")
    b.cyl((0, y, z - 3), min(w, d) * 0.9, 6.4, "steel")                              # jam nut
    b.cyl((0, y, z - length - 0.3), min(w, d) * 0.46, 0.6, "rubber", sides=8)        # bore
    for i in range(ports):
        zz = z - length + 8 + i * (length - 18) / max(1, ports - 1)
        b.box(-w / 2 - 0.4, w / 2 + 0.4, y - d / 2 + 4.5, y + d / 2 - 4.5, zz - 3, zz + 3, "rubber")       # side ports
        b.box(-w / 4, w / 4, y + d / 2 - 1, y + d / 2 + 0.35, zz - 2, zz + 2, "rubber")                   # top vents


def ar_front_sight(b: Bone, z, base_y=10.0, h=55.0):
    """A-frame front sight base: clamps the barrel, two legs, protective ears, post, bayonet lug and swivel."""
    sd = "steel_dark"
    b.cyl((0, 0, z - 8), 22, 9, sd)                                                 # front barrel band
    b.cyl((0, 0, z + 8), 22, 9, sd)                                                 # rear band (gas port)
    b.box(-6, 6, 6, base_y + 10, z - 12, z + 12, sd)                                # block
    b.box(-4, 4, base_y + 8, base_y + h * 0.72, z + 2, z + 7, sd, rot=(-8, 0, 0), pivot=(0, base_y + 8, z + 4))   # rear leg
    b.box(-4, 4, base_y + 8, base_y + h * 0.72, z - 8, z - 3, sd, rot=(14, 0, 0), pivot=(0, base_y + 8, z - 5))   # front leg
    b.box(-9, 9, base_y + h * 0.5, base_y + h * 0.62, z - 7, z + 7, sd)             # bridge
    b.box(-9, -5.5, base_y + h * 0.58, base_y + h, z - 6, z + 6, sd, rot=(0, 0, 6), pivot=(-7, base_y + h * 0.58, z))
    b.box(5.5, 9, base_y + h * 0.58, base_y + h, z - 6, z + 6, sd, rot=(0, 0, -6), pivot=(7, base_y + h * 0.58, z))
    b.cyl((0, base_y + h * 0.66, z), 6, 4, "steel", axis="y", sides=8)              # post detent wheel
    b.box(-1.1, 1.1, base_y + h * 0.68, base_y + h * 0.95, z - 1.1, z + 1.1, sd)    # post
    b.box(-4, 4, -17, -10, z - 9, z + 9, sd)                                        # bayonet lug
    b.box(-2.5, 2.5, -19, -17, z - 9, z - 3, sd)
    sling_swivel(b, 0, -17, z + 6, along="x", drop=9, w=16)


def buis_rear(b: Bone, z, y):
    b.box(-12, 12, y, y + 6, z - 14, z + 14, "alloy")
    b.box(-13, -12, y + 1, y + 5, z - 5, z + 5, "steel")                            # clamp bolt
    b.box(-9, -4, y + 6, y + 24, z - 4, z + 4, "alloy")                             # wings
    b.box(4, 9, y + 6, y + 24, z - 4, z + 4, "alloy")
    b.box(-4, 4, y + 6, y + 14, z - 3, z + 3, "alloy")
    b.box(-4.5, 4.5, y + 14, y + 23, z - 1.5, z + 1.5, "steel_dark")                # aperture leaf
    b.box(-1.2, 1.2, y + 17, y + 20.5, z - 1.8, z + 1.8, "rubber")
    b.cyl((11.5, y + 12, z), 7, 5, "steel", axis="x", sides=8)                      # windage knob


# ------------------------------------------------------------------------------------------------
# magazines
# ------------------------------------------------------------------------------------------------
def _mag_top(bone: Bone, top_y, zc, width, round_d, round_len, rot=None, pivot=None):
    """Feed lips, follower and the top cartridge(s) at the mouth of a magazine."""
    hw = width / 2
    r = dict(rot=rot, pivot=pivot) if rot else {}
    lip = max(1.6, round_d * 0.42)
    half = round_len / 2 + 2
    bone.box(-hw, -hw + 1.6, top_y, top_y + lip, zc - half + round_len * 0.3, zc + half, "steel", **r)     # feed lips
    bone.box(hw - 1.6, hw, top_y, top_y + lip, zc - half + round_len * 0.3, zc + half, "steel", **r)
    bone.box(-hw + 1.8, hw - 1.8, top_y - 3, top_y - 0.2, zc - half + 1, zc + half - 1, "polymer_tan", **r)  # follower
    double = width >= round_d * 1.85
    if double:
        bone.round_((-round_d * 0.22, top_y + round_d / 2 - 1, zc), round_len, round_d)
        bone.round_((round_d * 0.26, top_y - round_d * 0.3, zc + 0.6), round_len, round_d, detail=1)
    else:
        bone.round_((0, top_y + round_d / 2 - 1, zc), round_len, round_d)


def straight_mag(bone: Bone, top_y, z0, z1, length, width=24.0, mat="steel_dark", base_mat=None, ribs=True, round_d=6.0,
                 round_len=40.0, witness=None):
    """Mag body hanging straight down from top_y: feed lips, follower, the top rounds, ribs, witness holes, floorplate."""
    hw = width / 2
    zc = (z0 + z1) / 2
    yb = top_y - length
    bone.box(-hw, hw, yb, top_y, z0, z1, mat)
    bone.box(-hw - 1.5, hw + 1.5, yb - 6, yb, z0 - 2, z1 + 3, base_mat or mat)                    # floorplate
    bone.box(-hw + 2, hw - 2, yb - 7.2, yb - 6, zc - 4, zc + 4, "steel")                          # plate catch
    bone.box(-hw * 0.5, hw * 0.5, yb + 4, top_y - 8, z1, z1 + 1.2, mat)                           # spine
    bone.box(-hw * 0.4, hw * 0.4, yb + 4, top_y - 12, z0 - 1, z0, mat)                            # front rib
    if ribs:
        bone.box(-hw - 0.6, hw + 0.6, yb + 10, top_y - 20, zc - 4, zc + 4, mat)
        if z1 - z0 > 34:
            for dz in (-0.3, 0.3):
                zz = zc + (z1 - z0) * dz
                bone.box(-hw - 0.45, hw + 0.45, yb + 14, top_y - 26, zz - 1.6, zz + 1.6, mat)
    if witness is None:
        witness = mat in METAL_MAGS
    if witness and length > 50:
        n = max(2, min(5, int(length // 34)))
        for i in range(n):
            y = top_y - 22 - i * (length - 40) / n
            for sx in (-1, 1):
                bone.box(sx * hw - 0.35, sx * hw + 0.35, y - 3, y, z1 - 8, z1 - 4.5, "rubber")
                if i < n - 1:
                    bone.box(sx * hw - 0.45, sx * hw + 0.45, y - 2.5, y - 0.5, z1 - 7.5, z1 - 5, "brass")
    _mag_top(bone, top_y, zc, width, round_d, round_len)


def curved_mag(bone: Bone, top_y, z_front, depth, length, curve=28.0, segs=5, width=26.0, mat="steel_dark",
               rib_mat=None, round_d=8.0, round_len=50.0, base=True):
    """
    Magazine that curves forward as it goes down (AK, G3, M249-ish). Built from segments rotated
    progressively about their top-front corner, each with a side rib and front / rear seams.
    """
    seg = length / segs
    y = top_y
    z = z_front
    ang = 0.0
    step = curve / segs
    hw = width / 2
    for i in range(segs):
        a = ang + step / 2
        piv = (0, y, z)
        r = dict(rot=(a, 0, 0), pivot=piv)
        bone.box(-hw, hw, y - seg - 0.8, y, z, z + depth, mat, **r)
        bone.box(-hw * 0.45, hw * 0.45, y - seg - 0.4, y - 1, z + depth, z + depth + 1.2, mat, **r)      # spine seam
        bone.box(-hw * 0.35, hw * 0.35, y - seg - 0.4, y - 1, z - 1, z, mat, **r)                         # front seam
        if rib_mat:
            bone.box(-hw - 0.6, hw + 0.6, y - seg * 0.7, y - seg * 0.3, z + depth * 0.3, z + depth * 0.7, rib_mat, **r)
            bone.box(-hw - 0.45, hw + 0.45, y - seg * 0.92, y - seg * 0.08, z + depth * 0.1, z + depth * 0.16, rib_mat,
                     **r)
            bone.box(-hw - 0.45, hw + 0.45, y - seg * 0.92, y - seg * 0.08, z + depth * 0.84, z + depth * 0.9, rib_mat,
                     **r)
        else:
            bone.box(-hw - 0.5, hw + 0.5, y - seg * 0.9, y - seg * 0.1, z + depth * 0.42, z + depth * 0.58, mat, **r)
        rr = math.radians(a)
        y -= seg * math.cos(rr)
        z -= seg * math.sin(rr)
        ang += step
    if base:
        r = dict(rot=(ang, 0, 0), pivot=(0, y, z))
        bone.box(-hw - 1.5, hw + 1.5, y - 6, y, z - 2, z + depth + 3, rib_mat or mat, **r)
        bone.box(-hw + 2, hw - 2, y - 7.2, y - 6, z + depth / 2 - 4, z + depth / 2 + 4, "steel", **r)   # plate catch
    bone.box(-hw * 0.6, hw * 0.6, top_y - 10, top_y - 2, z_front + depth, z_front + depth + 3, rib_mat or mat)  # rear lug
    _mag_top(bone, top_y, z_front + depth / 2, width, round_d, min(round_len, depth + 14))


# ------------------------------------------------------------------------------------------------
# stocks, handguards, bipods, optics
# ------------------------------------------------------------------------------------------------
def ar_stock(b: Bone, z0, mat="polymer", tube_mat="alloy", ext=0.0):
    """M4 collapsible stock starting at receiver rear z0: buffer tube, castle nut, end plate, six-position body."""
    b.cyl((0, -4, z0 + 110), 30, 220, tube_mat)
    b.cyl((0, -4, z0 + 9), 36, 9, "steel_dark")                              # castle nut
    for ang in (0, 60, 120):
        b.box(-18.4, 18.4, -6, -2, z0 + 5.5, z0 + 12.5, "steel", rot=(0, 0, ang), pivot=(0, -4, z0 + 9))
    b.box(-17, 17, -30, 10, z0 + 1, z0 + 4.5, "steel_dark")                  # end plate with sling loop
    b.box(-3, 3, -40, -30, z0 + 1, z0 + 4.5, "steel_dark")
    for i in range(6):                                                       # position holes under the tube
        b.box(-2, 2, -19.6, -18.8, z0 + 50 + i * 26, z0 + 56 + i * 26, "rubber")
    s = z0 + 120 + ext
    b.taper(-20, 20, s, s + 100, 14, 14, -50, -70, mat)                      # sloped toe
    b.box(-15, 15, -20, 20, s - 30, s, mat)
    b.box(-8, 8, 14, 22, s - 20, s + 90, mat)                                # cheek ridge
    b.box(-6, 6, -34, -22, s - 24, s + 10, mat)                              # latch lever
    b.box(-7, 7, -37, -34, s - 20, s + 2, "steel_dark")
    for sx in (-1, 1):                                                       # sling slots
        b.box(sx * 20 - 0.4, sx * 20 + 0.4, -40, -22, s + 62, s + 68, "rubber")
        b.box(sx * 20 - 0.4, sx * 20 + 0.4, -6, 6, s + 20, s + 60, mat)
    b.box(-21, 21, -78, 18, s + 90, s + 104, "rubber")                       # butt pad
    for yy in (-60, -40, -20, 0):
        b.box(-19, 19, yy - 2, yy + 2, s + 104, s + 104.6, "polymer")


def picatinny_handguard(b: Bone, z0, z1, y_top=16.0, y_bot=-30.0, half_w=19.0, mat="alloy", slots=True):
    b.chamfer_box(-half_w, half_w, y_bot, y_top, z0, z1, mat, ch=4.0, edges="all")
    b.rail(z0 + 4, z1 - 4, y_top, mat="alloy", side="top", slots=slots)
    b.rail(z0 + 4, z1 - 4, y_bot, mat="alloy", side="bottom", slots=slots)
    b.cyl((0, (y_top + y_bot) / 2 + 6, z1 - 4), half_w * 1.7, 8, "steel_dark")        # barrel nut
    b.box(-half_w - 0.3, half_w + 0.3, y_bot + 6, y_top - 6, z0, z0 + 3, "steel_dark")   # front cap
    if slots:
        n = int((z1 - z0) // 40)
        for i in range(n):
            z = z0 + 14 + i * 40
            b.box(-half_w - 0.5, half_w + 0.5, (y_top + y_bot) / 2 - 6, (y_top + y_bot) / 2 + 6, z, z + 22, "rubber")
            for sx in (-1, 1):
                b.bc((sx * (half_w + 0.3), y_top - 7, z + 30), (0.6, 3.4, 3.4), "steel")           # rail screws
                b.bc((sx * (half_w + 0.3), y_bot + 7, z + 30), (0.6, 3.4, 3.4), "steel")


def bipod(b: Bone, z, y=-10.0, legs_len=180.0, folded=True, mat="steel_dark", fold="fwd"):
    """Harris-style bipod: clamp block, hinge, two-stage legs with rubber feet. fold: legs lie 'fwd' or 'back'."""
    d = -1 if fold == "fwd" else 1
    b.box(-14, 14, y - 10, y, z - 14, z + 14, mat)
    b.box(-16, 16, y - 4, y, z - 6, z + 6, mat)                              # clamp ears
    b.cyl((0, y - 7, z), 6, 34, "steel", axis="x", sides=8)                  # hinge pin
    up = legs_len * 0.56
    for sx in (-1, 1):
        if folded:
            x = sx * 8
            b.box(x - 4, x + 4, y - 15, y - 7, z + d * up, z, mat)                           # upper leg
            b.box(x - 3, x + 3, y - 14, y - 8, z + d * (legs_len - 8), z + d * up, "steel")  # extension
            b.box(x - 4.5, x + 4.5, y - 15.5, y - 6.5, z + d * (up + 6), z + d * (up - 6), mat)   # lock collar
            b.box(x - 4.5, x + 4.5, y - 15.5, y - 6.5, z + d * legs_len, z + d * (legs_len - 10), "rubber")   # foot
            b.box(x - 1, x + 1, y - 6.6, y - 5.6, z + d * up * 0.8, z + d * 10, "steel")     # return spring
        else:
            x = sx * 8
            r = dict(rot=(0, 0, sx * 12), pivot=(x, y - 7, z))
            b.box(x - 4, x + 4, y - 7 - up, y - 7, z - 4, z + 4, mat, **r)
            b.box(x - 3, x + 3, y - 7 - legs_len + 8, y - 7 - up, z - 3, z + 3, "steel", **r)
            b.box(x - 4.5, x + 4.5, y - 13 - up, y - 1 - up, z - 4.5, z + 4.5, mat, **r)
            b.box(x - 4.5, x + 4.5, y - 7 - legs_len, y + 3 - legs_len, z - 4.5, z + 4.5, "rubber", **r)


def scope(b: Bone, z_center, y_axis, length=300.0, tube_d=30.0, obj_d=50.0, eye_d=42.0, mat="alloy", mount_y=None,
          turrets=True):
    """Riflescope along Z centred on z_center at height y_axis: bells, lenses, turrets, zoom ring, rings and base."""
    zc, ya = z_center, y_axis
    L = length
    b.cyl((0, ya, zc), tube_d, L * 0.55, mat)                                                  # main tube
    # objective: cone up from the tube, bell, sunshade lip, recessed lens
    b.cyl((0, ya, zc - L * 0.255), obj_d, L * 0.05, mat, d2=tube_d + 1, steps=3)
    b.cyl((0, ya, zc - L * 0.375), obj_d, L * 0.2, mat)
    b.cyl((0, ya, zc - L * 0.482), obj_d * 1.04, L * 0.02, mat)
    b.cyl((0, ya, zc - L * 0.4915), obj_d * 0.9, 0.8, "rubber")
    b.cyl((0, ya, zc - L * 0.4935), obj_d * 0.82, 1.2, "glass")
    # eyepiece: cone, ocular housing, zoom ring, rubber eye ring, lens
    b.cyl((0, ya, zc + L * 0.265), tube_d + 1, L * 0.04, mat, d2=eye_d, steps=3)
    b.cyl((0, ya, zc + L * 0.375), eye_d, L * 0.18, mat)
    b.cyl((0, ya, zc + L * 0.3), eye_d * 0.94, L * 0.035, "steel_dark")                        # zoom ring
    for ang in (0, 45, 90, 135):
        b.box(-1.6, 1.6, ya - eye_d * 0.49, ya + eye_d * 0.49, zc + L * 0.285, zc + L * 0.315, "steel_dark",
              rot=(0, 0, ang), pivot=(0, ya, zc + L * 0.3))
    b.cyl((0, ya, zc + L * 0.472), eye_d * 1.05, L * 0.03, "rubber")
    b.cyl((0, ya, zc + L * 0.488), eye_d * 0.76, 1.2, "glass")
    if turrets:
        for axis, c in (("y", (0, ya + tube_d / 2 + 2, zc)), ("x", (tube_d / 2 + 2, ya, zc))):
            off = (0, 6, 0) if axis == "y" else (6, 0, 0)
            b.cyl((c[0] + off[0] * 0.3, c[1] + off[1] * 0.3, c[2]), 24, 5, mat, axis=axis)          # turret base
            b.cyl((c[0] + off[0], c[1] + off[1], c[2]), 20, 9, "steel_dark", axis=axis)             # knurled drum
            b.cyl((c[0] + off[0] * 1.9, c[1] + off[1] * 1.9, c[2]), 17, 2.4, mat, axis=axis)        # cap
        b.cyl((-tube_d / 2 - 4, ya, zc), 18, 7, "steel_dark", axis="x")                            # parallax knob
        b.box(-tube_d / 2 - 1, tube_d / 2 + 1, ya - 7, ya + 7, zc - 13, zc + 13, mat)              # saddle
    if mount_y is not None:
        for dz in (-L * 0.16, L * 0.16):
            z = zc + dz
            b.box(-12, 12, mount_y, ya - tube_d / 2 + 2, z - 9, z + 9, "alloy")                    # ring base
            b.cyl((0, ya, z), tube_d + 7, 16, "alloy")                                             # ring
            b.box(-tube_d / 2 - 6, tube_d / 2 + 6, ya - 2.5, ya + 2.5, z - 8.5, z + 8.5, "alloy")  # split flanges
            for sx in (-1, 1):
                for zz in (z - 5, z + 5):
                    b.bc((sx * (tube_d / 2 + 4), ya + 3, zz), (3, 1.4, 3), "steel")                 # cap screws
            b.box(-13, -12, mount_y + 1, mount_y + 6, z - 4, z + 4, "steel")                       # clamp nut
        b.box(-10, 10, mount_y - 3, mount_y, zc - L * 0.25, zc + L * 0.25, "steel_dark")           # base rail
