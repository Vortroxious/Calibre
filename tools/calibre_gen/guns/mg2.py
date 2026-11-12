"""Expansion 3, machine guns: RPD, M240B and MG 34 (belt fed), DP-28 (pan magazine on top) and the Bren (curved
magazine on top, sights offset to the left)."""
import numpy as np

from ..core import HOLD
from ..common import GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, moving
from ..templates import belt_reload
from ..parts import (pistol_grip, trigger_group, barrel, flash_hider_a2, bipod, pins, vents, sling_swivel,
                     side_swivel, curved_mag)
from ..longkit import slot, peep, eared_sight, ring_sight, tangent_sight, drum_sight, stock_solid
from ..pistolkit import control
from ..riflekit import butt_plate
from ..shotkit import crossbolt
from .lmgs import _belt, _belt_feed, LMG_FP
from .modern import _rifle_anims, _fp, _inspect


def _belt_anims(m, kick, push, step, cover_rot=(75, 0, 0), box_drop=(0, -260, 40), ch_travel=(0, 0, 110), rec=0.12,
                length=0.2):
    return [idle(m), draw(m, 1.0, sound="draw_rifle"),
            _belt_feed(fire_basic(m, "fire", kick=kick, push=push, recover=rec, length=length), step),
            _belt_feed(fire_basic(m, "fire_aim", kick=kick, push=push, recover=rec * 0.85, length=length * 0.92,
                                  aim=True), step, sway=2.5),
            belt_reload(m, "reload", False, cover_rot=cover_rot, box_drop=box_drop),
            belt_reload(m, "reload_empty", True, cover_rot=cover_rot, box_drop=box_drop, ch_travel=ch_travel),
            _inspect(m), dry_fire(m)]


def _top_mag(anims, bone="magazine"):
    """rifle_reload takes a magazine out downwards; these guns feed from the top. Mirror every magazine key in the
    horizontal plane so 'down' becomes 'up'."""
    for a in anims:
        for ch, f in (("pos", lambda v: np.array([v[0], -v[1], v[2]])), ("rot", lambda v: np.array([-v[0], v[1], -v[2]]))):
            tr = a.tracks.get((bone, ch))
            if tr:
                tr.keys = [(t, v if v is HOLD or not isinstance(v, np.ndarray) else f(v), e) for t, v, e in tr.keys]
    return anims


def _cover(body, z0, z1, hw, y0, y1, mat, hinge="rear", rail=False):
    """Feed cover as the `cover` bone (hinged at its rear or front edge)."""
    pz = z1 if hinge == "rear" else z0
    c = body.bone("cover", pivot=(0, y1, pz))
    c.rbox(-hw, hw, y0, y1, z0, z1, mat, r=5, edges="top")
    c.box(-hw * 0.7, hw * 0.7, y1 - 0.4, y1 + 0.6, z0 + 10, z1 - 10, "steel")
    if rail:
        c.rail(z0 + 8, z1 - 8, y1, mat="alloy")
    return c


