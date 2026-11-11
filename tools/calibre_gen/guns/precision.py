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
    m = new_gun("intervention")
    body = m["body"]
    st, al = "steel_dark", "alloy_grey"
    body.box(-19, 19, -18, 20, -110, 130, al)                                  # receiver
    body.box(0, 19.4, -2, 16, -70, -10, "rubber")                             # ejection port
    body.rail(-560, 126, 20, mat="alloy")                                       # long top rail
    # free-floated tube handguard with the carry handle and bipod pivot
    body.cyl((0, 2, -330), 44, 440, al, sides=12)
    for z in range(-520, -150, 46):
        body.box(-22.4, 22.4, -6, 10, z, z + 22, "rubber")                    # lightening slots
    body.box(-6, 6, 22, 30, -300, -200, "polymer")                            # carry handle on the rail
    body.box(-6, 6, 30, 60, -306, -296, "polymer")
    body.box(-6, 6, 30, 60, -204, -194, "polymer")
    body.box(-8, 8, 56, 64, -306, -194, "polymer")
    barrel(body, -550, -860, d=22)
    for z in range(-840, -570, 30):                                            # fluting
        body.box(-11.6, 11.6, -3, 3, z, z + 18, "steel")
    muzzle_brake(body, -860, d=30, length=74, ports=3)
    bipod(body, -520, y=-22, legs_len=230, folded=True)
    # lower + grip
    body.box(-17, 17, -48, -18, -110, 150, al)
    pistol_grip(body, 70, top_y=-48, length=92, width=28, depth=36, angle=-16, mat="polymer")
    trigger_group(m, body, 22, y_top=-48, guard_depth=28, guard_len=66, guard_mat=al)
    # collapsing skeleton stock with monopod
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    for sy in (-6, -40):
        stock.box(-6, 6, sy - 8, sy + 8, 150, 420, "steel_parked")
    stock.box(-16, 16, -20, 14, 330, 420, "polymer")                          # cheek pad
    stock.box(-18, 18, -110, 16, 420, 440, al)
    stock.box(-20, 20, -116, 20, 438, 450, "rubber")
    stock.box(-6, 6, -150, -60, 380, 392, "steel_dark")                       # monopod
    _bolt(m, "gun", -70, 126, 110, mat="steel_light", d=22)
    _brass(m, 15, 72)
    mag = m["gun"].bone("magazine", pivot=(0, -48, -40))
    straight_mag(mag, -46, -80, 0, 100, width=30, mat="steel_dark", round_d=15, round_len=96)
    sc = body.bone("scope", pivot=(0, 62, -40))
    scope(sc, -40, 62, length=380, tube_d=34, obj_d=60, eye_d=44, mat="steel_dark", mount_y=26)
    add_arms(m, right_hand=(10, -100, 104), left_hand=(-14, -40, -380), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -934), eject=(20, 8, -40), sight=(0, 62, 172))
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
    m = new_gun("svu")
    body = m["body"]
    p, st = "polymer", "steel_dark"
    body.box(-18, 18, -46, 14, -160, 330, p)                                  # bullpup shell
    body.taper(-18, 18, 330, 370, 14, 4, -46, -96, p)
    body.box(-19, 19, -100, 8, 366, 380, "rubber")
    body.box(-16, 16, 14, 30, 120, 300, p)                                      # cheek riser
    body.box(0, 18.3, -6, 12, 140, 210, "rubber")                             # ejection port
    body.box(-16, 16, -32, 12, -400, -160, p)                                  # handguard
    for z in range(-380, -180, 30):
        body.box(-16.4, 16.4, -24, 0, z, z + 14, "rubber")
    barrel(body, -400, -560, d=16)
    body.box(-14, 14, -14, 14, -660, -560, st)                                 # big triple-baffle brake
    for z in (-650, -626, -602, -578):
        body.box(-14.4, 14.4, -8, 8, z, z + 10, "rubber")
    # front + rear folding iron sights
    body.box(-2, 2, 14, 40, -390, -384, st)
    body.box(-8, 8, 30, 46, 60, 70, st)
    pistol_grip(body, -70, top_y=-46, length=86, width=26, depth=32, angle=-10, mat=p)
    trigger_group(m, body, -104, y_top=-46, guard_depth=30, guard_len=84, guard_mat=p)
    sel = body.bone("selector", pivot=(18, 0, 120))
    sel.box(18, 20, -6, 8, 120, 200, "steel")
    bolt = body.bone("bolt", pivot=(20, 2, 160))
    bolt.box(1, 16, -6, 8, 150, 200, "steel_light")
    bolt.box(16, 30, -2, 6, 150, 160, "steel_light")
    bolt.box(28, 34, -4, 8, 148, 162, "steel_light")
    pso = body.bone("pso1", pivot=(0, 60, 40))
    pso.box(-22, -16, 0, 46, -20, 80, st)
    scope(pso, 30, 70, length=280, tube_d=28, obj_d=40, eye_d=34, mat="steel_dark", mount_y=30)
    pso.box(-20, 20, 54, 88, 160, 190, "rubber")
    mag = m["gun"].bone("magazine", pivot=(0, -46, 140))
    curved_mag(mag, -40, 110, 70, 150, curve=12, segs=3, width=24, mat="steel_dark", rib_mat="steel", round_d=11,
               round_len=70)
    add_arms(m, right_hand=(8, -96, -40), left_hand=(-12, -36, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -662), under=(0, -32, -300), eject=(18, 6, 170), sight=(0, 70, 186))
    m.meta["integral_optic"] = {"zoom": 4.0, "reticle": "pso1", "eye": [0, 70, 186]}
    cyc = dict(bone="bolt", travel=(0, 0, 110), t_back=0.022, t_fwd=0.062)
    anims = _rifle_anims(m, 6.0, (4.8, 0.6, 1.4), 16, "ak", cyc, ch="bolt", ch_travel=(0, 0, 110), selector=(0, 0, 0),
                         rock=10, rec=0.22, length=0.34, tilt=(4, -10, -30), tilt_pos=(-30, 14, 10), draw_len=0.8)
    return GunAsset(m, anims, {"hip": {"pos": [0.12, -0.15, -0.16], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.07}})


