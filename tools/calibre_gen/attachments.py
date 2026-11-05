"""Attachment models. Origin = the socket the attachment snaps to on the gun.

optic  : sits on top of a rail, eye-line given by meta.eye (mm above the mount)
muzzle : threads on at the muzzle, extends to -Z
under  : hangs under a rail (-Y)
side   : clamps onto a left side rail (-X)
"""
from .core import Model
from .parts import scope


def _m(name):
    m = Model(name)
    return m, m.root.bone("body", pivot=(0, 0, 0))


def red_dot():
    m, b = _m("red_dot")
    b.box(-12, 12, 0, 8, -20, 20, "alloy")
    b.cyl((0, 22, 0), 30, 44, "alloy", sides=12)
    b.cyl((0, 22, -22.5), 24, 1, "glass", sides=12)
    b.cyl((0, 22, 22.5), 24, 1, "glass", sides=12)
    b.cyl((14, 22, 0), 10, 8, "alloy", axis="x")
    b.cyl((0, 37, 0), 10, 6, "alloy", axis="y")
    b.box(-0.8, 0.8, 21.2, 22.8, -18, -17.6, "emissive_red")
    m.meta = {"slot": "optic", "eye": [0, 22, 30], "zoom": 1.0, "reticle": "dot", "ads_time": 1.0}
    return m


def holo():
    m, b = _m("holo")
    b.box(-14, 14, 0, 14, -40, 30, "alloy")
    b.box(-14, -11, 14, 44, -36, 10, "alloy")
    b.box(11, 14, 14, 44, -36, 10, "alloy")
    b.box(-14, 14, 41, 44, -36, 10, "alloy")
    b.box(-11, 11, 14, 41, -30, -29, "glass")
    b.box(-11, 11, 14, 41, 4, 5, "glass")
    b.box(-6, 6, 4, 14, 10, 30, "rubber")
    for x in (-0.8,):
        b.box(x, x + 1.6, 27, 29, -29.6, -29.4, "emissive_red")
    m.meta = {"slot": "optic", "eye": [0, 28, 40], "zoom": 1.1, "reticle": "holo", "ads_time": 1.05}
    return m


def acog():
    m, b = _m("acog")
    b.box(-12, 12, 0, 10, -40, 40, "alloy")
    b.cyl((0, 26, -10), 30, 70, "alloy", sides=12)
    b.cyl((0, 26, -48), 40, 18, "alloy", sides=12)
    b.cyl((0, 26, 34), 32, 22, "rubber", sides=12)
    b.cyl((0, 26, -57.5), 34, 1, "glass", sides=12)
    b.cyl((0, 26, 45.5), 26, 1, "glass", sides=12)
    b.box(-4, 4, 41, 47, -30, 0, "alloy")
    b.box(-2.5, 2.5, 47, 51, -24, -6, "emissive_green")                           # fibre optic
    m.meta = {"slot": "optic", "eye": [0, 26, 55], "zoom": 4.0, "reticle": "acog", "ads_time": 1.15}
    return m


def scope_8x():
    m, b = _m("scope_8x")
    scope(b, 0, 40, length=320, tube_d=30, obj_d=50, eye_d=42, mount_y=0)
    m.meta = {"slot": "optic", "eye": [0, 40, 175], "zoom": 8.0, "reticle": "mildot", "ads_time": 1.3}
    return m


def pso1():
    m, b = _m("pso1")
    b.box(-6, 6, 0, 14, -30, 70, "steel_dark")
    scope(b, 20, 36, length=280, tube_d=28, obj_d=40, eye_d=34, mat="steel_dark", mount_y=14)
    b.box(-20, 20, 20, 52, 150, 176, "rubber")
    m.meta = {"slot": "optic", "eye": [0, 36, 180], "zoom": 4.0, "reticle": "pso1", "ads_time": 1.2}
    return m


def suppressor_pistol():
    m, b = _m("suppressor_pistol")
    b.cyl((0, 0, -80), 32, 160, "steel_dark", sides=12)
    b.cyl((0, 0, -161), 12, 2, "rubber", sides=8)
    m.meta = {"slot": "muzzle", "length": 160}
    return m


def suppressor_rifle():
    m, b = _m("suppressor_rifle")
    b.cyl((0, 0, -100), 40, 180, "steel_dark", sides=12)
    b.cyl((0, 0, -10), 32, 20, "steel", sides=12)
    b.cyl((0, 0, -191), 14, 2, "rubber", sides=8)
    m.meta = {"slot": "muzzle", "length": 190}
    return m


def compensator():
    m, b = _m("compensator")
    b.box(-12, 12, -12, 12, -60, 0, "steel_dark")
    for z in (-50, -36, -22):
        b.box(-6, 6, 8, 12.4, z, z + 7, "rubber")
        b.box(-12.4, 12.4, -4, 4, z, z + 7, "rubber")
    m.meta = {"slot": "muzzle", "length": 60}
    return m


def flash_hider():
    m, b = _m("flash_hider")
    b.cyl((0, 0, -30), 22, 60, "steel_dark")
    for i in range(4):
        b.box(-11.5, 11.5, -2, 2, -58, -20, "rubber", rot=(0, 0, 45 * i), pivot=(0, 0, -40))
    m.meta = {"slot": "muzzle", "length": 60}
    return m


def vertical_grip():
    m, b = _m("vertical_grip")
    b.box(-12, 12, -6, 0, -22, 22, "polymer")
    b.cyl((0, -60, 0), 30, 110, "polymer", axis="y")
    b.cyl((0, -116, 0), 34, 6, "rubber", axis="y")
    m.meta = {"slot": "under", "hand": [0, -55, 0]}
    return m


def angled_grip():
    m, b = _m("angled_grip")
    b.box(-12, 12, -6, 0, -40, 40, "polymer")
    b.box(-14, 14, -40, -6, -40, 30, "polymer", rot=(-30, 0, 0), pivot=(0, -6, -40))
    m.meta = {"slot": "under", "hand": [0, -20, 10]}
    return m


def bipod_att():
    m, b = _m("bipod_att")
    b.box(-14, 14, -14, 0, -20, 20, "alloy")
    for sx in (-1, 1):
        b.box(sx * 8 - 4, sx * 8 + 4, -18, -10, -200, -10, "steel_dark")
    m.meta = {"slot": "under", "hand": [0, -10, 0]}
    return m


def laser():
    m, b = _m("laser")
    b.box(-30, 0, -14, 14, -24, 24, "polymer")
    b.cyl((-15, 6, -26), 8, 4, "glass")
    b.cyl((-15, -6, -26), 12, 4, "glass")
    b.box(-31, -30, -4, 4, 0, 14, "steel")
    m.meta = {"slot": "side", "beam": [-15, 6, -28]}
    return m


ATTACHMENTS = {f.__name__: f for f in (red_dot, holo, acog, scope_8x, pso1, suppressor_pistol, suppressor_rifle,
                                       compensator, flash_hider, vertical_grip, angled_grip, bipod_att, laser)}
