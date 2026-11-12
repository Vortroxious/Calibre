"""Expansion 3, WWII II: M1 Carbine, SVT-40, Gewehr 43, FG 42, M3 Grease Gun, PPS-43 (real dimensions, kits)."""
from ..common import GunAsset, new_gun, add_arms, add_sockets, moving
from ..parts import (trigger_group, barrel, straight_mag, curved_mag, pistol_grip, pins, vents, sling_swivel,
                     side_swivel, ejection_port, bipod, muzzle_brake)
from ..longkit import slot, peep, aperture_sight, eared_sight, ring_sight, tangent_sight, flip_sight, stock_solid
from ..pistolkit import control
from ..riflekit import mil_stock, line_y, butt_plate, band, handguard, stock as _stock
from ..shotkit import crossbolt
from .modern import _rifle_anims, _fp
from .coldwar import _side_mag


def _carrier(m, z0, z1, x, y0, y1, handle_z, side=1, knob=12.0, mat="steel"):
    """Operating rod / carrier on the side of the receiver with its handle, as the `bolt` bone."""
    b = m["body"].bone("bolt", pivot=(x, (y0 + y1) / 2, handle_z))
    xs = sorted((x, x + side * 4.5))
    b.box(xs[0], xs[1], y0, y1, z0, z1, mat)
    hx = sorted((x + side * 4.5, x + side * 13))
    b.box(hx[0], hx[1], y0 + 1, y1 - 1, handle_z - 5, handle_z + 5, mat)
    b.cyl((x + side * 16, (y0 + y1) / 2, handle_z), knob, 7, mat, axis="x", sides=16)
    return b


# =================================================================================================
# M1 Carbine  (904 mm long, 458 mm barrel, 15-round magazine, op-slide handle on the right)
# =================================================================================================
def m1carbine():
    m = new_gun("m1carbine")
    body = m["body"]
    st, wd = "steel_parked", "wood"
    body.rbox(-12, 12, -18, 13, -96, 64, st, r=4.5, edges="top")                      # receiver
    body.box(9, 12.4, -2, 10, -70, -20, "rubber")                                      # ejection port
    pins(body, 12, [(-12, -88), (-12, 56)], d=4, mat="steel")
    ys = aperture_sight(body, 40, 13, st, w=15, h=19.5, hole=4.5)                      # line of sight at 28
    barrel(body, -96, -520, d=15, mat=st)
    body.cyl((0, 0, -120), 20, 48, st)                                                 # chamber / gas cylinder area
    body.cyl((0, -9, -150), 13, 36, st)                                                # gas piston housing
    body.rbox(-6, 6, 6, 10, -514, -496, st, r=2, edges="top")
    eared_sight(body, -505, 8, 22.6, st, w=14, depth=12, lean=5)                        # post top at 28
    top, bot = mil_stock(body, wd, nose=-332, butt=(380, -30, -116), action=(-96, 64), fore=(0, -22, -30),
                         belly=-42, wrist=(-14, -52), hw=(14, 15.5, 13.5, 16))
    butt_plate(body, 380, -116, -30, 16, st, th=3.5)
    handguard(body, -320, -96, 11, 0, 13, wd, caps=None)
    band(body, -330, line_y(bot, -330) - 0.8, 14, 15, st, w=14, swivel=True)
    body.box(-4, 4, line_y(bot, -330) - 10, line_y(bot, -330), -346, -324, st)       # bayonet lug (type 3 band)
    for sx in (-1, 1):                                                                 # sling slot with the oiler
        slot(body, sx * 16, -80, -66, 250, 290)
    trigger_group(m, body, 30, y_top=-42, guard_depth=24, guard_len=56, guard_mat=st)
    crossbolt(body, -2, -54, hw=6, d=6)                                                # safety in the guard front
    control(body, "mag_release", (12, -36, -6), [(12, 15, -40, -32, -12, 0, "steel")], press=(-1.6, 0, 0))
    body.box(-10, 10, -48, -42, -70, -10, st)                                          # magazine well
    _carrier(m, -260, -40, 12, -8, 0, -46, side=1, knob=10)
    mag = m["gun"].bone("magazine", pivot=(0, -46, -40))
    straight_mag(mag, -42, -68, -12, 92, width=17, mat="steel_dark", round_d=9.2, round_len=42)
    add_arms(m, right_hand=(8, -78, 100), left_hand=(-14, -40, -250), right_rot=(32, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -522), eject=(12, 6, -40), sight=(0, 28, 40))
    cyc = dict(bone="bolt", travel=(0, 0, 70), t_back=0.022, t_fwd=0.06)
    anims = _rifle_anims(m, 0.0, (3.0, 0.5, 1.2), 11, "ar", cyc, ch="bolt", ch_travel=(0, 0, 70), lock=False)
    return GunAsset(m, anims, _fp(pos=(0.118, -0.128, -0.2), rot=(0, 3.5, 0), ads=0.28))


