"""Carl Gustaf m/45 "Swedish K", Winchester Model 1894, Marlin 336, Winchester Model 12 trench gun, Benelli Nova."""
import math

import numpy as np

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden)
from ..templates import (rifle_reload, tube_reload, pump_cycle, lever_cycle, lever_fire, _settle, OFF_LEFT,
                         OFF_LEFT_ROT)
from ..parts import pistol_grip, trigger_group, barrel, straight_mag
from .ww2 import _butt, _band

LEVER_FP = {"hip": {"pos": [0.12, -0.14, -0.2], "rot": [0, 3, 0]}, "ads": {"dist": 0.5}}
SG_FP = {"hip": {"pos": [0.12, -0.13, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.32}}


def _gate_round(m, gate_at, length, d):
    """Cartridge that is thumbed through a side loading gate (lies at the gate, bullet forward)."""
    rl = m["gun"].bone("round_load", pivot=gate_at)
    rl.round_((gate_at[0], gate_at[1], gate_at[2] + length / 2 - 6), length, d)
    br = m["gun"].bone("brass", pivot=(0, 10, -40))
    br.cyl((0, 10, -40), d, length * 0.7, "brass")


def _lever(m, pivot_z, y, rear_z, loop_depth=40, loop_len=70, mat="steel", big_loop=False):
    lv = m["body"].bone("lever", pivot=(0, y, pivot_z))
    lv.box(-4, 4, y - 6, y, pivot_z - 8, rear_z, mat)                                  # lever arm under the receiver
    lz0 = rear_z - loop_len * 0.15
    lz1 = lz0 + loop_len
    yd = y - loop_depth - (14 if big_loop else 0)
    lv.box(-4, 4, yd, y - 4, lz0, lz0 + 9, mat)                                         # front of the finger loop
    lv.box(-4, 4, yd, yd + 7, lz0, lz1, mat)                                            # bottom
    lv.box(-4, 4, yd, y - 14, lz1 - 9, lz1, mat)                                        # rear
    lv.box(-4, 4, y - 18, y - 10, lz1 - 6, lz1 + 40, mat)                               # tang that latches to the wrist
    return lv


def _lever_trigger(m, z, y):
    t = m["body"].bone("trigger", pivot=(0, y, z))
    t.box(-2.5, 2.5, y - 20, y, z - 3, z + 2, "steel", rot=(-8, 0, 0), pivot=(0, y, z))
    return t


def _tube_mag(b, z0, z1, y, d=18, mat="steel"):
    b.cyl((0, y, (z0 + z1) / 2), d, abs(z1 - z0), mat)
    b.cyl((0, y, z1 - 4), d + 4, 8, mat)                                                  # magazine cap


# =================================================================================================
# Carl Gustaf m/45B
# =================================================================================================
def m45():
    A = 6.0
    m = new_gun("m45")
    body = m["body"]
    st = "steel_dark"
    body.cyl((0, 0, 20), 36, 280, st, sides=12)                           # tubular receiver -120 .. 160
    body.box(0, 18.5, -2, 10, -90, -40, "rubber")                         # ejection port
    body.box(17.6, 18.4, -2, 8, -10, 120, "rubber")                       # charging slot
    body.box(17, 21, 8, 12, 118, 128, st)                                 # safety notch
    # perforated jacket
    body.cyl((0, 0, -230), 32, 220, st, sides=12)                         # -120 .. -340
    for i, z in enumerate(range(-330, -140, 26)):
        for yy, xx in ((10, 16.4), (-10, 16.4)):
            body.box(-xx, xx, yy - 4, yy + 4, z, z + 9, "rubber")
        body.box(-4, 4, 16.4, 17.4, z + 13, z + 22, "rubber")
    barrel(body, -330, -352, d=14, mat="steel_light")
    body.box(-6, 6, 14, 30, -336, -326, st)                                # front sight with ears
    body.box(-6, -3, 30, 36, -336, -326, st)
    body.box(3, 6, 30, 36, -336, -326, st)
    body.box(-1, 1, 30, 34, -332, -330, st)
    body.box(-8, 8, 16, 24, 120, 150, st)                                 # rear L sight
    body.box(-8, -1.4, 24, 32, 140, 146, st)
    body.box(1.4, 8, 24, 32, 140, 146, st)
    # magazine housing that doubles as the foregrip
    body.box(-16, 16, -64, -18, -110, -40, st)
    pistol_grip(body, 10, top_y=-18, length=100, width=28, depth=36, angle=-14, mat="polymer")
    trigger_group(m, body, -16, y_top=-18, guard_depth=30, guard_len=60, guard_mat=st)
    # side-folding tube stock (extended)
    stock = m["gun"].bone("stock", pivot=(18, 0, 160))
    stock.box(14, 22, -6, 6, 150, 170, st)                                 # hinge
    stock.cyl((0, 6, 300), 14, 270, st)
    stock.cyl((0, -56, 290), 14, 250, st)
    stock.box(-6, 6, -56, 6, 160, 176, st)
    stock.box(-18, 18, -100, 16, 428, 444, st)                             # butt plate
    stock.box(-6, 6, -100, -56, 412, 430, st, rot=(-10, 0, 0), pivot=(0, -56, 412))
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-12, 12, -10, 12, -70, 40, "steel_light")
    ch = bolt.bone("charging_handle", pivot=(18, 2, 110))
    ch.box(17, 30, -2, 8, 104, 116, "steel_light")
    ch.cyl((34, 3, 110), 12, 10, "steel_light", axis="x")
    mag = m["gun"].bone("magazine", pivot=(0, -18, -76))
    straight_mag(mag, -18, -104, -46, 190, width=24, mat=st, round_d=9, round_len=29)
    add_arms(m, right_hand=(8, -88, 26), left_hand=(-10, -96, -78), right_rot=(34, 14, 6), left_rot=(30, -14, -4))
    add_sockets(m, muzzle=(0, 0, -354), eject=(18, 4, -64), sight=(0, 30, 143))

    def inspect():
        # cock it and hook the handle up into the safety notch, look through the jacket, then unhook it
        a = Anim(m, "inspect", 4.6)
        a.mv("gun", 0.0, 0.4, pos=(-30, 30, 40), rot=(6, -28, -34))
        a.mv("arm_right", 0.15, 0.4, pos=(26, 90, 60), rot=(-40, -20, -30))
        a.grab("arm_right", "charging_handle", 0.42, 1.5, fade_in=0.03, fade_out=0.06)
        a.key("bolt", 0.0, pos=(0, 0, 0))
        a.key("bolt", 0.44, pos=(0, 0, 0))
        a.key("bolt", 0.64, pos=(0, 0, 14), e="inoutquad")
        a.sound(0.6, "charging_handle_back")
        a.key("charging_handle", 0.0, rot=(0, 0, 0))
        a.key("charging_handle", 0.7, rot=(0, 0, 0))
        a.key("charging_handle", 0.82, rot=(0, 0, 60), e="outquad")      # up into the notch
        a.sound(0.82, "safety")
        a.mv("gun", 0.9, 1.4, pos=(-50, 40, 20), rot=(16, -50, -46))
        a.mv("arm_right", 1.56, 1.8, pos=(0, 0, 0), rot=(0, 0, 0))
        # sight down the vented jacket
        a.mv("gun", 1.7, 2.3, pos=(-10, -50, -40), rot=(-12, -6, -4), e="inoutsine")
        a.mv("gun", 2.6, 3.0, pos=(-30, 30, 40), rot=(6, -28, -34))
        a.mv("arm_right", 2.7, 2.95, pos=(26, 90, 60), rot=(-40, -20, -30))
        a.key("charging_handle", 3.1, rot=(0, 0, 60))
        a.key("charging_handle", 3.2, rot=(0, 0, 0), e="inquad")
        a.sound(3.2, "safety")
        a.key("bolt", 3.15, pos=(0, 0, 14))
        a.key("bolt", 3.3, pos=(0, 0, 0), e="inoutsine")
        a.sound(3.3, "charging_handle_forward")
        a.mv("arm_right", 3.35, 3.65, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.4, 4.55)
        return a

    cyc = dict(bone="bolt", travel=(0, 0, 66), t_back=0.022, t_fwd=0.07)
    kk = dict(kick=(2.6, 0.6, 1.4), push=10, cycle=cyc)
    anims = [
        idle(m), draw(m, 0.62, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.14, length=0.2, **kk),
        fire_basic(m, "fire_aim", recover=0.12, length=0.19, aim=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="smg", mag_out=140, mag_sound="smg",
                     tilt=(10, -8, -24), tilt_pos=(-26, 20, 30)),
        rifle_reload(m, "reload_empty", A, empty=True, style="smg", mag_out=140, bolt="bolt", bolt_travel=(0, 0, 66),
                     ch="bolt", ch_travel=(0, 0, 66), bolt_hold_open=False, ch_hand="right", mag_sound="smg",
                     tilt=(10, -8, -24), tilt_pos=(-26, 20, 30)),
        inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, {"hip": {"pos": [0.115, -0.12, -0.21], "rot": [0, 4, 0]}, "ads": {"dist": 0.24}})


