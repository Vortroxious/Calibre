"""Revolvers, rebuilt to real dimensions: S&W Model 29 (6.5"), Colt Python (6"), S&W 642 Airweight, Ruger
Single-Six (5.5")."""
import math

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, dry_fire, apply_hidden, moving)
from ..templates import revolver_reload, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import pins, screw
from ..pistolkit import guard, trigger, control, rev_cylinder, rev_grip, _rk


def _inspect(m):
    """Placeholder: build_assets replaces every inspect with the generated close-up one (cs2.py)."""
    return Anim(m, "inspect", 1.0)


def _hands(m, gp, A, y_bot, z_f, z_b):
    c = _rk(gp, A, (0, (gp[1] + y_bot) / 2 + 8, (z_f + z_b) / 2))
    add_arms(m, right_hand=(6, round(c[1]), round(c[2])), left_hand=(-14, round(c[1]) - 4, round(c[2]) - 10),
             right_rot=(34, 18, 6), left_rot=(34, -26, -6))


def _da_hammer(body, pivot, mat, w=8.0, spur=16.0):
    """Double-action hammer, drawn down (at rest): body in the frame slot, wide checkered spur, firing-pin nose."""
    h = body.bone("hammer", pivot=pivot)
    px, py, pz = pivot
    h.box(-w / 2 + 1, w / 2 - 1, py - 4, py + 22, pz - 5, pz + 3, mat)
    h.box(-w / 2 + 1.5, w / 2 - 1.5, py + 14, py + 20, pz - 7.5, pz - 5, "steel_dark")          # nose
    h.box(-w / 2, w / 2, py + 20, py + 26, pz - 2, pz + spur, mat, rot=(-18, 0, 0), pivot=(0, py + 22, pz))
    for i in range(4):
        h.box(-w / 2 + 0.5, w / 2 - 0.5, py + 26, py + 26.5, pz + 3 + i * 3, pz + 4.4 + i * 3, "steel_dark",
              rot=(-18, 0, 0), pivot=(0, py + 22, pz))
    return h


def _rear_sight(body, z0, z1, top, mat="steel_dark", w=16.0, h=7.0, outline="sight_white"):
    """Micrometer rear sight: long leaf, blade with a square notch, elevation and windage screws."""
    body.box(-w * 0.4, w * 0.4, top, top + 2.4, z0, z1, mat)
    body.box(-w / 2, -2, top + 2.4, top + h, z1 - 5, z1, mat)
    body.box(2, w / 2, top + 2.4, top + h, z1 - 5, z1, mat)
    body.box(-w / 2, w / 2, top + 2.4, top + h * 0.55, z1 - 5, z1, mat)
    if outline:
        body.box(-3.2, -2.2, top + h * 0.55, top + h - 0.5, z1 - 0.05, z1 + 0.15, outline)
        body.box(2.2, 3.2, top + h * 0.55, top + h - 0.5, z1 - 0.05, z1 + 0.15, outline)
    body.box(-2, 2, top + 2.4, top + 3.2, z0 + (z1 - z0) * 0.35, z0 + (z1 - z0) * 0.35 + 4, "steel")
    body.box(w / 2, w / 2 + 2, top + 3, top + h - 0.6, z1 - 4.5, z1 - 0.5, "steel")


def _ramp_sight(body, z_front, z_rear, top, h, mat, insert="sight_orange", w=3.4, base_w=8.0):
    """Ramped front blade on a base, with a coloured insert facing the shooter."""
    body.box(-base_w / 2, base_w / 2, top, top + 2.4, z_front - 2, z_rear + 4, mat)
    body.taper(-w / 2, w / 2, z_front, z_rear - 4, top + 2.6, top + h, top + 2.2, top + 2.2, mat)
    body.box(-w / 2, w / 2, top + 2.2, top + h, z_rear - 4, z_rear, mat)
    if insert:
        body.box(-w / 2 + 0.5, w / 2 - 0.5, top + h * 0.45, top + h - 0.4, z_rear - 0.05, z_rear + 0.2, insert)