# =================================================================================================
# SVT-40  (1226 mm long, 625 mm barrel with its six-port brake, 10-round box)
# =================================================================================================
def svt40():
    m = new_gun("svt40")
    body = m["body"]
    st, wd = "steel_dark", "wood_red"
    body.rbox(-13, 13, -30, 14, -100, 120, st, r=4, edges="top")                       # receiver
    body.box(9, 13.4, -2, 10, -70, 0, "rubber")                                        # ejection port
    pins(body, 13, [(-20, -92), (-20, 112)], d=4, mat="steel")
    body.cyl((0, 0, -134), 24, 68, st)                                                 # chamber reinforce
    body.rbox(-11, 11, 6, 18, -186, -112, st, r=3, edges="top")                        # rear sight base
    tangent_sight(body, -182, -116, 18, st, w=10, h=10)                                # notch top at 28
    barrel(body, -100, -762, d=16, mat=st)
    body.cyl((0, 0, -792), 22, 60, st)                                                 # six-port muzzle brake
    for z in range(-816, -770, 8):
        for sx in (-1, 1):
            body.box(sx * 11 - 0.4, sx * 11 + 0.4, -4, 4, z, z + 4, "rubber")
    body.cyl((0, 0, -822.3), 8, 0.6, "rubber", sides=8)
    ring_sight(body, -760, 8, st, r=7, depth=14, post_h=13, base_w=12)                 # hooded front sight
    body.rbox(-8, 8, -9, 26, -652, -628, st, r=3, edges="top")                         # gas block
    body.cyl((0, 20, -640), 14, 60, st)                                                # gas regulator
    body.cyl((0, 20, -604), 10, 14, "steel")
    top, bot = mil_stock(body, wd, nose=-570, butt=(400, -34, -126), action=(-100, 120), fore=(2, -28, -38),
                         belly=-50, wrist=(-14, -60), grip=False, hw=(15, 17, 14.5, 17))
    butt_plate(body, 400, -126, -34, 17, st, th=4)
    body.rbox(-14, 14, -2, 22, -570, -330, st, r=8, edges="top")                       # perforated steel cover
    for z in range(-560, -340, 22):
        for sx in (-1, 1):
            body.box(sx * 14 - 0.4, sx * 14 + 0.4, 4, 14, z, z + 10, "rubber")
    handguard(body, -326, -110, 13, 2, 17, wd)
    band(body, -330, line_y(bot, -330) - 0.8, 22.4, 15.5, st, w=10, swivel=True)
    band(body, -572, line_y(bot, -572) - 0.8, 22.4, 15.5, st, w=12)
    body.cyl((10, -14, -664), 5, 190, "steel_light")                                   # cleaning rod (right)
    trigger_group(m, body, 40, y_top=-50, guard_depth=24, guard_len=58, guard_mat=st)
    control(body, "safety", (0, -50, 72), [(-3, 3, -62, -50, 70, 76, "steel")], turn=(-30, 0, 0))
    control(body, "mag_release", (0, -50, 4), [(-5, 5, -60, -50, 2, 8, "steel")], turn=(-18, 0, 0))
    _carrier(m, -70, 20, 13, -6, 6, 10, side=1, knob=12)
    side_swivel(body, -17, -76, 320, h=16)
    mag = m["gun"].bone("magazine", pivot=(0, -50, -40))
    straight_mag(mag, -46, -78, -6, 60, width=24, mat="steel_dark", round_d=11.5, round_len=77)
    add_arms(m, right_hand=(10, -74, 168), left_hand=(-14, -46, -360), right_rot=(30, 12, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -823), eject=(13, 6, -40), sight=(0, 28, -118))
    cyc = dict(bone="bolt", travel=(0, 0, 90), t_back=0.022, t_fwd=0.062)
    anims = _rifle_anims(m, 0.0, (4.4, 0.6, 1.4), 15, "ar", cyc, ch="bolt", ch_travel=(0, 0, 90), rec=0.2, length=0.3,
                         draw_len=0.85)
    return GunAsset(m, anims, _fp(pos=(0.12, -0.14, -0.2), rot=(0, 3, 0), ads=0.3))


