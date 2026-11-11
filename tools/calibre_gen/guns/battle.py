"""FN FAL, FN SCAR-H, SVD Dragunov, M14 EBR."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden, along)
from ..templates import rifle_reload, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, flash_hider_a2, muzzle_brake,
                     picatinny_handguard, scope)
from ..common import moving
from ..parts import pins, vents, ejection_port, side_swivel, sling_swivel
from ..longkit import (slot, top_slot, ribs, ring_sight, eared_sight, drum_sight, flip_sight, aperture_sight,
                       peep, rod_stock, selector, paddle, button, stock_solid)
from ..pistolkit import control
from .ar15 import _buis, _flip_front

FP = {"hip": {"pos": [0.12, -0.13, -0.19], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.09}}


def _kk(bolt, travel, kick=4.2, push=15):
    return dict(kick=(kick, 0.6, 1.4), push=push, cycle=dict(bone=bolt, travel=travel, t_back=0.022, t_fwd=0.062))


# =================================================================================================
# FN FAL
# =================================================================================================
def fal():
    # FN FAL 50.00: 1090 mm long, 533 mm barrel
    A = 4.0
    st = "steel_parked"
    m = new_gun("fal")
    body = m["body"]
    P = "polymer"
    body.rbox(-15, 15, -14, 18, -150, 130, st, r=3, edges="top")                       # upper receiver
    body.rbox(-13, 13, 18, 23, -100, 126, st, r=2.4, edges="top")                      # top cover
    ejection_port(body, 15, -2, 12, -96, -36, lip_mat=st)
    slot(body, -15, 4, 8, -138, -30)                                                   # cocking slot (left)
    body.box(-14, 14, -42, -14, -122, 150, st)                                         # lower / trigger frame
    body.box(-15.4, 15.4, -16, -13, -146, 128, "rubber")
    body.cyl((0, -22, -124), 12, 34, "steel", axis="x", sides=16)                      # hinge pin
    body.rbox(-13, 13, -40, 14, 128, 160, st, r=4, edges="top")                        # stock socket
    # barrel, gas system, hand guards, front sight on the gas block, combination flash hider
    body.cyl((0, 0, -160), 30, 22, st)
    barrel(body, -150, -663, d=17, mat=st)
    body.cyl((0, 20, -300), 14, 280, st)                                               # gas cylinder
    body.rbox(-19, 19, -24, 32, -412, -168, P, r=9, edges="all")                       # hand guards
    vents(body, 19, 16, 22, -400, -180, n=7, fill=0.55)
    vents(body, 19, -14, -8, -400, -180, n=7, fill=0.55)
    body.box(-19.4, 19.4, 2, 5, -408, -172, "rubber")
    body.rbox(-9, 9, -11, 36, -446, -416, st, r=3, edges="top")                        # gas block
    eared_sight(body, -430, 36, 14, st, w=18, depth=14, lean=6)
    body.cyl((0, 20, -452), 12, 14, "steel")                                           # gas plug
    body.cyl((0, 0, -640), 22, 62, st)                                                 # long flash hider
    for ang in (0, 60, 120):
        body.box(-11.4, 11.4, -1.6, 1.6, -666, -622, "rubber", rot=(0, 0, ang), pivot=(0, 0, -644))
    body.cyl((0, 0, -671.3), 9.5, 0.6, "rubber", sides=8)
    sling_swivel(body, 0, -11, -438, along="x", drop=9, w=16)
    # carry handle folded down on the right
    body.cyl((16, 6, -112), 8, 5, st, axis="x", sides=8)
    body.path([(-112, 6), (-104, -14), (-52, -14), (-44, 6)], 5, 5, st, x=19)
    # sights: sliding aperture on the lower, behind the cover
    body.box(-9, 9, 18, 24, 112, 148, st)
    peep(body, 132, 24, 56, st, w=10, hole=4.4, depth=3, hole_y=48)
    for sx in (-1, 1):
        body.box(sx * 9 - 1.5, sx * 9 + 1.5, 24, 40, 124, 144, st)
    # frame: magazine well, grip, guard, controls
    body.box(-15, 15, -52, -42, -110, -40, st)
    control(body, "mag_release", (0, -44, -36), [(-5, 5, -62, -42, -40, -35, st), (-6, 6, -64, -58, -41, -30, st)],
            turn=(20, 0, 0))
    control(body, "bolt_catch", (-14, -30, -30), [(-17, -14, -40, -24, -36, -24, st)], press=(0, 3, 0))
    pistol_grip(body, 62, top_y=-40, length=96, width=28, depth=36, angle=-18, mat=P)
    trigger_group(m, body, 22, y_top=-42, guard_depth=27, guard_len=66, guard_mat=st)
    selector(body, (-14, -28, 66), mat="steel", length=16, side=-1, turn=(-60, 0, 0))
    pins(body, 14, [(-30, 24), (-26, 100)], d=5, mat="steel_dark")
    ch = body.bone("charging_handle", pivot=(-15, 6, -130))
    ch.box(-24, -15, 3, 9, -136, -124, st)
    ch.cyl((-28, 6, -130), 14, 8, P, axis="x", sides=16)
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 14.6, -1, 11, -94, -38, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    stock_solid(stock, 16, [(156, 10), (412, 4)], [(156, -36), (200, -44), (412, -108)], P, pad="rubber", pad_th=8)
    sling_swivel(stock, 0, -96, 360, along="z", drop=9)
    mag = m["gun"].bone("magazine", pivot=(0, -46, -75))
    curved_mag(mag, -40, -106, 62, 150, curve=6, segs=3, width=25, mat="steel_dark", rib_mat="steel", round_d=12,
               round_len=70)
    add_arms(m, right_hand=(8, -96, 74), left_hand=(-12, -50, -290), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -673), optic=(0, 23, 20), under=(0, -26, -290), eject=(15, 6, -66),
                sight=(0, 48, 132))


    kk = _kk("bolt", (0, 0, 100))
    anims = [
        idle(m), idle(m, "idle_empty", locked={"bolt": (0, 0, 100)}), draw(m, 0.75, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.18, length=0.28, **kk),
        fire_basic(m, "fire_aim", recover=0.15, length=0.25, aim=True, **kk),
        fire_basic(m, "fire_last", recover=0.18, length=0.28, lock_back=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="ak", rock=8, mag_out=70),
        rifle_reload(m, "reload_empty", A, empty=True, style="ak", rock=8, mag_out=70, bolt="bolt",
                     bolt_travel=(0, 0, 100), ch="charging_handle", ch_travel=(0, 0, 100), ch_hand="left"),
        firemode(m, selector_rot=(-60, 0, 0)), Anim(m, "inspect", 1.0), dry_fire(m),
    ]
    return GunAsset(m, anims, FP)


# =================================================================================================
# FN SCAR-H
# =================================================================================================
def scar_h():
    # FN SCAR-H (Mk 17, 16 in): 965 mm with the stock out, 406 mm barrel
    A = 2.0
    up, lo = "alloy_tan", "polymer_tan"
    m = new_gun("scar_h")
    body = m["body"]
    st = "steel_dark"
    body.rbox(-21, 21, -12, 38, -330, 100, up, r=6, edges="top")                       # monolithic upper
    body.box(-10.5, 10.5, 38, 42, -326, 96, up)
    body.rail(-324, 94, 42, mat=up, side="top")
    body.rail(-322, -200, -12, mat=up, side="bottom")
    for sx in (-1, 1):
        body.rail(-322, -214, 8, x=sx * 21, mat=up, side="right" if sx > 0 else "left", width=18)
        slot(body, sx * 21, 15, 19, -262, -136)                                        # charging-handle slots
        body.box(sx * 21 - 0.4, sx * 21 + 0.4, 24, 30, -180, 60, up)                   # extrusion rib
    ejection_port(body, 21, 0, 14, -116, -58, lip_mat=up)
    body.taper(21, 26, -54, -34, 16, 14, 2, 6, up, round=0)                            # brass deflector
    # barrel, gas regulator, brake
    barrel(body, -330, -521, d=19, mat=st)
    body.rbox(-9, 9, 6, 30, -356, -330, st, r=3, edges="top")                          # gas block
    body.cyl((0, 20, -362), 12, 12, "steel")
    muzzle_brake(body, -512, d=26, length=62, ports=3, mat=st)
    _buis(body, 80, 45, up, sy=70)
    _flip_front(body, -344, 30, st, sy=70)
    # lower: magazine well, grip, guard, ambidextrous controls
    body.rbox(-16, 16, -48, -12, -114, 70, lo, r=3, edges="bottom")
    body.rbox(-17, 17, -62, -12, -110, -44, lo, r=2.4, axis="y", edges="all")
    body.box(-17.6, 17.6, -64, -58, -111, -43, lo)
    body.box(-21.4, 21.4, -14, -11, -326, 96, "rubber")
    pistol_grip(body, 14, top_y=-46, length=92, width=28, depth=36, angle=-18, mat=lo)
    trigger_group(m, body, -18, y_top=-48, guard_depth=26, guard_len=62, guard_mat=lo)
    selector(body, (-16, -30, 20), mat=lo, length=15, side=-1, turn=(-90, 0, 0))
    body.box(16, 18.6, -33, -27, 6, 22, lo)
    control(body, "bolt_catch", (-16, -22, -36), [(-18.6, -16, -30, -14, -44, -30, st)], press=(0, 3, 0))
    button(body, "mag_release", (16, -34, -40), d=9, mat=st)
    pins(body, 16, [(-22, -100), (-22, 56)], d=5, mat=st)
    ch = body.bone("charging_handle", pivot=(-21, 17, -250))
    ch.box(-30, -21, 14, 20, -256, -244, st)
    ch.rbox(-37, -30, 11, 23, -260, -240, st, r=2.4, axis="y", edges="all")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 20.6, 1, 13, -114, -60, "steel_light")
    # side-folding, adjustable stock with the cheek riser
    stock = m["gun"].bone("stock", pivot=(21, 10, 100))
    stock.rbox(-20, 20, -40, 36, 100, 124, lo, r=5, edges="all")                       # hinge block
    stock.cyl((21, 0, 112), 9, 60, "steel", axis="y", sides=16)
    stock.rbox(-13, 13, -20, 26, 124, 330, lo, r=6, edges="all")                       # spine
    stock.rbox(-15, 15, 26, 40, 150, 300, lo, r=5, edges="top")                        # cheek riser
    stock.path([(124, -30), (220, -62), (330, -78)], 22, 12, lo)                       # lower strut
    stock.rbox(-19, 19, -92, 34, 328, 344, lo, r=5, edges="all")
    stock.rbox(-20, 20, -96, 36, 344, 356, "rubber", r=5, edges="all")
    side_swivel(body, -21, 4, 88, h=14)
    side_swivel(body, -21, 4, -310, h=14)
    mag = m["gun"].bone("magazine", pivot=(0, -50, -77))
    straight_mag(mag, -36, -106, -48, 158, width=26, mat="steel_dark", round_d=12, round_len=70)
    add_arms(m, right_hand=(8, -100, 30), left_hand=(-12, -44, -250), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -576), optic=(0, 45, -60), under=(0, -17, -260), side=(-24, 8, -268),
                eject=(22, 7, -86), sight=(0, 70, 80))


    kk = _kk("bolt", (0, 0, 96))
    anims = [
        idle(m), idle(m, "idle_empty", locked={"bolt": (0, 0, 96), "charging_handle": (0, 0, 96)}),
        draw(m, 0.75, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.17, length=0.27, **kk),
        fire_basic(m, "fire_aim", recover=0.14, length=0.24, aim=True, **kk),
        fire_basic(m, "fire_last", recover=0.17, length=0.27, lock_back=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="ar", bolt="bolt", bolt_travel=(0, 0, 96)),
        rifle_reload(m, "reload_empty", A, empty=True, style="ar", bolt="bolt", bolt_travel=(0, 0, 96)),
        firemode(m, selector_rot=(-90, 0, 0)), Anim(m, "inspect", 1.0), dry_fire(m),
    ]
    # reciprocating handle follows the bolt in fire/reload
    for a in anims:
        if a.name.startswith("fire") and ("bolt", "pos") in a.tracks:
            for (t, v, e) in a.tracks[("bolt", "pos")].keys:
                a.key("charging_handle", t, pos=v, e=e)
    return GunAsset(m, anims, FP)


# =================================================================================================
# SVD Dragunov (integral PSO-1)
# =================================================================================================
def svd():
    A = 6.0
    m = new_gun("svd")
    body = m["body"]
    st = "steel_dark"
    body.box(-14, 14, -34, 12, -100, 200, st)
    body.box(-12, 12, 12, 20, -60, 200, st)
    body.box(-14.5, 14.5, -40, -34, -100, -50, st)
    body.box(0, 14.3, -6, 10, -50, 30, "rubber")
    body.box(-14, 14, -20, 24, -126, -100, st)
    body.box(-17, 17, -30, 10, -400, -126, "wood_red")
    for z in range(-390, -140, 26):
        body.box(-17.4, 17.4, -20, 0, z, z + 12, "rubber")
    body.cyl((0, 14, -410), 16, 40, st)
    barrel(body, -400, -640, d=16)
    body.box(-6, 6, -8, 40, -620, -606, st)
    body.box(-10, 10, -10, 10, -700, -640, st)                                   # flash hider
    for z in (-690, -675, -660):
        body.box(-10.4, 10.4, -6, 6, z, z + 6, "rubber")
    pistol_grip(body, 30, top_y=-34, length=40, width=26, depth=30, angle=-10, mat="wood_red", checker=False)
    trigger_group(m, body, -6, y_top=-34, guard_depth=30, guard_len=70, guard_mat=st)
    # skeleton thumbhole stock + cheek rest
    stock = m["gun"].bone("stock", pivot=(0, 0, 200))
    stock.box(-15, 15, 0, 14, 200, 520, "wood_red")
    stock.box(-15, 15, -110, -84, 260, 520, "wood_red")
    stock.box(-15, 15, -110, 0, 200, 230, "wood_red", rot=(30, 0, 0), pivot=(0, 0, 215))
    stock.box(-15, 15, -110, 14, 480, 520, "wood_red")
    stock.box(-16, 16, -118, 18, 516, 528, st)
    cheek = stock.bone("cheek_rest", pivot=(0, 14, 360))
    cheek.box(-14, 14, 14, 34, 300, 420, "leather")
    sel = body.bone("selector", pivot=(14, 4, 0))
    sel.box(14, 16, -4, 8, 0, 100, "steel")
    bolt = body.bone("bolt", pivot=(18, 2, -60))
    bolt.box(1, 13, -6, 8, -60, -14, "steel_light")
    bolt.box(14, 28, -2, 6, -64, -54, "steel_light")
    bolt.box(26, 32, -4, 8, -66, -52, "steel_light")
    # PSO-1 4x on its side mount
    pso = body.bone("pso1", pivot=(0, 60, 40))
    pso.box(-20, -14, 0, 40, -10, 90, st)                                         # side rail mount
    scope(pso, 40, 66, length=280, tube_d=28, obj_d=40, eye_d=34, mat="steel_dark", mount_y=24)
    pso.box(-20, 20, 50, 84, 170, 200, "rubber")                                   # eyecup
    pso.box(-12, 12, 60, 80, -110, -96, "rubber")                                  # sunshade
    mag = m["gun"].bone("magazine", pivot=(0, -40, -80))
    curved_mag(mag, -34, -100, 70, 150, curve=12, segs=3, width=24, mat="steel_dark", rib_mat="steel", round_d=11,
               round_len=70)
    add_arms(m, right_hand=(8, -66, 36), left_hand=(-12, -40, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -700), optic=None, under=(0, -30, -320), eject=(15, 6, -30), sight=(0, 66, 196))
    m.meta["integral_optic"] = {"zoom": 4.0, "reticle": "pso1", "eye": [0, 66, 196]}

    def inspect():
        a = Anim(m, "inspect", 4.8)
        # bring the PSO-1 up to the eye, check through the scope
        a.mv("gun", 0.0, 0.6, pos=(-90, 30, 60), rot=(4, 16, 10), e="inoutsine")
        a.wave("gun", "rot", (0.4, 0.5, 0.2), 1.6)
        a.mv("arm_left", 0.7, 1.0, pos=(-10, 110, -40), rot=(-30, 0, 30))
        # adjust the elevation turret
        for t in (1.1, 1.3, 1.5):
            a.sound(t, "click_small")
        a.mv("arm_left", 1.6, 1.9, pos=(0, 0, 0), rot=(0, 0, 0))
        # rotate to look at the cheek rest, flip it
        a.mv("gun", 1.8, 2.5, pos=(-40, 30, -40), rot=(-6, -56, -10), e="inoutsine")
        a.mv("arm_left", 2.3, 2.6, pos=(20, 60, 560), rot=(-30, 40, 0))
        a.key("cheek_rest", 0.0, rot=(0, 0, 0))
        a.key("cheek_rest", 2.62, rot=(0, 0, 0))
        a.key("cheek_rest", 2.74, rot=(0, 0, -70), e="outquad")
        a.sound(2.74, "click_small")
        a.key("cheek_rest", 3.1, rot=(0, 0, -70))
        a.key("cheek_rest", 3.22, rot=(0, 0, 0), e="outback")
        a.sound(3.22, "click_small")
        a.mv("arm_left", 3.3, 3.8, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.5, 4.75)
        return a

    kk = _kk("bolt", (0, 0, 120), kick=5.0, push=16)
    anims = [
        idle(m), draw(m, 0.8, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.24, length=0.36, **kk),
        fire_basic(m, "fire_aim", recover=0.2, length=0.32, aim=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="ak", rock=10, mag_out=60),
        rifle_reload(m, "reload_empty", A, empty=True, style="ak", rock=10, mag_out=60, bolt="bolt", ch="bolt",
                     bolt_travel=(0, 0, 120), ch_travel=(0, 0, 120), bolt_hold_open=False, ch_hand="right"),
        inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, {"hip": {"pos": [0.12, -0.15, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.07}})


# =================================================================================================
# M14 EBR (Sage chassis)
# =================================================================================================
def m14ebr():
    A = 6.0
    m = new_gun("m14ebr")
    body = m["body"]
    al = "alloy"
    body.box(-14, 14, -14, 16, -100, 120, "steel_parked")                       # M14 receiver
    body.box(-19, 19, -40, 30, -360, -100, al)                                   # EBR chassis forend
    body.rail(-356, 116, 30, mat=al)
    body.rail(-350, -120, -40, mat=al, side="bottom")
    body.rail(-350, -150, -5, x=-19, mat=al, side="left", width=20)
    body.rail(-350, -150, -5, x=19, mat=al, side="right", width=20)
    body.box(-17, 17, -40, -14, -100, 140, al)
    body.box(-16, 16, -46, -40, -104, -40, al)
    for z in range(-340, -120, 30):
        body.box(-19.4, 19.4, -30, 10, z, z + 14, "rubber")
    pistol_grip(body, 42, top_y=-40, length=92, width=28, depth=36, angle=-18, mat="polymer")
    trigger_group(m, body, 4, y_top=-40, guard_depth=26, guard_len=62, guard_mat="steel_parked")
    sel = body.bone("selector", pivot=(0, -38, -20))
    sel.box(-3, 3, -44, -38, -30, -14, "steel")                                   # safety in the guard
    barrel(body, -360, -560, d=18)
    muzzle_brake(body, -560, d=22, length=50, ports=3)
    # adjustable stock
    stock = m["gun"].bone("stock", pivot=(0, 0, 140))
    stock.cyl((0, -6, 240), 32, 200, al)
    stock.taper(-20, 20, 240, 340, 14, 14, -58, -80, "polymer")
    stock.box(-14, 14, 14, 34, 250, 320, "polymer")
    stock.box(-22, 22, -86, 18, 336, 348, "rubber")
    # op-rod handle (right side)
    bolt = body.bone("bolt", pivot=(16, 0, -40))
    bolt.box(1, 13.5, -4, 10, -60, -10, "steel_light")
    bolt.box(14, 22, -2, 8, -120, -40, "steel_parked")
    bolt.box(20, 30, -4, 10, -128, -112, "steel_parked")
    mag = m["gun"].bone("magazine", pivot=(0, -46, -80))
    curved_mag(mag, -40, -100, 76, 150, curve=6, segs=3, width=26, mat="steel_dark", rib_mat="steel", round_d=10,
               round_len=70)
    add_arms(m, right_hand=(8, -96, 62), left_hand=(-12, -48, -260), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -610), optic=(0, 33, -10), under=(0, -43, -280), side=(-22, -5, -280),
                eject=(15, 6, -30), sight=(0, 50, 100))
    body.box(-8, 8, 33, 50, 96, 106, al)
    body.box(-6, 6, 33, 52, -330, -320, al)

    def inspect():
        a = Anim(m, "inspect", 4.2)
        # op-rod press check: rotate right side up, ease the op-rod back, look
        a.mv("gun", 0.0, 0.45, pos=(-40, 26, 40), rot=(6, -40, -44), e="inoutsine")
        a.mv("arm_right", 0.25, 0.5, pos=(30, 70, -120), rot=(-30, -20, -30))
        a.grab("arm_right", "bolt", 0.52, 1.5, fade_in=0.03, fade_out=0.06)
        a.key("bolt", 0.0, pos=(0, 0, 0))
        a.key("bolt", 0.55, pos=(0, 0, 0))
        a.key("bolt", 0.78, pos=(0, 0, 34), e="inoutquad")
        a.sound(0.74, "charging_handle_back")
        a.mv("gun", 0.8, 1.1, pos=(-46, 32, 50), rot=(10, -56, -60))
        a.key("bolt", 1.3, pos=(0, 0, 34))
        a.key("bolt", 1.42, pos=(0, 0, 0), e="inoutsine")
        a.sound(1.42, "charging_handle_forward")
        a.mv("arm_left", 1.5, 1.7, pos=(26, 40, 160), rot=(-10, 30, 20))
        a.mv("arm_left", 1.7, 1.76, pos=(20, 40, 166), rot=(-10, 30, 20), e="outquad")
        a.sound(1.75, "tap")
        a.mv("arm_right", 1.5, 1.8, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_left", 1.85, 2.3, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 1.9, 2.6, pos=(-60, 30, 30), rot=(10, 30, 20), e="inoutsine")
        _settle(a, 3.0, 4.15)
        return a

    kk = _kk("bolt", (0, 0, 96), kick=4.6, push=16)
    anims = [
        idle(m), idle(m, "idle_empty", locked={"bolt": (0, 0, 96)}), draw(m, 0.8, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.2, length=0.3, **kk),
        fire_basic(m, "fire_aim", recover=0.17, length=0.27, aim=True, **kk),
        fire_basic(m, "fire_last", recover=0.2, length=0.3, lock_back=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="ak", rock=8, mag_out=60),
        rifle_reload(m, "reload_empty", A, empty=True, style="ak", rock=8, mag_out=60, bolt="bolt", ch="bolt",
                     bolt_travel=(0, 0, 96), ch_travel=(0, 0, 96), bolt_hold_open=True, ch_hand="right"),
        inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, FP)


GUNS = {"fal": fal, "scar_h": scar_h, "svd": svd, "m14ebr": m14ebr}
