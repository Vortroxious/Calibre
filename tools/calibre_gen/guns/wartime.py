"""WWII pack: Mauser Kar98k, M1 Garand, Lee-Enfield No.4 Mk I, Thompson M1A1, MP 40, StG 44, MG 42, M1918 BAR."""
import numpy as np

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden)
from ..templates import bolt_clip_load, belt_reload, OFF_LEFT
from ..parts import pistol_grip, trigger_group, curved_mag, straight_mag, barrel, bipod, flash_hider_a2
from .ww2 import _military_bolt, _clip, _round_load, _bolt_set, _butt, _band, RIFLE_FP
from .lmgs import _belt, _belt_feed, LMG_FP
from .modern import _rifle_anims, _inspect, _fp


def _rifle_stock(body, z_rear, wd="wood", st="steel", wrist=(116, 236), butt=(236, 460)):
    body.box(-15, 15, -62, -10, wrist[0], wrist[1], wd, rot=(4, 0, 0), pivot=(0, -10, wrist[0]))
    _butt(body, butt[0], butt[1], wd, st, comb_y=-16, heel_drop=22, toe_y=-134, wrist_y=-70)


# =================================================================================================
# Mauser Kar98k
# =================================================================================================
def kar98k():
    m = new_gun("kar98k")
    body = m["body"]
    st, wd = "steel_dark", "wood"
    body.cyl((0, 0, -10), 32, 200, st, sides=12)                         # round receiver
    body.box(-9, 9, 15, 16.6, -80, 6, "rubber")
    body.box(-10, -7, 14, 24, 4, 14, st)                                 # charger guide
    body.box(7, 10, 14, 24, 4, 14, st)
    body.box(-6, 6, -14, 14, 90, 140, st)
    body.cyl((0, 0, -190), 24, 160, st)
    barrel(body, -270, -740, d=18)
    body.box(-6, 6, 9, 20, -740, -716, st)                               # hooded front sight
    body.box(-8, 8, 20, 32, -738, -718, st)
    body.box(-1, 1, 14, 26, -730, -728, st)
    body.box(-12, 12, 10, 20, -250, -150, st)                            # tangent rear sight
    body.box(-9, 9, 20, 26, -170, -160, st)
    body.box(-17, 17, -40, 4, -560, -110, wd)                            # forend
    body.box(-14, 14, 4, 15, -540, -280, wd)                             # upper handguard
    body.box(-18, 18, -54, -6, -110, 120, wd)
    _band(body, -540, top=16, bot=-42, mat=st)
    _band(body, -380, top=16, bot=-42, mat=st)
    body.box(-6, 6, -54, -40, -600, -560, st)                            # bayonet lug / nose cap
    body.cyl((0, -16, -650), 6, 180, "steel_light")
    body.box(-14, 14, -68, -54, -70, 4, st)                              # flush floorplate
    trigger_group(m, body, 40, y_top=-54, guard_depth=24, guard_len=56, guard_mat=st)
    _rifle_stock(body, 460)
    body.box(-16, 16, -96, -80, 300, 360, "rubber")                      # sling cut-out
    _military_bolt(m, -70, 104, 98, handle_len=46, knob_d=20, cock=(24, 26))
    _clip(m, (0, 15, 10), case_len=57, bullet_len=24, d=12)
    _round_load(m, (0, 12, -26), 80, 12)
    add_arms(m, right_hand=(10, -74, 168), left_hand=(-14, -46, -320), right_rot=(30, 12, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -742), eject=(16, 10, -30), sight=(0, 28, -160))
    travel, hrot = (0, 0, 92), (0, 0, 84)
    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             *_bolt_set(m, travel, hrot, kick=(7.8, 0.7, 1.6), push=24, cycle_len=0.88),
             *bolt_clip_load(m, travel=travel, handle_rot=hrot, push=52), _inspect(m), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    return GunAsset(m, anims, RIFLE_FP)


