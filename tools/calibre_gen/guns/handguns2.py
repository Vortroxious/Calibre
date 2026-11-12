"""Expansion 3 handguns on pistolkit, to real dimensions: SIG P226, Makarov PM, Walther P38, Luger P08 (toggle
action) and Mauser C96 (loaded from stripper clips)."""
import copy

import numpy as np

from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden, moving)
from ..templates import bolt_clip_load
from ..parts import pins, screw, serrations
from ..pistolkit import (raked, grip_frame, grip_panels, guard, slide_shell, port, muzzle_face, rear_plate, sights,
                         barrel_assy, hammer, trigger, control, pistol_mag)
from ..longkit import tangent_sight
from .sidearms import _auto_anims, _fix, _regrip, _hands, _inspect, PISTOL_FP
from .ww2 import _clip, _round_load


# =================================================================================================
# SIG Sauer P226  (196 mm long, 112 mm barrel, alloy frame, decocker)
# =================================================================================================
def p226():
    A, TRAVEL = -16.0, (0, 0, 44)
    m = new_gun("p226")
    body = m["body"]
    AL, SL = "alloy", "steel_dark"
    gp = (0, -19, 4)
    body.chamfer_box(-13.5, 13.5, -26, -9, -136, -22, AL, ch=2.8, edges="bottom")      # dust cover
    _fix(body.box(-13.5, 13.5, -28, -9, -84, 30, AL))
    _fix(body.box(-12, 12, -24, -9, 28, 40, AL))                                     # tang
    body.box(-10.5, 10.5, -30, -26, -132, -98, AL)                                   # accessory rail
    for i in range(3):
        body.box(-11, 11, -30.4, -28, -128 + i * 11, -123 + i * 11, "rubber")
    guard(body, -74, -24, -26, -58, AL, w=9, th=4, style="square")
    grip_frame(body, gp, A, 14, -122, -24, 30, AL, hump=2.2, front="checker", back="grooves")
    grip_panels(body, gp, A, 14, -114, -34, -17, 25, "polymer", style="checker", proud=1.4)
    r = raked(A, gp)
    body.box(-3, 3, -127, -122, 22, 28, AL, **r)                                     # lanyard loop
    pins(body, 13.5, [(-16, -38), (-20, 24), (-12, 12)], d=4, mat="steel_dark")
    control(body, "slide_stop", (-13.5, -12, -44),
            [(-15.4, -13.5, -13.4, -9.6, -50, -18, SL), (-16.6, -15.2, -14, -9, -26, -16, SL)], press=(0, 2.4, 0))
    control(body, "decocker", (-13.5, -18, -14),
            [(-15.6, -13.5, -21, -15, -26, -8, SL), (-16.8, -15.6, -20, -16, -26, -18, SL)], turn=(30, 0, 0))
    control(body, "takedown", (-13.5, -15, -92),
            [(-15.6, -13.5, -18.5, -11.5, -98, -86, SL), (-16.4, -15.6, -17, -13, -97, -82, SL)], turn=(-70, 0, 0))
    control(body, "mag_release", (-14, -37, -18),
            [(-16.2, -14, -41, -33, -22, -13, SL), (-16.6, -16.2, -40, -34, -21, -14, AL)], press=(1.6, 0, 0))
    trigger(body, (0, -27, -44), mat=SL, length=24, w=6.5)
    barrel_assy(body, -147, -26, d=14.5, rod_y=-7.5)
    hammer(body, (0, -8, 38), mat=SL, style="spur", cocked=30, w=7)
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide_shell(slide, -146, 34, -9, 13.5, 13, SL, ch=3.4)
    for sx in (-1, 1):                                                              # stepped slide flats
        slide.box(sx * 13 - 0.3, sx * 13 + 0.3, 1, 2, -140, 28, "steel")
    port(slide, 13, 13.5, -58, -24, 4)
    serrations(slide, 13, -6, 10, 2, 30, n=9, mat="rubber", proud=0.3)
    sights(slide, -142, 32, 14.1, front_h=5.0, rear_h=5.8, style="dot", mat=SL, rear_w=16)
    rear_plate(slide, 34, 13, -9, 13.5, mat=SL)
    muzzle_face(slide, -146, 14.5, 0, rod_y=-7.5, rod_d=6)
    pistol_mag(m, gp, A, -19, -128, -17, 16, 21, base_mat="polymer", round_d=9.6, round_len=29, holes=5)
    _hands(m, gp, A, -122, -24, 30)
    add_sockets(m, muzzle=(0, 0, -148), optic=None, under=(0, -30, -116), eject=(13, 10, -40), sight=(0, 19.9, 32))
    _regrip(m, -13, -82)
    anims = _auto_anims(m, A, TRAVEL, (9, 0.5, 1.4), 13, hammer_rot=-30)
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Makarov PM  (162 mm long, 94 mm fixed barrel, blowback, slide-mounted safety)
# =================================================================================================
def makarov():
    A, TRAVEL = -14.0, (0, 0, 36)
    m = new_gun("makarov")
    body = m["body"]
    SL = "steel_dark"
    gp = (0, -17, 2)
    body.chamfer_box(-11.5, 11.5, -22, -9, -110, -22, SL, ch=3.4, edges="bottom")
    _fix(body.box(-11.5, 11.5, -25, -9, -74, 26, SL))
    _fix(body.box(-10.5, 10.5, -22, -11, 24, 34, SL))
    guard(body, -64, -22, -22, -50, SL, w=7.5, th=3.6, style="round")
    body.box(-4, 4, -25, -22, -60, -54, "steel")                                     # takedown: the guard pulls down
    grip_frame(body, gp, A, 11.5, -100, -22, 26, SL, hump=1.6, front="plain", back="plain")
    grip_panels(body, gp, A, 11.5, -94, -30, -18, 22, "polymer", style="checker", proud=3.4, screws=False)
    r = raked(A, gp)
    for sx in (-1, 1):                                                              # the star in the grip
        xs = sorted((sx * 15.1, sx * 15.5))
        body.box(xs[0], xs[1], -48, -44, 2, 6, "steel", **r)
    body.box(-3, 3, -104, -98, 16, 24, SL, **r)                                      # lanyard ring post
    body.box(-1.6, 1.6, -108, -104, 14, 26, "steel", **r)
    pins(body, 11.5, [(-14, -34), (-18, 20)], d=4, mat="steel")
    control(body, "slide_stop", (-11.5, -12, -30),
            [(-13.2, -11.5, -13.2, -9.6, -38, -14, SL)], press=(0, 2.2, 0))
    mr = body.bone("mag_release", pivot=(0, -96, 24))                                # heel catch
    mr.box(-4, 4, -100, -92, 22, 28, "steel", **r)
    moving(m, "mag_release", pos=(0, 0, 2))
    trigger(body, (0, -26, -36), mat=SL, length=20, w=5.5)
    body.cyl((0, 0, -60), 12, 100, "steel_light")                                    # fixed barrel
    body.cyl((0, 0, -110.3), 5.6, 0.6, "rubber", sides=8)
    body.cyl((0, 0, -62), 15, 72, "steel")                                           # recoil spring round it
    hammer(body, (0, -7, 30), mat=SL, style="ring", cocked=28, w=6.5)
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.rbox(-11.5, 11.5, -9, 12, -112, 30, SL, r=5.5, edges="top")                # rounded slide
    port(slide, 11.5, 12, -52, -28, 3)
    for i in range(10):                                                             # fine slanted serrations
        z = 4 + i * 2.4
        for sx in (-1, 1):
            slide.box(sx * 11.5 - 0.3, sx * 11.5 + 0.3, -6, 8, z, z + 1.1, "rubber", rot=(10, 0, 0),
                      pivot=(0, 0, z))
    slide.cyl((0, 0, -112.3), 13.5, 0.6, SL)
    slide.cyl((0, 0, -112.6), 7, 0.5, "rubber", sides=8)
    sights(slide, -108, 28, 12, front_h=4.4, rear_h=5.0, style="plain", mat=SL, rear_w=12)
    sf = slide.bone("safety", pivot=(-11.5, 3, 18))                                  # safety-decocker on the slide
    sf.box(-13.8, -11.5, 0.5, 5.5, 6, 22, SL)
    sf.box(-14.4, -13.8, 1.5, 4.5, 8, 14, "steel")
    sf.box(-11.8, -11.4, -2.5, -0.8, 18, 22, "emissive_red")
    moving(m, "safety", rot=(-50, 0, 0))
    pistol_mag(m, gp, A, -17, -104, -14, 11, 12, body_mat=SL, base_mat=SL, round_d=9.4, round_len=25, holes=4,
               double=False)
    _hands(m, gp, A, -100, -22, 26)
    add_sockets(m, muzzle=(0, 0, -114), eject=(12, 9, -40), sight=(0, 17, 28))
    _regrip(m, -4, -70)
    anims = _auto_anims(m, A, TRAVEL, (7.5, 0.5, 1.3), 11, hammer_rot=-30)
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Walther P38  (216 mm long, 125 mm barrel standing proud of an open-top slide)
# =================================================================================================
def p38():
    A, TRAVEL = -18.0, (0, 0, 40)
    m = new_gun("p38")
    body = m["body"]
    ST, SL = "steel_parked", "steel_dark"
    gp = (0, -18, 4)
    body.chamfer_box(-12, 12, -22, -9, -116, -22, ST, ch=3.0, edges="bottom")
    _fix(body.box(-12, 12, -26, -9, -78, 30, ST))
    _fix(body.box(-11, 11, -22, -11, 28, 38, ST))
    guard(body, -74, -22, -22, -52, ST, w=8, th=3.8, style="round")
    grip_frame(body, gp, A, 12, -118, -22, 28, ST, hump=1.4, front="plain", back="plain")
    grip_panels(body, gp, A, 12, -110, -32, -16, 24, "polymer", style="grooves", proud=3.8)
    r = raked(A, gp)
    body.box(-3, 3, -124, -118, 18, 26, ST, **r)                                     # lanyard loop
    pins(body, 12, [(-16, -38), (-18, 24)], d=4, mat="steel")
    control(body, "slide_stop", (-12, -12, -40),
            [(-14, -12, -13.6, -9.8, -46, -18, SL), (-15.2, -14, -14, -9.2, -24, -16, SL)], press=(0, 2.4, 0))
    control(body, "takedown", (-12, -15, -96),
            [(-14.2, -12, -18.5, -11.5, -100, -92, SL), (-15, -14.2, -17, -13, -99, -86, SL)], turn=(-70, 0, 0))
    mr = body.bone("mag_release", pivot=(0, -116, 24))                               # heel catch
    mr.box(-4, 4, -120, -112, 20, 28, "steel", **r)
    moving(m, "mag_release", pos=(0, 0, 2))
    trigger(body, (0, -26, -42), mat=SL, length=22, w=6)
    b = barrel_assy(body, -170, -28, d=14, rod_y=None, mat=SL)
    b.box(-6, 6, -13, -6, -70, -40, "steel")                                         # locking block
    b.cyl((0, 7.2, -162), 3.4, 12, SL)                                               # front sight on the barrel
    b.box(-1.6, 1.6, 7, 13.5, -166, -158, SL)
    hammer(body, (0, -7, 36), mat=SL, style="spur", cocked=28, w=7)
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-13, 13, -9, -4.5, -122, 34, SL)
    for sx in (-1, 1):
        xs = sorted((sx * 8.4, sx * 13))
        slide.box(xs[0], xs[1], -4.5, 7.5, -122, -30, SL)                            # side walls
    slide.chamfer_box(-13, 13, -9, 12.5, -32, 34, SL, ch=3.8)                        # rear block
    slide.box(-8.4, 8.4, 6, 12.5, -122, -30, "rubber")                               # the open top shows the barrel
    serrations(slide, 13, -6, 9.5, 6, 30, n=9, mat="rubber", proud=0.3)
    sights(slide, -164, 30, 12.5, front_h=0.1, rear_h=5.4, style="plain", mat=SL, rear_w=14,
           front_on=b, front_top=7.4)
    slide.box(13, 13.6, 1.5, 5.5, -30, -10, "steel")                                 # loaded-chamber pin
    sf = slide.bone("safety", pivot=(-13, 3, 20))
    sf.box(-15.6, -13, 0.5, 5.5, 6, 24, SL)
    sf.box(-16.2, -15.6, 1.5, 4.5, 8, 16, "steel")
    moving(m, "safety", rot=(-45, 0, 0))
    pistol_mag(m, gp, A, -18, -124, -16, 12, 14, body_mat=SL, base_mat=SL, round_d=9.6, round_len=29, holes=4,
               double=False)
    _hands(m, gp, A, -118, -22, 28)
    add_sockets(m, muzzle=(0, 0, -172), eject=(13, 9, -40), sight=(0, 17.2, 30))
    _regrip(m, -13, -78)
    anims = _auto_anims(m, A, TRAVEL, (9, 0.5, 1.4), 13, hammer_rot=-30)
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Luger P08  (222 mm long, 102 mm barrel, toggle-lock: the knuckle breaks upward on every shot)
# =================================================================================================
TOGGLE_DEG = 64.0


