"""M4A1, HK416, AKM, Steyr AUG A3."""
import numpy as np

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden, along)
from ..templates import rifle_reload, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, flash_hider_a2, ar_front_sight,
                     buis_rear, ar_stock, picatinny_handguard, muzzle_brake)

RIFLE_FP = {"hip": {"pos": [0.118, -0.128, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.085}}


def _ar(name, hk=False):
    MAG_A = 4.0
    m = new_gun(name)
    body = m["body"]
    al = "alloy"
    # lower receiver
    body.box(-12, 12, -40, -6, -112, 98, al)
    body.box(-14, 14, -46, -6, -100, -34, al)                               # mag well flare
    body.box(-14.5, 14.5, -48, -44, -102, -32, al)
    body.box(-10, 10, -34, -6, 98, 112, al)                                 # receiver extension housing
    pistol_grip(body, 34, top_y=-38, length=92, width=27, depth=34, angle=-20, mat="polymer")
    trigger_group(m, body, 6, y_top=-40, guard_depth=26, guard_len=64, guard_mat=al)
    body.box(12, 15, -32, -24, -40, -30, "steel_dark")                     # mag release (right)
    bc = body.bone("bolt_catch", pivot=(-12, -14, -18))
    bc.box(-15, -12, -22, -10, -26, -10, "steel_dark")
    sel = body.bone("selector", pivot=(-12, -24, 42))
    sel.box(-15.5, -12, -27, -21, 34, 50, "steel_dark")
    sel.box(-16, -14, -28, -20, 48, 52, "steel_dark")
    # upper receiver (flat top)
    body.box(-13, 13, -6, 22, -130, 102, al)
    body.box(-9, 9, 22, 26, -130, 102, al)
    body.rail(-128, 100, 26, mat=al)
    body.box(13, 15, -2, 14, -64, -8, "rubber")                             # ejection port
    dc = body.bone("dust_cover", pivot=(15, -2, -36))
    dc.box(13.2, 15.2, -2, 15, -66, -6, al)
    fa = body.bone("forward_assist", pivot=(14, 10, 40))
    fa.cyl((19, 10, 40), 11, 16, al, axis="x")
    fa.cyl((28, 10, 40), 14, 4, al, axis="x")
    body.box(13, 18, 4, 16, 6, 30, al)                                      # brass deflector
    # barrel nut, handguard, barrel, sights
    if hk:
        body.box(-21, 21, -34, 22, -385, -130, al)                           # HK quad rail
        for side in ("left", "right"):
            body.rail(-380, -136, -6, x=-21 if side == "left" else 21, mat=al, side=side, width=20)
        body.rail(-380, -136, 22, mat=al)
        body.rail(-380, -136, -34, mat=al, side="bottom")
        barrel(body, -385, -455, d=17)
        body.box(-10, 10, -12, 12, -400, -385, "steel_dark")                 # piston gas block
        muzzle_brake(body, -455, d=22, length=50, ports=3, mat="steel_dark")
        stock = m["gun"].bone("stock", pivot=(0, 0, 102))
        stock.cyl((0, -4, 212), 30, 220, al)
        stock.taper(-22, 22, 230, 330, 14, 14, -58, -78, "polymer")           # HK slim stock
        stock.box(-20, 20, -24, 10, 200, 232, "polymer")
        stock.box(-23, 23, -86, 18, 326, 340, "rubber")
        stock.box(-12, 12, -50, -24, 260, 300, "rubber")
    else:
        picatinny_handguard(body, -320, -132, y_top=20, y_bot=-28, half_w=20)
        body.cyl((0, 0, -126), 32, 12, "steel_dark")                         # delta ring
        barrel(body, -320, -430, d=15)
        ar_front_sight(body, -338, base_y=8, h=46)
        flash_hider_a2(body, -430, d=20, length=52)
        stock = m["gun"].bone("stock", pivot=(0, 0, 102))
        ar_stock(stock, 102)
    # rear BUIS
    buis_rear(body, 78, 29)
    # charging handle + bolt carrier
    ch = body.bone("charging_handle", pivot=(0, 18, 104))
    ch.box(-6, 6, 14, 22, -10, 104, "steel_dark")
    ch.box(-20, 20, 14, 22, 102, 112, "steel_dark")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(1, 12.8, -1, 13, -62, -10, "steel_light")
    bolt.box(11, 12.9, 3, 9, -50, -40, "steel")                             # bolt face detail
    # magazine
    mag = m["gun"].bone("magazine", pivot=(0, -46, -66))
    curved_mag(mag, -40, -100, 64, 196, curve=12, segs=4, width=23, mat="alloy" if not hk else "polymer",
               rib_mat="steel_dark", round_d=8, round_len=56)
    add_arms(m, right_hand=(8, -92, 54), left_hand=(-10, -48, -250), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -485 if not hk else -505), optic=(0, 29, -40), under=(0, -31 if not hk else -37, -250),
                side=(-21, -4, -260), eject=(15, 6, -38), sight=(0, 52, 82))
    return m, MAG_A