# =================================================================================================
# M1 Garand: 8-round en-bloc clip, loaded from the top; the empty clip "pings" out after the last shot
# =================================================================================================
def garand():
    m = new_gun("garand")
    body = m["body"]
    st, wd = "steel_parked", "wood"
    body.box(-16, 16, -30, 16, -110, 100, st)                            # receiver
    body.box(-10, 10, 16, 18, -80, 40, "rubber")                         # open top (clip well)
    body.box(-12, 12, 16, 34, 70, 100, st)                               # rear sight housing
    body.box(-6, 6, 34, 44, 78, 92, st)                                  # aperture
    barrel(body, -110, -620, d=19)
    body.box(-10, 10, -6, 18, -630, -596, st)                            # gas cylinder + front sight
    body.box(-6, 6, -22, -6, -630, -600, st)
    body.box(-6, 6, 18, 30, -618, -606, st)
    body.box(-1, 1, 24, 34, -614, -610, st)
    body.cyl((0, -14, -360), 12, 480, st)                                # op-rod tube
    body.box(-17, 17, -44, 2, -500, -110, wd)                            # forend
    body.box(-14, 14, 2, 14, -480, -200, wd)                             # upper handguard
    body.box(-18, 18, -56, -8, -110, 120, wd)
    _band(body, -480, top=18, bot=-48, mat=st)
    trigger_group(m, body, 36, y_top=-56, guard_depth=26, guard_len=58, guard_mat=st)
    sf = body.bone("safety", pivot=(0, -56, -10))
    sf.box(-4, 4, -66, -56, -16, -4, st)
    _rifle_stock(body, 450)
    # operating rod + handle (right side) = the "bolt" that cycles and locks back on empty
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(14, 22, -18, -8, -400, -20, st)
    bolt.box(18, 34, -18, -4, -40, -20, st)                              # op-rod handle
    bolt.box(-10, 10, 0, 14, -60, 40, "steel_light")                     # bolt in the receiver
    # en-bloc clip with 8 rounds (the "magazine")
    mag = m["gun"].bone("magazine", pivot=(0, 14, -24))
    mag.box(-11, 11, -40, 14, -46, 2, "steel")
    for i in range(4):
        for sx in (-4.5, 4.5):
            mag.round_((sx, 10 - i * 10 + (2 if sx > 0 else 0), -24), 78, 11.5)
    add_arms(m, right_hand=(10, -76, 168), left_hand=(-14, -48, -320), right_rot=(30, 12, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -622), eject=(16, 12, -20), sight=(0, 40, 88))
    TRAVEL = (0, 0, 92)
    up = np.array([0.0, 150.0, 30.0])

    def ping(a, t):
        """The empty clip flies out of the top with its ping."""
        a.key("magazine", t, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("magazine", t + 0.12, pos=up * 0.6, rot=(-40, 0, 20), e="outquad")
        a.key("magazine", t + 0.3, pos=up + (30, 40, 40), rot=(-140, 30, 60), e="linear")
        a.key("magazine", t, scale=1)
        a.key("magazine", t + 0.3, scale=1)
        a.key("magazine", t + 0.301, scale=0)
        a.sound(t + 0.04, "clip_eject")

    def load(a, t0, empty):
        """Hand brings a full clip over the receiver and thumbs it down; the op rod slams forward."""
        hl = np.asarray(m.bones["arm_left"].pivot, dtype=float)
        piv = np.asarray(mag.pivot, dtype=float)
        a.mv("gun", 0.0, 0.3, pos=(-20, 18, 24), rot=(6, -8, -28), e="inoutsine")
        start = np.array([-60.0, -200.0, 80.0])
        over = np.array([0.0, 70.0, 0.0])
        a.key("arm_left", t0 - 0.35, pos=OFF_LEFT)
        a.key("arm_left", t0, pos=piv + start + (0, 10, 0) - hl, e="inoutsine")
        a.key("magazine", t0, pos=start, rot=(30, 0, 0))
        a.key("magazine", t0, scale=1)
        a.key("magazine", t0 + 0.42, pos=over, rot=(0, 0, 0), e="inoutcubic")
        a.key("arm_left", t0 + 0.42, pos=piv + over + (0, 18, 0) - hl, e="inoutcubic")
        a.sound(t0 + 0.1, "pouch")
        a.key("magazine", t0 + 0.6, pos=(0, 0, 0), e="inquad")
        a.key("arm_left", t0 + 0.6, pos=piv + (0, 22, 0) - hl, e="inquad")
        a.sound(t0 + 0.56, "clip_insert")
        # thumb out of the way, the op rod slams the bolt home
        a.key("arm_left", t0 + 0.7, pos=piv + (-40, 60, 20) - hl, e="outquad")
        a.key("bolt", t0 + 0.72, pos=TRAVEL)
        a.key("bolt", t0 + 0.8, pos=(0, 0, 0), e="inquad")
        a.sound(t0 + 0.8, "bolt_forward")
        a.kick("gun", "rot", t0 + 0.8, (2, 0, 1.2), attack=0.03, recover=0.25)
        a.mv("arm_left", t0 + 0.9, t0 + 1.3, pos=(0, 0, 0))
        a.mv("gun", t0 + 0.95, t0 + 1.45, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")

    def reload(name, empty):
        L = 2.1 if empty else 2.45
        a = Anim(m, name, L)
        a.key("bolt", 0.0, pos=TRAVEL if empty else (0, 0, 0))
        if not empty:
            # pull the op rod back and press the clip latch: the partial clip pings out
            a.mv("arm_right", 0.05, 0.25, pos=(10, 40, -170), rot=(-20, -20, -20))
            a.key("bolt", 0.25, pos=(0, 0, 0))
            a.key("bolt", 0.38, pos=TRAVEL, e="outquad")
            a.sound(0.34, "bolt_back")
            ping(a, 0.4)
            a.mv("arm_right", 0.5, 0.7, pos=(0, 0, 0))
            t0 = 0.95
        else:
            a.key("magazine", 0.0, scale=0)
            t0 = 0.5
        load(a, t0, empty)
        return a

    cyc = dict(bone="bolt", travel=TRAVEL, t_back=0.02, t_fwd=0.06)
    kk = dict(kick=(4.6, 0.6, 1.4), push=16, cycle=cyc)
    last = fire_basic(m, "fire_last", recover=0.2, length=0.5, lock_back=True, **kk)
    ping(last, 0.03)
    anims = [idle(m), idle(m, "idle_empty", locked={"bolt": TRAVEL}, extra_hidden=("magazine",)),
             draw(m, 0.8, sound="draw_rifle"),
             fire_basic(m, "fire", recover=0.2, length=0.3, **kk),
             fire_basic(m, "fire_aim", recover=0.17, length=0.27, aim=True, **kk), last,
             reload("reload", False), reload("reload_empty", True), _inspect(m), dry_fire(m)]
    return GunAsset(m, anims, {"hip": RIFLE_FP["hip"], "ads": {"dist": 0.3}})


# =================================================================================================
# Lee-Enfield No.4 Mk I (10-round box, loaded with two chargers; cock-on-close)
# =================================================================================================
def enfield():
    m = new_gun("enfield")
    body = m["body"]
    st, wd = "steel_dark", "wood"
    body.box(-15, 15, -18, 16, -110, 90, st)                             # receiver
    body.box(-9, 9, 16, 17.6, -70, 10, "rubber")
    body.box(-12, 12, 16, 34, 40, 80, st)                                # peep sight protectors
    body.box(-6, 6, 30, 44, 54, 66, st)
    barrel(body, -110, -720, d=19)
    body.box(-8, 8, 8, 20, -720, -700, st)                               # protected front sight
    body.box(-9, -7, 8, 32, -718, -702, st)
    body.box(7, 9, 8, 32, -718, -702, st)
    body.box(-1, 1, 14, 28, -712, -710, st)
    body.box(-17, 17, -40, 4, -640, -110, wd)                            # forend almost to the muzzle
    body.box(-14, 14, 4, 16, -620, -140, wd)
    _band(body, -620, top=18, bot=-42, mat=st)
    _band(body, -400, top=18, bot=-42, mat=st)
    body.box(-14, 14, -40, -18, -110, 116, wd)
    trigger_group(m, body, 40, y_top=-40, guard_depth=26, guard_len=56, guard_mat=st)
    # detachable 10-round box under the action
    mag = m["gun"].bone("magazine", pivot=(0, -40, -40))
    mag.box(-13, 13, -96, -40, -80, -6, st)
    mag.box(-14, 14, -100, -96, -82, -4, st)
    _rifle_stock(body, 470)
    _military_bolt(m, -70, 110, 104, handle_len=48, knob_d=22, cock=(22, 24))
    _clip(m, (0, 16, 14), case_len=56, bullet_len=22, d=12)
    _round_load(m, (0, 12, -26), 78, 12)
    add_arms(m, right_hand=(10, -74, 168), left_hand=(-14, -46, -340), right_rot=(30, 12, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -722), eject=(16, 10, -30), sight=(0, 40, 60))
    travel, hrot = (0, 0, 96), (0, 0, 70)
    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             *_bolt_set(m, travel, hrot, kick=(7.4, 0.7, 1.6), push=23, cycle_len=0.72),
             *bolt_clip_load(m, travel=travel, handle_rot=hrot, push=52), _inspect(m), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    return GunAsset(m, anims, {"hip": RIFLE_FP["hip"], "ads": {"dist": 0.3}})


# =================================================================================================
# Thompson M1A1
# =================================================================================================
def thompson():
    m = new_gun("thompson")
    body = m["body"]
    st, wd = "steel_parked", "wood"
    body.box(-17, 17, -34, 22, -120, 110, st)                            # milled receiver
    body.box(0, 17.3, -6, 12, -60, -10, "rubber")
    body.box(-10, 10, 22, 34, 70, 100, st)                               # rear sight ears
    body.box(-2, 2, 22, 30, -110, -100, st)
    barrel(body, -120, -380, d=20)
    body.box(-20, 20, -44, -12, -320, -150, wd)                          # horizontal handguard
    body.box(-17, 17, -46, -34, -110, -50, st)                           # mag well
    pistol_grip(body, 30, top_y=-34, length=88, width=28, depth=38, angle=-18, mat=wd)
    trigger_group(m, body, -10, y_top=-34, guard_depth=28, guard_len=60, guard_mat=st)
    sel = body.bone("selector", pivot=(-17, -20, 30))
    sel.box(-21, -17, -24, -16, 24, 38, "steel")
    ch = body.bone("charging_handle", pivot=(17, 4, -40))                  # M1A1: actuator knob on the right
    ch.box(17, 28, 0, 8, -46, -34, "steel")
    ch.cyl((30, 4, -40), 12, 6, "steel", axis="x")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 17, -4, 10, -58, -12, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 110))
    stock.taper(-17, 17, 110, 420, 12, -4, -36, -112, wd)
    stock.box(-18, 18, -116, -2, 416, 428, st)
    mag = m["gun"].bone("magazine", pivot=(0, -40, -80))
    straight_mag(mag, -36, -102, -58, 220, width=24, mat="steel_dark", round_d=11, round_len=30)
    _thompson_detail(m, body)
    add_arms(m, right_hand=(8, -94, 50), left_hand=(-10, -40, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -386), eject=(17, 4, -30), sight=(0, 32, 86))
    cyc = dict(bone="bolt", travel=(0, 0, 80), t_back=0.016, t_fwd=0.05)
    anims = _rifle_anims(m, 0.0, (2.4, 0.4, 1.0), 9, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 80),
                         selector=(-40, 0, 0), mag_sound="smg", rec=0.12, length=0.2)
    return GunAsset(m, anims, _fp(pos=(0.115, -0.12, -0.19), ads=0.22))


