"""FN M249 SAW and Kalashnikov PKM - belt fed from ammo boxes."""
import numpy as np
from ..core import Anim
from ..common import GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden
from ..templates import belt_reload, _settle
from ..parts import pistol_grip, trigger_group, barrel, flash_hider_a2, bipod
from ..parts import pins
from ..pistolkit import control
from ..longkit import eared_sight, peep, tangent_sight
from ..shotkit import crossbolt
from ..riflekit import butt_plate

LMG_FP = {"hip": {"pos": [0.13, -0.15, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.1}}


def _belt(bone, x0, y0, z, n=8, dx=-7.0, dy=-9.0, case="brass", tip="copper", d=8.0, length=56.0):
    """A dangling belt: n rounds stepping from the feed tray down to the box."""
    # one child bone per round (feed tray first) so the renderer can drop rounds from the tail as the box empties
    for i in range(n):
        x = x0 + dx * i
        y = y0 + dy * i
        r = bone.bone(f"belt_r{i}", pivot=(x, y, z))
        r.round_((x, y, z), length, d, case=case, tip=tip)
        r.box(x - 3, x + 3, y - d / 2 - 1, y + d / 2 + 1, z + length * 0.15, z + length * 0.3, "steel_dark")
    bone.model.meta["belt_rounds"] = [f"belt_r{i}" for i in range(n)]


def _belt_feed(a, step, sway=4.0):
    """Every shot pulls the belt one link into the gun. The links are identical, so the belt steps up one link and
    snaps back when the animation restarts for the next shot: it reads as a belt running through the feed tray."""
    step = np.asarray(step, dtype=float)
    a.key("belt", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
    a.key("belt", 0.045, pos=step, e="outquad")
    a.key("belt", 0.07, rot=(0, 0, sway), e="outquad")
    a.key("belt", a.length - 0.002, pos=step, rot=(0, 0, 0), e="inoutsine")
    a.key("belt", a.length, pos=(0, 0, 0), rot=(0, 0, 0), e="linear")
    a.shake("belt", "rot", 0.02, min(0.16, a.length - 0.01), (2.5, 0, 3.0), freq=18, seed=3)
    return a


def m249():
    # FN M249 SAW: 1041 mm long, 465 mm barrel, feed cover with rail, heat shield, 200-round box on the left
    m = new_gun("m249")
    body = m["body"]
    st = "steel_dark"
    body.rbox(-22, 22, -40, 12, -160, 130, st, r=3, edges="bottom")                # receiver
    body.rbox(-22, 22, 12, 22, 40, 130, st, r=4, edges="top")
    body.box(-22.4, 22.4, -16, -13, -150, 120, "steel")                            # stamped rib
    pins(body, 22, [(-30, -140), (-30, 110), (2, 104)], d=5, mat="steel")
    body.box(8, 22.3, -30, -10, -80, -20, "rubber")                                # ejection port (bottom right)
    body.rbox(-32, -22, -12, 8, -150, -90, st, r=2)                                # feed tray guide (left)
    body.rbox(-30, -22, -42, -14, -124, -74, st, r=2)                              # rifle-magazine well
    pistol_grip(body, 60, top_y=-40, length=96, width=28, depth=38, angle=-18, mat="polymer")
    trigger_group(m, body, 20, y_top=-40, guard_depth=28, guard_len=70, guard_mat=st)
    crossbolt(body, 50, -32, hw=22, d=8)                                           # push-through safety
    # barrel, heat shield, carry handle, gas system, bipod
    barrel(body, -160, -575, d=20)
    body.cyl((0, 0, -180), 30, 40, st)
    body.rbox(-15, 15, 4, 24, -350, -165, "polymer", r=9, edges="top")             # heat shield
    for z in range(-340, -180, 26):
        body.box(-5, 5, 23.6, 24.4, z, z + 14, "rubber")
    for z in (-262, -182):                                                         # carry handle
        body.box(-5, 5, 22, 56, z, z + 10, "steel")
    body.rbox(-7, 7, 52, 62, -266, -168, "polymer", r=3)
    body.cyl((0, -20, -300), 18, 260, st)                                          # gas cylinder
    body.rbox(-10, 10, -30, 8, -440, -412, st, r=3)                                # gas block and regulator
    body.cyl((0, -20, -446), 14, 12, "steel")
    bipod(body, -400, y=-30, legs_len=220, folded=True, fold="back")
    flash_hider_a2(body, -575, d=22, length=50)
    body.rbox(-6, 6, 8, 20, -548, -528, st, r=2, edges="top")                      # front sight
    eared_sight(body, -538, 18, 23.3, st, w=14, depth=12, lean=5)
    body.rbox(-24, 24, -72, -40, -160, -60, "polymer", r=8, edges="bottom")        # hand guard
    for z in range(-150, -70, 18):
        for sx in (-1, 1):
            body.box(sx * 24 - 0.3, sx * 24 + 0.3, -62, -46, z, z + 8, "rubber")
    # solid polymer stock
    stock = m["gun"].bone("stock", pivot=(0, 0, 130))
    stock.profile(-19, 19, [(130, 12), (403, 10)], [(130, -52), (180, -58), (403, -100)], "polymer")
    butt_plate(stock, 403, -100, 10, 19, "steel_dark", th=3, pad="rubber", pad_th=10)
    stock.box(-19.3, 19.3, -20, -14, 160, 380, "rubber")
    # feed cover hinged at the rear (front lifts)
    cover = body.bone("cover", pivot=(0, 22, 40))
    cover.rbox(-21, 21, 12, 30, -150, 40, st, r=5, edges="top")
    cover.rail(-140, 0, 30, mat="alloy")
    peep(cover, 24, 30, 43, st, w=10, hole=4.5, depth=3, hole_y=38)                # rear sight
    for sx in (-1, 1):
        cover.box(sx * 8 - 1.5, sx * 8 + 1.5, 30, 42, 14, 34, st)
    cover.cyl((12, 35, 24), 9, 5, "steel", axis="x", sides=8)
    # charging handle (right side)
    ch = body.bone("charging_handle", pivot=(22, -10, -120))
    ch.box(22, 36, -14, -4, -126, -114, "steel")
    ch.rbox(32, 40, -18, 0, -128, -112, "polymer", r=2, axis="x")
    body.box(22, 22.4, -11, -7, -112, -10, "rubber")
    # ammo box (200 rd) on the left underside + belt
    box = m["gun"].bone("box", pivot=(-14, -40, -70))
    box.rbox(-46, 18, -150, -40, -130, -20, "polymer_od", r=7)
    box.box(-44, 16, -152, -150, -128, -22, "canvas")
    box.box(-48, -46, -120, -60, -110, -40, "canvas")
    box.box(-40, 12, -40, -37, -126, -24, "polymer")                               # lid
    belt = m["gun"].bone("belt", pivot=(-24, -4, -110))
    _belt(belt, -22, -2, -130, n=6, dx=-5, dy=-7)
    add_arms(m, right_hand=(8, -96, 82), left_hand=(-10, -70, -110), right_rot=(34, 14, 6), left_rot=(30, -18, -4))
    add_sockets(m, muzzle=(0, 0, -626), optic=(0, 33, -60), under=None, eject=(10, -32, -50), sight=(0, 38, 24))


    anims = [idle(m), draw(m, 0.95, sound="draw_rifle"),
             _belt_feed(fire_basic(m, "fire", kick=(2.8, 0.6, 1.2), push=12, recover=0.12, length=0.2), (5, 7, 0)),
             _belt_feed(fire_basic(m, "fire_aim", kick=(2.8, 0.6, 1.2), push=12, recover=0.1, length=0.18, aim=True),
                        (5, 7, 0), sway=2.5),
             belt_reload(m, "reload", False, cover_rot=(75, 0, 0)),
             belt_reload(m, "reload_empty", True, cover_rot=(75, 0, 0), ch_travel=(0, 0, 110)),
             Anim(m, "inspect", 1.0), dry_fire(m)]
    return GunAsset(m, anims, LMG_FP)


def pkm():
    # PKM: 1192 mm long, 645 mm barrel, stamped receiver, skeleton stock, 100-round box hung under the receiver
    m = new_gun("pkm")
    body = m["body"]
    st, wd = "steel_dark", "wood_red"
    body.rbox(-20, 20, -40, 14, -160, 150, st, r=3, edges="bottom")
    for z in range(-150, 140, 48):
        for sx in (-1, 1):
            body.box(sx * 20 - 0.4, sx * 20 + 0.4, -30, 4, z, z + 12, "steel")       # stamped ribs
    pins(body, 20, [(-32, -146), (-32, 136), (4, 120)], d=5, mat="steel")
    body.box(-20.4, -8, -30, -10, -60, -10, "rubber")                              # ejection port (left)
    body.rbox(18, 32, -16, 8, -150, -96, st, r=2)                                  # feed (right side)
    pistol_grip(body, 50, top_y=-40, length=92, width=26, depth=34, angle=-18, mat=wd)
    trigger_group(m, body, 10, y_top=-40, guard_depth=28, guard_len=70, guard_mat=st)
    control(body, "safety", (-20, -30, 52), [(-23, -20, -33, -27, 34, 54, "steel")], turn=(-50, 0, 0))
    barrel(body, -160, -650, d=20)
    body.cyl((0, 0, -178), 30, 36, st)
    for k in range(8):                                                             # fluted rear half
        body.box(-1.2, 1.2, 9.5, 10.4, -420, -200, "rubber", rot=(0, 0, k * 45 + 22.5), pivot=(0, 0, 0))
    for z in (-242, -182):                                                         # carry handle
        body.box(-5, 5, 10, 46, z, z + 10, "steel")
    body.rbox(-7, 7, 42, 52, -246, -168, wd, r=3)
    body.cyl((0, -22, -380), 16, 400, st)                                          # gas tube
    body.rbox(-9, 9, -32, 10, -596, -572, st, r=3)                                 # gas block
    body.cyl((0, -22, -602), 12, 12, "steel")
    body.rbox(-6, 6, 8, 20, -640, -622, st, r=2, edges="top")                      # front sight
    eared_sight(body, -631, 18, 23.3, st, w=14, depth=12, lean=6)
    body.cyl((0, 0, -685), 23, 70, st)                                             # slotted flash hider
    for k in range(4):
        body.box(-11.9, 11.9, -1.6, 1.6, -712, -664, "rubber", rot=(0, 0, k * 45), pivot=(0, 0, 0))
    body.cyl((0, 0, -720.3), 11, 0.6, "rubber", sides=8)
    bp = body.bone("bipod", pivot=(0, -30, -560))
    bipod(bp, -560, y=-30, legs_len=240, folded=True, fold="back")
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))                              # skeleton stock
    stock.profile(-15, 15, [(150, 10), (466, 8)], [(150, -22), (230, -18), (466, -20)], wd)
    stock.profile(-15, 15, [(190, -18), (436, -84)], [(190, -44), (436, -112)], wd)
    stock.rbox(-15, 15, -112, 9, 430, 466, wd, r=4)
    butt_plate(stock, 466, -112, 8, 15, st, th=3)
    stock.box(-12, 12, 9, 11.5, 420, 472, st)                                      # hinged shoulder rest
    # cover hinged at the FRONT (rear lifts)
    cover = body.bone("cover", pivot=(0, 14, -150))
    cover.rbox(-19, 19, 14, 27, -150, 90, st, r=5, edges="top")
    for z in (-40, 20):
        cover.box(-12, 12, 26.6, 27.6, z, z + 40, "steel")
    tangent_sight(cover, -122, -70, 27, st, w=12, h=11)                            # notch top at 38
    ch = body.bone("charging_handle", pivot=(20, -20, -60))
    ch.box(20, 34, -26, -16, -66, -54, "steel")
    ch.cyl((36, -21, -60), 13, 6, "steel", axis="x", sides=16)
    box = m["gun"].bone("box", pivot=(14, -40, -100))
    box.rbox(-4, 44, -170, -40, -160, -40, "olive", r=5)
    box.box(-6, 46, -172, -168, -158, -42, "steel_dark")
    box.box(-4.4, 44.4, -60, -56, -160, -40, "steel_dark")                         # lid seam
    box.box(10, 30, -170, -160, -110, -90, "steel")                                # latch
    for sx in (-4.4, 44.4):
        box.box(sx - 0.4, sx + 0.4, -150, -80, -130, -70, "steel_dark")            # stamped panel
    belt = m["gun"].bone("belt", pivot=(26, -6, -130))
    _belt(belt, 24, -4, -150, n=6, dx=4, dy=-7, case="steel", tip="copper", d=9, length=60)
    add_arms(m, right_hand=(8, -94, 72), left_hand=(-10, -50, -200), right_rot=(34, 14, 6), left_rot=(26, -18, -4))
    add_sockets(m, muzzle=(0, 0, -721), optic=(-22, 6, 0), under=None, eject=(-14, -32, -30), sight=(0, 37.5, -72))


    anims = [idle(m), draw(m, 0.95, sound="draw_rifle"),
             _belt_feed(fire_basic(m, "fire", kick=(3.4, 0.7, 1.4), push=13, recover=0.14, length=0.22), (-4, 7, 0),
                        sway=-4.0),
             _belt_feed(fire_basic(m, "fire_aim", kick=(3.4, 0.7, 1.4), push=13, recover=0.12, length=0.2, aim=True),
                        (-4, 7, 0), sway=-2.5),
             belt_reload(m, "reload", False, cover_rot=(-70, 0, 0), box_drop=(30, -260, 20)),
             belt_reload(m, "reload_empty", True, cover_rot=(-70, 0, 0), box_drop=(30, -260, 20),
                         ch_travel=(0, 0, 120)),
             Anim(m, "inspect", 1.0), dry_fire(m)]
    return GunAsset(m, anims, LMG_FP)


GUNS = {"m249": m249, "pkm": pkm}
