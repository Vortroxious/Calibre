"""Sniper / precision pack: CheyTac M200 Intervention, AI L96A1, Remington 700, KAC SR-25, SVU, DSR-1."""
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden)
from ..templates import rifle_reload, bolt_cycle, bolt_load
from ..parts import (pistol_grip, trigger_group, curved_mag, straight_mag, barrel, muzzle_brake, scope, bipod,
                     picatinny_handguard)
from .snipers import _bolt, _ai_rifle, SNIPER_FP
from .hunting import _sporter_stock, _bolt_rifle
from ..common import moving
from ..pistolkit import control
from ..parts import pins, vents, sling_swivel
from ..riflekit import stock, line_y, butt_plate, bolt, rides
from .modern import _rifle_anims, _inspect, _flip_sights, _fp


def _bolt_anims(m, kick, push, travel, hrot, cyc_len=0.82, mag=True, mag_out=50, draw_len=0.85):
    anims = [idle(m), draw(m, draw_len, sound="draw_rifle"),
             fire_basic(m, "fire", kick=kick, push=push, recover=0.42, length=0.52),
             fire_basic(m, "fire_aim", kick=kick, push=push, recover=0.38, length=0.48, aim=True),
             bolt_cycle(m, "cycle", travel=travel, handle_rot=hrot, length=cyc_len),
             bolt_cycle(m, "cycle_aim", travel=travel, handle_rot=hrot, length=cyc_len, aim=True)]
    if mag:
        anims.append(rifle_reload(m, "reload", 0.0, empty=False, style="ar", mag_out=mag_out, tilt=(4, -6, -20)))
        hidden = ["brass"]
    else:
        anims += bolt_load(m, travel=travel, handle_rot=hrot)
        hidden = ["round_load", "brass"]
    anims += [_inspect(m), dry_fire(m)]
    apply_hidden(anims, hidden)
    return anims


def _brass(m, d=12, length=60):
    br = m["gun"].bone("brass", pivot=(0, 6, -30))
    br.cyl((0, 6, -20), d, length, "brass")