# =================================================================================================
# MP 40
# =================================================================================================
def mp40():
    m = new_gun("mp40")
    body = m["body"]
    st = "steel_dark"
    body.cyl((0, 0, -20), 30, 260, st, sides=12)                         # tubular receiver
    body.box(0, 15.3, -6, 8, -70, -30, "rubber")
    barrel(body, -150, -290, d=16)
    body.box(-6, 6, -16, -8, -300, -270, st)                             # barrel rest bar
    body.box(-8, 8, 10, 24, -290, -280, st)                              # hooded front sight
    body.box(-2, 2, 14, 22, 70, 80, st)
    body.box(-15, 15, -56, -14, -150, -30, "polymer")                    # bakelite lower
    body.box(-13, 13, -60, -14, -130, -90, st)                           # mag housing
    pistol_grip(body, 30, top_y=-30, length=86, width=26, depth=34, angle=-10, mat="polymer")
    trigger_group(m, body, -10, y_top=-30, guard_depth=24, guard_len=52, guard_mat=st)
    ch = body.bone("charging_handle", pivot=(-15, 0, -40))
    ch.box(-30, -15, -4, 6, -50, -30, "steel")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 15, -4, 8, -68, -32, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 110))                    # under-folding stock (folded)
    for sx in (-10, 10):
        stock.box(sx - 3, sx + 3, -70, -62, -120, 120, "steel")
    stock.box(-16, 16, -80, -60, -132, -118, st)
    mag = m["gun"].bone("magazine", pivot=(0, -60, -110))
    straight_mag(mag, -58, -122, -98, 220, width=20, mat="steel_dark", round_d=9, round_len=28)
    _mp40_detail(m, body)
    add_arms(m, right_hand=(8, -88, 50), left_hand=(-10, -110, -110), right_rot=(34, 14, 6), left_rot=(10, -18, -4))
    add_sockets(m, muzzle=(0, 0, -296), eject=(15, 2, -50), sight=(0, 24, 76))
    cyc = dict(bone="bolt", travel=(0, 0, 60), t_back=0.016, t_fwd=0.05)
    anims = _rifle_anims(m, 0.0, (2.0, 0.4, 1.0), 8, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 70),
                         mag_sound="smg", rec=0.12, length=0.2)
    return GunAsset(m, anims, _fp(pos=(0.115, -0.115, -0.2), ads=0.2))


