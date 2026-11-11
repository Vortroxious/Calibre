"""The Kalashnikov family from one kit, to real dimensions: AKM, AK-47 (milled Type 3), IMI Galil ARM."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode, moving)
from ..templates import rifle_reload
from ..parts import (pistol_grip, trigger_group, curved_mag, barrel, flash_hider_a2, pins, vents, sling_swivel,
                     side_swivel, bipod)
from ..longkit import slot, top_slot, peep, eared_sight, tangent_sight, flip_sight, stock_solid
from ..pistolkit import control


def _inspect(m):
    return Anim(m, "inspect", 1.0)


def _ak(name, *, barrel_out=385.0, milled=False, wood="wood_red", grip="wood_red", cover_ribs=True, swells=True,
        guard_len=188.0, gas_block=-330.0, front_at=-465.0, muzzle="slant", stock="wood", mag="ribbed",
        sight_y=52.0, rear="tangent", galil=False, st="steel_dark"):
    m = new_gun(name)
    body = m["body"]
    zf, zr = -110.0, 150.0                                  # receiver front (trunnion face) and rear
    # ---- receiver
    body.rbox(-16, 16, -30, 10, zf, zr, st, r=2.5 if not milled else 1.5, edges="bottom")
    body.box(-17, 17, -30, 13, zf - 18, zf + 2, st)                                # front trunnion
    if milled:
        for sx in (-1, 1):                                                         # lightening cut over the mag well
            slot(body, sx * 16, -20, -4, -98, -30, depth=0.6)
            body.box(sx * 16 - 0.3, sx * 16 + 0.3, -21, -3, -99, -29, "steel")
    else:
        for sx in (-1, 1):
            body.rbox(sx * 16 - 0.5, sx * 16 + 0.5, -20, -10, -84, -58, "steel", r=3, axis="x", edges="all")   # mag dimple
        pins(body, 16, [(-4, -100), (-22, -100), (2, 132), (-20, 132), (-12, 138)], d=4.5, mat="steel")     # rivets
        body.box(-16.5, 16.5, -2, 0, zf + 6, zr - 4, st)                                                    # rail crease
    pins(body, 16, [(-14, 4), (-16, 26), (-10, 44)], d=4, mat="steel")                # axis pins
    # ---- dust cover
    body.rbox(-15, 15, 10, 23, zf + 4, zr - 2, st, r=6.5, edges="top")
    if cover_ribs:
        for z in (-70, -10, 50):
            body.rbox(-13, 13, 22.4, 24.2, z, z + 14, st, r=0.9, axis="x", edges="top")
        body.box(-4, 4, 23, 24, 80, 136, st)
    body.cyl((0, 15, zr + 1.5), 9, 4, "steel", sides=16)                             # recoil-spring guide button
    # ejection port: the opening the carrier closes
    body.box(8, 16.4, 2, 10.4, -76, 26, "rubber")
    body.box(8, 15.5, 10, 19, -76, 26, "rubber")
    # ---- rear sight block, sights
    body.rbox(-13, 13, 10, sight_y - 12.5 if rear == "tangent" else 30, zf - 64, zf + 4, st, r=4, edges="top")
    if rear == "tangent":
        tangent_sight(body, zf - 60, zf, sight_y - 12.5, st, w=10, h=12.5)
        rear_z = zf - 3
    else:                                                                           # Galil: flip peep at the cover's rear
        body.rbox(-10, 10, 23, sight_y - 12, 104, 140, st, r=3, edges="top")
        flip_sight(body, 122, sight_y - 12, st, w=10, h=15)
        rear_z = 122
    # ---- barrel, gas system, hand guards
    zb = zf - barrel_out
    barrel(body, zf - 18, zb, d=15.5, mat=st)
    body.cyl((0, 0, zf - 40), 22, 44, st)                                            # chamber reinforce
    body.cyl((0, 27, (zf - 64 + gas_block) / 2), 15, zf - 64 - gas_block, "steel")   # gas tube
    zh0, zh1 = zf - 2 - guard_len, zf - 2
    body.rbox(-19, 19, -32, 13, zh0, zh1, wood, r=8, edges="bottom")                 # lower hand guard
    if swells:
        for sx in (-1, 1):
            xs = sorted((sx * 19, sx * 22.5))
            body.rbox(xs[0], xs[1], -26, -4, zh0 + 30, zh1 - 40, wood, r=1.6, axis="z", edges="all")
    body.rbox(-16.5, 16.5, 13, 39, zh0 + 4, zf - 66, wood, r=9, edges="top")         # upper hand guard on the gas tube
    for sx in (-1, 1):
        slot(body, sx * 16.5, 20, 24, zh0 + 20, zf - 86)
    body.box(-20, 20, -33, 14, zh0 - 8, zh0, st)                                     # hand guard retainer
    if galil:
        vents(body, 19, -18, -4, zh0 + 14, zh1 - 14, n=9, fill=0.5)
    else:
        side_swivel(body, -20, -10, zh0 - 4, h=14)
    # gas block (with the bayonet lug) and the front sight
    body.rbox(-9, 9, -11, 36, gas_block - 26, gas_block, st, r=3, edges="top")
    body.box(-4, 4, -19, -11, gas_block - 24, gas_block - 4, st)
    if galil:
        eared_sight(body, gas_block - 13, 36, sight_y - 36 + 3.4, st, w=16, depth=14, lean=4)
        body.path([(gas_block + 60, 34), (gas_block + 66, 62), (gas_block + 150, 62), (gas_block + 156, 34)], 5, 5, st,
                  x=-13)                                                             # carry handle (left)
    else:
        body.rbox(-8, 8, -9, 14, front_at - 14, front_at + 12, st, r=3, edges="all")
        body.box(-4.5, 4.5, 12, 30, front_at - 8, front_at + 6, st)
        eared_sight(body, front_at - 1, 28, sight_y - 28 + 3.6, st, w=15, depth=12, lean=6)
        body.cyl((0, -14, (zh0 + zb) / 2 + 10), 5, zh0 - zb - 30, "steel", sides=8)  # cleaning rod
        body.cyl((0, -14, zb + 18), 7, 6, "steel", sides=8)
    # ---- muzzle
    if muzzle == "slant":
        body.cyl((0, 0, zb - 9), 19, 22, st)
        body.box(-9.6, 9.6, -3, 12, zb - 24, zb - 12, st, rot=(-32, 0, 0), pivot=(0, -6, zb - 20))
        tip = zb - 22
    elif muzzle == "nut":
        body.cyl((0, 0, zb - 5), 18, 14, st)
        tip = zb - 12
    else:
        flash_hider_a2(body, zb + 10, d=20, length=44)
        tip = zb - 34
    body.cyl((0, 0, tip - 0.3), 8.4, 0.6, "rubber", sides=8)
    # ---- controls
    mr = control(body, "mag_release", (0, -32, -34), [(-5, 5, -56, -30, -40, -35, st), (-6, 6, -58, -52, -41, -30, st)],
                 turn=(22, 0, 0))
    trigger_group(m, body, 6, y_top=-30, guard_depth=30, guard_len=74, guard_mat=st)
    pistol_grip(body, 50, top_y=-28, length=92, width=27, depth=34, angle=-16, mat=grip)
    sel = body.bone("selector", pivot=(16, 2, 64))                                  # the big lever on the right
    sel.cyl((17, 2, 64), 12, 2.4, "steel", axis="x", sides=16)
    sel.box(16, 18, -3, 6, -34, 64, "steel")
    sel.box(18, 23, -7, 1, -36, -22, "steel")
    for i, z in enumerate((-28, -40)):
        body.box(16, 16.5, -12 - i * 7, -10 - i * 7, z - 3, z + 3, "white")          # A / R marks
    if galil:
        control(body, "safety", (-16, -26, 44), [(-19, -16, -29, -23, 28, 46, "steel"),
                                                 (-21, -19, -30, -22, 28, 34, "steel")], turn=(-30, 0, 0))
    # ---- bolt carrier with its handle
    bolt = body.bone("bolt", pivot=(18, 6, -50))
    bolt.box(8.4, 15.6, 2.4, 18.6, -74, 24, "steel_light")
    bolt.box(9, 15, 8, 12, -70, -50, "steel")
    if galil:
        bolt.box(15, 22, 8, 14, -56, -44, "steel_light")
        bolt.box(19, 25, 12, 30, -56, -44, "steel_light")                            # upturned handle
    else:
        bolt.box(15, 30, 4, 12, -56, -44, "steel_light")
        bolt.cyl((30, 8, -50), 12, 8, "steel_light", axis="x", sides=16)
    # ---- stock
    stock_b = m["gun"].bone("stock", pivot=(0, 0, zr))
    if stock == "wood":
        if milled:
            stock_b.box(-13, 13, 2, 12, zr - 4, zr + 46, st)                         # tangs
            stock_b.box(-13, 13, -34, -26, zr - 4, zr + 36, st)
        stock_solid(stock_b, 15, [(zr, 8), (zr + 40, 4), (366, -10)], [(zr, -28), (zr + 50, -36), (366, -102)], wood,
                    pad=None, plate=st)
        stock_b.cyl((0, -50, 368.3), 20, 1.2, "steel", sides=16)                     # butt-trap cover
        sling_swivel(stock_b, 0, -88, 320, along="z", drop=9)
        butt = 369
    else:                                                                           # Galil folding tube stock, open
        stock_b.rbox(-16, 16, -30, 12, zr - 2, zr + 16, st, r=3, edges="all")
        stock_b.cyl((16, -9, zr + 8), 9, 46, "steel", axis="y", sides=16)
        stock_b.cyl((0, 2, zr + 136), 15, 240, "steel")
        stock_b.path([(zr + 16, -24), (zr + 110, -58), (zr + 256, -64)], 12, 12, "steel")
        stock_b.rbox(-16, 16, -74, 14, zr + 254, zr + 268, st, r=4, axis="z", edges="all")
        stock_b.box(-17, 17, -78, 16, zr + 268, zr + 276, "rubber")
        butt = zr + 276
    # ---- magazine
    mg = m["gun"].bone("magazine", pivot=(0, -40, -70))
    if mag == "ribbed":
        curved_mag(mg, -26, -104, 68, 235, curve=34, segs=7, width=26, mat="steel_dark", rib_mat="steel", round_d=11.3,
                   round_len=56)
    elif mag == "slab":
        curved_mag(mg, -26, -104, 68, 235, curve=34, segs=7, width=26, mat="steel", rib_mat=None, round_d=11.3,
                   round_len=56)
    else:                                                                           # Galil 35 x 5.56
        curved_mag(mg, -26, -100, 60, 212, curve=24, segs=6, width=23, mat="steel_dark", rib_mat="steel", round_d=9.6,
                   round_len=57)
    if galil:
        bipod(body, gas_block - 4, y=-12, legs_len=205, folded=True, fold="back")
    add_arms(m, right_hand=(8, -84, 62), left_hand=(-12, -52, round((zh0 + zh1) / 2)), right_rot=(34, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, tip - 2), optic=None, under=(0, -34, (zh0 + zh1) / 2) if not galil else None,
                side=(-16, 10, 0) if not galil else None, eject=(16, 8, -30), sight=(0, sight_y, rear_z))
    return m


def _anims(m, mag_a, kick, push, travel=(0, 0, 112), rock=14, selector=(-14, 0, 0), draw_len=0.7, rec=0.15,
           length=0.24):
    cyc = dict(bone="bolt", travel=travel, t_back=0.022, t_fwd=0.06)
    kk = dict(kick=kick, push=push, cycle=cyc)
    return [idle(m), draw(m, draw_len, sound="draw_rifle"),
            fire_basic(m, "fire", recover=rec, length=length, **kk),
            fire_basic(m, "fire_aim", recover=rec * 0.87, length=length * 0.92, aim=True, **kk),
            rifle_reload(m, "reload", mag_a, empty=False, style="ak", rock=rock, mag_out=70),
            rifle_reload(m, "reload_empty", mag_a, empty=True, style="ak", rock=rock, mag_out=70, bolt="bolt", ch="bolt",
                         bolt_travel=travel, ch_travel=travel, bolt_hold_open=False, ch_hand="right"),
            firemode(m, selector_rot=selector), _inspect(m), dry_fire(m)]


def akm():
    """880 mm long, 415 mm barrel, stamped receiver, ribbed cover, slant brake, laminated furniture."""
    m = _ak("akm")
    fp = {"hip": {"pos": [0.118, -0.128, -0.17], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.24}}
    return GunAsset(m, _anims(m, 8.0, (3.4, 0.6, 1.4), 13), fp)


def ak47():
    """Type 3 AK-47: 870 mm long, milled receiver with lightening cuts, smooth cover, slab-sided magazine."""
    m = _ak("ak47", milled=True, wood="wood", grip="wood", cover_ribs=False, swells=False, muzzle="nut",
            mag="slab", st="steel")
    fp = {"hip": {"pos": [0.118, -0.128, -0.17], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.24}}
    return GunAsset(m, _anims(m, 8.0, (3.6, 0.6, 1.4), 13, draw_len=0.72), fp)


def galil():
    """IMI Galil ARM: 987 mm with the stock open, 460 mm barrel, bipod and carry handle, sights on the gas block
    and the rear of the cover."""
    m = _ak("galil", barrel_out=430, milled=True, wood="wood", grip="polymer", cover_ribs=False, swells=False,
            guard_len=232, gas_block=-362, muzzle="birdcage", stock="fold", mag="galil", sight_y=56, rear="flip",
            galil=True)
    fp = {"hip": {"pos": [0.118, -0.128, -0.2], "rot": [0, 4, 0]}, "ads": {"dist": 0.1}}
    return GunAsset(m, _anims(m, 6.0, (2.4, 0.5, 1.1), 10, travel=(0, 0, 100), rock=12, selector=(-26, 0, 0), rec=0.13,
                              length=0.22), fp)


GUNS = {"akm": akm, "ak47": ak47, "galil": galil}
