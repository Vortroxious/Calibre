"""Remington M24 SWS, Accuracy International AWM, Barrett M82A1 — all with their issued scopes."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden, along)
from ..templates import rifle_reload, bolt_cycle, bolt_load, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, muzzle_brake, scope, bipod)

SNIPER_FP = {"hip": {"pos": [0.12, -0.15, -0.18], "rot": [0, 3, 0]}, "ads": {"dist": 0.075}}


def _bolt(m, parent, z_front, z_rear, handle_z, knob=True, mat="steel_light", d=19.0):
    b = m[parent].bone("bolt", pivot=(0, 0, 0))
    b.cyl((0, 0, (z_front + z_rear) / 2), d, z_rear - z_front, mat)
    b.box(8, 40, -4, 4, handle_z - 5, handle_z + 5, mat, rot=(0, 0, -20), pivot=(8, 0, handle_z))  # handle
    if knob:
        b.box(36, 52, -18, -2, handle_z - 8, handle_z + 8, "polymer", rot=(0, 0, -20), pivot=(8, 0, handle_z))
    b.box(-8, 8, -8, 8, z_rear, z_rear + 14, "steel_dark")                                         # shroud
    return b


def m24():
    m = new_gun("m24")
    body = m["body"]
    st = "steel_dark"
    body.cyl((0, 0, -10), 34, 220, st, sides=12)                                 # 700 receiver
    body.box(0, 17.5, 2, 16, -60, 10, "rubber")                                   # ejection port
    barrel(body, -120, -720, d=22)
    body.cyl((0, 0, -716), 18, 8, st)
    # HS Precision stock (OD green)
    s = "polymer_od"
    body.box(-24, 24, -46, -10, -560, 100, s)
    body.box(-22, 22, -40, -16, -560, -140, s)
    body.box(-22, 22, -110, -10, 100, 160, s, rot=(-20, 0, 0), pivot=(0, -10, 100))   # grip area
    body.taper(-24, 24, 160, 359, 8, 8, -78, -100, s)
    body.box(-25, 25, -106, 14, 355, 371, "rubber")
    body.box(-6, 6, -46, -40, -480, -460, "steel")                                   # sling swivel
    trigger_group(m, body, 40, y_top=-46, guard_depth=26, guard_len=60, guard_mat=st)
    sel = body.bone("selector", pivot=(14, 10, 110))
    sel.box(12, 16, 6, 14, 104, 116, "steel")
    _bolt(m, "gun", -60, 110, 96)
    rl = m["gun"].bone("round_load", pivot=(0, 10, -20))
    rl.round_((0, 10, -20), 70, 12)

    br = m["gun"].bone("brass", pivot=(0, 6, -30))
    br.cyl((0, 6, -20), 12, 50, "brass")
    sc = body.bone("scope", pivot=(0, 50, -10))
    scope(sc, -10, 52, length=330, tube_d=30, obj_d=50, eye_d=42, mount_y=17)
    add_arms(m, right_hand=(10, -80, 150), left_hand=(-14, -50, -260), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -720), under=(0, -46, -360), eject=(18, 8, -20), sight=(0, 52, 150))
    m.meta["integral_optic"] = {"zoom": 10.0, "reticle": "mildot", "eye": [0, 52, 150]}

    def inspect():
        a = Anim(m, "inspect", 4.0)
        a.mv("gun", 0.0, 0.4, pos=(-30, 20, 30), rot=(4, -20, -26))
        a.mv("arm_right", 0.0, 0.2, pos=(20, 40, -30), rot=(-25, -20, -20))
        a.grab("arm_right", "bolt", 0.2, 1.8, fade_in=0.03, fade_out=0.06)
        a.key("bolt", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("bolt", 0.22, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("bolt", 0.34, pos=(0, 0, 0), rot=(0, 0, 66), e="outquad")
        a.sound(0.32, "bolt_open")
        a.key("bolt", 0.62, pos=(0, 0, 28), rot=(0, 0, 66), e="inoutsine")
        a.mv("gun", 0.6, 1.0, pos=(-40, 30, 40), rot=(10, -36, -50))                  # peek at the round
        a.key("bolt", 1.4, pos=(0, 0, 28), rot=(0, 0, 66))
        a.key("bolt", 1.56, pos=(0, 0, 0), rot=(0, 0, 66), e="inoutsine")
        a.key("bolt", 1.66, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
        a.sound(1.66, "bolt_close")
        a.mv("arm_right", 1.85, 2.1, pos=(0, 0, 0), rot=(0, 0, 0))
        # check the scope caps / turrets
        a.mv("gun", 1.8, 2.5, pos=(-60, 20, 0), rot=(-6, 30, 16), e="inoutsine")
        a.mv("arm_left", 2.2, 2.5, pos=(10, 110, 210), rot=(-40, 10, 20))
        for t in (2.6, 2.75, 2.9):
            a.sound(t, "click_small")
        a.mv("arm_left", 3.0, 3.4, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.0, 3.95)
        return a

    cyc = bolt_cycle(m, "cycle", travel=(0, 0, 96), handle_rot=(0, 0, 66))
    cyc_aim = bolt_cycle(m, "cycle_aim", travel=(0, 0, 96), handle_rot=(0, 0, 66), aim=True)
    anims = [idle(m), draw(m, 0.8, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(7, 0.6, 1.4), push=22, recover=0.4, length=0.5),
             fire_basic(m, "fire_aim", kick=(7, 0.6, 1.4), push=22, recover=0.36, length=0.45, aim=True),
             cyc, cyc_aim, *bolt_load(m, travel=(0, 0, 96), handle_rot=(0, 0, 66)), inspect(), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass"])
    return GunAsset(m, anims, SNIPER_FP)


def awm():
    A = 0.0
    m = new_gun("awm")
    body = m["body"]
    g = "polymer_od"
    body.box(-17, 17, -14, 18, -100, 120, "alloy_grey")                           # receiver
    body.box(0, 17.4, 0, 16, -60, 0, "rubber")
    barrel(body, -100, -700, d=24)
    muzzle_brake(body, -700, d=26, length=60, ports=2)
    # chassis + thumbhole stock (green)
    body.box(-26, 26, -50, -14, -420, 120, g)
    body.box(-24, 24, -46, -20, -420, -120, g)
    body.box(-20, 20, -120, -50, 70, 120, g, rot=(-14, 0, 0), pivot=(0, -50, 90))
    trigger_group(m, body, 30, y_top=-50, guard_depth=30, guard_len=70, guard_mat=g)
    stock = m["gun"].bone("stock", pivot=(-20, 0, 120))
    stock.box(-26, 26, -60, 8, 120, 180, g)
    stock.box(-26, 26, -110, -70, 140, 420, g)
    stock.box(-26, 26, -30, 8, 180, 420, g)
    stock.box(-26, 26, -110, 8, 400, 430, g)
    stock.box(-28, 28, -118, 12, 428, 442, "rubber")
    stock.box(-18, 18, 8, 26, 280, 380, g)                                        # cheek piece
    bipod(body, -400, y=-50, legs_len=200, folded=True)
    _bolt(m, "gun", -60, 116, 102, mat="steel_dark", d=21)
    br = m["gun"].bone("brass", pivot=(0, 6, -30))
    br.cyl((0, 6, -20), 14, 60, "brass")
    mag = m["gun"].bone("magazine", pivot=(0, -50, -30))
    straight_mag(mag, -46, -70, 20, 90, width=26, mat="steel_dark", round_d=13, round_len=80)
    sc = body.bone("scope", pivot=(0, 52, -10))
    scope(sc, -10, 54, length=340, tube_d=34, obj_d=56, eye_d=44, mount_y=18)
    add_arms(m, right_hand=(10, -96, 104), left_hand=(-14, -54, -280), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -760), under=None, eject=(18, 8, -20), sight=(0, 54, 160))
    m.meta["integral_optic"] = {"zoom": 12.0, "reticle": "mildot", "eye": [0, 54, 160]}

    def inspect():
        a = Anim(m, "inspect", 4.6)
        # open the bolt, look into the chamber
        a.mv("gun", 0.0, 0.4, pos=(-30, 20, 30), rot=(4, -20, -26))
        a.mv("arm_right", 0.0, 0.2, pos=(20, 40, -30), rot=(-25, -20, -20))
        a.grab("arm_right", "bolt", 0.2, 1.5, fade_in=0.03, fade_out=0.06)
        a.key("bolt", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("bolt", 0.22, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("bolt", 0.34, pos=(0, 0, 0), rot=(0, 0, 66), e="outquad")
        a.sound(0.32, "bolt_open")
        a.key("bolt", 0.56, pos=(0, 0, 34), rot=(0, 0, 66), e="inoutsine")
        a.mv("gun", 0.55, 0.9, pos=(-40, 30, 40), rot=(10, -36, -50))
        a.key("bolt", 1.15, pos=(0, 0, 34), rot=(0, 0, 66))
        a.key("bolt", 1.3, pos=(0, 0, 0), rot=(0, 0, 66), e="inoutsine")
        a.key("bolt", 1.4, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
        a.sound(1.4, "bolt_close")
        a.mv("arm_right", 1.5, 1.8, pos=(0, 0, 0), rot=(0, 0, 0))
        # fold the stock to the left and back
        a.mv("gun", 1.5, 2.1, pos=(-80, 30, -80), rot=(0, -60, -10), e="inoutsine")
        a.mv("arm_left", 1.7, 2.1, pos=(-40, -40, 600), rot=(0, -40, 0))
        a.grab("arm_left", "stock", 2.12, 3.4, fade_in=0.03, fade_out=0.06)
        a.key("stock", 0.0, rot=(0, 0, 0))
        a.key("stock", 2.15, rot=(0, 0, 0))
        a.sound(2.15, "stock_unlock")
        a.key("stock", 2.7, rot=(0, -150, 0), e="inoutsine")
        a.sound(2.7, "stock_lock")
        a.key("stock", 2.9, rot=(0, -150, 0))
        a.key("stock", 3.35, rot=(0, 0, 0), e="inoutsine")
        a.sound(3.35, "stock_lock")
        a.mv("arm_left", 3.4, 3.9, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.5, 4.55)
        return a

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(9, 0.6, 1.6), push=26, recover=0.45, length=0.55),
             fire_basic(m, "fire_aim", kick=(9, 0.6, 1.6), push=26, recover=0.4, length=0.5, aim=True),
             bolt_cycle(m, "cycle", travel=(0, 0, 104), handle_rot=(0, 0, 66)),
             bolt_cycle(m, "cycle_aim", travel=(0, 0, 104), handle_rot=(0, 0, 66), aim=True),
             rifle_reload(m, "reload", A, empty=False, style="ar", mag_out=50, tilt=(4, -6, -20)),
             inspect(), dry_fire(m)]
    apply_hidden(anims, ["brass"])
    m.warp_z([(-761, -788), (-110, -110)])
    return GunAsset(m, anims, SNIPER_FP)


def m82a1():
    A = 4.0
    m = new_gun("m82a1")
    body = m["body"]
    st = "steel_parked"
    # lower receiver
    body.box(-24, 24, -60, 0, -320, 300, st)
    pistol_grip(body, 60, top_y=-60, length=96, width=30, depth=40, angle=-16, mat="polymer")
    trigger_group(m, body, 20, y_top=-60, guard_depth=28, guard_len=66, guard_mat=st)
    body.box(-22, 22, -130, -60, 300, 360, st)                                      # monopod/stock
    body.box(-20, 20, -40, 0, 300, 480, "polymer")
    body.box(-24, 24, -60, 4, 470, 490, "rubber")
    body.box(-14, 14, 0, 30, 220, 330, "polymer")                                   # cheek rest
    sel = body.bone("selector", pivot=(-24, -40, 40))
    sel.box(-28, -24, -44, -36, 30, 50, "steel")
    bipod(body, -280, y=-60, legs_len=260, folded=True)
    # upper receiver + barrel recoil together
    up = m["gun"].bone("upper", pivot=(0, 0, 0))
    up.box(-24, 24, 0, 36, -360, 300, st)
    up.rail(-200, 280, 36, mat="alloy")
    up.box(0, 24.4, 2, 26, -80, -20, "rubber")
    for z in range(-350, -200, 22):
        up.box(-24.4, 24.4, 6, 28, z, z + 10, "rubber")                             # cooling holes
    barrel(up, -360, -900, d=30)
    up.box(-40, 40, -18, 18, -1000, -900, st)                                        # dual chamber brake
    up.box(-41, 41, -14, 14, -980, -960, "rubber")
    up.box(-41, 41, -14, 14, -940, -920, "rubber")
    ch = up.bone("charging_handle", pivot=(24, 16, -80))
    ch.box(24, 44, 10, 22, -86, -74, "steel")
    ch.box(40, 50, 6, 26, -88, -72, "polymer")
    # carry handle
    up.box(-6, 6, 36, 70, -160, -150, "steel")
    up.box(-6, 6, 64, 72, -160, -60, "polymer")
    up.box(-6, 6, 36, 70, -70, -60, "steel")
    mag = m["gun"].bone("magazine", pivot=(0, -60, -40))
    straight_mag(mag, -60, -90, 60, 130, width=34, mat="steel_dark", round_d=20, round_len=130)
    sc = up.bone("scope", pivot=(0, 80, 120))
    scope(sc, 120, 82, length=360, tube_d=34, obj_d=56, eye_d=44, mount_y=39)
    add_arms(m, right_hand=(10, -104, 80), left_hand=(-16, -70, 380), right_rot=(34, 14, 6), left_rot=(30, -22, -4))
    add_sockets(m, muzzle=(0, 0, -1000), eject=(24, 14, -50), sight=(0, 82, 300), parent="body")
    m.meta["integral_optic"] = {"zoom": 10.0, "reticle": "mildot", "eye": [0, 82, 300]}

    def inspect():
        a = Anim(m, "inspect", 4.8)
        # rest it on the shoulder
        a.mv("gun", 0.0, 0.7, pos=(-60, 120, 160), rot=(30, -20, -40), e="inoutsine")
        a.mv("arm_left", 0.1, 0.6, pos=(-60, 10, -40), rot=(10, -20, 0))
        a.wave("gun", "rot", (0.6, 0.4, 0.5), 1.6)
        a.wave("gun", "pos", (0, 2, 0), 0.8)
        # pat the upper receiver twice
        for t in (1.5, 1.85):
            a.mv("arm_left", t - 0.15, t, pos=(-10, 60, -60), rot=(-20, -10, 10), e="outquad")
            a.sound(t, "tap")
            a.spring("gun", "rot", t, (0.6, 0, 0.4), freq=7, damp=10)
            a.mv("arm_left", t, t + 0.12, pos=(-10, 80, -40), rot=(-20, -10, 10))
        # tug the charging handle a touch
        a.mv("arm_left", 2.1, 2.4, pos=(-20, -20, 40), rot=(0, 0, 0))
        a.mv("gun", 2.2, 2.9, pos=(-40, 30, 40), rot=(4, -40, -26), e="inoutsine")
        a.mv("arm_right", 2.6, 2.9, pos=(40, 120, -160), rot=(-30, -20, -30))
        a.grab("arm_right", "charging_handle", 2.92, 3.5, fade_in=0.03, fade_out=0.06)
        a.key("charging_handle", 2.92, pos=(0, 0, 0))
        a.key("charging_handle", 3.12, pos=(0, 0, 40), e="inoutquad")
        a.sound(3.1, "charging_handle_back")
        a.key("charging_handle", 3.38, pos=(0, 0, 0), e="inquad")
        a.sound(3.38, "charging_handle_forward")
        a.mv("arm_right", 3.5, 3.8, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_left", 3.3, 3.8, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.6, 4.75)
        return a

    def fire(name, aim):
        a = fire_basic(m, name, kick=(10, 0.8, 1.8), push=30, recover=0.5, length=0.6, aim=aim)
        # recoiling barrel/upper
        a.key("upper", 0.0, pos=(0, 0, 0))
        a.key("upper", 0.035, pos=(0, 0, 40), e="outquad")
        a.key("upper", 0.12, pos=(0, 0, 0), e="inoutsine")
        return a

    anims = [idle(m), draw(m, 1.0, sound="draw_rifle"), fire("fire", False), fire("fire_aim", True),
             rifle_reload(m, "reload", A, empty=False, style="ar", mag_out=60, length=3.0),
             rifle_reload(m, "reload_empty", A, empty=True, style="smg", mag_out=60, ch="charging_handle",
                          ch_travel=(0, 0, 120), bolt_hold_open=False, ch_hand="right", length=3.6),
             inspect(), dry_fire(m)]
    return GunAsset(m, anims, {"hip": {"pos": [0.13, -0.16, -0.24], "rot": [0, 3, 0]}, "ads": {"dist": 0.075}})


GUNS = {"m24": m24, "awm": awm, "m82a1": m82a1}