def _toggle_rotation(anims, travel_z):
    """The kit animates the toggle like a slide (a short travel along +Z). Turn that into the toggle breaking:
    the front link swings its rear up, the rear link folds the other way about the knuckle."""
    k1, k2 = -TOGGLE_DEG / travel_z, 2 * TOGGLE_DEG / travel_z
    for a in anims:
        tr = a.tracks.pop(("toggle", "pos"), None)
        if tr is not None:
            for bone, k in (("toggle", k1), ("toggle_rear", k2)):
                nt = copy.deepcopy(tr)
                nt.channel = "rot"
                nt.keys = [(t, v if v is not None and not isinstance(v, np.ndarray) else np.array([v[2] * k, 0.0, 0.0]),
                            e) for t, v, e in tr.keys]
                a.tracks[(bone, "rot")] = nt
        a.layers = [(b, ch, f) for b, ch, f in a.layers if not (b == "toggle" and ch == "pos")]
        if "toggle" in a.rest and "pos" in a.rest["toggle"]:
            z = float(np.asarray(a.rest["toggle"].pop("pos"))[2])
            a.rest["toggle"]["rot"] = np.array([z * k1, 0.0, 0.0])
            a.rest.setdefault("toggle_rear", {})["rot"] = np.array([z * k2, 0.0, 0.0])