# =================================================================================================
# S&W Model 29, 6 1/2"  (N frame, .44 Magnum, ~305 mm long)
# =================================================================================================
def model29():
    m = new_gun("model29")
    body = m["body"]
    bl = "steel"
    cy = -14.5
    body.chamfer_box(-12, 12, 8.4, 16, -32, 46, bl, ch=2.6, edges="top")           # top strap
    body.box(-12, 12, -46, -37.6, -32, 36, bl)                                      # under the cylinder
    body.box(-12, 12, -46, 16, -32, -12.4, bl)                                      # barrel boss
    body.box(-12, 12, -44, 14, 34, 46, bl)                                          # recoil shield
    body.box(-12, 12, -46, 2, 44, 60, bl)                                           # rear of the frame
    for sx in (-1, 1):                                                              # hammer-slot cheeks
        xs = sorted((sx * 4.5, sx * 12))
        body.box(xs[0], xs[1], 2, 13, 44, 57, bl)
    body.box(12, 12.6, -42, -4, 2, 56, bl)                                          # side plate (right)
    for y, z in ((-8, 50), (-40, 8), (-40, 50), (-22, 4)):
        screw(body, 12.6, y, z, d=4.6)
    body.cyl((0, 0, -109.5), 21, 155, bl)                                           # barrel -187 .. -32
    body.cyl((0, 0, -187.3), 17, 0.6, bl)
    body.cyl((0, 0, -187.8), 11.2, 0.5, "rubber")
    body.box(-5, 5, 9, 16, -187, -32, bl)                                           # rib
    for i in range(9):
        body.box(-4, 4, 16, 16.4, -180 + i * 16, -172 + i * 16, "rubber")
    body.chamfer_box(-7.5, 7.5, -26, -8, -152, -32, bl, ch=3.5, edges="bottom")     # ejector-rod shroud
    body.box(-5, 5, -24, -10, -156, -152, bl)
    _ramp_sight(body, -186, -158, 16, 12, bl)
    _rear_sight(body, 8, 58, 16)
    guard(body, -36, 24, -46, -78, bl, w=8, th=4.2, style="round")
    trigger(body, (0, -46, -4), mat=bl, length=24, w=9)
    _da_hammer(body, (0, -12, 54), bl, w=9, spur=17)
    control(body, "latch", (-12, -10, 44),
            [(-14.6, -12, -15, -5, 37, 51, bl), (-15.4, -14.6, -13.6, -6.4, 39, 49, "steel_dark")], press=(0, 0, -4))
    pins(body, 12, [(-30, 30), (-14, 40)], d=3.6, mat="steel_dark")
    gp, A = (0, -44, 44), -25.0
    rev_grip(body, gp, A, -150, 28, 62, bl, "wood", hw=7, proud=9, flare=6, line_mat="wood_red",
             medallion="steel_light")
    rev_cylinder(m, cy, 6, 43.5, 44.5, -11.5, 14.5, 11.6, 30, mat=bl, crane_pivot=(-10, -36, 0), rod_len=112)
    _hands(m, gp, A, -150, 28, 62)
    add_sockets(m, muzzle=(0, 0, -189), optic=(0, 16.4, -90), eject=None, sight=(0, 23, 58))

    def fire(name, aim):
        a = Anim(m, name, 0.5)
        k = 0.45 if aim else 1.0
        # double action: trigger pull cocks & rotates, then the hammer falls
        a.key("trigger", 0.0, rot=(-14, 0, 0))
        a.key("trigger", 0.12, rot=(0, 0, 0), e="outquad")
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.08, rot=(0, 0, 0))
        a.key("cylinder", 0.2, rot=(0, 0, -60), e="outquad")
        a.kick("gun", "rot", 0.0, (24 * k, 1.5 * k, 4 * k), attack=0.03, recover=0.4)
        a.kick("gun", "pos", 0.0, (0, 4 * k, 22 * k), attack=0.025, recover=0.36)
        a.spring("gun", "rot", 0.05, (2.0 * k, 0, 1.5 * k), freq=5, damp=8)
        return a

    def inspect():
        a = Anim(m, "inspect", 4.2)
        a.mv("gun", 0.0, 0.35, pos=(-40, 30, 30), rot=(10, -10, 26))
        a.mv("arm_right", 0.2, 0.3, pos=(-2, 6, -8), rot=(0, -3, 3))
        a.mv("arm_right", 0.36, 0.46, pos=(0, 0, 0), rot=(0, 0, 0))
        a.sound(0.3, "cylinder_latch")
        a.mv("arm_left", 0.1, 0.34, pos=(14, 10, -30), rot=(0, 10, -10))
        a.key("crane", 0.0, rot=(0, 0, 0))
        a.key("crane", 0.36, rot=(0, 0, 0))
        a.key("crane", 0.5, rot=(0, 0, 78), e="outback")
        a.sound(0.46, "cylinder_open")
        # spin it with the support fingers
        a.mv("arm_left", 0.6, 0.72, pos=(20, -4, -10), rot=(0, 10, -20))
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.7, rot=(0, 0, 0))
        a.key("cylinder", 2.0, rot=(0, 0, 840), e="outcubic")
        a.sound(0.72, "cylinder_spin")
        a.mv("arm_left", 0.75, 1.0, pos=(-40, -60, 40), rot=(20, -10, 10))
        a.mv("gun", 0.6, 1.4, pos=(-50, 44, 20), rot=(22, -24, 34), e="inoutsine")
        # wrist-flick it closed
        a.mv("gun", 2.1, 2.28, pos=(-60, 40, 20), rot=(14, -10, 60), e="inquad")
        a.mv("gun", 2.28, 2.42, pos=(-30, 28, 30), rot=(4, -6, -14), e="outquad")
        a.key("crane", 2.26, rot=(0, 0, 78))
        a.key("crane", 2.38, rot=(0, 0, 0), e="inquad")
        a.sound(2.38, "cylinder_close")
        a.spring("gun", "rot", 2.4, (0, 0, -3.0), freq=6, damp=8)
        a.mv("arm_left", 2.5, 3.0, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 2.6, 4.15)
        return a

    anims = [idle(m), draw(m, 0.6, sound="draw_pistol", style="pistol"), fire("fire", False), fire("fire_aim", True),
             revolver_reload(m, "reload"), inspect(), dry_fire(m)]
    apply_hidden(anims, ["speedloader", "brass"])
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.08, -0.29], "rot": [0, 6, 0]}, "ads": {"dist": 0.36}})