def _ar_anims(m, MAG_A, inspect_fn, hk=False):
    cyc = dict(bone="bolt", travel=(0, 0, 78), t_back=0.018, t_fwd=0.052)
    kk = dict(kick=(2.4, 0.4, 1.0), push=11, cycle=cyc)
    anims = [
        idle(m), idle(m, "idle_empty", locked={"bolt": (0, 0, 78)}),
        draw(m, 0.7, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.13, length=0.22, **kk),
        fire_basic(m, "fire_aim", recover=0.11, length=0.2, aim=True, **kk),
        fire_basic(m, "fire_last", recover=0.13, length=0.22, lock_back=True, **kk),
        rifle_reload(m, "reload", MAG_A, empty=False, style="ar", bolt="bolt", bolt_travel=(0, 0, 78)),
        rifle_reload(m, "reload_empty", MAG_A, empty=True, style="ar", bolt="bolt", bolt_travel=(0, 0, 78)),
        firemode(m, selector_rot=(0, 0, 0)),
        inspect_fn(m), dry_fire(m),
    ]
    fm = anims[-3]
    fm.key("selector", 0.19, rot=(0, 0, 0))
    fm.key("selector", 0.23, rot=(-90, 0, 0), e="outquad")
    fm.key("selector", 0.55, rot=(-90, 0, 0))
    return anims