# =================================================================================================
# StG 44
# =================================================================================================
def stg44():
    m = new_gun("stg44")
    body = m["body"]
    st, wd = "steel_dark", "wood"
    body.box(-16, 16, -34, 14, -130, 120, st)                            # stamped receiver
    body.box(0, 16.3, -6, 10, -60, -10, "rubber")
    body.box(-10, 10, 14, 26, -110, -60, st)                             # rear sight base
    body.cyl((0, 22, -300), 22, 340, st)                                 # gas tube above the barrel
    body.box(-14, 14, -26, 6, -300, -130, wd)                            # handguard
    barrel(body, -130, -450, d=17)
    body.box(-8, 8, 10, 30, -440, -428, st)                              # front sight
    body.box(-16, 16, -44, -34, -100, -36, st)
    pistol_grip(body, 40, top_y=-34, length=88, width=28, depth=36, angle=-14, mat="polymer")
    trigger_group(m, body, 4, y_top=-34, guard_depth=26, guard_len=58, guard_mat=st)
    sel = body.bone("selector", pivot=(0, -24, 40))
    sel.cyl((0, -24, 40), 8, 40, "steel", axis="x")
    ch = body.bone("charging_handle", pivot=(-16, 12, -120))
    ch.box(-30, -16, 8, 16, -130, -110, "steel")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16, -4, 8, -58, -12, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 120))
    stock.taper(-16, 16, 120, 400, 6, -6, -34, -116, wd)
    stock.box(-17, 17, -118, -4, 396, 408, st)
    mag = m["gun"].bone("magazine", pivot=(0, -40, -70))
    curved_mag(mag, -36, -96, 46, 240, curve=12, segs=4, width=24, mat="steel_dark", rib_mat="steel", round_d=9,
               round_len=36)
    _stg44_detail(m, body)
    add_arms(m, right_hand=(8, -94, 60), left_hand=(-10, -40, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -456), eject=(16, 2, -40), sight=(0, 30, -86))
    cyc = dict(bone="bolt", travel=(0, 0, 70), t_back=0.018, t_fwd=0.054)
    anims = _rifle_anims(m, 6.0, (2.8, 0.5, 1.2), 10, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 80),
                         selector=(0, 0, 0), rec=0.14, length=0.22)
    return GunAsset(m, anims, _fp(pos=(0.118, -0.125, -0.19), ads=0.32))


