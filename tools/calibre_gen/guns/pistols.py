"""M1911A1, Beretta M9, IMI Desert Eagle .50, S&W Model 29."""
import math

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden, along)
from ..templates import pistol_reload, revolver_reload, _settle, OFF_LEFT, OFF_LEFT_ROT


def _pistol_mag(m, pivot, angle, top_y, bottom_y, z0, z1, width, base_mat="steel_dark", body_mat="steel_dark",
                round_d=9.0, round_len=30.0):
    mag = m["gun"].bone("magazine", pivot=pivot, rot=(angle, 0, 0))
    mag.box(-width / 2, width / 2, bottom_y + 6, top_y, z0, z1, body_mat)
    mag.box(-width / 2 - 1.5, width / 2 + 1.5, bottom_y, bottom_y + 6, z0 - 2, z1 + 3, base_mat)
    mag.round_((0, top_y + round_d / 2 - 1, (z0 + z1) / 2 - 2), round_len, round_d)
    return mag


def _grip(body, pivot, angle, x, y0, y1, z0, z1, mat, panel_mat=None, panel_inset=4.0):
    body.box(-x, x, y0, y1, z0, z1, mat, rot=(angle, 0, 0), pivot=pivot)
    if panel_mat:
        body.box(-x - 2.2, x + 2.2, y0 + 8, y1 - 8, z0 + panel_inset, z1 - panel_inset, panel_mat, rot=(angle, 0, 0),
                 pivot=pivot)
        for sgn in (-1, 1):  # grip screws
            for yy in (y0 + 18, y1 - 18):
                body.box(sgn * (x + 2.2) - 1.5, sgn * (x + 2.2) + 1.5, yy - 2.5, yy + 2.5, (z0 + z1) / 2 - 2.5,
                         (z0 + z1) / 2 + 2.5, "steel", rot=(angle, 0, 0), pivot=pivot)


def _fixed_sights(slide, z_front, z_rear, top, front_h=6.0, rear_h=6.5, dots=True):
    slide.box(-1.6, 1.6, top, top + front_h, z_front, z_front + 6, "steel_dark")
    slide.box(-7.5, -1.8, top, top + rear_h, z_rear - 6, z_rear, "steel_dark")
    slide.box(1.8, 7.5, top, top + rear_h, z_rear - 6, z_rear, "steel_dark")
    slide.box(-7.5, 7.5, top, top + 2.5, z_rear - 6, z_rear, "steel_dark")
    if dots:
        slide.box(-0.9, 0.9, top + front_h - 2.5, top + front_h - 1, z_front + 5.9, z_front + 6.1, "sight_white")
        slide.box(-5.5, -3, top + rear_h - 3, top + rear_h - 1.5, z_rear - 0.1, z_rear + 0.1, "sight_white")
        slide.box(3, 5.5, top + rear_h - 3, top + rear_h - 1.5, z_rear - 0.1, z_rear + 0.1, "sight_white")