# =================================================================================================
# Colt Python, 6"  (.357 Magnum, vent rib, full underlug, ~292 mm long)
# =================================================================================================
def python():
    m = new_gun("python")
    body = m["body"]
    bl = "steel_dark"
    cy = -13.3
    body.chamfer_box(-11.5, 11.5, 7.4, 14.5, -30, 44, bl, ch=2.4, edges="top")      # top strap
    body.box(-11.5, 11.5, -42, -34.2, -30, 34, bl)
    body.box(-11.5, 11.5, -42, 14.5, -30, -11, bl)
    body.box(-11.5, 11.5, -40, 12, 32, 44, bl)                                      # recoil shield
    body.box(-11.5, 11.5, -42, 0, 42, 58, bl)
    for sx in (-1, 1):
        xs = sorted((sx * 4.5, sx * 11.5))
        body.box(xs[0], xs[1], 0, 11, 42, 55, bl)
    body.box(-12.1, -11.5, -38, -2, 0, 54, bl)                                      # side plate (left on a Colt)
    for y, z in ((-6, 48), (-36, 6), (-36, 48)):
        screw(body, -12.1, y, z, d=4.4)
    body.cyl((0, 0, -102), 19, 144, bl)                                             # barrel -174 .. -30
    body.cyl((0, 0, -174.3), 15, 0.6, bl)
    body.cyl((0, 0, -174.8), 9.2, 0.5, "rubber")
    body.chamfer_box(-9.5, 9.5, -27, -6, -174, -30, bl, ch=4.5, edges="bottom")     # full underlug
    body.box(-3, 3, -19, -11, -174.6, -174, "rubber")                               # ejector-rod recess
    body.box(-4.5, 4.5, 17, 20.5, -174, -30, bl)                                    # ventilated rib
    for i in range(7):
        z = -172 + i * 23
        body.box(-3.5, 3.5, 8.5, 17, z, z + 9, bl)                                  # rib posts
    for i in range(10):
        body.box(-3.6, 3.6, 20.5, 20.9, -168 + i * 14, -161 + i * 14, "rubber")
    _ramp_sight(body, -172, -148, 20.5, 10, bl)
    _rear_sight(body, 10, 54, 14.5)
    guard(body, -34, 22, -42, -72, bl, w=8, th=4, style="round")
    trigger(body, (0, -42, -4), mat=bl, length=22, w=8)
    _da_hammer(body, (0, -12, 52), bl, w=8, spur=16)
    control(body, "latch", (-11.5, -10, 40),
            [(-14.2, -11.5, -15, -6, 32, 46, bl), (-15, -14.2, -13.5, -7.5, 34, 44, "steel")], press=(0, 0, 4))
    pins(body, 11.5, [(-28, 28)], d=3.6, mat="steel")
    gp, A = (0, -40, 42), -25.0
    rev_grip(body, gp, A, -142, 26, 58, bl, "wood", hw=7, proud=8.5, flare=6, line_mat="wood_red", medallion="brass")
    rev_cylinder(m, cy, 6, 39.6, 41, -10, 13.3, 10.2, 30, mat=bl, crane_pivot=(-10, -34, 0), rod_len=104)
    _hands(m, gp, A, -142, 26, 58)
    add_sockets(m, muzzle=(0, 0, -176), optic=(0, 21, -90), eject=None, sight=(0, 21.5, 54))

    def fire(name, aim):
        a = Anim(m, name, 0.5)
        k = 0.45 if aim else 1.0
        a.key("trigger", 0.0, rot=(-14, 0, 0))
        a.key("trigger", 0.12, rot=(0, 0, 0), e="outquad")
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.08, rot=(0, 0, 0))
        a.key("cylinder", 0.2, rot=(0, 0, -60), e="outquad")
        a.kick("gun", "rot", 0.0, (22 * k, 1.5 * k, 4 * k), attack=0.03, recover=0.4)
        a.kick("gun", "pos", 0.0, (0, 4 * k, 20 * k), attack=0.025, recover=0.36)
        a.spring("gun", "rot", 0.05, (2.0 * k, 0, 1.5 * k), freq=5, damp=8)
        return a

    anims = [idle(m), draw(m, 0.6, sound="draw_pistol", style="pistol"), fire("fire", False), fire("fire_aim", True),
             revolver_reload(m, "reload"), _inspect(m), dry_fire(m)]
    apply_hidden(anims, ["speedloader", "brass"])
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.08, -0.29], "rot": [0, 6, 0]}, "ads": {"dist": 0.36}})


