"""Handguns, rebuilt on pistolkit to real dimensions: Glock 17, M1911A1, Beretta M9, Desert Eagle, Walther PPQ,
Bersa Thunder 380, Ruger Mark III, FN Five-seveN, H&K USP, CZ 75 SP-01."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden, moving)
from ..templates import pistol_reload
from ..parts import pins, screw, serrations, arc
from ..pistolkit import (raked, grip_frame, grip_panels, guard, slide_shell, port, muzzle_face, rear_plate, sights,
                         barrel_assy, hammer, trigger, control, pistol_mag)

PISTOL_FP = {"hip": {"pos": [0.1, -0.082, -0.27], "rot": [0, 6, 0]}, "ads": {"dist": 0.34}}


def _inspect(m):
    """Placeholder: build_assets replaces every inspect with the generated close-up one (cs2.py)."""
    return Anim(m, "inspect", 1.0)


def _auto_anims(m, A, travel, kick, push, hammer_rot=None, release="thumb", draw_len=0.55, rec=0.24, length=0.32,
                reload_len=None, reload_empty_len=None, slide="slide"):
    cyc = dict(bone=slide, travel=travel, t_back=0.022, t_fwd=0.058)
    k = dict(kick=kick, push=push, cycle=cyc, hammer=hammer_rot)
    return [idle(m), idle(m, "idle_empty", locked={slide: travel}),
            draw(m, draw_len, sound="draw_pistol", style="pistol"),
            fire_basic(m, "fire", recover=rec, length=length, **k),
            fire_basic(m, "fire_aim", recover=rec * 0.84, length=length * 0.88, aim=True, **k),
            fire_basic(m, "fire_last", recover=rec, length=length, lock_back=True, **k),
            pistol_reload(m, "reload", A, empty=False, slide_bone=slide, slide_travel=travel, length=reload_len),
            pistol_reload(m, "reload_empty", A, empty=True, slide_bone=slide, slide_travel=travel, release=release,
                          length=reload_empty_len),
            _inspect(m), dry_fire(m)]


# =================================================================================================
# Glock 17 Gen 4  (204 mm long, 186 mm slide, 114 mm barrel, 139 mm tall, 22 degree grip)
# =================================================================================================
def glock17():
    A, TRAVEL = -22.0, (0, 0, 42)
    m = new_gun("glock17")
    body = m["body"]
    P, SL = "polymer", "steel_dark"
    gp = (0, -18, 2)
    # frame: dust cover with the single-slot rail, body over the grip, beavertail
    body.chamfer_box(-12.4, 12.4, -24, -9.5, -143, -22, P, ch=2.4, edges="bottom")
    _fix(body.box(-12.4, 12.4, -27, -9.5, -86, 30, P))
    _fix(body.box(-12, 12, -23, -9.5, 28, 37, P))
    _fix(body.box(-10, 10, -19, -11, 36, 39.5, P))
    body.box(-10.5, 10.5, -28.5, -24, -138, -92, P)                              # accessory rail
    body.box(-10.9, 10.9, -29, -25.6, -119, -112, "rubber")
    body.box(-5, 5, -24.5, -24, -88, -74, "steel")                               # serial plate
    for sx in (-1, 1):                                                           # rail side grooves
        body.box(sx * 12.4 - 0.3, sx * 12.4 + 0.3, -21.5, -19.5, -138, -92, "rubber")
        body.box(sx * 12.4 - 0.4, sx * 12.4 + 0.5 * sx + 0.1 * sx, -19, -15, -64, -56, "steel_dark")   # takedown tabs
        body.box(sx * 15 - 0.3, sx * 15 + 0.3, -36, -27, -16, 10, "rubber", **raked(A, gp))             # thumb scallop
    guard(body, -70, -22, -24, -55, P, w=9, th=4, style="hook")
    grip_frame(body, gp, A, 15, -125, -24, 28, P, hump=3.0, front="finger")
    grip_panels(body, gp, A, 15, -116, -40, -17, 22, P, style="stipple", proud=0.5, screws=False)
    r = raked(A, gp)
    for i in range(5):                                                           # strap texture squares
        y = -112 + i * 15
        body.box(-9, 9, y, y + 8, -24.5, -24, P, **r)
        body.box(-9, 9, y, y + 8, 28, 28.5, P, **r)
    body.box(-3, 3, -124, -112, 28, 31, P, **r)                                  # lanyard hole plug
    pins(body, 12.4, [(-15, -38), (-12.5, -47)], d=4, mat="steel_dark")
    pins(body, 15, [(-36, 34)], d=4, mat="polymer_grey")
    control(body, "slide_stop", (-12.6, -11, -30),
            [(-13.6, -12.4, -12.6, -10, -44, -22, "steel_dark"), (-14.6, -12.4, -12.6, -8.6, -26, -18, "steel_dark")],
            press=(0, 2.4, 0))
    control(body, "mag_release", (-15, -37, -17),
            [(-16.4, -14.6, -41, -33, -22, -12, P), (-16.8, -16.4, -40, -34, -21, -13, "polymer_grey")],
            press=(1.6, 0, 0))
    trigger(body, (0, -26, -40), mat=P, length=22, safety_blade=True)
    barrel_assy(body, -149.6, -30, d=14, rod_y=-6.2)
    # slide
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide_shell(slide, -150, 36, -9.5, 12.5, 12.75, SL, ch=2.6)
    slide.box(-12.75, 12.75, -9.5, -6, -150, -146, SL)                           # nose
    for sx in (-1, 1):                                                           # nose bevels
        slide.box(sx * 12.75 - 0.2, sx * 12.75 + 0.2, -9.5, 9, -150, -138, "steel")
    port(slide, 12.75, 12.5, -62, -30, 4)
    serrations(slide, 12.75, -6.5, 9.5, 0, 30, n=8, mat="rubber", proud=0.3)
    sights(slide, -146, 34, 13.1, front_h=5.0, rear_h=5.6, style="outline", mat=P, rear_w=17)
    rear_plate(slide, 36, 12.75, -9.5, 12.5, mat=P)
    muzzle_face(slide, -150, 14, 0, rod_y=-6.2)
    pistol_mag(m, gp, A, -18, -131, -18, 14, 22, base_mat=P, holes=6)
    add_arms(m, right_hand=(6, -66, 20), left_hand=(-14, -70, 10), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -152), optic=(0, 13.2, 0), under=(0, -29, -115), eject=(13, 10, -46),
                sight=(0, 18.7, 34))
    _regrip(m, -14, -80)
    anims = _auto_anims(m, A, TRAVEL, (9, 0.5, 1.5), 14, release="overhand")
    return GunAsset(m, anims, PISTOL_FP)


def _fix(cubes):
    """Mark frame pieces that stay with the slide when _regrip slides the grip assembly along the frame."""
    for c in (cubes if isinstance(cubes, list) else [cubes]):
        c.fixed = True
    return cubes


def _regrip(m, dz, z_from):
    """
    Slide the whole grip assembly (grip, guard, trigger, frame controls, magazine, hands) by dz along the frame,
    leaving the slide, barrel, hammer, sockets and the pieces marked with _fix where they are. The grip is authored
    with its web under the slide's rear; most pistols carry the slide further back over the hand than that.
    """
    stay = {"root", "gun", "slide", "bolt", "barrel", "hammer", "muzzle", "mount_optic", "mount_under", "mount_side"}
    for b in m.order:
        p, anchored = b, False
        while p:
            if p.name in stay and p.name not in ("root", "gun"):
                anchored = True
            p = p.parent
        if anchored:
            continue
        if b.name == "body":
            for c in b.cubes:
                if getattr(c, "fixed", False) or (c.z0 + c.z1) / 2 < z_from:
                    continue
                c.z0 += dz
                c.z1 += dz
                if c.pivot:
                    c.pivot = (c.pivot[0], c.pivot[1], c.pivot[2] + dz)
            continue
        if b.name in ("root", "gun"):
            continue
        b.pivot = (b.pivot[0], b.pivot[1], b.pivot[2] + dz)
        for c in b.cubes:
            c.z0 += dz
            c.z1 += dz
            if c.pivot:
                c.pivot = (c.pivot[0], c.pivot[1], c.pivot[2] + dz)


def _hands(m, gp, A, y_bot, z_f, z_b, dx=6):
    """Arms on the grip: the firing hand at mid height, the support hand wrapped just under and ahead of it."""
    from ..pistolkit import _rk
    c = _rk(gp, A, (0, (gp[1] + y_bot) / 2 + 6, (z_f + z_b) / 2))
    add_arms(m, right_hand=(dx, round(c[1]), round(c[2])), left_hand=(-14, round(c[1]) - 4, round(c[2]) - 10),
             right_rot=(34, 18, 6), left_rot=(34, -26, -6))


# =================================================================================================
# M1911A1  (216 mm long, 127 mm barrel, 139 mm tall, single stack .45)
# =================================================================================================
def m1911():
    A, TRAVEL = -18.0, (0, 0, 46)
    m = new_gun("m1911")
    body = m["body"]
    ST = "steel_parked"
    gp = (0, -18, 4)
    # frame (narrower than the slide): short dust cover, rails, tang
    body.chamfer_box(-10, 10, -22, -9, -106, -22, ST, ch=3.5, edges="bottom")
    body.box(-10, 10, -26, -9, -74, 32, ST)
    body.box(-10.4, 10.4, -11, -9, -106, 36, ST)                                  # frame rails
    guard(body, -72, -22, -22, -50, ST, w=8, th=3.6, style="round")
    grip_frame(body, gp, A, 10, -122, -22, 30, ST, hump=2.6, front="plain", back="grooves", flare=False)
    grip_panels(body, gp, A, 10, -116, -32, -18, 25, "wood", style="diamond", proud=5.0, line_mat="wood_red")
    r = raked(A, gp)
    body.box(-8, 8, -122, -70, 30, 31.2, "steel_dark", **r)                        # arched mainspring housing
    body.box(-3, 3, -128, -122, 22, 28, ST, **r)                                   # lanyard loop
    body.box(-1.6, 1.6, -127, -123.5, 21.6, 28.4, "rubber", **r)
    # grip safety with its tang (static) and the plunger tube
    body.box(-8, 8, -64, -22, 30, 33, ST, **r)
    body.box(-8.5, 8.5, -24, -13, 30, 50, ST)
    body.box(-7, 7, -21, -15, 49, 54, ST)
    body.box(-11.6, -10, -14.5, -11.5, -20, 14, ST)                                # plunger tube
    pins(body, 10, [(-17, -36), (-14, 36), (-34, 22)], d=4, mat="steel_dark")
    body.box(10, 11.2, -14, -10, -50, -44, "steel_dark")                           # slide-stop pin (right)
    control(body, "slide_stop", (-10, -12, -44),
            [(-12.4, -10, -13.6, -9.6, -50, -20, ST), (-14, -12, -14.2, -9, -27, -18, "steel_dark")],
            press=(0, 2.6, 0))
    control(body, "safety", (-10, -12, 30),
            [(-12.6, -10, -16, -9.5, 14, 33, ST), (-15, -12.4, -14, -10.5, 8, 22, ST),
             (-15.4, -15, -13.6, -10.9, 9, 21, "steel_dark")], turn=(18, 0, 0))
    control(body, "mag_release", (-10, -38, -19),
            [(-12.6, -10, -41, -35, -22.5, -16, "steel_dark"), (-13, -12.6, -40, -36, -21.5, -17, ST)],
            press=(1.6, 0, 0))
    trigger(body, (0, -27, -38), mat=ST, length=17, style="straight", w=7)
    barrel_assy(body, -157, -18, d=14.6, rod_y=-14.5, rod_len=46)
    hammer(body, (0, -8, 38), mat=ST, style="spur", cocked=30, w=7.5)
    # slide: flat sides, round top, spring tunnel under the muzzle, bushing and plug
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide_shell(slide, -154, 36, -9, 13.5, 11.7, ST, ch=4.2, rib=False)
    slide.chamfer_box(-9, 9, -21, -9, -154, -106, ST, ch=4.0, edges="bottom")       # recoil-spring tunnel
    slide.cyl((0, 0, -155.5), 21, 5, ST)                                           # barrel bushing
    slide.box(-3, 3, -14, -8, -157.5, -154, ST)                                    # bushing skirt
    slide.cyl((0, -14.5, -155), 11, 3.5, "steel")                                  # recoil spring plug
    slide.cyl((0, -14.5, -157), 5, 0.6, "rubber", sides=8)
    muzzle_face(slide, -158, 14.6, 0)
    port(slide, 11.7, 13.5, -52, -18, 5)
    serrations(slide, 11.7, -6, 11, 2, 32, n=10, mat="rubber", proud=0.3)
    sights(slide, -150, 34, 13.5, front_h=4.0, rear_h=4.6, style="plain", mat="steel_dark", rear_w=12)
    rear_plate(slide, 36, 11.7, -9, 13.5, mat="steel_dark")
    slide.cyl((6.5, 7, 36.5), 5, 1.2, "steel", sides=8)                            # extractor end
    pistol_mag(m, gp, A, -18, -127, -16, 19, 14, base_mat="steel_dark", round_d=12, round_len=32, bumper=3,
               holes=6, double=False)
    _hands(m, gp, A, -122, -22, 30)
    add_sockets(m, muzzle=(0, 0, -160), eject=(12, 12, -34), sight=(0, 18.1, 34))
    anims = _auto_anims(m, A, TRAVEL, (11, 0.6, 1.4), 16, hammer_rot=-30, rec=0.26, length=0.34)
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Beretta M9  (217 mm long, 125 mm barrel, open-top slide, slide-mounted safety)
# =================================================================================================
def m9():
    A, TRAVEL = -16.0, (0, 0, 44)
    m = new_gun("m9")
    body = m["body"]
    AL, SL = "alloy", "steel_dark"
    gp = (0, -18, 4)
    body.chamfer_box(-12, 12, -22, -9, -128, -22, AL, ch=3.0, edges="bottom")       # dust cover (no rail)
    body.box(-12, 12, -26, -9, -78, 32, AL)
    body.box(-11, 11, -22, -11, 30, 42, AL)                                        # tang
    guard(body, -76, -22, -22, -52, AL, w=8.5, th=4, style="square")
    for i in range(4):                                                             # grooved guard front
        body.box(-3.6, 3.6, -46 + i * 5, -44 + i * 5, -78.4, -77.8, "rubber")
    grip_frame(body, gp, A, 12.5, -118, -22, 30, AL, hump=2.0, front="grooves", back="grooves")
    grip_panels(body, gp, A, 12.5, -112, -32, -17, 25, "polymer", style="checker", proud=4.5)
    r = raked(A, gp)
    for sx in (-1, 1):                                                             # medallions
        xs = sorted((sx * 17, sx * 17.6))
        body.box(xs[0], xs[1], -62, -52, -1, 9, "steel", **r)
    body.box(-3, 3, -124, -118, 22, 28, AL, **r)                                   # lanyard loop
    body.box(-1.6, 1.6, -123, -119.5, 21.6, 28.4, "rubber", **r)
    pins(body, 12, [(-16, -40), (-20, 24)], d=4, mat="steel_dark")
    control(body, "slide_stop", (-12, -12, -44),
            [(-14.2, -12, -13.6, -9.8, -48, -14, SL), (-15.6, -14, -14.2, -9.2, -22, -12, SL)], press=(0, 2.6, 0))
    control(body, "takedown", (-12, -15, -96),
            [(-14.4, -12, -18.5, -11.5, -100, -92, SL), (-15.2, -14.4, -17, -13, -99, -86, SL)], turn=(-60, 0, 0))
    body.box(12, 13.6, -17, -13, -98, -94, SL)                                     # takedown button (right)
    control(body, "mag_release", (-12.5, -37, -19),
            [(-14.8, -12.5, -41, -33, -23, -14, SL), (-15.2, -14.8, -40, -34, -22, -15, AL)], press=(1.6, 0, 0))
    trigger(body, (0, -26, -44), mat=SL, length=24, w=6.5)
    b = barrel_assy(body, -159, -30, d=15, rod_y=-8.5, mat="steel_dark")
    b.box(-6, 6, -13, -6, -72, -40, "steel")                                       # locking block
    hammer(body, (0, -7, 40), mat=SL, style="ring", cocked=30, w=7)
    # open-top slide: bridge at the muzzle, two rails, rear block
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-14, 14, -9, -4.5, -152, 36, SL)
    for sx in (-1, 1):
        xs = sorted((sx * 9.6, sx * 14))
        slide.box(xs[0], xs[1], -4.5, 6.2, -138, -34, SL)                          # side rails
        slide.box(xs[0] + (0.4 if sx > 0 else 2.2), xs[1] - (2.2 if sx > 0 else 0.4), 6.2, 7.6, -138, -34, SL)
    slide.chamfer_box(-14, 14, -9, 13.5, -152, -138, SL, ch=4.0)                    # front bridge
    slide.chamfer_box(-14, 14, -9, 13.5, -36, 36, SL, ch=3.6)                       # rear block
    slide.box(-9.6, 9.6, -4.5, 13.6, -36, -33, SL)
    muzzle_face(slide, -152, 15, 0, rod_y=-8.5, rod_d=5)
    slide.box(14, 14.7, 1.5, 5.5, -34, -14, "steel")                               # extractor / chamber indicator
    slide.box(14.6, 14.9, 2.4, 4.6, -32, -26, "sight_orange")
    serrations(slide, 14, -6, 10.5, 6, 32, n=9, mat="rubber", proud=0.3)
    sights(slide, -150, 34, 13.5, front_h=4.6, rear_h=5.4, style="dot", mat=SL, rear_w=15)
    rear_plate(slide, 36, 14, -9, 13.5, mat=SL)
    sf = slide.bone("safety", pivot=(0, 3, 22))                                     # ambidextrous safety / decocker
    for sx in (-1, 1):
        xs = sorted((sx * 14, sx * 16.6))
        sf.box(xs[0], xs[1], 0.5, 5.5, 6, 25, SL)
        xs = sorted((sx * 16.6, sx * 17.2))
        sf.box(xs[0], xs[1], 1.5, 4.5, 7, 17, "steel")
        sf.box(sx * 14.3 - 0.3, sx * 14.3 + 0.3, -2.5, -0.8, 20, 24, "red" if False else "sight_orange")
    moving(m, "safety", rot=(-40, 0, 0))
    pistol_mag(m, gp, A, -18, -124, -17, 15, 20, base_mat=SL, round_d=9.6, round_len=29, holes=6)
    _hands(m, gp, A, -118, -22, 30)
    add_sockets(m, muzzle=(0, 0, -161), eject=(14, 10, -40), sight=(0, 18.9, 34))
    anims = _auto_anims(m, A, TRAVEL, (9.5, 0.4, 1.2), 14, hammer_rot=-34)
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Desert Eagle Mark XIX .50 AE  (273 mm long, 152 mm fixed barrel, 159 mm tall)
# =================================================================================================
def deagle():
    A, TRAVEL = -14.0, (0, 0, 52)
    m = new_gun("deagle")
    body = m["body"]
    ST = "steel_dark"
    gp = (0, -20, 6)
    # frame
    body.chamfer_box(-14, 14, -28, -10, -205, -22, ST, ch=3.5, edges="bottom")
    _fix(body.box(-14, 14, -30, -10, -104, 36, ST))
    _fix(body.box(-12, 12, -26, -12, 34, 46, ST))
    guard(body, -88, -22, -28, -62, ST, w=9, th=4.4, style="hook")
    grip_frame(body, gp, A, 14.5, -138, -24, 34, ST, hump=3.0, front="finger", back="plain")
    grip_panels(body, gp, A, 14.5, -132, -36, -22, 32, "rubber", style="stipple", proud=1.6, screws=True)
    pins(body, 14, [(-18, -46), (-22, 26)], d=5, mat="steel")
    control(body, "slide_stop", (-14, -13, -60),
            [(-16.4, -14, -15.5, -10.5, -66, -30, ST), (-18, -16, -16, -10, -40, -30, "steel")], press=(0, 2.6, 0))
    control(body, "takedown", (-14, -20, -110), [(-16, -14, -24, -16, -116, -104, "steel")], turn=(-50, 0, 0))
    control(body, "mag_release", (-14.5, -42, -19),
            [(-17, -14.5, -46, -38, -23, -14, "steel"), (-17.4, -17, -45, -39, -22, -15, ST)], press=(1.6, 0, 0))
    trigger(body, (0, -30, -52), mat="steel", length=26, w=7)
    hammer(body, (0, -8, 42), mat="steel", style="bobbed", cocked=30, w=8)
    # fixed barrel: trapezoid block with the integral scope rail, muzzle crown, gas tube under it
    brl = body.bone("barrel", pivot=(0, 0, -78))
    brl.chamfer_box(-13.4, 13.4, -10, 17, -230, -78, ST, ch=7.5, edges="top")
    brl.box(-5.9, 5.9, 17, 19, -226, -84, ST)
    for i in range(7):                                                             # rail cross-slots
        z = -220 + i * 20
        brl.box(-6.2, 6.2, 17.4, 19.3, z, z + 6, "rubber")
    brl.cyl((0, 1, -230.4), 20, 0.8, "steel", sides=16)
    brl.cyl((0, 1, -230.9), 13, 0.5, "rubber", sides=16)
    brl.cyl((0, -14, -150), 11, 110, "steel", sides=8)                             # gas piston tube
    # slide: rear block + two arms reaching forward under the barrel
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide_shell(slide, -78, 40, -10, 16, 15.75, ST, ch=4.0)
    for sx in (-1, 1):
        xs = sorted((sx * 13.6, sx * 15.75))
        slide.box(xs[0], xs[1], -13, -2, -200, -78, ST)
        slide.box(xs[0], xs[1], -13, -4, -206, -200, ST)
    port(slide, 15.75, 16, -72, -40, 6)
    serrations(slide, 15.75, -6, 12.5, 8, 36, n=8, mat="rubber", proud=0.3)
    sights(slide, -225, 38, 16.6, front_h=5.0, rear_h=5.6, style="plain", mat=ST, rear_w=17, front_on=brl,
           front_top=19.0)
    rear_plate(slide, 40, 15.75, -10, 16, mat=ST)
    sf = slide.bone("safety", pivot=(0, 4, 26))
    for sx in (-1, 1):
        xs = sorted((sx * 15.75, sx * 18.2))
        sf.box(xs[0], xs[1], 1.5, 6.5, 12, 30, "steel")
        xs = sorted((sx * 18.2, sx * 18.8))
        sf.box(xs[0], xs[1], 2.5, 5.5, 13, 22, ST)
    moving(m, "safety", rot=(-38, 0, 0))
    pistol_mag(m, gp, A, -20, -143, -17, 25, 16, base_mat=ST, round_d=13.9, round_len=40, bumper=4, holes=5,
               double=False)
    _hands(m, gp, A, -138, -24, 34)
    add_sockets(m, muzzle=(0, 1, -233), optic=(0, 19, -150), eject=(16, 12, -56), sight=(0, 22.2, 38))
    _regrip(m, -14, -98)
    anims = _auto_anims(m, A, TRAVEL, (20, 1.0, 3.0), 24, hammer_rot=-30, release="overhand", draw_len=0.6, rec=0.36,
                        length=0.45, reload_len=1.9, reload_empty_len=2.4)
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.09, -0.3], "rot": [0, 6, 0]}, "ads": {"dist": 0.36}})


# =================================================================================================
# Walther PPQ M2 4"  (180 mm long, 102 mm barrel, 135 mm tall)
# =================================================================================================
def ppq():
    A, TRAVEL = -17.0, (0, 0, 42)
    m = new_gun("ppq")
    body = m["body"]
    P, SL = "polymer", "steel_dark"
    gp = (0, -18, 2)
    body.chamfer_box(-12.6, 12.6, -24, -9.5, -130, -22, P, ch=2.4, edges="bottom")
    _fix(body.box(-12.6, 12.6, -27, -9.5, -84, 30, P))
    _fix(body.box(-12, 12, -23, -9.5, 28, 38, P))
    body.rail(-126, -84, -24, mat=P, side="bottom", width=20)
    guard(body, -70, -22, -24, -54, P, w=9, th=4, style="hook")
    grip_frame(body, gp, A, 15.5, -116, -24, 28, P, hump=4.5, front="finger")
    grip_panels(body, gp, A, 15.5, -108, -36, -17, 23, P, style="stipple", proud=0.6, screws=False)
    r = raked(A, gp)
    for i in range(4):                                                             # cross-directional backstrap
        y = -104 + i * 17
        body.box(-9, 9, y, y + 9, 28, 28.6, P, **r)
        body.box(-9, 9, y, y + 9, -24.6, -24, P, **r)
    pins(body, 12.6, [(-15, -40), (-13, -52), (-34, 30)], d=4, mat="steel_dark")
    for sx in (-1, 1):                                                             # takedown tabs
        body.box(sx * 12.6 - 0.4, sx * 12.6 + 0.6 * sx, -19, -15, -66, -58, SL)
    ss = body.bone("slide_stop", pivot=(0, -11, -40))                              # long ambidextrous slide stop
    for sx in (-1, 1):
        xs = sorted((sx * 12.6, sx * 13.8))
        ss.box(xs[0], xs[1], -12.8, -10, -52, -6, SL)
        xs = sorted((sx * 13.8, sx * 14.8))
        ss.box(xs[0], xs[1], -13, -8.6, -18, -6, SL)
    moving(m, "slide_stop", pos=(0, 2.4, 0))
    control(body, "mag_release", (-15.5, -37, -18),
            [(-17.2, -15.4, -42, -33, -23, -12, P), (-17.6, -17.2, -41, -34, -22, -13, "polymer_grey")],
            press=(1.6, 0, 0))
    trigger(body, (0, -26, -40), mat=P, length=22, safety_blade=True)
    barrel_assy(body, -135.6, -28, d=14, rod_y=-6.4)
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide_shell(slide, -136, 36, -9.5, 13, 13, SL, ch=3.2)
    port(slide, 13, 13, -58, -28, 4.5)
    serrations(slide, 13, -6.5, 10, 2, 32, n=6, mat="rubber", proud=0.35, slant=-12)
    serrations(slide, 13, -6.5, 10, -130, -104, n=5, mat="rubber", proud=0.35, slant=-12)
    sights(slide, -132, 34, 13.6, front_h=5.0, rear_h=5.6, style="dot", mat=P, rear_w=17)
    rear_plate(slide, 36, 13, -9.5, 13, mat=P)
    slide.box(-1.2, 1.2, 0, 3, 36.8, 37.3, "sight_orange")                         # cocking indicator
    muzzle_face(slide, -136, 14, 0, rod_y=-6.4)
    mag = pistol_mag(m, gp, A, -18, -124, -18, 14, 22, base_mat=P, holes=6)
    mag.box(-12, 12, -124, -119, -22, -18, P)                                      # finger-rest toe
    _hands(m, gp, A, -116, -24, 28)
    add_sockets(m, muzzle=(0, 0, -138), optic=(0, 13.6, 0), under=(0, -27, -105), eject=(13, 10, -34),
                sight=(0, 19.2, 34))
    _regrip(m, -12, -80)
    anims = _auto_anims(m, A, TRAVEL, (9, 0.5, 1.5), 14)
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Bersa Thunder 380  (168 mm long, 89 mm fixed barrel, 120 mm tall)
# =================================================================================================
def bersa():
    A, TRAVEL = -14.0, (0, 0, 34)
    m = new_gun("bersa")
    body = m["body"]
    AL, SL = "alloy", "steel_dark"
    gp = (0, -18, 2)
    body.chamfer_box(-11.5, 11.5, -22, -9, -110, -22, AL, ch=3.0, edges="bottom")
    _fix(body.box(-11.5, 11.5, -26, -9, -80, 28, AL))
    _fix(body.box(-10.5, 10.5, -22, -11, 26, 40, AL))                              # beavertail
    guard(body, -66, -22, -22, -50, AL, w=8, th=3.6, style="hook")
    grip_frame(body, gp, A, 11.5, -102, -22, 26, AL, hump=2.4, front="grooves", back="grooves")
    grip_panels(body, gp, A, 11.5, -96, -30, -18, 22, "polymer", style="checker", proud=4.2)
    r = raked(A, gp)
    body.box(-16.4, -15.6, -44, -34, -14, 12, "polymer", **r)                      # thumb rest (left)
    pins(body, 11.5, [(-15, -38), (-19, 22)], d=4, mat="steel_dark")
    control(body, "slide_stop", (-11.5, -12, -36),
            [(-13.4, -11.5, -13.4, -9.8, -44, -16, SL), (-14.6, -13.2, -14, -9.2, -24, -15, SL)], press=(0, 2.4, 0))
    control(body, "takedown", (11.5, -15, -62), [(11.5, 13.6, -18.5, -11.5, -68, -56, SL)], turn=(-70, 0, 0))
    control(body, "mag_release", (-11.5, -36, -18),
            [(-13.8, -11.5, -40, -32, -22, -13, SL)], press=(1.6, 0, 0))
    trigger(body, (0, -26, -40), mat=SL, length=22, w=6)
    barrel_assy(body, -121, -30, d=12.5, rod_y=None, chamber=True)
    hammer(body, (0, -7, 32), mat=SL, style="ring", cocked=30, w=6.5)
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide_shell(slide, -118, 36, -9, 12, 12.2, SL, ch=3.4, rib=False)
    slide.box(-3.4, 3.4, 12, 13.2, -116, 30, SL)                                   # sighting rib
    for i in range(10):
        slide.box(-3.6, 3.6, 13.2, 13.5, -110 + i * 13, -104 + i * 13, "rubber")
    muzzle_face(slide, -118, 12.5, 0)
    port(slide, 12.2, 12, -54, -28, 4)
    serrations(slide, 12.2, -6, 9.5, 6, 32, n=11, mat="rubber", proud=0.3)
    sights(slide, -114, 34, 13.2, front_h=4.0, rear_h=4.6, style="dot", mat=SL, rear_w=13)
    rear_plate(slide, 36, 12.2, -9, 12, mat=SL)
    sf = slide.bone("safety", pivot=(-12.2, 3, 22))                                # safety / decocker (left)
    sf.box(-14.6, -12.2, 0.5, 5.5, 8, 25, SL)
    sf.box(-15.2, -14.6, 1.5, 4.5, 9, 18, "steel")
    sf.box(-12.6, -12.2, -2.5, -0.8, 20, 24, "sight_orange")
    moving(m, "safety", rot=(-40, 0, 0))
    mag = pistol_mag(m, gp, A, -18, -106, -15, 11, 12.5, base_mat="polymer", round_d=9.5, round_len=25, holes=5,
                     double=False)
    mag.box(-11, 11, -108, -101, -28, -15, "polymer")                              # finger rest
    mag.box(-10, 10, -111, -106, -27, -19, "polymer")
    _hands(m, gp, A, -102, -22, 26)
    add_sockets(m, muzzle=(0, 0, -123), eject=(12, 10, -40), sight=(0, 17.8, 34))
    _regrip(m, -12, -76)
    anims = _auto_anims(m, A, TRAVEL, (7.5, 0.5, 1.3), 12, hammer_rot=-34)
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Ruger Mark III, 5.5" bull barrel  (248 mm long, tubular receiver, bolt with cocking ears)
# =================================================================================================
def rugermk3():
    A, TRAVEL = -30.0, (0, 0, 30)
    m = new_gun("rugermk3")
    body = m["body"]
    ST = "steel"
    gp = (0, -22, 10)
    body.cyl((0, 0, -20), 26, 100, ST)                                             # receiver tube -70 .. 30
    body.cyl((0, 0, -140), 23.5, 140, ST)                                          # bull barrel -210 .. -70
    body.cyl((0, 0, -70.5), 25, 3, "steel_dark")                                   # shoulder ring
    body.cyl((0, 0, -210.3), 19, 0.6, ST)
    body.cyl((0, 0, -210.8), 5.6, 0.5, "rubber", sides=8)                          # .22 bore
    body.box(0, 13.3, -4, 6, -44, -14, "rubber")                                   # ejection port
    body.box(-13.4, -12.6, 1, 4, -56, -18, "steel_dark")                           # loaded-chamber indicator
    body.box(-13.5, -13.2, 1.6, 3.4, -30, -20, "sight_orange")
    for z in (-50, 6):                                                             # scope-base screws
        body.box(-2, 2, 12.8, 13.3, z - 2, z + 2, "steel_dark")
    # front sight on a ramp, adjustable target rear
    body.box(-3.4, 3.4, 11.5, 14, -208, -180, ST)
    body.box(-1.4, 1.4, 14, 21, -202, -190, "steel_dark")
    body.box(-1.4, 1.4, 14, 18, -190, -184, "steel_dark")
    body.box(-8, 8, 12.6, 15, 4, 30, "steel_dark")
    body.box(-8, -2, 15, 21, 22, 30, "steel_dark")
    body.box(2, 8, 15, 21, 22, 30, "steel_dark")
    body.box(-3, 3, 15, 16.4, 8, 14, "steel")
    body.box(8, 10.4, 15.5, 19.5, 23, 28, "steel")
    # grip frame
    _fix(body.box(-8, 8, -26, -11, -96, 36, ST))
    guard(body, -62, -18, -26, -54, ST, w=7, th=3.6, style="round")
    grip_frame(body, gp, A, 8, -130, -18, 22, ST, hump=0, front="grooves", back="plain", flare=False)
    grip_panels(body, gp, A, 8, -124, -34, -15, 19, "polymer", style="checker", proud=5.0)
    r = raked(A, gp)
    for sx in (-1, 1):                                                             # medallions
        xs = sorted((sx * 13, sx * 13.6))
        body.box(xs[0], xs[1], -52, -42, -3, 7, "steel_light", **r)
    body.box(-5, 5, -126, -112, 22, 24.5, "steel_dark", **r)                       # mainspring housing latch
    pins(body, 8, [(-18, -40), (-20, 20)], d=4, mat="steel_dark")
    control(body, "safety", (-8, -30, 30), [(-10.4, -8, -34, -26, 24, 36, "steel_dark"),
                                             (-11.4, -10.4, -33, -27, 26, 34, "steel")], press=(0, 4, 0))
    control(body, "slide_stop", (-8, -30, 8), [(-10.2, -8, -33, -27, 0, 16, "steel_dark"),
                                               (-11, -10.2, -32, -28, 9, 15, "steel")], press=(0, 2.6, 0))
    control(body, "mag_release", (-8, -44, -14), [(-10.6, -8, -48, -40, -18, -9, "steel_dark")], press=(1.6, 0, 0))
    trigger(body, (0, -26, -36), mat="steel_dark", length=20, w=6)
    # bolt with ears
    bolt = m["gun"].bone("bolt", pivot=(0, 0, 0))
    bolt.cyl((0, 0, -6), 19, 72, "steel_light")
    bolt.box(11, 13.2, -3, 5, -42, -16, "steel_light")                             # bolt face in the port
    bolt.cyl((0, 0, 33), 22, 6, "steel_light")
    for sx in (-1, 1):
        xs = sorted((sx * 9, sx * 17))
        bolt.box(xs[0], xs[1], -7, 7, 30, 40, "steel_light")
        for i in range(3):
            bolt.box(sx * 17 - 0.3, sx * 17 + 0.3, -6, 6, 31.5 + i * 3, 33 + i * 3, "steel_dark")
    mag = pistol_mag(m, gp, A, -22, -136, -10, 12, 10, base_mat="steel_dark", round_d=5.7, round_len=25, bumper=4,
                     holes=0, double=False)
    mag.box(-5.3, -4.9, -124, -34, -2, 2, "rubber")                                # follower slot
    mag.box(-7.4, -5, -60, -54, -3, 3, "steel")                                    # follower button
    _hands(m, gp, A, -130, -18, 22)
    add_sockets(m, muzzle=(0, 0, -212), optic=(0, 13, -22), eject=(13, 4, -30), sight=(0, 21, 30))
    _regrip(m, -30, -72)
    anims = _auto_anims(m, A, TRAVEL, (4.5, 0.3, 0.8), 6, slide="bolt")
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# FN Five-seveN Mk2  (208 mm long, 122 mm barrel, 20-round 5.7x28)
# =================================================================================================
def fiveseven():
    A, TRAVEL = -14.0, (0, 0, 40)
    m = new_gun("fiveseven")
    body = m["body"]
    P = "polymer"
    gp = (0, -18, 2)
    body.chamfer_box(-13, 13, -24, -9, -158, -22, P, ch=2.4, edges="bottom")
    _fix(body.box(-13, 13, -27, -9, -90, 32, P))
    _fix(body.box(-12, 12, -23, -9, 30, 39, P))
    body.rail(-154, -100, -24, mat=P, side="bottom", width=20)
    guard(body, -80, -24, -24, -56, P, w=9, th=4, style="square")
    for i in range(5):                                                             # checkered guard front
        body.box(-3.8, 3.8, -50 + i * 5, -48 + i * 5, -82.4, -81.8, "rubber")
    grip_frame(body, gp, A, 13.5, -117, -24, 30, P, hump=2.0, front="checker", back="checker")
    grip_panels(body, gp, A, 13.5, -110, -34, -18, 25, P, style="checker", proud=0.6, screws=False)
    pins(body, 13, [(-15, -44), (-30, 28)], d=4, mat="steel_dark")
    sf = body.bone("safety", pivot=(0, -15, -38))                                  # ambidextrous safety over the trigger
    for sx in (-1, 1):
        xs = sorted((sx * 13, sx * 14.8))
        sf.box(xs[0], xs[1], -18, -12, -46, -30, P)
        sf.box(sx * 14.8 - 0.3, sx * 14.8 + 0.3, -17, -13, -45, -39, "sight_orange")
    moving(m, "safety", rot=(-24, 0, 0))
    control(body, "slide_stop", (-13, -11, -18),
            [(-14.4, -13, -13, -9.6, -30, -4, P), (-15.4, -14.4, -13.4, -9, -14, -5, P)], press=(0, 2.4, 0))
    control(body, "takedown", (-13, -17, -86), [(-14.6, -13, -20, -14, -92, -80, P)], press=(0, 0, 4))
    control(body, "mag_release", (-13.5, -37, -19),
            [(-15.6, -13.5, -42, -33, -24, -13, P)], press=(1.6, 0, 0))
    trigger(body, (0, -26, -44), mat=P, length=24)
    barrel_assy(body, -165.6, -22, d=13, rod_y=-6.5)
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide_shell(slide, -166, 36, -9, 13, 13.5, P, ch=3.4)
    slide.box(-13.7, 13.7, -9, -4.5, -164, 34, "steel_dark")                        # steel slide under the cladding
    port(slide, 13.5, 13, -60, -20, 4)
    serrations(slide, 13.5, -4, 10.5, 4, 32, n=8, mat="rubber", proud=0.3)
    serrations(slide, 13.5, -4, 10.5, -160, -140, n=5, mat="rubber", proud=0.3)
    sights(slide, -162, 34, 13.6, front_h=5.6, rear_h=6.4, style="target", mat="steel_dark", rear_w=16)
    rear_plate(slide, 36, 13.5, -9, 13, mat=P)
    muzzle_face(slide, -166, 13, 0, rod_y=-6.5, rod_d=5)
    pistol_mag(m, gp, A, -18, -124, -20, 20, 20, body_mat=P, base_mat=P, round_d=7.9, round_len=40, holes=4)
    _hands(m, gp, A, -117, -24, 30)
    add_sockets(m, muzzle=(0, 0, -168), optic=(0, 13.6, 0), under=(0, -27, -128), eject=(14, 10, -34),
                sight=(0, 20, 34))
    _regrip(m, -8, -90)
    anims = _auto_anims(m, A, TRAVEL, (8, 0.5, 1.2), 12)
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# H&K USP .45  (201 mm long, 112 mm barrel, 141 mm tall)
# =================================================================================================
def usp():
    A, TRAVEL = -17.0, (0, 0, 46)
    m = new_gun("usp")
    body = m["body"]
    P, SL = "polymer", "steel_dark"
    gp = (0, -20, 4)
    body.chamfer_box(-15, 15, -27, -9, -146, -22, P, ch=2.6, edges="bottom")
    _fix(body.box(-15, 15, -29, -9, -87, 32, P))
    _fix(body.box(-13, 13, -25, -9, 30, 41, P))
    for sx in (-1, 1):                                                             # HK universal rail grooves
        body.box(sx * 15 - 0.4, sx * 15 + 0.4, -24, -21, -142, -100, "rubber")
    body.box(-12, 12, -29, -27, -142, -100, P)
    guard(body, -76, -24, -27, -60, P, w=9.5, th=4.2, style="hook")
    grip_frame(body, gp, A, 15, -122, -24, 30, P, hump=2.4, front="checker", back="checker")
    grip_panels(body, gp, A, 15, -114, -38, -18, 25, P, style="stipple", proud=0.5, screws=False)
    r = raked(A, gp)
    body.box(-3, 3, -128, -122, 22, 28, P, **r)                                    # lanyard loop
    body.box(-1.6, 1.6, -127, -123.5, 21.6, 28.4, "rubber", **r)
    pins(body, 15, [(-16, -42), (-34, 28)], d=4, mat="steel_dark")
    control(body, "slide_stop", (-15, -12, -46),
            [(-16.6, -15, -13.6, -9.8, -52, -16, SL), (-17.8, -16.4, -14.2, -9.2, -26, -16, SL)], press=(0, 2.6, 0))
    control(body, "safety", (-15, -15, 30),                                        # control lever (safety / decock)
            [(-17.4, -15, -18, -12, 6, 32, SL), (-18.6, -17.4, -17, -13, 6, 18, SL)], turn=(-24, 0, 0))
    mr = body.bone("mag_release", pivot=(0, -56, -22))                             # ambidextrous paddle
    for sx in (-1, 1):
        xs = sorted((sx * 4.8, sx * 9))
        mr.box(xs[0], xs[1], -60, -53, -30, -18, SL)
    moving(m, "mag_release", pos=(0, -2.4, 0))
    trigger(body, (0, -28, -44), mat=P, length=24)
    barrel_assy(body, -151, -24, d=15, rod_y=-7.5)
    hammer(body, (0, -8, 40), mat=SL, style="spur", cocked=28, w=7)
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide_shell(slide, -150, 36, -9, 14.5, 14.5, SL, ch=2.2)
    for sx in (-1, 1):                                                             # stepped nose
        slide.box(sx * 14.5 - 0.3, sx * 14.5 + 0.3, -9, 2, -150, -128, "steel")
    port(slide, 14.5, 14.5, -56, -22, 5)
    serrations(slide, 14.5, -5, 12, 4, 32, n=7, mat="rubber", proud=0.35)
    sights(slide, -146, 34, 15.1, front_h=5.0, rear_h=5.6, style="dot", mat=SL, rear_w=17)
    rear_plate(slide, 36, 14.5, -9, 14.5, mat=SL)
    muzzle_face(slide, -150, 15, 0, rod_y=-7.5, rod_d=6)
    pistol_mag(m, gp, A, -20, -128, -18, 20, 24, body_mat=P, base_mat=P, round_d=12, round_len=32, holes=4)
    _hands(m, gp, A, -122, -24, 30)
    add_sockets(m, muzzle=(0, 0, -153), optic=(0, 15.1, 0), under=(0, -29, -122), eject=(15, 12, -38),
                sight=(0, 20.7, 34))
    _regrip(m, -9, -84)
    anims = _auto_anims(m, A, TRAVEL, (10, 0.6, 1.4), 15, hammer_rot=-28)
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# CZ 75 SP-01  (207 mm long, 120 mm barrel, 147 mm tall; the slide rides inside the frame)
# =================================================================================================
def cz75():
    A, TRAVEL = -16.0, (0, 0, 40)
    m = new_gun("cz75")
    body = m["body"]
    ST = "steel_dark"
    gp = (0, -18, 4)
    body.chamfer_box(-14.5, 14.5, -25, 3, -150, -22, ST, ch=2.6, edges="bottom")   # full-length dust cover
    body.box(-14.5, 14.5, -27, 3, -78, 34, ST)
    body.box(-10.4, 10.4, -9, 3.4, -150, 34, "rubber")                             # slide channel
    body.rail(-146, -96, -25, mat=ST, side="bottom", width=20)
    body.chamfer_box(-11, 11, -22, -6, 32, 54, ST, ch=3, edges="bottom")           # extended beavertail
    guard(body, -76, -22, -25, -56, ST, w=8.5, th=4, style="hook")
    grip_frame(body, gp, A, 12.5, -126, -22, 30, ST, hump=2.6, front="checker", back="checker")
    grip_panels(body, gp, A, 12.5, -118, -34, -18, 25, "rubber", style="checker", proud=3.2)
    pins(body, 14.5, [(-12, -44), (-16, 26)], d=4, mat="steel")
    control(body, "slide_stop", (-14.5, -6, -44),
            [(-16.2, -14.5, -8, -4, -50, -18, "steel"), (-17.6, -16, -8.6, -3.4, -28, -18, "steel")],
            press=(0, 2.6, 0))
    sf = body.bone("safety", pivot=(0, -8, 30))                                    # ambidextrous safety
    for sx in (-1, 1):
        xs = sorted((sx * 14.5, sx * 16.6))
        sf.box(xs[0], xs[1], -11, -5, 10, 33, "steel")
        xs = sorted((sx * 16.6, sx * 18.4))
        sf.box(xs[0], xs[1], -10, -6.5, 8, 20, "steel")
    moving(m, "safety", rot=(18, 0, 0))
    control(body, "mag_release", (-12.5, -38, -19),
            [(-15.2, -12.5, -42, -34, -23, -14, "steel")], press=(1.6, 0, 0))
    trigger(body, (0, -24, -44), mat="steel", length=24, w=6.5)
    barrel_assy(body, -153, -18, d=14, y=6.0, rod_y=-2.0)
    hammer(body, (0, -4, 40), mat="steel", style="ring", cocked=30, w=7)
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-9.8, 9.8, -8, 3.2, -152, 36, ST)                                    # the part running in the frame
    slide_shell(slide, -152, 36, 3, 16, 10.5, ST, ch=2.6)
    port(slide, 10.5, 16, -48, -18, 9, bore_y=6)
    serrations(slide, 10.5, 5, 14, 6, 32, n=9, mat="rubber", proud=0.3)
    serrations(slide, 10.5, 5, 14, -146, -126, n=6, mat="rubber", proud=0.3)
    sights(slide, -148, 34, 16.6, front_h=5.4, rear_h=5.8, style="dot", mat=ST, rear_w=14, dot="sight_orange")
    rear_plate(slide, 36, 10.5, 3, 16, mat=ST)
    muzzle_face(slide, -152, 14, 6.0, rod_y=-2.0, rod_d=5)
    mag = pistol_mag(m, gp, A, -18, -132, -17, 15, 20, base_mat="rubber", round_d=9.6, round_len=29, bumper=7,
                     holes=6)
    _hands(m, gp, A, -126, -22, 30)
    add_sockets(m, muzzle=(0, 6, -155), optic=(0, 16.6, 0), under=(0, -28, -121), eject=(11, 14, -34),
                sight=(0, 22.4, 34))
    anims = _auto_anims(m, A, TRAVEL, (7.5, 0.5, 1.2), 12, hammer_rot=-30)
    return GunAsset(m, anims, PISTOL_FP)


GUNS = {"glock17": glock17, "m1911": m1911, "m9": m9, "deagle": deagle, "ppq": ppq, "bersa": bersa,
        "rugermk3": rugermk3, "fiveseven": fiveseven, "usp": usp, "cz75": cz75}