# =================================================================================================
# MG 42 (belt fed from the left)
# =================================================================================================
def mg42():
    m = new_gun("mg42")
    body = m["body"]
    st = "steel_dark"
    body.box(-20, 20, -40, 14, -170, 150, st)                            # receiver
    body.box(-18, 18, -18, 16, -560, -170, st)                           # perforated barrel jacket
    for z in range(-550, -180, 30):
        body.box(-18.5, 18.5, -10, 8, z, z + 14, "rubber")
    body.box(18, 22, -16, 12, -440, -300, st)                            # barrel-change hatch
    barrel(body, -560, -620, d=16)
    body.cyl((0, 0, -630), 30, 24, st)                                    # muzzle booster
    body.box(-6, 6, 16, 34, -540, -530, st)                              # front sight
    bipod(body, -470, y=-18, legs_len=230, folded=True)
    pistol_grip(body, 70, top_y=-40, length=90, width=28, depth=38, angle=-18, mat="polymer")
    trigger_group(m, body, 30, y_top=-40, guard_depth=28, guard_len=64, guard_mat=st)
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    stock.taper(-18, 18, 150, 430, 10, -2, -40, -110, "polymer")
    stock.box(-19, 19, -112, 6, 426, 438, st)
    cover = body.bone("cover", pivot=(0, 18, 60))
    cover.box(-20, 20, 14, 30, -160, 60, st)
    cover.box(-8, 8, 30, 38, -20, 30, st)                                # rear sight
    ch = body.bone("charging_handle", pivot=(22, -6, -120))
    ch.box(20, 34, -12, -2, -126, -114, "steel")
    ch.box(30, 38, -16, 2, -128, -112, "steel")
    box = m["gun"].bone("box", pivot=(-20, -40, -60))
    box.box(-60, 10, -170, -40, -130, -10, "olive")                      # 50-round drum / box
    box.box(-58, 8, -172, -170, -128, -12, st)
    belt = m["gun"].bone("belt", pivot=(-26, -4, -100))
    _belt(belt, -24, -2, -120, n=6, dx=-5, dy=-7, case="brass", tip="copper", d=11, length=80)
    add_arms(m, right_hand=(8, -96, 84), left_hand=(-10, -60, 80), right_rot=(34, 14, 6), left_rot=(30, -18, -4))
    add_sockets(m, muzzle=(0, 0, -642), eject=(-14, -40, -30), sight=(0, 38, 20))
    anims = [idle(m), draw(m, 1.0, sound="draw_rifle"),
             _belt_feed(fire_basic(m, "fire", kick=(3.0, 0.7, 1.4), push=12, recover=0.1, length=0.16), (5, 7, 0)),
             _belt_feed(fire_basic(m, "fire_aim", kick=(3.0, 0.7, 1.4), push=12, recover=0.09, length=0.15,
                                   aim=True), (5, 7, 0), sway=2.5),
             belt_reload(m, "reload", False, cover_rot=(75, 0, 0)),
             belt_reload(m, "reload_empty", True, cover_rot=(75, 0, 0), ch_travel=(0, 0, 110)),
             _inspect(m), dry_fire(m)]
    return GunAsset(m, anims, LMG_FP)