# =================================================================================================
# S&W 642 Airweight  (J frame, 5-shot .38, enclosed hammer, ~160 mm long)
# =================================================================================================
def sw642():
    m = new_gun("sw642")
    body = m["body"]
    al = "stainless"
    cy = -10.8
    body.chamfer_box(-10.5, 10.5, 6.4, 13, -20, 34, al, ch=2.2, edges="top")        # top strap
    body.box(-10.5, 10.5, -35, -27.8, -20, 32, al)
    body.box(-10.5, 10.5, -35, 13, -20, -9.4, al)
    body.box(-10.5, 10.5, -33, 12, 30.5, 40, al)                                    # recoil shield
    body.chamfer_box(-10.5, 10.5, -35, 19, 38, 56, al, ch=5, edges="top")           # humpback over the hammer
    body.box(-9, 9, 13, 18, 30, 40, al)
    body.box(-1.3, 1.3, 13, 13.5, -18, 34, "rubber")                                # sight groove
    body.box(-1.3, 1.3, 18.6, 19.2, 36, 54, "rubber")
    body.box(10.5, 11, -31, -4, 2, 50, al)                                          # side plate
    for y, z in ((-8, 46), (-29, 8), (-29, 44)):
        screw(body, 11, y, z, d=4)
    body.cyl((0, 0, -44), 15, 48, al)                                               # 1 7/8" barrel -68 .. -20
    body.cyl((0, 0, -68.3), 12, 0.6, al)
    body.cyl((0, 0, -68.8), 9, 0.5, "rubber")
    body.chamfer_box(-6, 6, -22, -6, -64, -20, al, ch=3, edges="bottom")            # ejector shroud
    body.box(-3.5, 3.5, 6.5, 9, -68, -20, al)                                       # rib
    body.taper(-1.5, 1.5, -68, -50, 9.5, 18, 9, 9, al)                              # integral ramp front sight
    body.box(-1.5, 1.5, 9, 18, -50, -47, al)
    for i in range(4):
        body.box(-1.6, 1.6, 10.5 + i * 2, 11.3 + i * 2, -47.05, -46.6, "rubber")
    guard(body, -30, 18, -35, -60, al, w=7.5, th=3.6, style="round")
    trigger(body, (0, -35, -4), mat=al, length=20, w=7.5)
    control(body, "latch", (-10.5, -7, 38),
            [(-13, -10.5, -11, -3, 32, 44, al), (-13.8, -13, -10, -4, 34, 42, "steel_dark")], press=(0, 0, -4))
    pins(body, 10.5, [(-24, 26)], d=3.2, mat="steel")
    gp, A = (0, -33, 40), -26.0
    rev_grip(body, gp, A, -100, 22, 52, al, "rubber", hw=6.5, proud=7, flare=3, style="grooves",
             line_mat="polymer_grey", medallion=None)
    rev_cylinder(m, cy, 5, 33.2, 39, -9, 10.8, 9.6, 29, mat=al, crane_pivot=(-9, -29, 0), rod_len=40)
    _hands(m, gp, A, -100, 22, 52)
    add_sockets(m, muzzle=(0, 0, -70), eject=None, sight=(0, 18.4, 40))

    def fire(name, aim):
        a = Anim(m, name, 0.42)
        k = 0.45 if aim else 1.0
        a.key("trigger", 0.0, rot=(-16, 0, 0))
        a.key("trigger", 0.12, rot=(0, 0, 0), e="outquad")
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.08, rot=(0, 0, 0))
        a.key("cylinder", 0.2, rot=(0, 0, -72), e="outquad")
        a.kick("gun", "rot", 0.0, (26 * k, 2 * k, 5 * k), attack=0.025, recover=0.36)    # light frame, big flip
        a.kick("gun", "pos", 0.0, (0, 4 * k, 18 * k), attack=0.022, recover=0.32)
        a.spring("gun", "rot", 0.05, (2.4 * k, 0, 1.8 * k), freq=5, damp=8)
        return a

    def inspect():
        # slow double-action press on a cleared gun: watch the cylinder index chamber by chamber
        a = Anim(m, "inspect", 3.8)
        a.mv("gun", 0.0, 0.4, pos=(-40, 30, 30), rot=(6, 46, 16))
        a.key("trigger", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        for i in range(3):
            t = 0.55 + i * 0.6
            a.key("trigger", t, rot=(0, 0, 0))
            a.key("trigger", t + 0.36, rot=(-16, 0, 0), e="inoutsine")
            a.key("trigger", t + 0.5, rot=(0, 0, 0), e="outquad")
            a.key("cylinder", t + 0.04, rot=(0, 0, -72 * i))
            a.key("cylinder", t + 0.34, rot=(0, 0, -72 * (i + 1)), e="inoutsine")
            a.sound(t + 0.36, "dry_fire")
            a.spring("gun", "rot", t + 0.36, (0.6, 0, 0), freq=9, damp=12)
        a.mv("gun", 1.2, 1.9, pos=(-44, 34, 26), rot=(10, 30, 26))
        a.mv("gun", 2.3, 2.7, pos=(-40, 40, 20), rot=(14, -40, -10))           # show the stainless side
        _settle(a, 2.9, 3.75)
        return a

    anims = [idle(m), draw(m, 0.5, sound="draw_pistol", style="pistol"), fire("fire", False), fire("fire_aim", True),
             revolver_reload(m, "reload", length=3.0), inspect(), dry_fire(m)]
    apply_hidden(anims, ["speedloader", "brass"])
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.08, -0.3], "rot": [0, 6, 0]}, "ads": {"dist": 0.36}})