# =================================================================================================
# CheyTac M200 Intervention (.408)
# =================================================================================================
def intervention():
    # CheyTac M200 Intervention: 1346 mm long, 737 mm fluted barrel, tube fore-end with carry handle, sliding stock
    m = new_gun("intervention")
    body = m["body"]
    st, al = "steel_dark", "alloy_grey"
    body.rbox(-19, 19, -18, 20, -110, 130, al, r=7, edges="top")               # receiver
    body.box(10, 19.4, 0, 14, -70, -10, "rubber")                              # ejection port
    body.rail(-430, 126, 20, mat="alloy")                                      # long top rail
    body.cyl((0, 2, -275), 46, 330, al)                                        # free-float tube
    for ang in (60, 120, 240, 300):
        for z in range(-420, -150, 54):
            body.box(-4, 4, 24.4, 25.4, z, z + 30, "rubber", rot=(0, 0, ang), pivot=(0, 2, 0))
    body.cyl((0, 2, -443), 48, 8, st)                                          # tube nut
    for z in (-306, -204):                                                     # carry handle
        body.box(-5, 5, 24, 52, z, z + 10, "polymer")
    body.rbox(-7, 7, 50, 60, -310, -190, "polymer", r=3)
    barrel(body, -440, -847, d=24, mat=st)
    for k in range(6):
        body.box(-1, 1, 11.5, 12.3, -830, -470, "rubber", rot=(0, 0, k * 60 + 30), pivot=(0, 0, 0))
    body.cyl((0, 0, -884), 30, 74, st)                                         # long ported brake
    for z in (-906, -886, -866):
        body.box(-15.4, 15.4, -5, 5, z - 5, z + 5, "rubber")
        body.box(-5, 5, 14, 15.4, z - 4, z + 4, "rubber")
    body.cyl((0, 0, -921.3), 14, 0.6, "rubber", sides=8)
    bipod(body, -420, y=-21, legs_len=230, folded=True)
    body.rbox(-17, 17, -48, -18, -110, 150, al, r=3, edges="bottom")           # lower
    pins(body, 17, [(-32, -92), (-32, 124)], d=5, mat="steel")
    pistol_grip(body, 70, top_y=-48, length=92, width=28, depth=36, angle=-16, mat="polymer")
    trigger_group(m, body, 22, y_top=-48, guard_depth=28, guard_len=66, guard_mat=al)
    control(body, "safety", (-17, -30, 44), [(-20, -17, -33, -27, 26, 46, "steel")], turn=(-50, 0, 0))
    control(body, "mag_release", (0, -50, 2), [(-4, 4, -66, -49, 0, 4, st)], turn=(14, 0, 0))
    body.rbox(-16, 16, -50, 12, 130, 160, al, r=4)                             # rod housing
    # sliding stock on two rods, with the cheek pad, butt frame and monopod
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    for sy in (-4, -38):
        stock.cyl((0, sy, 266), 13, 220, "steel_parked")
    stock.rbox(-16, 16, 3, 20, 250, 368, "polymer", r=6, edges="top")
    stock.rbox(-17, 17, -112, 14, 372, 410, al, r=5)
    stock.profile(-8, 8, [(300, -44), (372, -44)], [(300, -50), (372, -108)], al)
    butt_plate(stock, 410, -112, 14, 17, al, th=3, pad="rubber", pad_th=12)
    stock.cyl((0, -124, 392), 10, 26, st, axis="y", sides=16)                  # monopod
    stock.cyl((0, -139, 392), 18, 4, "rubber", axis="y", sides=16)
    bolt(m, -70, 126, 110, parent="gun", d=22, handle_len=32, droop=28, knob_d=22, knob_mat="polymer")
    sh = m["gun"].bone("shroud", pivot=(0, 0, 0))
    sh.cyl((0, 0, 135), 26, 18, st)
    sh.cyl((0, 0, 149), 26, 10, st, d2=16, steps=2)
    rides(m, "shroud")
    _brass(m, 15, 72)
    mag = m["gun"].bone("magazine", pivot=(0, -48, -40))
    straight_mag(mag, -46, -80, 0, 100, width=30, mat="steel_dark", round_d=15, round_len=96)
    sc = body.bone("scope", pivot=(0, 62, -40))
    scope(sc, -40, 62, length=380, tube_d=34, obj_d=60, eye_d=44, mat="steel_dark", mount_y=26)
    add_arms(m, right_hand=(10, -100, 104), left_hand=(-14, -40, -380), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -922), eject=(20, 8, -40), sight=(0, 62, 172))

    m.meta["integral_optic"] = {"zoom": 14.0, "reticle": "mildot", "eye": [0, 62, 172]}
    anims = _bolt_anims(m, (10, 0.8, 1.8), 30, (0, 0, 120), (0, 0, 66), cyc_len=0.95, mag_out=60, draw_len=1.0)
    return GunAsset(m, anims, {"hip": {"pos": [0.13, -0.16, -0.2], "rot": [0, 3, 0]}, "ads": {"dist": 0.07}})


# =================================================================================================
# Accuracy International L96A1 (green thumbhole stock)
# =================================================================================================
def l96():
    # Accuracy International L96A1: 1180 mm long, 655 mm barrel, green thumbhole stock bolted over the chassis
    m = _ai_rifle("l96", muzzle=-738, barrel_d=22, brake=None, flutes=False)
    body = m["body"]
    mag = m["gun"].bone("magazine", pivot=(0, -44, -30))
    straight_mag(mag, -46, -86, -6, 78, width=26, mat="steel_dark", round_d=12, round_len=66)
    sc = body.bone("scope", pivot=(0, 52, -10))
    scope(sc, -10, 52, length=300, tube_d=30, obj_d=46, eye_d=40, mat="polymer_od", mount_y=20)
    add_arms(m, right_hand=(10, -96, 100), left_hand=(-14, -48, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -739), eject=(17, 8, -20), sight=(0, 52, 150))

    m.meta["integral_optic"] = {"zoom": 6.0, "reticle": "mildot", "eye": [0, 52, 150]}
    anims = _bolt_anims(m, (7, 0.6, 1.4), 22, (0, 0, 96), (0, 0, 66), mag_out=46)
    return GunAsset(m, anims, SNIPER_FP)