# =================================================================================================
# M1911A1
# =================================================================================================
def m1911():
    A = -18.0
    TRAVEL = (0, 0, 46)
    m = new_gun("m1911")
    body = m["body"]
    blue = "steel"
    # frame
    body.box(-10.5, 10.5, -24, -9, -150, -30, blue)                     # dust cover (no rail)
    body.box(-10.5, 10.5, -24, -9, -30, 34, blue)
    body.box(-11, 11, -20, -8, 30, 44, blue)                            # frame tang
    # trigger guard (rounded front: two angled boxes)
    body.box(-4, 4, -52, -46, -48, -4, blue)
    body.box(-4, 4, -48, -24, -54, -48, blue, rot=(18, 0, 0), pivot=(0, -24, -50))
    # grip w/ walnut double-diamond panels
    gp = (0, -18, 16)
    _grip(body, gp, A, 11, -122, -16, -6, 38, blue, panel_mat="wood")
    # grip safety + mainspring housing
    gs = body.bone("grip_safety", pivot=(0, -20, 40))
    gs.box(-9, 9, -60, -18, 38, 46, blue, rot=(A, 0, 0), pivot=(0, -20, 40))
    gs.box(-11, 11, -22, -16, 38, 52, blue)                              # beavertail spur
    body.box(-8, 8, -122, -60, 40, 46, "steel_dark", rot=(A, 0, 0), pivot=gp)
    # slide stop & thumb safety (left side)
    body.box(-13, -10.5, -14, -8, -24, -2, blue)
    body.box(-13.5, -12, -12, -9, -27, -21, blue)                        # stop pin head
    safety = body.bone("safety", pivot=(-11, -12, 30))
    safety.box(-14, -10.5, -14, -9, 18, 32, blue)
    safety.box(-16, -13, -15, -11, 14, 22, blue)                         # thumb shelf
    body.box(-13, -10.5, -40, -32, -12, -2, "steel_dark")                # mag catch
    # barrel + bushing
    body.cyl((0, 0, -100), 13.5, 110, "steel_light")
    body.box(-6, 6, 6, 12, -30, 4, "steel_light")                         # hood
    # slide
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-11.7, 11.7, -9, 15, -176, 42, blue)
    slide.box(-9, 9, 15, 17, -174, 36, blue)
    slide.cyl((0, 0, -176), 20, 6, blue)                                  # bushing
    slide.box(-7, 7, -7, 7, -179.5, -178.5, "rubber")
    slide.box(0, 12, 9, 17.2, -30, 8, "rubber")                           # ejection port
    slide.box(1, 9, 10, 17.3, -28, 6, "steel_light")
    for i in range(9):
        z = 6 + i * 3.4
        slide.box(-11.9, -11.7, -5, 13, z, z + 1.5, "steel_dark")
        slide.box(11.7, 11.9, -5, 13, z, z + 1.5, "steel_dark")
    _fixed_sights(slide, -166, 34, 17, front_h=5.5, rear_h=5.5, dots=False)
    # hammer (cocked at rest)
    ham = body.bone("hammer", pivot=(0, -4, 42))
    ham.box(-3.5, 3.5, -6, 12, 40, 47, "steel", rot=(28, 0, 0), pivot=(0, -4, 42))
    ham.box(-4, 4, 8, 14, 46, 54, "steel", rot=(28, 0, 0), pivot=(0, -4, 42))
    # trigger (sliding)
    trig = body.bone("trigger", pivot=(0, -26, -28))
    trig.box(-3.5, 3.5, -40, -24, -32, -24, blue)
    _pistol_mag(m, gp, A, -16, -132, -2, 30, 13, base_mat="steel_dark")
    add_arms(m, right_hand=(6, -66, 32), left_hand=(-14, -70, 22), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -180), optic=None, under=None, eject=(12, 12, -10), sight=(0, 22.5, 36))

    def inspect():
        a = Anim(m, "inspect", 3.8)
        # thumb the safety on and off while looking at the left side
        a.mv("gun", 0.0, 0.4, pos=(-30, 40, 20), rot=(6, 48, 14))
        a.mv("arm_right", 0.35, 0.45, pos=(-8, 10, -4), rot=(0, -6, 4))
        a.key("safety", 0.0, rot=(0, 0, 0))
        a.key("safety", 0.45, rot=(0, 0, 0))
        a.key("safety", 0.5, rot=(-22, 0, 0), e="outquad")
        a.sound(0.5, "safety")
        a.key("safety", 0.85, rot=(-22, 0, 0))
        a.key("safety", 0.9, rot=(0, 0, 0), e="outquad")
        a.sound(0.9, "safety")
        a.mv("arm_right", 0.92, 1.05, pos=(0, 0, 0), rot=(0, 0, 0))
        # admire: slow roll from the left side to the top
        a.mv("gun", 1.0, 1.8, pos=(-50, 46, 26), rot=(18, 20, 40), e="inoutsine")
        a.wave("gun", "rot", (0.5, 0.6, 0.4), 1.9)
        # hammer check: support thumb rides the hammer down a touch, then re-cocks
        a.mv("gun", 1.9, 2.3, pos=(-30, 30, 30), rot=(4, -10, -20))
        a.mv("arm_left", 1.9, 2.25, pos=(20, 86, 66), rot=(-30, 10, 40))
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 2.3, rot=(0, 0, 0))
        a.key("hammer", 2.5, rot=(-12, 0, 0), e="inoutsine")
        a.key("hammer", 2.68, rot=(0, 0, 0), e="inquad")
        a.sound(2.68, "hammer_cock")
        a.mv("arm_left", 2.7, 3.2, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 2.8, 3.75)
        return a

    cyc = dict(bone="slide", travel=TRAVEL, t_back=0.024, t_fwd=0.062)
    k = dict(kick=(11, 0.6, 1.4), push=16, cycle=cyc, hammer=-30)
    anims = [
        idle(m), idle(m, "idle_empty", locked={"slide": TRAVEL}),
        draw(m, 0.55, sound="draw_pistol", style="pistol"),
        fire_basic(m, "fire", recover=0.26, length=0.34, **k),
        fire_basic(m, "fire_aim", recover=0.22, length=0.3, aim=True, **k),
        fire_basic(m, "fire_last", recover=0.26, length=0.34, lock_back=True, **k),
        pistol_reload(m, "reload", A, empty=False, slide_travel=TRAVEL),
        pistol_reload(m, "reload_empty", A, empty=True, slide_travel=TRAVEL, release="thumb"),
        inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.082, -0.27], "rot": [0, 6, 0]}, "ads": {"dist": 0.34}})


