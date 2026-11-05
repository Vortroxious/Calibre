"""Remington 870 (pump) and Benelli M4 (semi-auto), both tube fed, loaded shell by shell."""
from ..core import Anim
from ..common import GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden
from ..templates import tube_reload, pump_cycle, _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import pistol_grip, trigger_group, barrel

SG_FP = {"hip": {"pos": [0.12, -0.13, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.13}}


def _shells(m, port=(0, -32, -30)):
    sl = m["gun"].bone("shell_load", pivot=port)
    sl.shell12((port[0], port[1] - 4, port[2] + 10))
    se = m["gun"].bone("shell_eject", pivot=(14, 6, -40))
    se.shell12((14, 6, -40))


def rem870():
    m = new_gun("rem870")
    body = m["body"]
    st = "steel"
    body.box(-17, 17, -30, 22, -110, 90, st)                                     # receiver
    body.box(0, 17.3, -8, 14, -80, -10, "rubber")                                # ejection port
    body.box(-12, 12, -32, -30, -100, -20, "rubber")                             # loading port
    barrel(body, -110, -610, d=22, y=4)
    body.cyl((0, -22, -330), 22, 440, st)                                         # magazine tube
    body.cyl((0, -22, -552), 26, 8, st)                                           # tube cap
    body.box(-10, 10, -14, -4, -560, -540, st)                                    # barrel ring
    body.box(-2, 2, 15, 19, -606, -602, "brass")                                 # bead
    body.box(-6, 6, 22, 26, -110, 80, st)                                        # receiver rib
    trigger_group(m, body, 10, y_top=-30, guard_depth=28, guard_len=64, guard_mat="alloy")
    sel = body.bone("selector", pivot=(0, -36, 40))
    sel.cyl((0, -36, 40), 8, 40, "steel_dark", axis="x")                         # crossbolt safety
    stock = m["gun"].bone("stock", pivot=(0, 0, 90))
    stock.taper(-18, 18, 90, 438, 18, -6, -46, -122, "wood")
    stock.box(-19, 19, -124, -4, 438, 450, "rubber")
    stock.box(-15, 15, -90, -46, 110, 170, "wood", rot=(-28, 0, 0), pivot=(0, -46, 110))
    pump = m["gun"].bone("pump", pivot=(0, -22, -280))
    pump.box(-22, 22, -42, -4, -390, -200, "wood")
    for z in range(-380, -210, 18):
        pump.box(-22.4, 22.4, -36, -12, z, z + 8, "wood_light")
    pump.box(-6, -3, -14, -6, -200, -60, st)                                     # action bars
    pump.box(3, 6, -14, -6, -200, -60, st)
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.8, -6, 12, -78, -20, "steel_light")
    _shells(m)
    add_arms(m, right_hand=(8, -84, 120), left_hand=(-10, -40, -300), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -612), optic=(0, 26, -20), under=None, eject=(17, 4, -50), sight=(0, 24, 80))

    def inspect():
        a = Anim(m, "inspect", 4.2)
        # half-rack: ease the pump back, peek at the shell in the chamber
        a.mv("gun", 0.0, 0.4, pos=(-30, 20, 30), rot=(4, -30, -36))
        a.grab("arm_left", "pump", 0.0, 1.6, fade_in=0.0, fade_out=0.06)
        a.key("pump", 0.0, pos=(0, 0, 0))
        a.key("pump", 0.4, pos=(0, 0, 0))
        a.key("pump", 0.7, pos=(0, 0, 32), e="inoutsine")
        a.sound(0.66, "pump_back_light")
        a.show("shell_eject", 0.6, 1.4)
        a.key("shell_eject", 0.6, pos=(0, 0, 0))
        a.key("shell_eject", 0.72, pos=(0, 0, 6))
        a.mv("gun", 0.7, 1.0, pos=(-40, 30, -10), rot=(10, -30, -50))
        a.key("pump", 1.3, pos=(0, 0, 32))
        a.key("pump", 1.45, pos=(0, 0, 0), e="inquad")
        a.key("shell_eject", 1.3, pos=(0, 0, 6))
        a.key("shell_eject", 1.4, pos=(0, 0, 0))
        a.sound(1.45, "pump_forward")
        a.spring("gun", "rot", 1.45, (1.4, 0, -1.4), freq=6, damp=8)
        # pump rattle - the loose forend jingles while you turn it over
        a.mv("gun", 1.6, 2.3, pos=(-60, 30, 30), rot=(10, 30, 20), e="inoutsine")
        a.shake("pump", "pos", 1.7, 2.6, (0, 0, 3.0), freq=9, seed=3)
        a.sound(1.8, "pump_rattle")
        a.sound(2.3, "pump_rattle")
        _settle(a, 2.9, 4.15)
        return a

    reload = tube_reload(m)
    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8, 0.8, 2.0), push=24, recover=0.32, length=0.4),
             fire_basic(m, "fire_aim", kick=(8, 0.8, 2.0), push=24, recover=0.28, length=0.36, aim=True),
             pump_cycle(m, "cycle"), pump_cycle(m, "cycle_aim", aim=True), *reload, inspect(), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, SG_FP)


