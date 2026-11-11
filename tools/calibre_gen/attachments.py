"""Attachment models. Origin = the socket the attachment snaps to on the gun.

optic  : sits on top of a rail, eye-line given by meta.eye (mm above the mount)
muzzle : threads on at the muzzle, extends to -Z
under  : hangs under a rail (-Y)
side   : clamps onto a left side rail (-X)
"""
from .core import Model
from .parts import scope, bipod, flash_hider_a2


def _m(name):
    m = Model(name)
    return m, m.root.bone("body", pivot=(0, 0, 0))


def _clamp(b, z0, z1, hw=12.5, h=8.0, mat="alloy", nuts=1):
    """Rail clamp under an optic: rounded block, a recoil lug line, and thumb nut(s) on the left."""
    b.rbox(-hw, hw, 0, h, z0, z1, mat, r=2.4, edges="top")
    b.box(-hw - 0.3, hw + 0.3, 1.5, 3, z0 + 2, z1 - 2, "rubber")
    for i in range(nuts):
        z = z0 + (z1 - z0) * (i + 0.5) / nuts
        b.cyl((-hw - 3, h * 0.5, z), 11, 6, "steel", axis="x", sides=16)
        b.cyl((-hw - 6.4, h * 0.5, z), 7, 1, "steel_dark", axis="x", sides=8)


def red_dot():
    """Aimpoint-style tube sight on a spacer mount."""
    m, b = _m("red_dot")
    _clamp(b, -16, 16, h=7)
    b.rbox(-8, 8, 7, 12, -14, 14, "alloy", r=2, edges="top")                          # spacer
    b.cyl((0, 22, 0), 26, 50, "alloy")                                                # body tube
    b.cyl((0, 22, -24), 29, 8, "alloy")                                               # objective bell
    b.cyl((0, 22, 23), 28, 7, "alloy")                                                # ocular bell
    b.cyl((0, 22, -28.2), 24, 0.6, "rubber", sides=16)
    b.cyl((0, 22, -28.6), 21, 0.5, "glass_amber", sides=16)
    b.cyl((0, 22, 26.7), 23, 0.6, "rubber", sides=16)
    b.cyl((0, 22, 27.1), 20, 0.5, "glass", sides=16)
    b.cyl((0, 37, -4), 12, 6, "alloy", axis="y", sides=16)                            # elevation cap
    b.cyl((0, 40.4, -4), 9, 1.2, "steel_dark", axis="y", sides=8)
    b.cyl((15, 22, -4), 12, 6, "alloy", axis="x", sides=16)                           # windage cap
    b.cyl((18.4, 22, -4), 9, 1.2, "steel_dark", axis="x", sides=8)
    b.cyl((14, 24, 12), 15, 12, "alloy", axis="x", sides=16)                          # battery / brightness knob
    b.cyl((20.6, 24, 12), 16, 2.4, "steel_dark", axis="x", sides=16)
    for a in (0, 60, 120):
        b.box(20, 22.4, 23.2, 24.8, 4.4, 19.6, "alloy", rot=(a, 0, 0), pivot=(21, 24, 12))
    b.box(-0.8, 0.8, 21.2, 22.8, -27.2, -26.8, "emissive_red")
    m.meta = {"slot": "optic", "eye": [0, 22, 30], "zoom": 1.0, "reticle": "dot", "ads_time": 1.0}
    return m


def holo():
    """EOTech-style holographic sight: low battery base, hooded window."""
    m, b = _m("holo")
    b.rbox(-15, 15, 0, 13, -44, 34, "alloy", r=3, edges="top")                        # base / battery housing
    b.box(-15.3, 15.3, 1.5, 3, -40, 30, "rubber")
    b.cyl((-17.5, 6, 18), 11, 5, "steel", axis="x", sides=16)                         # clamp lever boss
    b.box(-21, -17, 3, 7, -2, 22, "steel")                                            # quick-detach lever
    b.cyl((0, 6.5, -45), 12, 3, "steel_dark", sides=16)                               # battery cap
    for sx in (-1, 1):                                                                # hood side walls, raked forward
        xs = sorted((sx * 12, sx * 15))
        b.box(xs[0], xs[1], 13, 45, -38, 8, "alloy")
        b.box(xs[0], xs[1], 13, 30, 8, 16, "alloy")
    b.rbox(-15, 15, 42, 47, -38, 8, "alloy", r=2.4, edges="top")                      # hood roof
    b.box(-12, 12, 13.5, 42, -34, -33.2, "glass")                                     # front window
    b.box(-12, 12, 13.5, 42, 3.2, 4, "glass")                                         # rear window
    b.box(-10, 10, 14, 15, -33, 4, "rubber")
    for x in (-7, 0, 7):                                                              # rear buttons
        b.box(x - 2.4, x + 2.4, 4, 9, 34, 35.4, "rubber")
    b.box(-0.8, 0.8, 27.2, 28.8, -33.6, -33.3, "emissive_red")
    b.box(-3.4, 3.4, 27.8, 28.2, -33.6, -33.3, "emissive_red")
    m.meta = {"slot": "optic", "eye": [0, 28, 40], "zoom": 1.1, "reticle": "holo", "ads_time": 1.05}
    return m


