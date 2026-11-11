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
                       peep, rod_stock, selector, paddle, button, stock_solid, tangent_sight)
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
    peep(body, 132, 24, 55, st, w=13, hole=7.0, depth=2.6, hole_y=48)
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
    # SVD Dragunov: 1225 mm long, 620 mm barrel, skeleton stock, PSO-1 on the side rail
    A = 6.0
    st = "steel_dark"
    wd = "wood_red"
    m = new_gun("svd")
    body = m["body"]
    body.rbox(-15, 15, -32, 10, -110, 160, st, r=2.5, edges="bottom")                  # receiver
    body.box(-16, 16, -32, 13, -128, -108, st)                                         # front trunnion
    body.rbox(-14, 14, 10, 22, -104, 158, st, r=6, edges="top")                        # cover
    body.box(-3, 3, 22, 23, -60, 130, st)
    body.box(8, 15.4, 2, 10.4, -70, 44, "rubber")                                      # ejection opening
    body.box(8, 14.5, 10, 19, -70, 44, "rubber")
    pins(body, 15, [(-4, -100), (-22, -100), (-14, 10), (-16, 34), (0, 140)], d=4.5, mat="steel")
    # back-up tangent sight, barrel, gas system, slotted hand guards
    body.rbox(-12, 12, 10, 32, -172, -108, st, r=4, edges="top")
    tangent_sight(body, -168, -112, 32, st, w=10, h=12)
    body.cyl((0, 0, -150), 22, 44, st)
    barrel(body, -128, -636, d=17, mat=st)
    body.cyl((0, 24, -290), 14, 236, "steel")                                          # gas tube
    body.rbox(-18, 18, -28, 36, -362, -114, wd, r=10, edges="all")                     # hand guards
    vents(body, 18, 4, 12, -352, -126, n=6, fill=0.6)
    body.box(-18.4, 18.4, -3, 0, -358, -118, "rubber")
    body.box(-19, 19, -29, 37, -370, -362, st)                                         # retainer
    body.rbox(-9, 9, -10, 32, -424, -398, st, r=3, edges="top")                        # gas block
    body.cyl((0, 24, -430), 11, 10, "steel")
    body.rbox(-8, 8, -9, 14, -668, -640, st, r=3, edges="all")                         # front sight base
    body.box(-4.5, 4.5, 12, 30, -662, -648, st)
    eared_sight(body, -655, 28, 16.5, st, w=15, depth=12, lean=6)
    body.box(-4, 4, -18, -9, -664, -644, st)                                           # bayonet lug
    body.cyl((0, 0, -668), 20, 64, st)                                                 # long slotted flash hider
    for ang in (0, 36, 72, 108, 144):
        body.box(-10.4, 10.4, -1.5, 1.5, -696, -650, "rubber", rot=(0, 0, ang), pivot=(0, 0, -672))
    body.cyl((0, 0, -700.3), 9, 0.6, "rubber", sides=8)
    # controls: paddle catch, guard, the AK-pattern safety lever
    control(body, "mag_release", (0, -34, -26), [(-5, 5, -58, -32, -32, -27, st), (-6, 6, -60, -54, -33, -22, st)],
            turn=(22, 0, 0))
    trigger_group(m, body, 14, y_top=-32, guard_depth=30, guard_len=78, guard_mat=st)
    control(body, "safety", (15, 2, 72), [(15, 17, -3, 6, -18, 72, "steel"), (17, 22, -7, 1, -20, -6, "steel")],
            turn=(-14, 0, 0))
    bolt = body.bone("bolt", pivot=(18, 6, -44))
    bolt.box(8.4, 14.6, 2.4, 18.6, -68, 42, "steel_light")
    bolt.box(14.6, 30, 4, 12, -50, -38, "steel_light")
    bolt.cyl((30, 8, -44), 12, 8, "steel_light", axis="x", sides=16)
    # skeleton thumbhole stock with the cheek rest
    stock = m["gun"].bone("stock", pivot=(0, 0, 160))
    stock.rbox(-14, 14, -6, 12, 160, 516, wd, r=5, edges="all")                        # comb
    stock.rbox(-13, 13, -104, -4, 152, 188, wd, r=5, axis="y", edges="all", rot=(-22, 0, 0), pivot=(0, -6, 170))
    stock.path([(206, -98), (300, -114), (506, -114)], 26, 16, wd)                     # lower bar
    stock.rbox(-14, 14, -122, 12, 496, 520, wd, r=5, edges="all")
    stock.box(-15, 15, -126, 14, 520, 526, st)
    stock.rbox(-13, 13, 12, 30, 300, 420, "leather", r=5, edges="top")                 # cheek rest
    stock.box(-14.4, 14.4, 10, 16, 310, 320, st)
    stock.box(-14.4, 14.4, 10, 16, 400, 410, st)
    side_swivel(stock, -14, -60, 508, h=14)
    side_swivel(body, -9, 10, -412, h=12)
    # PSO-1 on its side-rail bracket
    pso = body.bone("pso1", pivot=(0, 64, 40))
    pso.rbox(-22, -15, -4, 44, -20, 96, st, r=2.4, edges="top")
    pso.box(-22, -6, 40, 50, 0, 80, st)
    pso.cyl((-24, 10, 40), 10, 5, "steel", axis="x", sides=16)
    scope(pso, 40, 64, length=260, tube_d=28, obj_d=38, eye_d=34, mat="steel_dark", mount_y=None, turrets=False)
    pso.cyl((0, 64, -100), 40, 26, st)                                                 # sunshade
    for axis, c in (("y", (0, 64 + 22, 36)), ("x", (22, 64, 36))):
        pso.cyl(c, 24, 16, st, axis=axis)
    pso.rbox(-9, 9, 44, 54, 14, 60, st, r=2.4, edges="bottom")
    pso.cyl((0, 46, 84), 14, 22, st)                                                   # reticle lamp
    pso.cyl((0, 64, 178), 40, 26, "rubber", d2=46, steps=4)                            # eyecup
    pso.cyl((0, 64, 194), 46, 8, "rubber")
    mag = m["gun"].bone("magazine", pivot=(0, -40, -66))
    curved_mag(mag, -28, -100, 70, 112, curve=10, segs=3, width=24, mat="steel_dark", rib_mat="steel", round_d=12.4,
               round_len=76)
    add_arms(m, right_hand=(8, -70, 186), left_hand=(-12, -44, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -702), optic=None, under=(0, -30, -240), eject=(15, 6, -14), sight=(0, 64, 200))
    m.meta["integral_optic"] = {"zoom": 4.0, "reticle": "pso1", "eye": [0, 64, 200]}
    m.warp_z([(0, -140)])                                                              # put the grip where the hand is


    kk = _kk("bolt", (0, 0, 120), kick=5.0, push=16)
    anims = [
        idle(m), draw(m, 0.8, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.24, length=0.36, **kk),
        fire_basic(m, "fire_aim", recover=0.2, length=0.32, aim=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="ak", rock=10, mag_out=60),
        rifle_reload(m, "reload_empty", A, empty=True, style="ak", rock=10, mag_out=60, bolt="bolt", ch="bolt",
                     bolt_travel=(0, 0, 120), ch_travel=(0, 0, 120), bolt_hold_open=False, ch_hand="right"),
        Anim(m, "inspect", 1.0), dry_fire(m),
    ]
    return GunAsset(m, anims, {"hip": {"pos": [0.12, -0.15, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.07}})


# =================================================================================================
# M14 EBR (Sage chassis)
# =================================================================================================
def m14ebr():
    # M14 EBR (Mk 14 Mod 0): 965 mm with the stock out, 457 mm barrel, Sage chassis
    A = 6.0
    al = "alloy"
    m = new_gun("m14ebr")
    body = m["body"]
    st = "steel_parked"
    body.rbox(-14, 14, -14, 16, -100, 120, st, r=3, edges="top")                       # M14 receiver
    body.box(2, 14.4, 8, 16.4, -70, -10, "rubber")                                     # open top of the action
    for sx in (-1, 1):
        body.box(sx * 9 - 1.5, sx * 9 + 1.5, 16, 34, 98, 118, st)                      # rear sight ears
        body.cyl((sx * 13, 22, 108), 12, 5, "steel", axis="x", sides=16)               # windage / elevation knobs
    peep(body, 108, 16, 45, st, w=13, hole=7.0, depth=2.6, hole_y=38)
    # chassis: fore-end with four rails, bridge rail over the action, body under the receiver
    body.rbox(-19, 19, -40, 30, -360, -100, al, r=6, edges="all")
    body.rail(-356, -104, 30, mat=al, side="top")
    body.rail(-352, -120, -40, mat=al, side="bottom")
    for sx in (-1, 1):
        body.rail(-352, -150, -5, x=sx * 19, mat=al, side="right" if sx > 0 else "left", width=20)
    vents(body, 16, 14, 22, -346, -110, n=7, fill=0.5, proud=3.4)
    body.box(-10.5, 10.5, 20, 27, -98, 40, al)
    body.rail(-96, 38, 27, mat=al, side="top")
    for z in (-96, 34):
        body.box(-14.5, 14.5, 10, 24, z, z + 8, al)                                    # bridge legs
    body.rbox(-17, 17, -44, -14, -100, 150, al, r=3, edges="bottom")
    body.box(-16, 16, -50, -44, -104, -40, al)                                         # magazine well lip
    pistol_grip(body, 64, top_y=-42, length=92, width=28, depth=36, angle=-18, mat="polymer")
    trigger_group(m, body, 22, y_top=-44, guard_depth=26, guard_len=62, guard_mat=st)
    sel = body.bone("selector", pivot=(0, -44, -4))
    sel.box(-3, 3, -52, -44, -12, 4, "steel")                                          # safety in the guard
    control(body, "mag_release", (0, -46, -30), [(-5, 5, -64, -44, -34, -29, st), (-6, 6, -66, -60, -35, -24, st)],
            turn=(20, 0, 0))
    pins(body, 17, [(-30, -90), (-30, 130)], d=5, mat="steel_dark")
    # barrel, gas cylinder, long flash suppressor with the front sight
    barrel(body, -360, -547, d=18, mat=st)
    body.cyl((0, -15, -420), 17, 100, st)
    body.cyl((0, -15, -472), 13, 8, "steel")
    body.cyl((0, 0, -578), 22, 66, st)
    for ang in (0, 36, 72, 108, 144):
        body.box(-11.4, 11.4, -1.5, 1.5, -606, -566, "rubber", rot=(0, 0, ang), pivot=(0, 0, -586))
    body.cyl((0, 0, -611.3), 9.5, 0.6, "rubber", sides=8)
    eared_sight(body, -556, 11, 31.4, st, w=18, depth=12, lean=8)
    body.box(-4, 4, -18, -11, -560, -546, st)                                          # bayonet lug
    # operating rod and its handle (right)
    bolt = body.bone("bolt", pivot=(16, 0, -40))
    bolt.box(2, 13.6, 8.4, 16, -66, -14, "steel_light")
    bolt.box(14, 20, -4, 6, -260, -40, st)
    bolt.rbox(18, 30, -6, 10, -72, -56, st, r=3, axis="y", edges="all")
    # telescoping stock with a cheek rest
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    stock.rbox(-17, 17, -44, 12, 146, 176, al, r=4, edges="all")
    rod_stock(stock, 120, 338, 11, -18, "steel", -84, 22, butt_hw=18, rod=8)
    stock.rbox(-13, 13, 6, 24, 230, 320, "polymer", r=5, edges="top")
    stock.box(-4, 4, -18, 8, 250, 262, al)
    stock.box(-4, 4, -18, 8, 296, 308, al)
    side_swivel(body, -19, -10, -340, h=14)
    mag = m["gun"].bone("magazine", pivot=(0, -46, -62))
    curved_mag(mag, -38, -100, 76, 150, curve=6, segs=3, width=26, mat="steel_dark", rib_mat="steel", round_d=12,
               round_len=70)
    add_arms(m, right_hand=(8, -96, 76), left_hand=(-12, -56, -250), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -613), optic=(0, 33, -230), under=(0, -45, -250), side=(-23, -5, -260),
                eject=(15, 12, -40), sight=(0, 38, 108))


    kk = _kk("bolt", (0, 0, 96), kick=4.6, push=16)
    anims = [
        idle(m), idle(m, "idle_empty", locked={"bolt": (0, 0, 96)}), draw(m, 0.8, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.2, length=0.3, **kk),
        fire_basic(m, "fire_aim", recover=0.17, length=0.27, aim=True, **kk),
        fire_basic(m, "fire_last", recover=0.2, length=0.3, lock_back=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="ak", rock=8, mag_out=60),
        rifle_reload(m, "reload_empty", A, empty=True, style="ak", rock=8, mag_out=60, bolt="bolt", ch="bolt",
                     bolt_travel=(0, 0, 96), ch_travel=(0, 0, 96), bolt_hold_open=True, ch_hand="right"),
        Anim(m, "inspect", 1.0), dry_fire(m),
    ]
    return GunAsset(m, anims, FP)


GUNS = {"fal": fal, "scar_h": scar_h, "svd": svd, "m14ebr": m14ebr}
