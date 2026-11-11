"""WWII-era service arms: Mosin-Nagant M91/30, M1917 Enfield, Arisaka Type 99, SKS, PPSh-41."""
import math

import numpy as np

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden)
from ..templates import (bolt_cycle, bolt_clip_load, carrier_clip_load, follow_pos, _settle, OFF_LEFT, OFF_LEFT_ROT)
from ..parts import trigger_group, barrel

RIFLE_FP = {"hip": {"pos": [0.12, -0.14, -0.2], "rot": [0, 3, 0]}, "ads": {"dist": 0.42}}


# -------------------------------------------------------------------------------------------------
# shared bits
# -------------------------------------------------------------------------------------------------
def _military_bolt(m, z_front, z_rear, handle_z, handle_len=52, knob_d=17, bend=0.0, d=18.0, cock=None,
                   mat="steel_light"):
    """Rotating bolt with a handle sticking out to the right. `bend` sweeps the handle back (M1917 dog-leg)."""
    b = m["body"].bone("bolt", pivot=(0, 0, 0))
    b.cyl((0, 0, (z_front + z_rear) / 2), d, z_rear - z_front, mat)
    b.box(-3, 3, d / 2 - 1, d / 2 + 2, z_front + 8, z_rear - 24, "steel")                 # guide rib
    hp = (d / 2 - 2, 0, handle_z)
    b.box(d / 2 - 2, d / 2 + handle_len, -4, 4, handle_z - 4, handle_z + 4, mat, rot=(0, bend, -6), pivot=hp)
    kx = d / 2 + handle_len
    kz = handle_z + math.sin(math.radians(bend)) * handle_len
    b.cyl((kx - 2, -6, kz), knob_d, knob_d, mat, sides=8)                                     # bolt knob
    if cock:
        b.cyl((0, 0, z_rear + cock[1] / 2), cock[0], cock[1], "steel")                         # cocking piece
    return b


def _clip(m, guide, n=5, case_len=54, bullet_len=24, d=11.5, step=10.0):
    """Stripper clip bone (seated in the guide at rest) with a child bone of rounds."""
    gx, gy, gz = guide
    c = m["gun"].bone("clip", pivot=guide)
    c.box(gx - 7, gx + 7, gy, gy + n * step + 6, gz - 1, gz + 4, "steel")
    c.box(gx - 7, gx - 5, gy, gy + n * step + 6, gz - 5, gz + 4, "steel")
    c.box(gx + 5, gx + 7, gy, gy + n * step + 6, gz - 5, gz + 4, "steel")
    r = c.bone("clip_rounds", pivot=guide)
    L = case_len + bullet_len
    for i in range(n):
        x = gx + (1.6 if i % 2 else -1.6)
        r.round_((x, gy + 6 + i * step, gz - 2 - L / 2), L, d)
    return c


def _round_load(m, at, length, d):
    rl = m["gun"].bone("round_load", pivot=at)
    rl.round_(at, length, d)
    br = m["gun"].bone("brass", pivot=(0, 6, at[2] - 10))
    br.cyl((0, 6, at[2]), d, length * 0.65, "brass")


def _bolt_set(m, travel, handle_rot, kick, push, recover=0.45, length=0.55, cycle_len=0.85):
    return [fire_basic(m, "fire", kick=kick, push=push, recover=recover, length=length),
            fire_basic(m, "fire_aim", kick=kick, push=push, recover=recover * 0.9, length=length * 0.9, aim=True),
            bolt_cycle(m, "cycle", travel=travel, handle_rot=handle_rot, length=cycle_len),
            bolt_cycle(m, "cycle_aim", travel=travel, handle_rot=handle_rot, length=cycle_len, aim=True)]


def _disk(b, c, d, thick, mat, n=11):
    """Round disk with its axis along X (a drum magazine): a 16-sided prism."""
    return b.cyl(c, d, thick, mat, axis="x", sides=16)


def _butt(b, z0, z1, wood, plate, comb_y=-6.0, heel_drop=24.0, toe_y=-130.0, wrist_y=-64.0, w=19.0, n=9):
    """Rifle buttstock: the comb drops towards the heel and the toe line sweeps down from the wrist, as one smooth
    tapered solid, finished with a butt plate."""
    hy = comb_y - heel_drop
    b.taper(-w, w, z0, z1, comb_y, hy, wrist_y, toe_y, wood)
    b.box(-w - 0.5, w + 0.5, toe_y - 2, hy + 1, z1, z1 + 10, plate)


def _band(b, z, top=16, bot=-38, w=17, mat="steel"):
    b.box(-w, w, bot, top, z - 7, z + 7, mat)