# =================================================================================================
# RPD  (1037 mm long, 520 mm barrel, 100-round belt drum under the receiver, wooden furniture)
# =================================================================================================
def rpd():
    m = new_gun("rpd")
    body = m["body"]
    st, wd = "steel_dark", "wood_red"
    body.rbox(-16, 16, -36, 12, -130, 130, st, r=3, edges="bottom")                   # receiver
    pins(body, 16, [(-24, -120), (-24, 120)], d=4.5, mat="steel")
    body.box(-16.4, -10, -30, -10, -60, -10, "rubber")                                 # ejection (down/left)
    body.rbox(-17, 17, -34, 10, -330, -132, wd, r=8, edges="bottom")                   # hand guard
    body.cyl((0, -20, -420), 14, 180, st)                                              # gas tube
    body.rbox(-8, 8, -30, 8, -520, -500, st, r=3)                                      # gas block
    barrel(body, -130, -616, d=17, mat=st)
    body.cyl((0, 0, -628), 18, 24, st)                                                 # muzzle nut
    body.cyl((0, 0, -640.3), 8, 0.6, "rubber", sides=8)
    body.rbox(-6, 6, 8, 20, -612, -592, st, r=2, edges="top")
    eared_sight(body, -602, 18, 22.6, st, w=14, depth=12, lean=5)                      # post top at 40
    tangent_sight(body, -196, -134, 28, st, w=11, h=12)                                # notch top at 40
    body.rbox(-11, 11, 10, 28, -200, -130, st, r=3, edges="top")
    bipod(body, -560, y=-10, legs_len=220, folded=True, fold="back")
    pistol_grip(body, 50, top_y=-36, length=92, width=26, depth=34, angle=-16, mat=wd)
    trigger_group(m, body, 12, y_top=-36, guard_depth=26, guard_len=64, guard_mat=st)
    crossbolt(body, 46, -46, hw=12, d=7)
    stock = m["gun"].bone("stock", pivot=(0, 0, 130))
    stock_solid(stock, 16, [(130, 10), (383, -6)], [(130, -32), (190, -40), (383, -104)], wd, pad=None, plate=st)
    sling_swivel(stock, 0, -86, 340, along="x", w=18, drop=10, mat=st)
    _cover(body, -120, 60, 15, 12, 26, st, hinge="rear")
    ch = body.bone("charging_handle", pivot=(16, -14, -80))
    ch.box(16, 28, -18, -10, -86, -74, "steel")
    ch.cyl((30, -14, -80), 12, 6, "steel", axis="x", sides=16)
    body.box(16, 16.4, -16, -12, -74, 40, "rubber")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-10, 10, -10, 8, -60, 20, "steel_light")
    box = m["gun"].bone("box", pivot=(0, -36, -70))                                    # 100-round drum
    box.cyl((0, -86, -70), 110, 66, st, axis="x")
    box.cyl((-34, -86, -70), 98, 2, "steel", axis="x")
    box.cyl((34, -86, -70), 98, 2, "steel", axis="x")
    box.rbox(-14, 14, -40, -30, -98, -40, st, r=2)                                     # hanger
    box.box(-36, -32, -100, -72, -78, -62, "steel")                                    # latch
    belt = m["gun"].bone("belt", pivot=(-22, -4, -100))
    _belt(belt, -20, -2, -116, n=6, dx=-4, dy=-7, case="steel", tip="copper", d=11, length=56)
    add_arms(m, right_hand=(8, -94, 78), left_hand=(-10, -44, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -642), eject=(-14, -32, -30), sight=(0, 40, -136))
    anims = _belt_anims(m, (3.0, 0.6, 1.3), 12, (5, 7, 0))
    return GunAsset(m, anims, {"hip": LMG_FP["hip"], "ads": {"dist": 0.26}})