# =================================================================================================
# Winchester Model 1894 carbine
# =================================================================================================
def win1894():
    m = new_gun("win1894")
    body = m["body"]
    st = "steel"
    wd = "wood"
    body.box(-13, 13, -36, 18, -110, 40, st)                              # receiver
    body.box(-8, 8, 18, 19, -100, -16, "rubber")                          # top ejection
    body.box(13, 13.4, -30, -16, -66, -34, "steel_dark")                  # loading gate
    body.box(-13.6, -13, -10, 2, -10, 2, "steel_light")                   # saddle ring stud
    body.cyl((-16, -6, -4), 4, 20, "steel_light", axis="y")
    barrel(body, -110, -620, d=18)
    _tube_mag(body, -110, -600, -20, d=16)
    body.box(-6, 6, -16, -4, -606, -594, st)                               # barrel band at the muzzle
    body.box(-4, 4, 9, 16, -610, -594, st)                                 # ramp
    body.box(-1.5, 1.5, 16, 26, -608, -596, "brass")                       # front blade with brass bead
    body.box(-10, 10, 9, 20, -260, -240, st)                               # buckhorn rear sight
    body.box(-10, -1.6, 20, 27, -252, -246, st)
    body.box(1.6, 10, 20, 27, -252, -246, st)
    body.box(-16, 16, -36, 4, -400, -110, wd)                              # forend
    _band(body, -390, top=12, bot=-36, w=16)
    body.box(-14, 14, -40, -8, 40, 150, wd, rot=(4, 0, 0), pivot=(0, -8, 40))   # straight wrist
    _butt(body, 146, 400, wd, "steel", comb_y=-12, heel_drop=18, toe_y=-122, wrist_y=-46, w=18)
    body.box(-6, 6, -8, 2, 40, 120, st)                                     # upper tang
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-7, 7, 4, 18, -48, 40, "steel_light")
    bolt.box(-6, 6, 8, 16, 40, 56, "steel_light")
    ham = bolt.bone("hammer", pivot=(0, -2, 50))
    ham.box(-3, 3, -4, 22, 46, 54, st)
    ham.box(-4, 4, 18, 23, 52, 64, st)                                       # spur
    _lever(m, -80, -36, 40, loop_depth=38, loop_len=66)
    _lever_trigger(m, 26, -36)
    _gate_round(m, (14, -22, -50), 64, 10.5)
    add_arms(m, right_hand=(8, -76, 86), left_hand=(-14, -44, -280), right_rot=(32, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -622), eject=(0, 18, -50), sight=(0, 25.5, -249))
    hrot = (62, 0, 0)

    def inspect():
        # ease the lever open to see brass, close it — then the spin-cock: whip the carbine around the lever hand
        a = Anim(m, "inspect", 4.8)
        a.mv("gun", 0.0, 0.4, pos=(-20, 20, 20), rot=(4, -24, -30))
        a.grab("arm_right", "lever", 0.4, 1.4, fade_in=0.05, fade_out=0.06)
        a.key("lever", 0.0, rot=(0, 0, 0))
        a.key("lever", 0.45, rot=(0, 0, 0))
        a.key("lever", 0.7, rot=(22, 0, 0), e="inoutsine")
        a.sound(0.6, "lever_open")
        a.key("bolt", 0.0, pos=(0, 0, 0))
        a.key("bolt", 0.48, pos=(0, 0, 0))
        a.key("bolt", 0.7, pos=(0, 0, 24), e="inoutsine")
        a.mv("gun", 0.65, 0.95, pos=(-30, 30, 30), rot=(8, -40, -44))
        a.key("lever", 1.15, rot=(22, 0, 0))
        a.key("lever", 1.3, rot=(0, 0, 0), e="inquad")
        a.key("bolt", 1.15, pos=(0, 0, 24))
        a.key("bolt", 1.3, pos=(0, 0, 0), e="inquad")
        a.sound(1.3, "lever_close")
        a.mv("gun", 1.3, 1.6, pos=(0, -30, 30), rot=(0, 0, 0))
        # thumb the hammer to half-cock, show the saddle ring side (it jingles), then ease the hammer down
        a.mv("arm_right", 1.45, 1.65, pos=(-4, 64, -10), rot=(-20, -10, 0))
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 1.66, rot=(0, 0, 0))
        a.key("hammer", 1.76, rot=(-18, 0, 0), e="inoutsine")
        a.sound(1.76, "hammer_thumb")
        a.mv("arm_right", 1.8, 2.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 1.9, 2.5, pos=(-60, 20, 0), rot=(6, 40, 34), e="inoutsine")
        a.shake("gun", "pos", 2.5, 2.9, (0.0, 0.0, 2.0), freq=9, seed=7)
        a.sound(2.55, "click_small")
        a.sound(2.75, "click_small")
        a.mv("gun", 2.9, 3.3, pos=(-20, 20, 20), rot=(4, -24, -30))
        a.mv("arm_right", 3.2, 3.4, pos=(-4, 64, -10), rot=(-20, -10, 0))
        a.key("hammer", 3.42, rot=(-18, 0, 0))
        a.key("hammer", 3.5, rot=(8, 0, 0), e="inoutsine")      # back to full cock
        a.sound(3.5, "hammer_cock")
        a.key("hammer", 3.56, rot=(0, 0, 0))
        a.mv("arm_right", 3.6, 3.85, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.6, 4.75)
        return a

    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             lever_fire(m, "fire", kick=(6.0, 0.6, 1.4), push=20, recover=0.34, length=0.42),
             lever_fire(m, "fire_aim", kick=(6.0, 0.6, 1.4), push=20, recover=0.3, length=0.38, aim=True),
             lever_cycle(m, "cycle", lever_rot=hrot, travel=(0, 0, 72), eject=(10, 190, 30), eject_rot=(-220, 0, 40)),
             lever_cycle(m, "cycle_aim", lever_rot=hrot, travel=(0, 0, 72), aim=True, eject=(10, 190, 30),
                         eject_rot=(-220, 0, 40)),
             *tube_reload(m, port_tilt=(6, -14, 52), port_pos=(-30, 40, 30), load_bone="round_load",
                          push=(0, 0, -50), sound="loading_gate", loop_len=0.56),
             inspect(), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass"])
    return GunAsset(m, anims, LEVER_FP)


