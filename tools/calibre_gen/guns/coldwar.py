"""Cold War pack: M60, M16A1, IMI Galil ARM, H&K G3A3, Sten Mk II, Colt Python, Skorpion vz. 61, KS-23."""
import math

import numpy as np

from ..core import Anim, HOLD
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden)
from ..templates import rifle_reload, revolver_reload, belt_reload, pump_cycle, tube_reload
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, flash_hider_a2, bipod,
                     ar_front_sight)
from ..common import moving
from ..parts import pins, vents, ejection_port, side_swivel, sling_swivel
from ..longkit import (slot, top_slot, ribs, ring_sight, eared_sight, drum_sight, flip_sight, aperture_sight,
                       peep, rod_stock, selector, paddle, button, stock_solid)
from ..pistolkit import control
from ..riflekit import butt_plate
from ..shotkit import sg_receiver, port_bolt, sg_barrel, sg_tube, forend, sg_butt, crossbolt
from .ar15 import _buis, _flip_front
from .lmgs import _belt, _belt_feed, LMG_FP
from .modern import _rifle_anims, _inspect, _fp


# =================================================================================================
# M60 (belt fed from a 100-round box on the left)
# =================================================================================================
def m60():
    # M60: 1105 mm long, 560 mm barrel, stamped receiver, bipod on the barrel, 100-round bandolier on the left
    m = new_gun("m60")
    body = m["body"]
    st = "steel_parked"
    body.rbox(-20, 20, -42, 16, -150, 150, st, r=4, edges="bottom")           # stamped receiver
    body.box(-20.4, 20.4, -30, 6, -120, -60, "steel_dark")                    # feed tray side plates
    body.box(-20.4, 20.4, -12, -9, -50, 140, "steel_dark")
    pins(body, 20, [(-32, -136), (-32, 134), (4, 130)], d=5, mat="steel")
    body.rbox(-16, 16, -40, 8, -380, -150, "polymer", r=8, edges="bottom")    # fore-end
    for z in range(-366, -170, 26):
        for sx in (-1, 1):
            body.box(sx * 16 - 0.35, sx * 16 + 0.35, -28, -4, z, z + 12, "rubber")
    body.cyl((0, -18, -440), 18, 160, st)                                     # gas cylinder
    body.cyl((0, -18, -526), 22, 12, st)
    barrel(body, -150, -610, d=19, mat="steel_dark")
    for z in (-322, -212):                                                    # carrying handle, laid over to the left
        body.box(-5, 5, 8, 46, z, z + 10, "steel_dark", rot=(0, 0, 62), pivot=(0, 0, 0))
    body.rbox(-7, 7, 42, 52, -326, -198, "steel_dark", r=3, rot=(0, 0, 62), pivot=(0, 0, 0))
    flash_hider_a2(body, -610, d=24, length=50)
    body.profile(-1.6, 1.6, [(-600, 14), (-590, 46), (-584, 46)], [(-600, 9), (-584, 9)], st)    # tall front blade
    body.rbox(-5, 5, 8, 14, -604, -580, st, r=2, edges="top")
    bipod(body, -560, y=-10, legs_len=220, folded=True, fold="back")
    pistol_grip(body, 60, top_y=-42, length=92, width=30, depth=38, angle=-16, mat="polymer")
    trigger_group(m, body, 20, y_top=-42, guard_depth=28, guard_len=66, guard_mat=st)
    control(body, "safety", (-20, -30, 44), [(-23, -20, -33, -27, 28, 46, "steel")], turn=(-50, 0, 0))
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    stock.rbox(-17, 17, -46, 6, 150, 202, "polymer", r=5)
    stock.profile(-18, 18, [(200, 6), (430, -2)], [(200, -46), (430, -106)], "polymer")
    butt_plate(stock, 430, -106, -2, 18, st, th=3, pad="rubber", pad_th=9)
    stock.box(-10, 10, -2, 1, 396, 445, st)                                   # hinged shoulder rest
    stock.cyl((0, -1, 398), 5, 24, "steel", axis="x", sides=8)
    cover = body.bone("cover", pivot=(0, 16, 120))
    cover.rbox(-20, 20, 16, 30, -140, 120, st, r=5, edges="top")
    cover.box(-10, 10, 29.6, 30.6, -120, 40, "steel_dark")
    peep(cover, 96, 30, 51, st, w=10, hole=4.5, depth=3, hole_y=46)           # leaf rear sight
    cover.box(-9, 9, 30, 34, 84, 108, st)
    cover.cyl((10, 36, 96), 9, 5, "steel", axis="x", sides=8)
    ch = body.bone("charging_handle", pivot=(20, -14, -100))
    ch.box(20, 38, -20, -8, -106, -94, "steel")
    ch.rbox(34, 42, -24, -4, -108, -92, "steel", r=2, axis="x")
    body.box(20, 20.4, -16, -12, -92, 30, "rubber")
    box = m["gun"].bone("box", pivot=(-20, -42, -80))                         # 100-round bandolier
    box.rbox(-70, 6, -190, -42, -150, -20, "canvas", r=9)
    box.box(-68, 4, -192, -190, -148, -22, "steel_dark")
    box.box(-71, -68, -150, -60, -120, -50, "olive")
    box.rbox(-30, -20, -44, -16, -130, -40, st, r=2)                          # hanger
    belt = m["gun"].bone("belt", pivot=(-26, -6, -100))
    _belt(belt, -24, -4, -120, n=7, dx=-5, dy=-7, case="brass", tip="copper", d=10, length=70)
    add_arms(m, right_hand=(8, -98, 74), left_hand=(-10, -50, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -661), under=(0, -40, -300), eject=(14, -40, -40), sight=(0, 46, 96))

    anims = [idle(m), draw(m, 1.0, sound="draw_rifle"),
             _belt_feed(fire_basic(m, "fire", kick=(3.2, 0.7, 1.4), push=12, recover=0.12, length=0.2), (5, 7, 0)),
             _belt_feed(fire_basic(m, "fire_aim", kick=(3.2, 0.7, 1.4), push=12, recover=0.1, length=0.18,
                                   aim=True), (5, 7, 0), sway=2.5),
             belt_reload(m, "reload", False, cover_rot=(75, 0, 0)),
             belt_reload(m, "reload_empty", True, cover_rot=(75, 0, 0), ch_travel=(0, 0, 100)),
             _inspect(m), dry_fire(m)]
    return GunAsset(m, anims, LMG_FP)