# =================================================================================================
# M1918 BAR
# =================================================================================================
def bar():
    m = new_gun("bar")
    body = m["body"]
    st, wd = "steel_parked", "wood"
    body.box(-18, 18, -40, 18, -170, 120, st)                            # long receiver
    body.box(0, 18.3, -6, 12, -70, -10, "rubber")
    body.box(-10, 10, 18, 34, 60, 100, st)                               # rear sight leaf
    body.cyl((0, -22, -420), 16, 380, st)                                # gas cylinder
    body.box(-17, 17, -34, 8, -380, -170, wd)                            # handguard
    barrel(body, -170, -700, d=19)
    flash_hider_a2(body, -700, d=24, length=40)
    body.box(-6, 6, 10, 30, -690, -680, st)
    bipod(body, -640, y=-10, legs_len=260, folded=True)
    body.box(-17, 17, -46, -40, -140, -50, st)
    trigger_group(m, body, 10, y_top=-40, guard_depth=28, guard_len=62, guard_mat=st)
    sel = body.bone("selector", pivot=(-18, -22, 30))
    sel.box(-22, -18, -26, -18, 24, 38, "steel")
    ch = body.bone("charging_handle", pivot=(-18, -4, -150))
    ch.box(-32, -18, -10, 2, -160, -140, "steel")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 18, -4, 10, -68, -12, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 120))
    stock.box(-15, 15, -62, -6, 120, 220, wd, rot=(4, 0, 0), pivot=(0, -6, 120))
    stock.taper(-17, 17, 216, 450, -8, -20, -66, -130, wd)
    stock.box(-18, 18, -134, -18, 446, 458, st)
    mag = m["gun"].bone("magazine", pivot=(0, -46, -96))
    straight_mag(mag, -42, -140, -52, 150, width=30, mat="steel_dark", round_d=12, round_len=60)
    _bar_detail(m, body)
    add_arms(m, right_hand=(8, -100, 60), left_hand=(-10, -40, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -742), eject=(18, 4, -40), sight=(0, 34, 80))
    cyc = dict(bone="bolt", travel=(0, 0, 90), t_back=0.02, t_fwd=0.06)
    anims = _rifle_anims(m, 0.0, (3.6, 0.6, 1.4), 13, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 90),
                         selector=(-40, 0, 0), rec=0.16, length=0.24, draw_len=0.95)
    return GunAsset(m, anims, _fp(pos=(0.125, -0.14, -0.2), ads=0.3))