# =================================================================================================
# Beretta M9 / 92FS
# =================================================================================================
def m9():
    A = -15.0
    TRAVEL = (0, 0, 44)
    m = new_gun("m9")
    body = m["body"]
    body.box(-11, 11, -24, -8, -146, -26, "alloy")
    body.box(-11, 11, -24, -8, -26, 38, "alloy")
    body.box(-4.5, 4.5, -55, -49, -50, -2, "alloy")                      # trigger guard (squared)
    body.box(-4.5, 4.5, -55, -24, -56, -49, "alloy")
    body.box(-3, 3, -58, -54, -58, -44, "alloy")                          # finger hook
    gp = (0, -18, 16)
    _grip(body, gp, A, 12.5, -126, -18, -6, 40, "alloy", panel_mat="polymer")
    body.box(-13.5, -11, -14, -8, -22, -4, "steel_dark")                  # slide stop
    body.box(-13.5, -11, -26, -20, -40, -34, "steel_dark")                # takedown lever
    body.box(-13, -11, -44, -36, -6, 4, "polymer")                        # mag release
    # barrel (exposed by the open-top slide)
    body.cyl((0, 1, -95), 14, 110, "steel_light")
    body.box(-7, 7, 4, 14, -36, 8, "steel_light")
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-11.5, 11.5, -9, 9, -150, 44, "steel_dark")                 # lower slide walls
    slide.box(-11.5, 11.5, 9, 16, -24, 44, "steel_dark")                   # rear upper
    slide.box(-11.5, -6, 9, 15, -150, -24, "steel_dark")                   # open-top left wall
    slide.box(6, 11.5, 9, 15, -150, -24, "steel_dark")
    slide.box(-8, 8, -7, 9, -152, -150, "steel_dark")
    slide.box(-6.5, 6.5, -6, 6, -152.5, -152, "rubber")
    slide.box(0, 11.7, 9, 16.2, -24, 2, "rubber")
    for i in range(8):
        z = 12 + i * 3.6
        slide.box(-11.7, -11.5, -6, 12, z, z + 1.6, "steel")
        slide.box(11.5, 11.7, -6, 12, z, z + 1.6, "steel")
    _fixed_sights(slide, -146, 40, 15, front_h=7, rear_h=8)
    dec = slide.bone("decocker", pivot=(0, 10, 32))
    dec.box(-14.5, -11.5, 8, 13, 26, 38, "steel_dark")
    dec.box(11.5, 14.5, 8, 13, 26, 38, "steel_dark")
    dec.box(-16, -14.5, 9, 13, 30, 38, "steel_dark")
    ham = body.bone("hammer", pivot=(0, -4, 46))
    ham.box(-4, 4, -6, 12, 44, 51, "steel_dark", rot=(26, 0, 0), pivot=(0, -4, 46))
    ham.box(-4.5, 4.5, 8, 15, 49, 57, "steel_dark", rot=(26, 0, 0), pivot=(0, -4, 46))
    trig = body.bone("trigger", pivot=(0, -24, -30))
    trig.box(-3, 3, -46, -24, -34, -27, "steel_dark", rot=(-8, 0, 0), pivot=(0, -24, -30))
    _pistol_mag(m, gp, A, -18, -136, -2, 32, 21, base_mat="polymer")
    add_arms(m, right_hand=(6, -68, 34), left_hand=(-14, -72, 24), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 1, -154), under=None, eject=(12, 12, -8), sight=(0, 22, 40))

    def inspect():
        a = Anim(m, "inspect", 3.5)
        a.mv("gun", 0.0, 0.4, pos=(-36, 34, 30), rot=(6, -36, -16))
        # decocker flick: lever down, hammer drops safely
        a.mv("arm_right", 0.35, 0.48, pos=(-6, 22, 12), rot=(-10, -8, 6))
        a.key("decocker", 0.0, rot=(0, 0, 0))
        a.key("decocker", 0.5, rot=(0, 0, 0))
        a.key("decocker", 0.56, rot=(0, 0, -40), e="outquad")
        a.sound(0.56, "decocker")
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 0.56, rot=(0, 0, 0))
        a.key("hammer", 0.6, rot=(-34, 0, 0), e="inquad")
        a.spring("gun", "rot", 0.6, (1.2, 0, 0), freq=8, damp=12)
        a.key("decocker", 0.95, rot=(0, 0, -40))
        a.key("decocker", 1.02, rot=(0, 0, 0), e="outquad")
        a.sound(1.02, "safety")
        a.mv("arm_right", 1.02, 1.15, pos=(0, 0, 0), rot=(0, 0, 0))
        # tilt to show the open slide and the exposed barrel
        a.mv("gun", 1.1, 1.8, pos=(-56, 44, 20), rot=(26, 30, 44), e="inoutcubic")
        a.wave("gun", "rot", (0.6, 0.5, 0.4), 1.7)
        # support thumb cocks the hammer back
        a.mv("gun", 2.0, 2.35, pos=(-30, 28, 30), rot=(4, -8, -18))
        a.mv("arm_left", 2.0, 2.3, pos=(20, 86, 70), rot=(-30, 10, 40))
        a.key("hammer", 2.32, rot=(-34, 0, 0))
        a.key("hammer", 2.55, rot=(0, 0, 0), e="inoutsine")
        a.sound(2.55, "hammer_cock")
        a.mv("arm_left", 2.6, 3.1, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 2.65, 3.45)
        return a

    cyc = dict(bone="slide", travel=TRAVEL, t_back=0.024, t_fwd=0.06)
    k = dict(kick=(9.5, 0.4, 1.2), push=14, cycle=cyc, hammer=-34)
    anims = [
        idle(m), idle(m, "idle_empty", locked={"slide": TRAVEL}),
        draw(m, 0.55, sound="draw_pistol", style="pistol"),
        fire_basic(m, "fire", recover=0.24, length=0.32, **k),
        fire_basic(m, "fire_aim", recover=0.2, length=0.28, aim=True, **k),
        fire_basic(m, "fire_last", recover=0.24, length=0.32, lock_back=True, **k),
        pistol_reload(m, "reload", A, empty=False, slide_travel=TRAVEL),
        pistol_reload(m, "reload_empty", A, empty=True, slide_travel=TRAVEL, release="thumb"),
        inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.082, -0.27], "rot": [0, 6, 0]}, "ads": {"dist": 0.34}})


