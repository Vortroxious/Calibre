"""M4A1, HK416, AKM, Steyr AUG A3."""
import numpy as np

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden, along)
from ..templates import rifle_reload, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, flash_hider_a2, ar_front_sight,
                     buis_rear, ar_stock, picatinny_handguard, muzzle_brake)

RIFLE_FP = {"hip": {"pos": [0.118, -0.128, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.085}}


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


GUNS = {"aug": aug}
