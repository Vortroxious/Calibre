"""Field and hunting guns: Charles Daly pump, Mossberg 190 bolt-action shotgun, Tikka T3, Savage Model 10."""
import numpy as np

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden)
from ..templates import (rifle_reload, tube_reload, pump_cycle, bolt_cycle, _settle, OFF_LEFT, OFF_LEFT_ROT)
from ..parts import pistol_grip, trigger_group, barrel, straight_mag, scope, sling_swivel
from ..pistolkit import control
from ..riflekit import mil_stock, line_y, butt_plate, receiver, stepped_barrel, bolt, rides
from .ww2 import _butt, _military_bolt
from .classic import _sg_shells, _tube_mag

SG_FP = {"hip": {"pos": [0.12, -0.13, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.32}}
SCOPED_FP = {"hip": {"pos": [0.12, -0.15, -0.18], "rot": [0, 3, 0]}, "ads": {"dist": 0.075}}


def _sporter_stock(body, z0, mat, plate="rubber", grip_mat=None, w=18, length=360):
    """Sporter wrist with a gentle pistol grip and a lofted butt."""
    body.box(-14, 14, -46, -10, z0, z0 + 110, mat, rot=(4, 0, 0), pivot=(0, -10, z0))
    body.box(-14, 14, -104, -46, z0 + 14, z0 + 62, grip_mat or mat, rot=(-24, 0, 0), pivot=(0, -46, z0 + 40))
    _butt(body, z0 + 106, z0 + length, mat, plate, comb_y=-12, heel_drop=16, toe_y=-128, wrist_y=-72, w=w)


def _choke(m, z, d, length, mat="steel_light", y=4):
    c = m["body"].bone("choke", pivot=(0, y, z))
    c.cyl((0, y, z - length / 2), d, length, mat, sides=12)
    for i in range(4):
        c.box(-d / 2 - 0.6, d / 2 + 0.6, y - 2, y + 2, z - length + 4 + i * (length - 8) / 3,
              z - length + 6 + i * (length - 8) / 3, "rubber")
    return c


# =================================================================================================
# Charles Daly 300 Field pump
# =================================================================================================
def cdaly():
    m = new_gun("cdaly")
    body = m["body"]
    al = "alloy"
    wd = "wood"
    body.box(-17, 17, -30, 22, -114, 80, al)
    body.box(0, 17.3, -8, 14, -84, -14, "rubber")
    body.box(-12, 12, -32, -30, -100, -20, "rubber")
    barrel(body, -114, -740, d=21, y=4, mat="steel_dark")
    body.box(-4, 4, 15, 19, -730, -114, "steel_dark")                       # vent rib
    for z in range(-720, -130, 40):
        body.box(-3, 3, 14, 15, z, z + 20, "steel_dark")
    body.box(-1.5, 1.5, 19, 23, -728, -724, "brass")                        # front bead
    body.box(-1, 1, 19, 21, -420, -418, "white")                           # mid bead
    _choke(m, -740, 22, 26)
    _tube_mag(body, -114, -520, -22, d=22, mat=al)
    trigger_group(m, body, 10, y_top=-30, guard_depth=28, guard_len=62, guard_mat=al)
    sel = body.bone("selector", pivot=(0, -36, 40))
    sel.cyl((0, -36, 40), 8, 40, "steel_dark", axis="x")
    _sporter_stock(body, 80, wd)
    pump = m["gun"].bone("pump", pivot=(0, -22, -280))
    pump.box(-21, 21, -42, -4, -380, -210, wd)
    for z in range(-360, -230, 30):
        pump.box(-21.4, 21.4, -34, -14, z, z + 18, "wood_red")            # checkering panels
    pump.box(-5, -2, -14, -6, -210, -70, "steel")
    pump.box(2, 5, -14, -6, -210, -70, "steel")
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.8, -6, 12, -78, -20, "steel_light")
    _sg_shells(m)
    add_arms(m, right_hand=(8, -86, 132), left_hand=(-10, -40, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -766), optic=(0, 22, -20), eject=(17, 4, -50), sight=(0, 23.5, 70))

    def inspect():
        # turn the muzzle up, back the choke tube out a few turns to check it, run it back in snug
        a = Anim(m, "inspect", 4.6)
        a.mv("gun", 0.0, 0.5, pos=(-90, 10, -60), rot=(6, 64, 14), e="inoutsine")
        a.mv("arm_left", 0.2, 0.55, pos=(10, 30, -420), rot=(-40, 10, 20))
        a.key("choke", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("choke", 0.6, pos=(0, 0, 0), rot=(0, 0, 0))
        for i in range(3):
            t = 0.65 + i * 0.32
            a.key("choke", t + 0.26, pos=(0, 0, -3 * (i + 1)), rot=(0, 0, -150 * (i + 1)), e="inoutsine")
            a.sound(t + 0.1, "click_small")
            a.mv("arm_left", t, t + 0.14, pos=(14, 36, -420), rot=(-40, 10, 50), e="inoutsine")
            a.mv("arm_left", t + 0.14, t + 0.3, pos=(10, 30, -420), rot=(-40, 10, 20), e="inoutsine")
        a.mv("gun", 1.6, 2.0, pos=(-96, 16, -60), rot=(2, 70, 24))
        a.key("choke", 2.1, pos=(0, 0, -9), rot=(0, 0, -450))
        a.key("choke", 2.6, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")
        a.sound(2.6, "click_small")
        a.mv("arm_left", 2.1, 2.6, pos=(14, 36, -420), rot=(-40, 10, 80), e="linear")
        a.mv("arm_left", 2.7, 3.2, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 2.8, 4.55)
        return a

    anims = [idle(m), draw(m, 0.8, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8, 0.8, 2.0), push=24, recover=0.32, length=0.4),
             fire_basic(m, "fire_aim", kick=(8, 0.8, 2.0), push=24, recover=0.28, length=0.36, aim=True),
             pump_cycle(m, "cycle", travel=(0, 0, 86)), pump_cycle(m, "cycle_aim", travel=(0, 0, 86), aim=True),
             *tube_reload(m), inspect(), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, SG_FP)


# =================================================================================================
# Mossberg 190 (16 gauge, bolt action, C-Lect-Choke, 2-round box magazine)
# =================================================================================================
def mossberg190():
    m = new_gun("mossberg190")
    body = m["body"]
    st = "steel"
    wd = "wood_light"
    body.cyl((0, 0, -10), 36, 220, st, sides=12)                            # receiver -120 .. 100
    body.box(0, 18.6, -4, 12, -96, -20, "rubber")                          # ejection port
    barrel(body, -120, -640, d=20, mat=st)
    body.box(-3, 3, 14, 20, -716, -706, "steel")                            # bead stud on the choke body
    body.box(-1.5, 1.5, 20, 23.5, -714, -708, "brass")
    # C-Lect-Choke: a big ribbed sleeve with a turning collar
    body.cyl((0, 0, -680), 30, 70, st, sides=12)
    col = body.bone("choke", pivot=(0, 0, -690))
    col.cyl((0, 0, -690), 34, 24, "steel_light", sides=12)
    for i in range(6):
        col.box(-17.6, 17.6, -2, 2, -700 + i * 4, -698 + i * 4, "rubber")
    col.box(-2, 2, 16, 19, -700, -680, "white")                              # index mark
    body.box(-16, 16, -40, -6, -440, -120, wd)                               # forend
    body.box(-17, 17, -52, -8, -120, 110, wd)
    body.box(-12, 12, -64, -52, -96, -40, "steel_dark")                      # mag well
    trigger_group(m, body, 20, y_top=-52, guard_depth=24, guard_len=58, guard_mat=st)
    sel = body.bone("selector", pivot=(10, 8, 100))
    sel.box(8, 14, 4, 16, 96, 106, "steel")
    _sporter_stock(body, 110, wd)
    _military_bolt(m, -84, 112, 40, handle_len=40, knob_d=16, d=22, cock=(18, 16))
    br = m["gun"].bone("shell_eject", pivot=(14, 6, -50))
    br.shell12((14, 6, -50), length=64, d=18)
    mag = m["gun"].bone("magazine", pivot=(0, -52, -68))
    mag.box(-11, 11, -100, -52, -94, -42, "steel_dark")
    mag.box(-12, 12, -106, -100, -96, -40, "steel_dark")
    mag.shell12((0, -46, -54), length=64, d=18)
    add_arms(m, right_hand=(10, -86, 160), left_hand=(-14, -46, -320), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -716), eject=(18, 6, -50), sight=(0, 24, 70))
    travel, hrot = (0, 0, 96), (0, 0, 80)

    def inspect():
        # click the C-Lect-Choke collar through its settings, then lift the bolt to peek at the shell
        a = Anim(m, "inspect", 4.6)
        a.mv("gun", 0.0, 0.5, pos=(-90, 10, -60), rot=(6, 62, 14), e="inoutsine")
        a.mv("arm_left", 0.2, 0.55, pos=(6, 40, -370), rot=(-40, 10, 20))
        a.key("choke", 0.0, rot=(0, 0, 0))
        a.key("choke", 0.6, rot=(0, 0, 0))
        for i in range(4):
            t = 0.7 + i * 0.28
            a.key("choke", t + 0.12, rot=(0, 0, -36 * (i + 1)), e="outquad")
            a.sound(t + 0.12, "click_small")
        a.key("choke", 2.0, rot=(0, 0, -144))
        a.key("choke", 2.3, rot=(0, 0, -72), e="inoutsine")                # back to modified
        a.sound(2.3, "click_small")
        a.mv("arm_left", 2.35, 2.7, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 2.2, 2.7, pos=(-30, 20, 30), rot=(4, -20, -26))
        a.mv("arm_right", 2.4, 2.6, pos=(20, 40, -30), rot=(-25, -20, -20))
        a.grab("arm_right", "bolt", 2.6, 3.7, fade_in=0.03, fade_out=0.06)
        a.key("bolt", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("bolt", 2.62, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("bolt", 2.74, pos=(0, 0, 0), rot=hrot, e="outquad")
        a.sound(2.72, "bolt_open")
        a.key("bolt", 2.94, pos=(0, 0, 30), rot=hrot, e="inoutsine")
        a.mv("gun", 2.9, 3.2, pos=(-40, 30, 40), rot=(10, -36, -50))
        a.key("bolt", 3.4, pos=(0, 0, 30), rot=hrot)
        a.key("bolt", 3.54, pos=(0, 0, 0), rot=hrot, e="inoutsine")
        a.key("bolt", 3.64, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
        a.sound(3.64, "bolt_close")
        a.mv("arm_right", 3.75, 4.0, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.7, 4.55)
        return a

    def cycle(name, aim):
        a = bolt_cycle(m, name, travel=travel, handle_rot=hrot, length=0.9, aim=aim)
        a.show("shell_eject", 0.3, 0.7)
        a.key("shell_eject", 0.3, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("shell_eject", 0.38, pos=(20, 30, 50), rot=(20, 0, -60), e="outquad")
        a.key("shell_eject", 0.7, pos=(180, -120, 200), rot=(200, 0, -300), e="inquad")
        return a

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8, 0.8, 1.8), push=24, recover=0.4, length=0.5),
             fire_basic(m, "fire_aim", kick=(8, 0.8, 1.8), push=24, recover=0.36, length=0.45, aim=True),
             cycle("cycle", False), cycle("cycle_aim", True),
             rifle_reload(m, "reload", 0.0, empty=False, style="ar", mag_out=60, tilt=(4, -6, -20)),
             inspect(), dry_fire(m)]
    apply_hidden(anims, ["shell_eject"])
    return GunAsset(m, anims, {"hip": SG_FP["hip"], "ads": {"dist": 0.2}})


# =================================================================================================
# Tikka T3 (synthetic, scoped, 3-round flush magazine)
# =================================================================================================
def _bolt_rifle(name, stock_mat, *, muzzle, butt, barrel_d, breech_d=29.0, nose=-450, fore=(-4, -34, -42), belly=-52,
                wrist=(-16, -60), comb=None, heel=-20, toe=-126, hw=(16, 18, 15, 17), trig_z=30, st="steel_dark",
                top_port=True, bolt_parent="body", handle_z=92, bolt_kw=None, pad_th=14.0, spacer=None, butt_gap=0.0,
                checker="polymer", scope_kw=None, scope_y=52, brass_len=56, guard_mat=None):
    """
    Scoped sporting / sniping bolt action on the rifle kit: tubular receiver, tapered barrel, a one-piece stock with
    pistol grip and recoil pad, chequered panels, sling studs, a bolt with a shroud that does not turn with it, the
    safety, and the scope in rings. `butt` is the rear-most z. Returns (model, top, bot) of the stock outline.
    """
    m = new_gun(name)
    body = m["body"]
    receiver(body, -115, 95, 32, st, port=(-80, -10), top_port=top_port, tang=(132, wrist[0] + 2, -4))
    stepped_barrel(body, -115, muzzle, breech_d, barrel_d, st, reinforce=36, cone=70, taper=1.2)
    zb = butt - butt_gap - 4 - pad_th - (1.6 if spacer else 0)
    top, bot = mil_stock(body, stock_mat, nose=nose, butt=(zb, heel, toe), action=(-115, 100), fore=fore, belly=belly,
                         wrist=wrist, grip=True, comb=comb, hw=hw)
    butt_plate(body, zb + butt_gap, toe, heel, hw[3], "polymer", th=4, pad="rubber", pad_th=pad_th, spacer=spacer)
    if checker:                                                          # grip and fore-end panels
        for sx in (-1, 1):
            body.box(sx * hw[2] - 0.3, sx * hw[2] + 0.3, wrist[1] - 10, wrist[1] + 26, 158, 196, checker)
            body.box(sx * hw[0] - 0.3, sx * hw[0] + 0.3, fore[1] + 8, fore[0] - 8, nose + 70, -180, checker)
    sling_swivel(body, 0, line_y(bot, nose + 50), nose + 50, along="x", w=16, drop=9, mat="steel")
    sling_swivel(body, 0, line_y(bot, zb - 70), zb - 70, along="x", w=16, drop=9, mat="steel")
    trigger_group(m, body, trig_z, y_top=belly, guard_depth=24, guard_len=60, guard_mat=guard_mat or st)
    kw = dict(d=19, handle_len=38, droop=32, knob_d=18)
    kw.update(bolt_kw or {})
    bolt(m, -70, 110, handle_z, parent=bolt_parent, **kw)
    sh = m[bolt_parent].bone("shroud", pivot=(0, 0, 0))                  # slides with the bolt, does not turn
    sh.cyl((0, 0, 118), 22, 16, st)
    sh.cyl((0, 0, 131), 22, 10, st, d2=13, steps=2)
    sh.cyl((0, 0, 136.3), 6, 0.6, "sight_orange", sides=8)               # cocking indicator
    rides(m, "shroud")
    control(body, "safety", (14, 6, 108), [(12, 16, 3, 9, 100, 112, "steel"), (14, 18, 7, 12, 98, 104, "steel")],
            turn=(-35, 0, 0))
    br = m["gun"].bone("brass", pivot=(0, 6, -30))
    br.cyl((0, 6, -20), 12, brass_len, "brass")
    br.cyl((0, 6, -20 + brass_len / 2 - 1), 13, 1.6, "brass")
    sc = body.bone("scope", pivot=(0, scope_y - 2, -10))
    skw = dict(length=320, tube_d=30, obj_d=48, eye_d=42, mount_y=17)
    skw.update(scope_kw or {})
    scope(sc, -10, scope_y, **skw)
    return m, top, bot


def tikka_t3():
    # Tikka T3 Lite: 1080 mm long, 570 mm barrel, grey synthetic stock, flush single-stack magazine
    m, top, bot = _bolt_rifle("tikka_t3", "polymer_grey", muzzle=-675, butt=404, barrel_d=16, nose=-452, top_port=False,
                              guard_mat="polymer", bolt_kw=dict(handle_len=36, droop=30, knob_d=17, knob_mat="polymer"))
    body = m["body"]
    body.box(-16.3, 16.3, -30, -27, -440, -130, "polymer")              # fore-end groove
    mag = m["gun"].bone("magazine", pivot=(0, -52, -40))
    straight_mag(mag, -50, -78, -4, 24, width=22, mat="polymer", round_d=12, round_len=84)
    control(body, "mag_release", (0, -54, -82), [(-4, 4, -60, -53, -90, -80, "polymer")], press=(0, 0, 3))
    add_arms(m, right_hand=(10, -86, 140), left_hand=(-14, -48, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -676), eject=(17, 8, -20), sight=(0, 52, 150))

    m.meta["integral_optic"] = {"zoom": 7.0, "reticle": "mildot", "eye": [0, 52, 150]}
    travel, hrot = (0, 0, 98), (0, 0, 70)

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(7.5, 0.6, 1.5), push=24, recover=0.42, length=0.52),
             fire_basic(m, "fire_aim", kick=(7.5, 0.6, 1.5), push=24, recover=0.38, length=0.48, aim=True),
             bolt_cycle(m, "cycle", travel=travel, handle_rot=hrot, length=0.78),
             bolt_cycle(m, "cycle_aim", travel=travel, handle_rot=hrot, length=0.78, aim=True),
             rifle_reload(m, "reload", 0.0, empty=False, style="ar", mag_out=40, tilt=(4, -6, -20)),
             Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["brass"])
    return GunAsset(m, anims, SCOPED_FP)


