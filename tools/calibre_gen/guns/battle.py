"""FN FAL, FN SCAR-H, SVD Dragunov, M14 EBR."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden, along)
from ..templates import rifle_reload, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, flash_hider_a2, muzzle_brake,
                     picatinny_handguard, scope)

FP = {"hip": {"pos": [0.12, -0.13, -0.19], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.09}}


def _kk(bolt, travel, kick=4.2, push=15):
    return dict(kick=(kick, 0.6, 1.4), push=push, cycle=dict(bone=bolt, travel=travel, t_back=0.022, t_fwd=0.062))


# =================================================================================================
# FN FAL
# =================================================================================================
def fal():
    A = 4.0
    m = new_gun("fal")
    body = m["body"]
    st = "steel_parked"
    body.box(-15, 15, -10, 18, -120, 170, st)                                   # upper receiver
    body.box(-14, 14, -40, -10, -100, 150, st)                                  # lower
    body.box(-15.5, 15.5, -46, -40, -104, -40, st)
    body.box(0, 15.3, -4, 14, -60, 0, "rubber")
    pistol_grip(body, 40, top_y=-40, length=92, width=28, depth=36, angle=-18, mat="polymer")
    trigger_group(m, body, 4, y_top=-40, guard_depth=28, guard_len=64, guard_mat=st)
    sel = body.bone("selector", pivot=(-14, -26, 46))
    sel.box(-18, -14, -30, -22, 38, 54, "steel")
    # carry handle (folding)
    ch_ = body.bone("carry_handle", pivot=(0, 18, -40))
    ch_.box(-3, 3, 18, 44, -60, -52, "steel")
    ch_.box(-3, 3, 38, 46, -60, 20, "polymer")
    ch_.box(-3, 3, 18, 44, 12, 20, "steel")
    # rear aperture sight
    body.box(-8, 8, 18, 36, 150, 166, st)
    body.box(-2, 2, 30, 34, 150, 166, "rubber")
    # handguard (polymer, vented), gas regulator, front sight, flash hider
    body.box(-18, 18, -34, 14, -340, -120, "polymer")
    for z in range(-330, -130, 22):
        body.box(-18.4, 18.4, -22, 6, z, z + 10, "rubber")
    body.cyl((0, 14, -350), 18, 40, st)
    barrel(body, -340, -540, d=17)
    body.box(-6, 6, -10, 44, -380, -366, st)
    body.box(-8, -5, 30, 50, -380, -366, st)
    body.box(5, 8, 30, 50, -380, -366, st)
    body.box(-1, 1, 30, 46, -374, -372, st)
    flash_hider_a2(body, -540, d=22, length=60)
    # fixed stock
    stock = m["gun"].bone("stock", pivot=(0, 0, 170))
    stock.taper(-18, 18, 170, 518, 14, -22, -52, -128, "polymer")
    stock.box(-19.5, 19.5, -130, -20, 518, 530, "rubber")
    # charging handle: left side, non-reciprocating
    ch = body.bone("charging_handle", pivot=(-15, 4, -110))
    ch.box(-32, -15, 0, 10, -118, -102, "steel")
    ch.box(-36, -30, -2, 12, -120, -100, "steel")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 14.8, -2, 12, -58, -2, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -46, -70))
    curved_mag(mag, -40, -100, 76, 160, curve=8, segs=3, width=26, mat="steel_dark", rib_mat="steel", round_d=10,
               round_len=70)
    add_arms(m, right_hand=(8, -96, 60), left_hand=(-12, -46, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -600), optic=(0, 18, 60), under=(0, -34, -260), eject=(15, 6, -30),
                sight=(0, 34, 160))

    def inspect():
        a = Anim(m, "inspect", 4.4)
        a.mv("gun", 0.0, 0.45, pos=(-30, 20, 30), rot=(6, 24, 20))
        # pull the charging handle partway, look into the action
        a.mv("arm_left", 0.1, 0.45, pos=(-22, 50, 130), rot=(-20, -20, 10))
        a.grab("arm_left", "charging_handle", 0.48, 1.25, fade_in=0.03, fade_out=0.06)
        for b in ("charging_handle", "bolt"):
            a.key(b, 0.0, pos=(0, 0, 0))
            a.key(b, 0.5, pos=(0, 0, 0))
            a.key(b, 0.7, pos=(0, 0, 50), e="inoutquad")
            a.key(b, 1.1, pos=(0, 0, 50))
            a.key(b, 1.18, pos=(0, 0, 0), e="inquad")
        a.sound(0.68, "charging_handle_back")
        a.sound(1.18, "charging_handle_forward")
        a.mv("gun", 0.7, 1.0, pos=(-40, 30, 40), rot=(10, -30, -40))
        # flip the carry handle up, grab it, rotate the rifle
        a.mv("arm_left", 1.3, 1.6, pos=(10, 90, 170), rot=(-50, 0, 20))
        a.key("carry_handle", 0.0, rot=(0, 0, 0))
        a.key("carry_handle", 1.6, rot=(0, 0, 0))
        a.key("carry_handle", 1.72, rot=(0, 0, -90), e="outback")
        a.sound(1.7, "click_small")
        a.grab("arm_left", "carry_handle", 1.75, 2.9, fade_in=0.03, fade_out=0.06)
        a.mv("gun", 1.8, 2.5, pos=(-60, 50, 40), rot=(16, -40, -10), e="inoutsine")
        a.key("carry_handle", 2.8, rot=(0, 0, -90))
        a.key("carry_handle", 2.95, rot=(0, 0, 0), e="inquad")
        a.sound(2.95, "click_small")
        a.mv("arm_left", 3.0, 3.4, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.1, 4.35)
        return a

    kk = _kk("bolt", (0, 0, 100))
    anims = [
        idle(m), idle(m, "idle_empty", locked={"bolt": (0, 0, 100)}), draw(m, 0.75, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.18, length=0.28, **kk),
        fire_basic(m, "fire_aim", recover=0.15, length=0.25, aim=True, **kk),
        fire_basic(m, "fire_last", recover=0.18, length=0.28, lock_back=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="ak", rock=8, mag_out=70),
        rifle_reload(m, "reload_empty", A, empty=True, style="ak", rock=8, mag_out=70, bolt="bolt",
                     bolt_travel=(0, 0, 100), ch="charging_handle", ch_travel=(0, 0, 100), ch_hand="left"),
        firemode(m, selector_rot=(-60, 0, 0)), inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, FP)


# =================================================================================================
# FN SCAR-H
# =================================================================================================
def scar_h():
    A = 2.0
    m = new_gun("scar_h")
    body = m["body"]
    up, lo = "alloy_tan", "polymer_tan"
    body.box(-17, 17, -8, 28, -330, 112, up)
    body.rail(-326, 110, 28, mat=up)
    body.rail(-320, -170, -6, x=-17, mat=up, side="left", width=18)
    body.rail(-320, -170, -6, x=17, mat=up, side="right", width=18)
    body.box(-14, 14, -40, -8, -110, 112, lo)
    body.rail(-320, -130, -8, mat=lo, side="bottom")
    body.box(-15, 15, -46, -40, -104, -44, lo)
    body.box(0, 17.2, -4, 14, -60, -10, "rubber")
    body.box(-17.3, -17, -2, 6, -150, 0, "rubber")                             # charging handle slot
    pistol_grip(body, 40, top_y=-40, length=92, width=28, depth=36, angle=-18, mat=lo)
    trigger_group(m, body, 4, y_top=-40, guard_depth=26, guard_len=62, guard_mat=lo)
    sel = body.bone("selector", pivot=(-14, -24, 46))
    sel.box(-17, -14, -28, -20, 38, 54, "steel_dark")
    barrel(body, -330, -470, d=18)
    body.box(-12, 12, -10, 12, -350, -330, "steel_dark")
    muzzle_brake(body, -470, d=24, length=52, ports=3)
    # flip-up sights
    body.box(-6, 6, 31, 52, -316, -306, up)
    body.box(-8, 8, 31, 50, 96, 106, up)
    # side-folding, adjustable stock
    stock = m["gun"].bone("stock", pivot=(14, 0, 112))
    stock.box(-14, 14, -20, 20, 112, 150, lo)
    stock.box(-12, 12, -24, 14, 150, 240, lo)
    ext = stock.bone("stock_ext", pivot=(0, 0, 240))
    ext.box(-15, 15, -90, 14, 240, 330, lo)
    ext.box(-14, 14, 14, 26, 230, 310, lo)                                       # cheek riser
    ext.box(-16, 16, -96, 18, 326, 340, "rubber")
    # reciprocating charging handle (left)
    ch = body.bone("charging_handle", pivot=(-17, 2, -60))
    ch.box(-36, -17, -2, 8, -66, -54, "polymer")
    ch.box(-40, -32, -4, 10, -68, -52, "polymer")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.8, -2, 12, -58, -12, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -46, -72))
    curved_mag(mag, -40, -102, 76, 160, curve=8, segs=3, width=26, mat="steel_dark", rib_mat="steel", round_d=10,
               round_len=70)
    add_arms(m, right_hand=(8, -96, 60), left_hand=(-12, -42, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -522), optic=(0, 31, -60), under=(0, -11, -250), side=(-20, -6, -250),
                eject=(17, 6, -36), sight=(0, 50, 101))

    def inspect():
        a = Anim(m, "inspect", 4.6)
        a.mv("gun", 0.0, 0.45, pos=(-30, 20, 30), rot=(6, 30, 20))
        # half-pull the charging handle, let it slam (the SCAR "bite")
        a.mv("arm_left", 0.1, 0.45, pos=(-26, 48, 180), rot=(-20, -20, 10))
        a.grab("arm_left", "charging_handle", 0.48, 1.0, fade_in=0.03, fade_out=0.05)
        for b in ("charging_handle", "bolt"):
            a.key(b, 0.0, pos=(0, 0, 0))
            a.key(b, 0.5, pos=(0, 0, 0))
            a.key(b, 0.68, pos=(0, 0, 46), e="inoutquad")
            a.key(b, 0.9, pos=(0, 0, 46))
            a.key(b, 0.95, pos=(0, 0, 0), e="inquad")
        a.sound(0.66, "charging_handle_back")
        a.sound(0.95, "charging_handle_forward")
        a.mv("arm_left", 1.0, 1.3, pos=(-40, -20, 120), rot=(0, 0, 0))
        # stock adjust: rotate to see the stock, pump it out and back
        a.mv("gun", 1.2, 1.8, pos=(-80, 30, -60), rot=(4, -60, -10), e="inoutsine")
        a.mv("arm_left", 1.4, 1.8, pos=(30, -50, 470), rot=(0, 40, 10))
        a.grab("arm_left", "stock_ext", 1.82, 3.0, fade_in=0.03, fade_out=0.06)
        a.key("stock_ext", 0.0, pos=(0, 0, 0))
        a.key("stock_ext", 1.85, pos=(0, 0, 0))
        a.key("stock_ext", 2.05, pos=(0, 0, 40), e="inoutquad")
        a.sound(2.05, "stock_adjust")
        a.key("stock_ext", 2.45, pos=(0, 0, 40))
        a.key("stock_ext", 2.62, pos=(0, 0, 0), e="inoutquad")
        a.sound(2.62, "stock_adjust")
        a.mv("arm_left", 3.0, 3.5, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.1, 4.55)
        return a

    kk = _kk("bolt", (0, 0, 96))
    anims = [
        idle(m), idle(m, "idle_empty", locked={"bolt": (0, 0, 96), "charging_handle": (0, 0, 96)}),
        draw(m, 0.75, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.17, length=0.27, **kk),
        fire_basic(m, "fire_aim", recover=0.14, length=0.24, aim=True, **kk),
        fire_basic(m, "fire_last", recover=0.17, length=0.27, lock_back=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="ar", bolt="bolt", bolt_travel=(0, 0, 96)),
        rifle_reload(m, "reload_empty", A, empty=True, style="ar", bolt="bolt", bolt_travel=(0, 0, 96)),
        firemode(m, selector_rot=(-90, 0, 0)), inspect(), dry_fire(m),
    ]
    # reciprocating handle follows the bolt in fire/reload
    for a in anims:
        if a.name.startswith("fire") and ("bolt", "pos") in a.tracks:
            for (t, v, e) in a.tracks[("bolt", "pos")].keys:
                a.key("charging_handle", t, pos=v, e=e)
    return GunAsset(m, anims, FP)


# =================================================================================================
# SVD Dragunov (integral PSO-1)
# =================================================================================================
def svd():
    A = 6.0
    m = new_gun("svd")
    body = m["body"]
    st = "steel_dark"
    body.box(-14, 14, -34, 12, -100, 200, st)
    body.box(-12, 12, 12, 20, -60, 200, st)
    body.box(-14.5, 14.5, -40, -34, -100, -50, st)
    body.box(0, 14.3, -6, 10, -50, 30, "rubber")
    body.box(-14, 14, -20, 24, -126, -100, st)
    body.box(-17, 17, -30, 10, -400, -126, "wood_red")
    for z in range(-390, -140, 26):
        body.box(-17.4, 17.4, -20, 0, z, z + 12, "rubber")
    body.cyl((0, 14, -410), 16, 40, st)
    barrel(body, -400, -640, d=16)
    body.box(-6, 6, -8, 40, -620, -606, st)
    body.box(-10, 10, -10, 10, -700, -640, st)                                   # flash hider
    for z in (-690, -675, -660):
        body.box(-10.4, 10.4, -6, 6, z, z + 6, "rubber")
    pistol_grip(body, 30, top_y=-34, length=40, width=26, depth=30, angle=-10, mat="wood_red", checker=False)
    trigger_group(m, body, -6, y_top=-34, guard_depth=30, guard_len=70, guard_mat=st)
    # skeleton thumbhole stock + cheek rest
    stock = m["gun"].bone("stock", pivot=(0, 0, 200))
    stock.box(-15, 15, 0, 14, 200, 520, "wood_red")
    stock.box(-15, 15, -110, -84, 260, 520, "wood_red")
    stock.box(-15, 15, -110, 0, 200, 230, "wood_red", rot=(30, 0, 0), pivot=(0, 0, 215))
    stock.box(-15, 15, -110, 14, 480, 520, "wood_red")
    stock.box(-16, 16, -118, 18, 516, 528, st)
    cheek = stock.bone("cheek_rest", pivot=(0, 14, 360))
    cheek.box(-14, 14, 14, 34, 300, 420, "leather")
    sel = body.bone("selector", pivot=(14, 4, 0))
    sel.box(14, 16, -4, 8, 0, 100, "steel")
    bolt = body.bone("bolt", pivot=(18, 2, -60))
    bolt.box(1, 13, -6, 8, -60, -14, "steel_light")
    bolt.box(14, 28, -2, 6, -64, -54, "steel_light")
    bolt.box(26, 32, -4, 8, -66, -52, "steel_light")
    # PSO-1 4x on its side mount
    pso = body.bone("pso1", pivot=(0, 60, 40))
    pso.box(-20, -14, 0, 40, -10, 90, st)                                         # side rail mount
    scope(pso, 40, 66, length=280, tube_d=28, obj_d=40, eye_d=34, mat="steel_dark", mount_y=24)
    pso.box(-20, 20, 50, 84, 170, 200, "rubber")                                   # eyecup
    pso.box(-12, 12, 60, 80, -110, -96, "rubber")                                  # sunshade
    mag = m["gun"].bone("magazine", pivot=(0, -40, -80))
    curved_mag(mag, -34, -100, 70, 150, curve=12, segs=3, width=24, mat="steel_dark", rib_mat="steel", round_d=11,
               round_len=70)
    add_arms(m, right_hand=(8, -66, 36), left_hand=(-12, -40, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -700), optic=None, under=(0, -30, -320), eject=(15, 6, -30), sight=(0, 66, 196))
    m.meta["integral_optic"] = {"zoom": 4.0, "reticle": "pso1", "eye": [0, 66, 196]}

    def inspect():
        a = Anim(m, "inspect", 4.8)
        # bring the PSO-1 up to the eye, check through the scope
        a.mv("gun", 0.0, 0.6, pos=(-90, 30, 60), rot=(4, 16, 10), e="inoutsine")
        a.wave("gun", "rot", (0.4, 0.5, 0.2), 1.6)
        a.mv("arm_left", 0.7, 1.0, pos=(-10, 110, -40), rot=(-30, 0, 30))
        # adjust the elevation turret
        for t in (1.1, 1.3, 1.5):
            a.sound(t, "click_small")
        a.mv("arm_left", 1.6, 1.9, pos=(0, 0, 0), rot=(0, 0, 0))
        # rotate to look at the cheek rest, flip it
        a.mv("gun", 1.8, 2.5, pos=(-40, 30, -40), rot=(-6, -56, -10), e="inoutsine")
        a.mv("arm_left", 2.3, 2.6, pos=(20, 60, 560), rot=(-30, 40, 0))
        a.key("cheek_rest", 0.0, rot=(0, 0, 0))
        a.key("cheek_rest", 2.62, rot=(0, 0, 0))
        a.key("cheek_rest", 2.74, rot=(0, 0, -70), e="outquad")
        a.sound(2.74, "click_small")
        a.key("cheek_rest", 3.1, rot=(0, 0, -70))
        a.key("cheek_rest", 3.22, rot=(0, 0, 0), e="outback")
        a.sound(3.22, "click_small")
        a.mv("arm_left", 3.3, 3.8, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.5, 4.75)
        return a

    kk = _kk("bolt", (0, 0, 120), kick=5.0, push=16)
    anims = [
        idle(m), draw(m, 0.8, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.24, length=0.36, **kk),
        fire_basic(m, "fire_aim", recover=0.2, length=0.32, aim=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="ak", rock=10, mag_out=60),
        rifle_reload(m, "reload_empty", A, empty=True, style="ak", rock=10, mag_out=60, bolt="bolt", ch="bolt",
                     bolt_travel=(0, 0, 120), ch_travel=(0, 0, 120), bolt_hold_open=False, ch_hand="right"),
        inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, {"hip": {"pos": [0.12, -0.15, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.07}})


# =================================================================================================
# M14 EBR (Sage chassis)
# =================================================================================================
def m14ebr():
    A = 6.0
    m = new_gun("m14ebr")
    body = m["body"]
    al = "alloy"
    body.box(-14, 14, -14, 16, -100, 120, "steel_parked")                       # M14 receiver
    body.box(-19, 19, -40, 30, -360, -100, al)                                   # EBR chassis forend
    body.rail(-356, 116, 30, mat=al)
    body.rail(-350, -120, -40, mat=al, side="bottom")
    body.rail(-350, -150, -5, x=-19, mat=al, side="left", width=20)
    body.rail(-350, -150, -5, x=19, mat=al, side="right", width=20)
    body.box(-17, 17, -40, -14, -100, 140, al)
    body.box(-16, 16, -46, -40, -104, -40, al)
    for z in range(-340, -120, 30):
        body.box(-19.4, 19.4, -30, 10, z, z + 14, "rubber")
    pistol_grip(body, 42, top_y=-40, length=92, width=28, depth=36, angle=-18, mat="polymer")
    trigger_group(m, body, 4, y_top=-40, guard_depth=26, guard_len=62, guard_mat="steel_parked")
    sel = body.bone("selector", pivot=(0, -38, -20))
    sel.box(-3, 3, -44, -38, -30, -14, "steel")                                   # safety in the guard
    barrel(body, -360, -560, d=18)
    muzzle_brake(body, -560, d=22, length=50, ports=3)
    # adjustable stock
    stock = m["gun"].bone("stock", pivot=(0, 0, 140))
    stock.cyl((0, -6, 240), 32, 200, al)
    stock.taper(-20, 20, 240, 340, 14, 14, -58, -80, "polymer")
    stock.box(-14, 14, 14, 34, 250, 320, "polymer")
    stock.box(-22, 22, -86, 18, 336, 348, "rubber")
    # op-rod handle (right side)
    bolt = body.bone("bolt", pivot=(16, 0, -40))
    bolt.box(1, 13.5, -4, 10, -60, -10, "steel_light")
    bolt.box(14, 22, -2, 8, -120, -40, "steel_parked")
    bolt.box(20, 30, -4, 10, -128, -112, "steel_parked")
    mag = m["gun"].bone("magazine", pivot=(0, -46, -80))
    curved_mag(mag, -40, -100, 76, 150, curve=6, segs=3, width=26, mat="steel_dark", rib_mat="steel", round_d=10,
               round_len=70)
    add_arms(m, right_hand=(8, -96, 62), left_hand=(-12, -48, -260), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -610), optic=(0, 33, -10), under=(0, -43, -280), side=(-22, -5, -280),
                eject=(15, 6, -30), sight=(0, 50, 100))
    body.box(-8, 8, 33, 50, 96, 106, al)
    body.box(-6, 6, 33, 52, -330, -320, al)

    def inspect():
        a = Anim(m, "inspect", 4.2)
        # op-rod press check: rotate right side up, ease the op-rod back, look
        a.mv("gun", 0.0, 0.45, pos=(-40, 26, 40), rot=(6, -40, -44), e="inoutsine")
        a.mv("arm_right", 0.25, 0.5, pos=(30, 70, -120), rot=(-30, -20, -30))
        a.grab("arm_right", "bolt", 0.52, 1.5, fade_in=0.03, fade_out=0.06)
        a.key("bolt", 0.0, pos=(0, 0, 0))
        a.key("bolt", 0.55, pos=(0, 0, 0))
        a.key("bolt", 0.78, pos=(0, 0, 34), e="inoutquad")
        a.sound(0.74, "charging_handle_back")
        a.mv("gun", 0.8, 1.1, pos=(-46, 32, 50), rot=(10, -56, -60))
        a.key("bolt", 1.3, pos=(0, 0, 34))
        a.key("bolt", 1.42, pos=(0, 0, 0), e="inoutsine")
        a.sound(1.42, "charging_handle_forward")
        a.mv("arm_left", 1.5, 1.7, pos=(26, 40, 160), rot=(-10, 30, 20))
        a.mv("arm_left", 1.7, 1.76, pos=(20, 40, 166), rot=(-10, 30, 20), e="outquad")
        a.sound(1.75, "tap")
        a.mv("arm_right", 1.5, 1.8, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_left", 1.85, 2.3, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 1.9, 2.6, pos=(-60, 30, 30), rot=(10, 30, 20), e="inoutsine")
        _settle(a, 3.0, 4.15)
        return a

    kk = _kk("bolt", (0, 0, 96), kick=4.6, push=16)
    anims = [
        idle(m), idle(m, "idle_empty", locked={"bolt": (0, 0, 96)}), draw(m, 0.8, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.2, length=0.3, **kk),
        fire_basic(m, "fire_aim", recover=0.17, length=0.27, aim=True, **kk),
        fire_basic(m, "fire_last", recover=0.2, length=0.3, lock_back=True, **kk),
        rifle_reload(m, "reload", A, empty=False, style="ak", rock=8, mag_out=60),
        rifle_reload(m, "reload_empty", A, empty=True, style="ak", rock=8, mag_out=60, bolt="bolt", ch="bolt",
                     bolt_travel=(0, 0, 96), ch_travel=(0, 0, 96), bolt_hold_open=True, ch_hand="right"),
        inspect(), dry_fire(m),
    ]
    return GunAsset(m, anims, FP)


GUNS = {"fal": fal, "scar_h": scar_h, "svd": svd, "m14ebr": m14ebr}