# =================================================================================================
# M240B  (1245 mm long, 630 mm barrel, heat shield, carry handle on the barrel, bag on the left)
# =================================================================================================
def m240b():
    m = new_gun("m240b")
    body = m["body"]
    st, al = "steel_parked", "alloy"
    body.rbox(-20, 20, -44, 18, -170, 180, st, r=4, edges="bottom")                    # receiver
    body.box(-20.4, 20.4, -14, -11, -160, 170, "steel_dark")
    pins(body, 20, [(-32, -160), (-32, 170), (6, 170)], d=5, mat="steel")
    body.rail(-160, -20, 18, mat=al)
    body.rbox(-18, 18, -48, -18, -380, -172, "polymer", r=8, edges="bottom")           # hand guard
    vents(body, 18, -40, -26, -370, -184, n=7, fill=0.5)
    body.cyl((0, -26, -470), 18, 200, st)                                              # gas cylinder
    body.rbox(-10, 10, -38, 10, -582, -560, st, r=3)                                   # gas block
    barrel(body, -170, -780, d=19, mat="steel_dark")
    body.rbox(-15, 15, 4, 16, -560, -180, st, r=6, edges="top")                        # heat shield over the barrel
    vents(body, 15, 6, 12, -550, -190, n=10, fill=0.5)
    flash_hider_a2(body, -780, d=24, length=50)
    body.rbox(-6, 6, 10, 22, -770, -750, st, r=2, edges="top")
    eared_sight(body, -760, 20, 31.6, st, w=14, depth=12, lean=5)                      # post top at 50
    for z in (-430, -330):                                                             # carry handle, laid left
        body.box(-5, 5, 8, 46, z, z + 10, "polymer", rot=(0, 0, 62), pivot=(0, 0, 0))
    body.rbox(-7, 7, 42, 52, -434, -316, "polymer", r=3, rot=(0, 0, 62), pivot=(0, 0, 0))
    bipod(body, -560, y=-38, legs_len=240, folded=True, fold="back")
    pistol_grip(body, 60, top_y=-44, length=96, width=30, depth=38, angle=-16, mat="polymer")
    trigger_group(m, body, 20, y_top=-44, guard_depth=28, guard_len=70, guard_mat=st)
    crossbolt(body, 56, -32, hw=20, d=8)
    stock = m["gun"].bone("stock", pivot=(0, 0, 180))
    stock_solid(stock, 19, [(180, 14), (421, 6)], [(180, -40), (240, -44), (421, -108)], "polymer", pad="rubber",
                pad_th=6, plate=st)
    stock.box(-20, 20, -40, -36, 260, 380, "rubber")
    c = _cover(body, -160, 80, 19, 18, 32, st, hinge="rear", rail=True)
    peep(c, 70, 32, 56, st, w=12, hole=5, depth=3, hole_y=50)
    for sx in (-1, 1):
        c.box(sx * 8 - 1.5, sx * 8 + 1.5, 32, 52, 62, 78, st)
    ch = body.bone("charging_handle", pivot=(20, -16, -120))
    ch.box(20, 34, -22, -10, -126, -114, "steel")
    ch.rbox(32, 40, -26, -6, -128, -112, "polymer", r=2, axis="x")
    body.box(20, 20.4, -18, -14, -112, 40, "rubber")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-12, 12, -14, 10, -80, 20, "steel_light")
    box = m["gun"].bone("box", pivot=(-20, -44, -80))                                  # 100-round soft pouch
    box.rbox(-70, 6, -190, -44, -150, -20, "canvas", r=9)
    box.box(-71, -68, -150, -60, -120, -50, "olive")
    box.rbox(-30, -20, -46, -18, -130, -40, st, r=2)
    belt = m["gun"].bone("belt", pivot=(-26, -6, -100))
    _belt(belt, -24, -4, -120, n=7, dx=-5, dy=-7, case="brass", tip="copper", d=10, length=70)
    add_arms(m, right_hand=(8, -100, 84), left_hand=(-10, -60, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -832), optic=(0, 35, -40), under=None, eject=(14, -44, -40), sight=(0, 50, 70))
    anims = _belt_anims(m, (3.2, 0.7, 1.4), 12, (5, 7, 0), ch_travel=(0, 0, 100))
    return GunAsset(m, anims, LMG_FP)