# =================================================================================================
# Gewehr 43  (1117 mm long, 546 mm barrel, gas piston over the barrel, cocking handle on the left)
# =================================================================================================
def g43():
    m = new_gun("g43")
    body = m["body"]
    st, wd = "steel_dark", "wood"
    body.rbox(-13, 13, -30, 15, -100, 110, st, r=4, edges="top")                       # receiver
    body.box(9, 13.4, -2, 10, -68, 4, "rubber")                                        # ejection port
    body.box(13, 16.5, -8, 6, -60, 70, st)                                             # ZF 4 scope rail (right)
    for z in (-50, 0, 50):
        body.box(16.5, 17.2, -4, 2, z, z + 10, "rubber")
    pins(body, 13, [(-20, -90), (-20, 102)], d=4, mat="steel")
    body.rbox(-11, 11, 6, 18, -170, -104, st, r=3, edges="top")
    tangent_sight(body, -166, -108, 18, st, w=10, h=10)                                # notch top at 28
    barrel(body, -100, -690, d=17, mat=st)
    body.cyl((0, 0, -701), 19, 22, st)                                                 # muzzle nut
    body.cyl((0, 0, -712.3), 8, 0.6, "rubber", sides=8)
    ring_sight(body, -684, 8.5, st, r=7, depth=14, post_h=12.5, base_w=12)
    body.cyl((0, 19, -440), 16, 300, st)                                               # gas cylinder over the barrel
    body.rbox(-9, 9, 4, 28, -604, -584, st, r=3, edges="top")                          # gas block
    top, bot = mil_stock(body, wd, nose=-480, butt=(401, -34, -128), action=(-100, 110), fore=(2, -28, -38),
                         belly=-50, wrist=(-14, -60), grip=True, hw=(15, 17, 14.5, 17))
    butt_plate(body, 401, -128, -34, 17, st, th=4)
    handguard(body, -470, -300, 13, 2, 14, wd)
    band(body, -474, line_y(bot, -474) - 0.8, 26, 15.5, st, w=12, swivel=True)
    trigger_group(m, body, 40, y_top=-50, guard_depth=24, guard_len=58, guard_mat=st)
    control(body, "safety", (0, 8, 112), [(-4, 4, 4, 14, 108, 118, "steel")], turn=(0, 0, -80))
    control(body, "mag_release", (13, -40, 4), [(13, 16, -46, -36, -2, 10, "steel")], press=(-1.6, 0, 0))
    _carrier(m, -70, 30, -13, -4, 8, 12, side=-1, knob=12)                             # handle on the left
    sling_swivel(body, 0, line_y(bot, 320), 320, along="x", w=20, drop=11, mat=st)
    mag = m["gun"].bone("magazine", pivot=(0, -50, -40))
    straight_mag(mag, -46, -80, -6, 62, width=25, mat="steel_dark", round_d=12, round_len=80)
    add_arms(m, right_hand=(10, -74, 168), left_hand=(-14, -46, -330), right_rot=(30, 12, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -714), eject=(13, 6, -40), sight=(0, 28, -110))
    cyc = dict(bone="bolt", travel=(0, 0, 92), t_back=0.022, t_fwd=0.062)
    anims = _rifle_anims(m, 0.0, (4.6, 0.6, 1.4), 15, "ar", cyc, ch="bolt", ch_travel=(0, 0, 92), rec=0.2, length=0.3,
                         draw_len=0.85)
    return GunAsset(m, anims, _fp(pos=(0.12, -0.14, -0.2), rot=(0, 3, 0), ads=0.3))


