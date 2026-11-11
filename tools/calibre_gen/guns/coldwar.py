"""Cold War pack: M60, M16A1, IMI Galil ARM, H&K G3A3, Sten Mk II, Colt Python, Skorpion vz. 61, KS-23."""
import math

import numpy as np

from ..core import Anim, HOLD
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden)
from ..templates import rifle_reload, revolver_reload, belt_reload, pump_cycle, tube_reload
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, flash_hider_a2, bipod,
                     ar_front_sight)
from .lmgs import _belt, _belt_feed, LMG_FP
from .modern import _rifle_anims, _inspect, _fp


# =================================================================================================
# M60 (belt fed from a 100-round box on the left)
# =================================================================================================
def m60():
    m = new_gun("m60")
    body = m["body"]
    st = "steel_parked"
    body.box(-20, 20, -42, 16, -150, 150, st)                                 # stamped receiver
    body.box(-20.4, 20.4, -30, 6, -120, -60, "steel_dark")                    # feed tray side plates
    body.box(-15, 15, -36, 8, -380, -150, "polymer")                           # A3-ish forend
    for z in range(-370, -160, 26):
        body.box(-15.4, 15.4, -28, 0, z, z + 12, "rubber")
    body.cyl((0, -18, -420), 18, 200, st)                                       # gas cylinder
    barrel(body, -150, -700, d=19, mat="steel_dark")
    body.box(-6, 6, -24, 10, -560, -540, st)                                    # barrel carry handle mount
    body.box(-5, 5, 10, 46, -560, -548, "steel_dark")
    body.box(-5, 5, 42, 50, -560, -420, "steel_dark")
    body.box(-5, 5, 10, 46, -432, -420, "steel_dark")
    flash_hider_a2(body, -700, d=24, length=50)
    body.box(-3, 3, 12, 34, -690, -684, st)                                     # front sight blade
    bipod(body, -640, y=-10, legs_len=250, folded=True)
    pistol_grip(body, 60, top_y=-42, length=92, width=30, depth=38, angle=-16, mat="polymer")
    trigger_group(m, body, 20, y_top=-42, guard_depth=28, guard_len=66, guard_mat=st)
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    stock.box(-17, 17, -46, 6, 150, 200, "polymer")
    stock.taper(-18, 18, 200, 450, 4, -6, -46, -110, "polymer")
    stock.box(-19, 19, -114, 2, 446, 460, st)
    stock.box(-8, 8, -70, -54, 300, 320, st)                                    # shoulder rest hinge
    cover = body.bone("cover", pivot=(0, 16, 120))
    cover.box(-20, 20, 16, 30, -140, 120, st)
    cover.box(-9, 9, 30, 46, 70, 110, st)                                       # leaf rear sight
    ch = body.bone("charging_handle", pivot=(20, -14, -100))
    ch.box(20, 38, -20, -8, -106, -94, "steel")
    ch.box(34, 42, -24, -4, -108, -92, "steel")
    box = m["gun"].bone("box", pivot=(-20, -42, -80))
    box.box(-70, 6, -190, -42, -150, -20, "olive")                              # 100-round can / bag
    box.box(-68, 4, -192, -190, -148, -22, "steel_dark")
    belt = m["gun"].bone("belt", pivot=(-26, -6, -100))
    _belt(belt, -24, -4, -120, n=7, dx=-5, dy=-7, case="brass", tip="copper", d=10, length=70)
    add_arms(m, right_hand=(8, -98, 74), left_hand=(-10, -50, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -750), under=(0, -36, -300), eject=(14, -40, -40), sight=(0, 46, 90))
    anims = [idle(m), draw(m, 1.0, sound="draw_rifle"),
             _belt_feed(fire_basic(m, "fire", kick=(3.2, 0.7, 1.4), push=12, recover=0.12, length=0.2), (5, 7, 0)),
             _belt_feed(fire_basic(m, "fire_aim", kick=(3.2, 0.7, 1.4), push=12, recover=0.1, length=0.18,
                                   aim=True), (5, 7, 0), sway=2.5),
             belt_reload(m, "reload", False, cover_rot=(75, 0, 0)),
             belt_reload(m, "reload_empty", True, cover_rot=(75, 0, 0), ch_travel=(0, 0, 100)),
             _inspect(m), dry_fire(m)]
    return GunAsset(m, anims, LMG_FP)