# =================================================================================================
# Marlin 336 (side eject, pistol grip, drilled for optics)
# =================================================================================================
def marlin336():
    m = new_gun("marlin336")
    body = m["body"]
    st = "steel"
    wd = "wood_light"
    body.box(-13, 13, -36, 22, -110, 46, st)                               # solid-top receiver
    body.box(13, 13.5, -4, 14, -86, -20, "rubber")                         # side ejection port
    gate = body.bone("gate", pivot=(13, -22, -48))
    gate.box(13, 13.6, -30, -14, -66, -30, "steel_dark")
    body.box(-14, 14, -26, -18, 30, 40, "steel_dark")                      # crossbolt safety
    barrel(body, -110, -620, d=19)
    _tube_mag(body, -110, -560, -21, d=16)
    body.box(-1.5, 1.5, 16, 28, -608, -596, "brass")
    body.box(-5, 5, 9, 16, -610, -594, st)                                  # ramp
    body.box(-10, 10, 9, 22, -260, -240, st)
    body.box(-10, -1.6, 22, 29, -252, -246, st)
    body.box(1.6, 10, 22, 29, -252, -246, st)
    body.box(-16, 16, -38, 4, -390, -110, wd)
    body.box(-17, 17, -30, -10, -370, -330, wd)                             # forend tip
    _band(body, -520, top=12, bot=-30, w=12)
    body.box(-14, 14, -40, -8, 46, 160, wd, rot=(4, 0, 0), pivot=(0, -8, 46))
    body.box(-14, 14, -100, -46, 110, 160, wd, rot=(-26, 0, 0), pivot=(0, -46, 136))   # pistol grip
    body.box(-14.6, 14.6, -102, -96, 126, 160, "polymer", rot=(-26, 0, 0), pivot=(0, -46, 136))
    _butt(body, 156, 420, wd, "rubber", comb_y=-10, heel_drop=16, toe_y=-124, wrist_y=-64, w=18)
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-8, 8, -4, 16, -70, 50, "steel_light")
    ham = bolt.bone("hammer", pivot=(0, -2, 54))
    ham.box(-3, 3, -4, 22, 50, 58, st)
    ham.box(-4, 4, 18, 23, 56, 68, st)
    _lever(m, -84, -36, 44, loop_depth=40, loop_len=72, big_loop=True)
    _lever_trigger(m, 22, -36)
    _gate_round(m, (14, -22, -54), 64, 10.5)
    add_arms(m, right_hand=(8, -86, 110), left_hand=(-14, -44, -280), right_rot=(34, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -622), optic=(0, 22, -30), eject=(14, 6, -50), sight=(0, 27.5, -249))
    hrot = (58, 0, 0)

    def inspect():
        # crossbolt safety on/off, press-check the lever to see brass, then thumb the loading gate
        a = Anim(m, "inspect", 4.6)
        a.mv("gun", 0.0, 0.4, pos=(-30, 20, 30), rot=(4, -26, -30))
        a.mv("arm_right", 0.2, 0.32, pos=(-4, 30, -80), rot=(0, -6, 4))
        a.sound(0.34, "safety")
        a.mv("arm_right", 0.5, 0.6, pos=(6, 30, -80), rot=(0, -6, 4))
        a.sound(0.62, "safety")
        a.mv("arm_right", 0.7, 0.85, pos=(0, 0, 0), rot=(0, 0, 0))
        a.grab("arm_right", "lever", 0.9, 1.9, fade_in=0.05, fade_out=0.06)
        a.key("lever", 0.0, rot=(0, 0, 0))
        a.key("lever", 0.95, rot=(0, 0, 0))
        a.key("lever", 1.2, rot=(18, 0, 0), e="inoutsine")
        a.sound(1.1, "lever_open")
        a.key("bolt", 0.0, pos=(0, 0, 0))
        a.key("bolt", 0.98, pos=(0, 0, 0))
        a.key("bolt", 1.2, pos=(0, 0, 20), e="inoutsine")
        a.mv("gun", 1.1, 1.45, pos=(-40, 30, 40), rot=(10, -46, -50))
        a.key("lever", 1.6, rot=(18, 0, 0))
        a.key("lever", 1.76, rot=(0, 0, 0), e="inquad")
        a.key("bolt", 1.6, pos=(0, 0, 20))
        a.key("bolt", 1.76, pos=(0, 0, 0), e="inquad")
        a.sound(1.76, "lever_close")
        # roll to the right side and press the loading gate in with the left thumb
        a.mv("gun", 1.9, 2.4, pos=(-30, 40, 30), rot=(6, -14, 52))
        a.mv("arm_left", 2.0, 2.45, pos=(30, 30, 230), rot=(-30, 30, 50))
        for t in (2.6, 3.0):
            a.key("gate", t - 0.05, pos=(0, 0, 0))
            a.key("gate", t, pos=(-2.5, 0, 0), e="outquad")
            a.key("gate", t + 0.14, pos=(0, 0, 0), e="inquad")
            a.sound(t + 0.14, "loading_gate")
        a.mv("arm_left", 3.2, 3.6, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.3, 4.55)
        return a

    reload = tube_reload(m, port_tilt=(6, -14, 52), port_pos=(-30, 40, 30), load_bone="round_load",
                         push=(0, 0, -50), sound="loading_gate", loop_len=0.56)
    lp = reload[1]
    lp.key("gate", 0.0, pos=(0, 0, 0))
    lp.key("gate", 0.56 * 0.6, pos=(0, 0, 0))
    lp.key("gate", 0.56 * 0.68, pos=(-2.5, 0, 0), e="outquad")
    lp.key("gate", 0.56 * 0.8, pos=(0, 0, 0), e="inquad")
    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             lever_fire(m, "fire", kick=(6.0, 0.6, 1.4), push=20, recover=0.34, length=0.42),
             lever_fire(m, "fire_aim", kick=(6.0, 0.6, 1.4), push=20, recover=0.3, length=0.38, aim=True),
             lever_cycle(m, "cycle", lever_rot=hrot, travel=(0, 0, 70), eject=(170, 70, 60), eject_rot=(30, 0, -260)),
             lever_cycle(m, "cycle_aim", lever_rot=hrot, travel=(0, 0, 70), aim=True, eject=(170, 70, 60),
                         eject_rot=(30, 0, -260)),
             *reload, inspect(), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass"])
    return GunAsset(m, anims, LEVER_FP)