# =================================================================================================
# DSR-Precision DSR-1 (bullpup bolt action, .338 LM)
# =================================================================================================
def dsr1():
    m = new_gun("dsr1")
    body = m["body"]
    k, al = "polymer", "alloy_grey"
    body.box(-20, 20, -40, 20, -160, 300, al)                                  # aluminium chassis
    body.rail(-560, 290, 20, mat="alloy")                                      # full-length top rail
    body.box(0, 20.4, -2, 16, 120, 190, "rubber")                             # ejection port behind the grip
    body.box(-20, 20, -40, 16, -560, -160, al)                                 # fore-end tube shroud
    for z in range(-540, -180, 40):
        body.box(-20.4, 20.4, -24, 4, z, z + 22, "rubber")
    barrel(body, -560, -760, d=22)
    muzzle_brake(body, -760, d=30, length=66, ports=3)
    body.box(-16, 16, -60, -40, -560, -440, k)                                 # front grip block
    bipod(body, -500, y=-60, legs_len=200, folded=True)
    # spare-magazine holder ahead of the trigger guard (the DSR's signature)
    body.box(-17, 17, -150, -40, -160, -100, "steel_dark")
    body.box(-14, 14, -154, -150, -158, -102, "steel")
    pistol_grip(body, -60, top_y=-40, length=96, width=28, depth=36, angle=-14, mat=k)
    trigger_group(m, body, -94, y_top=-40, guard_depth=30, guard_len=70, guard_mat=al)
    # butt with adjustable cheek and pad
    body.box(-20, 20, -110, -40, 280, 330, k)
    body.box(-18, 18, -110, -90, 190, 290, k)                                  # monopod housing
    body.box(-6, 6, -150, -110, 240, 252, "steel_dark")
    body.box(-18, 18, 20, 40, 200, 300, k)                                     # cheek piece
    body.box(-22, 22, -116, 24, 326, 340, "rubber")
    _bolt(m, "gun", 80, 270, 250, mat="steel_light", d=22)                     # bolt sits behind the grip
    br = m["gun"].bone("brass", pivot=(0, 6, 140))
    br.cyl((0, 6, 150), 14, 70, "brass")
    mag = m["gun"].bone("magazine", pivot=(0, -40, 130))
    straight_mag(mag, -38, 100, 170, 80, width=28, mat="steel_dark", round_d=14, round_len=70)
    sc = body.bone("scope", pivot=(0, 60, 20))
    scope(sc, 20, 60, length=340, tube_d=34, obj_d=56, eye_d=44, mat="steel_dark", mount_y=24)
    add_arms(m, right_hand=(10, -100, -36), left_hand=(-14, -56, -460), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -826), eject=(20, 8, 150), sight=(0, 60, 210))
    m.meta["integral_optic"] = {"zoom": 12.0, "reticle": "mildot", "eye": [0, 60, 210]}
    anims = _bolt_anims(m, (8, 0.7, 1.6), 24, (0, 0, 100), (0, 0, 66), cyc_len=0.9, mag_out=50)
    return GunAsset(m, anims, {"hip": {"pos": [0.12, -0.15, -0.14], "rot": [0, 3, 0]}, "ads": {"dist": 0.07}})


GUNS = {"intervention": intervention, "l96": l96, "rem700": rem700, "svu": svu, "dsr1": dsr1}