# =================================================================================================
# Remington 700 (walnut sporter, internal box magazine)
# =================================================================================================
def rem700():
    # Remington 700 BDL: 1060 mm long, walnut Monte Carlo stock with black fore-end tip and grip cap
    m, top, bot = _bolt_rifle("rem700", "wood", muzzle=-660, butt=399, barrel_d=17, nose=-440, comb=-8, heel=-18,
                              checker="wood_red", spacer="white", bolt_parent="gun", pad_th=12,
                              bolt_kw=dict(handle_len=34, droop=38, knob_d=17),
                              scope_kw=dict(length=300, tube_d=28, obj_d=44, eye_d=38, mat="steel_dark", mount_y=16),
                              scope_y=50)
    body = m["body"]
    yt = line_y(bot, -440)
    body.rbox(-16.3, 16.3, yt - 0.3, -3.7, -441, -406, "polymer", r=4)  # fore-end tip
    body.box(-16.4, 16.4, yt - 0.4, -3.6, -406, -404, "white")
    body.rbox(-15.3, 15.3, -88, -84, 172, 204, "polymer", r=1.5, axis="y")           # grip cap
    body.box(-12, 12, -56, -52, -92, 4, "steel_dark")                   # hinged floorplate and its latch
    body.cyl((0, -56.2, -86), 5, 0.8, "steel", axis="y", sides=8)
    body.box(-2.5, 2.5, -58, -52, 2, 8, "steel")
    rl = m["gun"].bone("round_load", pivot=(0, 10, -20))
    rl.round_((0, 10, -20), 66, 12)
    add_arms(m, right_hand=(10, -86, 140), left_hand=(-14, -48, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -662), eject=(17, 8, -20), sight=(0, 50, 150))

    m.meta["integral_optic"] = {"zoom": 6.0, "reticle": "mildot", "eye": [0, 50, 150]}
    anims = _bolt_anims(m, (6, 0.6, 1.3), 20, (0, 0, 90), (0, 0, 70), cyc_len=0.76, mag=False)
    return GunAsset(m, anims, SNIPER_FP)