def luger():
    A = -34.0
    m = new_gun("luger")
    body = m["body"]
    ST = "steel_dark"
    gp = (0, -16, 12)
    # receiver (barrel extension) with the toggle on top, the frame and the steeply raked grip
    body.rbox(-11, 11, -14, 11, -26, 82, ST, r=3, edges="top")                       # receiver
    body.box(-11.4, 11.4, -4, 4, 10, 74, "rubber")                                   # side rails gap
    body.rbox(-12, 12, -26, -10, -30, 86, ST, r=2.5, edges="bottom")                 # frame
    body.cyl((0, 0, -32), 22, 14, ST)                                                # barrel shank
    body.cyl((0, 0, -78), 16, 82, ST, d2=13, steps=4)                                # tapered barrel
    body.cyl((0, 0, -119.4), 13, 0.6, ST)
    body.cyl((0, 0, -119.8), 5.6, 0.5, "rubber", sides=8)
    body.box(-3, 3, 5, 9, -118, -102, ST)                                            # front sight base
    body.box(-1.2, 1.2, 9, 16.5, -114, -106, ST)
    body.box(-6, 6, 11, 14, 74, 84, ST)                                              # rear sight notch on the
    for sx in (-1, 1):                                                              # toggle's rear link
        body.box(sx * 4 - 2, sx * 4 + 2, 14, 18, 76, 82, ST)
    guard(body, -20, 20, -26, -48, ST, w=7, th=3.6, style="round")
    trigger(body, (0, -26, 2), mat=ST, length=18, w=5)
    grip_frame(body, gp, A, 12, -96, 20, 56, ST, y_top=-14, hump=0.0, front="plain", back="plain")
    grip_panels(body, gp, A, 12, -90, -24, 24, 52, "wood", style="checker", proud=3.6)
    r = raked(A, gp)
    control(body, "safety", (-12, -18, 66), [(-14.4, -12, -22, -14, 58, 74, "steel"),
                                             (-15, -14.4, -21, -15, 70, 74, "steel")], turn=(-40, 0, 0))
    control(body, "takedown", (-12, -10, -18), [(-14.4, -12, -14, -6, -24, -10, "steel")], turn=(-70, 0, 0))
    control(body, "mag_release", (-12, -30, 22), [(-14, -12, -34, -26, 18, 26, "steel")], press=(1.6, 0, 0))
    pins(body, 12, [(-18, -24), (-18, 80)], d=4, mat="steel")
    # toggle: front link on the barrel extension, rear link to the frame, knurled knobs at the knuckle
    tg = body.bone("toggle", pivot=(0, 11, 20))
    tg.rbox(-7, 7, 4, 15, 18, 50, ST, r=3, edges="top")
    tg.box(-4, 4, 3, 11, 10, 20, "steel_light")                                       # breech block
    rr = tg.bone("toggle_rear", pivot=(0, 11, 50))
    rr.rbox(-7, 7, 4, 15, 50, 76, ST, r=3, edges="top")
    for sx in (-1, 1):                                                              # the knuckle grips
        rr.cyl((sx * 11, 12, 50), 16, 7, ST, axis="x", sides=16)
        for k in range(8):
            rr.box(sx * 14.6 - 0.3, sx * 14.6 + 0.3, 11, 13, 49, 51, "steel_light", rot=(k * 22.5, 0, 0),
                   pivot=(sx * 14.6, 12, 50))
    pistol_mag(m, gp, A, -14, -100, 14, 44, 12, body_mat=ST, base_mat="wood", round_d=9.6, round_len=29, holes=3,
               double=False)
    _hands(m, gp, A, -96, 20, 56)
    add_sockets(m, muzzle=(0, 0, -121), eject=(0, 18, 30), sight=(0, 16.5, 80))
    anims = _auto_anims(m, A, (0, 0, 1), (8, 0.5, 1.3), 12, slide="toggle", release="overhand")
    _toggle_rotation(anims, 1.0)
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Mauser C96  (312 mm long, 140 mm barrel, fixed 10-round magazine in front of the guard, loaded from clips)
# =================================================================================================
def c96():
    m = new_gun("c96")
    body = m["body"]
    ST, WD = "steel_dark", "wood"
    body.rbox(-13, 13, -40, 14, -60, 96, ST, r=3, edges="top")                       # receiver
    for sx in (-1, 1):
        body.box(sx * 13 - 0.4, sx * 13 + 0.4, -30, -6, -50, 30, "steel")           # milled side panels
        body.box(sx * 13 - 0.6, sx * 13 + 0.6, -28, -8, -46, 26, ST)
    body.cyl((0, 0, -132), 15, 146, ST, d2=12.5, steps=4)                            # barrel
    body.cyl((0, 0, -205.4), 11.5, 0.6, ST)
    body.cyl((0, 0, -205.8), 5.4, 0.5, "rubber", sides=8)
    body.box(-3, 3, 6, 9, -202, -188, ST)                                            # front sight
    body.box(-1, 1, 9, 17, -198, -192, ST)
    body.rbox(-10, 10, 0, 12, -60, -10, ST, r=2, edges="top")                        # rear sight base
    tangent_sight(body, -56, -12, 12, ST, w=10, h=5)                                 # notch top at 17
    body.rbox(-12, 12, -88, -40, -58, -8, ST, r=2.5)                                 # magazine box
    body.box(-12.4, 12.4, -88, -84, -58, -8, "steel")                                # floorplate
    guard(body, -6, 34, -40, -66, ST, w=7, th=3.6, style="round")
    trigger(body, (0, -40, 12), mat=ST, length=18, w=5)
    # broomhandle grip
    gp, A = (0, -36, 74), -14.0
    r = raked(A, gp)
    body.rbox(-13, 13, -136, -36, 56, 96, WD, r=12, axis="y", rot=(A, 0, 0), pivot=gp)
    for i in range(12):                                                             # the grip's grooves
        y = -130 + i * 7.6
        body.box(-13.3, 13.3, y, y + 1.8, 58, 94, "rubber", **r)
    body.rbox(-9, 9, -144, -136, 62, 90, ST, r=3, axis="y", rot=(A, 0, 0), pivot=gp)  # stock-slot cap
    body.cyl((0, -140, 99), 8, 4, "steel", axis="z", sides=8)                         # lanyard ring
    hammer(body, (0, -6, 98), mat=ST, style="ring", cocked=26, w=7)
    control(body, "safety", (-13, -6, 92), [(-15.4, -13, -10, -2, 86, 96, "steel")], turn=(-50, 0, 0))
    pins(body, 13, [(-30, -40), (-30, 40), (-14, 80)], d=4.5, mat="steel")
    bolt = body.bone("bolt", pivot=(0, 0, 0))                                        # square bolt with its ears
    bolt.box(-8, 8, -1, 12, -16, 94, "steel_light")
    for sx in (-1, 1):
        bolt.box(sx * 8, sx * 12.6, 3, 11, 78, 94, "steel_light")
        for k in range(4):
            bolt.box(sx * 12.6 - 0.3, sx * 12.6 + 0.3, 3, 11, 79 + k * 4, 80.5 + k * 4, "steel")
    _clip(m, (0, 13, -30), n=10, case_len=25, bullet_len=10, d=9.8, step=4.6)
    _round_load(m, (0, 8, -40), 35, 9.8)
    add_arms(m, right_hand=(8, -84, 72), left_hand=(-14, -90, 58), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -207), eject=(0, 16, -20), sight=(0, 17, -12))
    travel = (0, 0, 52)
    cyc = dict(bone="bolt", travel=travel, t_back=0.024, t_fwd=0.064)
    k = dict(kick=(8.5, 0.5, 1.4), push=12, cycle=cyc, hammer=-28)
    anims = [idle(m), draw(m, 0.6, sound="draw_pistol", style="pistol"),
             fire_basic(m, "fire", recover=0.24, length=0.32, **k),
             fire_basic(m, "fire_aim", recover=0.2, length=0.28, aim=True, **k),
             *bolt_clip_load(m, travel=travel, handle_rot=(0, 0, 0), push=40), _inspect(m), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    return GunAsset(m, anims, {"hip": PISTOL_FP["hip"], "ads": {"dist": 0.38}})


GUNS = {"p226": p226, "makarov": makarov, "p38": p38, "luger": luger, "c96": c96}