# =================================================================================================
# MG 34  (1219 mm long, 627 mm barrel in a perforated round jacket, 50-round belt drum on the left)
# =================================================================================================
def mg34():
    m = new_gun("mg34")
    body = m["body"]
    st = "steel_dark"
    body.rbox(-18, 18, -38, 16, -150, 150, st, r=5, edges="top")                       # receiver
    pins(body, 18, [(-28, -140), (-28, 140)], d=4.5, mat="steel")
    body.cyl((0, 0, -165), 40, 30, st)                                                 # jacket collar
    body.cyl((0, 0, -410), 36, 460, st)                                                # round barrel jacket
    for z in range(-620, -190, 30):
        for ang in (0, 45, 90, 135):
            body.box(-18.4, 18.4, -3.5, 3.5, z, z + 14, "rubber", rot=(0, 0, ang), pivot=(0, 0, z + 7))
    body.cyl((0, 0, -650), 40, 18, st)                                                 # front of the jacket
    body.cyl((0, 0, -690), 34, 60, st, d2=24, steps=4)                                 # muzzle booster
    body.cyl((0, 0, -728), 20, 18, st)
    body.cyl((0, 0, -737.3), 10, 0.6, "rubber", sides=8)
    body.rbox(-5, 5, 18, 24, -646, -632, st, r=2, edges="top")                         # folding front sight
    body.box(-1.3, 1.3, 24, 46, -641, -637, st)
    tangent_sight(body, -150, -80, 34, st, w=11, h=12)                                 # notch top at 46
    body.rbox(-11, 11, 14, 34, -154, -76, st, r=3, edges="top")
    bipod(body, -600, y=-18, legs_len=230, folded=True, fold="back")
    # two-part trigger (upper: single shot, lower: automatic) in a steeply raked grip
    pistol_grip(body, 70, top_y=-38, length=92, width=28, depth=36, angle=-16, mat="polymer")
    trigger_group(m, body, 30, y_top=-38, guard_depth=30, guard_len=66, guard_mat=st)
    body.box(-2.4, 2.4, -60, -50, 22, 26, "steel_light")                               # the lower ("D") half
    crossbolt(body, 72, -26, hw=18, d=8)
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    stock_solid(stock, 17, [(150, 10), (434, 0)], [(150, -32), (230, -34), (330, -66), (434, -106)], "polymer",
                pad=None, plate=st)
    stock.rbox(-18, 18, -34, 12, 150, 166, st, r=4)
    _cover(body, -140, 40, 17, 16, 30, st, hinge="rear")
    ch = body.bone("charging_handle", pivot=(18, -6, -100))
    ch.box(18, 30, -12, 0, -106, -94, "steel")
    ch.rbox(28, 36, -20, 8, -108, -92, "steel", r=2.5, axis="x")
    body.box(18, 18.4, -9, -3, -94, 40, "rubber")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-10, 10, -10, 8, -60, 20, "steel_light")
    box = m["gun"].bone("box", pivot=(-18, -38, -60))                                  # 50-round Gurttrommel
    box.cyl((-80, -40, -70), 124, 96, st, axis="z")
    box.cyl((-80, -40, -120), 116, 4, "steel", axis="z")
    box.cyl((-80, -40, -20), 116, 4, "steel", axis="z")
    box.rbox(-30, -18, -32, -8, -110, -30, st, r=2)
    box.rbox(-96, -64, 22, 28, -100, -40, st, r=2)
    belt = m["gun"].bone("belt", pivot=(-24, -4, -100))
    _belt(belt, -22, -2, -120, n=6, dx=-5, dy=-7, case="brass", tip="copper", d=11, length=80)
    add_arms(m, right_hand=(8, -96, 84), left_hand=(-10, -60, 80), right_rot=(34, 14, 6), left_rot=(30, -18, -4))
    add_sockets(m, muzzle=(0, 0, -738), eject=(-14, -38, -30), sight=(0, 46, -82))
    m.warp_z([(-740, -785), (-170, -170)])
    anims = _belt_anims(m, (3.0, 0.7, 1.4), 12, (5, 7, 0))
    return GunAsset(m, anims, {"hip": LMG_FP["hip"], "ads": {"dist": 0.34}})