def _m16a1_detail(m, body, al="alloy"):
    body.box(13.2, 15.2, -2, 15, -66, -6, al, rot=(0, 0, -100), pivot=(15, -2, -36))   # dust cover, open
    for z in (-100, 90):                                                  # takedown + pivot pins
        body.box(-13, -12, -26, -18, z - 4, z + 4, "steel")
        body.box(12, 13, -26, -18, z - 4, z + 4, "steel")
    body.box(-6, 6, -36, -28, 96, 104, al)                                # rear lug
    body.box(12, 15, -32, -24, -40, -30, "steel_dark")                    # mag release
    body.box(-5, 5, -24, -12, -450, -430, "steel_dark")                   # bayonet lug
    body.box(-2, 2, -34, -24, -446, -436, "steel")                        # front sling swivel
    body.box(-17.3, 17.3, -5, -3, -388, -132, "rubber")                   # handguard halves seam
    for z in range(-380, -150, 20):                                       # top cooling holes
        body.box(-4, 4, 12.6, 13.4, z, z + 6, "rubber")
    body.cyl((0, -4, -392), 30, 6, "steel_dark")                          # handguard cap
    body.cyl((14, 58, 70), 8, 6, "steel_dark", axis="x")                  # windage drum
    body.box(-6.4, 6.4, 26, 44, -80, 40, "rubber")                        # carry-handle opening
    body.box(-14, -13, -10, 6, 30, 50, al)                                # forward-assist housing fins
    stock = m["stock"]
    stock.box(-10, 10, -80, -10, 370, 371, "steel_dark")                  # butt trap door
    stock.box(-3, 3, -86, -74, 300, 312, "steel")                        # rear sling swivel
    stock.box(-11.5, 11.5, -20, -12, 118, 126, "steel")                   # stock screw plate
    m["magazine"].box(-12, 12, -162, -158, -100, -32, "steel_dark")        # mag floorplate lip


