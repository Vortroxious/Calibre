"""Modern pack: Kriss Vector, H&K MP7A1, H&K G36C, FAMAS F1, IWI Tavor X95, FN Five-seveN, H&K USP, CZ 75 SP-01,
Franchi SPAS-12, Atchisson AA-12."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden)
from ..templates import rifle_reload, pistol_reload, pump_cycle, tube_reload
from ..parts import pistol_grip, trigger_group, curved_mag, straight_mag, barrel, flash_hider_a2
from ..common import moving
from ..parts import pins, vents, ejection_port, side_swivel, sling_swivel
from ..longkit import (slot, top_slot, ribs, ring_sight, eared_sight, drum_sight, flip_sight, aperture_sight,
                       peep, rod_stock, selector, paddle, button, stock_solid)
from ..pistolkit import control
from .ar15 import _buis, _flip_front
from .shotguns import _shells


def _fp(pos=(0.115, -0.12, -0.2), rot=(0, 4, 0), ads=0.2):
    return {"hip": {"pos": list(pos), "rot": list(rot)}, "ads": {"dist": ads}}


def _inspect(m):
    """Placeholder: build_assets replaces every inspect with the generated close-up one (cs2.py)."""
    return Anim(m, "inspect", 1.0)


def _flip_sights(b, z_front, z_rear, top, mat="polymer"):
    """Folding BUIS front and rear on a top rail."""
    b.box(-8, 8, top, top + 6, z_front - 10, z_front + 10, mat)
    b.box(-1.5, 1.5, top + 6, top + 24, z_front - 3, z_front + 3, mat)
    b.box(-8, 8, top, top + 6, z_rear - 10, z_rear + 10, mat)
    b.box(-8, -2, top + 6, top + 22, z_rear - 3, z_rear + 3, mat)
    b.box(2, 8, top + 6, top + 22, z_rear - 3, z_rear + 3, mat)


def _rifle_anims(m, mag_a, kick, push, style, cyc, ch=None, ch_travel=(0, 0, 70), bolt=None, bolt_travel=(0, 0, 70),
                 selector=(0, 0, 0), lock=False, mag_sound="rifle", draw_len=0.7, rec=0.13, length=0.22, rock=0.0,
                 tilt=(6, -6, -26), tilt_pos=(-20, 16, 24)):
    kk = dict(kick=kick, push=push, cycle=cyc)
    a = [idle(m), draw(m, draw_len, sound="draw_rifle"),
         fire_basic(m, "fire", recover=rec, length=length, **kk),
         fire_basic(m, "fire_aim", recover=rec * 0.85, length=length * 0.9, aim=True, **kk)]
    if lock:
        a.append(fire_basic(m, "fire_last", recover=rec, length=length, lock_back=True, **kk))
    a += [rifle_reload(m, "reload", mag_a, empty=False, style=style, mag_sound=mag_sound, rock=rock, tilt=tilt,
                       tilt_pos=tilt_pos),
          rifle_reload(m, "reload_empty", mag_a, empty=True, style=style, bolt=bolt, bolt_travel=bolt_travel, ch=ch,
                       ch_travel=ch_travel, mag_sound=mag_sound, rock=rock, tilt=tilt, tilt_pos=tilt_pos,
                       bolt_hold_open=lock)]
    if m.has("selector"):
        a.append(firemode(m, selector_rot=selector))
    a += [_inspect(m), dry_fire(m)]
    return a


def _famas_detail(m, body, p="polymer"):
    body.box(-14, 14, 14, 20, 210, 300, p)                                # cheek rest
    for sx in (-1, 1):                                                    # folded bipod legs
        body.box(sx * 18, sx * 21, -30, -20, -300, 0, "steel_dark")
        body.box(sx * 17, sx * 22, -34, -18, -310, -300, "rubber")
    body.cyl((0, 0, -478), 24, 6, "steel_dark")                           # grenade rings on the flash hider
    body.cyl((0, 0, -494), 24, 6, "steel_dark")
    body.box(-8, -6, 56, 78, -252, -236, p)                               # front sight wings
    body.box(6, 8, 56, 78, -252, -236, p)
    for z in range(-230, 190, 40):                                        # carry-handle slots
        body.box(-8.4, 8.4, 52, 58, z, z + 10, "rubber")
    body.box(-3, 3, 14, 15, -120, -40, "rubber")                          # charging-handle slot
    body.box(-18.4, -18, -6, 12, 120, 180, "polymer_grey")                # blanked left port
    body.box(-18.4, 18.4, -16, -14, -120, 300, "rubber")                  # receiver seam
    body.box(-3, 3, -86, -76, 334, 344, "steel")                         # sling loop
    body.box(-6, 6, -50, -44, 144, 152, "steel_dark")                     # mag release
    body.box(-17.4, 17.4, 4, 8, -320, -120, "rubber")                     # handguard top line


# =================================================================================================
# Kriss Vector .45 (Gen II SMG)
# =================================================================================================
def vector():
    # Kriss Vector Gen II SMG: 617 mm with the stock open (406 folded), 140 mm barrel set low under the rail
    m = new_gun("vector")
    body = m["body"]
    P, st = "polymer", "steel_dark"
    body.chamfer_box(-17, 17, 18, 58, -154, 206, P, ch=4, edges="top")              # upper, full length
    body.rail(-150, 202, 58, mat="alloy", side="top")
    body.profile(-17, 17, [(-154, 18), (20, 18)], [(-154, -30), (-60, -52), (20, -86)], P)   # the Super V housing
    body.box(-17, 17, -92, 18, 20, 62, P)                                          # magazine well
    body.box(-17.6, 17.6, -92, -86, 18, 64, P)
    body.box(-16, 16, -42, 18, 62, 152, P)                                         # trigger housing
    body.chamfer_box(-17, 17, -22, 18, 150, 206, P, ch=5, edges="bottom")           # rear
    body.box(-17.4, 17.4, 16, 19, -150, 202, "rubber")                             # upper / lower seam
    for sx in (-1, 1):                                                             # side panels on the housing
        body.box(sx * 17 - 0.4, sx * 17 + 0.4, -22, 6, -130, -20, "polymer_grey")
    body.rail(-146, -80, -30, mat="alloy", side="bottom")
    barrel(body, -154, -196, d=17, mat="steel")
    body.cyl((0, 0, -202), 21, 14, st)                                             # thread protector
    body.cyl((0, 0, -209.3), 11, 0.6, "rubber", sides=8)
    ejection_port(body, 17, 22, 38, 18, 60, lip_mat=P)
    _flip_sights(body, -136, 188, 61)
    pistol_grip(body, 124, top_y=-40, length=88, width=28, depth=36, angle=-14, mat=P)
    trigger_group(m, body, 86, y_top=-42, guard_depth=26, guard_len=56, guard_mat=P)
    selector(body, (-16, -24, 126), mat="steel", length=16, side=-1, turn=(-40, 0, 0))
    control(body, "safety", (-16, -8, 100), [(-18.6, -16, -11, -5, 86, 104, "steel")], turn=(-30, 0, 0))
    control(body, "bolt_catch", (-17, 2, 40), [(-19.4, -17, -6, 8, 34, 46, st)], press=(0, 3, 0))
    button(body, "mag_release", (-17, -60, 56), d=9, mat=st)
    pins(body, 17, [(4, -120), (-30, 70), (4, 190)], d=5, mat="steel")
    ch = body.bone("charging_handle", pivot=(-18, 2, -100))
    ch.box(-22, -17, -2, 6, -112, -88, st)
    ch.box(-30, -22, -3, 7, -96, -88, st)
    slot(body, -17, 0, 4, -112, -40)
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.6, 23, 37, 20, 58, "steel_light")
    # side-folding stock, open
    stock = m["gun"].bone("stock", pivot=(17, 38, 206))
    stock.box(-17, 17, 18, 58, 206, 222, P)
    stock.cyl((17, 38, 214), 8, 36, "steel", axis="y", sides=8)
    stock.box(-8, 8, 36, 52, 222, 400, P)
    stock.path([(222, 22), (300, -6), (400, -34)], 14, 10, P)
    stock.box(-8, 8, -8, 38, 296, 308, P)
    stock.box(-16, 16, -46, 56, 398, 408, P)
    stock.box(-17, 17, -50, 58, 408, 418, "rubber")
    mag = m["gun"].bone("magazine", pivot=(0, -92, 41))
    straight_mag(mag, -40, 24, 58, 196, width=27, mat=P, base_mat="polymer_grey", round_d=11.6, round_len=32,
                 witness=False)
    for i in range(6):                                                             # numbered witness holes
        mag.box(-2, 2, -110 - i * 20, -106 - i * 20, 58, 58.5, "rubber")
    add_arms(m, right_hand=(8, -86, 136), left_hand=(-10, -52, -90), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -210), optic=(0, 61, 30), under=(0, -33, -110), side=(-17, 36, -130),
                eject=(17, 30, 40), sight=(0, 83, 188))
    m.warp_z([(0, -80)])                                                              # put the grip where the hand is

    cyc = dict(bone="bolt", travel=(0, 0, 28), t_back=0.01, t_fwd=0.032)
    anims = _rifle_anims(m, 0.0, (1.8, 0.3, 0.8), 7, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 60),
                         selector=(-40, 0, 0), mag_sound="smg", rec=0.1, length=0.18)
    return GunAsset(m, anims, _fp(ads=0.16))


# =================================================================================================
# H&K MP7A1
# =================================================================================================
def mp7():
    # H&K MP7A1: 638 mm with the stock out (415 in), 180 mm barrel, magazine in the grip
    m = new_gun("mp7")
    body = m["body"]
    P, st = "polymer", "steel_dark"
    body.chamfer_box(-17, 17, -24, 24, -230, 150, P, ch=5, edges="top")              # receiver
    body.box(-13, 13, 24, 28, -224, 146, P)
    body.rail(-220, 142, 28, mat="alloy", side="top")
    body.chamfer_box(-16, 16, -46, -24, -230, -72, P, ch=5, edges="bottom")          # fore-end
    for sx in (-1, 1):
        body.rail(-214, -150, 0, x=sx * 17, mat="alloy", side="right" if sx > 0 else "left", width=18)
    body.box(-17.4, 17.4, -26, -23, -226, 146, "rubber")
    barrel(body, -230, -244, d=14, mat="steel")
    flash_hider_a2(body, -238, d=17, length=28)
    ejection_port(body, 17, -4, 10, -64, -22, lip_mat=P)
    _flip_sights(body, -206, 128, 31)
    # grip with the magazine well, guard, ambidextrous controls
    gp = (0, -24, 12)
    r = dict(rot=(-10, 0, 0), pivot=gp)
    body.box(-16, 16, -128, -24, -10, 36, P, **r)
    body.box(-14.5, 14.5, -128, -24, -12.5, -10, P, **r)
    body.box(-14.5, 14.5, -128, -24, 36, 38.5, P, **r)
    for i in range(5):
        body.box(-16.5, 16.5, -118 + i * 17, -110 + i * 17, -6, 32, P, **r)
    body.box(-17, 17, -132, -126, -12, 38, P, **r)
    trigger_group(m, body, -40, y_top=-26, guard_depth=26, guard_len=52, guard_mat=P)
    selector(body, (-17, -12, 22), mat=P, length=16, side=-1, turn=(-50, 0, 0))
    body.box(17, 20, -15, -9, 8, 24, P)
    control(body, "bolt_catch", (-17, -14, -30), [(-19.4, -17, -20, -10, -36, -24, st)], press=(0, 3, 0))
    mr = body.bone("mag_release", pivot=(0, -50, -12))
    mr.box(5, 9, -54, -46, -18, -8, st)
    mr.box(-9, -5, -54, -46, -18, -8, st)
    moving(m, "mag_release", pos=(0, -2.4, 0))
    pins(body, 17, [(-16, -80), (-16, 130)], d=5, mat="steel")
    # folding foregrip, down
    fg = body.bone("foregrip", pivot=(0, -46, -150))
    fg.box(-11, 11, -124, -46, -164, -138, P, rot=(6, 0, 0), pivot=(0, -46, -150))
    for i in range(4):
        fg.box(-11.5, 11.5, -114 + i * 16, -108 + i * 16, -162, -140, P, rot=(6, 0, 0), pivot=(0, -46, -150))
    fg.cyl((0, -46, -150), 8, 34, "steel", axis="x", sides=8)
    ch = body.bone("charging_handle", pivot=(0, 18, 150))
    ch.box(-6, 6, 14, 22, 100, 152, st)
    ch.box(-18, 18, 13, 23, 150, 160, st)
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.6, -3, 9, -62, -24, "steel_light")
    # retractable stock, out
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    rod_stock(stock, 20, 354, 12, -4, "steel_dark", -64, 22, butt_hw=17, rod=7)
    side_swivel(body, -17, 8, 138, h=12)
    side_swivel(body, -17, -34, -220, h=12)
    mag = m["gun"].bone("magazine", pivot=gp, rot=(-10, 0, 0))
    straight_mag(mag, -28, -4, 30, 150, width=21, mat=P, base_mat="polymer_grey", round_d=7.2, round_len=30,
                 witness=False)
    add_arms(m, right_hand=(8, -84, 26), left_hand=(-8, -90, -150), right_rot=(34, 14, 6), left_rot=(10, -18, -4))
    add_sockets(m, muzzle=(0, 0, -268), optic=(0, 31, -40), side=(-20, 0, -180), eject=(17, 3, -42),
                sight=(0, 53, 128))

    cyc = dict(bone="bolt", travel=(0, 0, 24), t_back=0.01, t_fwd=0.03)
    anims = _rifle_anims(m, -10.0, (1.6, 0.3, 0.8), 6, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 40),
                         selector=(0, 0, 0), mag_sound="pistol", rec=0.1, length=0.16, tilt=(10, -8, -24),
                         tilt_pos=(-30, 24, 30))
    return GunAsset(m, anims, _fp(pos=(0.11, -0.1, -0.22), ads=0.17))


# =================================================================================================
# H&K G36C
# =================================================================================================
def g36c():
    # H&K G36C: 720 mm with the stock open (500 folded), 228 mm barrel
    p = "polymer"
    m = new_gun("g36c")
    body = m["body"]
    st = "steel_dark"
    body.rbox(-18, 18, -24, 20, -160, 110, p, r=6, edges="top")                        # polymer receiver
    ribs(body, 18, -16, 12, (-140, 40, 70), 10, p, proud=0.7)
    body.box(-18.4, 18.4, -26, -23, -156, 106, "rubber")
    ejection_port(body, 18, -2, 12, -96, -44, lip_mat=p)
    body.rbox(18, 24, -2, 14, -40, -20, p, r=2.4, axis="y", edges="all")               # case deflector
    # low carry rail on two posts; the charging handle swings in the gap under it
    body.box(-9, 9, 20, 40, -150, -128, p)
    body.box(-9, 9, 20, 40, 60, 92, p)
    body.rbox(-11, 11, 38, 44, -150, 92, p, r=2.4, edges="top")
    body.rail(-146, 88, 44, mat="alloy", side="top")
    _buis(body, 74, 47, p, sy=68)
    _flip_front(body, -132, 47, p, sy=68)
    # hand guard with rails, barrel, four-prong hider
    body.rbox(-19, 19, -34, 16, -292, -160, p, r=8, edges="all")
    vents(body, 19, -10, -2, -284, -170, n=5, fill=0.55)
    body.rail(-286, -168, -34, mat="alloy", side="bottom")
    for sx in (-1, 1):
        body.rail(-284, -200, 4, x=sx * 19, mat="alloy", side="right" if sx > 0 else "left", width=16)
    barrel(body, -292, -352, d=17, mat=st)
    body.cyl((0, 0, -372), 21, 40, st)                                                 # open-prong flash hider
    for ang in (0, 45, 90, 135):
        body.box(-10.9, 10.9, -1.6, 1.6, -392.3, -366, "rubber", rot=(0, 0, ang), pivot=(0, 0, -378))
    # magazine well, grip, guard, controls
    body.rbox(-17, 17, -60, -24, -104, -40, p, r=2.4, axis="y", edges="all")
    body.box(-16, 16, -44, -24, -40, 80, p)
    paddle(body, (0, -58, -38), mat=p, w=16, h=8, d=11)
    pistol_grip(body, 34, top_y=-42, length=90, width=28, depth=36, angle=-16, mat=p)
    trigger_group(m, body, -2, y_top=-44, guard_depth=27, guard_len=60, guard_mat=p)
    selector(body, (-16, -30, 36), mat=p, length=15, side=-1, turn=(-90, 0, 0))
    body.box(16, 18.6, -33, -27, 22, 38, p)
    control(body, "bolt_catch", (0, -46, -34), [(-3, 3, -52, -44, -38, -30, st)], press=(0, 3, 0))
    pins(body, 18, [(-12, -148), (-12, 96), (-34, 50)], d=5, mat="steel")
    ch = body.bone("charging_handle", pivot=(0, 28, -120))
    ch.box(-4, 4, 22, 34, -128, -112, st)
    ch.rbox(-14, 14, 24, 32, -132, -124, p, r=2.4, axis="y", edges="all")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 17.6, -1, 11, -94, -46, "steel_light")
    # side-folding skeleton stock, open
    stock = m["gun"].bone("stock", pivot=(18, 0, 110))
    stock.rbox(-18, 18, -26, 22, 110, 126, p, r=5, edges="all")
    stock.cyl((18, -2, 118), 8, 44, "steel", axis="y", sides=16)
    stock.rbox(-8, 8, 2, 20, 126, 316, p, r=4, edges="all")
    stock.path([(126, -18), (210, -52), (316, -70)], 16, 11, p)
    stock.rbox(-8, 8, -52, 4, 206, 220, p, r=3, edges="all")
    stock.rbox(-17, 17, -82, 24, 314, 326, p, r=4, edges="all")
    stock.rbox(-18, 18, -86, 26, 326, 336, "rubber", r=4, edges="all")
    mag = m["gun"].bone("magazine", pivot=(0, -50, -72))
    curved_mag(mag, -34, -100, 58, 196, curve=12, segs=5, width=26, mat="polymer_clear", rib_mat="polymer_grey",
               round_d=9.6, round_len=57)
    add_arms(m, right_hand=(8, -94, 50), left_hand=(-10, -50, -226), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -394), optic=(0, 47, -20), under=(0, -40, -226), side=(-22, 4, -240),
                eject=(19, 5, -70), sight=(0, 68, 74))

    cyc = dict(bone="bolt", travel=(0, 0, 64), t_back=0.018, t_fwd=0.052)
    anims = _rifle_anims(m, 9.0, (2.4, 0.4, 1.0), 9, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 70),
                         bolt="bolt", bolt_travel=(0, 0, 64), selector=(-90, 0, 0))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.125, -0.19), ads=0.2))


# =================================================================================================
# FAMAS F1 (bullpup, carry handle with the sights and the charging handle under it)
# =================================================================================================
def famas():
    # FAMAS F1: 757 mm long bullpup, 488 mm barrel, the long carry handle is the sight tunnel
    p = "polymer"
    m = new_gun("famas")
    body = m["body"]
    st = "steel_dark"
    body.rbox(-19, 19, -44, 16, -150, 270, p, r=7, edges="all")                        # receiver / butt
    body.taper(-19, 19, 150, 270, -40, -40, -44, -98, p)                               # butt drop
    body.rbox(-20, 20, -102, 20, 270, 284, "rubber", r=6, edges="all")
    for i in range(5):
        body.box(-17, 17, -92 + i * 22, -86 + i * 22, 284, 284.6, p)
    body.rbox(-14, 14, 16, 25, 150, 262, p, r=4, edges="top")                          # cheek rest
    body.box(-19.4, 19.4, -16, -13, -146, 266, "rubber")
    body.rbox(-18, 18, -36, 12, -292, -150, p, r=7, edges="all")                       # hand guard
    vents(body, 18, -22, -8, -284, -160, n=6, fill=0.5)
    barrel(body, -292, -440, d=17, mat=st)
    for z in (-332, -352):
        body.cyl((0, 0, z), 22, 5, st)                                                 # grenade-launching rings
    flash_hider_a2(body, -432, d=20, length=40)
    # carry handle with the sights inside it
    body.rbox(-6.5, 6.5, 12, 64, -264, -246, p, r=2.4, axis="y", edges="all")
    body.rbox(-8, 8, 16, 66, 122, 152, p, r=3, axis="y", edges="all")
    body.rbox(-8, 8, 58, 70, -264, 152, p, r=3.2, edges="top")
    for i in range(9):
        slot(body, 8, 60, 66, -240 + i * 42, -218 + i * 42)
        slot(body, -8, 60, 66, -240 + i * 42, -218 + i * 42)
    body.box(-1.2, 1.2, 70, 80, -257, -253, st)                                        # front post and its wings
    for sx in (-1, 1):
        body.box(sx * 6 - 1.2, sx * 6 + 1.2, 70, 84, -262, -248, p)
    peep(body, 140, 70, 87, p, w=13, hole=7.0, depth=2.6, hole_y=80)
    for sx in (-1, 1):                                                                 # bipod legs folded along the top
        xs = sorted((sx * 19, sx * 22.5))
        body.box(xs[0], xs[1], 2, 10, -250, -20, st)
        body.box(xs[0] - 0.5, xs[1] + 0.5, 0, 12, -262, -250, "rubber")
        body.cyl((sx * 20.5, 6, -14), 9, 5, "steel", axis="x", sides=16)
    # grip, guard, selector inside the guard
    pistol_grip(body, -46, top_y=-44, length=88, width=28, depth=34, angle=-14, mat=p)
    trigger_group(m, body, -84, y_top=-44, guard_depth=28, guard_len=64, guard_mat=p)
    sel = body.bone("selector", pivot=(0, -50, -58))
    sel.box(-6, 6, -56, -50, -66, -50, "steel")
    ejection_port(body, 19, -4, 10, 96, 150, lip_mat=p)
    body.box(-19.5, -19, -4, 10, 96, 150, "polymer_grey")                              # blanked left port
    body.box(-17, 17, -52, -44, 14, 66, p)                                             # magazine well lip
    paddle(body, (0, -50, 68), mat=p, w=16, h=8, d=10)
    pins(body, 19, [(-6, -130), (-6, 60), (-30, 200)], d=5, mat="steel")
    side_swivel(body, -19, -30, 250, h=14)
    side_swivel(body, -18, 0, -280, h=12)
    ch = body.bone("charging_handle", pivot=(0, 30, -60))
    ch.box(-3, 3, 16, 36, -66, -54, st)
    ch.rbox(-7, 7, 34, 46, -70, -50, st, r=3, axis="y", edges="all")
    top_slot(body, 16, -3, 3, -120, -40)
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 18.6, -3, 9, 98, 148, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -44, 40))
    straight_mag(mag, -34, 18, 62, 156, width=24, mat="steel_dark", round_d=9.6, round_len=57)
    add_arms(m, right_hand=(8, -100, -40), left_hand=(-10, -52, -220), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -475), optic=(0, 70, -40), side=(-18, -10, -230), eject=(20, 3, 123),
                sight=(0, 80, 140))

    cyc = dict(bone="bolt", travel=(0, 0, 60), t_back=0.014, t_fwd=0.044)
    anims = _rifle_anims(m, 0.0, (2.2, 0.4, 1.0), 9, "ar", cyc, ch="charging_handle", ch_travel=(0, 0, 70),
                         selector=(0, 0, 90), tilt=(4, -10, -30), tilt_pos=(-30, 14, 10))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.135, -0.16), ads=0.22))


# =================================================================================================
# IWI Tavor X95 (bullpup)
# =================================================================================================
def x95():
    # IWI Tavor X95 (330 mm barrel): 580 mm long bullpup
    p = "polymer_tan"
    m = new_gun("x95")
    body = m["body"]
    st = "steel_dark"
    body.rbox(-20, 20, -52, 22, -200, 250, p, r=8, edges="all")                        # body shell
    body.taper(-20, 20, 140, 250, -48, -48, -52, -102, p)                              # butt drop
    body.rbox(-21, 21, -106, 26, 250, 264, "rubber", r=6, edges="all")
    for i in range(5):
        body.box(-18, 18, -96 + i * 23, -90 + i * 23, 264, 264.6, "polymer")
    body.box(-20.4, 20.4, -18, -15, -196, 246, "rubber")                               # shell seam
    body.box(-10.5, 10.5, 22, 26, -192, 204, "alloy")
    body.rail(-190, 202, 26, mat="alloy", side="top")
    _buis(body, 184, 29, p, sy=62)
    _flip_front(body, -176, 29, p, sy=62)
    body.rbox(-19, 19, -44, 18, -234, -200, p, r=7, edges="all")                       # nose
    body.rail(-228, -110, -52, mat="alloy", side="bottom")
    for sx in (-1, 1):
        body.rail(-226, -150, -10, x=sx * 20, mat="alloy", side="right" if sx > 0 else "left", width=16)
        slot(body, sx * 20, 4, 8, -168, -60)                                           # charging slots
    barrel(body, -234, -282, d=17, mat=st)
    flash_hider_a2(body, -274, d=20, length=42)
    pistol_grip(body, -46, top_y=-52, length=88, width=28, depth=36, angle=-14, mat=p)
    trigger_group(m, body, -84, y_top=-52, guard_depth=28, guard_len=66, guard_mat=p)
    selector(body, (-20, -36, -30), mat=p, length=15, side=-1, turn=(-60, 0, 0))
    body.box(20, 22.6, -39, -33, -44, -28, p)
    button(body, "mag_release", (20, -44, -4), d=9, mat=st)
    ejection_port(body, 20, -4, 12, 100, 160, lip_mat=p)
    body.rbox(20, 25, -4, 14, 162, 180, p, r=2.4, axis="y", edges="all")               # case deflector
    body.rbox(-18, 18, -72, -52, 24, 98, p, r=2.4, axis="y", edges="all")              # magazine well
    control(body, "bolt_catch", (0, -72, 104), [(-6, 6, -76, -68, 98, 112, st)], press=(0, 3, 0))
    pins(body, 20, [(-6, -180), (-6, 120), (-34, 200)], d=5, mat="steel")
    side_swivel(body, -20, 6, 236, h=14)
    side_swivel(body, -19, 4, -224, h=12)
    ch = body.bone("charging_handle", pivot=(-20, 6, -150))
    ch.box(-28, -20, 3, 9, -156, -144, st)
    ch.rbox(-36, -28, 0, 12, -160, -140, p, r=2.4, axis="y", edges="all")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 19.6, -3, 11, 102, 158, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -56, 61))
    curved_mag(mag, -40, 32, 58, 170, curve=10, segs=5, width=22.5, mat="polymer", rib_mat="polymer_grey",
               round_d=9.6, round_len=57)
    add_arms(m, right_hand=(8, -104, -40), left_hand=(-10, -66, -170), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -318), optic=(0, 29, 0), under=(0, -57, -170), side=(-23, -10, -190),
                eject=(21, 4, 130), sight=(0, 62, 184))

    cyc = dict(bone="bolt", travel=(0, 0, 64), t_back=0.016, t_fwd=0.05)
    anims = _rifle_anims(m, 8.0, (2.2, 0.4, 1.0), 9, "ar", cyc, ch="charging_handle", ch_travel=(0, 0, 70),
                         selector=(-60, 0, 0), tilt=(4, -10, -30), tilt_pos=(-30, 14, 10))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.13, -0.16), ads=0.2))


# =================================================================================================
# Franchi SPAS-12 (pump mode)
# =================================================================================================
def spas12():
    m = new_gun("spas12")
    body = m["body"]
    st = "steel_dark"
    body.box(-18, 18, -32, 22, -110, 100, st)                                   # receiver
    body.box(0, 18.3, -6, 14, -80, -10, "rubber")
    body.box(-12, 12, -34, -32, -100, -20, "rubber")
    barrel(body, -110, -560, d=22, y=4)
    body.box(-14, 14, -4, 18, -420, -110, st)                                    # perforated heat shield
    for z in range(-410, -120, 26):
        body.box(-14.5, 14.5, 2, 12, z, z + 12, "rubber")
    body.cyl((0, -22, -320), 24, 420, st)                                        # magazine tube
    body.cyl((0, -22, -532), 28, 10, st)
    body.box(-6, 6, 18, 30, -546, -530, st)
    body.box(-6, 6, 22, 30, 60, 90, st)                                          # rear aperture
    pistol_grip(body, 110, top_y=-32, length=90, width=28, depth=36, angle=-16, mat="polymer")
    trigger_group(m, body, 30, y_top=-32, guard_depth=28, guard_len=64, guard_mat=st)
    sel = body.bone("selector", pivot=(0, -36, 70))
    sel.cyl((0, -36, 70), 8, 40, "steel", axis="x")
    stock = m["gun"].bone("stock", pivot=(0, 0, 100))                            # folding stock (folded down)
    for sx in (-12, 12):
        stock.box(sx - 3, sx + 3, -8, 2, 100, 340, "steel")
    stock.box(-14, 14, -10, 6, 330, 346, "steel")
    stock.box(-20, 20, -60, 6, 340, 352, "rubber")
    pump = m["gun"].bone("pump", pivot=(0, -22, -260))
    pump.box(-24, 24, -46, -4, -340, -180, "polymer")
    for z in range(-334, -186, 14):
        pump.box(-24.4, 24.4, -40, -10, z, z + 6, "rubber")
    pump.box(-6, -3, -14, -6, -180, -60, st)
    pump.box(3, 6, -14, -6, -180, -60, st)
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 17.8, -6, 12, -78, -20, "steel_light")
    _shells(m)
    add_arms(m, right_hand=(8, -86, 124), left_hand=(-10, -42, -260), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -562), optic=(0, 26, -20), eject=(18, 4, -50), sight=(0, 30, 76))
    anims = [idle(m), draw(m, 0.8, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8.5, 0.8, 2.0), push=25, recover=0.34, length=0.42),
             fire_basic(m, "fire_aim", kick=(8.5, 0.8, 2.0), push=25, recover=0.3, length=0.38, aim=True),
             pump_cycle(m, "cycle", travel=(0, 0, 90)), pump_cycle(m, "cycle_aim", travel=(0, 0, 90), aim=True),
             *tube_reload(m), _inspect(m), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, _fp(pos=(0.12, -0.13, -0.2), rot=(0, 3.5, 0), ads=0.13))


# =================================================================================================
# Atchisson AA-12 (box magazine, open bolt full auto)
# =================================================================================================
def aa12():
    m = new_gun("aa12")
    body = m["body"]
    st = "steel_dark"
    body.box(-22, 22, -40, 30, -260, 140, st)                                    # big square receiver tube
    body.box(-24, 24, -10, 8, -250, 130, st)                                     # ribs
    body.rail(-250, 120, 30, mat="alloy", side="top")
    body.box(0, 22.3, -6, 14, -60, 0, "rubber")
    barrel(body, -260, -470, d=24)
    body.cyl((0, 0, -476), 28, 14, st)
    body.box(-6, 6, 30, 60, -150, -140, st)                                      # carry-handle posts
    body.box(-6, 6, 30, 60, 60, 70, st)
    body.box(-8, 8, 56, 64, -150, 70, st)
    pistol_grip(body, 110, top_y=-40, length=92, width=30, depth=38, angle=-16, mat="polymer")
    trigger_group(m, body, 30, y_top=-40, guard_depth=30, guard_len=66, guard_mat=st)
    sel = body.bone("selector", pivot=(-22, -26, 80))
    sel.box(-25, -22, -30, -22, 74, 88, "steel")
    ch = body.bone("charging_handle", pivot=(-22, 14, -120))
    ch.box(-36, -22, 8, 20, -130, -110, "steel")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 22, -6, 12, -58, -2, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 140))
    stock.box(-18, 18, -20, 24, 140, 200, "polymer")
    stock.taper(-19, 19, 200, 360, 24, 18, -30, -92, "polymer")
    stock.box(-20, 20, -96, 22, 356, 368, "rubber")
    mag = m["gun"].bone("magazine", pivot=(0, -40, -100))
    mag.box(-26, 26, -150, -40, -140, -60, "polymer")                            # 8-round box
    mag.box(-27.5, 27.5, -156, -150, -142, -57, "polymer_grey")
    mag.shell12((0, -44, -86), length=64, d=19)
    add_arms(m, right_hand=(8, -100, 124), left_hand=(-10, -44, -220), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -484), optic=(0, 32, -60), eject=(22, 4, -30), sight=(0, 64, 66))
    cyc = dict(bone="bolt", travel=(0, 0, 70), t_back=0.02, t_fwd=0.07)
    anims = _rifle_anims(m, 0.0, (4.5, 0.6, 1.6), 16, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 80),
                         selector=(-40, 0, 0), rec=0.18, length=0.26, mag_sound="rifle")
    return GunAsset(m, anims, _fp(pos=(0.12, -0.14, -0.21), ads=0.15))


GUNS = {"vector": vector, "mp7": mp7, "g36c": g36c, "famas": famas, "x95": x95, "spas12": spas12, "aa12": aa12}