# =================================================================================================
# H&K G3A3 (roller delayed, slap reload)
# =================================================================================================
def g3a3():
    # H&K G3A3: 1025 mm long, 450 mm barrel
    st = "steel_dark"
    m = new_gun("g3a3")
    body = m["body"]
    P = "polymer"
    body.rbox(-17, 17, -24, 26, -220, 100, st, r=6.5, edges="top")                     # stamped receiver
    body.box(-2.5, 2.5, 26, 26.8, -216, 84, st)
    ribs(body, 17, -16, 12, (-196, -150, -40, 20), 12, "steel")
    ejection_port(body, 17, 0, 14, -106, -60, lip_mat=st)
    body.box(17, 18.6, 1, 13, -60, -54, "steel")
    body.rbox(-17.4, 17.4, -24, 26.4, 98, 106, st, r=6.5, edges="top")                 # end cap
    for sx in (-1, 1):
        body.box(sx * 17.4 - 0.4, sx * 17.4 + 0.4, 2, 14, -30, 16, "steel")            # claw-mount cuts
    # cocking tube, barrel, slim hand guard, ring front sight, drum rear, slotted hider
    body.cyl((0, 16, -372), 24, 306, st)
    body.cyl((0, 16, -526.5), 26, 5, st)
    slot(body, -12, 14, 18, -516, -330)
    slot(body, -12, 18, 24, -342, -330)
    barrel(body, -220, -640, d=18, mat="steel")
    body.box(-9, 9, -10, 28, -540, -524, st)
    ring_sight(body, -532, 28, st, r=11, depth=16)
    drum_sight(body, 66, 26, st, d=22)                                                 # line of sight y = 41
    body.rbox(-20, 20, -36, 4, -512, -236, P, r=8, edges="bottom")
    vents(body, 20, -26, -8, -500, -246, n=12, fill=0.5)
    body.box(-20.4, 20.4, -6, -3, -508, -240, "rubber")
    flash_hider_a2(body, -628, d=22, length=44)
    bipod_lug = body.box(-6, 6, -40, -36, -508, -492, st)
    # trigger housing, grip, guard, selector, magazine well with paddle and button
    body.rbox(-14.5, 14.5, -50, -24, -72, 96, P, r=3, edges="bottom")
    pistol_grip(body, 34, top_y=-46, length=88, width=29, depth=38, angle=-14, mat=P)
    trigger_group(m, body, -20, y_top=-48, guard_depth=27, guard_len=58, guard_mat=P)
    selector(body, (-14.5, -32, 38), mat="steel", length=18, side=-1, turn=(-50, 0, 0))
    body.box(14.5, 15.1, -35, -29, 28, 44, "steel")
    pins(body, 17, [(-16, -88), (-16, 86)], d=5, mat="steel")
    body.box(-16, 16, -56, -24, -152, -96, st)
    body.box(-16.6, 16.6, -56, -53, -153, -95, st)
    paddle(body, (0, -54, -94), mat=st, w=16, h=8, d=10)
    body.cyl((17, -40, -100), 7, 2.4, "steel", axis="x", sides=8)
    ch = body.bone("charging_handle", pivot=(-12, 16, -500))
    ch.box(-26, -11.5, 13, 19, -506, -494, "steel")
    ch.cyl((-30, 16, -500), 14, 14, P, axis="x")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.5, 1, 13, -104, -62, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 100))
    stock.rbox(-16, 16, -26, 24, 104, 140, P, r=6, edges="all")
    stock_solid(stock, 17, [(136, 20), (352, 16)], [(136, -24), (190, -36), (352, -92)], P, pad="rubber", pad_th=8)
    sling_swivel(stock, 0, -80, 300, along="z", drop=9)
    side_swivel(body, -12, 16, -520, h=12)
    mag = m["gun"].bone("magazine", pivot=(0, -50, -124))
    curved_mag(mag, -40, -150, 52, 160, curve=6, segs=3, width=25, mat="steel_dark", rib_mat="steel", round_d=12,
               round_len=70)
    add_arms(m, right_hand=(8, -90, 50), left_hand=(-10, -52, -380), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -674), optic=(0, 27, -40), under=(0, -38, -380), eject=(17, 7, -84),
                sight=(0, 41, 66))

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
    # Sten Mk II: 762 mm long, 197 mm barrel, magazine out to the left, T stock
    m = new_gun("sten")
    body = m["body"]
    st = "steel_parked"
    body.cyl((0, 0, -45), 38, 310, st)                                             # receiver tube -200 .. 110
    body.cyl((0, 0, 112), 40, 6, st)                                               # end cap
    body.cyl((0, 0, 116.5), 14, 3, "steel", sides=8)
    slot(body, 19, -2, 5, -140, 46)                                                # cocking slot (right)
    slot(body, 19, 5, 13, 34, 46)                                                  # safety notch
    ejection_port(body, 19, -15, -5, -186, -146)
    body.cyl((0, 0, -243), 33, 86, st)                                             # barrel nut / hand guard sleeve
    for z in (-276, -256, -236, -216):
        for ang in (0, 60, 120):
            body.box(-16.9, 16.9, -3.5, 3.5, z, z + 11, "rubber", rot=(0, 0, ang), pivot=(0, 0, z + 5))
    body.cyl((0, 0, -205), 36, 10, "steel_dark")
    barrel(body, -286, -355, d=15, mat="steel_dark")
    body.taper(-1.6, 1.6, -200, -182, 19, 27.4, 19, 19, st)                        # triangular front sight
    body.box(-6, 6, 19, 22, 68, 92, st)                                            # rear peep
    peep(body, 86, 21, 34, st, w=12, hole=6.5, depth=3, hole_y=27.4)
    # magazine housing on the left (a collar that turns to close the port)
    body.cyl((0, 0, -166), 44, 46, st)
    body.box(-56, -18, -15, 15, -188, -144, st)
    body.box(-57, -55, -17, 17, -190, -142, st)
    control(body, "mag_release", (-40, 0, -142), [(-48, -30, -6, 6, -143, -138, "steel")], press=(0, 0, 3))
    # trigger housing, guard, cross-bolt selector
    body.chamfer_box(-13, 13, -48, -17, -46, 56, st, ch=3, edges="bottom")
    trigger_group(m, body, 12, y_top=-48, guard_depth=24, guard_len=54, guard_mat=st)
    sel = body.bone("selector", pivot=(13, -32, 30))
    sel.cyl((15.5, -32, 30), 9, 5, "steel", axis="x", sides=8)
    body.cyl((-14, -32, 30), 9, 2, "steel", axis="x", sides=8)
    pins(body, 13, [(-26, -30), (-40, 44)], d=4, mat="steel_dark")
    # T stock: tube strut, grip lug behind the trigger, flat butt plate
    stock = m["gun"].bone("stock", pivot=(0, 0, 110))
    stock.box(-8, 8, -30, -4, 100, 122, st)
    stock.cyl((0, -16, 256), 17, 284, st)
    stock.path([(118, -24), (104, -62), (112, -84)], 8, 9, st)                     # grip lug
    stock.box(-17, 17, -112, 12, 396, 404, st)
    stock.box(-5, 5, -70, -24, 388, 397, st)
    side_swivel(stock, -17, -80, 400, h=14)
    side_swivel(body, -16.5, 0, -280, h=12)
    bolt = body.bone("bolt", pivot=(19, 2, -100))
    bolt.box(2, 18.6, -14, -6, -184, -148, "steel_light")
    bolt.box(18.5, 31, -2, 6, -106, -94, "steel")
    bolt.cyl((34, 2, -100), 13, 7, "steel", axis="x")
    mag = m["gun"].bone("magazine", pivot=(-56, 0, -166))
    mag.box(-262, -56, -12, 12, -184, -148, "steel_dark")                          # 32-round stick, out to the left
    mag.box(-268, -262, -13.5, 13.5, -186, -146, "steel")
    mag.box(-262, -70, 12, 13, -170, -162, "steel_dark")
    mag.box(-262, -70, -13, -12, -170, -162, "steel_dark")
    for i in range(5):
        x = -240 + i * 36
        mag.box(x, x + 3.5, -12.4, 12.4, -151, -147.6, "rubber")
        mag.box(x + 0.6, x + 2.9, -4, 4, -148.2, -147.3, "brass")
    mag.round_((-52, 0, -166), 29, 9.6)
    add_arms(m, right_hand=(8, -70, 60), left_hand=(-12, -20, -246), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -357), eject=(19, -10, -166), sight=(0, 27.4, 86))

    cyc = dict(bone="bolt", travel=(0, 0, 80), t_back=0.018, t_fwd=0.05)
    anims = _rifle_anims(m, 0.0, (1.6, 0.4, 0.9), 7, "smg", cyc, ch="bolt", ch_travel=(0, 0, 80), mag_sound="smg",
                         selector=(0, 0, 0), rec=0.1, length=0.18, tilt=(10, 10, 10), tilt_pos=(10, 16, 24))
    fm = next(a for a in anims if a.name == "firemode")
    fm.key("selector", 0.2, pos=(0, 0, 0))
    fm.key("selector", 0.26, pos=(-8, 0, 0), e="outquad")
    fm.key("selector", 0.55, pos=(-8, 0, 0))
    _side_mag(anims)
    return GunAsset(m, anims, _fp(pos=(0.11, -0.115, -0.21), ads=0.24))