# =================================================================================================
# DP-28  (1270 mm long, 604 mm barrel, 47-round pan magazine on top, perforated jacket)
# =================================================================================================
def dp28():
    m = new_gun("dp28")
    body = m["body"]
    st, wd = "steel_dark", "wood"
    body.rbox(-16, 16, -36, 14, -150, 120, st, r=4, edges="top")                       # receiver
    pins(body, 16, [(-26, -140), (-26, 110)], d=4.5, mat="steel")
    body.rbox(-15, 15, 14, 24, -80, -4, st, r=3, edges="top")                          # magazine mount
    body.cyl((0, -2, -400), 34, 500, st)                                               # perforated barrel jacket
    for z in range(-630, -170, 34):
        for ang in (0, 60, 120):
            body.box(-17.4, 17.4, -4, 4, z, z + 18, "rubber", rot=(0, 0, ang), pivot=(0, -2, z + 9))
    body.cyl((0, 0, -690), 36, 80, st, d2=20, steps=4)                                 # conical flash hider
    body.cyl((0, 0, -730.3), 14, 0.6, "rubber", sides=8)
    body.rbox(-6, 6, 14, 22, -660, -640, st, r=2, edges="top")                         # front sight with wings
    eared_sight(body, -650, 20, 38.6, st, w=16, depth=12, lean=6)                      # post top at 56
    body.rbox(-12, 12, 14, 30, 60, 116, st, r=3, edges="top")                          # rear sight block
    tangent_sight(body, 60, 116, 30, st, w=12, h=26)                                   # notch top at 56
    bipod(body, -600, y=-20, legs_len=250, folded=True, fold="back")
    body.cyl((0, -26, -400), 12, 300, st)                                              # gas tube / piston
    # trigger group with the grip safety; no pistol grip, the wrist of the stock is gripped
    trigger_group(m, body, 50, y_top=-36, guard_depth=28, guard_len=64, guard_mat=st)
    control(body, "safety", (0, -36, 90), [(-4, 4, -52, -36, 86, 96, "steel")], turn=(20, 0, 0))
    stock = m["gun"].bone("stock", pivot=(0, 0, 120))
    stock_solid(stock, 16, [(120, 8), (180, 0), (436, -14)], [(120, -40), (176, -56), (230, -62), (436, -120)], wd,
                pad=None, plate=st)
    sling_swivel(stock, 0, -96, 380, along="x", w=18, drop=10, mat=st)
    ch = body.bone("charging_handle", pivot=(16, -14, -100))
    ch.box(16, 28, -18, -10, -106, -94, "steel")
    ch.cyl((30, -14, -100), 12, 6, "steel", axis="x", sides=16)
    body.box(16, 16.4, -16, -12, -94, 40, "rubber")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-10, 10, -10, 8, -80, 20, "steel_light")
    control(body, "mag_release", (0, 24, 0), [(-4, 4, 24, 30, -6, 6, "steel")], press=(0, 0, 3))
    mag = m["gun"].bone("magazine", pivot=(0, 24, -42))                                # 47-round pan
    mag.cyl((0, 34, -42), 250, 18, "olive", axis="y")
    mag.cyl((0, 44, -42), 236, 4, st, axis="y", d2=120, steps=3)                       # domed lid
    mag.cyl((0, 47, -42), 60, 4, st, axis="y")
    for k in range(12):                                                                # pressed ribs on the lid
        mag.box(-1.6, 1.6, 43, 45.6, -42 + 64, -42 + 112, "steel", rot=(0, k * 30, 0), pivot=(0, 44, -42))
    mag.round_((0, 22, -42), 77, 11.5)
    add_arms(m, right_hand=(8, -82, 150), left_hand=(-10, -40, -320), right_rot=(32, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -732), eject=(0, -36, -40), sight=(0, 56, 100))
    m.warp_z([(-740, -840), (-160, -160)])                                            # the long jacket
    cyc = dict(bone="bolt", travel=(0, 0, 90), t_back=0.022, t_fwd=0.06)
    anims = _rifle_anims(m, 0.0, (3.0, 0.6, 1.3), 12, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 100),
                         rec=0.13, length=0.22, draw_len=1.0, tilt=(6, -6, -18), tilt_pos=(-20, -10, 24))
    _top_mag(anims)
    m.meta["mag_dir"] = "top"
    return GunAsset(m, anims, {"hip": LMG_FP["hip"], "ads": {"dist": 0.3}})


