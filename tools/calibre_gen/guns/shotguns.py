"""Remington 870 (pump) and Benelli M4 (semi-auto), both tube fed, loaded shell by shell."""
from ..core import Anim
from ..common import GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden
from ..templates import tube_reload, pump_cycle, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import pistol_grip, trigger_group, barrel
from ..shotkit import sg_receiver, port_bolt, sg_barrel, sg_tube, forend, sg_butt, crossbolt
from ..common import moving
from ..pistolkit import control
from ..longkit import aperture_sight, eared_sight
from ..riflekit import butt_plate

SG_FP = {"hip": {"pos": [0.12, -0.13, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.13}}


def _shells(m, port=(0, -32, -30)):
    sl = m["gun"].bone("shell_load", pivot=port)
    sl.shell12((port[0], port[1] - 4, port[2] + 10))
    se = m["gun"].bone("shell_eject", pivot=(14, 6, -40))
    se.shell12((14, 6, -40))


def rem870():
    # Remington 870: 978 mm long, 470 mm barrel, steel receiver, walnut furniture
    m = new_gun("rem870")
    body = m["body"]
    st = "steel"
    roof = sg_receiver(body, -110, 90, st)
    body.box(-6, 6, 21.8, 22.5, -106, 86, "steel_dark")                          # matted top
    sg_barrel(body, -110, -612, d=22, y=4, mat=st)
    sg_tube(body, -110, -556, y=-22, d=22, mat=st, ring=-530)
    trigger_group(m, body, 10, y_top=-30, guard_depth=28, guard_len=64, guard_mat="alloy")
    crossbolt(body, 36, -42)
    body.box(-3, 3, -37, -30, -28, -20, st)                                      # action bar lock
    stock = m["gun"].bone("stock", pivot=(0, 0, 90))
    sg_butt(stock, "wood", 90, 366, checker="wood_red")
    pump = m["gun"].bone("pump", pivot=(0, -22, -280))
    forend(pump, -390, -200, "wood", grooves=9, groove_mat="wood_red")
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    port_bolt(bolt, (-80, -10), roof=roof)
    _shells(m)
    add_arms(m, right_hand=(8, -84, 120), left_hand=(-10, -40, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -613), optic=(0, 26, -20), under=None, eject=(17, 4, -50), sight=(0, 24, 80))


    reload = tube_reload(m)
    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8, 0.8, 2.0), push=24, recover=0.32, length=0.4),
             fire_basic(m, "fire_aim", kick=(8, 0.8, 2.0), push=24, recover=0.28, length=0.36, aim=True),
             pump_cycle(m, "cycle"), pump_cycle(m, "cycle_aim", aim=True), *reload, Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, SG_FP)


def benelli_m4():
    # Benelli M4 Super 90: 1010 mm long with the stock out, 470 mm barrel, ghost-ring sights, gas operated
    m = new_gun("benelli_m4")
    body = m["body"]
    al = "alloy"
    roof = sg_receiver(body, -110, 90, al, y1=24, port=(-92, 10))
    body.rail(-100, 80, 24, mat=al)
    sg_barrel(body, -110, -652, d=22, y=4, mat="steel_dark", bead=False)
    sg_tube(body, -110, -560, y=-22, d=22, mat=al, ring=-520)
    body.rbox(-22, 22, -44, 12, -420, -112, "polymer", r=10)                     # two-piece hand guard
    for z in range(-402, -140, 26):
        for sx in (-1, 1):
            body.box(sx * 22 - 0.35, sx * 22 + 0.35, -32, -4, z, z + 11, "rubber")
    body.box(-22.4, 22.4, -16, -14, -418, -114, "rubber")
    for sx in (-1, 1):
        body.cyl((sx * 9, -9, -450), 10, 44, al)                                 # twin gas pistons
    ys = aperture_sight(body, 66, 27, al, w=18, h=13, hole=6)                    # line of sight at 35.5
    body.rbox(-5, 5, 14, 24, -644, -626, al, r=2, edges="top")
    eared_sight(body, -635, 22, 15.7, al, w=14, depth=12, lean=4)
    pistol_grip(body, 40, top_y=-30, length=96, width=30, depth=38, angle=-18, mat="polymer")
    trigger_group(m, body, 2, y_top=-30, guard_depth=28, guard_len=66, guard_mat="polymer")
    latch = body.bone("latch", pivot=(0, -32, -40))
    latch.box(-4, 4, -36, -30, -46, -36, "steel")                                # shell-latch / carrier release
    crossbolt(body, 30, -42)
    body.cyl((17.3, -14, 30), 9, 1.2, "steel", axis="x", sides=8)                # bolt release button
    stock = m["gun"].bone("stock", pivot=(0, 0, 90))
    stock.cyl((0, -4, 162), 30, 146, al)                                         # recoil tube
    for z in (120, 150, 180):
        stock.box(-2, 2, -21, -18, z - 5, z + 5, "rubber")                       # position notches
    stock.profile(-19, 19, [(226, 16), (343, 16)], [(226, -30), (343, -90)], "polymer")
    stock.rbox(-14, 14, 16, 28, 236, 330, "polymer", r=5, edges="top")           # cheek piece
    butt_plate(stock, 343, -90, 16, 19, "polymer", th=3, pad="rubber", pad_th=12)
    bolt = body.bone("bolt", pivot=(16, 0, -60))
    port_bolt(bolt, (-92, -22), roof=roof)
    bolt.box(16, 30, 0, 8, -72, -62, "steel_light")
    bolt.cyl((34, 4, -67), 12, 10, "steel_light", axis="x", sides=16)
    _shells(m)
    add_arms(m, right_hand=(8, -94, 68), left_hand=(-10, -44, -260), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -653), optic=(0, 27, -20), under=None, side=(-20, -20, -260), eject=(17, 4, -50),
                sight=(0, 35.5, 66))


    def cycle(name):
        """Shell into the ejection port + bolt release (used after an empty reload)."""
        a = Anim(m, name, 0.9)
        a.mv("gun", 0.0, 0.2, pos=(-20, 16, 20), rot=(2, -14, -38))
        a.mv("arm_right", 0.0, 0.2, pos=(30, 50, -110), rot=(-30, -20, -30))
        a.grab("arm_right", "bolt", 0.2, 0.55, fade_in=0.02, fade_out=0.06)
        a.key("bolt", 0.0, pos=(0, 0, 0))
        a.key("bolt", 0.22, pos=(0, 0, 0))
        a.key("bolt", 0.36, pos=(0, 0, 70), e="inoutquad")
        a.sound(0.34, "charging_handle_back")
        a.key("bolt", 0.44, pos=(0, 0, 0), e="inquad")
        a.sound(0.44, "bolt_release")
        a.spring("gun", "rot", 0.44, (1.6, 0, -1.6), freq=6, damp=8)
        a.mv("arm_right", 0.56, 0.8, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 0.5, 0.88, pos=(0, 0, 0), rot=(0, 0, 0))
        return a

    reload = tube_reload(m)
    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(7, 0.8, 1.8), push=22,
                        cycle=dict(bone="bolt", travel=(0, 0, 70), t_back=0.025, t_fwd=0.07), recover=0.3, length=0.38),
             fire_basic(m, "fire_aim", kick=(7, 0.8, 1.8), push=22,
                        cycle=dict(bone="bolt", travel=(0, 0, 70), t_back=0.025, t_fwd=0.07), recover=0.26,
                        length=0.34, aim=True),
             cycle("cycle"), *reload, Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, SG_FP)


GUNS = {"rem870": rem870, "benelli_m4": benelli_m4}