# =================================================================================================
# Winchester Model 12 trench gun
# =================================================================================================
def _sg_shells(m, port=(0, -32, -30)):
    sl = m["gun"].bone("shell_load", pivot=port)
    sl.shell12((port[0], port[1] - 4, port[2] + 10))
    se = m["gun"].bone("shell_eject", pivot=(14, 6, -40))
    se.shell12((14, 6, -40))


def model12():
    m = new_gun("model12")
    body = m["body"]
    st = "steel"
    wd = "wood"
    body.box(-17, 17, -30, 22, -120, 76, st)
    body.box(0, 17.3, -8, 14, -86, -16, "rubber")
    body.box(-12, 12, -32, -30, -100, -20, "rubber")
    barrel(body, -120, -620, d=21, y=4)
    _tube_mag(body, -120, -520, -22, d=22)
    # ventilated heat shield with the bayonet adapter
    hs = "steel_dark"
    body.box(-15, 15, 6, 22, -540, -170, hs)
    for z in range(-530, -180, 28):
        body.box(-15.4, 15.4, 12, 18, z, z + 12, "rubber")
        body.box(-6, 6, 22, 22.4, z + 14, z + 24, "rubber")
    body.box(-12, 12, -40, 16, -600, -560, hs)                           # bayonet adapter
    body.box(-4, 4, -48, -40, -596, -566, hs)                             # lug
    body.box(-3, 3, 15, 22, -616, -608, st)
    body.box(-1.5, 1.5, 22, 26, -614, -610, "brass")                     # bead on a raised stud
    trigger_group(m, body, 10, y_top=-30, guard_depth=28, guard_len=62, guard_mat=st)
    sel = body.bone("selector", pivot=(0, -36, -26))
    sel.cyl((0, -36, -26), 8, 36, "steel_dark", axis="x")
    body.box(-14, 14, -46, -8, 76, 190, wd, rot=(6, 0, 0), pivot=(0, -8, 76))
    _butt(body, 186, 440, wd, "rubber", comb_y=-14, heel_drop=22, toe_y=-128, wrist_y=-54, w=19)
    pump = m["gun"].bone("pump", pivot=(0, -22, -300))
    pump.box(-21, 21, -42, -4, -380, -230, wd)
    for z in range(-374, -236, 12):
        pump.box(-21.4, 21.4, -38, -8, z, z + 5, "wood_light")             # deep ribs
    pump.box(-5, -2, -14, -6, -230, -70, st)
    pump.box(2, 5, -14, -6, -230, -70, st)
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.8, -6, 12, -84, -24, "steel_light")
    _sg_shells(m)
    add_arms(m, right_hand=(8, -84, 120), left_hand=(-10, -40, -310), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -622), under=None, eject=(17, 4, -50), sight=(0, 25, 70))

    def inspect():
        # run the action wide open and look into the chamber, close it, then knock on the heat shield
        a = Anim(m, "inspect", 4.4)
        a.mv("gun", 0.0, 0.4, pos=(-30, 20, 30), rot=(4, -30, -36))
        a.grab("arm_left", "pump", 0.0, 1.7, fade_in=0.0, fade_out=0.06)
        a.key("pump", 0.0, pos=(0, 0, 0))
        a.key("pump", 0.42, pos=(0, 0, 0))
        a.key("pump", 0.62, pos=(0, 0, 92), e="outquad")
        a.sound(0.6, "pump_back")
        a.mv("gun", 0.62, 0.95, pos=(-40, 30, -10), rot=(10, -30, -50))
        a.key("pump", 1.35, pos=(0, 0, 92))
        a.key("pump", 1.5, pos=(0, 0, 0), e="inquad")
        a.sound(1.5, "pump_forward")
        a.spring("gun", "rot", 1.5, (1.6, 0, -1.4), freq=6, damp=8)
        # knuckle-tap the shield, then tug the bayonet adapter
        a.mv("gun", 1.6, 2.2, pos=(-50, 20, -40), rot=(4, 30, 24))
        a.mv("arm_left", 1.9, 2.25, pos=(-6, 70, -160), rot=(-40, 10, 20))
        for t in (2.35, 2.55):
            a.mv("arm_left", t - 0.08, t, pos=(-6, 62, -160), rot=(-40, 10, 20), e="inquad")
            a.mv("arm_left", t, t + 0.1, pos=(-6, 76, -160), rot=(-40, 10, 20), e="outquad")
            a.sound(t, "tap")
            a.spring("gun", "rot", t, (-0.8, 0, 0), freq=9, damp=12)
        a.mv("arm_left", 2.8, 3.1, pos=(10, 30, -270), rot=(-10, 10, 0))
        a.shake("gun", "pos", 3.1, 3.4, (0, 0, 2), freq=10, seed=5)
        a.sound(3.15, "click_small")
        a.mv("arm_left", 3.4, 3.75, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.4, 4.35)
        return a

    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8, 0.8, 2.0), push=24, recover=0.32, length=0.4),
             fire_basic(m, "fire_aim", kick=(8, 0.8, 2.0), push=24, recover=0.28, length=0.36, aim=True),
             pump_cycle(m, "cycle", travel=(0, 0, 92), length=0.52), pump_cycle(m, "cycle_aim", travel=(0, 0, 92),
                                                                                 length=0.52, aim=True),
             *tube_reload(m), inspect(), dry_fire(m)]
    # slam-fire selector has no lever on a real Model 12 — the "mode" is just holding the trigger while pumping
    fm = Anim(m, "firemode", 0.5)
    fm.mv("gun", 0.0, 0.14, rot=(2, -4, 7), pos=(-4, 3, 4))
    fm.mv("arm_right", 0.04, 0.16, pos=(0, 2, -6), rot=(-6, 0, 0))
    fm.sound(0.18, "click_small")
    fm.mv("arm_right", 0.26, 0.42, pos=(0, 0, 0), rot=(0, 0, 0))
    fm.mv("gun", 0.24, 0.5, rot=(0, 0, 0), pos=(0, 0, 0))
    anims.append(fm)
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, SG_FP)