def m4a1():
    m, A = _ar("m4a1")

    def inspect(m):
        a = Anim(m, "inspect", 4.6)
        # forward assist tap
        a.mv("gun", 0.0, 0.4, pos=(-40, 20, 40), rot=(4, -38, -24))
        a.mv("arm_left", 0.1, 0.42, pos=(40, 60, 270), rot=(-20, 50, 10))
        a.mv("arm_left", 0.45, 0.52, pos=(32, 60, 276), rot=(-20, 50, 10), e="outquad")
        a.key("forward_assist", 0.0, pos=(0, 0, 0))
        a.key("forward_assist", 0.47, pos=(0, 0, 0))
        a.key("forward_assist", 0.52, pos=(-5, 0, 0), e="outquad")
        a.key("forward_assist", 0.6, pos=(0, 0, 0))
        a.sound(0.52, "forward_assist")
        a.mv("arm_left", 0.58, 0.66, pos=(40, 60, 270), rot=(-20, 50, 10))
        a.mv("arm_left", 0.66, 0.72, pos=(32, 60, 276), rot=(-20, 50, 10), e="outquad")
        a.key("forward_assist", 0.67, pos=(0, 0, 0))
        a.key("forward_assist", 0.72, pos=(-5, 0, 0), e="outquad")
        a.key("forward_assist", 0.8, pos=(0, 0, 0))
        a.sound(0.72, "forward_assist")
        # dust cover check: flick it closed
        a.mv("arm_left", 0.85, 1.1, pos=(36, 50, 190), rot=(-20, 50, 10))
        a.key("dust_cover", 0.0, rot=(0, 0, 0))
        a.key("dust_cover", 1.1, rot=(0, 0, 0))
        a.key("dust_cover", 1.18, rot=(0, 0, -100), e="outback")
        a.sound(1.16, "dust_cover")
        a.key("dust_cover", 1.95, rot=(0, 0, -100))
        a.key("dust_cover", 2.05, rot=(0, 0, 0), e="inquad")
        a.sound(2.05, "dust_cover")
        a.mv("gun", 1.2, 1.6, pos=(-50, 26, 46), rot=(10, -50, -40))
        # charging handle tug
        a.mv("arm_left", 1.3, 1.6, pos=(-10, -40, 40), rot=(10, 0, 0))
        a.mv("arm_right", 2.1, 2.35, pos=(10, 112, 60), rot=(-40, -10, -20))
        a.mv("gun", 2.1, 2.4, pos=(-20, 10, 30), rot=(-4, -8, -10))
        a.grab("arm_right", "charging_handle", 2.36, 2.9, fade_in=0.03, fade_out=0.06)
        a.key("charging_handle", 2.36, pos=(0, 0, 0))
        a.key("charging_handle", 2.52, pos=(0, 0, 26), e="inoutquad")
        a.key("bolt", 2.36, pos=(0, 0, 0))
        a.key("bolt", 2.52, pos=(0, 0, 22), e="inoutquad")
        a.sound(2.5, "charging_handle_back")
        a.mv("gun", 2.52, 2.8, pos=(-40, 20, 40), rot=(6, -30, -50))       # peek into the port
        a.key("charging_handle", 2.86, pos=(0, 0, 26))
        a.key("charging_handle", 2.94, pos=(0, 0, 0), e="inquad")
        a.key("bolt", 2.86, pos=(0, 0, 22))
        a.key("bolt", 2.94, pos=(0, 0, 0), e="inquad")
        a.sound(2.94, "charging_handle_forward")
        a.mv("arm_right", 2.96, 3.3, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_left", 2.9, 3.5, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.3, 4.55)
        return a

    return GunAsset(m, _ar_anims(m, A, inspect), RIFLE_FP)


def hk416():
    m, A = _ar("hk416", hk=True)

    def inspect(m):
        a = Anim(m, "inspect", 4.3)
        # mag check: pull, look at the witness holes, reseat
        a.mv("gun", 0.0, 0.4, pos=(-30, 20, 40), rot=(4, -14, -30))
        a.mv("arm_left", 0.05, 0.4, pos=along(A, 40, (6, 0, 0)), rot=(10, 10, 10))
        a.grab("arm_left", "magazine", 0.42, 1.9, fade_in=0.04, fade_out=0.06)
        a.key("magazine", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("magazine", 0.45, pos=(0, 0, 0), rot=(0, 0, 0))
        a.sound(0.45, "mag_out_rifle")
        a.key("magazine", 0.7, pos=along(A, 70, (-30, -10, 30)), rot=(10, 30, 50), e="inoutsine")
        a.key("magazine", 0.95, pos=along(A, 70, (-60, 10, 60)), rot=(20, 50, 80), e="inoutsine")
        a.key("magazine", 1.25, pos=along(A, 70, (-60, 10, 60)), rot=(20, 50, 80))
        a.key("magazine", 1.5, pos=along(A, 60, (-10, 0, 10)), rot=(6, 6, 6), e="inoutsine")
        a.key("magazine", 1.72, pos=along(A, 20), rot=(0, 0, 0), e="inoutsine")
        a.key("magazine", 1.82, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
        a.sound(1.82, "mag_in_rifle")
        a.spring("gun", "rot", 1.82, (-2.0, 0, 1.0), freq=6, damp=9)
        a.key("magazine", 1.92, pos=along(A, 1.5))
        a.key("magazine", 1.97, pos=(0, 0, 0))
        a.mv("arm_left", 2.0, 2.4, pos=(0, 0, 0), rot=(0, 0, 0))
        # quick turn to show the right side
        a.mv("gun", 2.2, 2.9, pos=(-50, 30, 40), rot=(8, -46, -10), e="inoutsine")
        _settle(a, 3.2, 4.25)
        return a

    return GunAsset(m, _ar_anims(m, A, inspect, hk=True), RIFLE_FP)


# =================================================================================================
# AKM
# =================================================================================================
def akm():
    MAG_A = 10.0
    m = new_gun("akm")
    body = m["body"]
    st = "steel_dark"
    # stamped receiver + dust cover
    body.box(-14, 14, -34, 12, -96, 196, st)
    body.box(-12, 12, 12, 20, -60, 196, st)                                  # dust cover
    for z in range(-40, 190, 30):
        body.box(-12.3, 12.3, 14, 18, z, z + 10, st)
    body.box(-14.5, 14.5, -40, -34, -100, -40, st)                          # mag well
    body.box(-6, 6, -46, -34, -40, -34, st)                                 # mag catch
    body.box(0, 14.3, -6, 10, -50, 40, "rubber")                           # ejection slot under the selector
    # trunnion, rear sight block
    body.box(-14, 14, -20, 24, -126, -96, st)
    body.box(-8, 8, 24, 36, -126, -96, st)
    body.box(-6, 6, 36, 40, -126, -100, st)                                 # leaf
    # wood furniture
    body.box(-17, 17, -34, 6, -330, -126, "wood_red")                      # lower handguard
    body.box(-8, 8, -10, 2, -320, -140, "steel")
    body.box(-14, 14, 6, 24, -310, -126, "wood_red")                       # gas tube cover
    body.cyl((0, 14, -340), 14, 40, st)                                     # gas block
    body.box(-6, 6, -14, 30, -350, -330, st)
    barrel(body, -330, -420, d=16)
    # front sight post
    body.box(-8, 8, -8, 10, -420, -398, st)
    body.box(-8, -5, 10, 40, -416, -402, st)
    body.box(5, 8, 10, 40, -416, -402, st)
    body.box(-1, 1, 10, 34, -410, -408, st)
    # slant brake
    body.box(-10, 10, -10, 10, -462, -420, st)
    body.box(-10.5, 10.5, -8, 4, -446, -436, "rubber")
    # pistol grip + trigger
    pistol_grip(body, 20, top_y=-34, length=96, width=26, depth=34, angle=-18, mat="wood_red", checker=False)
    trigger_group(m, body, -6, y_top=-34, guard_depth=30, guard_len=70, guard_mat=st)
    # fixed wooden stock
    stock = m["gun"].bone("stock", pivot=(0, 0, 196))
    stock.taper(-17, 17, 196, 470, 8, -30, -36, -128, "wood_red")                 # comb drops to the heel, toe sweeps down
    stock.box(-18.5, 18.5, -130, -28, 470, 481, st)                        # steel butt plate
    # selector lever (right side), rotates around its front pivot
    sel = body.bone("selector", pivot=(14, 4, 0))
    sel.box(14, 16, -4, 8, 0, 120, "steel")
    sel.box(14, 18, -8, 0, 110, 124, "steel")
    # bolt carrier with charging handle (right side)
    bolt = body.bone("bolt", pivot=(18, 2, -60))
    bolt.box(1, 13, -6, 8, -60, -14, "steel_light")
    bolt.box(14, 28, -2, 6, -64, -54, "steel_light")
    bolt.box(26, 32, -4, 8, -66, -52, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -40, -70))
    curved_mag(mag, -34, -100, 60, 230, curve=34, segs=6, width=26, mat="steel_dark", rib_mat="steel",
               round_d=10, round_len=56)
    add_arms(m, right_hand=(8, -90, 40), left_hand=(-12, -44, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -464), optic=None, under=(0, -34, -260), side=(-16, 10, 0), eject=(15, 6, -40),
                sight=(0, 40, -110))

    def inspect():
        a = Anim(m, "inspect", 4.6)
        # rotate to the ejection port side, rack it halfway, peek
        a.mv("gun", 0.0, 0.45, pos=(-12, 12, 0), rot=(6, -34, -44), e="inoutsine")
        a.mv("arm_right", 0.25, 0.5, pos=(30, 96, -60), rot=(-40, -20, -30))
        a.grab("arm_right", "bolt", 0.5, 1.4, fade_in=0.03, fade_out=0.06)
        a.key("bolt", 0.0, pos=(0, 0, 0))
        a.key("bolt", 0.52, pos=(0, 0, 0))
        a.key("bolt", 0.7, pos=(0, 0, 60), e="inoutquad")
        a.sound(0.66, "charging_handle_back")
        a.mv("gun", 0.7, 1.05, pos=(-16, 16, 0), rot=(10, -46, -60), e="inoutsine")
        a.key("bolt", 1.25, pos=(0, 0, 60))
        a.key("bolt", 1.32, pos=(0, 0, 0), e="inquad")
        a.sound(1.32, "charging_handle_forward")
        a.spring("gun", "rot", 1.32, (1.6, 0, -1.6), freq=6, damp=8)
        a.mv("arm_right", 1.4, 1.7, pos=(0, 0, 0), rot=(0, 0, 0))
        # selector clack: down to auto, down to semi, up to safe
        a.mv("arm_right", 1.9, 2.05, pos=(10, 40, -60), rot=(-20, -10, -10))
        for t, r in ((2.1, (-14, 0, 0)), (2.45, (-28, 0, 0)), (2.85, (0, 0, 0))):
            a.key("selector", t - 0.05, rot=(0, 0, 0) if t == 2.1 else ((-14, 0, 0) if t == 2.45 else (-28, 0, 0)))
            a.key("selector", t, rot=r, e="outquad")
            a.sound(t, "selector_ak")
            a.spring("gun", "rot", t, (0.6, 0, 0.6), freq=8, damp=12)
        a.mv("arm_right", 2.9, 3.15, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 1.6, 2.2, pos=(-30, 24, 40), rot=(0, -30, -10))
        _settle(a, 3.3, 4.55)
        return a

    cyc = dict(bone="bolt", travel=(0, 0, 112), t_back=0.022, t_fwd=0.06)
    kk = dict(kick=(3.4, 0.6, 1.4), push=13, cycle=cyc)
    anims = [
        idle(m), draw(m, 0.7, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.15, length=0.24, **kk),
        fire_basic(m, "fire_aim", recover=0.13, length=0.22, aim=True, **kk),
        rifle_reload(m, "reload", MAG_A, empty=False, style="ak", rock=14, mag_out=70),
        rifle_reload(m, "reload_empty", MAG_A, empty=True, style="ak", rock=14, mag_out=70, bolt="bolt",
                     ch="bolt", bolt_travel=(0, 0, 112), ch_travel=(0, 0, 112), bolt_hold_open=False, ch_hand="right"),
        firemode(m, selector_rot=(-14, 0, 0)), inspect(), dry_fire(m),
    ]
    fp = {"hip": {"pos": [0.118, -0.128, -0.17], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.24}}
    return GunAsset(m, anims, fp)


# =================================================================================================
# Steyr AUG A3
# =================================================================================================
def aug():
    MAG_A = -4.0
    m = new_gun("aug")
    body = m["body"]
    g = "polymer_od"
    # stock shell
    body.box(-24, 24, -58, 14, -60, 300, g)
    body.box(-22, 22, -88, -58, 150, 300, g)
    body.box(-25, 25, -92, 18, 296, 308, "rubber")
    # receiver (alloy) with rail
    body.box(-17, 17, 0, 30, -140, 140, "alloy")
    body.rail(-136, 136, 30, mat="alloy")
    # barrel + integral folding foregrip
    body.cyl((0, 4, -150), 34, 30, "steel_dark")
    barrel(body, -150, -420, d=17, y=4)
    for i in range(6):
        body.box(-10, 10, -6, 14, -330 + i * 22, -322 + i * 22, "steel_dark")  # cooling ribs
    flash_hider_a2(body, -420, d=20, length=40)
    fg = body.bone("foregrip", pivot=(0, -14, -150))
    fg.box(-12, 12, -100, -14, -168, -138, g, rot=(-8, 0, 0), pivot=(0, -14, -150))
    # big trigger guard enclosing the hand + grip
    body.box(-14, 14, -150, -140, -140, 40, g)
    body.box(-14, 14, -150, -58, -150, -138, g)
    pistol_grip(body, 30, top_y=-58, length=84, width=28, depth=38, angle=-12, mat=g, checker=False)
    trigger_group(m, body, -40, y_top=-58, guard_depth=0.1, guard_len=2, guard_mat=g)
    sel = body.bone("selector", pivot=(0, -40, 10))
    sel.box(-28, 28, -46, -36, 4, 16, "polymer")                               # crossbolt safety
    # charging handle (left side, reciprocating slot)
    ch = body.bone("charging_handle", pivot=(-20, 14, -90))
    ch.box(-34, -17, 8, 20, -98, -82, "polymer")
    ch.box(-38, -32, 6, 22, -100, -80, "polymer")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(14, 24.5, -10, 8, 150, 200, "steel_light")                        # visible through the port
    body.box(24, 24.6, -12, 10, 140, 210, "rubber")
    # mag behind the grip (translucent)
    mag = m["gun"].bone("magazine", pivot=(0, -58, 112))
    curved_mag(mag, -56, 86, 60, 190, curve=12, segs=4, width=24, mat="polymer_clear", rib_mat="polymer_grey",
               round_d=8, round_len=56)
    body.box(-6, 6, -70, -58, 152, 160, "polymer")                             # mag release
    add_arms(m, right_hand=(8, -110, 46), left_hand=(-10, -78, -152), right_rot=(34, 14, 6), left_rot=(10, -18, -4))
    add_sockets(m, muzzle=(0, 4, -460), optic=(0, 33, -20), under=None, side=(-17, 15, -60), eject=(25, 0, 170),
                sight=(0, 58, 60))
    # BUIS on rail
    body.box(-8, 8, 33, 54, 54, 66, "alloy")

    def inspect():
        a = Anim(m, "inspect", 4.4)
        # cradle it in the support arm: rotate to show the left, tilt the mag towards the camera
        a.mv("gun", 0.0, 0.55, pos=(-80, 30, 70), rot=(-10, 40, 50), e="inoutsine")
        a.mv("arm_left", 0.1, 0.55, pos=(20, -40, 180), rot=(10, 10, 20))
        a.wave("gun", "rot", (0.6, 0.6, 0.4), 2.2)
        # tap the translucent mag (round count)
        for t in (1.25, 1.55):
            a.mv("arm_left", t - 0.12, t, pos=(20, -100, 260), rot=(30, 10, 20), e="outquad")
            a.sound(t, "tap")
            a.mv("arm_left", t, t + 0.1, pos=(20, -80, 240), rot=(20, 10, 20))
        a.mv("gun", 1.9, 2.6, pos=(-50, 40, 50), rot=(14, -46, -24), e="inoutsine")
        a.mv("arm_left", 1.9, 2.6, pos=(0, 0, 0), rot=(0, 0, 0))
        # fold the foregrip and back
        a.key("foregrip", 0.0, rot=(0, 0, 0))
        a.key("foregrip", 2.7, rot=(0, 0, 0))
        a.key("foregrip", 2.85, rot=(70, 0, 0), e="outquad")
        a.sound(2.85, "click_small")
        a.key("foregrip", 3.15, rot=(70, 0, 0))
        a.key("foregrip", 3.3, rot=(0, 0, 0), e="outback")
        a.sound(3.3, "click_small")
        _settle(a, 3.4, 4.35)
        return a

    cyc = dict(bone="bolt", travel=(0, 0, 60), t_back=0.018, t_fwd=0.052)
    kk = dict(kick=(2.2, 0.3, 0.9), push=10, cycle=cyc)
    anims = [
        idle(m), idle(m, "idle_empty", locked={"charging_handle": (0, 0, 100)}),
        draw(m, 0.7, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.13, length=0.22, **kk),
        fire_basic(m, "fire_aim", recover=0.11, length=0.2, aim=True, **kk),
        fire_basic(m, "fire_last", recover=0.13, length=0.22, **kk),
        rifle_reload(m, "reload", MAG_A, empty=False, style="ar", tilt=(4, -10, -30), tilt_pos=(-30, 14, 10)),
        rifle_reload(m, "reload_empty", MAG_A, empty=True, style="smg", ch="charging_handle", bolt="charging_handle",
                     bolt_travel=(0, 0, 100), ch_travel=(0, 0, 100), bolt_hold_open=True, ch_hand="left",
                     tilt=(4, -10, -30), tilt_pos=(-30, 14, 10)),
        firemode(m, selector_rot=(0, 0, 0)), inspect(), dry_fire(m),
    ]
    anims[5].key("charging_handle", 0.0, pos=(0, 0, 0))
    anims[5].key("charging_handle", 0.03, pos=(0, 0, 100), e="outquad")
    anims[5].key("charging_handle", 0.22, pos=(0, 0, 100))
    fm = anims[-3]
    fm.key("selector", 0.19, pos=(0, 0, 0))
    fm.key("selector", 0.23, pos=(-10, 0, 0), e="outquad")
    fm.key("selector", 0.55, pos=(-10, 0, 0))
    return GunAsset(m, anims, {"hip": {"pos": [0.12, -0.125, -0.26], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.11}})


GUNS = {"m4a1": m4a1, "hk416": hk416, "akm": akm, "aug": aug}
