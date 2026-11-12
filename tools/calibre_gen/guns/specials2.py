"""Expansion 3 specials: Ingram MAC-10, VSS Vintorez (integral suppressor, PSO-1), Kel-Tec KSG (twin magazine
tubes, bullpup pump) and a side-by-side double-barrel shotgun (break action)."""
import numpy as np

from ..core import Anim
from ..common import GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden, moving
from ..templates import tube_reload, pump_cycle, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import (pistol_grip, trigger_group, barrel, straight_mag, curved_mag, pins, vents, sling_swivel,
                     side_swivel, ejection_port, scope)
from ..longkit import slot, peep, eared_sight, ring_sight, tangent_sight, flip_sight, stock_solid
from ..pistolkit import control
from ..riflekit import butt_plate, stock as _stock
from ..shotkit import forend, crossbolt
from .modern import _rifle_anims, _fp
from .aks import _anims as _ak_anims
from .shotguns import _shells, SG_FP
from .ar15 import _buis, _flip_front


# =================================================================================================
# Ingram MAC-10  (548 mm with the stock out, 146 mm barrel, magazine through the grip)
# =================================================================================================
def mac10():
    m = new_gun("mac10")
    body = m["body"]
    st = "steel_dark"
    body.rbox(-22, 22, -30, 24, -132, 84, st, r=3)                                     # stamped box receiver
    body.box(-22.4, 22.4, -6, -3, -128, 80, "rubber")                                  # upper / lower seam
    pins(body, 22, [(-16, -120), (-16, 74), (10, 74)], d=5, mat="steel")
    barrel(body, -132, -170, d=17, mat="steel")
    body.cyl((0, 0, -150), 22, 22, "steel")                                            # thread protector / nut
    for k in range(8):
        body.box(-11.4, 11.4, -1, 1, -160, -140, "steel_dark", rot=(0, 0, k * 22.5), pivot=(0, 0, -150))
    body.path([(-132, -24), (-150, -46), (-120, -52)], 8, 5, "canvas")                 # the strap loop at the front
    body.rbox(-5, 5, 24, 32, -126, -112, st, r=2, edges="top")                         # front post in its ears
    eared_sight(body, -119, 30, 10, st, w=14, depth=10, lean=4)
    body.rbox(-10, 10, 24, 30, 60, 84, st, r=2, edges="top")
    peep(body, 74, 30, 46, st, w=14, hole=5, depth=3, hole_y=38)
    slot(body, 0.0, 24, 24.6, -110, 40)                                                # cocking slot on top
    body.box(-3, 3, 23.8, 24.5, -110, 40, "rubber")
    # the grip is the magazine well, straight down under the receiver's middle
    body.rbox(-17, 17, -128, -30, -64, -16, "polymer", r=6, axis="y")
    for i in range(6):
        body.box(-17.3, 17.3, -120 + i * 14, -114 + i * 14, -60, -20, "rubber")
    guard = body.path([(-120, -30), (-124, -66), (-112, -76), (-70, -76), (-64, -30)], 6, 5, st)
    trig = body.bone("trigger", pivot=(0, -32, -86))
    trig.box(-2.5, 2.5, -56, -32, -90, -84, st)
    control(body, "selector", (-22, -12, -100), [(-25, -22, -16, -8, -110, -94, "steel")], turn=(-40, 0, 0))
    control(body, "mag_release", (0, -128, -14), [(-6, 6, -132, -124, -16, -10, "steel")], press=(0, 0, 2))
    bolt = body.bone("bolt", pivot=(0, 0, 0))                                          # bolt with the top knob
    bolt.box(-10, 10, -10, 10, -100, -10, "steel_light")
    bolt.cyl((0, 30, -100), 13, 10, "steel", axis="y", sides=16)
    bolt.box(-2, 2, 22, 26, -102, -98, "steel")
    stock = m["gun"].bone("stock", pivot=(0, 0, 84))                                   # telescoping wire stock, out
    for sx in (-1, 1):
        stock.cyl((sx * 14, -14, 222), 7, 284, "steel")
    stock.rbox(-20, 20, -84, -4, 360, 370, st, r=3)
    stock.box(-6, 6, -84, -20, 370, 376, "rubber")
    stock.rbox(-18, 18, -20, -6, 84, 96, st, r=2)
    mag = m["gun"].bone("magazine", pivot=(0, -128, -40))
    straight_mag(mag, -30, -60, -20, 230, width=26, mat="steel_dark", round_d=11, round_len=29)
    add_arms(m, right_hand=(8, -84, -40), left_hand=(-12, -30, -150), right_rot=(34, 18, 6), left_rot=(30, -14, -4))
    add_sockets(m, muzzle=(0, 0, -172), eject=(22, 4, -60), sight=(0, 38, 74))
    cyc = dict(bone="bolt", travel=(0, 0, 64), t_back=0.016, t_fwd=0.045)
    anims = _rifle_anims(m, 0.0, (1.8, 0.5, 1.2), 8, "smg", cyc, ch="bolt", ch_travel=(0, 0, 64), mag_sound="smg",
                         selector=(-40, 0, 0), rec=0.09, length=0.15, draw_len=0.55)
    return GunAsset(m, anims, _fp(pos=(0.11, -0.11, -0.24), ads=0.26))