# =================================================================================================
# Benelli Nova
# =================================================================================================
def nova():
    m = new_gun("nova")
    body = m["body"]
    pl = "polymer"
    body.box(-18, 18, -32, 26, -114, 84, pl)                              # one-piece polymer receiver
    body.box(-18.4, 18.4, -24, 18, -90, 60, "polymer_grey")
    body.box(0, 18.6, -8, 14, -86, -16, "rubber")
    body.box(-12, 12, -34, -32, -100, -20, "rubber")
    barrel(body, -114, -580, d=22, y=4)
    _tube_mag(body, -114, -440, -22, d=24, mat="alloy")
    body.box(-3, 3, 15, 28, -580, -570, "polymer")
    body.box(-1.5, 1.5, 28, 32, -578, -572, "brass")
    body.box(-6, 6, 26, 30, -100, 70, pl)                                  # receiver rib
    pistol_grip(body, 52, top_y=-32, length=96, width=30, depth=36, angle=-18, mat=pl)
    trigger_group(m, body, 14, y_top=-32, guard_depth=28, guard_len=64, guard_mat=pl)
    rel = body.bone("latch", pivot=(0, -60, -20))
    rel.box(-4, 4, -64, -58, -26, -16, "polymer_grey")                    # pump release button
    sel = body.bone("selector", pivot=(0, -36, 46))
    sel.cyl((0, -36, 46), 8, 38, "steel_dark", axis="x")
    body.box(-16, 16, -40, -6, 84, 190, pl)
    _butt(body, 186, 420, pl, "rubber", comb_y=-10, heel_drop=18, toe_y=-126, wrist_y=-60, w=19)
    pump = m["gun"].bone("pump", pivot=(0, -22, -280))
    pump.box(-23, 23, -46, -2, -380, -220, pl)
    for z in range(-370, -230, 20):
        pump.box(-23.4, 23.4, -40, -10, z, z + 8, "polymer_grey")
    pump.box(-5, -2, -14, -6, -220, -70, "steel")
    pump.box(2, 5, -14, -6, -220, -70, "steel")
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 18, -6, 12, -82, -22, "steel_light")
    _sg_shells(m)
    add_arms(m, right_hand=(8, -94, 72), left_hand=(-10, -44, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -582), optic=(0, 30, -20), eject=(18, 4, -50), sight=(0, 31, 70))

    def inspect():
        # press the pump release in front of the guard, slide the forend half back, then roll to the loading port
        a = Anim(m, "inspect", 4.2)
        a.mv("gun", 0.0, 0.4, pos=(-30, 20, 30), rot=(2, -20, -30))
        a.mv("arm_right", 0.2, 0.34, pos=(0, 20, -60), rot=(-8, 0, 0))
        a.key("latch", 0.0, pos=(0, 0, 0))
        a.key("latch", 0.36, pos=(0, 0, 0))
        a.key("latch", 0.4, pos=(0, 2.5, 0), e="outquad")
        a.sound(0.4, "click_small")
        a.key("latch", 0.7, pos=(0, 2.5, 0))
        a.key("latch", 0.74, pos=(0, 0, 0))
        a.mv("arm_right", 0.6, 0.8, pos=(0, 0, 0), rot=(0, 0, 0))
        a.grab("arm_left", "pump", 0.0, 1.5, fade_in=0.0, fade_out=0.06)
        a.key("pump", 0.0, pos=(0, 0, 0))
        a.key("pump", 0.44, pos=(0, 0, 0))
        a.key("pump", 0.7, pos=(0, 0, 36), e="inoutsine")
        a.sound(0.66, "pump_back_light")
        a.mv("gun", 0.7, 1.0, pos=(-40, 30, 40), rot=(10, -44, -52))
        a.key("pump", 1.2, pos=(0, 0, 36))
        a.key("pump", 1.36, pos=(0, 0, 0), e="inquad")
        a.sound(1.36, "pump_forward")
        a.spring("gun", "rot", 1.36, (1.4, 0, -1.2), freq=6, damp=8)
        # roll it over to show the loading port, slap the polymer receiver
        a.mv("gun", 1.6, 2.2, pos=(-30, 40, -90), rot=(14, -6, -48), e="inoutsine")
        a.mv("gun", 2.5, 2.9, pos=(-20, 40, -90), rot=(10, -4, -40))
        a.sound(2.6, "tap")
        a.spring("gun", "rot", 2.6, (0, 0, 2.4), freq=7, damp=9)
        _settle(a, 2.95, 4.15)
        return a

    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8.5, 0.8, 2.0), push=25, recover=0.32, length=0.4),
             fire_basic(m, "fire_aim", kick=(8.5, 0.8, 2.0), push=25, recover=0.28, length=0.36, aim=True),
             pump_cycle(m, "cycle", travel=(0, 0, 84)), pump_cycle(m, "cycle_aim", travel=(0, 0, 84), aim=True),
             *tube_reload(m), inspect(), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, SG_FP)


GUNS = {"m45": m45, "win1894": win1894, "marlin336": marlin336, "model12": model12, "nova": nova}