# =================================================================================================
# M16A1 (carry handle, triangle handguard, 20-round mag, fixed A1 stock)
# =================================================================================================
def m16a1():
    m = new_gun("m16a1")
    body = m["body"]
    al = "alloy"
    body.box(-12, 12, -40, -6, -112, 98, al)                                   # lower
    body.box(-14, 14, -46, -6, -100, -34, al)
    pistol_grip(body, 34, top_y=-38, length=90, width=26, depth=34, angle=-20, mat="polymer")
    trigger_group(m, body, 6, y_top=-40, guard_depth=26, guard_len=64, guard_mat=al)
    bc = body.bone("bolt_catch", pivot=(-12, -14, -18))
    bc.box(-15, -12, -22, -10, -26, -10, "steel_dark")
    sel = body.bone("selector", pivot=(-12, -24, 42))
    sel.box(-15.5, -12, -27, -21, 34, 50, "steel_dark")
    body.box(-13, 13, -6, 20, -130, 102, al)                                   # upper
    body.box(13, 15, -2, 14, -64, -8, "rubber")
    fa = body.bone("forward_assist", pivot=(14, 10, 40))
    fa.cyl((18, 10, 40), 9, 14, al, axis="x")                                   # teardrop assist
    # carry handle with the A1 rear sight
    body.box(-6, 6, 20, 52, -110, -96, al)
    body.box(-6, 6, 20, 52, 60, 96, al)
    body.box(-8, 8, 46, 56, -110, 96, al)
    body.box(-6, 6, 56, 66, 62, 80, al)
    body.box(-4, 4, 66, 72, 66, 76, "steel_dark")
    # slim round handguard (A1 triangle), long 20" barrel
    body.cyl((0, -4, -260), 34, 260, "polymer", sides=12)
    for z in range(-380, -150, 20):
        body.box(-17.4, 17.4, -14, 4, z, z + 6, "rubber")
    body.cyl((0, -4, -126), 34, 12, "steel_dark")                              # delta ring
    barrel(body, -390, -560, d=14)
    ar_front_sight(body, -440, base_y=6, h=50)
    body.cyl((0, 0, -584), 16, 48, "steel_dark")                                # three-prong flash hider
    for ang in (0, 120, 240):
        body.box(-1.6, 1.6, 5, 9, -606, -570, "rubber", rot=(0, 0, ang), pivot=(0, 0, -584))
    stock = m["gun"].bone("stock", pivot=(0, 0, 102))
    stock.box(-11, 11, -32, -4, 98, 140, "polymer")
    stock.taper(-17, 17, 140, 360, 4, 10, -36, -90, "polymer")
    stock.box(-18, 18, -94, 12, 356, 370, "rubber")
    ch = body.bone("charging_handle", pivot=(0, 18, 104))
    ch.box(-5, 5, 14, 20, -10, 104, "steel_dark")
    ch.box(-16, 16, 14, 20, 100, 110, "steel_dark")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(1, 12.8, -1, 13, -62, -10, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -46, -66))
    straight_mag(mag, -40, -100, -32, 120, width=23, mat="alloy", base_mat="steel_dark", round_d=8, round_len=56)
    _m16a1_detail(m, body)
    add_arms(m, right_hand=(8, -92, 54), left_hand=(-10, -44, -280), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -610), under=(0, -22, -280), eject=(15, 6, -38), sight=(0, 72, 70))
    cyc = dict(bone="bolt", travel=(0, 0, 78), t_back=0.018, t_fwd=0.052)
    anims = _rifle_anims(m, 0.0, (2.4, 0.4, 1.0), 11, "ar", cyc, bolt="bolt", bolt_travel=(0, 0, 78), lock=True,
                         selector=(-90, 0, 0))
    anims.insert(1, idle(m, "idle_empty", locked={"bolt": (0, 0, 78)}))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.135, -0.2), ads=0.11))


# =================================================================================================
# IMI Galil ARM (AK-derived, folding stock, bipod + carry handle)
# =================================================================================================
def galil():
    m = new_gun("galil")
    body = m["body"]
    st = "steel_dark"
    body.box(-15, 15, -32, 12, -140, 150, st)                                  # milled receiver
    body.box(-13, 13, 12, 18, -100, 150, st)                                   # dust cover
    body.box(0, 15.3, -4, 10, -60, 20, "rubber")
    body.box(-16, 16, -30, 10, -360, -140, "wood")                             # wooden handguard
    for z in range(-350, -160, 24):
        body.box(-16.4, 16.4, -22, 0, z, z + 10, "wood_light")
    body.cyl((0, 16, -280), 16, 200, st)                                        # gas tube
    barrel(body, -360, -500, d=15)
    flash_hider_a2(body, -500, d=20, length=40)
    body.box(-6, 6, 16, 42, -470, -456, st)                                     # front sight post (tall)
    body.box(-8, 8, 18, 40, 130, 146, st)                                       # flip rear sight
    bipod(body, -340, y=-30, legs_len=210, folded=True)
    body.box(-6, 6, 24, 40, -200, -100, st)                                     # carry handle
    body.box(-6, 6, 12, 26, -200, -190, st)
    pistol_grip(body, 40, top_y=-32, length=86, width=26, depth=32, angle=-14, mat="polymer")
    trigger_group(m, body, 6, y_top=-32, guard_depth=28, guard_len=70, guard_mat=st)
    sel = body.bone("selector", pivot=(15, 0, 60))
    sel.box(15, 18, -10, 6, -10, 70, "steel")                                   # AK lever
    sel.box(-18, -15, -24, -16, 30, 44, "steel")                                # Galil thumb selector
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))                           # tubular folding stock (open)
    stock.cyl((0, -2, 260), 14, 220, "steel")
    stock.cyl((0, -50, 260), 14, 220, "steel")
    stock.box(-16, 16, -60, 8, 360, 380, "steel_dark")
    stock.box(-18, 18, -66, 12, 378, 390, "rubber")
    bolt = body.bone("bolt", pivot=(16, 4, -10))
    bolt.box(1, 14, -4, 10, -56, 20, "steel_light")
    bolt.box(14, 22, 10, 18, 4, 14, "steel_light")
    bolt.box(18, 26, 16, 28, 2, 16, "steel_light")                             # upturned handle
    mag = m["gun"].bone("magazine", pivot=(0, -32, -90))
    curved_mag(mag, -30, -110, 62, 200, curve=18, segs=4, width=24, mat="steel_dark", rib_mat="steel", round_d=8,
               round_len=50)
    add_arms(m, right_hand=(8, -88, 46), left_hand=(-10, -34, -260), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -540), under=(0, -30, -260), eject=(16, 6, -20), sight=(0, 40, 138))
    cyc = dict(bone="bolt", travel=(0, 0, 90), t_back=0.018, t_fwd=0.054)
    anims = _rifle_anims(m, 6.0, (2.4, 0.5, 1.1), 10, "ak", cyc, ch="bolt", ch_travel=(0, 0, 90), selector=(0, 0, 0),
                         rock=12)
    fm = next(a for a in anims if a.name == "firemode")
    fm.key("selector", 0.2, rot=(0, 0, 0))
    fm.key("selector", 0.26, rot=(-26, 0, 0), e="outquad")
    fm.key("selector", 0.55, rot=(-26, 0, 0))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.128, -0.2), ads=0.1))


