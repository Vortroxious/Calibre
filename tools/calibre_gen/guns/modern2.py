"""Expansion 3, modern rifles: SIG MCX and H&K HK417 from the AR kit; the bullpups L85A2, QBZ-95 and FN F2000."""
from ..common import GunAsset, new_gun, add_arms, add_sockets, moving
from ..parts import (pistol_grip, trigger_group, curved_mag, barrel, flash_hider_a2, pins, vents, ejection_port,
                     side_swivel, sling_swivel)
from ..longkit import slot, peep, eared_sight, selector, button
from ..pistolkit import control
from ..riflekit import butt_plate
from ..shotkit import crossbolt
from .ar15 import _ar, _anims as _ar_anims, _buis, _flip_front, FP as AR_FP
from .modern import _rifle_anims, _fp


def mcx():
    """SIG MCX (.300 Blackout, 11.5 in barrel): 760 mm with the stock open, slim free-float guard, folding stock."""
    m, a = _ar("mcx", barrel_out=313, barrel_d=17, guard="ff", guard_len=250, front="flip", stock="mcx", muzzle="a2",
               mag="pmag30")
    return GunAsset(m, _ar_anims(m, a, kick=(2.6, 0.45, 1.0), push=11), AR_FP)


def hk417():
    """H&K HK417 (16.5 in): 985 mm with the stock out, 419 mm barrel, AR-10 size receivers, quad rail."""
    m, a = _ar("hk417", ul=222, hw_low=12.5, hw_up=15.5, barrel_out=445, barrel_d=19, guard="hk", guard_len=270,
               front="flip", stock="hk", muzzle="brake", mag="sr25")
    return GunAsset(m, _ar_anims(m, a, kick=(3.8, 0.5, 1.2), push=14, rec=0.18, length=0.27, draw_len=0.8,
                                 travel=(0, 0, 60)),
                    {"hip": {"pos": [0.12, -0.13, -0.19], "rot": [0, 4, 0]}, "ads": {"dist": 0.09}})


