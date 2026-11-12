"""The AR family from one kit, to real dimensions: Colt M4A1, H&K HK416, Colt M16A1, KAC SR-25."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode, moving)
from ..templates import rifle_reload
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, flash_hider_a2, ar_front_sight,
                     ar_stock, muzzle_brake, pins, vents, ejection_port, sling_swivel, side_swivel, bipod)
from ..longkit import slot, peep, selector, button, stock_solid
from ..pistolkit import control

SIGHT_Y = 66.0          # an AR's line of sight sits 2.6 in over the bore


def _inspect(m):
    return Anim(m, "inspect", 1.0)


def _buis(body, z, y_rail, mat="alloy", sy=None):
    """Flip-up rear sight on the top rail: clamp, upright arm, aperture, windage knob. sy = line of sight height."""
    SIGHT_Y = sy if sy is not None else globals()["SIGHT_Y"]
    body.rbox(-10.5, 10.5, y_rail, y_rail + 6, z - 13, z + 13, mat, r=2, edges="top")
    body.box(-11.4, -10.5, y_rail + 1, y_rail + 5, z - 5, z + 5, "steel")
    for sx in (-1, 1):                                    # two slim uprights: the view between them stays open
        xs = sorted((sx * 6.5, sx * 8.5))
        body.box(xs[0], xs[1], y_rail + 6, SIGHT_Y - 5, z - 2.4, z + 2.4, mat)
    peep(body, z, SIGHT_Y - 7, SIGHT_Y + 7, mat, w=17, hole=8.0, depth=2.6, hole_y=SIGHT_Y)       # ghost ring
    body.cyl((11, SIGHT_Y - 10, z), 8, 4, "steel", axis="x", sides=16)


def _flip_front(body, z, y_rail, mat="alloy", sy=None):
    """Flip-up front sight on the top rail: clamp, wings, post up to the line of sight."""
    SIGHT_Y = sy if sy is not None else globals()["SIGHT_Y"]
    body.rbox(-10.5, 10.5, y_rail, y_rail + 6, z - 11, z + 11, mat, r=2, edges="top")
    for sx in (-1, 1):
        xs = sorted((sx * 5, sx * 8.5))
        body.box(xs[0], xs[1], y_rail + 6, SIGHT_Y + 6, z - 3.4, z + 3.4, mat, rot=(0, 0, -sx * 5),
                 pivot=(sx * 6.5, y_rail + 6, z))
    body.box(-4, 4, y_rail + 6, SIGHT_Y - 12, z - 2.6, z + 2.6, mat)
    body.box(-1.1, 1.1, SIGHT_Y - 12, SIGHT_Y, z - 1.1, z + 1.1, "steel_dark")


def _ar(name, *, ul=197.0, hw_low=11.5, hw_up=14.0, barrel_out, barrel_d=17.0, guard="ras", guard_len=178.0,
        front="fsb", fsb_at=None, stock="m4", top="flat", muzzle="a2", mag="stanag30", deflector=True,
        al="alloy", poly="polymer", assist="round", bipod_at=None):
    m = new_gun(name)
    body = m["body"]
    zf = 102.0 - ul                                   # front face of the upper receiver
    big = ul > 205                                    # AR-10 pattern
    mw0, mw1 = zf + 6, zf + (78 if big else 70)       # magazine well
    # ---- lower receiver
    body.box(-hw_low, hw_low, -42, -13, zf + 2, 98, al)
    body.rbox(-hw_low - 1.6, hw_low + 1.6, -66, -13, mw0, mw1, al, r=2.2, axis="y", edges="all")       # magazine well
    body.box(-hw_low - 2.2, hw_low + 2.2, -68, -63, mw0 - 0.6, mw1 + 0.6, al)                          # flared mouth
    body.box(-3, 3, -62, -16, mw0 - 1.6, mw0, al)                                                    # front ridge
    body.rbox(-hw_low, hw_low, -40, -6, 84, 110, al, r=4, edges="bottom")                             # buffer-tube ring boss
    body.box(-hw_low - 0.4, hw_low + 0.4, -15.5, -12.5, zf + 4, 96, "rubber")                          # upper / lower seam
    pistol_grip(body, 36, top_y=-40, length=92, width=27, depth=34, angle=-20, mat=poly)
    trigger_group(m, body, 8, y_top=-42, guard_depth=26, guard_len=64, guard_mat=al)
    pins(body, hw_low, [(-24, zf + 12), (-22, 90), (-30, 10), (-27, 30)], d=5, mat="steel_dark")
    control(body, "bolt_catch", (-hw_low, -16, -16),
            [(-hw_low - 3, -hw_low, -27, -7, -24, -8, "steel_dark"), (-hw_low - 3.8, -hw_low - 3, -13, -8, -23, -9, "steel"),
             (-hw_low - 3.6, -hw_low - 3, -26, -20, -22, -10, "steel")], press=(0, 3.5, 0))
    button(body, "mag_release", (hw_low, -31, -32 if not big else -26), d=9, mat="steel_dark")
    body.box(hw_low, hw_low + 1.4, -37, -25, mw1 - 2, mw1 + 14, al)                                   # release fence
    selector(body, (-hw_low, -26, 44), mat="steel_dark", length=15, side=-1, turn=(-90, 0, 0))
    body.box(hw_low, hw_low + 0.6, -29, -23, 38, 50, "steel_dark")                                    # selector stub (right)
    # ---- upper receiver
    body.rbox(-hw_up, hw_up, -13, 21, zf, 102, al, r=5.5, edges="top")
    z_port0, z_port1 = zf + 44, zf + 100
    ejection_port(body, hw_up, -3, 12, z_port0, z_port1, lip_mat=al)
    dc = body.bone("dust_cover", pivot=(hw_up, -4, (z_port0 + z_port1) / 2))                          # open, hanging
    dc.box(hw_up, hw_up + 1.8, -20, -4, z_port0 - 1, z_port1 + 1, al)
    dc.box(hw_up + 1.8, hw_up + 2.6, -14, -8, z_port0 + 20, z_port1 - 20, "steel_dark")
    moving(m, "dust_cover", rot=(0, 0, 150))
    if deflector:
        body.taper(hw_up, hw_up + 5, z_port1 + 2, z_port1 + 24, 16, 14, 2, 6, al, round=0)
    fa = body.bone("forward_assist", pivot=(hw_up, 9, zf + 142))
    if assist == "round":
        fa.cyl((hw_up + 5, 9, zf + 144), 11, 15, al, axis="x", sides=16)
        fa.cyl((hw_up + 13, 9, zf + 144), 14, 3.4, al, axis="x", sides=16)
        body.box(hw_up - 1, hw_up + 6, 1, 17, zf + 132, zf + 156, al)
    else:                                                                                            # A1 teardrop
        fa.cyl((hw_up + 5, 9, zf + 144), 9, 14, al, axis="x", sides=16)
        fa.box(hw_up + 11, hw_up + 13, 4, 14, zf + 138, zf + 152, al)
        body.box(hw_up - 1, hw_up + 5, 2, 16, zf + 134, zf + 154, al)
    ch = body.bone("charging_handle", pivot=(0, 18, 104))
    ch.box(-6, 6, 15, 21, zf + 96, 104, "steel_dark")
    ch.rbox(-20, 20, 14, 22, 100, 111, "steel_dark", r=2, axis="y", edges="all")
    ch.box(-24, -18, 15, 21, 96, 106, "steel")                                                       # latch
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(1, hw_up - 0.2, -2, 12, z_port0 + 1, z_port1 - 1, "steel_light")
    bolt.box(hw_up - 2.4, hw_up - 0.1, 2, 8, z_port0 + 6, z_port0 + 16, "steel")
    for i in range(4):
        bolt.box(hw_up - 0.6, hw_up, 0, 11, z_port1 - 8 - i * 6, z_port1 - 5 - i * 6, "steel")
    # ---- top: rail with back-up sights, or the fixed carry handle
    if top == "flat":
        body.box(-10.5, 10.5, 21, 26.5, zf + 2, 100, al)
        body.rail(zf + 3, 99, 26.5, mat=al, side="top")
        y_rail = 29.5
        _buis(body, 84, y_rail, al)
        optic = (0, y_rail, -30)
    else:
        body.box(-6, 6, 21, 30, zf + 60, 100, al)
        body.taper(-6, 6, zf + 78, zf + 100, 30, 56, 21, 21, al, round=0)                             # front leg
        body.rbox(-7.5, 7.5, 50, 58, zf + 96, 78, al, r=2.4, edges="top")                             # handle bar
        body.rbox(-8.5, 8.5, 21, 60, 64, 101, al, r=3, edges="top")                                   # rear sight housing
        for sx in (-1, 1):
            xs = sorted((sx * 6, sx * 9))
            body.box(xs[0], xs[1], 60, SIGHT_Y + 7, 80, 92, al)                                         # sight ears
        for sx in (-1, 1):
            slot(body, sx * 6, 31, 48, zf + 104, 62)
        peep(body, 96, 60, SIGHT_Y + 6, al, w=12, hole=7.0, depth=2.6, hole_y=SIGHT_Y)
        body.cyl((11, 58, 86), 12, 5, "steel_dark", axis="x", sides=16)                               # windage drum
        y_rail = None
        optic = None
    # ---- barrel, gas block / front sight, hand guard
    zb = zf - barrel_out                                                                             # bare muzzle
    zg0, zg1 = zf - 12 - guard_len, zf - 12
    barrel(body, zf, zb, d=barrel_d, mat="steel_dark")
    under = side = None
    if guard == "ras":                                    # M4 with the KAC rail system and panels
        body.cyl((0, 0, zf - 6), 36, 12, "steel_dark")
        body.cyl((0, 0, zf - 13), 40, 4, "steel_dark")
        body.rbox(-22, 22, -26, 22, zg0, zg1, al, r=7, edges="all")
        body.rail(zg0 + 3, zg1 - 3, 22, mat=al, side="top")
        body.rail(zg0 + 3, zg1 - 3, -26, mat=al, side="bottom")
        for sx in (-1, 1):                                # ribbed rail covers on the sides
            xs = sorted((sx * 22, sx * 26))
            body.rbox(xs[0], xs[1], -11, 9, zg0 + 6, zg1 - 6, poly, r=1.6, axis="z", edges="all")
            for i in range(9):
                z = zg0 + 12 + i * (guard_len - 24) / 9
                body.box(sx * 26 - 0.3, sx * 26 + 0.45, -9, 7, z, z + 6, "rubber")
        body.box(-23, 23, -27, 23, zg0 - 3, zg0, "steel_dark")
        under, side = (0, -31, (zg0 + zg1) / 2), (-26, -1, (zg0 + zg1) / 2)
        hg_hw, hg_bot = 24, -30
    elif guard == "hk":                                   # HK416 free-floating quad rail
        body.cyl((0, 0, zf - 6), 38, 12, "steel_dark")
        body.rbox(-21.5, 21.5, -30, 24, zg0, zg1, al, r=7, edges="all")
        body.rail(zg0 + 3, zg1 - 3, 24, mat=al, side="top")
        body.rail(zg0 + 3, zg1 - 3, -30, mat=al, side="bottom")
        for sx in (-1, 1):
            body.rail(zg0 + 3, zg1 - 3, -3, x=sx * 21.5, mat=al, side="right" if sx > 0 else "left", width=20)
        vents(body, 19, 9, 15, zg0 + 10, zg1 - 10, n=7, fill=0.5, proud=3.2)
        body.box(-8, 8, -12, 12, zg0 - 20, zg0, "steel_dark")                                         # piston gas block
        under, side = (0, -35, (zg0 + zg1) / 2), (-26, -3, (zg0 + zg1) / 2)
        hg_hw, hg_bot = 24, -34
    elif guard == "a1":                                   # M16A1 triangular hand guards
        body.cyl((0, 0, zf - 6), 34, 12, "steel_dark")
        body.cyl((0, 0, zf - 14), 44, 6, "steel_dark", d2=34, steps=3)                                # delta ring
        body.rbox(-22, 22, -22, -2, zg0, zg1, poly, r=8, edges="bottom")
        body.rbox(-14, 14, -4, 21, zg0, zg1, poly, r=9, edges="top")
        body.box(-22.4, 22.4, -4.5, -2.5, zg0 + 4, zg1 - 4, "rubber")                                 # halves seam
        for i in range(10):
            z = zg0 + 16 + i * (guard_len - 32) / 10
            body.box(-4, 4, 20.6, 21.4, z, z + 8, "rubber")                                           # top vents
            body.box(-6, 6, -22.4, -21.6, z, z + 8, "rubber")                                         # bottom vents
        body.cyl((0, 0, zg0 - 2), 40, 5, "steel_dark")                                                # hand guard cap
        under, side = (0, -24, (zg0 + zg1) / 2), None
        hg_hw, hg_bot = 20, -22
    else:                                                 # SR-25 free-float tube with a full top rail
        body.cyl((0, 0, zf - 8), 44, 16, "steel_dark")
        body.cyl((0, 0, (zg0 + zg1) / 2), 50, guard_len, al)
        body.box(-10.5, 10.5, 21, 26.5, zg0, zg1, al)
        body.rail(zg0 + 3, zg1 - 3, 26.5, mat=al, side="top")
        for ang in (55, 125, 235, 305):
            for i in range(6):
                z = zg0 + 24 + i * (guard_len - 60) / 6
                body.box(-4, 4, 24.4, 25.6, z, z + 24, "rubber", rot=(0, 0, ang), pivot=(0, 0, z + 12))
        body.rail(zg0 + 10, zg0 + 90, -25, mat=al, side="bottom")
        under, side = (0, -30, zg0 + 60), (-26, 0, zg0 + 60)
        hg_hw, hg_bot = 25, -27
    if front == "fsb":
        zs = fsb_at if fsb_at is not None else zg0 - 22
        ar_front_sight(body, zs, base_y=8, h=61)
        body.cyl((0, 14, (zs + zg1) / 2), 5, zg1 - zs, "steel")                                       # gas tube
    else:
        _flip_front(body, zg0 + 16, 29.5 if guard != "hk" else 27, al)
    # ---- muzzle device
    if muzzle == "a2":
        flash_hider_a2(body, zb + 12, d=barrel_d + 4, length=44)
        tip = zb + 12 - 44
    elif muzzle == "a1":
        body.cyl((0, 0, zb - 10), barrel_d + 4, 44, "steel_dark")
        for ang in (0, 120, 240):
            body.box(-1.8, 1.8, barrel_d * 0.2, barrel_d / 2 + 2.4, zb - 32.3, zb - 4, "rubber", rot=(0, 0, ang),
                     pivot=(0, 0, zb - 18))
        body.cyl((0, 0, zb - 32.3), barrel_d * 0.5, 0.6, "rubber", sides=8)
        tip = zb - 32
    else:
        muzzle_brake(body, zb + 10, d=barrel_d + 7, length=56, ports=3, mat="steel_dark")
        tip = zb + 10 - 56
    if bipod_at is not None:
        bipod(body, bipod_at, y=hg_bot, legs_len=200, folded=True, fold="back")
    # ---- stock
    st = m["gun"].bone("stock", pivot=(0, 0, 102))
    if stock == "m4":
        ar_stock(st, 102, mat=poly, ext=44)
        butt = 102 + 120 + 44 + 104
    elif stock == "hk":
        ar_stock(st, 102, mat=poly, ext=44)
        st.rbox(-14, 14, -76, -52, 300, 366, poly, r=5, edges="bottom")                               # storage toe
        st.box(-22.4, 22.4, -80, 20, 370, 374, "rubber")                                              # convex pad
        butt = 374
    elif stock == "mcx":                                  # folding skeleton stock, no buffer tube
        st.rbox(-12, 12, -34, 6, 98, 116, al, r=3)
        st.cyl((12, -14, 107), 9, 42, "steel", axis="y", sides=16)
        st.path([(112, -2), (300, -2)], 12, 9, al)
        st.path([(112, -26), (200, -30), (300, -74)], 9, 7, al)
        st.rbox(-11, 11, 2, 12, 170, 284, poly, r=4, edges="top")                                     # cheek rest
        st.rbox(-14, 14, -84, 12, 298, 312, poly, r=4)
        st.rbox(-15, 15, -86, 14, 312, 320, "rubber", r=5)
        butt = 320
    elif stock == "a1":
        st.cyl((0, -4, 122), 30, 40, al)
        stock_solid(st, 17.5, [(110, 12), (356, 14)], [(110, -30), (150, -40), (356, -98)], poly, pad="rubber",
                    pad_th=8, plate="steel_dark")
        st.box(-9, 9, -84, -6, 366, 366.8, "steel_dark")                                              # trap door
        sling_swivel(st, 0, -84, 318, along="z", drop=9)
        butt = 366
    else:                                                 # fixed precision stock
        st.cyl((0, -4, 126), 32, 48, al)
        stock_solid(st, 18.5, [(112, 14), (364, 16)], [(112, -32), (156, -44), (364, -104)], poly, pad="rubber",
                    pad_th=10, plate="steel_dark")
        st.rbox(-13, 13, 16, 30, 230, 330, poly, r=5, edges="top")                                    # cheek riser
        sling_swivel(st, 0, -90, 326, along="z", drop=9)
        butt = 376
    side_swivel(body, -hw_low, -22, 100, h=14)
    # ---- magazine
    mg = m["gun"].bone("magazine", pivot=(0, -46, (mw0 + mw1) / 2))
    if mag == "stanag30":
        curved_mag(mg, -22, mw0 + 3, 58, 168, curve=10, segs=5, width=21.5, mat="alloy_grey", rib_mat="steel_dark",
                   round_d=9.6, round_len=57)
        mag_a = 4.0
    elif mag == "pmag30":
        curved_mag(mg, -22, mw0 + 3, 58, 172, curve=10, segs=5, width=22.5, mat=poly, rib_mat="polymer_grey",
                   round_d=9.6, round_len=57)
        mag_a = 4.0
    elif mag == "stanag20":
        straight_mag(mg, -22, mw0 + 3, mw0 + 61, 112, width=21.5, mat="alloy_grey", base_mat="steel_dark", round_d=9.6,
                     round_len=57)
        mag_a = 0.0
    else:                                                 # 7.62 x 51, 20 rounds
        straight_mag(mg, -22, mw0 + 3, mw0 + 69, 150, width=25, mat="steel_dark", round_d=12, round_len=70)
        mag_a = 0.0
    add_arms(m, right_hand=(8, -92, 54), left_hand=(-10, hg_bot - 20, round((zg0 + zg1) / 2)), right_rot=(34, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, tip - 2), optic=optic, under=under, side=side,
                eject=(hw_up + 1, 6, (z_port0 + z_port1) / 2), sight=(0, SIGHT_Y, 84 if top == "flat" else 96))
    return m, mag_a


def _anims(m, mag_a, kick=(2.4, 0.4, 1.0), push=11, rec=0.13, length=0.22, draw_len=0.7, travel=(0, 0, 54)):
    cyc = dict(bone="bolt", travel=travel, t_back=0.018, t_fwd=0.052)
    kk = dict(kick=kick, push=push, cycle=cyc)
    anims = [idle(m), idle(m, "idle_empty", locked={"bolt": travel}),
             draw(m, draw_len, sound="draw_rifle"),
             fire_basic(m, "fire", recover=rec, length=length, **kk),
             fire_basic(m, "fire_aim", recover=rec * 0.85, length=length * 0.9, aim=True, **kk),
             fire_basic(m, "fire_last", recover=rec, length=length, lock_back=True, **kk),
             rifle_reload(m, "reload", mag_a, empty=False, style="ar", bolt="bolt", bolt_travel=travel),
             rifle_reload(m, "reload_empty", mag_a, empty=True, style="ar", bolt="bolt", bolt_travel=travel),
             firemode(m, selector_rot=(-90, 0, 0)), _inspect(m), dry_fire(m)]
    return anims


FP = {"hip": {"pos": [0.118, -0.128, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.085}}


def m4a1():
    """838 mm with the stock out, 368 mm (14.5 in) barrel."""
    m, a = _ar("m4a1", barrel_out=348, guard="ras", guard_len=178, front="fsb", stock="m4", muzzle="a2")
    return GunAsset(m, _anims(m, a), FP)


def hk416():
    """HK416 D14.5RS: 900 mm with the stock out, 368 mm barrel, piston gas block, quad rail."""
    m, a = _ar("hk416", barrel_out=348, barrel_d=18, guard="hk", guard_len=228, front="flip", stock="hk",
               muzzle="brake", mag="pmag30")
    return GunAsset(m, _anims(m, a), FP)


def m16a1():
    """986 mm long, 508 mm (20 in) barrel, carry handle, triangular hand guards, 20-round magazine."""
    m, a = _ar("m16a1", barrel_out=488, barrel_d=15.5, guard="a1", guard_len=300, front="fsb", stock="a1",
               top="carry", muzzle="a1", mag="stanag20", deflector=False, assist="teardrop")
    return GunAsset(m, _anims(m, a), {"hip": {"pos": [0.118, -0.135, -0.2], "rot": [0, 4, 0]}, "ads": {"dist": 0.11}})


def sr25():
    """KAC SR-25: AR-10 pattern, 1118 mm long, 610 mm (24 in) free-floated barrel."""
    m, a = _ar("sr25", ul=222, hw_low=12.5, hw_up=15.5, barrel_out=588, barrel_d=19, guard="ff", guard_len=330,
               front="flip", stock="fixed", muzzle="a2", mag="sr25", bipod_at=None)
    return GunAsset(m, _anims(m, a, kick=(4.0, 0.5, 1.2), push=15, rec=0.2, length=0.3, draw_len=0.8,
                              travel=(0, 0, 60)),
                    {"hip": {"pos": [0.12, -0.13, -0.19], "rot": [0, 4, 0]}, "ads": {"dist": 0.09}})


GUNS = {"m4a1": m4a1, "hk416": hk416, "m16a1": m16a1, "sr25": sr25}
