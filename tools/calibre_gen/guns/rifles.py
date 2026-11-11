"""M4A1, HK416, AKM, Steyr AUG A3."""
import numpy as np

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden, along)
from ..templates import rifle_reload, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, flash_hider_a2, ar_front_sight,
                     buis_rear, ar_stock, picatinny_handguard, muzzle_brake)
from ..common import moving
from ..parts import pins, vents, ejection_port, side_swivel, sling_swivel
from ..longkit import (slot, top_slot, ribs, ring_sight, eared_sight, drum_sight, flip_sight, aperture_sight,
                       peep, rod_stock, selector, paddle, button, stock_solid)
from ..pistolkit import control
from .ar15 import _buis, _flip_front

RIFLE_FP = {"hip": {"pos": [0.118, -0.128, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.085}}


# =================================================================================================
# Steyr AUG A3
# =================================================================================================
def aug():
    # Steyr AUG A3: 790 mm long bullpup, 508 mm barrel, translucent magazine behind the grip
    MAG_A = -4.0
    g = "polymer_od"
    m = new_gun("aug")
    body = m["body"]
    al, st = "alloy", "steel_dark"
    # one-piece stock shell: butt, magazine housing, grip, the big hand guard loop
    body.rbox(-22, 22, -62, 28, 60, 310, g, r=9, edges="all")                          # butt / mechanism housing
    body.rbox(-21, 21, -30, 26, -40, 62, g, r=7, edges="all")                          # over the grip
    body.rbox(-23, 23, -70, 30, 310, 318, "rubber", r=6, edges="all")                  # butt plate
    for i in range(4):
        body.box(-20, 20, -56 + i * 22, -50 + i * 22, 318, 318.6, "polymer")
    body.box(-22.4, 22.4, -10, -6, 66, 300, "rubber")                                  # shell seam
    for sx in (-1, 1):
        body.cyl((sx * 22.5, -38, 286), 12, 2, "steel", axis="x", sides=16)             # sling pin / swivel
    gp = (0, -30, 46)
    body.rbox(-15, 15, -128, -30, 28, 64, g, r=5, axis="y", edges="all", rot=(-12, 0, 0), pivot=gp)   # grip
    body.path([(26, -30), (-18, -40), (-34, -82), (-20, -120), (30, -132), (58, -126)], 30, 9, g)     # hand guard loop
    trig = body.bone("trigger", pivot=(0, -30, 6))
    trig.box(-3.5, 3.5, -52, -30, 2, 9, st, rot=(6, 0, 0), pivot=(0, -30, 6))
    trig.box(-3.5, 3.5, -64, -50, -1, 6, st, rot=(22, 0, 0), pivot=(0, -50, 4))
    sel = body.bone("selector", pivot=(-21, -18, 30))                                  # cross-bolt safety
    sel.cyl((-22.5, -18, 30), 10, 5, "steel", axis="x", sides=16)
    body.cyl((21.6, -18, 30), 10, 2, "sight_orange", axis="x", sides=16)
    ejection_port(body, 22, -6, 12, 150, 206, lip_mat=g)
    body.box(-22.6, -22, -6, 12, 150, 206, "polymer")                                  # blanked left port
    paddle(body, (0, -62, 142), mat=g, w=18, h=8, d=12)                                 # magazine release behind the mag
    # receiver with the top rail and back-up sights
    body.rbox(-17, 17, 24, 40, -112, 124, al, r=5, edges="top")
    body.rbox(-17, 17, -16, 26, -112, -36, al, r=6, edges="bottom")                    # receiver housing round the barrel
    body.box(-10.5, 10.5, 40, 44, -108, 120, al)
    body.rail(-106, 118, 44, mat=al, side="top")
    for sx in (-1, 1):
        body.rail(-104, -40, 30, x=sx * 17, mat=al, side="right" if sx > 0 else "left", width=14)
    _buis(body, 96, 47, al, sy=70)
    _flip_front(body, -92, 47, al, sy=70)
    slot(body, -17, 28, 32, -104, 4)                                                   # cocking slot (left)
    # barrel group: collar, gas plug, folding fore grip, flash hider
    body.cyl((0, 0, -124), 30, 26, st)
    barrel(body, -112, -470, d=18, mat=st)
    body.cyl((14, 4, -150), 12, 44, st)                                                # gas cylinder
    body.cyl((14, 4, -174), 14, 6, "steel")
    flash_hider_a2(body, -458, d=22, length=44)
    fg = body.bone("foregrip", pivot=(0, -12, -146))
    fg.rbox(-11, 11, -108, -12, -160, -132, g, r=5, axis="y", edges="all", rot=(4, 0, 0), pivot=(0, -12, -146))
    fg.box(-12, 12, -112, -106, -162, -130, g, rot=(4, 0, 0), pivot=(0, -12, -146))
    fg.cyl((0, -10, -146), 12, 30, st, axis="x", sides=16)
    ch = body.bone("charging_handle", pivot=(-17, 30, -96))
    ch.box(-26, -17, 27, 33, -102, -90, st)
    ch.rbox(-34, -26, 22, 38, -104, -88, "polymer", r=3, axis="y", edges="all")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 21.6, -5, 11, 152, 204, "steel_light")
    # translucent waffle magazine
    mag = m["gun"].bone("magazine", pivot=(0, -62, 104))
    curved_mag(mag, -36, 76, 58, 200, curve=10, segs=5, width=24, mat="polymer_clear", rib_mat="polymer_grey",
               round_d=9.6, round_len=57)
    add_arms(m, right_hand=(8, -100, 50), left_hand=(-10, -78, -146), right_rot=(34, 14, 6), left_rot=(10, -18, -4))
    add_sockets(m, muzzle=(0, 0, -504), optic=(0, 47, -10), under=None, side=(-21, 30, -72), eject=(23, 3, 178),
                sight=(0, 70, 96))


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
        firemode(m, selector_rot=(0, 0, 0)), Anim(m, "inspect", 1.0), dry_fire(m),
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
