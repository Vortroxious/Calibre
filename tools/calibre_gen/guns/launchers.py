"""RPG-7 with PG-7V rocket."""
from ..core import Anim
from ..common import GunAsset, new_gun, add_arms, add_sockets, idle, draw, dry_fire
from ..templates import _settle, OFF_LEFT, OFF_LEFT_ROT


def rpg7():
    m = new_gun("rpg7")
    body = m["body"]
    st = "steel_parked"
    body.cyl((0, 0, 60), 42, 760, st, sides=12)                                   # launch tube
    body.cyl((0, 0, -90), 58, 230, "wood", sides=12)                              # heat shield
    body.cyl((0, 0, 470), 52, 30, st, sides=12)                                   # venturi
    body.cyl((0, 0, 520), 70, 70, st, sides=12)
    body.cyl((0, 0, 556), 62, 2, "rubber", sides=12)
    body.cyl((0, 0, -320), 48, 10, st, sides=12)                                  # muzzle ring
    # grips
    body.box(-12, 12, -130, -24, -40, -4, "wood", rot=(-12, 0, 0), pivot=(0, -24, -22))
    body.box(-12, 12, -120, -24, 60, 96, "polymer", rot=(-18, 0, 0), pivot=(0, -24, 78))
    body.box(-6, 6, -60, -24, 30, 60, st)                                          # trigger housing
    trig = body.bone("trigger", pivot=(0, -40, 46))
    trig.box(-3, 3, -58, -40, 42, 48, st)
    ham = body.bone("hammer", pivot=(0, -24, 110))
    ham.box(-4, 4, -30, -10, 100, 116, st)
    # iron sights (folding) + PGO-7 bracket on the left
    body.box(-4, 4, 22, 52, -160, -152, st)
    body.box(-4, 4, 22, 46, 40, 48, st)
    pgo = body.bone("pgo7", pivot=(-40, 30, 70))
    pgo.box(-36, -22, -10, 30, 40, 100, st)
    pgo.cyl((-46, 34, 70), 28, 150, "steel_dark", sides=12)
    pgo.box(-58, -34, 22, 46, 140, 160, "rubber")
    # rocket (PG-7V): warhead cone + ogive + booster stub
    r = m["gun"].bone("rocket", pivot=(0, 0, -330))
    r.cyl((0, 0, -360), 84, 70, "rocket_green", sides=12)
    r.cyl((0, 0, -430), 70, 70, "rocket_green", sides=12)
    r.cyl((0, 0, -490), 46, 50, "rocket_green", sides=12)
    r.cyl((0, 0, -530), 24, 40, "warhead", sides=12)
    r.cyl((0, 0, -552), 12, 12, "steel")                                           # fuze
    r.cyl((0, 0, -320), 40, 20, "warhead")
    add_arms(m, right_hand=(8, -104, 96), left_hand=(-10, -96, -2), right_rot=(34, 14, 6), left_rot=(30, -18, -4))
    add_sockets(m, muzzle=(0, 0, -330), eject=None, sight=(0, 46, 44))

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

    def inspect():
        a = Anim(m, "inspect", 4.2)
        # shoulder the tube and look down the sights, then look over the warhead
        a.mv("gun", 0.0, 0.7, pos=(-120, 60, 120), rot=(4, 6, 0), e="inoutsine")
        a.wave("gun", "rot", (0.4, 0.4, 0.2), 1.5)
        a.mv("gun", 1.5, 2.1, pos=(-60, 30, 60), rot=(10, 40, 20), e="inoutsine")
        a.mv("arm_left", 1.6, 2.0, pos=(20, 60, -280), rot=(-30, 20, 30))
        a.sound(2.1, "tap")
        a.mv("arm_left", 2.4, 2.9, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 2.9, 4.15)
        return a

    anims = [idle(m), idle(m, "idle_empty", extra_hidden=("rocket",)), draw(m, 1.0, sound="draw_rifle"),
             fire("fire", False), fire("fire_aim", True), reload(), inspect(), dry_fire(m)]
    return GunAsset(m, anims, {"hip": {"pos": [0.16, -0.1, -0.22], "rot": [0, 2, 0]}, "ads": {"dist": 0.1}})


GUNS = {"rpg7": rpg7}