# =================================================================================================
# Skorpion vz. 61 (machine pistol, wire stock folded over the top)
# =================================================================================================
def skorpion():
    # Skorpion vz. 61: 270 mm with the wire stock folded over the top (517 open), 115 mm barrel
    m = new_gun("skorpion")
    body = m["body"]
    st = "steel_dark"
    body.chamfer_box(-14, 14, -22, 16, -170, 70, st, ch=3.5, edges="top")           # receiver
    for sx in (-1, 1):
        slot(body, sx * 14, 2, 9, -150, -84)                                       # cocking-knob slots
    top_slot(body, 16, -8, 8, -92, -54)                                            # the Skorpion ejects straight up
    barrel(body, -170, -198, d=12.5, mat="steel")
    body.cyl((0, 0, -174), 18, 8, st)
    eared_sight(body, -156, 16, 15, st, w=14, depth=12, lean=6)
    flip_sight(body, 44, 16, st, w=9, h=16)
    # lower frame, magazine housing, wooden grip, guard
    body.chamfer_box(-13, 13, -40, -22, -96, 70, st, ch=3, edges="bottom")
    body.box(-12, 12, -52, -22, -76, -42, st)
    button(body, "mag_release", (-13, -34, -38), d=8, mat="steel")
    pistol_grip(body, 44, top_y=-38, length=80, width=25, depth=32, angle=-10, mat="wood_red")
    trigger_group(m, body, 4, y_top=-40, guard_depth=24, guard_len=52, guard_mat=st)
    selector(body, (-13, -28, 40), mat="steel", length=13, side=-1, marks=False, turn=(-60, 0, 0))
    pins(body, 14, [(-10, -150), (-10, 56), (-32, 12)], d=4, mat="steel")
    side_swivel(body, -14, 0, 60, h=12)
    # wire stock folded forward over the receiver: hinge at the rear, two arms, butt loop over the front sight
    stock = m["gun"].bone("stock", pivot=(0, 12, 66))
    stock.box(-15, 15, 4, 18, 62, 74, st)
    for sx in (-1, 1):
        stock.path([(66, 12), (40, 24), (-150, 26), (-176, 14)], 3.6, 3.6, "steel", x=sx * 12.5)
    stock.box(-14.5, 14.5, 10, 14, -180, -174, "steel")
    stock.box(-14.5, 14.5, -8, 12, -182, -178, "steel", rot=(-14, 0, 0), pivot=(0, 12, -178))
    bolt = body.bone("bolt", pivot=(0, 6, -110))
    bolt.box(-7.5, 7.5, 9, 16.4, -90, -56, "steel_light")
    for sx in (-1, 1):
        bolt.cyl((sx * 17, 5.5, -112), 12, 6, "steel_light", axis="x")
        bolt.cyl((sx * 20.3, 5.5, -112), 8, 1, "steel_dark", axis="x", sides=8)
    mag = m["gun"].bone("magazine", pivot=(0, -40, -59))
    curved_mag(mag, -30, -74, 28, 132, curve=26, segs=5, width=17, mat="steel_dark", rib_mat="steel", round_d=8.4,
               round_len=25)
    add_arms(m, right_hand=(6, -82, 50), left_hand=(-12, -84, -62), right_rot=(34, 16, 6), left_rot=(30, -24, -4))
    add_sockets(m, muzzle=(0, 0, -200), eject=None, sight=(0, 29, 44))

    cyc = dict(bone="bolt", travel=(0, 0, 40), t_back=0.01, t_fwd=0.03)
    anims = _rifle_anims(m, 4.0, (1.4, 0.4, 0.8), 6, "smg", cyc, ch="bolt", ch_travel=(0, 0, 44), mag_sound="smg",
                         selector=(-60, 0, 0), rec=0.09, length=0.15, draw_len=0.55)
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
    # KS-23: 23 mm pump carbine, 1040 mm long, 510 mm rifled barrel, three-round tube, wooden butt
    m = new_gun("ks23")
    body = m["body"]
    st = "steel_dark"
    roof = sg_receiver(body, -120, 100, st, hw=20, y0=-36, y1=22, port=(-90, -10), load=(-110, -20), port_y=-8)
    sg_barrel(body, -120, -638, d=30, y=4, mat=st, bead=False)
    body.cyl((0, 4, -644), 34, 12, st)
    sg_tube(body, -120, -480, y=-26, d=26, mat=st, ring=-450, barrel_y=4, barrel_d=30)
    body.rbox(-4, 4, 18, 26, -634, -614, st, r=2, edges="top")                 # front blade
    body.box(-1.3, 1.3, 26, 34, -626, -622, st)
    body.box(-9, 9, 22, 26, 58, 82, st)                                         # rear notch
    for sx in (-1, 1):
        body.box(sx * 5.4 - 3.6, sx * 5.4 + 3.6, 26, 34.5, 68, 74, st)
    trigger_group(m, body, 40, y_top=-36, guard_depth=28, guard_len=66, guard_mat=st)
    crossbolt(body, 70, -48)
    sg_butt(body, "wood", 100, 390, top0=18, bot0=-36, comb=-6, heel=-26, toe=-118, hw=(16, 18))
    pump = m["gun"].bone("pump", pivot=(0, -26, -280))
    forend(pump, -400, -220, "wood", hw=26, y0=-54, y1=-6, grooves=10, groove_mat="wood_red", bar_y=-12)
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    port_bolt(bolt, (-90, -10), hw=20, roof=roof)
    _big_shells(m)
    add_arms(m, right_hand=(8, -88, 128), left_hand=(-10, -46, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -651), eject=(20, 4, -50), sight=(0, 34, 70))

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(11, 1.0, 2.4), push=30, recover=0.4, length=0.5),
             fire_basic(m, "fire_aim", kick=(11, 1.0, 2.4), push=30, recover=0.36, length=0.46, aim=True),
             pump_cycle(m, "cycle", travel=(0, 0, 100), length=0.68),
             pump_cycle(m, "cycle_aim", travel=(0, 0, 100), length=0.68, aim=True),
             *tube_reload(m), _inspect(m), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, _fp(pos=(0.12, -0.13, -0.2), rot=(0, 3.5, 0), ads=0.13))


GUNS = {"m60": m60, "g3a3": g3a3, "sten": sten, "skorpion": skorpion, "ks23": ks23}
