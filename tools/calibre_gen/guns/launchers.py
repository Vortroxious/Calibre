"""RPG-7 with PG-7V rocket."""
from ..core import Anim
from ..common import GunAsset, new_gun, add_arms, add_sockets, idle, draw, dry_fire
from ..templates import _settle, OFF_LEFT, OFF_LEFT_ROT
from ..parts import pistol_grip


def rpg7():
    # RPG-7: 950 mm launcher, wooden heat shield ahead of the flared venturi, PGO-7 sight, PG-7V rocket loaded
    m = new_gun("rpg7")
    body = m["body"]
    st = "steel_parked"
    body.cyl((0, 0, -30), 46, 660, st)                                            # launch tube
    body.cyl((0, 0, -352), 52, 16, st)                                            # muzzle ring
    body.box(-3, 3, 22, 26.4, -360.4, -350, "rubber")                             # rocket index notch
    body.cyl((0, 0, 345), 60, 190, "wood")                                        # heat shield
    for z in (258, 345, 432):
        body.cyl((0, 0, z), 62.5, 9, st)                                          # its clamps
    body.cyl((0, 0, 460), 46, 40, st)
    body.cyl((0, 0, 525), 46, 130, st, d2=88, steps=6)                            # venturi cone
    body.cyl((0, 0, 587), 92, 6, st)
    body.cyl((0, 0, 590.4), 78, 0.8, "rubber", sides=24)
    # trigger grip with the trigger and hammer, and the second grip behind it
    body.rbox(-8, 8, -62, -22, 24, 104, st, r=3)
    pistol_grip(body, 78, top_y=-60, length=70, width=24, depth=32, angle=-16, mat="wood")
    body.box(-3, 3, -84, -81, 30, 64, st)                                         # trigger guard
    body.box(-3, 3, -84, -60, 28, 32, st)
    trig = body.bone("trigger", pivot=(0, -60, 46))
    trig.box(-2.5, 2.5, -78, -60, 43, 48, st, rot=(8, 0, 0), pivot=(0, -60, 46))
    ham = body.bone("hammer", pivot=(0, -24, 110))
    ham.box(-4, 4, -32, -10, 102, 114, st)
    ham.rbox(-5, 5, -34, -28, 110, 124, st, r=1.5, axis="x")
    pistol_grip(body, 200, top_y=-22, length=92, width=22, depth=30, angle=-10, mat="wood")
    # folding iron sights + PGO-7 on its bracket
    body.box(-4, 4, 22, 26, -292, -270, st)
    body.box(-1.3, 1.3, 26, 52, -283, -279, st)
    body.box(-6, 6, 22, 26, 34, 58, st)
    for sx in (-1, 1):
        body.box(sx * 4.4 - 2.6, sx * 4.4 + 2.6, 26, 52.5, 44, 48, st)
    pgo = body.bone("pgo7", pivot=(-40, 30, 70))
    pgo.rbox(-34, -22, -8, 30, 40, 100, st, r=2)
    pgo.cyl((-46, 36, 70), 30, 110, "steel_dark")
    pgo.cyl((-46, 36, 4), 38, 24, "steel_dark")
    pgo.cyl((-46, 36, -8.4), 30, 0.8, "glass", sides=16)
    pgo.rbox(-56, -36, 36, 58, 110, 130, "steel_dark", r=4)                       # prism housing
    pgo.cyl((-46, 48, 152), 26, 44, "steel_dark")
    pgo.cyl((-46, 48, 184), 36, 20, "rubber")
    pgo.cyl((-46, 54, 70), 12, 10, "steel", axis="y", sides=8)                    # range knob
    for z in (-250, 150):
        body.box(-25.5, -22, -4, 4, z - 4, z + 4, st)                             # sling loops
    # rocket (PG-7V): booster in the tube, warhead cone, body, ogive and fuze
    r = m["gun"].bone("rocket", pivot=(0, 0, -360))
    r.cyl((0, 0, -340), 40, 40, "warhead")
    r.cyl((0, 0, -395), 85, 70, "rocket_green", d2=40, steps=5)
    r.cyl((0, 0, -475), 85, 90, "rocket_green")
    r.cyl((0, 0, -476), 86.5, 6, "warhead")
    r.cyl((0, 0, -610), 22, 180, "rocket_green", d2=85, steps=7)
    r.cyl((0, 0, -722), 14, 44, "warhead", d2=22, steps=2)
    r.cyl((0, 0, -747), 10, 6, "steel")
    add_arms(m, right_hand=(8, -118, 96), left_hand=(-10, -34, -60), right_rot=(34, 14, 6), left_rot=(30, -18, -4))
    add_sockets(m, muzzle=(0, 0, -362), eject=None, sight=(0, 52, 46))


    def fire(name, aim):
        a = Anim(m, name, 0.7)
        k = 0.6 if aim else 1.0
        a.hide("rocket")
        a.kick("gun", "rot", 0.0, (6 * k, 1.0, 2.0 * k), attack=0.04, recover=0.55)
        a.kick("gun", "pos", 0.0, (0, 10 * k, 30 * k), attack=0.04, recover=0.5)
        a.shake("gun", "pos", 0.0, 0.3, (2, 2, 2), freq=22, seed=7)
        a.key("trigger", 0.0, rot=(-14, 0, 0))
        a.key("trigger", 0.15, rot=(0, 0, 0))
        a.key("hammer", 0.0, rot=(-30, 0, 0))
        a.key("hammer", 0.7, rot=(-30, 0, 0))
        return a

    def reload():
        a = Anim(m, "reload", 3.4)
        a.mv("gun", 0.0, 0.5, pos=(-40, -60, -40), rot=(-14, 10, -30), e="inoutsine")  # bring the muzzle down/left
        a.mv("arm_left", 0.05, 0.4, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
        a.show("rocket", 0.42)
        a.key("rocket", 0.42, pos=(-80, -300, -100), rot=(40, 0, 40))
        a.grab("arm_left", "rocket", 0.45, 2.2, fade_in=0.05, fade_out=0.08)
        a.key("rocket", 1.2, pos=(0, -10, -230), rot=(4, 0, 30), e="outcubic")       # line it up with the bore
        a.key("rocket", 1.55, pos=(0, 0, -150), rot=(0, 0, 30), e="inoutsine")
        a.sound(1.6, "rocket_slide")
        a.key("rocket", 1.95, pos=(0, 0, 0), rot=(0, 0, 30), e="inoutsine")
        a.key("rocket", 2.15, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")           # twist to index the lug
        a.sound(2.15, "rocket_seat")
        a.event(2.15, "ammo")
        a.spring("gun", "rot", 2.15, (-1.6, 0, 1.2), freq=5, damp=8)
        a.mv("arm_left", 2.25, 2.7, pos=(0, 0, 0), rot=(0, 0, 0))
        # cock the hammer
        a.mv("arm_right", 2.4, 2.6, pos=(-2, 40, 20), rot=(-10, -6, 0))
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 2.6, rot=(0, 0, 0))
        a.key("hammer", 2.75, rot=(-30, 0, 0), e="outquad")
        a.sound(2.75, "hammer_cock")
        a.mv("arm_right", 2.8, 3.0, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 2.6, 3.35)
        return a

    anims = [idle(m), idle(m, "idle_empty", extra_hidden=("rocket",)), draw(m, 1.0, sound="draw_rifle"),
             fire("fire", False), fire("fire_aim", True), reload(), Anim(m, "inspect", 1.0), dry_fire(m)]
    return GunAsset(m, anims, {"hip": {"pos": [0.16, -0.1, -0.22], "rot": [0, 2, 0]}, "ads": {"dist": 0.1}})


GUNS = {"rpg7": rpg7}