# =================================================================================================
# Mosin-Nagant M91/30
# =================================================================================================
def mosin():
    m = new_gun("mosin")
    body = m["body"]
    st = "steel"
    wd = "wood"
    # receiver: hexagonal, with open top between the rings
    body.cyl((0, 0, -10), 32, 200, st, sides=8)                       # -110 .. 90
    body.box(-9, 9, 15, 16.6, -82, 6, "rubber")                       # open top of the action
    body.box(-10, -7, 14, 24, 6, 16, st)                              # charger guide ears
    body.box(7, 10, 14, 24, 6, 16, st)
    body.box(-6, 6, -14, 14, 90, 150, st)                             # tang
    # barrel (stepped profile) + sights
    body.cyl((0, 0, -200), 24, 180, st)
    barrel(body, -280, -830, d=19)
    body.box(-6, 6, 9, 22, -830, -808, st)                            # front sight base
    body.box(-8, -6, 10, 30, -828, -810, st)                          # hood
    body.box(6, 8, 10, 30, -828, -810, st)
    body.box(-8, 8, 28, 30, -828, -810, st)
    body.box(-1, 1, 14, 26, -820, -818, st)                           # post
    body.box(-12, 12, 10, 18, -260, -150, st)                         # tangent rear sight base
    sight = body.bone("rear_sight", pivot=(0, 18, -250))
    sight.box(-9, 9, 18, 22, -250, -158, st)
    sight.box(-9, 9, 22, 24, -166, -158, st)                          # notch block with a V gap
    sight.box(-9, -1.6, 24, 28, -166, -158, st)
    sight.box(1.6, 9, 24, 28, -166, -158, st)
    # stock: forend, handguards, bands, straight wrist, butt
    body.box(-17, 17, -40, 4, -570, -110, wd)
    body.box(-14, 14, 4, 15, -560, -290, wd)                          # front upper handguard
    body.box(-14, 14, 4, 15, -280, -265, wd)
    body.box(-18, 18, -54, -6, -110, 120, wd)                         # receiver bed
    _band(body, -548, top=16, bot=-42)
    _band(body, -360, top=16, bot=-42)
    body.box(-13, 13, -38, 4, -582, -570, st)                         # nose cap
    body.cyl((0, -16, -700), 6, 260, "steel_light")                   # cleaning rod
    body.box(-14, 14, -70, -54, -76, 2, "steel_dark")                 # magazine box
    body.box(-15, 15, -74, -70, -80, 6, "steel_dark")                 # floorplate
    trigger_group(m, body, 40, y_top=-54, guard_depth=24, guard_len=56, guard_mat=st)
    body.box(-15, 15, -62, -10, 116, 240, wd, rot=(4, 0, 0), pivot=(0, -10, 116))    # straight wrist
    _butt(body, 236, 391, wd, st, comb_y=-16, heel_drop=18, toe_y=-128, wrist_y=-70)
    _military_bolt(m, -70, 104, 98, handle_len=50, knob_d=18, cock=(22, 22))
    _clip(m, (0, 15, 12), case_len=54, bullet_len=23, d=11.5)
    _round_load(m, (0, 12, -26), 77, 11.5)
    add_arms(m, right_hand=(10, -74, 168), left_hand=(-14, -46, -330), right_rot=(30, 12, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -832), eject=(16, 10, -30), sight=(0, 26, -160))
    travel, hrot = (0, 0, 92), (0, 0, 84)

    def inspect():
        # hold the trigger, draw the bolt all the way out and look at its face, then slide it home
        a = Anim(m, "inspect", 5.2)
        a.mv("gun", 0.0, 0.4, pos=(-30, 20, 30), rot=(4, -20, -26))
        a.mv("arm_right", 0.0, 0.2, pos=(20, 40, -30), rot=(-25, -20, -20))
        a.grab("arm_right", "bolt", 0.2, 3.3, fade_in=0.03, fade_out=0.08)
        a.key("bolt", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("bolt", 0.22, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("bolt", 0.34, pos=(0, 0, 0), rot=hrot, e="outquad")
        a.sound(0.32, "bolt_open")
        a.key("bolt", 0.58, pos=travel, rot=hrot, e="inoutquad")
        a.sound(0.56, "bolt_back")
        # trigger held: the bolt stop drops and the bolt comes out of the receiver
        a.key("trigger", 0.0, rot=(0, 0, 0))
        a.key("trigger", 0.62, rot=(0, 0, 0))
        a.key("trigger", 0.7, rot=(-14, 0, 0), e="outquad")
        a.key("trigger", 1.1, rot=(-14, 0, 0))
        a.key("trigger", 1.2, rot=(0, 0, 0))
        a.sound(0.7, "click_small")
        a.key("bolt", 0.78, pos=travel, rot=hrot)
        a.key("bolt", 1.12, pos=(0, 10, 230), rot=hrot, e="inoutsine")
        a.mv("gun", 0.7, 1.2, pos=(-60, -10, 60), rot=(0, -30, -30))
        # turn the bolt to look at the face / extractor
        a.key("bolt", 1.55, pos=(30, 70, 250), rot=(-30, 150, 40), e="inoutsine")
        a.key("bolt", 2.2, pos=(34, 74, 252), rot=(-24, 160, 20), e="linear")
        a.sound(1.6, "cloth")
        a.key("bolt", 2.65, pos=(0, 10, 230), rot=hrot, e="inoutsine")
        a.key("bolt", 2.95, pos=travel, rot=hrot, e="inoutsine")
        a.sound(2.92, "bolt_forward")
        a.key("bolt", 3.12, pos=(0, 0, 0), rot=hrot, e="inoutquad")
        a.sound(3.1, "bolt_forward")
        a.key("bolt", 3.24, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
        a.sound(3.24, "bolt_close")
        a.spring("gun", "rot", 3.24, (1.4, 0, -1.2), freq=6, damp=8)
        a.mv("gun", 2.5, 3.0, pos=(-30, 20, 30), rot=(4, -20, -26))
        a.mv("arm_right", 3.38, 3.7, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.6, 5.15)
        return a

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             *_bolt_set(m, travel, hrot, kick=(7.5, 0.7, 1.6), push=24, cycle_len=0.9),
             *bolt_clip_load(m, travel=travel, handle_rot=hrot, push=52), inspect(), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    return GunAsset(m, anims, RIFLE_FP)


# =================================================================================================
# M1917 Enfield
# =================================================================================================
def m1917():
    m = new_gun("m1917")
    body = m["body"]
    st = "steel_parked"
    wd = "wood_light"
    body.cyl((0, 0, -6), 34, 220, st, sides=8)                          # receiver -116 .. 104
    body.box(-9, 9, 16, 17.6, -84, 8, "rubber")
    body.box(-10, -7, 16, 24, 8, 18, st)
    body.box(7, 10, 16, 24, 8, 18, st)
    # receiver bridge with the protective sight ears and ladder aperture
    body.box(-16, 16, 10, 26, 30, 70, st)
    body.box(-16, -11, 26, 52, 30, 70, st)                              # left ear
    body.box(11, 16, 26, 52, 30, 70, st)                                # right ear
    lad = body.bone("rear_sight", pivot=(0, 26, 66))
    lad.box(-8, 8, 26, 30, 30, 66, st)                                  # ladder lies forward
    for x0, x1, y0, y1 in ((-6, 6, 26, 28), (-6, 6, 32, 34), (-6, -2, 28, 32), (2, 6, 28, 32)):
        lad.box(x0, x1, y0, y1, 46, 50, "steel_dark")                   # battle-sight aperture ring
    body.box(-6, 6, -14, 14, 104, 150, st)
    # barrel and front sight with ears
    body.cyl((0, 0, -210), 26, 190, st)
    barrel(body, -300, -840, d=19)
    body.box(-9, 9, 9, 18, -834, -810, st)
    body.box(-9, -6, 18, 34, -832, -812, st)
    body.box(6, 9, 18, 34, -832, -812, st)
    body.box(-1, 1, 18, 30, -824, -821, st)
    # stock (semi pistol grip), finger grooves in the forend
    body.box(-17, 17, -42, 4, -600, -116, wd)
    for z in (-300, -250):
        body.box(-17.4, 17.4, -24, -14, z, z + 30, "wood")
    body.box(-14, 14, 4, 16, -590, -130, wd)
    _band(body, -580, top=18, bot=-44, mat=st)
    _band(body, -420, top=18, bot=-44, mat=st)
    body.box(-13, 13, -38, 0, -612, -600, st)
    body.box(-18, 18, -56, -8, -116, 120, wd)
    body.box(-15, 15, -86, -56, -84, 4, st)                             # the "belly" of the 6-rd magazine
    body.box(-16, 16, -90, -86, -88, 8, st)
    trigger_group(m, body, 40, y_top=-56, guard_depth=24, guard_len=60, guard_mat=st)
    body.box(-15, 15, -62, -10, 116, 240, wd, rot=(4, 0, 0), pivot=(0, -10, 116))    # wrist
    body.box(-14, 14, -108, -50, 128, 176, wd, rot=(-24, 0, 0), pivot=(0, -50, 150))  # semi pistol grip
    _butt(body, 236, 405, wd, st, comb_y=-16, heel_drop=18, toe_y=-130, wrist_y=-80)
    sel = body.bone("selector", pivot=(10, 6, 150))                      # wing safety
    sel.box(8, 14, 4, 18, 146, 154, "steel")
    _military_bolt(m, -76, 112, 100, handle_len=46, knob_d=17, bend=-28, cock=(20, 26))
    _clip(m, (0, 17, 14), case_len=63, bullet_len=21, d=12)
    _round_load(m, (0, 12, -30), 84, 12)
    add_arms(m, right_hand=(10, -86, 148), left_hand=(-14, -48, -330), right_rot=(34, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -842), eject=(16, 10, -30), sight=(0, 30, 48))
    travel, hrot = (0, 0, 100), (0, 0, 88)

    def inspect():
        # bolt half-open chamber check, then flip up the ladder sight and run the aperture up and down
        a = Anim(m, "inspect", 4.8)
        a.mv("gun", 0.0, 0.4, pos=(-30, 20, 30), rot=(4, -22, -28))
        a.mv("arm_right", 0.0, 0.2, pos=(20, 40, -30), rot=(-25, -20, -20))
        a.grab("arm_right", "bolt", 0.2, 1.5, fade_in=0.03, fade_out=0.06)
        a.key("bolt", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("bolt", 0.24, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("bolt", 0.36, pos=(0, 0, 0), rot=hrot, e="outquad")
        a.sound(0.34, "bolt_open")
        a.key("bolt", 0.58, pos=(0, 0, 34), rot=hrot, e="inoutsine")
        a.mv("gun", 0.55, 0.9, pos=(-40, 30, 40), rot=(10, -36, -50))
        a.key("bolt", 1.1, pos=(0, 0, 34), rot=hrot)
        a.key("bolt", 1.26, pos=(0, 0, 0), rot=hrot, e="inoutsine")
        a.key("bolt", 1.36, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
        a.sound(1.36, "bolt_close")
        a.mv("arm_right", 1.5, 1.8, pos=(0, 0, 0), rot=(0, 0, 0))
        # bring the receiver bridge to the eye, flip the ladder up
        a.mv("gun", 1.4, 1.9, pos=(-20, -50, -40), rot=(-14, -8, -6), e="inoutsine")
        a.mv("arm_left", 1.7, 2.0, pos=(20, 120, 360), rot=(-60, 10, 20))
        a.key("rear_sight", 0.0, rot=(0, 0, 0))
        a.key("rear_sight", 2.05, rot=(0, 0, 0))
        a.key("rear_sight", 2.25, rot=(-88, 0, 0), e="outback")
        a.sound(2.22, "click_small")
        # run the aperture slide up the ladder: three detent clicks
        for i, t in enumerate((2.6, 2.85, 3.1)):
            a.sound(t, "click_small")
            a.spring("rear_sight", "rot", t, (1.5, 0, 0), freq=12, damp=14)
        a.key("rear_sight", 3.35, rot=(-88, 0, 0))
        a.key("rear_sight", 3.52, rot=(0, 0, 0), e="inquad")
        a.sound(3.52, "click_small")
        a.mv("arm_left", 3.55, 3.9, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.6, 4.75)
        return a

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             *_bolt_set(m, travel, hrot, kick=(8, 0.7, 1.6), push=25, cycle_len=0.88),
             *bolt_clip_load(m, travel=travel, handle_rot=hrot, push=54), inspect(), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    m.warp_z([(-841, -760), (-110, -110)])
    return GunAsset(m, anims, {"hip": RIFLE_FP["hip"], "ads": {"dist": 0.2}})


# =================================================================================================
# Arisaka Type 99
# =================================================================================================
def arisaka():
    m = new_gun("arisaka")
    body = m["body"]
    st = "steel"
    wd = "wood"
    body.cyl((0, 0, -8), 32, 200, st, sides=8)
    body.box(-9, 9, 15, 16.6, -82, 8, "rubber")
    body.box(-10, -7, 15, 24, 8, 18, st)
    body.box(7, 10, 15, 24, 8, 18, st)
    body.box(-6, 6, -14, 14, 92, 150, st)
    body.cyl((0, 0, -200), 24, 180, st)
    barrel(body, -290, -780, d=19)
    body.box(-6, 6, 9, 20, -778, -756, st)
    body.box(-8, -6, 10, 30, -776, -758, st)
    body.box(6, 8, 10, 30, -776, -758, st)
    body.box(-1, 1, 14, 28, -768, -766, st)
    # leaf rear sight with the folding anti-aircraft lead arms
    body.box(-12, 12, 10, 18, -250, -170, st)
    body.box(-9, 9, 18, 24, -244, -176, st)
    body.box(-5, -1.6, 24, 30, -182, -176, st)                         # notch ears
    body.box(1.6, 5, 24, 30, -182, -176, st)
    for side, name in ((-1, "aa_left"), (1, "aa_right")):
        aa = body.bone(name, pivot=(side * 10, 22, -210))
        aa.box(side * 10 - 2 if side > 0 else side * 10 - 2, side * 10 + 2, 20, 24, -214, -206, st)
        aa.box(min(side * 10, side * 62), max(side * 10, side * 62), 21, 23, -212, -208, st)
    # stock, two-piece with the joint under the receiver; monopod under the forend
    body.box(-17, 17, -40, 4, -560, -110, wd)
    body.box(-14, 14, 4, 15, -545, -130, wd)
    _band(body, -540, top=16, bot=-42)
    _band(body, -390, top=16, bot=-42)
    body.box(-13, 13, -36, 2, -572, -560, st)
    body.cyl((0, -16, -660), 6, 220, "steel_light")
    body.box(-18, 18, -54, -6, -110, 118, wd)
    body.box(-14, 14, -68, -54, -78, 0, "steel_dark")
    body.box(-15, 15, -72, -68, -82, 4, "steel_dark")
    mono = body.bone("monopod", pivot=(0, -40, -470))
    mono.box(-2, 2, -44, -40, -470, -330, "steel_light")                  # folded wire leg
    mono.box(-10, 10, -46, -40, -340, -330, "steel_light")
    trigger_group(m, body, 40, y_top=-54, guard_depth=24, guard_len=58, guard_mat=st)
    body.box(-15, 15, -62, -10, 116, 236, wd, rot=(4, 0, 0), pivot=(0, -10, 116))
    body.box(-14, 14, -104, -50, 128, 172, wd, rot=(-24, 0, 0), pivot=(0, -50, 148))
    _butt(body, 232, 351, wd, st, comb_y=-16, heel_drop=14, toe_y=-122, wrist_y=-80)
    _military_bolt(m, -70, 104, 96, handle_len=44, knob_d=16, cock=(28, 18))
    # the bolt's sliding dust cover (rides with the bolt, does not rotate)
    dc = body.bone("dust_cover", pivot=(0, 0, 0))
    dc.box(-13, 13, 16.5, 19, -84, 10, "steel_dark")
    dc.box(-14, -12, 10, 19, -84, 10, "steel_dark")
    dc.box(12, 14, 13, 19, -84, -10, "steel_dark")
    _clip(m, (0, 15, 12), case_len=57, bullet_len=23, d=12)
    _round_load(m, (0, 12, -28), 80, 12)
    add_arms(m, right_hand=(10, -84, 150), left_hand=(-14, -46, -320), right_rot=(34, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -782), eject=(16, 10, -30), sight=(0, 28, -180))
    travel, hrot = (0, 0, 94), (0, 0, 86)

    def inspect():
        # swing out the anti-aircraft lead arms and track a plane, unfold the monopod, then twist the safety knob
        a = Anim(m, "inspect", 5.4)
        a.mv("gun", 0.0, 0.45, pos=(-30, 30, 50), rot=(10, -16, 20))
        a.mv("arm_left", 0.2, 0.5, pos=(-20, 60, 110), rot=(-30, 10, 10))
        for name, t, r in (("aa_left", 0.6, (0, 0, -90)), ("aa_right", 0.9, (0, 0, 90))):
            a.key(name, 0.0, rot=(0, 0, 0))
            a.key(name, t, rot=(0, 0, 0))
            a.key(name, t + 0.14, rot=r, e="outback")
            a.sound(t + 0.12, "click_small")
            a.key(name, 3.1, rot=r)
            a.key(name, 3.25 + (0.15 if name == "aa_right" else 0), rot=(0, 0, 0), e="inquad")
            a.sound(3.24 + (0.15 if name == "aa_right" else 0), "click_small")
        a.mv("arm_left", 1.1, 1.4, pos=(0, 0, 0), rot=(0, 0, 0))
        # aim up at the sky and sweep, like leading an aircraft
        a.mv("gun", 1.2, 1.7, pos=(0, -40, -30), rot=(-38, 6, 0), e="inoutsine")
        a.mv("gun", 1.7, 2.4, pos=(10, -40, -30), rot=(-34, -10, -2), e="inoutsine")
        # flip the monopod down and back up
        a.mv("gun", 2.4, 2.8, pos=(-40, 30, 30), rot=(6, 30, 30))
        a.key("monopod", 0.0, rot=(0, 0, 0))
        a.key("monopod", 2.6, rot=(0, 0, 0))
        a.key("monopod", 2.78, rot=(-80, 0, 0), e="outback")
        a.sound(2.76, "stock_lock")
        a.key("monopod", 3.0, rot=(-80, 0, 0))
        a.key("monopod", 3.16, rot=(0, 0, 0), e="inquad")
        a.sound(3.16, "stock_lock")
        # push and turn the big safety knob on the cocking piece
        a.mv("gun", 3.4, 3.8, pos=(-30, 20, 30), rot=(-6, 24, 12))
        a.mv("arm_right", 3.5, 3.75, pos=(-10, 70, -30), rot=(-30, -20, -20))
        a.sound(3.9, "safety")
        a.sound(4.25, "safety")
        a.mv("arm_right", 4.3, 4.6, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 4.3, 5.35)
        return a

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             *_bolt_set(m, travel, hrot, kick=(7.5, 0.7, 1.6), push=24, cycle_len=0.88),
             *bolt_clip_load(m, travel=travel, handle_rot=hrot, push=52), inspect(), dry_fire(m)]
    follow_pos(anims, "bolt", "dust_cover")
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    m.warp_z([(-781, -757), (-110, -110)])
    return GunAsset(m, anims, RIFLE_FP)


# =================================================================================================
# SKS (Type 45 pattern, folding blade bayonet)
# =================================================================================================
def sks():
    m = new_gun("sks")
    body = m["body"]
    st = "steel"
    wd = "wood_red"
    body.box(-14, 14, -30, 14, -90, 140, st)                            # milled receiver
    body.box(-12, 12, 14, 24, -10, 170, st)                             # receiver cover
    body.box(0, 14.3, -4, 12, -60, 10, "rubber")                       # ejection port
    body.box(-6, 6, -40, -30, 0, 20, st)
    # barrel, gas tube, front sight, bayonet lug
    body.cyl((0, 0, -140), 22, 100, st)
    barrel(body, -190, -560, d=17)
    body.cyl((0, 20, -260), 14, 330, st)                                # gas tube -95 .. -425
    body.box(-8, 8, 0, 30, -440, -420, st)                              # gas block
    body.box(-6, 6, 8, 30, -548, -528, st)                               # front sight tower
    body.box(-8, -6, 22, 46, -546, -530, st)
    body.box(6, 8, 22, 46, -546, -530, st)
    body.box(-1, 1, 30, 40, -540, -538, st)
    body.box(-10, 10, 14, 30, -110, -70, st)                            # tangent rear sight
    body.box(-8, 8, 30, 34, -110, -40, st)
    body.box(-8, -1.6, 34, 41, -44, -40, st)
    body.box(1.6, 8, 34, 41, -44, -40, st)
    # wood: forend, handguard over the gas tube, semi pistol grip butt
    body.box(-17, 17, -34, 6, -420, -90, wd)
    body.box(-13, 13, 12, 28, -420, -150, wd)
    _band(body, -400, top=8, bot=-36, w=18)
    body.box(-17, 17, -48, -8, -90, 150, wd)
    body.box(-14, 14, -86, -30, -84, -6, st)                             # 10-rd fixed magazine
    body.box(-15, 15, -90, -86, -88, -2, st)
    trigger_group(m, body, 26, y_top=-48, guard_depth=26, guard_len=60, guard_mat=st)
    body.box(-15, 15, -60, -10, 140, 250, wd, rot=(4, 0, 0), pivot=(0, -10, 140))
    body.box(-14, 14, -104, -48, 150, 196, wd, rot=(-24, 0, 0), pivot=(0, -48, 172))
    _butt(body, 246, 449, wd, st, comb_y=-14, heel_drop=20, toe_y=-128, wrist_y=-80, w=18)

    sel = body.bone("selector", pivot=(0, -40, 60))
    sel.box(-3, 3, -46, -38, 56, 66, "steel")                           # safety behind the trigger
    # carrier with the charger guide and right-hand handle
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-10, 10, -6, 12, -60, 60, "steel_light")
    bolt.box(-8, 8, 12, 14, -10, 14, "steel_light")                     # charger guide on the carrier
    bolt.box(10, 28, -2, 6, -40, -30, "steel_light")
    bolt.box(26, 32, -6, 10, -42, -28, "steel_light")
    # folding blade bayonet, hinged at the front band
    bay = body.bone("bayonet", pivot=(0, -20, -470))
    bay.box(-6, 6, -26, -14, -478, -462, st)
    bay.box(-2, 2, -26, -14, -462, -236, "steel_light")                   # folded back along the forend
    bay.box(-2.5, 2.5, -25, -15, -244, -236, "steel_light")
    _clip(m, (0, 13, -14), n=10, case_len=39, bullet_len=17, d=11, step=5.0)
    _round_load(m, (0, 10, -40), 56, 11)
    add_arms(m, right_hand=(8, -82, 170), left_hand=(-14, -40, -300), right_rot=(34, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -562), eject=(15, 6, -30), sight=(0, 40, -44))
    travel = (0, 0, 100)

    def inspect():
        # flick the bayonet out until it locks, show it off, fold it back
        a = Anim(m, "inspect", 4.6)
        a.mv("gun", 0.0, 0.45, pos=(-40, 30, 60), rot=(14, -24, 30))
        a.mv("arm_left", 0.25, 0.55, pos=(10, -10, -160), rot=(10, 10, 0))
        a.key("bayonet", 0.0, rot=(0, 0, 0))
        a.key("bayonet", 0.6, rot=(0, 0, 0))
        a.key("bayonet", 0.82, rot=(-180, 0, 0), e="outback")
        a.sound(0.66, "stock_unlock")
        a.sound(0.82, "stock_lock")
        a.spring("gun", "rot", 0.82, (2.0, 0, 1.0), freq=6, damp=8)
        a.spring("bayonet", "rot", 0.82, (4.0, 0, 0), freq=12, damp=14)
        a.mv("arm_left", 0.9, 1.2, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 0.95, 1.6, pos=(-60, 10, -30), rot=(2, -50, -10))
        a.mv("gun", 1.8, 2.3, pos=(-30, 30, 40), rot=(10, 20, 30))
        a.key("bayonet", 2.6, rot=(-180, 0, 0))
        a.mv("arm_left", 2.3, 2.6, pos=(10, -40, -280), rot=(10, 10, 0))
        a.key("bayonet", 2.62, rot=(-176, 0, 0))
        a.sound(2.62, "stock_unlock")
        a.key("bayonet", 2.95, rot=(0, 0, 0), e="inoutsine")
        a.sound(2.95, "stock_lock")
        a.spring("gun", "rot", 2.95, (-1.2, 0, 0.8), freq=6, damp=8)
        a.mv("arm_left", 3.0, 3.4, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.1, 4.55)
        return a

    cyc = dict(bone="bolt", travel=travel, t_back=0.024, t_fwd=0.07)
    kk = dict(kick=(4.2, 0.6, 1.4), push=16, cycle=cyc)
    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", recover=0.2, length=0.3, **kk),
             fire_basic(m, "fire_aim", recover=0.18, length=0.28, aim=True, **kk),
             *carrier_clip_load(m, travel=travel, push=40), inspect(), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    return GunAsset(m, anims, {"hip": RIFLE_FP["hip"], "ads": {"dist": 0.38}})


# =================================================================================================
# PPSh-41 with the 71-round drum
# =================================================================================================
def ppsh41():
    m = new_gun("ppsh41")
    body = m["body"]
    st = "steel_dark"
    wd = "wood"
    body.box(-15, 15, -24, 18, -110, 120, st)                              # receiver
    body.box(-12, 12, 18, 22, -60, 110, st)
    body.box(14.6, 15.4, 0, 10, -40, 60, "rubber")                       # charging slot
    body.box(-6, 6, 22, 30, 50, 70, st)                                    # L-flip rear sight
    body.box(-5, 5, 30, 32, 60, 66, st)
    body.box(-5, -1.4, 32, 37, 60, 66, st)
    body.box(1.4, 5, 32, 37, 60, 66, st)
    # ventilated barrel jacket with the slanted muzzle brake
    body.cyl((0, 0, -250), 30, 280, st, sides=8)                           # -110 .. -390
    for z in range(-380, -130, 32):
        for y in (8, -8):
            body.box(-15.4, 15.4, y - 4, y + 4, z, z + 16, "rubber")
        body.box(-6, 6, 14.6, 15.4, z, z + 16, "rubber")
    barrel(body, -110, -385, d=14, mat="steel_light")
    body.box(-15, 15, -15, 15, -420, -390, st, rot=(-30, 0, 0), pivot=(0, 15, -390))   # slanted brake
    body.box(-5, -3, 15, 38, -404, -392, st)                                # front sight hood
    body.box(3, 5, 15, 38, -404, -392, st)
    body.box(-5, 5, 36, 38, -404, -392, st)
    body.box(-1, 1, 15, 33, -398, -396, st)
    # wood stock: receiver bed, drum cut, wrist, butt
    body.box(-17, 17, -46, -8, -110, -40, wd)
    body.box(-17, 17, -46, -8, 30, 150, wd)
    body.box(-15, 15, -64, -12, 140, 236, wd, rot=(5, 0, 0), pivot=(0, -12, 140))
    _butt(body, 232, 450, wd, st, comb_y=-18, heel_drop=18, toe_y=-124, wrist_y=-68, w=18)

    body.box(-8, 8, -40, -24, -40, 30, st)                                 # mag housing / catch
    trigger_group(m, body, 70, y_top=-46, guard_depth=26, guard_len=58, guard_mat=st)
    sel = body.bone("selector", pivot=(0, -52, 40))
    sel.box(-3, 3, -58, -48, 38, 46, "steel")                              # fire selector inside the guard
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-10, 10, -10, 12, -40, 70, "steel_light")
    ch = bolt.bone("charging_handle", pivot=(15, 5, 40))
    ch.box(15, 28, 0, 10, 34, 46, "steel_light")
    ch.box(26, 30, -2, 12, 32, 48, "steel_light")
    # 71-round drum
    dc = (0, -118, -6)
    mag = m["gun"].bone("magazine", pivot=(0, -30, -6))
    mag.box(-8, 8, -42, -24, -30, 18, st)                                 # feed tower
    _disk(mag, dc, 192, 42, st, n=13)
    _disk(mag, (dc[0] + 22.5, dc[1], dc[2]), 176, 3, "steel", n=11)                    # lid
    _disk(mag, (dc[0] - 22.5, dc[1], dc[2]), 176, 3, "steel", n=11)
    for i in range(12):                                                    # lid ribs
        a = math.radians(i * 30)
        mag.box(22, 25, dc[1] + math.sin(a) * 72 - 4, dc[1] + math.sin(a) * 70 + 4,
                dc[2] + math.cos(a) * 72 - 4, dc[2] + math.cos(a) * 72 + 4, st)
    key = mag.bone("drum_key", pivot=(dc[0] + 26, dc[1], dc[2]))
    key.box(24, 30, dc[1] - 6, dc[1] + 6, dc[2] - 6, dc[2] + 6, "steel_light")
    key.box(28, 32, dc[1] - 22, dc[1] + 22, dc[2] - 4, dc[2] + 4, "steel_light")
    add_arms(m, right_hand=(8, -66, 170), left_hand=(-14, -60, -210), right_rot=(30, 12, 6),
             left_rot=(24, -18, -4))
    add_sockets(m, muzzle=(0, 0, -420), eject=(15, 10, -30), sight=(0, 33, 62))
    travel = (0, 0, 92)

    def reload(name, empty):
        L = 3.3 if empty else 3.0
        a = Anim(m, name, L)
        if empty:
            a.key("bolt", 0.0, pos=(0, 0, 0))
        a.mv("gun", 0.0, 0.35, pos=(-30, 30, 30), rot=(6, -14, -30))
        # left hand grabs the drum, thumb on the catch, pull it forward off the housing
        a.mv("arm_left", 0.05, 0.36, pos=(-20, -60, 150), rot=(10, 10, 20))
        a.grab("arm_left", "magazine", 0.38, 1.1, fade_in=0.04, fade_out=0.06)
        a.key("magazine", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("magazine", 0.4, pos=(0, 0, 0), rot=(0, 0, 0))
        a.sound(0.42, "drum_out")
        a.key("magazine", 0.5, pos=(0, -4, -14), rot=(4, 0, 0), e="outquad")
        a.key("magazine", 0.68, pos=(0, -60, -40), rot=(16, 0, 10), e="inoutsine")
        a.spring("gun", "rot", 0.45, (-2.0, 0, 1.4), freq=5, damp=8)
        a.kick("gun", "pos", 0.5, (0, 10, 0), attack=0.05, recover=0.3)           # the gun gets lighter
        a.key("magazine", 1.1, pos=(-60, -360, 120), rot=(40, 0, 30), e="inoutsine")
        a.mv("arm_left", 1.1, 1.35, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
        a.sound(1.3, "pouch")
        a.at_hand("magazine", 1.36, grip=(0, 60, -10), rot=(40, 0, 30))
        a.grab("arm_left", "magazine", 1.4, 2.2, fade_in=0.06, fade_out=0.06)
        a.key("magazine", 1.85, pos=(0, -50, -30), rot=(14, 0, 8), e="outcubic")
        a.key("magazine", 2.0, pos=(0, -10, -4), rot=(3, 0, 0), e="inoutsine")
        a.key("magazine", 2.1, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")         # heel of the hand drives it home
        a.sound(2.1, "drum_in")
        a.event(2.1, "ammo")
        a.spring("gun", "rot", 2.1, (-3.0, 0, 1.6), freq=5, damp=8)
        a.kick("gun", "pos", 2.1, (0, -10, 0), attack=0.03, recover=0.25)
        t = 2.25
        if empty:
            # cock the bolt with the right-hand handle
            a.mv("arm_left", t, t + 0.3, pos=(0, 0, 0), rot=(0, 0, 0))
            a.mv("arm_right", t, t + 0.16, pos=(24, 70, -110), rot=(-30, -20, -20))
            a.grab("arm_right", "charging_handle", t + 0.16, t + 0.42, fade_in=0.02, fade_out=0.05)
            a.key("bolt", t + 0.16, pos=(0, 0, 0))
            a.key("bolt", t + 0.32, pos=travel, e="inoutquad")
            a.sound(t + 0.3, "charging_handle_back")
            a.spring("gun", "rot", t + 0.32, (1.4, 0, -1.4), freq=6, damp=8)
            a.mv("arm_right", t + 0.45, t + 0.7, pos=(0, 0, 0), rot=(0, 0, 0))
            _settle(a, t + 0.45, L - 0.02)
        else:
            a.mv("arm_left", t, t + 0.4, pos=(0, 0, 0), rot=(0, 0, 0))
            _settle(a, t + 0.05, L - 0.02)
        return a

    def inspect():
        # roll it over to show the drum, crank the winding key (ratchet clicks), then look down the jacket
        a = Anim(m, "inspect", 4.8)
        a.mv("gun", 0.0, 0.45, pos=(-40, 30, 30), rot=(10, 30, 50), e="inoutsine")
        a.mv("arm_left", 0.2, 0.55, pos=(30, -90, 140), rot=(0, 40, 40))
        a.key("drum_key", 0.0, rot=(0, 0, 0))
        a.key("drum_key", 0.6, rot=(0, 0, 0))
        for i in range(4):
            t = 0.7 + i * 0.32
            a.key("drum_key", t + 0.2, rot=(-(i + 1) * 80, 0, 0), e="inoutsine")
            a.sound(t + 0.08, "click_small")
            a.sound(t + 0.16, "click_small")
            a.spring("gun", "rot", t + 0.1, (0, 0.4, 0.6), freq=8, damp=12)
        a.mv("arm_left", 2.0, 2.35, pos=(0, 0, 0), rot=(0, 0, 0))
        # sight down the perforated jacket, then flip the L rear sight
        a.mv("gun", 2.0, 2.6, pos=(-20, -40, -40), rot=(-10, -6, -4), e="inoutsine")
        a.sound(2.7, "click_small")
        a.mv("arm_right", 2.7, 2.9, pos=(-6, 20, -20), rot=(-10, -10, 0))
        a.sound(3.0, "selector")
        a.key("selector", 0.0, pos=(0, 0, 0))
        a.key("selector", 2.95, pos=(0, 0, 0))
        a.key("selector", 3.02, pos=(0, 0, -6), e="outquad")
        a.key("selector", 3.3, pos=(0, 0, -6))
        a.key("selector", 3.37, pos=(0, 0, 0), e="outquad")
        a.sound(3.37, "selector")
        a.mv("arm_right", 3.45, 3.7, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.5, 4.75)
        return a

    cyc = dict(bone="bolt", travel=travel, t_back=0.018, t_fwd=0.045)
    kk = dict(kick=(2.0, 0.6, 1.2), push=9, cycle=cyc)
    fm = Anim(m, "firemode", 0.55)
    fm.mv("gun", 0.0, 0.14, rot=(4, -4, 10), pos=(-4, 3, 4))
    fm.mv("arm_right", 0.04, 0.18, pos=(-2, 10, -36), rot=(0, -6, 4))
    fm.key("selector", 0.0, pos=(0, 0, 0))
    fm.key("selector", 0.2, pos=(0, 0, 0))
    fm.key("selector", 0.25, pos=(0, 0, -6), e="outquad")
    fm.key("selector", 0.55, pos=(0, 0, -6))
    fm.sound(0.23, "selector")
    fm.mv("arm_right", 0.28, 0.45, pos=(0, 0, 0), rot=(0, 0, 0))
    fm.mv("gun", 0.26, 0.55, rot=(0, 0, 0), pos=(0, 0, 0))
    anims = [idle(m), draw(m, 0.7, sound="draw_rifle"),
             fire_basic(m, "fire", recover=0.09, length=0.14, **kk),
             fire_basic(m, "fire_aim", recover=0.08, length=0.13, aim=True, **kk),
             reload("reload", False), reload("reload_empty", True), fm, inspect(), dry_fire(m)]
    return GunAsset(m, anims, {"hip": {"pos": [0.115, -0.12, -0.2], "rot": [0, 4, 0]}, "ads": {"dist": 0.26}})


GUNS = {"mosin": mosin, "m1917": m1917, "arisaka": arisaka, "sks": sks, "ppsh41": ppsh41}
