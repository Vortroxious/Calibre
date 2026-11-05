"""H&K MP5A3, H&K UMP-45, IMI Uzi, FN P90."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden, along)
from ..templates import rifle_reload, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import pistol_grip, trigger_group, curved_mag, straight_mag, barrel


def _fp(pos=(0.115, -0.118, -0.2), rot=(0, 4, 0), ads=0.11):
    return {"hip": {"pos": list(pos), "rot": list(rot)}, "ads": {"dist": ads}}


# =================================================================================================
# MP5A3
# =================================================================================================
def mp5():
    MAG_A = 8.0
    m = new_gun("mp5")
    body = m["body"]
    st = "steel_dark"
    # stamped receiver
    body.box(-15, 15, -20, 16, -230, 58, st)
    body.box(-12, 12, 16, 20, -230, 50, st)                                # top weld seam
    for z in (-150, -60, 10):
        body.box(-15.4, 15.4, -16, 12, z, z + 18, "steel")                   # stamped ribs
    body.box(0, 15.3, -4, 10, -70, -30, "rubber")                           # ejection port
    # cocking tube + barrel + handguard
    body.cyl((0, 10, -300), 22, 150, st)
    body.cyl((0, -4, -330), 16, 220, "steel")
    body.box(-17, 17, -30, 4, -380, -230, "polymer")                       # slim handguard
    for z in range(-372, -236, 16):
        body.box(-17.4, 17.4, -24, -6, z, z + 8, "rubber")
    body.cyl((0, -4, -452), 18, 14, "steel")                                # 3-lug muzzle
    for ang in (0, 120, 240):
        body.box(-3, 3, 5, 10, -456, -446, "steel", rot=(0, 0, ang), pivot=(0, -4, -451))
    # hooded front sight
    body.box(-10, 10, 18, 22, -390, -370, st)
    body.box(-10, -7, 22, 40, -388, -372, st)
    body.box(7, 10, 22, 40, -388, -372, st)
    body.box(-10, 10, 38, 41, -388, -372, st)
    body.box(-1.2, 1.2, 22, 33, -381, -379, st)
    # drum rear sight
    body.box(-12, 12, 20, 26, 26, 52, st)
    body.cyl((0, 34, 40), 22, 14, st, axis="x", sides=12)
    body.box(-2, 2, 36, 40, 32, 33, "rubber")
    body.box(-14, 14, 20, 24, -130, -100, st)                                # claw mount bump
    # lower (Navy trigger group)
    lower = body
    lower.box(-13, 13, -40, -20, -60, 60, "polymer")
    pistol_grip(lower, 28, top_y=-38, length=86, width=30, depth=38, angle=-14, mat="polymer")
    trigger_group(m, lower, -6, y_top=-40, guard_depth=28, guard_len=58, guard_mat="polymer")
    sel = lower.bone("selector", pivot=(-14, -30, 38))
    sel.box(-17, -14, -34, -26, 32, 46, "steel")
    sel.box(-18, -15, -36, -24, 44, 48, "steel")
    # mag well
    body.box(-14, 14, -40, -20, -110, -62, st)
    body.box(-15.5, -13, -46, -40, -66, -58, st)                             # paddle release
    # retractable A3 stock
    stock = m["gun"].bone("stock", pivot=(0, 0, 58))
    for sx in (-12, 12):
        stock.box(sx - 3, sx + 3, -6, 2, 58, 270, "steel")
    stock.box(-18, 18, -70, 10, 260, 276, st)
    stock.box(-20, 20, -76, 12, 274, 286, "rubber")
    # cocking lever (HK) - charging handle on the left of the tube
    ch = body.bone("charging_handle", pivot=(-12, 10, -350))
    ch.box(-30, -12, 6, 14, -358, -346, "steel")
    ch.box(-34, -28, 4, 16, -360, -344, "polymer")
    # bolt visible through the port
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 14.5, -2, 8, -68, -32, "steel_light")
    # magazine (curved 30 rd 9mm)
    mag = m["gun"].bone("magazine", pivot=(0, -40, -100))
    curved_mag(mag, -36, -106, 30, 220, curve=14, segs=4, width=22, mat="steel_dark", rib_mat="steel", round_d=9,
               round_len=29)
    add_arms(m, right_hand=(8, -84, 50), left_hand=(-10, -40, -310), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, -4, -460), optic=(0, 24, -40), under=(0, -30, -320), side=(-17, -14, -300),
                eject=(16, 4, -50), sight=(0, 38, 46))

    def inspect():
        a = Anim(m, "inspect", 4.4)
        # HK slap check: lock the lever, peek into the port, slap it home
        a.mv("gun", 0.0, 0.35, pos=(-24, 26, 40), rot=(6, -10, -30))
        a.mv("arm_left", 0.05, 0.35, pos=(-14, 54, -40), rot=(-10, -10, 20))
        a.grab("arm_left", "charging_handle", 0.35, 0.85, fade_in=0.03, fade_out=0.04)
        a.key("charging_handle", 0.35, pos=(0, 0, 0))
        a.key("charging_handle", 0.52, pos=(0, 0, 42), e="inoutquad")
        a.key("bolt", 0.35, pos=(0, 0, 0))
        a.key("bolt", 0.52, pos=(0, 0, 36), e="inoutquad")
        a.sound(0.5, "charging_handle_back")
        a.mv("gun", 0.55, 0.85, pos=(-40, 30, 50), rot=(10, -30, -60))     # peek at the chamber
        a.key("charging_handle", 0.95, pos=(0, 0, 42))
        a.key("charging_handle", 1.0, pos=(0, 0, 0), e="inquad")
        a.key("bolt", 0.95, pos=(0, 0, 36))
        a.key("bolt", 1.0, pos=(0, 0, 0), e="inquad")
        a.mv("arm_left", 0.86, 0.95, pos=(-10, 74, -80), rot=(-20, -10, 30))
        a.mv("arm_left", 0.95, 1.0, pos=(-10, 50, -40), rot=(-20, -10, 30), e="inquad")
        a.sound(1.0, "hk_slap")
        a.spring("gun", "rot", 1.0, (2.4, 0, -2.0), freq=6, damp=8)
        # look at the drum sight
        a.mv("arm_left", 1.1, 1.5, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 1.2, 1.9, pos=(-60, 20, 60), rot=(-14, 40, 24), e="inoutsine")
        a.wave("gun", "rot", (0.5, 0.6, 0.3), 1.6)
        a.mv("arm_right", 2.2, 2.32, pos=(-4, 30, 10), rot=(0, -6, 0))
        a.sound(2.35, "click_small")
        a.mv("arm_right", 2.4, 2.55, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 2.6, 3.2, pos=(-30, 40, 50), rot=(20, -40, -40), e="inoutsine")
        _settle(a, 3.4, 4.35)
        return a

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
        firemode(m, selector_rot=(-50, 0, 0)), inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, _fp())


# =================================================================================================
# UMP-45
# =================================================================================================
def ump45():
    MAG_A = 0.0
    m = new_gun("ump45")
    body = m["body"]
    p = "polymer"
    body.box(-17, 17, -36, 24, -250, 60, p)
    body.box(-17.5, 17.5, -30, 18, -250, -150, p)
    for z in range(-244, -156, 14):
        body.box(-17.8, 17.8, -24, 10, z, z + 7, "rubber")                    # vent slots
    body.rail(-240, 50, 24, mat="alloy")
    body.rail(-240, -160, -36, mat="alloy", side="bottom")
    body.rail(-240, -170, -6, x=-17.5, mat="alloy", side="left", width=16)
    body.rail(-240, -170, -6, x=17.5, mat="alloy", side="right", width=16)
    body.cyl((0, 0, -278), 18, 56, "steel")
    body.cyl((0, 0, -300), 22, 14, "steel_dark")
    body.box(0, 17.3, -2, 14, -80, -40, "rubber")
    pistol_grip(body, 28, top_y=-36, length=88, width=30, depth=40, angle=-14, mat=p)
    trigger_group(m, body, -8, y_top=-36, guard_depth=30, guard_len=60, guard_mat=p)
    body.box(-17, 17, -60, -36, -120, -60, p)                               # mag well
    sel = body.bone("selector", pivot=(-17, -26, 36))
    sel.box(-20, -17, -30, -22, 30, 44, "steel")
    # rear sight / front sight (flip-up style blocks)
    body.box(-10, 10, 27, 40, 30, 46, "alloy")
    body.box(-8, 8, 27, 44, -236, -226, "alloy")
    # folding stock (folds to the right)
    stock = m["gun"].bone("stock", pivot=(14, 0, 60))
    stock.box(-14, 14, -20, 14, 60, 130, p)
    stock.taper(-14, 14, 130, 290, 14, 14, -40, -62, p)
    stock.box(-14, 14, -30, -8, 150, 260, "rubber")                         # skeleton cut-out look
    stock.box(-15, 15, -64, 16, 286, 300, "rubber")
    # charging handle: front left
    ch = body.bone("charging_handle", pivot=(-17, 8, -220))
    ch.box(-34, -17, 4, 12, -226, -214, "polymer")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.8, 0, 12, -76, -44, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -40, -100))
    straight_mag(mag, -38, -114, -66, 200, width=26, mat="polymer", round_d=11, round_len=30)
    add_arms(m, right_hand=(8, -84, 50), left_hand=(-10, -48, -200), right_rot=(34, 14, 6), left_rot=(22, -18, -4))
    add_sockets(m, muzzle=(0, 0, -306), optic=(0, 27, -60), under=(0, -39, -210), side=(-21, -6, -210),
                eject=(17, 6, -60), sight=(0, 42, 46))

    def inspect():
        a = Anim(m, "inspect", 4.2)
        # fold and unfold the stock
        a.mv("gun", 0.0, 0.45, pos=(-60, 30, 60), rot=(4, -50, -20), e="inoutsine")
        a.mv("arm_left", 0.1, 0.45, pos=(60, 40, 280), rot=(-10, 60, 10))
        a.grab("arm_left", "stock", 0.48, 1.4, fade_in=0.04, fade_out=0.06)
        a.key("stock", 0.0, rot=(0, 0, 0))
        a.key("stock", 0.5, rot=(0, 0, 0))
        a.key("stock", 0.58, rot=(0, 8, 0), e="outquad")
        a.sound(0.56, "stock_unlock")
        a.key("stock", 1.2, rot=(0, 172, 0), e="inoutsine")
        a.key("stock", 1.3, rot=(0, 176, 0), e="inquad")
        a.sound(1.3, "stock_lock")
        a.spring("gun", "rot", 1.3, (0, 1.5, 0), freq=6, damp=9)
        a.mv("gun", 1.4, 2.0, pos=(-50, 40, 40), rot=(10, 30, 20))
        a.key("stock", 2.1, rot=(0, 176, 0))
        a.grab("arm_left", "stock", 2.1, 2.9, fade_in=0.2, fade_out=0.06)
        a.key("stock", 2.2, rot=(0, 168, 0), e="outquad")
        a.sound(2.18, "stock_unlock")
        a.key("stock", 2.75, rot=(0, 4, 0), e="inoutsine")
        a.key("stock", 2.82, rot=(0, 0, 0), e="inquad")
        a.sound(2.82, "stock_lock")
        a.mv("arm_left", 2.95, 3.4, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.1, 4.15)
        return a

    cyc = dict(bone="bolt", travel=(0, 0, 32), t_back=0.016, t_fwd=0.05)
    anims = [
        idle(m), draw(m, 0.65, sound="draw_rifle"),
        fire_basic(m, "fire", kick=(3.6, 0.5, 1.4), push=11, cycle=cyc, recover=0.14, length=0.24),
        fire_basic(m, "fire_aim", kick=(3.6, 0.5, 1.4), push=11, cycle=cyc, recover=0.12, length=0.2, aim=True),
        rifle_reload(m, "reload", MAG_A, empty=False, style="smg", mag_sound="smg"),
        rifle_reload(m, "reload_empty", MAG_A, empty=True, style="smg", bolt="bolt", bolt_travel=(0, 0, 32),
                     ch="charging_handle", ch_travel=(0, 0, 70), bolt_hold_open=False, ch_hand="left", mag_sound="smg"),
        firemode(m, selector_rot=(-50, 0, 0)), inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, _fp())


# =================================================================================================
# Uzi
# =================================================================================================
def uzi():
    A = -6.0
    m = new_gun("uzi")
    body = m["body"]
    st = "steel_parked"
    body.box(-17, 17, -22, 18, -230, 80, st)
    for z in range(-210, 60, 40):
        body.box(-17.3, 17.3, -16, 12, z, z + 22, st)                         # side grooves
    body.cyl((0, -2, -250), 16, 44, "steel")
    body.cyl((0, -2, -262), 22, 10, st)                                     # barrel nut
    body.box(0, 17.2, -4, 10, -80, -36, "rubber")
    body.box(-17, 17, -40, -22, -190, -110, "polymer")                     # front grip (wood/polymer)
    # sight towers
    body.box(-10, 10, 18, 34, -214, -204, st)
    body.box(-1, 1, 30, 38, -210, -208, st)
    body.box(-12, 12, 18, 34, 56, 66, st)
    body.box(-2, 2, 30, 34, 56, 56.5, "rubber")
    # top cover
    cover = body.bone("cover", pivot=(0, 18, 80))
    cover.box(-16, 16, 18, 22, -200, 80, st)
    # grip with mag inside + grip safety
    gp = (0, -22, 0)
    body.box(-16, 16, -130, -22, -26, 22, "polymer", rot=(A, 0, 0), pivot=gp)
    body.box(-18, 18, -140, -128, -28, 24, st, rot=(A, 0, 0), pivot=gp)
    gs = body.bone("grip_safety", pivot=(0, -40, 22))
    gs.box(-8, 8, -90, -36, 22, 28, st, rot=(A, 0, 0), pivot=(0, -40, 22))
    trigger_group(m, body, -40, y_top=-22, guard_depth=30, guard_len=56, guard_mat=st)
    sel = body.bone("selector", pivot=(-17, -28, 0))
    sel.box(-21, -17, -32, -24, -6, 6, "steel")
    # folded metal stock under the receiver
    stock = m["gun"].bone("stock", pivot=(0, -12, 80))
    for sx in (-14, 14):
        stock.box(sx - 3, sx + 3, -20, -14, -120, 84, "steel")
    stock.box(-16, 16, -24, -12, -130, -110, "steel")
    ch = cover.bone("charging_handle", pivot=(0, 22, 10))
    ch.box(-6, 6, 22, 32, 4, 18, "steel")
    ch.box(-9, 9, 30, 34, 2, 20, "steel")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.8, -2, 8, -76, -40, "steel_light")
    mag = m["gun"].bone("magazine", pivot=gp, rot=(A, 0, 0))
    straight_mag(mag, -24, -14, 14, 220, width=20, mat="steel_dark", round_d=9, round_len=29)
    add_arms(m, right_hand=(8, -80, 26), left_hand=(-10, -44, -150), right_rot=(34, 14, 6), left_rot=(24, -18, -4))
    add_sockets(m, muzzle=(0, -2, -268), eject=(17, 4, -60), sight=(0, 33, 62))

    def inspect():
        a = Anim(m, "inspect", 3.9)
        # tilt to look along the top cover, push the cocking knob a hair
        a.mv("gun", 0.0, 0.5, pos=(-40, 30, 70), rot=(-28, -12, -24), e="inoutsine")
        a.mv("arm_left", 0.2, 0.55, pos=(-4, 80, 110), rot=(-40, 0, 30))
        a.grab("arm_left", "charging_handle", 0.55, 0.95, fade_in=0.03, fade_out=0.05)
        a.key("charging_handle", 0.55, pos=(0, 0, 0))
        a.key("charging_handle", 0.75, pos=(0, 0, 18), e="inoutsine")
        a.key("charging_handle", 0.95, pos=(0, 0, 0), e="inoutsine")
        a.sound(0.72, "charging_handle_back")
        # rotate, squeeze the grip safety
        a.mv("arm_left", 1.0, 1.35, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 1.0, 1.7, pos=(-50, 34, 30), rot=(10, -48, -10))
        a.key("grip_safety", 0.0, rot=(0, 0, 0))
        a.key("grip_safety", 1.9, rot=(0, 0, 0))
        a.key("grip_safety", 1.98, rot=(-10, 0, 0), e="outquad")
        a.sound(1.98, "click_small")
        a.key("grip_safety", 2.3, rot=(-10, 0, 0))
        a.key("grip_safety", 2.36, rot=(0, 0, 0), e="outquad")
        a.sound(2.36, "click_small")
        a.mv("arm_right", 1.9, 2.0, pos=(0, 2, -4), rot=(-4, 0, 0))
        a.mv("arm_right", 2.3, 2.4, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 2.7, 3.85)
        return a

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
        firemode(m, selector_rot=(0, 0, 0)), inspect(), dry_fire(m),
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
    m = new_gun("p90")
    body = m["body"]
    p = "polymer"
    # main shell (bullpup: grip far forward, action behind it)
    body.box(-26, 26, -56, 24, -220, 250, p)
    body.box(-24, 24, -100, -56, 140, 250, p)                               # butt
    body.box(-25, 25, -106, -96, 150, 252, "rubber")
    body.box(-24, 24, -60, -10, -260, -220, p)                              # nose under the barrel
    body.cyl((0, -8, -282), 18, 50, "steel")
    body.cyl((0, -8, -300), 22, 12, p)
    # thumbhole grip / hand stop
    body.box(-20, 20, -120, -56, -30, 10, p)
    body.box(-22, 22, -126, -116, -40, 60, p)
    body.box(-20, 20, -120, -56, 60, 110, p)
    body.box(-22, 22, -92, -56, -190, -160, p)                              # front hand stop
    # integrated optic housing
    body.box(-16, 16, 24, 62, -60, 40, p)
    body.box(-12, 12, 40, 58, -61, -59, "glass")
    body.box(-12, 12, 40, 58, 39, 41, "glass")
    body.box(-1, 1, 46, 52, -10, -9, "emissive_red")
    trigger_group(m, body, -80, y_top=-56, guard_depth=0.1, guard_len=4, guard_mat=p)
    # charging handles under the front, both sides
    ch = body.bone("charging_handle", pivot=(0, -40, -150))
    ch.box(-32, -26, -44, -36, -156, -144, "polymer_grey")
    ch.box(26, 32, -44, -36, -156, -144, "polymer_grey")
    sel = body.bone("selector", pivot=(0, -70, -80))
    sel.cyl((0, -70, -80), 14, 4, "polymer_grey", axis="y")
    # magazine along the top (translucent, 50 rds)
    mag = m["gun"].bone("magazine", pivot=(0, 30, 120))
    mag.box(-22, 22, 24, 40, -190, 150, "polymer_clear")
    mag.box(-23, 23, 22, 30, 150, 170, "polymer_grey")                       # rear latch block
    for z in range(-180, 140, 14):
        mag.box(-3, 3, 28, 39, z, z + 9, "brass")                           # rounds visible through
    add_arms(m, right_hand=(8, -96, -10), left_hand=(-12, -78, -175), right_rot=(34, 14, 6), left_rot=(26, -18, -4))
    add_sockets(m, muzzle=(0, -8, -306), optic=None, eject=None, sight=(0, 50, 40))

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

    def inspect():
        a = Anim(m, "inspect", 4.0)
        # flip upside down to look through the top-mounted magazine
        a.mv("gun", 0.0, 0.6, pos=(-60, 60, 60), rot=(20, 0, 90), e="inoutsine")
        a.mv("gun", 0.6, 1.2, pos=(-60, 70, 70), rot=(28, -10, 170), e="inoutsine")
        a.mv("arm_left", 0.3, 0.9, pos=(-10, 50, 100), rot=(-20, 0, 40))
        a.wave("gun", "rot", (0.8, 0.8, 0.5), 1.8)
        a.mv("arm_left", 1.6, 1.8, pos=(10, 30, 120), rot=(-20, 0, 40))
        a.sound(1.8, "tap")
        a.mv("arm_left", 1.85, 2.0, pos=(-10, 50, 100), rot=(-20, 0, 40))
        a.mv("gun", 2.2, 2.9, pos=(-40, 40, 50), rot=(10, -30, 40), e="inoutsine")
        a.mv("arm_left", 2.4, 3.0, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.0, 3.95)
        return a

    anims = [
        idle(m), draw(m, 0.6, sound="draw_rifle"),
        fire_basic(m, "fire", kick=(2.2, 0.3, 0.9), push=8, recover=0.1, length=0.18),
        fire_basic(m, "fire_aim", kick=(2.2, 0.3, 0.9), push=8, recover=0.08, length=0.16, aim=True),
        reload("reload", False), reload("reload_empty", True),
        firemode(m, selector_rot=(0, 90, 0)), inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, _fp(pos=(0.12, -0.105, -0.26), ads=0.12))


GUNS = {"mp5": mp5, "ump45": ump45, "uzi": uzi, "p90": p90}
