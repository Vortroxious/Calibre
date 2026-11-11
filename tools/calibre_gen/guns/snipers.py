"""Remington M24 SWS, Accuracy International AWM, Barrett M82A1 — all with their issued scopes."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden, along)
from ..templates import rifle_reload, bolt_cycle, bolt_load, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, muzzle_brake, scope, bipod)
from ..common import moving
from ..parts import pins, vents, sling_swivel
from ..pistolkit import control
from ..riflekit import stock, line_y, butt_plate, bolt, rides
from .hunting import _bolt_rifle

SNIPER_FP = {"hip": {"pos": [0.12, -0.15, -0.18], "rot": [0, 3, 0]}, "ads": {"dist": 0.075}}


def _bolt(m, parent, z_front, z_rear, handle_z, knob=True, mat="steel_light", d=19.0):
    b = m[parent].bone("bolt", pivot=(0, 0, 0))
    b.cyl((0, 0, (z_front + z_rear) / 2), d, z_rear - z_front, mat)
    b.box(8, 40, -4, 4, handle_z - 5, handle_z + 5, mat, rot=(0, 0, -20), pivot=(8, 0, handle_z))  # handle
    if knob:
        b.box(36, 52, -18, -2, handle_z - 8, handle_z + 8, "polymer", rot=(0, 0, -20), pivot=(8, 0, handle_z))
    b.box(-8, 8, -8, 8, z_rear, z_rear + 14, "steel_dark")                                         # shroud
    return b


def _ai_rifle(name, *, muzzle, barrel_d, brake=None, flutes=False, g="polymer_od", rec="steel_dark", butt=442):
    """
    Accuracy International chassis rifle: flat-bottomed receiver, free-floated barrel, two polymer stock halves bolted
    over the chassis, thumbhole grip, adjustable cheek piece and butt spacers, spigot bipod. No magazine or scope.
    """
    m = new_gun(name)
    body = m["body"]
    body.rbox(-17, 17, -14, 18, -100, 120, rec, r=8, edges="top")                 # receiver
    body.box(9, 17.4, 2, 13, -62, 0, "rubber")                                    # ejection port
    body.rbox(-10, 10, 17, 20, -92, 112, "steel_dark", r=1.2, edges="top")        # scope dovetail
    zf = muzzle + (brake or 0)
    body.cyl((0, 0, -110), barrel_d + 8, 22, rec)                                 # barrel shank
    barrel(body, -100, zf, d=barrel_d, mat="steel_dark")
    if flutes:
        for k in range(6):
            body.box(-1, 1, barrel_d / 2 - 0.5, barrel_d / 2 + 0.3, zf + 70, -200, "rubber", rot=(0, 0, k * 60 + 30),
                     pivot=(0, 0, 0))
    if brake:
        muzzle_brake(body, zf, d=barrel_d + 5, length=brake, ports=2)
    else:
        body.cyl((0, 0, muzzle + 11), barrel_d + 3, 22, "steel_dark")
        body.cyl((0, 0, muzzle - 0.3), barrel_d * 0.5, 0.6, "rubber", sides=8)
    # fore-end and receiver sides
    stock(body, [(-430, -11), (124, -11)], [(-430, -36), (-404, -46), (-110, -52), (124, -52)], [(-430, 124, 25)], g)
    body.rbox(-25, 25, -14, 3, -104, 124, g, r=2.5, edges="top")
    for z in (-390, -260, -130, 10, 100):                                         # the stock bolts
        for sx in (-1, 1):
            body.cyl((sx * 25.3, -30, z), 7, 0.8, "steel_dark", axis="x", sides=8)
            body.cyl((sx * 25.8, -30, z), 3.4, 0.5, "rubber", axis="x", sides=8)
    for sx in (-1, 1):
        body.box(sx * 25 - 0.3, sx * 25 + 0.3, -44, -20, -380, -160, "olive")     # grip stipple
    body.rbox(-17, 17, -126, -48, 62, 112, g, r=8, axis="y", rot=(-14, 0, 0), pivot=(0, -50, 90))
    trigger_group(m, body, 30, y_top=-52, guard_depth=30, guard_len=70, guard_mat=g)
    control(body, "mag_release", (0, -54, -2), [(-4, 4, -70, -53, -5, -1, "steel_dark")], turn=(14, 0, 0))
    # thumbhole butt: low behind the action so the bolt clears it, then the raised cheek piece
    zb = butt - 16.6
    st = m["gun"].bone("stock", pivot=(-20, 0, 124))
    stock(st, [(124, -12), (250, -12), (264, 6), (zb, 6)], [(124, -40), (172, -40), (198, -118), (zb, -124)],
          [(124, zb, 24)], g)
    st.profile(-20, 20, [(100, -110), (200, -104)], [(100, -127), (200, -123)], g)        # strap under the thumbhole
    st.rbox(-17, 17, 6, 20, 276, 384, g, r=6, edges="top")                        # adjustable cheek piece
    for z in (300, 360):
        for sx in (-1, 1):
            st.cyl((sx * 24.6, -8, z), 9, 1.4, "steel_dark", axis="x", sides=8)
    for z, y in ((300, -70), (400, -30), (400, -100)):
        for sx in (-1, 1):
            st.cyl((sx * 24.3, y, z), 7, 0.8, "steel_dark", axis="x", sides=8)
    butt_plate(st, zb, -124, 6, 24, "polymer", th=3, pad="rubber", pad_th=12, spacer="polymer")
    st.cyl((0, -128, 392), 12, 10, "steel_dark", axis="y", sides=16)              # rear spike housing
    bipod(body, -412, y=-44, legs_len=200, folded=True)
    bolt(m, -60, 116, 102, parent="gun", d=21, mat="steel_dark", handle_len=28, droop=38, knob_d=23,
         knob_mat="polymer")
    sh = m["gun"].bone("shroud", pivot=(0, 0, 0))
    sh.cyl((0, 0, 125), 24, 18, "steel_dark")
    sh.cyl((0, 0, 139), 24, 10, "steel_dark", d2=15, steps=2)
    sf = sh.bone("safety", pivot=(12, 4, 124))
    sf.box(11, 15, 2, 6, 112, 126, "steel")
    sf.box(13, 17, 4, 9, 110, 116, "steel")
    moving(m, "safety", rot=(-40, 0, 0))
    rides(m, "shroud")
    br = m["gun"].bone("brass", pivot=(0, 6, -30))
    br.cyl((0, 6, -20), barrel_d / 2 + 1, 60, "brass")
    return m


def m24():
    # M24 SWS: 1092 mm long, heavy 610 mm barrel, wide composite stock with the adjustable butt, fixed 10x scope
    m, top, bot = _bolt_rifle("m24", "polymer_od", muzzle=-720, butt=371, barrel_d=22, breech_d=30, nose=-560,
                              fore=(-6, -38, -44), belly=-46, wrist=(-14, -58), comb=-3, heel=-5, toe=-106,
                              hw=(22, 23, 17, 21), trig_z=40, bolt_parent="gun", handle_z=96, checker=None, butt_gap=10,
                              bolt_kw=dict(handle_len=36, droop=32, knob_d=18, mat="steel_dark"),
                              scope_kw=dict(length=330, tube_d=30, obj_d=50, eye_d=42, mount_y=17, turrets=True))
    body = m["body"]
    zb = 371 - 10 - 4 - 14
    body.cyl((0, -56, zb + 5), 40, 4, "steel", sides=24)                # length-of-pull thumbwheel
    for y in (-30, -82):
        body.cyl((0, y, zb + 5), 8, 10, "steel_light")
    body.box(-13, 13, -50, -46, -96, 0, "steel_dark")                   # floorplate
    body.box(-2.5, 2.5, -52, -46, -2, 6, "steel")
    for sx in (-1, 1):                                                  # palm swell and stipple bands
        body.box(sx * 17 - 0.3, sx * 17 + 0.3, -68, -32, 158, 196, "olive")
        body.box(sx * 22 - 0.3, sx * 22 + 0.3, -32, -14, -500, -200, "olive")
    rl = m["gun"].bone("round_load", pivot=(0, 10, -20))
    rl.round_((0, 10, -20), 70, 12)
    add_arms(m, right_hand=(10, -80, 150), left_hand=(-14, -50, -260), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -721), under=(0, line_y(bot, -360), -360), eject=(18, 8, -20), sight=(0, 52, 150))

    m.meta["integral_optic"] = {"zoom": 10.0, "reticle": "mildot", "eye": [0, 52, 150]}

    cyc = bolt_cycle(m, "cycle", travel=(0, 0, 96), handle_rot=(0, 0, 66))
    cyc_aim = bolt_cycle(m, "cycle_aim", travel=(0, 0, 96), handle_rot=(0, 0, 66), aim=True)
    anims = [idle(m), draw(m, 0.8, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(7, 0.6, 1.4), push=22, recover=0.4, length=0.5),
             fire_basic(m, "fire_aim", kick=(7, 0.6, 1.4), push=22, recover=0.36, length=0.45, aim=True),
             cyc, cyc_aim, *bolt_load(m, travel=(0, 0, 96), handle_rot=(0, 0, 66)), Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass"])
    return GunAsset(m, anims, SNIPER_FP)


def awm():
    # Accuracy International AWM: 1230 mm long, 686 mm fluted barrel with brake, thumbhole chassis stock
    A = 0.0
    m = _ai_rifle("awm", muzzle=-788, barrel_d=24, brake=60, flutes=True)
    body = m["body"]
    mag = m["gun"].bone("magazine", pivot=(0, -50, -30))
    straight_mag(mag, -46, -90, -4, 84, width=26, mat="steel_dark", round_d=13, round_len=82)
    sc = body.bone("scope", pivot=(0, 52, -10))
    scope(sc, -10, 54, length=340, tube_d=34, obj_d=56, eye_d=44, mount_y=20)
    add_arms(m, right_hand=(10, -96, 104), left_hand=(-14, -54, -280), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -789), under=None, eject=(18, 8, -20), sight=(0, 54, 160))

    m.meta["integral_optic"] = {"zoom": 12.0, "reticle": "mildot", "eye": [0, 54, 160]}

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(9, 0.6, 1.6), push=26, recover=0.45, length=0.55),
             fire_basic(m, "fire_aim", kick=(9, 0.6, 1.6), push=26, recover=0.4, length=0.5, aim=True),
             bolt_cycle(m, "cycle", travel=(0, 0, 104), handle_rot=(0, 0, 66)),
             bolt_cycle(m, "cycle_aim", travel=(0, 0, 104), handle_rot=(0, 0, 66), aim=True),
             rifle_reload(m, "reload", A, empty=False, style="ar", mag_out=50, tilt=(4, -6, -20)),
             Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["brass"])
    return GunAsset(m, anims, SNIPER_FP)


def m82a1():
    # Barrett M82A1: 1448 mm long, 737 mm fluted barrel, arrowhead brake, stamped two-part receiver
    A = 4.0
    m = new_gun("m82a1")
    body = m["body"]
    st = "steel_parked"
    body.rbox(-24, 24, -60, 0, -320, 455, st, r=4, edges="bottom")                  # lower receiver
    body.box(-24.4, 24.4, -24, -21, -310, 445, "steel_dark")                        # stamped rib
    pins(body, 24, [(-10, -300), (-34, -110), (-10, 300), (-10, 440)], d=7, mat="steel")
    pistol_grip(body, 60, top_y=-60, length=96, width=30, depth=40, angle=-16, mat="polymer")
    trigger_group(m, body, 20, y_top=-60, guard_depth=28, guard_len=66, guard_mat=st)
    control(body, "safety", (-24, -40, 44), [(-27, -24, -43, -37, 26, 46, "steel")], turn=(-50, 0, 0))
    control(body, "mag_release", (0, -62, 66), [(-5, 5, -78, -61, 62, 66, "steel_dark")], turn=(-16, 0, 0))
    body.rbox(-25, 25, -64, 38, 455, 462, "steel_dark", r=5)                        # back plate and recoil pad
    body.rbox(-25, 25, -64, 38, 462, 480, "rubber", r=7)
    body.rbox(-11, 11, -122, -58, 384, 420, "polymer", r=7, axis="y", rot=(-10, 0, 0), pivot=(0, -60, 400))   # rear grip
    body.cyl((0, -124, 414), 9, 6, "steel", axis="y", sides=8)                      # monopod socket
    bipod(body, -280, y=-60, legs_len=260, folded=True)
    # upper receiver + barrel recoil together
    up = m["gun"].bone("upper", pivot=(0, 0, 0))
    up.rbox(-24, 24, 0, 36, -360, 455, st, r=5, edges="top")
    up.rail(-200, 300, 36, mat="alloy")
    up.box(10, 24.4, 4, 26, -80, -20, "rubber")                                     # ejection port
    for z in range(-350, -210, 24):
        for sx in (-1, 1):
            up.box(sx * 24 - 0.4, sx * 24 + 0.4, 8, 28, z, z + 12, "rubber")        # cooling slots
    up.box(-24.4, 24.4, 15, 18, 20, 445, "steel_dark")
    up.rbox(-18, 18, 36, 46, 330, 446, "polymer", r=4, edges="top")                 # cheek pad
    up.cyl((0, 0, -368), 44, 16, st)                                                # barrel bushing
    barrel(up, -360, -868, d=30)
    for k in range(6):
        up.box(-1.4, 1.4, 14.4, 15.3, -850, -420, "rubber", rot=(0, 0, k * 60 + 30), pivot=(0, 0, 0))
    for sx in (-1, 1):
        up.cyl((sx * 19, -8, -405), 7, 74, "steel")                                 # barrel spring rods
    up.cyl((0, 0, -876), 36, 16, st)                                                # two-chamber arrowhead brake
    up.rbox(-42, 42, -17, 17, -928, -884, st, r=4)
    up.rbox(-34, 34, -17, 17, -968, -928, st, r=4)
    up.box(-42.4, 42.4, -11, 11, -918, -896, "rubber")
    up.box(-34.4, 34.4, -11, 11, -958, -940, "rubber")
    up.cyl((0, 0, -968.3), 18, 0.6, "rubber", sides=8)
    ch = up.bone("charging_handle", pivot=(24, 16, -80))
    ch.box(24, 40, 11, 21, -86, -74, "steel")
    ch.cyl((44, 16, -80), 16, 10, "polymer", axis="x", sides=16)
    for z in (-160, -70):                                                           # carry handle
        up.box(-5, 5, 38, 66, z, z + 10, "steel")
    up.rbox(-7, 7, 62, 72, -164, -56, "polymer", r=3)
    mag = m["gun"].bone("magazine", pivot=(0, -60, -40))
    straight_mag(mag, -60, -90, 60, 130, width=34, mat="steel_dark", round_d=20, round_len=130)
    sc = up.bone("scope", pivot=(0, 80, 120))
    scope(sc, 120, 82, length=360, tube_d=34, obj_d=56, eye_d=44, mount_y=39)
    add_arms(m, right_hand=(10, -104, 80), left_hand=(-16, -92, 400), right_rot=(34, 14, 6), left_rot=(30, -22, -4))
    add_sockets(m, muzzle=(0, 0, -969), eject=(24, 14, -50), sight=(0, 82, 300), parent="body")

    m.meta["integral_optic"] = {"zoom": 10.0, "reticle": "mildot", "eye": [0, 82, 300]}

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
             Anim(m, "inspect", 1.0), dry_fire(m)]
    return GunAsset(m, anims, {"hip": {"pos": [0.13, -0.16, -0.24], "rot": [0, 3, 0]}, "ads": {"dist": 0.075}})


GUNS = {"m24": m24, "awm": awm, "m82a1": m82a1}