# =================================================================================================
# H&K G3A3 (roller delayed, slap reload)
# =================================================================================================
def g3a3():
    m = new_gun("g3a3")
    body = m["body"]
    st = "steel_dark"
    body.box(-16, 16, -22, 18, -260, 80, st)                                    # stamped receiver
    body.box(-13, 13, 18, 22, -260, 70, st)
    for z in (-180, -80, 0):
        body.box(-16.4, 16.4, -18, 14, z, z + 20, "steel")
    body.box(0, 16.3, -4, 12, -80, -30, "rubber")
    body.cyl((0, 10, -340), 24, 170, st)                                        # cocking tube
    body.cyl((0, -4, -380), 18, 260, "steel")
    body.box(-19, 19, -36, 4, -460, -260, "polymer")                            # slim handguard
    for z in range(-450, -270, 20):
        body.box(-19.4, 19.4, -28, -6, z, z + 10, "rubber")
    barrel(body, -460, -580, d=17)
    flash_hider_a2(body, -580, d=22, length=40)
    # hooded front sight + drum rear
    body.box(-11, 11, 20, 24, -440, -420, st)
    body.box(-11, -8, 24, 44, -438, -422, st)
    body.box(8, 11, 24, 44, -438, -422, st)
    body.box(-1.2, 1.2, 24, 36, -431, -429, st)
    body.box(-12, 12, 22, 28, 30, 60, st)
    body.cyl((0, 36, 46), 24, 16, st, axis="x", sides=12)
    body.box(-16, 16, 22, 26, -160, -130, st)                                   # claw mount bumps
    body.box(-14, 14, -42, -22, -70, 70, "polymer")                             # trigger housing
    pistol_grip(body, 36, top_y=-40, length=88, width=30, depth=38, angle=-14, mat="polymer")
    trigger_group(m, body, 0, y_top=-42, guard_depth=28, guard_len=60, guard_mat="polymer")
    sel = body.bone("selector", pivot=(-15, -32, 46))
    sel.box(-18, -15, -36, -28, 40, 54, "steel")
    body.box(-15, 15, -42, -22, -126, -70, st)                                  # mag well
    stock = m["gun"].bone("stock", pivot=(0, 0, 80))
    stock.box(-14, 14, -24, 16, 80, 120, "polymer")
    stock.taper(-18, 18, 120, 360, 14, 14, -30, -90, "polymer")
    stock.box(-20, 20, -96, 18, 356, 370, "rubber")
    ch = body.bone("charging_handle", pivot=(-14, 10, -400))
    ch.box(-34, -12, 6, 14, -408, -394, "steel")
    ch.box(-38, -30, 4, 16, -410, -392, "polymer")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 15.5, -2, 10, -78, -32, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -42, -110))
    curved_mag(mag, -38, -122, 52, 160, curve=8, segs=3, width=24, mat="steel_dark", rib_mat="steel", round_d=10,
               round_len=60)
    add_arms(m, right_hand=(8, -86, 48), left_hand=(-10, -44, -360), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, -4, -620), optic=(0, 26, -60), under=(0, -36, -360), eject=(16, 4, -55),
                sight=(0, 44, 46))
    cyc = dict(bone="bolt", travel=(0, 0, 56), t_back=0.016, t_fwd=0.05)
    kk = dict(kick=(3.6, 0.6, 1.4), push=14, cycle=cyc)
    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", recover=0.17, length=0.26, **kk),
             fire_basic(m, "fire_aim", recover=0.15, length=0.24, aim=True, **kk),
             rifle_reload(m, "reload", 6.0, empty=False, style="hk", bolt="bolt", bolt_travel=(0, 0, 56),
                          ch_travel=(0, 0, 60)),
             rifle_reload(m, "reload_empty", 6.0, empty=True, style="hk", bolt="bolt", bolt_travel=(0, 0, 56),
                          ch="charging_handle", ch_travel=(0, 0, 60), bolt_hold_open=False, ch_hand="left"),
             firemode(m, selector_rot=(-50, 0, 0)), _inspect(m), dry_fire(m)]
    return GunAsset(m, anims, _fp(pos=(0.118, -0.128, -0.2), ads=0.1))