# =================================================================================================
# SVU (bullpup SVD with PSO-1)
# =================================================================================================
def svu():
    # OTs-03 SVU: bullpup Dragunov, 900 mm long, 520 mm barrel, big slotted muzzle device, PSO-1 on the side rail
    m = new_gun("svu")
    body = m["body"]
    p, st = "polymer", "steel_dark"
    body.rbox(-16, 16, -34, 10, -150, 330, st, r=3, edges="bottom")            # receiver
    body.rbox(-14, 14, 10, 24, -30, 330, st, r=6.5, edges="top")               # cover
    body.box(-3, 3, 24, 25, 0, 300, st)
    pins(body, 16, [(-20, -130), (-22, 90), (-4, 300)], d=4.5, mat="steel")
    body.box(8, 16.4, 2, 10.2, 140, 212, "rubber")                             # ejection opening
    body.box(8, 14.5, 10, 16, 140, 212, "rubber")
    body.rbox(-18, 18, -48, -6, -150, 60, p, r=4, edges="bottom")              # polymer lower shell
    pistol_grip(body, -70, top_y=-46, length=86, width=26, depth=32, angle=-10, mat=p)
    trigger_group(m, body, -104, y_top=-48, guard_depth=30, guard_len=84, guard_mat=p)
    body.rbox(-15, 15, 24, 34, 170, 312, p, r=5, edges="top")                  # cheek rest
    body.rbox(-17, 17, -82, 26, 330, 340, st, r=4)                             # butt frame
    body.profile(-12, 12, [(250, -34), (330, -34)], [(250, -40), (330, -80)], st)
    body.rbox(-18, 18, -86, 28, 340, 360, "rubber", r=7)
    for i in range(5):
        body.box(-14, 14, -76 + i * 22, -72 + i * 22, 360, 360.5, "polymer")
    # hand guard, gas block, barrel, muzzle device
    body.rbox(-17, 17, -30, 27, -330, -150, p, r=9)
    vents(body, 17, -4, 6, -320, -165, n=5, fill=0.6)
    body.box(-17.4, 17.4, 12, 14, -326, -154, "rubber")
    body.rbox(-9, 9, -10, 28, -352, -330, st, r=3, edges="top")                # gas block
    body.box(-5, 5, 28, 31, -350, -318, st)                                    # folded front sight
    body.box(-6, 6, 25, 28, 30, 56, st)                                        # folded rear sight
    barrel(body, -150, -424, d=17, mat=st)
    body.cyl((0, 0, -480), 34, 120, st)
    body.cyl((0, 0, -424), 22, 10, st)
    for z in (-520, -496, -472, -448):
        body.box(-17.4, 17.4, -7, 7, z - 6, z + 6, "rubber")
        body.box(-7, 7, 16, 17.4, z - 5, z + 5, "rubber")
    body.cyl((0, 0, -540.3), 14, 0.6, "rubber", sides=8)
    sling_swivel(body, 0, -30, -310, along="x", w=16, drop=9, mat=st)
    sel = body.bone("selector", pivot=(16, -14, 214))                          # AK-pattern safety lever
    sel.box(16, 18, -18, -10, 130, 214, "steel")
    sel.box(18, 22, -22, -14, 130, 142, "steel")
    bolt = body.bone("bolt", pivot=(20, 2, 160))
    bolt.box(8.4, 15.6, 3, 13, 150, 204, "steel_light")
    bolt.box(15.6, 28, 4, 10, 150, 160, "steel_light")
    bolt.cyl((30, 7, 155), 12, 8, "steel_light", axis="x", sides=16)
    pso = body.bone("pso1", pivot=(0, 60, 40))                                 # PSO-1 on its side-rail bracket
    pso.box(-20, -16, -6, 50, -10, 90, st)
    pso.rbox(-20, 8, 44, 50, -6, 86, st, r=2)
    scope(pso, 30, 70, length=280, tube_d=28, obj_d=40, eye_d=34, mat="steel_dark", mount_y=50)
    pso.cyl((0, 70, 178), 38, 24, "rubber")
    mag = m["gun"].bone("magazine", pivot=(0, -40, 140))
    curved_mag(mag, -34, 110, 68, 128, curve=8, segs=3, width=24, mat="steel_dark", rib_mat="steel", round_d=11,
               round_len=70)
    control(body, "mag_release", (0, -36, 186), [(-5, 5, -60, -34, 184, 188, st)], turn=(-18, 0, 0))
    add_arms(m, right_hand=(8, -96, -40), left_hand=(-12, -36, -250), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -541), under=(0, -32, -250), eject=(18, 6, 170), sight=(0, 70, 186))

    m.meta["integral_optic"] = {"zoom": 4.0, "reticle": "pso1", "eye": [0, 70, 186]}
    cyc = dict(bone="bolt", travel=(0, 0, 110), t_back=0.022, t_fwd=0.062)
    anims = _rifle_anims(m, 6.0, (4.8, 0.6, 1.4), 16, "ak", cyc, ch="bolt", ch_travel=(0, 0, 110), selector=(0, 0, 0),
                         rock=10, rec=0.22, length=0.34, tilt=(4, -10, -30), tilt_pos=(-30, 14, 10), draw_len=0.8)
    return GunAsset(m, anims, {"hip": {"pos": [0.12, -0.15, -0.16], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.07}})


