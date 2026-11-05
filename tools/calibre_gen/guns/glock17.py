"""Glock 17 Gen 4 - 9x19mm, 17 rounds, striker fired."""
from ..core import Anim
from ..common import GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden, along
from ..templates import pistol_reload

NAME = "glock17"
MAG_ANGLE = -18.0
SLIDE_TRAVEL = (0, 0, 42)


def model():
    m = new_gun(NAME)
    body = m["body"]
    # ---- frame (polymer) ----
    body.box(-11.5, 11.5, -26, -10, -146, -30, "polymer")                    # dust cover
    body.box(-10, 10, -31, -26, -142, -96, "polymer")                        # accessory rail
    for z in (-136, -124, -112):
        body.box(-10.5, 10.5, -32, -30, z, z + 4, "polymer")
    body.box(-11.5, 11.5, -26, -10, -30, 30, "polymer")                      # frame top
    body.box(-12, 12, -26, -12, 22, 40, "polymer")                           # beavertail
    body.box(-11, 11, -26, -10, -30, -24, "polymer")
    # trigger guard (square front)
    body.box(-5, 5, -58, -26, -50, -43, "polymer")
    body.box(-5, 5, -58, -52, -50, -6, "polymer")
    body.box(-5, 5, -52, -40, -10, -4, "polymer")
    # grip (tilted 18 deg), with texture panels and mag well flare
    gp = (0, -18, 14)
    body.box(-14.5, 14.5, -128, -18, -12, 40, "polymer", rot=(-18, 0, 0), pivot=gp)
    body.box(-15, 15, -112, -48, -10, 38, "polymer", rot=(-18, 0, 0), pivot=gp, inflate=0.0)
    body.box(-4, 4, -122, -24, 40, 44, "polymer", rot=(-18, 0, 0), pivot=gp)  # backstrap
    body.box(-15.5, 15.5, -128, -122, -14, 42, "polymer", rot=(-18, 0, 0), pivot=gp)  # flare
    # slide stop lever + takedown lever
    body.box(-13.5, -11.5, -18, -12, -18, -2, "steel_dark")
    body.box(11.5, 12.5, -24, -18, -40, -30, "steel_dark")
    body.box(-12.5, -11.5, -24, -18, -40, -30, "steel_dark")
    # mag release
    body.box(-14, -11.5, -42, -34, -10, -2, "polymer")
    # ---- barrel (static; visible at the muzzle and through the ejection port) ----
    barrel = body.bone("barrel", pivot=(0, 0, 0))
    barrel.cyl((0, 0, -100), 13, 104, "steel_light")
    barrel.box(-7, 7, 4, 14, -24, 8, "steel_light")                          # hood
    # ---- slide ----
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-12.7, 12.7, -10, 15, -150, 36, "steel_dark")
    slide.box(-11, 11, 15, 17.5, -148, 34, "steel_dark")                     # top flat
    slide.box(-12.7, -9.5, -10, 15, -150, -135, "steel_dark", )
    slide.box(9.5, 12.7, -10, 15, -150, -135, "steel_dark")
    # muzzle face (hollow look)
    slide.box(-7.5, 7.5, -7.5, 7.5, -151, -150, "rubber")
    # ejection port (dark cut on top right) -- barrel hood shows through
    slide.box(0, 12.9, 10, 17.6, -24, 10, "rubber")
    slide.box(1, 9, 13, 17.7, -22, 8, "steel_light")
    # rear serrations
    for i in range(7):
        z = 6 + i * 4.2
        slide.box(-12.9, -12.7, -6, 13, z, z + 1.8, "steel")
        slide.box(12.7, 12.9, -6, 13, z, z + 1.8, "steel")
    # extractor
    slide.box(12.7, 13.4, 5, 9, -18, 4, "steel")
    # sights
    slide.box(-1.8, 1.8, 17.5, 23, -142, -136, "steel_dark")
    slide.box(-1, 1, 21, 22.5, -136.2, -135.8, "sight_white")
    slide.box(-8, -2, 17.5, 23.5, 22, 30, "steel_dark")
    slide.box(2, 8, 17.5, 23.5, 22, 30, "steel_dark")
    slide.box(-8, 8, 17.5, 19.5, 22, 30, "steel_dark")
    slide.box(-6.5, -3, 20, 21.5, 30, 30.3, "sight_white")
    slide.box(3, 6.5, 20, 21.5, 30, 30.3, "sight_white")
    # striker cover plate
    slide.box(-6, 6, -6, 10, 36, 37, "polymer")
    # ---- trigger ----
    trig = body.bone("trigger", pivot=(0, -27, -27))
    trig.box(-3, 3, -46, -27, -31, -26, "polymer", rot=(-6, 0, 0), pivot=(0, -27, -27))
    trig.box(-1, 1, -42, -30, -32, -30, "polymer")                          # safety blade
    # ---- magazine ----
    mag = m["gun"].bone("magazine", pivot=gp, rot=(MAG_ANGLE, 0, 0))
    mag.box(-11, 11, -126, -18, -6, 26, "steel_dark")
    mag.box(-13, 13, -134, -126, -8, 30, "polymer")                         # base plate
    mag.box(-10, 10, -18, -16, -4, 24, "polymer")                           # follower lips
    mag.round_((0, -11, 6), 29, 9.0)
    for y in (-110, -95, -80, -65, -50, -35):
        mag.box(-11.2, -11, y, y + 2, 20, 23, "white")                       # witness holes
    # ---- arms / sockets ----
    add_arms(m, right_hand=(6, -66, 30), left_hand=(-14, -70, 20), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -152), optic=(0, 17.5, 4), under=(0, -31, -118), eject=(13, 12, -6),
                sight=(0, 22.5, 30))
    return m


