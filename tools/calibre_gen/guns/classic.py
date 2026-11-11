"""Carl Gustaf m/45 "Swedish K", Winchester Model 1894, Marlin 336, Winchester Model 12 trench gun, Benelli Nova."""
import math

import numpy as np

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden)
from ..templates import (rifle_reload, tube_reload, pump_cycle, lever_cycle, lever_fire, _settle, OFF_LEFT,
                         OFF_LEFT_ROT)
from ..parts import pistol_grip, trigger_group, barrel, straight_mag
from ..shotkit import sg_receiver, port_bolt, sg_barrel, sg_tube, forend, sg_butt, crossbolt
from ..parts import screw
from ..common import moving
from ..pistolkit import control
from ..riflekit import stock, band, butt_plate
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
    body.rbox(-16, 16, -64, -18, -110, -40, st, r=4, axis="y")
    pistol_grip(body, 10, top_y=-18, length=100, width=28, depth=36, angle=-14, mat="polymer")
    trigger_group(m, body, -16, y_top=-18, guard_depth=30, guard_len=60, guard_mat=st)
    # side-folding tube stock (extended)
    stock = m["gun"].bone("stock", pivot=(18, 0, 160))
    stock.box(14, 22, -6, 6, 150, 170, st)                                 # hinge
    stock.cyl((0, 6, 300), 14, 270, st)
    stock.cyl((0, -56, 290), 14, 250, st)
    stock.box(-6, 6, -56, 6, 160, 176, st)
    stock.rbox(-18, 18, -100, 16, 428, 444, st, r=5)                       # butt plate
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
    # Winchester Model 1894 carbine: 960 mm long, 508 mm barrel, full-length tube, straight grip, saddle ring
    m = new_gun("win1894")
    body = m["body"]
    st, wd = "steel", "wood"
    body.rbox(-13, 13, -36, 18, -110, 40, st, r=3, edges="top")           # receiver
    body.box(-8, 8, 17.6, 18.6, -100, -16, "rubber")                      # top ejection
    body.rbox(13, 13.6, -30, -16, -66, -34, "steel_dark", r=0.2)          # loading gate
    for y, z in ((-8, -84), (-26, -20), (4, 22)):
        screw(body, 13, y, z, d=5)
        screw(body, -13, y, z, d=5)
    body.box(-14.6, -13, -8, -2, -8, 0, "steel_light")                    # saddle ring stud and ring
    for z in (-12, 2):
        body.box(-17, -15, -22, -4, z, z + 2, "steel_light")
    body.box(-17, -15, -24, -22, -12, 4, "steel_light")
    barrel(body, -110, -604, d=18)
    _tube_mag(body, -110, -590, -20, d=16)
    body.rbox(-9, 9, -30, 11, -590, -578, st, r=5)                        # front band
    body.rbox(-4, 4, 9, 16, -598, -574, st, r=2, edges="top")             # ramp
    body.box(-1.2, 1.2, 16, 25.5, -592, -582, st)
    body.box(-1.6, 1.6, 22.4, 25.6, -592.4, -589, "brass")                # bead
    body.box(-9, 9, 9, 13, -276, -236, st)                                # buckhorn rear sight
    body.box(-3, 3, 13, 15, -268, -244, st)
    for sx in (-1, 1):
        body.box(sx * 5.3 - 3.7, sx * 5.3 + 3.7, 13, 26.5, -252, -247, st, rot=(0, 0, sx * -8), pivot=(sx * 6, 13, -250))
    stock(body, [(-402, 4), (-110, 4)], [(-402, -32), (-110, -36)], [(-402, -110, 16)], wd)      # fore-end
    band(body, -392, -33.5, 12, 17, st, w=12)
    body.rbox(-6, 6, -8, 3, 40, 122, st, r=2, edges="top")                # upper tang
    top, bot = sg_butt(body, wd, 40, 356, top0=4, bot0=-36, comb=-12, heel=-30, toe=-118, grip=False, pad=None,
                       plate=st, hw=(14, 17))
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.rbox(-7, 7, 4, 18.4, -48, 40, "steel_light", r=3, edges="top")
    bolt.box(-6, 6, 8, 16, 40, 56, "steel_light")
    ham = bolt.bone("hammer", pivot=(0, -2, 50))
    ham.box(-3, 3, -4, 22, 46, 54, st)
    ham.rbox(-4, 4, 18, 23, 52, 64, st, r=1.5, axis="x")                  # spur
    _lever(m, -80, -36, 40, loop_depth=38, loop_len=66)
    _lever_trigger(m, 26, -36)
    _gate_round(m, (14, -22, -50), 64, 10.5)
    add_arms(m, right_hand=(8, -76, 86), left_hand=(-14, -44, -280), right_rot=(32, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -605), eject=(0, 18, -50), sight=(0, 25.5, -249))

    hrot = (62, 0, 0)

    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             lever_fire(m, "fire", kick=(6.0, 0.6, 1.4), push=20, recover=0.34, length=0.42),
             lever_fire(m, "fire_aim", kick=(6.0, 0.6, 1.4), push=20, recover=0.3, length=0.38, aim=True),
             lever_cycle(m, "cycle", lever_rot=hrot, travel=(0, 0, 72), eject=(10, 190, 30), eject_rot=(-220, 0, 40)),
             lever_cycle(m, "cycle_aim", lever_rot=hrot, travel=(0, 0, 72), aim=True, eject=(10, 190, 30),
                         eject_rot=(-220, 0, 40)),
             *tube_reload(m, port_tilt=(6, -14, 52), port_pos=(-30, 40, 30), load_bone="round_load",
                          push=(0, 0, -50), sound="loading_gate", loop_len=0.56),
             Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass"])
    return GunAsset(m, anims, LEVER_FP)