def savage10():
    # Savage Model 10 FCP-SR: 940 mm long, short heavy threaded barrel, AccuTrigger, ten-round box, top rail
    m, top, bot = _bolt_rifle("savage10", "polymer", muzzle=-521, butt=382, barrel_d=21, breech_d=27, nose=-430,
                              top_port=False, fore=(-4, -36, -42), hw=(17, 18, 15, 17),
                              bolt_kw=dict(handle_len=38, droop=28, knob="tactical", knob_d=14, knob_mat="polymer"))
    body = m["body"]
    body.cyl((0, 0, -527), 17, 12, "steel")                             # muzzle threads
    cap = body.bone("thread_cap", pivot=(0, 0, -532))
    cap.cyl((0, 0, -545), 24, 26, "steel_dark")
    for k in range(6):
        cap.box(-12.3, 12.3, -1, 1, -556, -536, "steel", rot=(0, 0, k * 30), pivot=(0, 0, -545))
    blade = m["trigger"].bone("accu_blade", pivot=(0, -54, 30))         # AccuTrigger safety blade
    blade.box(-1, 1, -70, -56, 27, 29, "sight_orange")
    body.rail(-120, 90, 16, mat="alloy")
    body.cyl((0, 0, -118), 34, 8, "steel")                              # barrel nut
    mag = m["gun"].bone("magazine", pivot=(0, -52, -40))
    straight_mag(mag, -50, -80, -6, 78, width=24, mat="steel_dark", round_d=12, round_len=57)
    control(body, "mag_release", (0, -54, -2), [(-4, 4, -68, -53, -5, -1, "steel_dark")], turn=(14, 0, 0))
    add_arms(m, right_hand=(10, -86, 140), left_hand=(-14, -48, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -558), eject=(17, 8, -20), sight=(0, 52, 150))

    m.meta["integral_optic"] = {"zoom": 8.0, "reticle": "mildot", "eye": [0, 52, 150]}
    travel, hrot = (0, 0, 80), (0, 0, 70)

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(5.5, 0.6, 1.2), push=18, recover=0.36, length=0.46),
             fire_basic(m, "fire_aim", kick=(5.5, 0.6, 1.2), push=18, recover=0.32, length=0.42, aim=True),
             bolt_cycle(m, "cycle", travel=travel, handle_rot=hrot, length=0.74),
             bolt_cycle(m, "cycle_aim", travel=travel, handle_rot=hrot, length=0.74, aim=True),
             rifle_reload(m, "reload", 0.0, empty=False, style="ar", mag_out=80, tilt=(4, -6, -20)),
             Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["brass"])
    return GunAsset(m, anims, SCOPED_FP)


GUNS = {"cdaly": cdaly, "mossberg190": mossberg190, "tikka_t3": tikka_t3, "savage10": savage10}