def acog():
    """Trijicon ACOG 4x32: tapered housing, fibre-optic light pipe on top, thumbscrew base."""
    m, b = _m("acog")
    _clamp(b, -34, 34, h=9, nuts=2)
    b.rbox(-9, 9, 9, 14, -30, 30, "alloy", r=2, edges="top")
    b.cyl((0, 26, -36), 38, 34, "alloy")                                              # objective housing
    b.cyl((0, 26, -54.5), 40, 5, "alloy")
    b.cyl((0, 26, -8), 38, 24, "alloy", d2=29, steps=5)                               # taper to the body
    b.cyl((0, 26, 18), 29, 30, "alloy")                                               # body
    b.cyl((0, 26, 38), 31, 12, "alloy")                                               # ocular
    b.cyl((0, 26, 47), 33, 8, "rubber")                                               # eye ring
    b.cyl((0, 26, -57.3), 34, 0.6, "rubber", sides=16)
    b.cyl((0, 26, -57.7), 30, 0.5, "glass", sides=16)
    b.cyl((0, 26, 51.3), 27, 0.6, "rubber", sides=16)
    b.cyl((0, 26, 51.7), 23, 0.5, "glass", sides=16)
    b.rbox(-5, 5, 40, 46.5, -40, 6, "alloy", r=2, edges="top")                        # fibre housing
    b.box(-2.6, 2.6, 46.5, 48.4, -36, 2, "emissive_red")                              # the light pipe
    b.cyl((17, 26, 16), 13, 6, "alloy", axis="x", sides=16)                           # windage cap
    b.cyl((0, 43, 18), 13, 6, "alloy", axis="y", sides=16)                            # elevation cap
    b.box(-3, 3, 14, 20, 24, 44, "alloy")
    m.meta = {"slot": "optic", "eye": [0, 26, 55], "zoom": 4.0, "reticle": "acog", "ads_time": 1.15}
    return m


def scope_8x():
    m, b = _m("scope_8x")
    scope(b, 0, 40, length=320, tube_d=30, obj_d=50, eye_d=42, mount_y=3)
    b.rbox(-11, 11, 0, 3, -84, 84, "steel_dark", r=1.2, edges="top")
    m.meta = {"slot": "optic", "eye": [0, 40, 175], "zoom": 8.0, "reticle": "mildot", "ads_time": 1.3}
    return m


def pso1():
    """PSO-1: short 4x tube, big knurled drums, sliding sunshade, long rubber eyecup, reticle lamp underneath."""
    m, b = _m("pso1")
    b.rbox(-7, 7, 0, 14, -34, 74, "steel_dark", r=2.4, edges="top")                   # mount bracket
    b.box(-10, -7, 2, 10, -20, 60, "steel_dark")
    b.cyl((-11, 6, 30), 10, 5, "steel", axis="x", sides=16)                           # clamp lever
    scope(b, 20, 36, length=250, tube_d=28, obj_d=38, eye_d=34, mat="steel_dark", mount_y=None, turrets=False)
    b.cyl((0, 36, -116), 40, 26, "steel_dark")                                        # sunshade, pulled out
    for axis, c, o in (("y", (0, 36 + 22, 16), (0, 1)), ("x", (22, 36, 16), (1, 0))):   # the two big drums
        b.cyl(c, 24, 16, "steel_dark", axis=axis)
        b.cyl((c[0] + o[1] * 9, c[1] + o[0] * 9, c[2]), 20, 2.4, "steel", axis=axis, sides=16)
    b.rbox(-9, 9, 14, 24, -6, 40, "steel_dark", r=2.4, edges="bottom")                # saddle on the bracket
    b.cyl((0, 16, 60), 14, 22, "steel_dark")                                          # reticle lamp / battery
    b.cyl((0, 16, 72), 15, 3, "steel", sides=16)
    b.cyl((0, 36, 152), 40, 26, "rubber", d2=46, steps=4)                             # eyecup
    b.cyl((0, 36, 168), 46, 8, "rubber")
    m.meta = {"slot": "optic", "eye": [0, 36, 180], "zoom": 4.0, "reticle": "pso1", "ads_time": 1.2}
    return m