# =================================================================================================
# Sten Mk II (side-mounted magazine)
# =================================================================================================
def _side_mag(anims, bone="magazine"):
    """rifle_reload drops a magazine downwards; the Sten's goes out to the left. Turn every magazine key -90 deg
    about the bore so 'down' becomes 'left'."""
    for a in anims:
        for ch in ("pos", "rot"):
            tr = a.tracks.get((bone, ch))
            if not tr:
                continue
            tr.keys = [(t, v if v is HOLD or not isinstance(v, np.ndarray) else np.array([v[1], -v[0], v[2]]), e)
                       for t, v, e in tr.keys]
    return anims


def sten():
    m = new_gun("sten")
    body = m["body"]
    st = "steel_parked"
    body.cyl((0, 0, -40), 34, 300, st, sides=12)                               # tubular receiver
    body.box(14, 17.6, -2, 6, -120, 60, "rubber")                              # cocking slot (right)
    body.box(14, 17.6, 6, 14, 54, 66, "rubber")                                # safety notch
    body.box(0, 17.4, -14, -4, -120, -70, "rubber")                            # ejection port
    body.cyl((0, 0, -230), 26, 80, st, sides=12)                               # barrel sleeve
    for z in (-256, -236, -216):
        body.box(-13.4, 13.4, -4, 4, z, z + 10, "rubber")
    barrel(body, -270, -300, d=14)
    body.box(-2, 2, 17, 30, -260, -254, st)                                    # front sight
    body.box(-6, 6, 17, 28, 80, 90, st)                                        # rear peep
    # mag housing on the left (rotates down as a dust cover in real life)
    body.box(-50, -16, -14, 14, -136, -90, st)
    body.box(-14, 14, -44, -16, -20, 50, st)                                   # trigger housing
    trigger_group(m, body, 20, y_top=-44, guard_depth=24, guard_len=56, guard_mat=st)
    sel = body.bone("selector", pivot=(14, -30, 40))
    sel.box(14, 18, -34, -26, 34, 46, "steel")                                  # push-through fire selector
    # skeleton T stock: one tube + butt plate, used as the grip
    stock = m["gun"].bone("stock", pivot=(0, 0, 110))
    stock.cyl((0, -14, 200), 12, 180, st)
    stock.box(-5, 5, -70, -14, 110, 124, st, rot=(30, 0, 0), pivot=(0, -14, 117))
    stock.box(-18, 18, -100, 10, 286, 296, st)
    stock.box(-6, 6, -100, -14, 280, 290, st)
    bolt = body.bone("bolt", pivot=(16, 2, -40))
    bolt.box(1, 16, -6, 6, -110, -60, "steel_light")
    bolt.box(16, 30, -2, 6, -50, -40, "steel")
    bolt.box(28, 34, -4, 8, -52, -38, "steel")
    mag = m["gun"].bone("magazine", pivot=(-50, 0, -113))
    mag.box(-210, -50, -12, 12, -130, -96, "steel_dark")                        # 32 rd stick sticking out left
    mag.box(-216, -210, -14, 14, -132, -94, "steel")
    for x in range(-190, -60, 34):
        mag.box(x, x + 14, -12.4, 12.4, -120, -106, "steel")
    mag.round_((-48, 0, -110), 26, 8)
    add_arms(m, right_hand=(8, -64, 44), left_hand=(-12, -16, -210), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -304), eject=(18, -8, -90), sight=(0, 28, 86))
    cyc = dict(bone="bolt", travel=(0, 0, 80), t_back=0.018, t_fwd=0.05)
    anims = _rifle_anims(m, 0.0, (1.6, 0.4, 0.9), 7, "smg", cyc, ch="bolt", ch_travel=(0, 0, 80), mag_sound="smg",
                         selector=(0, 0, 0), rec=0.1, length=0.18, tilt=(10, 10, 10), tilt_pos=(10, 16, 24))
    fm = next(a for a in anims if a.name == "firemode")
    fm.key("selector", 0.2, pos=(0, 0, 0))
    fm.key("selector", 0.26, pos=(-8, 0, 0), e="outquad")
    fm.key("selector", 0.55, pos=(-8, 0, 0))
    _side_mag(anims)
    return GunAsset(m, anims, _fp(pos=(0.11, -0.115, -0.21), ads=0.14))