def benelli_m4():
    m = new_gun("benelli_m4")
    body = m["body"]
    al = "alloy"
    body.box(-17, 17, -30, 24, -110, 90, al)
    body.rail(-100, 80, 24, mat=al)
    body.box(0, 17.3, -8, 14, -80, -10, "rubber")
    body.box(-12, 12, -32, -30, -100, -20, "rubber")
    barrel(body, -110, -560, d=22, y=4)
    body.cyl((0, -22, -300), 22, 380, al)
    body.box(-22, 22, -44, -4, -380, -130, "polymer")                            # forend (fixed)
    for z in range(-370, -140, 22):
        body.box(-22.4, 22.4, -38, -10, z, z + 10, "rubber")
    body.box(-10, 10, -14, 6, -470, -450, al)                                     # gas cylinder ring
    # ghost ring sights
    body.box(-8, 8, 24, 40, 60, 74, al)
    body.cyl((0, 36, 67), 14, 4, "steel_dark")
    body.box(-3, 3, 14, 30, -550, -540, al)
    body.box(-1, 1, 26, 30, -546, -544, "tritium")
    pistol_grip(body, 40, top_y=-30, length=96, width=30, depth=38, angle=-18, mat="polymer")
    trigger_group(m, body, 2, y_top=-30, guard_depth=28, guard_len=66, guard_mat="polymer")
    latch = body.bone("latch", pivot=(0, -32, -40))
    latch.box(-4, 4, -36, -30, -46, -36, "steel")                                # shell-latch / carrier release
    sel = body.bone("selector", pivot=(0, -36, 50))
    sel.cyl((0, -36, 50), 8, 40, "steel_dark", axis="x")
    stock = m["gun"].bone("stock", pivot=(0, 0, 90))
    stock.cyl((0, -4, 200), 30, 220, al)
    stock.taper(-20, 20, 220, 340, 14, 14, -62, -84, "polymer")
    stock.box(-14, 14, 14, 30, 230, 320, "polymer")
    stock.box(-22, 22, -90, 18, 336, 350, "rubber")
    bolt = body.bone("bolt", pivot=(16, 0, -60))
    bolt.box(2, 16.8, -6, 12, -78, -20, "steel_light")
    bolt.box(16, 30, 0, 8, -60, -50, "steel_light")
    bolt.cyl((34, 4, -55), 12, 10, "steel_light", axis="x")
    _shells(m)
    add_arms(m, right_hand=(8, -94, 68), left_hand=(-10, -44, -260), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -562), optic=(0, 27, -20), under=None, side=(-20, -20, -260), eject=(17, 4, -50),
                sight=(0, 40, 74))

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

    def inspect():
        a = Anim(m, "inspect", 4.0)
        # press the shell-latch button, roll to show the loading port
        a.mv("gun", 0.0, 0.5, pos=(-30, 30, 40), rot=(14, -10, -70), e="inoutsine")
        a.mv("arm_left", 0.2, 0.55, pos=(-6, -10, 250), rot=(10, -10, 30))
        a.key("latch", 0.0, pos=(0, 0, 0))
        a.key("latch", 0.6, pos=(0, 0, 0))
        a.key("latch", 0.66, pos=(0, 2.5, 0), e="outquad")
        a.sound(0.66, "click_small")
        a.key("latch", 1.0, pos=(0, 2.5, 0))
        a.key("latch", 1.05, pos=(0, 0, 0), e="outquad")
        a.sound(1.05, "click_small")
        a.mv("gun", 1.1, 1.8, pos=(-50, 40, 40), rot=(20, -40, -120), e="inoutsine")   # look into the port
        a.mv("arm_left", 1.1, 1.6, pos=(0, 0, 0), rot=(0, 0, 0))
        a.wave("gun", "rot", (0.6, 0.6, 0.4), 1.6)
        a.mv("gun", 2.2, 2.9, pos=(-40, 30, 30), rot=(6, 30, 20), e="inoutsine")
        _settle(a, 3.0, 3.95)
        return a

    reload = tube_reload(m)
    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(7, 0.8, 1.8), push=22,
                        cycle=dict(bone="bolt", travel=(0, 0, 70), t_back=0.025, t_fwd=0.07), recover=0.3, length=0.38),
             fire_basic(m, "fire_aim", kick=(7, 0.8, 1.8), push=22,
                        cycle=dict(bone="bolt", travel=(0, 0, 70), t_back=0.025, t_fwd=0.07), recover=0.26,
                        length=0.34, aim=True),
             cycle("cycle"), *reload, inspect(), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, SG_FP)


GUNS = {"rem870": rem870, "benelli_m4": benelli_m4}