def _thompson_detail(m, body, st="steel_parked", wd="wood"):
    body.box(-17.3, 17.3, -22, -19, -118, 108, "steel_dark")             # receiver / frame seam
    body.box(-14, 14, 22, 25, -118, 108, st)                             # rounded top
    body.box(-19, -17, -30, -22, 60, 80, "steel")                         # frame latch
    body.box(-19, -17, -30, -24, -100, -88, "steel")                      # magazine catch
    body.box(-21, -17, -14, -6, 40, 52, "steel")                          # safety lever
    body.box(17, 17.6, 0, 8, -60, 30, "rubber")                           # actuator slot
    body.box(-3, 3, 25, 36, 80, 88, st)                                   # fixed peep between the ears
    body.box(-1.4, 1.4, 30, 33, 79.6, 88.4, "rubber")
    body.cyl((0, 0, -128), 26, 16, st)                                    # barrel shoulder at the receiver
    body.box(-5, 5, 10, 16, -372, -356, st)                               # front sight base + blade
    body.box(-1.4, 1.4, 16, 27, -368, -362, st)
    body.cyl((0, 0, -381), 22, 4, "steel_dark")                           # crown
    body.box(-5, 5, -5, 5, -383.5, -383, "rubber")
    for z in range(-312, -160, 24):                                       # finger grooves in the handguard
        body.box(-20.4, 20.4, -36, -24, z, z + 10, "wood_light")
    body.box(-21, 21, -46, -10, -326, -320, st)                           # handguard nose cap
    body.box(-4, 4, -52, -42, -306, -294, "steel")                        # front sling swivel
    stock = m["stock"]
    stock.box(-11, 11, 2, 12, 110, 160, st)                               # upper tang
    stock.box(-11, 11, -40, -32, 110, 150, st)                            # lower tang
    stock.box(-17.4, 17.4, -30, -26, 150, 400, "wood_light")              # grain line
    stock.box(-4, 4, -106, -96, 360, 372, "steel")                        # rear sling swivel
    stock.box(-12, 12, -100, -16, 428, 430, "steel_dark")                 # butt-trap door
    stock.box(-15, 15, -8, -2, 426, 429, "steel")
    m["magazine"].box(-12.4, 12.4, -250, -244, -60, -56, "steel")          # mag spine/base detail
    m["magazine"].box(-12.4, 12.4, -60, -52, -102, -98, "steel")


def _mp40_detail(m, body, st="steel_dark"):
    body.box(-15.4, -14.6, -3, 4, -120, -10, "rubber")                    # cocking slot (left)
    body.box(-15.4, -14.6, 4, 11, -16, -8, "rubber")                      # safety notch
    for y in (8, -8):                                                     # receiver flutes
        body.box(14.6, 15.4, y - 1.5, y + 1.5, 0, 100, "rubber")
        body.box(-15.4, -14.6, y - 1.5, y + 1.5, 10, 100, "rubber")
    body.cyl((0, 0, 112), 32, 6, st, sides=12)                            # end cap
    body.box(-6, 6, -6, 6, 115, 120, "steel")
    body.box(-8, 8, 14, 20, 60, 92, st)                                   # rear sight base + flip leaves
    body.box(-6, 6, 20, 30, 70, 74, st)
    body.box(-6, 6, 20, 23, 74, 90, st)
    body.box(-1.2, 1.2, 25, 29, 69.6, 74.4, "rubber")
    body.box(-9, -7, 10, 30, -292, -278, st)                              # front sight hood
    body.box(7, 9, 10, 30, -292, -278, st)
    body.box(-9, 9, 28, 30, -292, -278, st)
    body.box(-1.2, 1.2, 10, 26, -286, -284, "steel")
    body.cyl((0, 0, -154), 26, 10, st)                                    # barrel nut
    body.cyl((0, 0, -294), 18, 8, "steel")                                # muzzle cap
    body.box(-6, 6, -26, -16, -300, -292, st)                             # barrel rest loop
    for z in range(-146, -36, 14):                                        # bakelite ribs
        body.box(-15.4, 15.4, -52, -22, z, z + 5, "rubber")
    for z in (-124, -114, -104):                                          # mag housing ribs
        body.box(-13.4, 13.4, -58, -22, z, z + 4, "rubber")
    body.box(-16, -13, -34, -26, -104, -96, "steel")                      # mag release
    body.box(-17, -15, -8, 8, 88, 98, "steel")                            # sling bar
    body.box(-14, 14, -30, -14, 96, 120, st)                              # stock hinge block
    stock = m["stock"]
    stock.box(-14, 14, -66, -56, 110, 124, st)
    stock.box(-16, -12, -68, -62, 100, 108, "steel")                      # lock button
    stock.box(-18, 18, -86, -56, -136, -132, "steel")                     # shoulder pad
    stock.box(-14, 14, -78, -74, -120, 110, "steel_dark")                 # cross brace line