# =================================================================================================
# FG 42 (type 2)  (1060 mm long, 525 mm barrel, magazine from the left, bipod, steep pistol grip)
# =================================================================================================
def fg42():
    m = new_gun("fg42")
    body = m["body"]
    st, wd = "steel_parked", "wood"
    body.rbox(-15, 15, -32, 16, -130, 150, st, r=4, edges="top")                       # stamped receiver
    body.box(-15.4, 15.4, -14, -11, -126, 146, "rubber")
    pins(body, 15, [(-24, -120), (-24, 140), (6, 140)], d=4.5, mat="steel")
    ejection_port(body, 15, -2, 10, -40, 10, lip_mat=st)
    body.rbox(-17, 17, -36, 18, -330, -130, wd, r=9, edges="bottom")                   # wooden hand guard
    vents(body, 17, -22, -6, -320, -140, n=6, fill=0.5)
    barrel(body, -130, -612, d=16, mat="steel_dark")
    muzzle_brake(body, -612, d=22, length=52, ports=3)
    body.box(-3, 3, -26, -14, -560, -430, "steel")                                     # folded bayonet spike
    body.rbox(-6, 6, 10, 20, -596, -576, st, r=2, edges="top")                         # folding front sight
    body.box(-1.3, 1.3, 20, 44, -588, -584, st)
    body.rbox(-9, 9, 16, 24, 110, 146, st, r=3, edges="top")                           # diopter rear sight
    peep(body, 128, 24, 51, st, w=12, hole=5, depth=3, hole_y=44)
    for sx in (-1, 1):
        body.box(sx * 7.5 - 1.5, sx * 7.5 + 1.5, 24, 46, 120, 136, st)
    bipod(body, -360, y=-6, legs_len=230, folded=True, fold="back")
    # steeply raked pistol grip and the straight-line stock
    pistol_grip(body, 30, top_y=-32, length=96, width=26, depth=34, angle=-8, mat=wd)
    trigger_group(m, body, -10, y_top=-32, guard_depth=26, guard_len=58, guard_mat=st)
    control(body, "selector", (-15, -16, 20), [(-18, -15, -19, -13, 6, 22, "steel")], turn=(-50, 0, 0))
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    stock_solid(stock, 16, [(150, 12), (380, 10)], [(150, -26), (230, -40), (380, -98)], wd, pad=None, plate=st)
    sling_swivel(stock, 0, -84, 340, along="x", w=20, drop=10, mat=st)
    # magazine well on the left: the 20-round box sticks out sideways
    body.rbox(-42, -15, -14, 12, -82, -38, st, r=3, axis="x")
    control(body, "mag_release", (-32, 12, -36), [(-38, -26, 12, 16, -38, -34, "steel")], press=(0, -1.6, 0))
    ch = body.bone("charging_handle", pivot=(15, 6, -90))
    ch.box(15, 26, 2, 10, -96, -84, "steel")
    ch.cyl((28, 6, -90), 12, 6, "steel", axis="x", sides=16)
    body.box(15, 15.4, 4, 8, -84, 40, "rubber")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 14.6, -1, 9, -38, 8, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(-42, 0, -60))
    mag.box(-152, -42, -12, 12, -80, -40, "steel_dark")                                # out to the left
    mag.box(-158, -152, -13.5, 13.5, -82, -38, "steel")
    for i in range(4):
        x = -140 + i * 24
        mag.box(x, x + 3, -12.4, 12.4, -43, -39.6, "rubber")
        mag.box(x + 0.4, x + 2.6, -4, 4, -40.2, -39.3, "brass")
    mag.round_((-38, 0, -60), 80, 12)
    add_arms(m, right_hand=(8, -92, 30), left_hand=(-12, -40, -250), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -666), eject=(16, 4, -16), sight=(0, 44, 128))
    cyc = dict(bone="bolt", travel=(0, 0, 70), t_back=0.02, t_fwd=0.056)
    anims = _rifle_anims(m, 0.0, (3.4, 0.6, 1.3), 12, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 90),
                         selector=(-50, 0, 0), rec=0.16, length=0.24, tilt=(10, 10, 10), tilt_pos=(10, 16, 24),
                         draw_len=0.85)
    _side_mag(anims)
    return GunAsset(m, anims, _fp(pos=(0.12, -0.13, -0.2), rot=(0, 3.5, 0), ads=0.16))