# =================================================================================================
# VSS Vintorez  (894 mm long, 200 mm barrel inside the integral suppressor, skeleton stock, PSO-1)
# =================================================================================================
def vss():
    m = new_gun("vss")
    body = m["body"]
    st, wd = "steel_dark", "wood"
    zf = -110.0
    body.rbox(-15, 15, -30, 10, zf, 140, st, r=2.5, edges="bottom")                   # receiver
    body.rbox(-14, 14, 10, 22, zf + 4, 138, st, r=6, edges="top")                      # cover
    body.box(8, 15.4, 1, 9, -76, 18, "rubber")                                         # ejection opening
    body.box(8, 14.5, 9, 16, -76, 18, "rubber")
    pins(body, 15, [(-4, -100), (-22, -100), (-14, 10), (0, 130)], d=4.5, mat="steel")
    body.box(-17, -15, -18, 14, -90, 80, st)                                           # side rail for the scope
    # integral suppressor: the long can over the barrel, with its hand guard behind the front half
    body.cyl((0, 0, -290), 40, 360, st)                                                # -110 .. -470
    body.cyl((0, 0, -471), 38, 4, st)
    body.cyl((0, 0, -473.4), 12, 0.6, "rubber", sides=8)
    for z in (-460, -300, -180):
        body.cyl((0, 0, z), 41.4, 3, "steel")
    body.rbox(-21, 21, -26, 22, -290, zf, wd, r=10)                                    # wooden hand guard
    vents(body, 21, -16, 8, -280, -120, n=6, fill=0.55)
    body.rbox(-6, 6, 20, 30, -462, -444, st, r=2, edges="top")                         # front sight on the can
    eared_sight(body, -453, 28, 12, st, w=12, depth=10, lean=4)
    tangent_sight(body, -110, -60, 22, st, w=10, h=13)                                 # notch top at 35
    control(body, "mag_release", (0, -32, -34), [(-5, 5, -56, -30, -40, -35, st), (-6, 6, -58, -52, -41, -30, st)],
            turn=(22, 0, 0))
    trigger_group(m, body, 6, y_top=-30, guard_depth=30, guard_len=74, guard_mat=st)
    sel = body.bone("selector", pivot=(16, 2, 64))
    sel.cyl((17, 2, 64), 12, 2.4, "steel", axis="x", sides=16)
    sel.box(16, 18, -3, 6, -34, 64, "steel")
    sel.box(18, 23, -7, 1, -36, -22, "steel")
    bolt = body.bone("bolt", pivot=(18, 6, -50))
    bolt.box(8.4, 15.6, 2.4, 18.6, -74, 16, "steel_light")
    bolt.box(15, 30, 4, 12, -56, -44, "steel_light")
    bolt.cyl((30, 8, -50), 12, 8, "steel_light", axis="x", sides=16)
    # skeleton thumbhole stock, wood
    stock = m["gun"].bone("stock", pivot=(0, 0, 140))
    _stock(stock, [(140, 10), (190, 10), (300, 6), (418, -4)], [(140, -16), (300, -18), (418, -20)], [(140, 418, 15)],
           wd)
    _stock(stock, [(176, -36), (220, -60), (418, -78)], [(150, -84), (220, -110), (418, -112)], [(150, 418, 15)], wd)
    stock.profile(-15, 15, [(140, -16), (176, -36)], [(140, -30), (150, -84)], wd)        # grip under the receiver
    stock.rbox(-16, 16, -114, 10, 412, 420, "rubber", r=4)
    # PSO-1 on its side bracket
    pso = body.bone("pso1", pivot=(0, 64, 20))
    pso.rbox(-22, -15, -10, 44, -30, 70, st, r=2.4, edges="top")
    pso.box(-22, -6, 40, 50, -10, 60, st)
    pso.cyl((-24, 10, 20), 10, 5, "steel", axis="x", sides=16)
    scope(pso, 20, 64, length=260, tube_d=28, obj_d=38, eye_d=34, mat="steel_dark", mount_y=None, turrets=False)
    pso.cyl((0, 64, -120), 40, 26, st)                                                 # sunshade
    for axis, c in (("y", (0, 64 + 22, 16)), ("x", (22, 64, 16))):
        pso.cyl(c, 24, 16, st, axis=axis)
    pso.rbox(-9, 9, 44, 54, -6, 40, st, r=2.4, edges="bottom")
    pso.cyl((0, 64, 158), 40, 26, "rubber", d2=46, steps=4)                            # eyecup
    pso.cyl((0, 64, 174), 46, 8, "rubber")
    mg = m["gun"].bone("magazine", pivot=(0, -40, -70))                                # 10-round 9x39 box
    curved_mag(mg, -26, -104, 64, 120, curve=10, segs=3, width=26, mat="steel_dark", rib_mat="steel", round_d=10,
               round_len=56)
    add_arms(m, right_hand=(8, -84, 62), left_hand=(-12, -52, -200), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -474), optic=None, under=None, eject=(16, 8, -30), sight=(0, 64, 180))
    m.meta["integral_optic"] = {"zoom": 4.0, "reticle": "pso1", "eye": [0, 64, 180]}
    anims = _ak_anims(m, 4.0, (2.2, 0.4, 1.0), 9, travel=(0, 0, 100), rock=10, rec=0.13, length=0.21)
    return GunAsset(m, anims, {"hip": {"pos": [0.118, -0.135, -0.18], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.07}})