# =================================================================================================
# DSR-Precision DSR-1 (bullpup bolt action, .338 LM)
# =================================================================================================
def dsr1():
    # DSR-1: bullpup bolt action, 990 mm long, 650 mm fluted barrel, spare-magazine holder ahead of the guard
    m = new_gun("dsr1")
    body = m["body"]
    k, al = "polymer", "alloy_grey"
    body.rbox(-20, 20, -40, 20, -160, 290, al, r=5, edges="top")               # chassis
    body.rail(-430, 280, 20, mat="alloy")                                      # full-length top rail
    body.box(10, 20.4, -2, 14, 110, 180, "rubber")                             # ejection port behind the grip
    pins(body, 20, [(-24, -140), (-24, 60), (-24, 260)], d=5, mat="steel")
    body.rbox(-19, 19, -36, 18, -430, -160, al, r=8, edges="bottom")           # slotted fore-end
    vents(body, 19, -14, 2, -415, -175, n=6, fill=0.6)
    barrel(body, -430, -594, d=22, mat="steel_dark")
    for i in range(6):
        body.box(-1, 1, 10.5, 11.3, -584, -440, "rubber", rot=(0, 0, i * 60 + 30), pivot=(0, 0, 0))
    muzzle_brake(body, -594, d=30, length=66, ports=3)
    body.rbox(-16, 16, -60, -36, -420, -300, k, r=5, edges="bottom")           # front grip block
    bipod(body, -400, y=-60, legs_len=190, folded=True, fold="back")
    # spare-magazine holder ahead of the trigger guard (the DSR's signature)
    body.rbox(-17, 17, -56, -40, -184, -106, k, r=3, edges="bottom")
    body.rbox(-14, 14, -128, -50, -178, -112, "steel_dark", r=2.5)
    body.box(-15, 15, -134, -128, -180, -110, "steel_dark")
    pistol_grip(body, -60, top_y=-40, length=96, width=28, depth=36, angle=-14, mat=k)
    trigger_group(m, body, -94, y_top=-40, guard_depth=30, guard_len=70, guard_mat=al)
    control(body, "safety", (-20, -10, -56), [(-23, -20, -13, -7, -74, -54, "steel")], turn=(-50, 0, 0))
    control(body, "mag_release", (0, -42, 174), [(-4, 4, -58, -41, 172, 176, "steel_dark")], turn=(-16, 0, 0))
    # butt: strut, monopod, adjustable cheek piece, pad
    body.profile(-14, 14, [(190, -40), (280, -40)], [(190, -52), (280, -110)], k)
    body.rbox(-20, 20, -114, -38, 276, 316, k, r=5)
    body.cyl((0, -112, 250), 10, 54, "steel_dark", axis="y", sides=16)
    body.cyl((0, -141, 250), 18, 4, "rubber", axis="y", sides=16)
    for z in (214, 284):
        body.cyl((0, 26, z), 8, 12, "steel", axis="y", sides=8)
    body.rbox(-18, 18, 30, 44, 196, 304, k, r=6, edges="top")                  # cheek piece on its posts
    butt_plate(body, 316, -114, 20, 20, k, th=3, pad="rubber", pad_th=11)
    bolt(m, 80, 270, 250, parent="gun", d=22, mat="steel_light", handle_len=28, droop=30, knob_d=20,
         knob_mat="polymer")                                                   # the bolt sits behind the grip
    br = m["gun"].bone("brass", pivot=(0, 6, 140))
    br.cyl((0, 6, 150), 14, 70, "brass")
    mag = m["gun"].bone("magazine", pivot=(0, -40, 130))
    straight_mag(mag, -38, 100, 170, 80, width=28, mat="steel_dark", round_d=14, round_len=70)
    sc = body.bone("scope", pivot=(0, 60, 20))
    scope(sc, 20, 60, length=340, tube_d=34, obj_d=56, eye_d=44, mat="steel_dark", mount_y=24)
    add_arms(m, right_hand=(10, -100, -36), left_hand=(-14, -56, -360), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -661), eject=(20, 8, 150), sight=(0, 60, 210))

    m.meta["integral_optic"] = {"zoom": 12.0, "reticle": "mildot", "eye": [0, 60, 210]}
    anims = _bolt_anims(m, (8, 0.7, 1.6), 24, (0, 0, 100), (0, 0, 66), cyc_len=0.9, mag_out=50)
    return GunAsset(m, anims, {"hip": {"pos": [0.12, -0.15, -0.14], "rot": [0, 3, 0]}, "ads": {"dist": 0.07}})


GUNS = {"intervention": intervention, "l96": l96, "rem700": rem700, "svu": svu, "dsr1": dsr1}