def l85a2():
    """L85A2: 785 mm long bullpup, 518 mm barrel, stamped steel body with green furniture, right-side cocking
    handle, iron sights in a carry-handle base."""
    g, st = "polymer_od", "steel_dark"
    m = new_gun("l85a2")
    body = m["body"]
    body.rbox(-17, 17, -34, 22, -150, 256, st, r=4, edges="top")                       # stamped body
    body.rbox(-16, 16, -54, -34, -150, 250, st, r=3, edges="bottom")                   # trigger mechanism housing
    body.box(-17.4, 17.4, -35.5, -33, -148, 252, "rubber")
    pins(body, 17, [(-24, -130), (-24, 110), (-40, 236), (8, 240)], d=5, mat="steel")
    body.rbox(-18, 18, -100, 24, 256, 262, st, r=5)                                    # butt plate and pad
    body.rbox(-19, 19, -102, 26, 262, 270, "rubber", r=7)
    body.profile(-16, 16, [(170, -54), (256, -54)], [(170, -56), (256, -100)], st)
    body.rbox(-19.5, -17, -6, 20, 150, 240, g, r=2.4, axis="z")                        # cheek piece (left)
    body.rail(-140, 200, 22, mat=st, width=17)                                         # sight rail
    body.rbox(-9, 9, 25, 48, 128, 176, st, r=3, edges="top")                           # rear sight base
    peep(body, 168, 46, 70, st, w=12, hole=5, depth=3, hole_y=62)
    for sx in (-1, 1):
        body.box(sx * 8 - 1.5, sx * 8 + 1.5, 46, 68, 158, 176, st)
    # hand guard, gas block, barrel
    body.rbox(-22, 22, -40, 30, -330, -150, g, r=10)
    vents(body, 22, 6, 16, -320, -165, n=6, fill=0.6)
    body.box(-22.4, 22.4, -6, -4, -326, -154, "rubber")
    body.rbox(-9, 9, -10, 30, -352, -330, st, r=3, edges="top")
    eared_sight(body, -341, 28, 39.6, st, w=14, depth=12, lean=4)                      # post top at 62
    barrel(body, -150, -473, d=17, mat=st)
    flash_hider_a2(body, -473, d=20, length=42)
    body.box(-3, 3, -18, -9, -430, -410, st)                                           # bayonet lug
    pistol_grip(body, -46, top_y=-54, length=86, width=28, depth=36, angle=-14, mat=g)
    trigger_group(m, body, -84, y_top=-54, guard_depth=28, guard_len=66, guard_mat=st)
    crossbolt(body, -60, -44, hw=16, d=7)
    selector(body, (-17, -24, 196), mat=st, length=16, side=-1, turn=(-50, 0, 0))
    control(body, "mag_release", (-16, -40, 20), [(-19, -16, -46, -34, 14, 26, st)], press=(1.6, 0, 0))
    body.rbox(-15, 15, -74, -54, 30, 96, st, r=2.4, axis="y")                          # magazine well
    ejection_port(body, 17, -2, 14, 100, 160, lip_mat=st)
    body.rbox(17, 19.5, -8, -2, 96, 164, st, r=1.2, axis="z")                          # dust cover, open
    ch = body.bone("charging_handle", pivot=(17, 6, 60))
    ch.box(17, 28, 3, 9, 54, 66, st)
    ch.cyl((30, 6, 60), 13, 6, st, axis="x", sides=16)
    body.box(17, 17.4, 4, 8, 66, 160, "rubber")                                        # its slot
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.6, -1, 13, 102, 158, "steel_light")
    side_swivel(body, -17, 0, 244, h=14)
    side_swivel(body, -22, -4, -322, h=14)
    mag = m["gun"].bone("magazine", pivot=(0, -58, 63))
    curved_mag(mag, -42, 34, 58, 168, curve=10, segs=5, width=21.5, mat="alloy_grey", rib_mat="steel_dark",
               round_d=9.6, round_len=57)
    add_arms(m, right_hand=(8, -104, -40), left_hand=(-10, -60, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -517), optic=(0, 25, 20), under=(0, -40, -240), side=(-23, 0, -260),
                eject=(18, 4, 130), sight=(0, 62, 168))
    cyc = dict(bone="bolt", travel=(0, 0, 64), t_back=0.018, t_fwd=0.055)
    anims = _rifle_anims(m, 8.0, (2.2, 0.4, 1.0), 9, "ar", cyc, ch="charging_handle", ch_travel=(0, 0, 80),
                         selector=(-50, 0, 0), tilt=(4, -10, -30), tilt_pos=(-30, 14, 10))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.13, -0.16), ads=0.16))