# =================================================================================================
# Kel-Tec KSG  (663 mm long, 470 mm barrel, bullpup pump with two magazine tubes under the barrel)
# =================================================================================================
def ksg():
    m = new_gun("ksg")
    body = m["body"]
    p, st = "polymer", "steel_dark"
    body.rbox(-22, 22, -60, 22, -150, 218, p, r=9)                                     # shell
    body.profile(-22, 22, [(140, -60), (218, -60)], [(140, -62), (218, -104)], p)
    body.rbox(-23, 23, -108, 26, 218, 230, "rubber", r=8)
    body.box(-22.4, 22.4, -24, -22, -146, 214, "rubber")                               # moulded seam
    pins(body, 22, [(-40, -130), (-40, 120), (4, 200)], d=5, mat="steel")
    body.rail(-150, 200, 22, mat="alloy")                                              # full-length top rail
    body.box(-14, 14, -62, -60, 120, 196, "rubber")                                    # loading ports underneath
    body.box(-12, 12, -62, -60, 40, 110, "rubber")                                     # ejection port, also below
    sg_y = 2.0
    barrel(body, -150, -433, d=21, mat=st, y=sg_y)
    for sx in (-1, 1):                                                                 # twin magazine tubes
        body.cyl((sx * 13, -34, -280), 24, 260, st)
        body.cyl((sx * 13, -34, -414), 26, 10, st)
    body.rbox(-30, 30, -48, 10, -420, -400, st, r=4)                                   # front cap
    pistol_grip(body, -20, top_y=-60, length=90, width=28, depth=36, angle=-12, mat=p)
    trigger_group(m, body, -56, y_top=-60, guard_depth=26, guard_len=60, guard_mat=p)
    crossbolt(body, -30, -72, hw=14, d=7)
    sel = body.bone("selector", pivot=(0, -62, 116))                                   # tube selector lever
    sel.box(-16, 16, -66, -62, 112, 120, "steel")
    moving(m, "selector", pos=(10, 0, 0))
    rel = body.bone("latch", pivot=(0, -62, -10))                                      # pump release
    rel.box(-4, 4, -66, -60, -16, -4, st)
    pump = m["gun"].bone("pump", pivot=(0, -34, -300))
    forend(pump, -360, -230, p, hw=34, y0=-60, y1=-8, grooves=6, groove_mat="polymer_grey", bars_to=-150, bar_y=-14)
    pump.rbox(-14, 14, -150, -60, -320, -280, p, r=6, axis="y")                         # vertical fore grip
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-10, 10, -54, -40, 40, 110, "steel_light")
    _shells(m, port=(0, -60, 160))
    add_arms(m, right_hand=(8, -110, -24), left_hand=(-10, -100, -300), right_rot=(34, 14, 6), left_rot=(30, -14, -4))
    add_sockets(m, muzzle=(0, sg_y, -434), optic=(0, 25, 0), under=None, eject=(0, -62, 80), sight=(0, 40, 160))
    _buis(body, 180, 25, p, sy=40)
    _flip_front(body, -136, 25, p, sy=40)
    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8, 0.8, 2.0), push=24, recover=0.32, length=0.4),
             fire_basic(m, "fire_aim", kick=(8, 0.8, 2.0), push=24, recover=0.28, length=0.36, aim=True),
             pump_cycle(m, "cycle", travel=(0, 0, 90)), pump_cycle(m, "cycle_aim", travel=(0, 0, 90), aim=True),
             *tube_reload(m, port_tilt=(-10, 8, -40), port_pos=(-20, 40, 30)),
             Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, {"hip": SG_FP["hip"], "ads": {"dist": 0.16}})