def _can(b, d, length, collar_d, mat="steel_dark"):
    b.cyl((0, 0, -length / 2 - 4), d, length - 8, mat)
    b.cyl((0, 0, -8), collar_d, 16, "steel")                                          # mount collar
    for ang in (0, 60, 120):                                                          # wrench flats
        b.box(-collar_d / 2 - 0.3, collar_d / 2 + 0.3, -2, 2, -15, -3, "steel_dark", rot=(0, 0, ang),
              pivot=(0, 0, -8))
    b.cyl((0, 0, -22), d + 1.4, 3, mat)                                               # knurled bands
    b.cyl((0, 0, -length + 12), d + 1.4, 3, mat)
    b.cyl((0, 0, -length - 1.5), d * 0.92, 3.4, mat)                                  # end cap
    b.cyl((0, 0, -length - 3.4), d * 0.4, 0.6, "rubber", sides=16)


def suppressor_pistol():
    m, b = _m("suppressor_pistol")
    _can(b, 32, 160, 24)
    m.meta = {"slot": "muzzle", "length": 160}
    return m


def suppressor_rifle():
    m, b = _m("suppressor_rifle")
    _can(b, 40, 190, 30)
    m.meta = {"slot": "muzzle", "length": 190}
    return m


def compensator():
    m, b = _m("compensator")
    b.rbox(-12, 12, -12, 12, -60, 0, "steel_dark", r=4, edges="all")
    b.cyl((0, 0, -2.5), 20, 5, "steel")
    for z in (-50, -36, -22):
        b.box(-6, 6, 9, 12.4, z, z + 7, "rubber")
        b.box(-12.4, 12.4, -4, 4, z, z + 7, "rubber")
    b.cyl((0, 0, -60.3), 10, 0.6, "rubber", sides=16)
    m.meta = {"slot": "muzzle", "length": 60}
    return m


def flash_hider():
    m, b = _m("flash_hider")
    flash_hider_a2(b, 0, d=22, length=60)
    m.meta = {"slot": "muzzle", "length": 60}
    return m


def vertical_grip():
    m, b = _m("vertical_grip")
    b.rbox(-12.5, 12.5, -8, 0, -22, 22, "polymer", r=2.4, edges="bottom")
    b.cyl((-14.5, -4, 0), 9, 4, "steel", axis="x", sides=16)
    b.cyl((0, -58, 0), 30, 100, "polymer", axis="y", d2=26, steps=3)
    for i in range(5):
        b.cyl((0, -30 - i * 14, 0), 31.4, 3, "polymer", axis="y")
    b.cyl((0, -111, 0), 33, 6, "rubber", axis="y")
    m.meta = {"slot": "under", "hand": [0, -55, 0]}
    return m


def angled_grip():
    m, b = _m("angled_grip")
    b.rbox(-12.5, 12.5, -7, 0, -44, 44, "polymer", r=2.4, edges="bottom")
    b.profile(-13.5, 13.5, [(-44, -6), (40, -6)], [(-44, -12), (-34, -40), (-22, -44), (40, -8)], "polymer")
    for i in range(4):
        b.box(-13.9, 13.9, -30 + i * 5, -27.6 + i * 5, -14 + i * 9, 4 + i * 9, "rubber")
    m.meta = {"slot": "under", "hand": [0, -20, 10]}
    return m


def bipod_att():
    m, b = _m("bipod_att")
    bipod(b, 0, y=0, legs_len=190, folded=True, mat="alloy")
    m.meta = {"slot": "under", "hand": [0, -10, 0]}
    return m


def laser():
    """Box laser / illuminator on the left rail."""
    m, b = _m("laser")
    b.rbox(-30, 0, -14, 14, -26, 26, "polymer", r=3.5, edges="all")
    b.cyl((-15, 6, -27.5), 12, 4, "polymer", sides=16)                                # laser aperture
    b.cyl((-15, 6, -29.7), 8, 0.6, "glass", sides=8)
    b.cyl((-15, -6, -28.5), 16, 6, "polymer", sides=16)                               # illuminator
    b.cyl((-15, -6, -31.7), 12, 0.6, "glass", sides=16)
    b.cyl((-15, 15.5, 4), 9, 3.4, "steel_dark", axis="y", sides=16)                   # adjusters
    b.cyl((-31.6, 4, 4), 9, 3.4, "steel_dark", axis="x", sides=16)
    b.box(-24, -10, 14, 15.4, 12, 22, "rubber")                                       # fire button
    b.cyl((0.8, 0, 0), 9, 2, "steel", axis="x", sides=16)                             # clamp screw
    m.meta = {"slot": "side", "beam": [-15, 6, -30]}
    return m


ATTACHMENTS = {f.__name__: f for f in (red_dot, holo, acog, scope_8x, pso1, suppressor_pistol, suppressor_rifle,
                                       compensator, flash_hider, vertical_grip, angled_grip, bipod_att, laser)}