def _stg44_detail(m, body, st="steel_dark", wd="wood"):
    for z in (-120, -20, 60):                                             # stamped ribs
        body.box(-16.4, 16.4, -30, 10, z, z + 8, "steel")
    body.box(16, 18, -14, -8, -64, -6, "steel")                           # hinged port cover (open)
    body.box(-6, 6, 26, 30, -104, -64, st)                                # tangent leaf + slider
    body.box(-8, 8, 26, 32, -90, -82, "steel")
    body.box(-1.2, 1.2, 28, 31, -104.4, -100, "rubber")
    body.cyl((0, 22, -472), 26, 10, st)                                   # gas tube nut
    body.box(-8, 8, 8, 16, -444, -426, st)                                # gas block
    body.box(-10, -8, 10, 36, -444, -424, st)                             # hooded front sight
    body.box(8, 10, 10, 36, -444, -424, st)
    body.box(-10, 10, 34, 36, -444, -424, st)
    body.box(-1.2, 1.2, 10, 30, -436, -434, "steel")
    body.cyl((0, 0, -458), 20, 12, "steel")                               # thread protector
    for z in range(-290, -140, 30):                                       # handguard grooves
        body.box(-14.4, 14.4, -18, -6, z, z + 12, "wood_light")
    body.box(-15, 15, -48, -34, -20, 90, st)                              # trigger housing sheet
    body.box(-14, 14, -60, -44, -100, -40, st)                            # long magazine well
    body.box(14, 18, -54, -46, -44, -36, "steel")                         # mag release
    body.box(-19, -16, -30, -22, 60, 72, "steel")                         # safety lever
    body.box(-17, -15, -8, 8, -126, -118, "steel")                        # front sling loop
    stock = m["stock"]
    stock.box(-12, 12, 4, 12, 120, 150, st)                               # receiver tang
    stock.box(-4, 4, -104, -94, 330, 342, "steel")                        # rear sling loop
    stock.box(-12, 12, -100, -16, 408, 410, "steel")                      # butt-plate trap
    stock.box(-16.4, 16.4, -40, -36, 150, 390, "wood_light")


def _bar_detail(m, body, st="steel_parked", wd="wood"):
    body.box(-18.4, 18.4, -10, -6, -160, 110, "rubber")                   # receiver lightening groove
    body.box(-6, 6, 34, 40, 76, 84, "steel")                              # rear aperture slider
    body.box(-1.2, 1.2, 36, 39, 75.6, 84.4, "rubber")
    body.box(-10, -8, 18, 40, 94, 100, st)                                # rear sight ears
    body.box(8, 10, 18, 40, 94, 100, st)
    body.box(18, 19.5, -12, -6, -70, -10, "steel")                        # ejection port cover (open)
    body.box(-5, 5, -46, -40, -48, -40, "steel")                          # magazine release
    body.cyl((0, -22, -612), 22, 12, st)                                  # gas cylinder nut
    body.box(-10, 10, -32, -12, -630, -616, st)                           # gas regulator
    body.box(-14, 14, -34, 6, -560, -550, st)                             # barrel / gas band
    body.box(-8, -6, 10, 34, -694, -680, st)                              # front sight wings
    body.box(6, 8, 10, 34, -694, -680, st)
    for z in range(-370, -180, 26):                                       # handguard ridges
        body.box(-17.4, 17.4, -24, -6, z, z + 10, "wood_light")
    body.box(-4, 4, -38, -28, -540, -530, "steel")                        # front sling swivel
    body.box(-15, 15, -46, -40, -50, 70, st)                              # trigger housing
    body.box(-22, -18, -8, 0, 70, 90, "steel")                            # rate selector detent
    stock = m["stock"]
    stock.box(-10, 10, -8, -2, 116, 180, st)                              # upper tang
    stock.box(-10, 10, -66, -58, 116, 170, st)                            # lower tang
    stock.box(-16, 16, -60, -40, 458, 470, "steel")                       # hinged shoulder rest
    stock.box(-4, 4, -120, -110, 380, 392, "steel")                       # rear sling swivel
    stock.box(-17.4, 17.4, -60, -56, 230, 440, "wood_light")


GUNS = {"kar98k": kar98k, "garand": garand, "enfield": enfield, "thompson": thompson, "mp40": mp40,
        "stg44": stg44, "mg42": mg42, "bar": bar}