def inspect(m):
    a = Anim(m, "inspect", 3.6)
    # press check: bring gun in, pinch the front of the slide
    a.mv("gun", 0.0, 0.35, pos=(-40, 30, 40), rot=(8, 20, -28))
    a.mv("arm_left", 0.05, 0.4, pos=(26, 72, -122), rot=(-30, 30, 50))
    a.grab("arm_left", "slide", 0.42, 0.9, fade_in=0.04, fade_out=0.06)
    a.key("slide", 0.0, pos=(0, 0, 0))
    a.key("slide", 0.45, pos=(0, 0, 0))
    a.key("slide", 0.62, pos=(0, 0, 16), e="inoutquad")
    a.sound(0.6, "press_check")
    a.mv("gun", 0.45, 0.65, pos=(-44, 34, 44), rot=(12, 26, -46))      # tilt to look into the chamber
    a.key("slide", 0.85, pos=(0, 0, 16))
    a.key("slide", 0.92, pos=(0, 0, 0), e="inquad")
    a.sound(0.92, "slide_forward_light")
    a.spring("gun", "rot", 0.92, (1.2, 0, -1), freq=6, damp=9)
    # thumb taps the back of the slide to make sure it's in battery
    a.mv("arm_left", 0.95, 1.15, pos=(18, 40, 30), rot=(-10, 10, 30))
    a.mv("arm_left", 1.15, 1.22, pos=(18, 40, 38), rot=(-10, 10, 30), e="outquad")
    a.sound(1.2, "tap")
    a.mv("arm_left", 1.25, 1.55, pos=(-50, -60, 60), rot=(20, -20, 10))
    # rotate to show the right side
    a.mv("gun", 1.0, 1.7, pos=(-60, 40, 30), rot=(10, -62, -14), e="inoutcubic")
    a.wave("gun", "rot", (0.6, 0.8, 0.0), 1.8)
    a.mv("gun", 2.2, 2.65, pos=(-50, 36, 34), rot=(-6, -40, 18), e="inoutsine")   # tilt down to read the slide
    a.mv("gun", 2.75, 3.45, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutcubic")
    a.mv("arm_left", 2.8, 3.4, pos=(0, 0, 0), rot=(0, 0, 0))
    a.spring("gun", "rot", 3.4, (1.0, 0, 0.6), freq=4, damp=8)
    return a


def build():
    m = model()
    cyc = dict(bone="slide", travel=SLIDE_TRAVEL, t_back=0.022, t_fwd=0.058)
    anims = [
        idle(m),
        idle(m, "idle_empty", locked={"slide": SLIDE_TRAVEL}),
        draw(m, 0.55, sound="draw_pistol", style="pistol"),
        fire_basic(m, "fire", kick=(9, 0.5, 1.5), push=14, cycle=cyc, recover=0.24, length=0.32),
        fire_basic(m, "fire_aim", kick=(9, 0.5, 1.5), push=14, cycle=cyc, recover=0.2, length=0.28, aim=True),
        fire_basic(m, "fire_last", kick=(9, 0.5, 1.5), push=14, cycle=cyc, recover=0.24, length=0.32, lock_back=True),
        pistol_reload(m, "reload", MAG_ANGLE, empty=False, slide_travel=SLIDE_TRAVEL),
        pistol_reload(m, "reload_empty", MAG_ANGLE, empty=True, slide_travel=SLIDE_TRAVEL, release="overhand"),
        inspect(m),
        dry_fire(m),
    ]
    apply_hidden(anims, [])
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.082, -0.27], "rot": [0, 6, 0]}, "ads": {"dist": 0.34}})
GUNS = {"glock17": build}