def qbz95():
    """QBZ-95: 745 mm long bullpup, 463 mm barrel, one-piece polymer body with the long integral carry handle,
    full-hand trigger guard, charging handle under the carry handle."""
    p, st = "polymer", "steel_dark"
    m = new_gun("qbz95")
    body = m["body"]
    body.rbox(-19, 19, -44, 24, -200, 248, p, r=8)                                     # body shell
    body.profile(-19, 19, [(150, -44), (248, -44)], [(150, -46), (248, -96)], p)        # butt drop
    body.rbox(-20, 20, -100, 28, 248, 262, "rubber", r=7)
    for i in range(5):
        body.box(-16, 16, -90 + i * 23, -84 + i * 23, 262, 262.6, "polymer_grey")
    body.box(-19.4, 19.4, -12, -10, -196, 244, "rubber")                               # shell seam
    pins(body, 19, [(-28, -180), (-28, 120), (4, 220)], d=5, mat="steel")
    # carry handle with the rear sight in it; the dovetail on top takes an optic
    for sx in (-1, 1):                                                                 # front posts, the
        body.rbox(sx * 9 - 3, sx * 9 + 3, 24, 70, -150, -134, p, r=1.5, axis="x")      # front sight between
    body.box(-6, 6, 24, 32, -150, -134, p)
    body.box(-1.2, 1.2, 32, 59, -144, -140, "steel_dark")
    for sx in (-1, 1):                                                                 # rear posts: open between
        body.rbox(sx * 9 - 3, sx * 9 + 3, 24, 70, 112, 128, p, r=1.5, axis="x")
    body.rbox(-9, 9, 66, 78, -152, 130, p, r=4)
    body.rail(-120, 100, 78, mat="alloy", width=16)
    body.box(-8, 8, 24, 30, 96, 128, p)
    for sx in (-1, 1):
        body.box(sx * 5.4 - 2.6, sx * 5.4 + 2.6, 30, 60, 118, 124, p)                  # rear notch
    ch = body.bone("charging_handle", pivot=(0, 30, -60))                              # rides under the handle
    ch.rbox(-7, 7, 24, 34, -74, -46, st, r=2.5, edges="top")
    body.box(-3, 3, 24, 24.6, -46, 60, "rubber")
    # front: hand guard nose, front sight ring, barrel
    body.rbox(-18, 18, -38, 22, -300, -200, p, r=8)
    vents(body, 18, -6, 6, -292, -208, n=3, fill=0.6)
    body.rbox(-9, 9, -10, 34, -334, -312, st, r=3, edges="top")
    barrel(body, -200, -441, d=17, mat=st)
    flash_hider_a2(body, -441, d=20, length=42)
    body.box(-3, 3, -18, -9, -400, -380, st)                                           # bayonet lug
    # full-hand trigger guard running into the grip
    pistol_grip(body, -46, top_y=-44, length=96, width=28, depth=36, angle=-12, mat=p)
    body.path([(-130, -44), (-136, -96), (-124, -136), (-40, -140)], 12, 6, p)
    trig = trigger_group(m, body, -84, y_top=-44, guard_depth=20, guard_len=40, guard_mat=p)
    selector(body, (-19, -20, 200), mat=st, length=14, side=-1, turn=(-60, 0, 0))
    control(body, "mag_release", (0, -66, 102), [(-6, 6, -80, -62, 98, 104, st)], turn=(-16, 0, 0))
    body.rbox(-16, 16, -64, -44, 30, 96, p, r=2.4, axis="y")                           # magazine well
    ejection_port(body, 19, 0, 14, 100, 160, lip_mat=p)
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 18.6, 1, 13, 102, 158, "steel_light")
    side_swivel(body, -19, 4, 236, h=14)
    side_swivel(body, -18, -2, -292, h=12)
    mag = m["gun"].bone("magazine", pivot=(0, -50, 63))
    curved_mag(mag, -34, 34, 58, 170, curve=18, segs=6, width=23, mat="polymer", rib_mat="polymer_grey",
               round_d=9.8, round_len=58)
    add_arms(m, right_hand=(8, -100, -40), left_hand=(-10, -56, -250), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -485), optic=(0, 81, -10), under=None, eject=(20, 6, 130), sight=(0, 59, 121))
    cyc = dict(bone="bolt", travel=(0, 0, 64), t_back=0.018, t_fwd=0.055)
    anims = _rifle_anims(m, 12.0, (2.3, 0.4, 1.0), 9, "ar", cyc, ch="charging_handle", ch_travel=(0, 0, 90),
                         selector=(-60, 0, 0), tilt=(4, -10, -30), tilt_pos=(-30, 14, 10))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.13, -0.16), ads=0.17))


