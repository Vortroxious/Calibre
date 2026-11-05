"""Reusable gun part builders (mm, render space, barrel towards -Z, bore axis at y=0)."""
from __future__ import annotations

import math

from .core import Bone


def pistol_grip(b: Bone, top_z, top_y=-22.0, length=90.0, width=28.0, depth=34.0, angle=-20.0, mat="polymer",
                checker=True):
    """AR/AK-style rifle pistol grip hanging from (0, top_y, top_z), raked back by `angle`."""
    piv = (0, top_y, top_z)
    b.box(-width / 2, width / 2, top_y - length, top_y, top_z - depth / 2, top_z + depth / 2, mat, rot=(angle, 0, 0),
          pivot=piv)
    b.box(-width / 2 + 1, width / 2 - 1, top_y - length + 6, top_y - 14, top_z + depth / 2, top_z + depth / 2 + 5, mat,
          rot=(angle, 0, 0), pivot=piv)  # palm swell
    b.box(-width / 2 - 1, width / 2 + 1, top_y - length - 4, top_y - length, top_z - depth / 2 - 2,
          top_z + depth / 2 + 5, mat, rot=(angle, 0, 0), pivot=piv)
    if checker:
        for i in range(4):
            y = top_y - 22 - i * 16
            b.box(-width / 2 - 0.4, width / 2 + 0.4, y - 4, y, top_z - depth / 2 + 4, top_z + depth / 2 - 4, mat,
                  rot=(angle, 0, 0), pivot=piv)


def trigger_group(m, body: Bone, z, y_top=-22.0, guard_depth=30.0, guard_len=62.0, guard_mat="alloy", width=8.0,
                  trig_mat="steel_dark"):
    """Trigger guard + `trigger` bone. z = trigger pivot z."""
    yb = y_top - guard_depth
    body.box(-width / 2, width / 2, yb - 4, yb, z - guard_len * 0.55, z + guard_len * 0.45, guard_mat)
    body.box(-width / 2, width / 2, yb, y_top, z - guard_len * 0.55, z - guard_len * 0.55 + 5, guard_mat)
    trig = body.bone("trigger", pivot=(0, y_top - 2, z))
    trig.box(-2.5, 2.5, y_top - 22, y_top - 2, z - 3, z + 2, trig_mat, rot=(-10, 0, 0), pivot=(0, y_top - 2, z))
    return trig


def barrel(b: Bone, z0, z1, d=16.0, mat="steel", y=0.0):
    zc = (z0 + z1) / 2
    return b.cyl((0, y, zc), d, abs(z1 - z0), mat)


def flash_hider_a2(b: Bone, z, d=20.0, length=55.0):
    b.cyl((0, 0, z - length / 2), d, length, "steel_dark")
    for i in range(3):
        b.box(-d / 2 - 0.5, d / 2 + 0.5, d / 2 - 3, d / 2 + 0.3, z - length + 6 + i * 10, z - length + 10 + i * 10,
              "rubber")


def muzzle_brake(b: Bone, z, d=26.0, length=60.0, ports=3, mat="steel_dark", w=None):
    w = w or d
    b.box(-w / 2, w / 2, -d / 2, d / 2, z - length, z, mat)
    for i in range(ports):
        zz = z - length + 8 + i * (length - 14) / max(1, ports - 1)
        b.box(-w / 2 - 0.4, w / 2 + 0.4, -d / 2 + 4, d / 2 - 4, zz - 3, zz + 3, "rubber")


def ar_front_sight(b: Bone, z, base_y=10.0, h=55.0):
    b.box(-9, 9, base_y, base_y + 10, z - 12, z + 12, "steel_dark")          # gas block base
    b.box(-4, 4, base_y + 10, base_y + h * 0.7, z - 6, z + 6, "steel_dark")   # tower
    b.box(-9, -5, base_y + h * 0.55, base_y + h, z - 6, z + 6, "steel_dark")  # ears
    b.box(5, 9, base_y + h * 0.55, base_y + h, z - 6, z + 6, "steel_dark")
    b.box(-1.2, 1.2, base_y + h * 0.7, base_y + h * 0.95, z - 1.2, z + 1.2, "steel_dark")  # post


def buis_rear(b: Bone, z, y):
    b.box(-12, 12, y, y + 6, z - 14, z + 14, "alloy")
    b.box(-9, 9, y + 6, y + 22, z - 4, z + 4, "alloy")
    b.box(-3, 3, y + 22, y + 27, z - 3, z + 3, "alloy")
    b.box(-1, 1, y + 22, y + 24, z - 3.2, z - 3, "rubber")


def straight_mag(bone: Bone, top_y, z0, z1, length, width=24.0, mat="steel_dark", base_mat=None, ribs=True, round_d=6.0,
                 round_len=40.0):
    """Mag body hanging straight down from top_y. Round visible on top."""
    bone.box(-width / 2, width / 2, top_y - length, top_y, z0, z1, mat)
    bone.box(-width / 2 - 1.5, width / 2 + 1.5, top_y - length - 6, top_y - length, z0 - 2, z1 + 3, base_mat or mat)
    if ribs:
        bone.box(-width / 2 - 0.6, width / 2 + 0.6, top_y - length + 10, top_y - 20, (z0 + z1) / 2 - 4, (z0 + z1) / 2 + 4,
                 mat)
    bone.round_((0, top_y + round_d / 2 - 1, (z0 + z1) / 2), round_len, round_d)