# =================================================================================================
# Ruger Single-Six, 5 1/2"  (single action .22, loading gate, ~280 mm long)
# =================================================================================================
def singlesix():
    m = new_gun("singlesix")
    body = m["body"]
    bl = "steel"
    gf = "alloy"                                                                    # grip frame
    cy = -12.0
    body.chamfer_box(-10.5, 10.5, 7.2, 14, -16, 36, bl, ch=2.2, edges="top")        # flat-top strap
    body.box(-10.5, 10.5, -38, -31, -16, 34, bl)
    body.box(-10.5, 10.5, -38, 14, -16, -7, bl)
    body.chamfer_box(-10.5, 10.5, -36, 12, 32.6, 46, bl, ch=3.5, edges="top")       # recoil shield
    body.box(-8.5, 8.5, -30, -4, 44, 54, bl)
    body.cyl((0, 0, -86), 15.5, 140, bl)                                            # barrel -156 .. -16
    body.cyl((0, 0, -156.3), 12, 0.6, bl)
    body.cyl((0, 0, -156.8), 5.6, 0.5, "rubber", sides=8)
    _ramp_sight(body, -154, -134, 7.4, 13, bl, insert=None, w=2.8, base_w=6)
    _rear_sight(body, 12, 44, 14, w=13, h=6, outline=None)
    # ejector-rod housing on the right, low
    body.cyl((9, -14, -70), 10.5, 108, bl, sides=8)
    body.box(13.6, 14.4, -15.5, -12.5, -120, -24, "rubber")                         # rod slot
    body.cyl((9, -14, -124.5), 9, 1.2, "steel_dark", sides=8)
    ej = body.bone("ejector", pivot=(9, -14, 0))
    ej.cyl((9, -14, -64), 4.6, 116, "steel_light", sides=8)
    ej.box(13.5, 18.5, -18.5, -9.5, -121, -110, "steel_light")                      # thumb button
    ej.box(18.5, 19, -17.5, -10.5, -120, -111, "steel_dark")
    # base pin and its latch
    body.cyl((0, cy, -22), 6, 16, "steel_light", sides=8)
    body.cyl((0, cy, -31), 8.5, 4, "steel_light", sides=8)
    body.box(-12, -10.5, -15, -9, -14, -8, "steel_dark")
    gate = body.bone("gate", pivot=(11, -24, 36))
    gate.box(9, 12.6, -27, -3, 33, 45.4, bl)
    gate.box(12.6, 13.4, -12, -5, 35, 44, bl)                                       # thumb notch
    moving(m, "gate", rot=(0, 0, -80))
    pins(body, 10.5, [(-34, 2), (-34, 22), (-20, 40)], d=3.4, mat="steel_dark")
    # grip frame: guard, straps, two-piece smooth stocks
    body.box(-6, 6, -44, -37, -24, 54, gf)
    guard(body, -22, 26, -44, -64, gf, w=7, th=3.6, style="round")
    trigger(body, (0, -44, 2), mat=bl, length=17, w=5.5)
    gp, A = (0, -32, 50), -30.0
    rev_grip(body, gp, A, -132, 30, 58, gf, "wood_red", hw=6, proud=7, flare=3.5, style="smooth",
             medallion="steel_light", wrap_front=False)
    ham = body.bone("hammer", pivot=(0, -16, 48))                                   # drawn at full cock
    hr = dict(rot=(30, 0, 0), pivot=(0, -16, 48))
    ham.box(-3.5, 3.5, -16, 18, 44, 52, bl, **hr)
    ham.box(-2.4, 2.4, 10, 17, 41, 44, "steel_dark", **hr)
    ham.box(-5, 5, 14, 21, 50, 66, bl, **hr)                                        # wide spur
    for i in range(4):
        ham.box(-4.4, 4.4, 21, 21.5, 52 + i * 3.2, 53.6 + i * 3.2, "steel_dark", **hr)
    rev_cylinder(m, cy, 6, 36.5, 38, -6, 12.0, 7.0, 15, mat=bl, crane=False, parent="body", flutes=True,
                 bullet="steel_dark", cases=False, rim=0.9)
    # the chamber lined up with the gate sits at 4:30 seen from behind (right, low)
    gx, gy = math.cos(math.radians(-30)) * 12.0, cy + math.sin(math.radians(-30)) * 12.0
    rl = m["gun"].bone("round_load", pivot=(gx, gy, 34))
    rl.round_((gx, gy, 34 + 12), 25, 5.8)
    br = m["gun"].bone("brass", pivot=(gx, gy, 34))
    br.cyl((gx, gy, 24), 5.8, 15, "brass", sides=8)
    br.cyl((gx, gy, 31.8), 7, 1, "brass", sides=8)
    _hands(m, gp, A, -132, 30, 58)
    add_sockets(m, muzzle=(0, 0, -158), eject=None, sight=(0, 20, 44))

    def fire(name, aim):
        a = Anim(m, name, 0.7)
        k = 0.45 if aim else 1.0
        a.key("trigger", 0.0, rot=(-10, 0, 0))
        a.key("trigger", 0.08, rot=(0, 0, 0), e="outquad")
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 0.012, rot=(-44, 0, 0), e="inquad")
        a.kick("gun", "rot", 0.0, (12 * k, 1 * k, 2 * k), attack=0.025, recover=0.3)
        a.kick("gun", "pos", 0.0, (0, 3 * k, 10 * k), attack=0.022, recover=0.28)
        a.spring("gun", "rot", 0.04, (1.2 * k, 0, 1.0 * k), freq=5, damp=8)
        # thumb rides the hammer spur back to full cock; the cylinder indexes as the hand rises
        a.mv("arm_right", 0.24, 0.34, pos=(-3, 18, 2), rot=(-14, -6, 0))
        a.key("hammer", 0.34, rot=(-44, 0, 0))
        a.key("hammer", 0.5, rot=(4, 0, 0), e="inoutsine")
        a.key("hammer", 0.54, rot=(0, 0, 0), e="outquad")
        a.sound(0.52, "hammer_thumb")
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.36, rot=(0, 0, 0))
        a.key("cylinder", 0.5, rot=(0, 0, -60), e="inoutsine")
        a.mv("arm_right", 0.54, 0.68, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 0.3, 0.45, pos=(0, 0, 0), rot=(-2 * k, 0, 0))
        a.mv("gun", 0.5, 0.69, pos=(0, 0, 0), rot=(0, 0, 0))
        return a

    def dry():
        a = dry_fire(m)
        a.key("hammer", 0.04, rot=(0, 0, 0))
        a.key("hammer", 0.06, rot=(-44, 0, 0), e="inquad")
        a.key("hammer", 0.25, rot=(-44, 0, 0))
        return a

    port_pos, port_tilt = (-30, 30, 40), (8, -16, 48)
    rest = {"gun": {"pos": port_pos, "rot": port_tilt}, "arm_left": {"pos": OFF_LEFT, "rot": OFF_LEFT_ROT},
            "gate": {"rot": (0, 0, -80)}, "hammer": {"rot": (-14, 0, 0)}}

    def reload_start():
        a = Anim(m, "reload_start", 0.7)
        a.mv("gun", 0.0, 0.35, pos=port_pos, rot=port_tilt)
        # thumb the hammer to half-cock so the cylinder spins free, flip the gate open
        a.mv("arm_right", 0.05, 0.16, pos=(-3, 18, 2), rot=(-14, -6, 0))
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 0.14, rot=(0, 0, 0))
        a.key("hammer", 0.22, rot=(-14, 0, 0), e="inoutsine")
        a.sound(0.22, "hammer_thumb")
        a.mv("arm_right", 0.26, 0.4, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_left", 0.0, 0.3, pos=(30, 20, 120), rot=(-20, 30, 40))
        a.key("gate", 0.0, rot=(0, 0, 0))
        a.key("gate", 0.36, rot=(0, 0, 0))
        a.key("gate", 0.46, rot=(0, 0, -80), e="outquad")
        a.sound(0.44, "loading_gate")
        a.mv("arm_left", 0.5, 0.68, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
        return a

    def reload_loop():
        # one chamber: punch the empty out with the rod, thumb a round in, click the cylinder round to the next one
        L = 0.95
        a = Anim(m, "reload_loop", L, rest=rest)
        a.mv("arm_right", 0.0, 0.12, pos=(-2, 6, -60), rot=(0, -10, 0))
        a.key("ejector", 0.0, pos=(0, 0, 0))
        a.key("ejector", 0.12, pos=(0, 0, 0))
        a.key("ejector", 0.22, pos=(0, 0, 52), e="outquad")
        a.sound(0.2, "ejector_rod")
        a.key("ejector", 0.32, pos=(0, 0, 0), e="inoutsine")
        a.mv("arm_right", 0.32, 0.42, pos=(0, 0, 0), rot=(0, 0, 0))
        a.show("brass", 0.12, 0.6)
        a.key("brass", 0.12, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("brass", 0.22, pos=(0, 0, 30), e="outquad")
        a.key("brass", 0.6, pos=(40, -160, 120), rot=(80, 0, 60), e="inquad")
        a.show("round_load", 0.3, 0.7)
        a.at_hand("round_load", 0.3, rot=(30, 0, 30))
        a.grab("arm_left", "round_load", 0.32, 0.66, fade_in=0.02, fade_out=0.05)
        a.key("round_load", 0.56, pos=(0, 0, 10), rot=(0, 0, 0), e="outcubic")
        a.key("round_load", 0.66, pos=(0, 0, -10), rot=(0, 0, 0), e="inquad")
        a.sound(0.64, "round_insert")
        a.event(0.64, "ammo")
        a.mv("arm_left", 0.7, 0.85, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.72, rot=(0, 0, 0))
        a.key("cylinder", 0.86, rot=(0, 0, -60), e="inoutsine")
        a.sound(0.86, "click_small")
        a.spring("gun", "rot", 0.64, (0.6, 0, 0.4), freq=8, damp=10)
        return a

    def reload_end():
        a = Anim(m, "reload_end", 0.8, rest=rest)
        a.mv("arm_left", 0.0, 0.18, pos=(30, 20, 120), rot=(-20, 30, 40))
        a.key("gate", 0.18, rot=(0, 0, -80))
        a.key("gate", 0.26, rot=(0, 0, 0), e="inquad")
        a.sound(0.26, "loading_gate")
        a.mv("arm_right", 0.3, 0.4, pos=(-3, 18, 2), rot=(-14, -6, 0))
        a.key("hammer", 0.4, rot=(-14, 0, 0))
        a.key("hammer", 0.5, rot=(4, 0, 0), e="inoutsine")
        a.key("hammer", 0.54, rot=(0, 0, 0))
        a.sound(0.5, "hammer_cock")
        a.mv("arm_right", 0.55, 0.68, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_left", 0.3, 0.65, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 0.3, 0.78, pos=(0, 0, 0), rot=(0, 0, 0))
        return a

    def inspect():
        # half-cock, open the gate and spin the cylinder past the clicks, close up and ease the hammer
        a = Anim(m, "inspect", 4.2)
        a.mv("gun", 0.0, 0.4, pos=(-40, 30, 30), rot=(6, -30, -24))
        a.mv("arm_right", 0.3, 0.4, pos=(-3, 18, 2), rot=(-14, -6, 0))
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 0.38, rot=(0, 0, 0))
        a.key("hammer", 0.46, rot=(-14, 0, 0))
        a.sound(0.46, "hammer_thumb")
        a.mv("arm_right", 0.5, 0.62, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_left", 0.3, 0.6, pos=(30, 20, 120), rot=(-20, 30, 40))
        a.key("gate", 0.0, rot=(0, 0, 0))
        a.key("gate", 0.6, rot=(0, 0, 0))
        a.key("gate", 0.7, rot=(0, 0, -80), e="outquad")
        a.sound(0.68, "loading_gate")
        a.mv("arm_left", 0.75, 0.9, pos=(34, 0, 110), rot=(-20, 30, 60))
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.9, rot=(0, 0, 0))
        a.key("cylinder", 2.1, rot=(0, 0, -720), e="outcubic")
        for i in range(8):
            a.sound(0.95 + 0.06 * i + 0.012 * i * i, "click_small")
        a.mv("gun", 0.9, 1.6, pos=(-50, 40, 30), rot=(10, -50, -36))
        a.key("gate", 2.3, rot=(0, 0, -80))
        a.key("gate", 2.38, rot=(0, 0, 0), e="inquad")
        a.sound(2.38, "loading_gate")
        a.mv("arm_left", 2.4, 2.8, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_right", 2.7, 2.8, pos=(-3, 18, 2), rot=(-14, -6, 0))
        a.key("hammer", 2.8, rot=(-14, 0, 0))
        a.key("hammer", 2.9, rot=(4, 0, 0), e="inoutsine")
        a.key("hammer", 2.94, rot=(0, 0, 0))
        a.sound(2.9, "hammer_cock")
        a.mv("arm_right", 2.95, 3.1, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.0, 4.15)
        return a

    anims = [idle(m), draw(m, 0.55, sound="draw_pistol", style="pistol"), fire("fire", False), fire("fire_aim", True),
             reload_start(), reload_loop(), reload_end(), inspect(), dry()]
    apply_hidden(anims, ["round_load", "brass"])
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.08, -0.29], "rot": [0, 6, 0]}, "ads": {"dist": 0.36}})