def f2000():
    """FN F2000 Tactical: 688 mm long bullpup, 400 mm barrel, smooth polymer shell around the barrel, top rail,
    forward ejection chute, thumbhole grip."""
    p, st = "polymer", "steel_dark"
    m = new_gun("f2000")
    body = m["body"]
    body.rbox(-21, 21, -46, 26, -190, 244, p, r=10)                                    # shell
    body.profile(-21, 21, [(140, -46), (244, -46)], [(140, -48), (244, -98)], p)        # butt
    body.rbox(-22, 22, -102, 30, 244, 258, "rubber", r=8)
    body.box(-21.4, 21.4, -8, -6, -186, 240, "rubber")                                 # shell seam
    pins(body, 21, [(-30, -170), (-30, 110), (6, 216)], d=5, mat="steel")
    body.profile(-20, 20, [(-340, 12), (-190, 26)], [(-340, -34), (-190, -46)], p)      # tapering fore-end
    body.rbox(-20, 20, -58, -40, -330, -200, p, r=8, edges="bottom")                   # hand rest
    vents(body, 20.4, -52, -46, -320, -210, n=5, fill=0.5)
    body.box(21, 21.5, 0, 12, -230, -196, "rubber")                                    # forward ejection chute mouth
    body.rbox(21, 24, -2, 14, -196, -150, p, r=2, axis="z")
    body.rail(-180, 200, 26, mat="alloy")
    _buis(body, 180, 29, p, sy=62)
    _flip_front(body, -164, 29, p, sy=62)
    barrel(body, -340, -388, d=17, mat=st)
    flash_hider_a2(body, -388, d=20, length=42)
    # thumbhole grip joined to the full-hand guard
    pistol_grip(body, -46, top_y=-46, length=92, width=28, depth=38, angle=-14, mat=p)
    body.path([(-126, -46), (-134, -98), (-120, -138), (-44, -142)], 14, 7, p)
    body.path([(-10, -128), (40, -110), (80, -70)], 14, 7, p)                          # strap behind the grip
    trigger_group(m, body, -84, y_top=-46, guard_depth=18, guard_len=40, guard_mat=p)
    sel = body.bone("selector", pivot=(0, -50, -84))                                   # rotary selector under the trigger
    sel.cyl((0, -68, -84), 20, 5, p, axis="y", sides=16)
    sel.box(-2, 2, -71, -70.4, -94, -84, "white")
    moving(m, "selector", rot=(0, 60, 0))
    button(body, "mag_release", (21, -40, 20), d=9, mat=st)
    body.rbox(-17, 17, -68, -46, 30, 98, p, r=2.4, axis="y")                           # magazine well
    ch = body.bone("charging_handle", pivot=(-21, 8, -150))                            # left side, well forward
    ch.box(-30, -21, 5, 11, -156, -144, st)
    ch.rbox(-38, -30, 2, 14, -160, -140, p, r=2.4, axis="y")
    body.box(-21.4, -21, 6, 10, -144, -60, "rubber")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-8, 8, 0, 12, 100, 160, "steel_light")                                    # hidden under the top hatch
    body.rbox(-10, 10, 25.4, 27, 100, 170, p, r=1.2)                                   # inspection hatch
    side_swivel(body, -21, 6, 230, h=14)
    side_swivel(body, -20, -4, -320, h=12)
    mag = m["gun"].bone("magazine", pivot=(0, -54, 64))
    curved_mag(mag, -38, 36, 58, 168, curve=10, segs=5, width=21.5, mat="alloy_grey", rib_mat="steel_dark",
               round_d=9.6, round_len=57)
    add_arms(m, right_hand=(8, -102, -40), left_hand=(-10, -72, -265), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -432), optic=(0, 29, 0), under=None, side=(-22, -10, -280), eject=(22, 6, -210),
                sight=(0, 62, 180))
    cyc = dict(bone="bolt", travel=(0, 0, 60), t_back=0.016, t_fwd=0.05)
    anims = _rifle_anims(m, 8.0, (2.2, 0.4, 1.0), 9, "ar", cyc, ch="charging_handle", ch_travel=(0, 0, 80),
                         selector=(0, 60, 0), tilt=(4, -10, -30), tilt_pos=(-30, 14, 10))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.13, -0.16), ads=0.2))


GUNS = {"mcx": mcx, "hk417": hk417, "l85a2": l85a2, "qbz95": qbz95, "f2000": f2000}