# =================================================================================================
# Desert Eagle Mark XIX .50 AE
# =================================================================================================
def deagle():
    A = -12.0
    TRAVEL = (0, 0, 52)
    m = new_gun("deagle")
    body = m["body"]
    st = "stainless"
    body.box(-13, 13, -30, -12, -150, -30, "steel_dark")
    body.box(-13, 13, -30, -12, -30, 40, "steel_dark")
    body.box(-5, 5, -64, -58, -58, -4, "steel_dark")
    body.box(-5, 5, -64, -30, -64, -58, "steel_dark")
    gp = (0, -22, 18)
    _grip(body, gp, A, 13, -140, -22, -8, 42, "polymer")
    body.box(-14, 14, -138, -128, -10, 44, "polymer", rot=(A, 0, 0), pivot=gp)
    body.box(-15, -13, -20, -14, -24, -6, "steel_dark")
    # fixed barrel with the iconic triangular profile + integral rail
    bar = body.bone("barrel", pivot=(0, 0, 0))
    bar.box(-14, 14, -12, 12, -262, -150, "steel_dark")
    bar.box(-10, 10, 12, 20, -262, -150, "steel_dark")                    # upper taper
    bar.box(-6, 6, 20, 26, -262, -150, "steel_dark")
    bar.rail(-258, -154, 26, width=14, mat="steel_dark")
    bar.box(-14.5, 14.5, -10, 10, -246, -238, "rubber")                    # polygonal muzzle flats
    bar.box(-7, 7, -7, 7, -263, -262, "rubber")
    bar.box(-15, -14, -12, 12, -220, -170, "steel_dark")                   # side flats
    bar.box(14, 15, -12, 12, -220, -170, "steel_dark")
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-15, 15, -12, 20, -150, 44, "steel_dark")
    slide.box(-12, 12, 20, 24, -150, 42, "steel_dark")
    slide.box(0, 15.2, 6, 20.5, -40, 0, "rubber")
    slide.box(2, 11, 8, 20.6, -38, -2, "steel_light")
    for i in range(10):
        z = 4 + i * 3.6
        slide.box(-15.2, -15, -8, 16, z, z + 1.6, "steel")
        slide.box(15, 15.2, -8, 16, z, z + 1.6, "steel")
    dec = slide.bone("safety", pivot=(0, 12, 38))
    dec.box(-18, -15, 8, 16, 30, 42, "steel_dark")
    dec.box(15, 18, 8, 16, 30, 42, "steel_dark")
    _fixed_sights(slide, -146, 40, 24, front_h=8, rear_h=8)
    ham = body.bone("hammer", pivot=(0, -4, 46))
    ham.box(-4, 4, -6, 14, 44, 51, "steel_dark", rot=(26, 0, 0), pivot=(0, -4, 46))
    ham.box(-5, 5, 10, 18, 49, 58, "steel_dark", rot=(26, 0, 0), pivot=(0, -4, 46))
    trig = body.bone("trigger", pivot=(0, -30, -30))
    trig.box(-3.5, 3.5, -54, -30, -34, -27, "steel_dark", rot=(-8, 0, 0), pivot=(0, -30, -30))
    _pistol_mag(m, gp, A, -22, -148, -4, 36, 17, round_d=13, round_len=40)
    add_arms(m, right_hand=(6, -72, 36), left_hand=(-14, -76, 26), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -264), optic=(0, 29, -200), eject=(15, 14, -20), sight=(0, 32, 40))

    def inspect():
        a = Anim(m, "inspect", 4.0)
        # hand-over-hand: tilt to show the left flat, roll over the top, show the right flat
        a.mv("gun", 0.0, 0.5, pos=(-60, 50, 20), rot=(14, 56, 30), e="inoutcubic")
        a.mv("arm_left", 0.1, 0.5, pos=(-20, -30, 30), rot=(10, 0, 0))
        a.wave("gun", "rot", (0.6, 0.8, 0.3), 2.0)
        a.mv("gun", 1.0, 1.25, pos=(-60, 70, 10), rot=(30, 10, 70), e="inoutsine")
        a.sound(1.15, "cloth")
        a.mv("gun", 1.25, 1.6, pos=(-50, 50, 10), rot=(12, -58, -32), e="inoutsine")
        a.mv("arm_left", 1.3, 1.6, pos=(30, 10, -30), rot=(0, 20, 0))
        a.mv("gun", 2.4, 2.8, pos=(-40, 30, 30), rot=(-24, -30, -10), e="inoutsine")  # muzzle down, look down the rail
        a.mv("arm_left", 2.4, 2.8, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.1, 3.95)
        return a

    cyc = dict(bone="slide", travel=TRAVEL, t_back=0.028, t_fwd=0.075)
    k = dict(kick=(20, 1.0, 3.0), push=24, cycle=cyc, hammer=-30)
    anims = [
        idle(m), idle(m, "idle_empty", locked={"slide": TRAVEL}),
        draw(m, 0.6, sound="draw_pistol", style="pistol"),
        fire_basic(m, "fire", recover=0.36, length=0.45, **k),
        fire_basic(m, "fire_aim", recover=0.3, length=0.4, aim=True, **k),
        fire_basic(m, "fire_last", recover=0.36, length=0.45, lock_back=True, **k),
        pistol_reload(m, "reload", A, empty=False, slide_travel=TRAVEL, length=1.9),
        pistol_reload(m, "reload_empty", A, empty=True, slide_travel=TRAVEL, release="overhand", length=2.4),
        inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.09, -0.3], "rot": [0, 6, 0]}, "ads": {"dist": 0.36}})


