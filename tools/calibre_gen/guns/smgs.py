"""H&K MP5A3, H&K UMP-45, IMI Uzi, FN P90."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden, along)
from ..templates import rifle_reload, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..common import moving
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, pins, vents, ejection_port,
                     side_swivel, sling_swivel, flash_hider_a2)
from ..longkit import (slot, top_slot, ribs, ring_sight, eared_sight, drum_sight, flip_sight, aperture_sight,
                       peep, rod_stock, selector, paddle, button, stock_solid)
from ..pistolkit import control


def _fp(pos=(0.115, -0.118, -0.2), rot=(0, 4, 0), ads=0.11):
    return {"hip": {"pos": list(pos), "rot": list(rot)}, "ads": {"dist": ads}}


# =================================================================================================
# MP5A3
# =================================================================================================
def mp5():
    # H&K MP5A3: 660 mm with the stock out (490 in), 225 mm barrel
    MAG_A = 8.0
    m = new_gun("mp5")
    body = m["body"]
    st, P = "steel_dark", "polymer"
    # stamped receiver with the rounded top, weld seam and pressed ribs
    body.chamfer_box(-15, 15, -22, 24, -200, 60, st, ch=6, edges="top")
    body.box(-2.5, 2.5, 24, 24.8, -196, 44, st)
    ribs(body, 15, -14, 10, (-176, -132, -34, 14), 12, "steel")
    ejection_port(body, 15, 0, 13, -96, -58, lip_mat=st)
    body.box(15, 16.6, 1, 12, -58, -52, "steel")                                   # port buffer
    body.chamfer_box(-15.4, 15.4, -22, 24.4, 58, 66, st, ch=6, edges="top")        # end cap
    for sx in (-1, 1):
        body.box(sx * 15.4 - 0.4, sx * 15.4 + 0.4, 0, 12, -24, 20, "steel")        # scope-claw cuts
    # cocking tube over the barrel, with the lever slot and its lock notch
    body.cyl((0, 14, -292), 23, 186, st)
    body.cyl((0, 14, -386.5), 25, 5, st)
    slot(body, -11.5, 12.5, 16.5, -378, -232)
    slot(body, -11.5, 16.5, 22, -244, -232)
    barrel(body, -200, -418, d=15, mat="steel")
    body.cyl((0, 0, -424), 17, 12, "steel")                                        # 3-lug muzzle
    for ang in (0, 120, 240):
        body.box(-3, 3, 7.5, 11, -428, -420, "steel", rot=(0, 0, ang), pivot=(0, 0, -424))
    body.cyl((0, 0, -430.3), 9, 0.6, "rubber", sides=8)
    body.box(-9, 9, -10, 26, -398, -384, st)                                       # front sight tower
    ring_sight(body, -391, 26, st, r=10, depth=14)
    drum_sight(body, 34, 24, st, d=20)                                             # line of sight y = 38
    # slim handguard
    body.chamfer_box(-17, 17, -34, 6, -368, -206, P, ch=7, edges="bottom")
    vents(body, 17, -24, -8, -360, -214, n=9, fill=0.5)
    body.box(-17.4, 17.4, -6, -3, -366, -208, "rubber")
    body.box(-6, 6, -38, -34, -366, -350, st)                                      # handguard pin lug
    # trigger housing, grip, guard, selector with its pictograms
    body.chamfer_box(-13.5, 13.5, -48, -22, -68, 58, P, ch=3, edges="bottom")
    pistol_grip(body, 30, top_y=-44, length=84, width=28, depth=36, angle=-14, mat=P)
    trigger_group(m, body, -24, y_top=-46, guard_depth=26, guard_len=56, guard_mat=P)
    selector(body, (-13.5, -30, 34), mat="steel", length=18, side=-1, turn=(-50, 0, 0))
    body.box(13.5, 14, -33, -27, 24, 40, "steel")                                  # right-side indicator
    pins(body, 15, [(-16, -84), (-16, 50)], d=5, mat="steel")
    # magazine well with the paddle release and the button
    body.box(-14, 14, -52, -22, -142, -96, st)
    body.box(-14.6, 14.6, -52, -49, -143, -95, st)
    paddle(body, (0, -50, -94), mat=st, w=16, h=8, d=10)
    body.cyl((15, -36, -100), 7, 2.4, "steel", axis="x", sides=8)
    # A3 retractable stock: fork over the end cap, rods along the receiver, butt plate
    stock = m["gun"].bone("stock", pivot=(0, 0, 60))
    stock.box(-18.5, 18.5, -8, 14, 52, 72, st)
    rod_stock(stock, -150, 214, 17.2, 3, "steel", -74, 18, butt_hw=17)
    stock.box(-4, 4, -26, -8, 62, 70, st)                                          # sling ring lug
    side_swivel(body, -15, 6, -384, h=14)
    side_swivel(body, -17.5, -4, 64, h=14)
    # cocking lever, bolt in the port
    ch = body.bone("charging_handle", pivot=(-12, 14, -352))
    ch.box(-24, -11.5, 11, 17, -358, -346, "steel")
    ch.cyl((-28, 14, -352), 13, 12, P, axis="x")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 14.5, 1, 12, -94, -60, "steel_light")
    bolt.box(12, 14.7, 4, 8, -64, -58, "steel")
    mag = m["gun"].bone("magazine", pivot=(0, -40, -120))
    curved_mag(mag, -24, -135, 32, 205, curve=13, segs=5, width=21, mat="steel_dark", rib_mat="steel", round_d=9.6,
               round_len=29)
    add_arms(m, right_hand=(8, -88, 46), left_hand=(-10, -44, -290), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -432), optic=(0, 25, -60), under=(0, -34, -290), side=(-17, -14, -290),
                eject=(16, 6, -76), sight=(0, 38, 40))


    cyc = dict(bone="bolt", travel=(0, 0, 30), t_back=0.012, t_fwd=0.04)
    anims = [
        idle(m), draw(m, 0.65, sound="draw_rifle"),
        fire_basic(m, "fire", kick=(2.6, 0.4, 1.2), push=9, cycle=cyc, recover=0.12, length=0.2),
        fire_basic(m, "fire_aim", kick=(2.6, 0.4, 1.2), push=9, cycle=cyc, recover=0.1, length=0.18, aim=True),
        rifle_reload(m, "reload", MAG_A, empty=False, style="hk", bolt="bolt", bolt_travel=(0, 0, 36),
                     ch_travel=(0, 0, 42), mag_sound="smg"),
        rifle_reload(m, "reload_empty", MAG_A, empty=True, style="hk", bolt="bolt", bolt_travel=(0, 0, 36),
                     ch="charging_handle", ch_travel=(0, 0, 42), bolt_hold_open=False, ch_hand="left",
                     mag_sound="smg"),
        firemode(m, selector_rot=(-50, 0, 0)), Anim(m, "inspect", 1.0), dry_fire(m),
    ]
    return GunAsset(m, anims, _fp())


# =================================================================================================
# UMP-45
# =================================================================================================
def ump45():
    # H&K UMP45: 690 mm with the stock open (450 folded), 200 mm barrel, polymer receiver
    MAG_A = 0.0
    m = new_gun("ump45")
    body = m["body"]
    P, st = "polymer", "steel_dark"
    body.chamfer_box(-19, 19, -12, 30, -330, 60, P, ch=7, edges="top")              # upper receiver / handguard shell
    body.chamfer_box(-19, 19, -36, -12, -330, -168, P, ch=6, edges="bottom")        # handguard belly
    vents(body, 19, -4, 12, -320, -190, n=6, fill=0.5)
    body.box(-19.4, 19.4, -14, -11, -326, 56, "rubber")                            # shell seam
    body.rail(-150, 30, 30, mat="alloy", side="top")
    body.rail(-320, -200, -36, mat="alloy", side="bottom")
    barrel(body, -330, -388, d=17, mat="steel")
    body.cyl((0, 0, -384), 20, 10, st)
    ejection_port(body, 19, 2, 16, -112, -66, lip_mat=P)
    # sights: hooded front on the shell, aperture rear
    eared_sight(body, -316, 30, 10, P, w=16, depth=14, lean=0)
    aperture_sight(body, 44, 30, P, w=16, h=13)
    # lower: trigger housing, grip, guard, ambidextrous selector, bolt catch
    body.chamfer_box(-15, 15, -40, -12, -84, 60, P, ch=3, edges="bottom")
    pistol_grip(body, 34, top_y=-38, length=86, width=29, depth=37, angle=-13, mat=P)
    trigger_group(m, body, -22, y_top=-40, guard_depth=27, guard_len=60, guard_mat=P)
    selector(body, (-15, -24, 36), mat=P, length=18, side=-1, turn=(-50, 0, 0))
    body.box(15, 18, -27, -21, 20, 38, P)
    control(body, "bolt_catch", (-15, -18, -40), [(-17.4, -15, -24, -12, -48, -32, st)], press=(0, 3, 0))
    pins(body, 15, [(-18, -76), (-18, 52)], d=5, mat="steel")
    # magazine well
    body.chamfer_box(-16, 16, -64, -12, -152, -100, P, ch=2.5, edges="bottom")
    paddle(body, (0, -60, -98), mat=P, w=16, h=8, d=10)
    # side-folding skeleton stock (open)
    stock = m["gun"].bone("stock", pivot=(-19, 0, 60))
    stock.box(-19, 19, -30, 28, 60, 74, P)                                         # hinge block
    stock.cyl((19, 0, 67), 8, 56, "steel", axis="y", sides=8)
    stock.box(-9, 9, 6, 20, 74, 276, P)                                            # upper strut
    stock.path([(74, -26), (150, -40), (276, -72)], 16, 10, P)                     # lower strut
    stock.box(-9, 9, -44, 8, 168, 180, P)                                          # brace
    stock.box(-17, 17, -84, 24, 274, 284, P)
    stock.box(-18, 18, -88, 26, 284, 296, "rubber")
    side_swivel(body, -19, 12, -300, h=14)
    ch = body.bone("charging_handle", pivot=(-19, 20, -292))
    ch.box(-30, -18.5, 17, 23, -298, -286, st)
    ch.cyl((-33, 20, -292), 12, 10, P, axis="x")
    slot(body, -19, 18.5, 21.5, -300, -214)
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 18.5, 3, 15, -110, -68, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -40, -126))
    straight_mag(mag, -36, -148, -104, 196, width=27, mat=P, base_mat=P, round_d=12, round_len=32, witness=False)
    for sx in (-1, 1):                                                             # clear witness strip
        mag.box(sx * 13.5 - 0.3, sx * 13.5 + 0.3, -216, -56, -112, -107, "polymer_clear")
        for i in range(5):
            mag.box(sx * 13.5 - 0.4, sx * 13.5 + 0.4, -76 - i * 28, -72 - i * 28, -111.6, -107.4, "brass")
    add_arms(m, right_hand=(8, -84, 50), left_hand=(-10, -48, -250), right_rot=(34, 14, 6), left_rot=(22, -18, -4))
    add_sockets(m, muzzle=(0, 0, -390), optic=(0, 33, -60), under=(0, -39, -260), side=(-21, 4, -270),
                eject=(19, 8, -88), sight=(0, 38.5, 44))


    cyc = dict(bone="bolt", travel=(0, 0, 32), t_back=0.016, t_fwd=0.05)
    anims = [
        idle(m), draw(m, 0.65, sound="draw_rifle"),
        fire_basic(m, "fire", kick=(3.6, 0.5, 1.4), push=11, cycle=cyc, recover=0.14, length=0.24),
        fire_basic(m, "fire_aim", kick=(3.6, 0.5, 1.4), push=11, cycle=cyc, recover=0.12, length=0.2, aim=True),
        rifle_reload(m, "reload", MAG_A, empty=False, style="smg", mag_sound="smg"),
        rifle_reload(m, "reload_empty", MAG_A, empty=True, style="smg", bolt="bolt", bolt_travel=(0, 0, 32),
                     ch="charging_handle", ch_travel=(0, 0, 70), bolt_hold_open=False, ch_hand="left", mag_sound="smg"),
        firemode(m, selector_rot=(-50, 0, 0)), Anim(m, "inspect", 1.0), dry_fire(m),
    ]
    return GunAsset(m, anims, _fp())


# =================================================================================================
# Uzi
# =================================================================================================
def uzi():
    # IMI Uzi: 650 mm with the stock open (470 folded), 260 mm barrel, magazine in the grip
    A = 0.0
    m = new_gun("uzi")
    body = m["body"]
    st = "steel_parked"
    body.box(-23, 23, -28, 22, -215, 160, st)                                      # stamped receiver
    ribs(body, 23, -22, 16, (-196, -150, 60, 106), 26, st, proud=0.9)              # pressed panels
    body.chamfer_box(-21, 21, 22, 29, -213, 158, st, ch=2.5, edges="top")          # top cover
    top_slot(body, 29, -3, 3, -160, -30)                                           # cocking slot
    body.box(-6, 6, 29, 30.5, 60, 100, st)                                         # cover latch
    ejection_port(body, 23, -4, 12, -72, -22, lip_mat=st)
    body.cyl((0, -2, -222), 34, 16, "steel_dark")                                  # barrel nut
    for ang in range(0, 180, 30):
        body.box(-17.4, 17.4, -3, -1, -229, -216, "rubber", rot=(0, 0, ang), pivot=(0, -2, -222))
    barrel(body, -215, -310, d=17, mat="steel_dark", y=-2)
    eared_sight(body, -196, 29, 13, st, w=20, depth=14)
    flip_sight(body, 128, 29, st, w=12, h=14)
    for sx in (-1, 1):                                                             # ribbed handguard panels
        xs = sorted((sx * 23, sx * 27))
        body.box(xs[0], xs[1], -30, -4, -205, -62, "polymer")
    vents(body, 27, -26, -8, -200, -66, n=10, fill=0.45, proud=0.3)
    # grip frame with the magazine well, grip safety, guard, sliding selector
    body.box(-17, 17, -44, -28, -70, 60, st)
    gp = (0, -44, 22)
    r = dict(rot=(-4, 0, 0), pivot=gp)
    body.box(-16, 16, -134, -44, 2, 44, st, **r)
    for sx in (-1, 1):
        xs = sorted((sx * 16, sx * 19))
        body.box(xs[0], xs[1], -130, -50, 0, 46, "polymer", **r)                   # grip scales
        for i in range(6):
            body.box(sx * 19 - 0.3, sx * 19 + 0.3, -124 + i * 12, -119 + i * 12, 4, 42, "rubber", **r)
    gs = body.bone("grip_safety", pivot=(0, -60, 46))
    gs.box(-8, 8, -112, -56, 44, 49, "polymer", **r)
    moving(m, "grip_safety", pos=(0, 0, -3))
    body.box(-17.4, 17.4, -138, -132, 0, 46, st, **r)                              # mag well mouth
    trigger_group(m, body, -30, y_top=-44, guard_depth=28, guard_len=60, guard_mat=st)
    sel = body.bone("selector", pivot=(-19, -38, 20))
    sel.box(-21.5, -19, -41, -35, 12, 28, "polymer")
    sel.box(-22.2, -21.5, -40, -36, 14, 20, "steel")
    slot(body, -17, -40, -36, 2, 40)
    button(body, "mag_release", (-19, -128, 22), d=10, mat="steel_dark")
    pins(body, 23, [(-18, -40), (-18, 140)], d=5, mat="steel_dark")
    side_swivel(body, -23, 6, -190, h=14)
    side_swivel(body, -23, 6, 140, h=14)
    # folding stock, open: two struts and the butt plate
    stock = m["gun"].bone("stock", pivot=(0, -20, 160))
    stock.box(-14, 14, -30, -10, 152, 166, "steel_dark")
    for sx in (-1, 1):
        stock.path([(160, -20), (250, -34), (336, -40)], 5, 8, "steel_dark", x=sx * 11)
    stock.box(-14, 14, -40, -30, 244, 256, "steel_dark")                           # hinge of the two halves
    stock.box(-17, 17, -92, -4, 332, 342, "steel_dark")
    for i in range(5):
        stock.box(-15, 15, -86 + i * 17, -80 + i * 17, 342, 343, "steel")
    ch = body.bone("charging_handle", pivot=(0, 30, -120))
    ch.cyl((0, 36, -120), 20, 10, "polymer", axis="y")
    ch.box(-3, 3, 29, 33, -124, -116, st)
    top_slot(ch, 41, -1.5, 1.5, -128, -112)
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 22.5, -3, 11, -70, -24, "steel_light")
    bolt.box(21, 22.7, 2, 6, -30, -24, "steel")
    mag = m["gun"].bone("magazine", pivot=(0, -60, 22), rot=(-4, 0, 0))
    straight_mag(mag, -44, 6, 38, 232, width=22, mat="steel_dark", round_d=9.6, round_len=29)
    add_arms(m, right_hand=(8, -92, 30), left_hand=(-12, -44, -140), right_rot=(34, 14, 6), left_rot=(24, -18, -4))
    add_sockets(m, muzzle=(0, -2, -312), eject=(23, 4, -46), sight=(0, 40, 128))


    cyc = dict(bone="bolt", travel=(0, 0, 34), t_back=0.02, t_fwd=0.07)
    anims = [
        idle(m), draw(m, 0.6, sound="draw_rifle"),
        fire_basic(m, "fire", kick=(3.0, 0.6, 1.8), push=10, cycle=cyc, recover=0.14, length=0.22),
        fire_basic(m, "fire_aim", kick=(3.0, 0.6, 1.8), push=10, cycle=cyc, recover=0.12, length=0.2, aim=True),
        rifle_reload(m, "reload", A, empty=False, style="smg", mag_out=120, mag_sound="smg",
                     tilt=(10, -8, -24), tilt_pos=(-26, 20, 30)),
        rifle_reload(m, "reload_empty", A, empty=True, style="smg", mag_out=120, bolt="bolt", bolt_travel=(0, 0, 34),
                     ch="charging_handle", ch_travel=(0, 0, 80), bolt_hold_open=False, ch_hand="left", mag_sound="smg",
                     tilt=(10, -8, -24), tilt_pos=(-26, 20, 30)),
        firemode(m, selector_rot=(0, 0, 0)), Anim(m, "inspect", 1.0), dry_fire(m),
    ]
    # selector on the Uzi slides: override with a translation
    anims[-3].key("selector", 0.19, pos=(0, 0, 0))
    anims[-3].key("selector", 0.23, pos=(0, 0, -6), e="outquad")
    anims[-3].key("selector", 0.55, pos=(0, 0, -6))
    return GunAsset(m, anims, _fp(pos=(0.11, -0.115, -0.24), ads=0.2))


# =================================================================================================
# P90
# =================================================================================================
def p90():
    # FN P90: 505 mm long bullpup, 264 mm barrel, 50-round magazine lying on top
    m = new_gun("p90")
    body = m["body"]
    P, al = "polymer", "alloy"
    body.chamfer_box(-27, 27, -24, 22, -250, 200, P, ch=7, edges="all")             # body
    body.chamfer_box(-27, 27, -86, -22, 62, 200, P, ch=8, edges="bottom")           # butt
    body.box(-28, 28, -90, 26, 200, 207, "rubber")                                 # butt plate
    for i in range(5):
        body.box(-25, 25, -80 + i * 20, -72 + i * 20, 207, 207.6, P)
    # main grip and the thumb hole behind it
    gp = (0, -22, -36)
    r = dict(rot=(-12, 0, 0), pivot=gp)
    body.box(-17, 17, -112, -22, -54, -18, P, **r)
    body.box(-15, 15, -112, -22, -56.5, -54, P, **r)
    body.box(-15, 15, -112, -22, -18, -15.5, P, **r)
    for i in range(5):
        body.box(-17.5, 17.5, -104 + i * 16, -97 + i * 16, -50, -22, P, **r)
    body.box(-20, 20, -112, -98, -24, 74, P)                                       # bottom bar closing the thumb hole
    body.box(-20, 20, -100, -84, 56, 76, P)
    # the big guard that doubles as the support-hand grip
    body.path([(-214, -22), (-196, -70), (-170, -100), (-70, -104), (-40, -96)], 40, 11, P)
    body.box(-20, 20, -62, -22, -132, -112, P, rot=(10, 0, 0), pivot=(0, -22, -122))   # front web / thumb rest
    body.box(-27.4, 27.4, -4, 0, -240, 190, "rubber")                              # moulding seam
    body.box(-12, 12, -26, -22, 76, 132, "rubber")                                 # ejection chute (underneath)
    # upper receiver with the integrated sight, back-up notches either side
    body.chamfer_box(-20, 20, 22, 34, -236, 44, al, ch=3, edges="top")
    body.box(-13, 13, 34, 48, -130, -66, al)                                       # reflex sight: an open housing
    for sx in (-1, 1):
        xs = sorted((sx * 9.5, sx * 13))
        body.box(xs[0], xs[1], 48, 76, -136, -60, al)
    body.chamfer_box(-13, 13, 72, 78, -136, -60, al, ch=2.5, edges="top")
    body.box(-9.5, 9.5, 48, 51, -136, -60, al)
    body.box(-0.7, 0.7, 61.3, 62.7, -120.5, -119.5, "sight_orange")                # the dot
    body.box(-0.25, 0.25, 51, 61.3, -120.2, -119.8, "steel_dark")
    for sx in (-1, 1):
        body.box(sx * 13, sx * 13 + sx * 3, 72, 78, -110, -86, al)
    barrel(body, -250, -278, d=14, mat="steel")
    flash_hider_a2(body, -272, d=19, length=34)
    selector_d = body.bone("selector", pivot=(0, -56, -74))                         # rotary selector under the trigger
    selector_d.cyl((0, -56, -74), 22, 5, "steel_dark", axis="y")
    selector_d.box(-2, 2, -59.2, -58.5, -86, -74, "white")
    trig = body.bone("trigger", pivot=(0, -24, -80))
    trig.box(-3.5, 3.5, -50, -24, -84, -78, "steel_dark", rot=(6, 0, 0), pivot=(0, -24, -80))
    trig.box(-3.5, 3.5, -62, -48, -88, -82, "steel_dark", rot=(22, 0, 0), pivot=(0, -48, -82))
    for sx in (-1, 1):                                                             # ambidextrous mag release tabs
        body.box(sx * 20, sx * 20 + sx * 3, 24, 32, 46, 62, P)
    pins(body, 27, [(8, -200), (8, 150)], d=5, mat="steel_dark")
    side_swivel(body, -27, 10, -226, h=14)
    side_swivel(body, -27, 6, 180, h=14)
    ch = body.bone("charging_handle", pivot=(0, 12, -160))
    for sx in (-1, 1):
        ch.box(sx * 27, sx * 27 + sx * 7, 8, 16, -170, -150, P)
        ch.box(sx * 34, sx * 34 + sx * 3, 6, 18, -172, -148, P)
        slot(body, sx * 27, 10, 14, -172, -90)
    # translucent magazine on top: rounds lie across it
    mag = m["gun"].bone("magazine", pivot=(0, 34, -70))
    mag.chamfer_box(-25, 25, 34, 50, -196, 70, "polymer_clear", ch=3, edges="top")
    mag.box(-23, 23, 50, 52.5, -190, 20, "polymer_clear")
    mag.box(-22, 22, 30, 50, 44, 70, P)                                            # feed tower
    for i in range(12):
        z = -186 + i * 18
        mag.box(-18, 12, 49.6, 51, z, z + 6, "brass")
        mag.box(12, 20, 49.8, 50.8, z + 1, z + 5, "copper")
    mag.box(-25.4, 25.4, 38, 46, -196, -190, P)
    add_arms(m, right_hand=(8, -78, -30), left_hand=(-12, -64, -150), right_rot=(34, 14, 6), left_rot=(26, -18, -4))
    add_sockets(m, muzzle=(0, 0, -308), optic=None, eject=None, sight=(0, 62, -50))


    def reload(name, empty):
        L = 2.8 if empty else 2.5
        a = Anim(m, name, L)
        a.mv("gun", 0.0, 0.32, pos=(-30, 10, 30), rot=(-10, -8, -30))
        # support hand reaches over to the rear of the magazine & presses the release
        a.mv("arm_left", 0.05, 0.35, pos=(20, 130, 300), rot=(-50, 30, 40))
        a.grab("arm_left", "magazine", 0.4, 0.9, fade_in=0.03, fade_out=0.06)
        a.key("magazine", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("magazine", 0.42, pos=(0, 0, 0), rot=(0, 0, 0))
        a.sound(0.42, "mag_release")
        a.key("magazine", 0.55, pos=(0, 6, 4), rot=(8, 0, 0), e="outquad")          # rear pops up
        a.key("magazine", 0.68, pos=(0, 16, 40), rot=(10, 0, 0), e="inoutsine")
        a.sound(0.66, "mag_out_p90")
        a.key("magazine", 0.9, pos=(-80, 60, 160), rot=(30, 20, 40), e="inoutsine")
        a.mv("arm_left", 0.92, 1.15, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
        a.key("magazine", 1.15, pos=(-80, -300, 200), rot=(30, 20, 40))
        a.grab("arm_left", "magazine", 1.18, 1.95, fade_in=0.05, fade_out=0.08)
        a.key("magazine", 1.55, pos=(0, 30, 30), rot=(10, 0, 0), e="outcubic")
        a.key("magazine", 1.7, pos=(0, 8, 0), rot=(8, 0, 0), e="inoutsine")          # hook the front
        a.key("magazine", 1.85, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")            # press the rear down
        a.sound(1.85, "mag_in_p90")
        a.event(1.85, "ammo")
        a.spring("gun", "rot", 1.85, (-2.0, 0, 1.0), freq=6, damp=9)
        t = 1.95
        if empty:
            a.mv("arm_left", t, t + 0.2, pos=(-14, 30, 30), rot=(10, 0, 0))
            a.grab("arm_left", "charging_handle", t + 0.2, t + 0.44, fade_in=0.02, fade_out=0.06)
            a.key("charging_handle", t + 0.2, pos=(0, 0, 0))
            a.key("charging_handle", t + 0.32, pos=(0, 0, 70), e="inoutquad")
            a.sound(t + 0.3, "charging_handle_back")
            a.key("charging_handle", t + 0.38, pos=(0, 0, 0), e="inquad")
            a.sound(t + 0.38, "charging_handle_forward")
            a.mv("arm_left", t + 0.44, t + 0.7, pos=(0, 0, 0), rot=(0, 0, 0))
            _settle(a, t + 0.4, L - 0.02)
        else:
            a.mv("arm_left", t, t + 0.4, pos=(0, 0, 0), rot=(0, 0, 0))
            _settle(a, t, L - 0.02)
        return a

    anims = [
        idle(m), draw(m, 0.6, sound="draw_rifle"),
        fire_basic(m, "fire", kick=(2.2, 0.3, 0.9), push=8, recover=0.1, length=0.18),
        fire_basic(m, "fire_aim", kick=(2.2, 0.3, 0.9), push=8, recover=0.08, length=0.16, aim=True),
        reload("reload", False), reload("reload_empty", True),
        firemode(m, selector_rot=(0, 90, 0)), Anim(m, "inspect", 1.0), dry_fire(m),
    ]
    return GunAsset(m, anims, _fp(pos=(0.12, -0.105, -0.26), ads=0.12))


GUNS = {"mp5": mp5, "ump45": ump45, "uzi": uzi, "p90": p90}