# =================================================================================================
# Marlin 336 (side eject, pistol grip, drilled for optics)
# =================================================================================================
def marlin336():
    # Marlin 336: 978 mm long, 508 mm barrel, solid-top receiver with side ejection, pistol-grip stock
    m = new_gun("marlin336")
    body = m["body"]
    st, wd = "steel", "wood_light"
    body.rbox(-13, 13, -36, 22, -110, 46, st, r=6, edges="top")            # solid-top receiver
    body.box(13, 13.5, -4, 13, -86, -20, "rubber")                         # side ejection port
    body.box(12.6, 13.2, -2.5, 11.5, -84, -24, "steel_light")              # the bolt in it
    for y, z in ((-10, -92), (-28, -10), (6, 30)):
        screw(body, 13, y, z, d=5)
        screw(body, -13, y, z, d=5)
    gate = body.bone("gate", pivot=(13, -22, -48))
    gate.box(13, 13.6, -30, -14, -66, -30, "steel_dark")
    sf = body.bone("safety", pivot=(0, -22, 35))                           # cross-bolt safety
    sf.cyl((0.8, -22, 35), 8, 29, "steel_dark", axis="x", sides=8)
    moving(m, "safety", pos=(-2.4, 0, 0))
    barrel(body, -110, -616, d=19)
    _tube_mag(body, -110, -540, -21, d=16)
    body.rbox(-5, 5, 9, 16, -610, -584, st, r=2, edges="top")              # ramp with a hooded bead
    body.box(-1.2, 1.2, 16, 27.5, -602, -592, st)
    body.box(-1.6, 1.6, 24.4, 27.6, -602.4, -599, "brass")
    body.box(-9, 9, 9, 13, -276, -236, st)                                 # semi-buckhorn rear sight
    body.box(-3, 3, 13, 15, -268, -244, st)
    for sx in (-1, 1):
        body.box(sx * 5.3 - 3.7, sx * 5.3 + 3.7, 13, 28.5, -252, -247, st, rot=(0, 0, sx * -8), pivot=(sx * 6, 13, -250))
    stock(body, [(-392, 4), (-110, 4)], [(-392, -32), (-110, -38)], [(-392, -110, 16)], wd)      # fore-end
    body.rbox(-16.6, 16.6, -33, 5, -400, -390, st, r=5)                    # fore-end cap
    band(body, -520, -30, 11.5, 10, st, w=10)                              # barrel band on the tube
    body.rbox(-6, 6, -8, 5, 46, 124, st, r=2, edges="top")
    top, bot = sg_butt(body, wd, 46, 362, top0=6, bot0=-36, comb=-8, heel=-28, toe=-120, grip=True, pad="rubber",
                       pad_th=10, hw=(14, 17), spacer="white", checker="wood")
    body.rbox(-14.4, 14.4, -77.5, -74, 86, 114, "polymer", r=1.2, axis="y")           # grip cap
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-8, 8, -4, 16, -70, 50, "steel_light")
    ham = bolt.bone("hammer", pivot=(0, -2, 54))
    ham.box(-3, 3, -4, 24, 50, 58, st)
    ham.rbox(-4, 4, 20, 25, 56, 68, st, r=1.5, axis="x")
    _lever(m, -84, -36, 44, loop_depth=40, loop_len=72, big_loop=True)
    _lever_trigger(m, 22, -36)
    _gate_round(m, (14, -22, -54), 64, 10.5)
    add_arms(m, right_hand=(8, -86, 110), left_hand=(-14, -44, -280), right_rot=(34, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -617), optic=(0, 22, -30), eject=(14, 6, -50), sight=(0, 27.5, -249))

    hrot = (58, 0, 0)

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
             *reload, Anim(m, "inspect", 1.0), dry_fire(m)]
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
    # Winchester Model 12 "trench gun": 1003 mm long, 510 mm barrel, heat shield and bayonet adapter
    m = new_gun("model12")
    body = m["body"]
    st, wd, hs = "steel", "wood", "steel_dark"
    roof = sg_receiver(body, -120, 76, st, port=(-86, -16))
    sg_barrel(body, -120, -637, d=21, y=4, mat=st, bead=False)
    sg_tube(body, -120, -520, y=-22, d=22, mat=st)
    body.rbox(-15, 15, 4, 23, -548, -170, hs, r=8, edges="top")              # ventilated heat shield
    for z in range(-536, -186, 28):
        for sx in (-1, 1):
            body.box(sx * 15 - 0.4, sx * 15 + 0.4, 6, 12, z, z + 12, "rubber")
        body.box(-4, 4, 22.6, 23.4, z + 14, z + 24, "rubber")
    body.rbox(-13, 13, -40, 17, -612, -572, hs, r=4)                          # bayonet adapter
    body.box(-4, 4, -49, -40, -606, -578, hs)
    for z in (-600, -584):
        body.cyl((13.3, -8, z), 5, 0.8, "steel", axis="x", sides=8)
    body.box(-3, 3, 14, 21.6, -632, -624, st)                                 # bead on its raised stud
    body.box(-1.5, 1.5, 21.6, 25, -630, -626, "brass")
    trigger_group(m, body, 10, y_top=-30, guard_depth=28, guard_len=62, guard_mat=st)
    crossbolt(body, -20, -42)
    sg_butt(body, wd, 76, 366)
    pump = m["gun"].bone("pump", pivot=(0, -22, -300))
    forend(pump, -380, -230, wd, grooves=12, groove_mat="wood_red")
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    port_bolt(bolt, (-86, -16), roof=roof)
    _sg_shells(m)
    add_arms(m, right_hand=(8, -84, 120), left_hand=(-10, -40, -310), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -638), under=None, eject=(17, 4, -50), sight=(0, 25, 70))


    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8, 0.8, 2.0), push=24, recover=0.32, length=0.4),
             fire_basic(m, "fire_aim", kick=(8, 0.8, 2.0), push=24, recover=0.28, length=0.36, aim=True),
             pump_cycle(m, "cycle", travel=(0, 0, 92), length=0.52), pump_cycle(m, "cycle_aim", travel=(0, 0, 92),
                                                                                 length=0.52, aim=True),
             *tube_reload(m), Anim(m, "inspect", 1.0), dry_fire(m)]
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
    # Benelli Nova: 1257 mm long, 711 mm vent-rib barrel, one-piece polymer receiver and stock
    m = new_gun("nova")
    body = m["body"]
    pl = "polymer"
    roof = sg_receiver(body, -114, 84, pl, hw=18, y0=-32, y1=26, port=(-86, -16), pin=False)
    for sx in (-1, 1):
        body.box(sx * 18 - 0.3, sx * 18 + 0.3, -26, -12, -100, 70, "polymer_grey")   # moulded panel line
    top = sg_barrel(body, -114, -887, d=22, y=4, mat="steel_dark", rib="steel_dark")
    sg_tube(body, -114, -520, y=-22, d=24, mat="alloy")
    trigger_group(m, body, 14, y_top=-32, guard_depth=28, guard_len=64, guard_mat=pl)
    rel = body.bone("latch", pivot=(0, -60, -20))
    rel.box(-4, 4, -64, -58, -26, -16, "polymer_grey")                    # pump release button
    crossbolt(body, 42, -44)
    sg_butt(body, pl, 84, 370, top0=20, bot0=-32, comb=-6, heel=-30, toe=-122, checker="polymer_grey")
    pump = m["gun"].bone("pump", pivot=(0, -22, -280))
    forend(pump, -390, -220, pl, hw=23, y0=-46, y1=-2, grooves=7, groove_mat="polymer_grey")
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    port_bolt(bolt, (-86, -16), hw=18, roof=roof)
    _sg_shells(m)
    add_arms(m, right_hand=(8, -88, 124), left_hand=(-10, -44, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -888), optic=(0, 30, -20), eject=(18, 4, -50), sight=(0, top + 0.5, 70))


    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8.5, 0.8, 2.0), push=25, recover=0.32, length=0.4),
             fire_basic(m, "fire_aim", kick=(8.5, 0.8, 2.0), push=25, recover=0.28, length=0.36, aim=True),
             pump_cycle(m, "cycle", travel=(0, 0, 84)), pump_cycle(m, "cycle_aim", travel=(0, 0, 84), aim=True),
             *tube_reload(m), Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, SG_FP)


GUNS = {"m45": m45, "win1894": win1894, "marlin336": marlin336, "model12": model12, "nova": nova}