# =================================================================================================
# M3 "Grease Gun"  (757 mm with the wire stock out, 203 mm barrel, tube receiver, cocking crank)
# =================================================================================================
def m3grease():
    m = new_gun("m3grease")
    body = m["body"]
    st = "steel_parked"
    body.cyl((0, 0, -30), 54, 240, st)                                                 # receiver tube -150 .. 90
    body.cyl((0, 0, 91), 50, 4, st)
    body.cyl((0, 0, -152), 44, 6, st)                                                  # barrel collar
    for k in range(10):
        body.box(-23.3, 23.3, -1.2, 1.2, -158, -148, "steel_light", rot=(0, 0, k * 18), pivot=(0, 0, -153))
    barrel(body, -150, -292, d=16, mat="steel_dark")
    body.rbox(-6, 6, 26, 34, 60, 84, st, r=2, edges="top")                             # rear peep
    peep(body, 74, 30, 46, st, w=12, hole=5, depth=3, hole_y=40)
    body.rbox(-4, 4, 26, 34, -140, -120, st, r=2, edges="top")                         # front blade
    body.box(-1.2, 1.2, 34, 40, -132, -128, st)
    # magazine housing (also the hand hold) and the hinged ejection-port cover on the right
    body.rbox(-14, 14, -64, -22, -146, -100, st, r=3, axis="y")
    cover = body.bone("dust_cover", pivot=(22, 12, -70))
    cover.rbox(18, 24, -6, 14, -120, -40, st, r=2.4, axis="z")
    moving(m, "dust_cover", rot=(0, 0, 100))
    crank = body.bone("charging_handle", pivot=(27, -6, -30))                          # cocking crank
    crank.box(26, 30, -10, -2, -34, -26, "steel")
    crank.box(28, 31, -38, -6, -34, -28, "steel")
    crank.cyl((31, -38, -31), 8, 8, "steel", axis="x", sides=8)
    moving(m, "charging_handle", rot=(90, 0, 0))
    body.rbox(-12, 12, -34, -20, -30, 90, st, r=3, edges="bottom")                     # trigger housing
    pistol_grip(body, 40, top_y=-30, length=92, width=26, depth=32, angle=-14, mat=st)
    trigger_group(m, body, 2, y_top=-32, guard_depth=26, guard_len=56, guard_mat=st)
    control(body, "mag_release", (-14, -48, -96), [(-17, -14, -52, -44, -102, -90, "steel")], press=(1.6, 0, 0))
    stock = m["gun"].bone("stock", pivot=(0, 0, 90))                                   # wire stock, extended
    for sx in (-1, 1):
        stock.cyl((sx * 9, -24, 280), 7, 380, "steel")
    stock.path([(96, -14), (110, -26)], 8, 6, "steel")
    stock.rbox(-16, 16, -80, -12, 456, 465, "steel", r=3)
    stock.path([(456, -76), (440, -54), (456, -32)], 6, 6, "steel")                    # the plate's loop
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-10, 10, -6, 12, -120, -46, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -64, -123))
    straight_mag(mag, -60, -140, -106, 190, width=24, mat="steel_dark", round_d=11, round_len=29)
    add_arms(m, right_hand=(8, -76, 40), left_hand=(-12, -100, -123), right_rot=(34, 14, 6), left_rot=(30, -14, -4))
    add_sockets(m, muzzle=(0, 0, -294), eject=(24, 0, -80), sight=(0, 40, 74))
    cyc = dict(bone="bolt", travel=(0, 0, 70), t_back=0.024, t_fwd=0.07)
    anims = _rifle_anims(m, 0.0, (1.6, 0.4, 0.9), 7, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 0),
                         mag_sound="smg", rec=0.12, length=0.2)
    return GunAsset(m, anims, _fp(pos=(0.11, -0.115, -0.21), ads=0.22))