def saa():
    """Colt Single Action Army (5.5 in): 279 mm long, the pattern the Single-Six copies at full size. Built from the
    Single-Six with the frame and cylinder widened for .45 Colt, a steel grip frame, walnut stocks and a
    case-hardened frame."""
    asset = singlesix()
    m = asset.model
    m.name = "saa"
    k = 1.12                                                    # .45 Colt: wider frame, 41 mm cylinder
    arms = {b.name for b in m.order if b.name.startswith("arm_")}
    remap = {"alloy": "steel_dark", "wood_red": "wood", "steel": "steel_dark"}
    for b in m.order:
        p = b
        under_arm = False
        while p:
            if p.name in arms:
                under_arm = True
            p = p.parent
        if under_arm:
            continue
        b.pivot = (b.pivot[0] * k, b.pivot[1] * k, b.pivot[2])
        for c in b.cubes:
            c.x0, c.x1, c.y0, c.y1 = c.x0 * k, c.x1 * k, c.y0 * k, c.y1 * k
            if c.pivot:
                c.pivot = (c.pivot[0] * k, c.pivot[1] * k, c.pivot[2])
            c.mat = remap.get(c.mat, c.mat)
    return asset


GUNS = {"model29": model29, "python": python, "sw642": sw642, "singlesix": singlesix, "saa": saa}