# =================================================================================================
# Bren Mk II  (1158 mm long, 635 mm barrel, curved 30-round magazine on top, sights offset to the left)
# =================================================================================================
def bren():
    m = new_gun("bren")
    body = m["body"]
    st, wd = "steel_parked", "wood"
    SX = -26.0                                                                         # the sights sit to the left
    body.rbox(-17, 17, -40, 16, -150, 150, st, r=4, edges="top")                       # receiver
    body.box(-17.4, 17.4, -14, -11, -146, 146, "steel_dark")
    pins(body, 17, [(-30, -140), (-30, 140), (6, 140)], d=5, mat="steel")
    body.rbox(-14, 14, 16, 24, -96, -20, st, r=3, edges="top")                         # magazine well
    cover = body.bone("dust_cover", pivot=(0, 24, -20))                                # sliding well cover, open
    cover.rbox(-12, 12, 24, 27, -18, 20, st, r=1.2)
    barrel(body, -150, -620, d=20, mat="steel_dark")
    for z in range(-330, -170, 10):                                                    # cooling fins
        body.cyl((0, 0, z), 30, 4, "steel_dark")
    body.cyl((0, 0, -150), 34, 20, st)                                                 # barrel nut and latch
    body.cyl((0, -22, -420), 18, 280, st)                                              # gas cylinder
    body.rbox(-10, 10, -32, 12, -566, -548, st, r=3)                                   # gas regulator block
    body.cyl((0, 0, -660), 30, 80, st, d2=18, steps=4)                                 # conical flash hider
    body.cyl((0, 0, -700.3), 12, 0.6, "rubber", sides=8)
    for z in (-300, -240):                                                             # barrel carry handle
        body.box(-4, 4, 10, 40, z, z + 8, st)
    body.rbox(-6, 6, 36, 44, -304, -228, wd, r=3)
    # offset front sight on the barrel, drum rear sight on the left of the receiver
    body.rbox(SX - 4, -8, -4, 8, -612, -598, st, r=2)
    eared_sight(body, -604, 8, 24, st, w=12, depth=10, lean=4)                        # (on its arm, left)
    for c in body.cubes[-4:]:
        c.x0 += SX
        c.x1 += SX
        if c.pivot:
            c.pivot = (c.pivot[0] + SX, c.pivot[1], c.pivot[2])
    body.rbox(SX - 8, -17, -4, 18, 100, 140, st, r=3, axis="z")                       # rear sight arm
    sy = drum_sight(body, 120, 18, st, d=18, w=12)
    for c in body.cubes[-8:]:
        c.x0 += SX
        c.x1 += SX
        if c.pivot:
            c.pivot = (c.pivot[0] + SX, c.pivot[1], c.pivot[2])
    bipod(body, -560, y=-22, legs_len=250, folded=True, fold="back")
    pistol_grip(body, 50, top_y=-40, length=96, width=28, depth=36, angle=-16, mat=wd)
    trigger_group(m, body, 12, y_top=-40, guard_depth=28, guard_len=64, guard_mat=st)
    control(body, "selector", (-17, -22, 60), [(-20, -17, -26, -18, 46, 64, "steel")], turn=(-50, 0, 0))
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    stock_solid(stock, 15, [(150, 6), (414, -4)], [(150, -40), (210, -44), (300, -52), (414, -104)], st, pad="rubber",
                pad_th=8, plate=st)
    stock.box(-15.4, 15.4, -40, -20, 180, 380, wd)                                     # wooden cheek pieces
    stock.cyl((0, -60, 330), 10, 50, st, axis="y", sides=16)                           # folded monopod
    stock.box(-12, 12, -40, -36, 400, 440, st)                                         # butt strap (shoulder piece)
    ch = body.bone("charging_handle", pivot=(17, -12, -90))
    ch.box(17, 30, -16, -8, -96, -84, "steel")
    ch.path([(-96, 0), (-80, 0)], 6, 6, "steel", x=32)
    body.box(17, 17.4, -14, -10, -84, 40, "rubber")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-10, 10, -14, 8, -80, 20, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, 24, -58))                                # curved, sticking up
    curved_mag(mag, 26, -96, 70, 180, curve=30, segs=6, width=24, mat="steel_dark", rib_mat="steel", round_d=11.5,
               round_len=70)
    for c in mag.cubes:                                                                # mirror it to point up
        c.y0, c.y1 = 52 - c.y1, 52 - c.y0
        if c.pivot:
            c.pivot = (c.pivot[0], 52 - c.pivot[1], c.pivot[2])
        if any(c.rot):
            c.rot = (-c.rot[0], c.rot[1], -c.rot[2])
    add_arms(m, right_hand=(8, -96, 60), left_hand=(-10, -40, 380), right_rot=(34, 14, 6), left_rot=(30, -18, -4))
    add_sockets(m, muzzle=(0, 0, -702), eject=(0, -40, -40), sight=(SX, sy, 120))
    cyc = dict(bone="bolt", travel=(0, 0, 90), t_back=0.022, t_fwd=0.06)
    anims = _rifle_anims(m, 0.0, (3.0, 0.6, 1.3), 12, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 100),
                         selector=(-50, 0, 0), rec=0.14, length=0.24, draw_len=1.0, tilt=(6, -6, -18),
                         tilt_pos=(-20, -10, 24))
    _top_mag(anims)
    m.meta["mag_dir"] = "top"
    return GunAsset(m, anims, {"hip": LMG_FP["hip"], "ads": {"dist": 0.3}})


GUNS = {"rpd": rpd, "m240b": m240b, "mg34": mg34, "dp28": dp28, "bren": bren}