# =================================================================================================
# PPS-43  (820 mm with the stock open, 243 mm barrel, stamped receiver, slotted shroud and brake)
# =================================================================================================
def pps43():
    m = new_gun("pps43")
    body = m["body"]
    st = "steel_dark"
    body.rbox(-14, 14, -28, 16, -150, 120, st, r=3, edges="all")                       # stamped receiver
    body.box(-14.4, 14.4, -6, -4, -146, 116, "rubber")                                 # seam
    pins(body, 14, [(-18, -140), (-18, 110)], d=4, mat="steel")
    ejection_port(body, 14, -2, 12, -100, -50, lip_mat=st)
    body.rbox(-16, 16, -14, 16, -340, -150, st, r=6, edges="top")                      # shroud
    for z in range(-330, -160, 30):
        for sx in (-1, 1):
            body.box(sx * 16 - 0.4, sx * 16 + 0.4, -6, 8, z, z + 16, "rubber")
    body.box(-17, 17, -16, 18, -372, -340, st)                                         # U-shaped brake
    body.box(-12, 12, -8, 8, -372.4, -366, "rubber")
    barrel(body, -150, -350, d=14, mat="steel_light")
    ring_sight(body, -352, 16, st, r=6.5, depth=12, post_h=12, base_w=12)              # post top at 30
    body.rbox(-8, 8, 16, 22, 40, 70, st, r=2, edges="top")                             # L-flip rear sight
    for sx in (-1, 1):
        body.box(sx * 4.6 - 2.4, sx * 4.6 + 2.4, 22, 30.5, 54, 60, st)
    pistol_grip(body, 40, top_y=-28, length=90, width=26, depth=32, angle=-14, mat="wood")
    trigger_group(m, body, 2, y_top=-28, guard_depth=26, guard_len=58, guard_mat=st)
    control(body, "safety", (0, -30, -32), [(-3, 3, -40, -30, -36, -28, "steel")], press=(0, 0, 4))
    control(body, "mag_release", (0, -30, -52), [(-6, 6, -40, -28, -56, -50, "steel")], turn=(20, 0, 0))
    body.rbox(-14, 14, -46, -28, -110, -54, st, r=2, axis="y")                         # magazine well
    stock = m["gun"].bone("stock", pivot=(0, 0, 120))                                  # folding stock, open
    stock.rbox(-14, 14, -10, 14, 118, 132, st, r=3)
    for sx in (-1, 1):
        stock.path([(130, 6), (440, 6)], 6, 5, st, x=sx * 11)
        stock.path([(130, -6), (300, -40), (440, -76)], 6, 5, st, x=sx * 11)
    stock.rbox(-14, 14, -84, 14, 440, 450, st, r=4)
    stock.rbox(-15, 15, -86, 16, 448, 452, "rubber", r=4)
    ch = body.bone("bolt", pivot=(14, 4, -20))
    ch.box(-9, 9, -2, 12, -100, -40, "steel_light")
    ch.box(9, 22, 1, 9, -26, -14, "steel_light")
    ch.cyl((24, 5, -20), 11, 6, "steel_light", axis="x", sides=16)
    body.box(14, 14.4, 2, 8, -40, 60, "rubber")                                        # cocking slot
    mag = m["gun"].bone("magazine", pivot=(0, -46, -82))
    curved_mag(mag, -40, -106, 46, 196, curve=16, segs=5, width=22, mat="steel_dark", rib_mat="steel", round_d=9.4,
               round_len=34)
    add_arms(m, right_hand=(8, -74, 40), left_hand=(-12, -10, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -374), eject=(14, 6, -76), sight=(0, 30, 57))
    cyc = dict(bone="bolt", travel=(0, 0, 76), t_back=0.02, t_fwd=0.056)
    anims = _rifle_anims(m, 10.0, (1.8, 0.4, 0.9), 8, "smg", cyc, ch="bolt", ch_travel=(0, 0, 76), mag_sound="smg",
                         rec=0.11, length=0.18)
    return GunAsset(m, anims, _fp(pos=(0.11, -0.115, -0.21), ads=0.24))


GUNS = {"m1carbine": m1carbine, "svt40": svt40, "g43": g43, "fg42": fg42, "m3grease": m3grease, "pps43": pps43}