# =================================================================================================
# Side-by-side double-barrel shotgun  (1143 mm long, 711 mm barrels, break action, double triggers)
# =================================================================================================
def doublebarrel():
    m = new_gun("doublebarrel")
    body = m["body"]
    st, wd = "steel_dark", "wood"
    HZ, HY = -36.0, -14.0                                                              # hinge pin
    body.rbox(-20, 20, -30, 12, -36, 64, "steel_parked", r=6, edges="top")             # action body
    body.box(-20.4, 20.4, -24, -10, -30, 50, "steel")                                  # engraved side panels
    for sx in (-1, 1):
        body.cyl((sx * 20.3, -18, 10), 9, 0.8, "steel_light", axis="x", sides=16)
    body.cyl((0, HY, HZ), 10, 42, "steel", axis="x", sides=16)                         # hinge pin
    lever = body.bone("top_lever", pivot=(0, 14, 66))                                  # top lever
    lever.rbox(-4, 4, 12, 16, 50, 92, "steel_parked", r=1.5)
    lever.rbox(-4, 18, 12, 16, 84, 96, "steel_parked", r=1.5)
    moving(m, "top_lever", rot=(0, -40, 0))
    sf = body.bone("safety", pivot=(0, 15, 100))                                       # tang safety
    sf.box(-3, 3, 14, 17, 96, 106, "steel")
    moving(m, "safety", pos=(0, 0, -5))
    # the barrels, rib, fore-end and extractor drop together on the hinge
    br = body.bone("barrels", pivot=(0, HY, HZ))
    for sx in (-1, 1):
        br.cyl((sx * 10, 0, -390), 22, 708, st, d2=19, steps=4)
        br.cyl((sx * 10, 0, -744.3), 15, 0.6, st)
        br.cyl((sx * 10, 0, -744.8), 17, 0.6, "rubber", sides=8)
    br.box(-3, 3, 9, 13, -742, -40, st)                                                # sighting rib
    br.box(-1.6, 1.6, 13, 16, -738, -734, "brass")                                     # bead
    br.box(-4, 4, -12, -6, -742, -40, st)                                              # lower rib
    br.rbox(-21, 21, -26, -6, -40, -36, st, r=3)                                       # lumps
    br.box(-12, 12, -24, -8, -50, -30, st)
    fe = br.bone("forend", pivot=(0, -14, -100))
    fe.rbox(-21, 21, -30, -6, -260, -50, wd, r=8, edges="bottom")                      # splinter fore-end
    fe.box(-6, 6, -31, -28, -70, -56, "steel")                                         # its latch
    ex = br.bone("extractor", pivot=(0, 0, -36))
    ex.box(-18, 18, -6, 6, -40, -36, "steel_light")
    moving(m, "extractor", pos=(0, 0, 10))
    # stock, grip, double triggers
    sg = body.bone("stock_b", pivot=(0, 0, 64))
    _stock(sg, [(64, 12), (120, 0), (220, -14), (400, -30)], [(64, -30), (110, -48), (160, -54), (400, -122)],
           [(64, 160, 14.5), (160, 400, 17)], wd)
    for sx in (-1, 1):                                                                 # chequering
        sg.box(sx * 14.5 - 0.3, sx * 14.5 + 0.3, -40, -14, 90, 140, "wood_red")
    butt_plate(sg, 400, -122, -30, 17, "rubber", th=3)
    guard_pts = [(-24, -30), (-28, -52), (0, -58), (40, -52), (54, -40)]
    body.path(guard_pts, 7, 3.6, "steel_parked")
    t1 = body.bone("trigger", pivot=(0, -30, 4))
    t1.box(-2.5, 2.5, -48, -30, 1, 6, "steel", rot=(8, 0, 0), pivot=(0, -30, 4))
    t2 = body.bone("trigger_rear", pivot=(0, -30, 22))
    t2.box(-2.5, 2.5, -46, -30, 19, 24, "steel", rot=(14, 0, 0), pivot=(0, -30, 22))
    sling_swivel(sg, 0, -110, 340, along="x", w=16, drop=9, mat="steel")
    # shells: two fired cases in the chambers that come out, two fresh ones from the hand
    se = br.bone("shell_eject", pivot=(0, 0, -36))
    sl = br.bone("shell_load", pivot=(0, 0, -36))
    for sx in (-1, 1):
        se.shell12((sx * 10, 0, -70))
        sl.shell12((sx * 10, 0, -70))
    add_arms(m, right_hand=(8, -80, 130), left_hand=(-10, -36, -160), right_rot=(32, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -745), eject=(0, 6, -40), sight=(0, 16, 60))

    OPEN = (-34, 0, 0)

    def reload(name, both):
        L = 2.5
        a = Anim(m, name, L)
        a.mv("gun", 0.0, 0.3, pos=(-20, 30, 40), rot=(14, -6, -30))
        a.mv("arm_right", 0.05, 0.2, pos=(-2, 8, -12), rot=(-4, -6, 4))
        a.key("top_lever", 0.12, rot=(0, 0, 0))
        a.key("top_lever", 0.22, rot=(0, -40, 0), e="outquad")
        a.sound(0.2, "lever_open")
        a.key("barrels", 0.22, rot=(0, 0, 0))
        a.key("barrels", 0.4, rot=OPEN, e="outback")
        a.sound(0.36, "bolt_open")
        a.key("top_lever", 0.5, rot=(0, -40, 0))
        a.key("top_lever", 0.6, rot=(0, 0, 0), e="outquad")
        a.mv("arm_right", 0.5, 0.65, pos=(0, 0, 0), rot=(0, 0, 0))
        # the extractors lift the empties and they fly out over the shoulder
        a.key("extractor", 0.38, pos=(0, 0, 0))
        a.key("extractor", 0.46, pos=(0, 0, 10), e="outquad")
        a.key("extractor", 1.6, pos=(0, 0, 10))
        a.key("extractor", 1.66, pos=(0, 0, 0))
        a.show("shell_eject", 0.0, 0.85)
        a.key("shell_eject", 0.42, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("shell_eject", 0.5, pos=(0, 8, 30), rot=(-20, 0, 0), e="outquad")
        a.key("shell_eject", 0.85, pos=(40, 160, 260), rot=(-200, 30, 0), e="inquad")
        a.sound(0.5, "click_small")
        # two fresh shells, both thumbed in together
        a.mv("arm_left", 0.3, 0.6, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
        a.show("shell_load", 0.8, L)
        a.key("shell_load", 0.8, pos=(-60, -60, 140), rot=(30, 0, 30))
        a.grab("arm_left", "shell_load", 0.82, 1.5, fade_in=0.12, fade_out=0.06)
        a.key("shell_load", 1.18, pos=(0, 6, 46), rot=(4, 0, 0), e="outcubic")
        a.key("shell_load", 1.36, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
        a.sound(1.3, "shell_insert")
        a.sound(1.36, "shell_insert")
        a.event(1.36, "ammo")
        a.mv("arm_left", 1.5, 1.85, pos=(0, 0, 0), rot=(0, 0, 0))
        # snap the barrels shut with a flick of the wrist
        a.key("barrels", 1.6, rot=OPEN)
        a.key("barrels", 1.74, rot=(0, 0, 0), e="inquad")
        a.sound(1.73, "bolt_close")
        a.spring("gun", "rot", 1.74, (-3.0, 0, 1.2), freq=6, damp=8)
        a.mv("gun", 1.62, 1.78, pos=(-10, 20, 30), rot=(-4, -4, -16), e="inquad")
        _settle(a, 1.8, L - 0.02)
        return a

    k = dict(kick=(10, 1.0, 2.2), push=28)
    anims = [idle(m), draw(m, 0.8, sound="draw_rifle"),
             fire_basic(m, "fire", recover=0.34, length=0.42, **k),
             fire_basic(m, "fire_aim", recover=0.3, length=0.38, aim=True, **k),
             reload("reload", False), reload("reload_empty", True), Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, {"hip": SG_FP["hip"], "ads": {"dist": 0.3}})


GUNS = {"mac10": mac10, "vss": vss, "ksg": ksg, "doublebarrel": doublebarrel}