# =================================================================================================
# Skorpion vz. 61 (machine pistol, wire stock folded over the top)
# =================================================================================================
def skorpion():
    m = new_gun("skorpion")
    body = m["body"]
    st = "steel_dark"
    body.box(-12, 12, -24, 14, -150, 60, st)                                    # receiver
    body.box(-12.3, 12.3, 0, 12, -120, 30, "steel")                             # bolt-way slots both sides
    barrel(body, -150, -200, d=12)
    body.cyl((0, 0, -204), 15, 8, st)
    body.box(-1.5, 1.5, 14, 26, -140, -134, st)                                 # front post with ears
    body.box(-6, -4, 14, 24, -142, -132, st)
    body.box(4, 6, 14, 24, -142, -132, st)
    body.box(-6, 6, 14, 22, 30, 44, st)                                         # flip rear
    body.box(-12, 12, -40, -24, -90, 50, st)
    # wooden grip (offset rearward), guard
    pistol_grip(body, 30, top_y=-40, length=76, width=24, depth=30, angle=-8, mat="wood_red")
    trigger_group(m, body, -10, y_top=-40, guard_depth=24, guard_len=60, guard_mat=st)
    sel = body.bone("selector", pivot=(-12, -10, 34))
    sel.box(-16, -12, -14, -6, 28, 40, "steel")
    stock = m["gun"].bone("stock", pivot=(0, 14, 50))                           # wire stock folded forward on top
    for sx in (-9, 9):
        stock.box(sx - 2, sx + 2, 14, 18, -130, 56, "steel")
    stock.box(-11, 11, 14, 18, -140, -130, "steel")
    stock.box(-11, 11, 18, 22, -140, -128, "steel")
    bolt = body.bone("bolt", pivot=(0, 6, -60))                                  # cocking knobs both sides
    bolt.box(-12, 12, 2, 10, -80, -40, "steel_light")
    bolt.cyl((16, 6, -50), 10, 10, "steel_light", axis="x")
    bolt.cyl((-16, 6, -50), 10, 10, "steel_light", axis="x")
    mag = m["gun"].bone("magazine", pivot=(0, -40, -70))
    curved_mag(mag, -36, -84, 24, 140, curve=24, segs=4, width=18, mat="steel_dark", rib_mat="steel", round_d=7,
               round_len=18)
    add_arms(m, right_hand=(6, -78, 36), left_hand=(-12, -100, -60), right_rot=(34, 16, 6), left_rot=(30, -24, -4))
    add_sockets(m, muzzle=(0, 0, -208), eject=None, sight=(0, 24, 38))
    cyc = dict(bone="bolt", travel=(0, 0, 40), t_back=0.01, t_fwd=0.03)
    anims = _rifle_anims(m, 4.0, (1.4, 0.4, 0.8), 6, "smg", cyc, ch="bolt", ch_travel=(0, 0, 44), mag_sound="smg",
                         selector=(0, 0, 60), rec=0.09, length=0.15, draw_len=0.55)
    return GunAsset(m, anims, _fp(pos=(0.11, -0.1, -0.24), rot=(0, 5, 0), ads=0.24))