def curved_mag(bone: Bone, top_y, z_front, depth, length, curve=28.0, segs=5, width=26.0, mat="steel_dark",
               rib_mat=None, round_d=8.0, round_len=50.0, base=True):
    """
    Magazine that curves forward as it goes down (AK, G3, M249-ish). Built from segments rotated
    progressively about their top-front corner. Returns nothing; segments live in the bone.
    """
    seg = length / segs
    y = top_y
    z = z_front
    ang = 0.0
    step = curve / segs
    for i in range(segs):
        a = ang + step / 2
        piv = (0, y, z)
        bone.box(-width / 2, width / 2, y - seg - 0.8, y, z, z + depth, mat, rot=(a, 0, 0), pivot=piv)
        if rib_mat:
            bone.box(-width / 2 - 0.6, width / 2 + 0.6, y - seg * 0.7, y - seg * 0.3, z + depth * 0.3, z + depth * 0.7,
                     rib_mat, rot=(a, 0, 0), pivot=piv)
        # advance along the rotated segment's front edge
        r = math.radians(a)
        y -= seg * math.cos(r)
        z -= seg * math.sin(r)
        ang += step
    if base:
        r = math.radians(ang)
        bone.box(-width / 2 - 1.5, width / 2 + 1.5, y - 6, y, z - 2, z + depth + 3, rib_mat or mat, rot=(ang, 0, 0),
                 pivot=(0, y, z))
    bone.round_((0, top_y + round_d / 2 - 1, z_front + depth / 2), round_len, round_d)


def ar_stock(b: Bone, z0, mat="polymer", tube_mat="alloy", ext=0.0):
    """M4 collapsible stock starting at receiver rear z0."""
    b.cyl((0, -4, z0 + 110), 30, 220, tube_mat)
    s = z0 + 120 + ext
    b.taper(-20, 20, s, s + 100, 14, 14, -50, -70, mat)                     # sloped toe
    b.box(-21, 21, -78, 18, s + 90, s + 104, "rubber")
    b.box(-15, 15, -20, 20, s - 30, s, mat)


def picatinny_handguard(b: Bone, z0, z1, y_top=16.0, y_bot=-30.0, half_w=19.0, mat="alloy", slots=True):
    b.box(-half_w, half_w, y_bot, y_top, z0, z1, mat)
    b.rail(z0 + 4, z1 - 4, y_top, mat="alloy", side="top", slots=slots)
    b.rail(z0 + 4, z1 - 4, y_bot, mat="alloy", side="bottom", slots=slots)
    if slots:
        for i in range(int((z1 - z0) // 40)):
            z = z0 + 14 + i * 40
            b.box(-half_w - 0.5, half_w + 0.5, (y_top + y_bot) / 2 - 6, (y_top + y_bot) / 2 + 6, z, z + 22, "rubber")


def bipod(b: Bone, z, y=-10.0, legs_len=180.0, folded=True, mat="steel_dark"):
    b.box(-14, 14, y - 10, y, z - 14, z + 14, mat)
    for sx in (-1, 1):
        if folded:
            b.box(sx * 6 - 4, sx * 6 + 4, y - 14, y - 6, z - legs_len, z, mat)
        else:
            b.box(sx * 6 - 4, sx * 6 + 4, y - legs_len, y, z - 4, z + 4, mat, rot=(0, 0, sx * 12), pivot=(sx * 6, y, z))


def scope(b: Bone, z_center, y_axis, length=300.0, tube_d=30.0, obj_d=50.0, eye_d=42.0, mat="alloy", mount_y=None,
          turrets=True):
    """Generic riflescope along Z centred on z_center at bore-height y_axis."""
    zc = z_center
    b.cyl((0, y_axis, zc), tube_d, length * 0.55, mat, sides=12)
    b.cyl((0, y_axis, zc - length * 0.36), obj_d, length * 0.24, mat, sides=12)       # objective bell
    b.cyl((0, y_axis, zc + length * 0.36), eye_d, length * 0.22, mat, sides=12)       # eyepiece
    b.cyl((0, y_axis, zc - length * 0.485), obj_d * 0.84, 1.2, "glass", sides=12)
    b.cyl((0, y_axis, zc + length * 0.475), eye_d * 0.8, 1.2, "glass", sides=12)
    if turrets:
        b.cyl((0, y_axis + tube_d / 2 + 8, zc), 22, 16, mat, axis="y", sides=12)
        b.cyl((tube_d / 2 + 8, y_axis, zc), 22, 16, mat, axis="x", sides=12)
    if mount_y is not None:
        for dz in (-length * 0.16, length * 0.16):
            b.box(-12, 12, mount_y, y_axis - tube_d / 2 + 2, zc + dz - 9, zc + dz + 9, "alloy")
            b.box(-17, 17, y_axis - 6, y_axis + 6, zc + dz - 9, zc + dz + 9, "alloy")