# =================================================================================================
# S&W Model 29 (.44 Magnum, 6.5")
# =================================================================================================
def model29():
    m = new_gun("model29")
    body = m["body"]
    bl = "steel"
    cy_c = (0, -15.0)  # cylinder centre (x, y)
    # frame
    body.box(-12, 12, 14, 22, -14, 34, bl)                                # top strap
    body.box(-12, 12, -40, -30, -16, 34, bl)                              # bottom of window
    body.box(-12, 12, -40, 22, -22, -14, bl)                              # front of window
    body.box(-12, 12, -36, 20, 32, 42, bl)                                # recoil shield
    body.box(-12, 12, -42, 4, 42, 54, bl)
    _fixed_sights(body, -188, 44, 22, front_h=8, rear_h=5, dots=False)
    body.box(-1.5, 1.5, 22, 30, -188, -176, "sight_orange")
    # barrel with full underlug ejector shroud
    body.cyl((0, 0, -105), 17, 166, bl)
    body.box(-6, 6, 8, 22, -188, -22, bl)                                 # rib
    body.box(-8, 8, -28, -6, -150, -22, bl)                               # ejector shroud
    body.box(-6.5, 6.5, -6.5, 6.5, -189, -188, "rubber")
    # trigger guard and trigger
    body.box(-4, 4, -66, -60, -40, 20, bl)
    body.box(-4, 4, -66, -40, -44, -38, bl)
    trig = body.bone("trigger", pivot=(0, -40, -6))
    trig.box(-3.5, 3.5, -62, -40, -10, -2, bl, rot=(-12, 0, 0), pivot=(0, -40, -6))
    # grip (Goncalo Alves wood, round butt)
    gp = (0, -30, 50)
    body.box(-13, 13, -140, -30, 34, 70, "wood", rot=(-24, 0, 0), pivot=gp)
    body.box(-14, 14, -130, -48, 30, 72, "wood", rot=(-24, 0, 0), pivot=gp)
    body.box(-12, 12, -40, -24, 46, 64, bl)
    # thumb latch
    body.box(-15, -12, -8, 0, 34, 46, bl)
    # hammer (DA/SA) - decocked at rest
    ham = body.bone("hammer", pivot=(0, -14, 54))
    ham.box(-4, 4, -14, 16, 50, 58, bl)
    ham.box(-5, 5, 12, 18, 56, 68, bl)
    # crane + cylinder (swings out to the left)
    crane = m["gun"].bone("crane", pivot=(-10, -34, 0))
    crane.box(-14, -6, -38, -28, -20, 32, bl)                             # yoke
    cyl = crane.bone("cylinder", pivot=(0, cy_c[1], 0))
    cyl.cyl((0, cy_c[1], 9), 44, 41, bl, sides=12)
    for i in range(6):  # flutes
        a = math.radians(30 + 60 * i)
        x = math.cos(a) * 20.5
        y = cy_c[1] + math.sin(a) * 20.5
        cyl.box(x - 2.5, x + 2.5, y - 2.5, y + 2.5, -8, 22, "steel_dark")
    rounds = cyl.bone("rounds", pivot=(0, cy_c[1], 0))
    brass = cyl.bone("brass", pivot=(0, cy_c[1], 0))
    for i in range(6):
        a = math.radians(90 + 60 * i)
        x = math.cos(a) * 14.0
        y = cy_c[1] + math.sin(a) * 14.0
        rounds.cyl((x, y, 30.5), 11.5, 1.5, "brass")
        rounds.cyl((x, y, 30.6), 5, 1.4, "copper")
        brass.cyl((x, y, 18), 11, 28, "brass")
    ej = crane.bone("ejector", pivot=(0, cy_c[1], 0))
    ej.cyl((0, cy_c[1], -60), 7, 110, "steel_light")
    ej.cyl((0, cy_c[1], -116), 9, 8, "steel_light")
    ej.cyl((0, cy_c[1], 29), 26, 2, "steel_light", sides=12)               # extractor star
    sl = crane.bone("speedloader", pivot=(0, cy_c[1], 0))
    sl.cyl((0, cy_c[1], 46), 46, 12, "polymer", sides=12)
    sl.cyl((0, cy_c[1], 56), 18, 12, "polymer")
    for i in range(6):
        a = math.radians(90 + 60 * i)
        x = math.cos(a) * 14.0
        y = cy_c[1] + math.sin(a) * 14.0
        sl.round_((x, y, 28), 40, 11)
    add_arms(m, right_hand=(6, -76, 58), left_hand=(-14, -80, 48), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -190), optic=(0, 22, -40), eject=None, sight=(0, 27, 44))

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


GUNS = {"m1911": m1911, "m9": m9, "deagle": deagle, "model29": model29}