# =================================================================================================
# KS-23 (23 mm pump)
# =================================================================================================
def _big_shells(m, port=(0, -36, -30)):
    sl = m["gun"].bone("shell_load", pivot=port)
    sl.shell12((port[0], port[1] - 4, port[2] + 12), length=80, d=24)
    se = m["gun"].bone("shell_eject", pivot=(16, 6, -40))
    se.shell12((16, 6, -40), length=80, d=24)


def ks23():
    m = new_gun("ks23")
    body = m["body"]
    st = "steel_dark"
    body.box(-20, 20, -36, 22, -120, 100, st)                                  # receiver
    body.box(0, 20.3, -8, 16, -90, -10, "rubber")
    body.box(-14, 14, -38, -36, -110, -20, "rubber")                           # loading port
    barrel(body, -120, -620, d=30, y=4)                                         # 23 mm bore, rifled
    body.cyl((0, 4, -626), 34, 12, st)
    body.cyl((0, -26, -300), 26, 360, st)                                       # 3-round tube
    body.box(-4, 4, 20, 32, -610, -600, st)
    body.box(-8, 8, 22, 34, 60, 80, st)
    body.box(-16, 16, -32, 22, 100, 130, "wood")                               # wrist
    body.box(-16, 16, -84, -32, 100, 150, "wood", rot=(-26, 0, 0), pivot=(0, -32, 120))
    body.taper(-17, 17, 130, 420, 18, 10, -40, -110, "wood")                   # straight stock
    body.box(-18, 18, -114, 14, 416, 430, "rubber")
    trigger_group(m, body, 40, y_top=-36, guard_depth=28, guard_len=66, guard_mat=st)
    pump = m["gun"].bone("pump", pivot=(0, -26, -280))
    pump.box(-26, 26, -54, -6, -400, -220, "wood")
    for z in range(-390, -230, 16):
        pump.box(-26.4, 26.4, -46, -14, z, z + 6, "wood_light")
    pump.box(-7, -4, -16, -8, -220, -60, st)
    pump.box(4, 7, -16, -8, -220, -60, st)
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 19.8, -6, 14, -86, -16, "steel_light")
    _big_shells(m)
    add_arms(m, right_hand=(8, -88, 128), left_hand=(-10, -46, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -632), eject=(20, 4, -50), sight=(0, 34, 70))
    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(11, 1.0, 2.4), push=30, recover=0.4, length=0.5),
             fire_basic(m, "fire_aim", kick=(11, 1.0, 2.4), push=30, recover=0.36, length=0.46, aim=True),
             pump_cycle(m, "cycle", travel=(0, 0, 100), length=0.68),
             pump_cycle(m, "cycle_aim", travel=(0, 0, 100), length=0.68, aim=True),
             *tube_reload(m), _inspect(m), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, _fp(pos=(0.12, -0.13, -0.2), rot=(0, 3.5, 0), ads=0.13))


GUNS = {"m60": m60, "m16a1": m16a1, "galil": galil, "g3a3": g3a3, "sten": sten, "skorpion": skorpion, "ks23": ks23}
