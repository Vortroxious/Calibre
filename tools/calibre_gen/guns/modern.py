"""Modern pack: Kriss Vector, H&K MP7A1, H&K G36C, FAMAS F1, IWI Tavor X95, FN Five-seveN, H&K USP, CZ 75 SP-01,
Franchi SPAS-12, Atchisson AA-12."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden)
from ..templates import rifle_reload, pistol_reload, pump_cycle, tube_reload
from ..parts import pistol_grip, trigger_group, curved_mag, straight_mag, barrel, flash_hider_a2
from .pistols import _pistol_mag, _grip, _fixed_sights
from .shotguns import _shells


def _fp(pos=(0.115, -0.12, -0.2), rot=(0, 4, 0), ads=0.2):
    return {"hip": {"pos": list(pos), "rot": list(rot)}, "ads": {"dist": ads}}


def _inspect(m):
    """Placeholder: build_assets replaces every inspect with the generated close-up one (cs2.py)."""
    return Anim(m, "inspect", 1.0)


def _flip_sights(b, z_front, z_rear, top, mat="polymer"):
    """Folding BUIS front and rear on a top rail."""
    b.box(-8, 8, top, top + 6, z_front - 10, z_front + 10, mat)
    b.box(-1.5, 1.5, top + 6, top + 24, z_front - 3, z_front + 3, mat)
    b.box(-8, 8, top, top + 6, z_rear - 10, z_rear + 10, mat)
    b.box(-8, -2, top + 6, top + 22, z_rear - 3, z_rear + 3, mat)
    b.box(2, 8, top + 6, top + 22, z_rear - 3, z_rear + 3, mat)


def _rifle_anims(m, mag_a, kick, push, style, cyc, ch=None, ch_travel=(0, 0, 70), bolt=None, bolt_travel=(0, 0, 70),
                 selector=(0, 0, 0), lock=False, mag_sound="rifle", draw_len=0.7, rec=0.13, length=0.22, rock=0.0,
                 tilt=(6, -6, -26), tilt_pos=(-20, 16, 24)):
    kk = dict(kick=kick, push=push, cycle=cyc)
    a = [idle(m), draw(m, draw_len, sound="draw_rifle"),
         fire_basic(m, "fire", recover=rec, length=length, **kk),
         fire_basic(m, "fire_aim", recover=rec * 0.85, length=length * 0.9, aim=True, **kk)]
    if lock:
        a.append(fire_basic(m, "fire_last", recover=rec, length=length, lock_back=True, **kk))
    a += [rifle_reload(m, "reload", mag_a, empty=False, style=style, mag_sound=mag_sound, rock=rock, tilt=tilt,
                       tilt_pos=tilt_pos),
          rifle_reload(m, "reload_empty", mag_a, empty=True, style=style, bolt=bolt, bolt_travel=bolt_travel, ch=ch,
                       ch_travel=ch_travel, mag_sound=mag_sound, rock=rock, tilt=tilt, tilt_pos=tilt_pos,
                       bolt_hold_open=lock)]
    if m.has("selector"):
        a.append(firemode(m, selector_rot=selector))
    a += [_inspect(m), dry_fire(m)]
    return a


def _pistol_anims(m, mag_a, travel, kick, push, hammer=None, release="thumb", draw_len=0.5):
    cyc = dict(bone="slide", travel=travel, t_back=0.022, t_fwd=0.058)
    k = dict(kick=kick, push=push, cycle=cyc, hammer=hammer)
    return [idle(m), idle(m, "idle_empty", locked={"slide": travel}),
            draw(m, draw_len, sound="draw_pistol", style="pistol"),
            fire_basic(m, "fire", recover=0.24, length=0.32, **k),
            fire_basic(m, "fire_aim", recover=0.2, length=0.28, aim=True, **k),
            fire_basic(m, "fire_last", recover=0.24, length=0.32, lock_back=True, **k),
            pistol_reload(m, "reload", mag_a, empty=False, slide_travel=travel),
            pistol_reload(m, "reload_empty", mag_a, empty=True, slide_travel=travel, release=release),
            _inspect(m), dry_fire(m)]


PISTOL_FP = {"hip": {"pos": [0.1, -0.082, -0.27], "rot": [0, 6, 0]}, "ads": {"dist": 0.34}}



def _grip_texture(body, gp, A, x, y0, y1, z0, z1, mat="polymer_grey", step=14):
    for yy in range(int(y0), int(y1), step):
        body.box(-x - 0.6, x + 0.6, yy, yy + 6, z0, z1, mat, rot=(A, 0, 0), pivot=gp)


def _usp_detail(m, body, gp, A, p="polymer"):
    slide = m["slide"]
    slide.box(1, 9, 13, 19.1, -32, 2, "steel_light")                     # barrel hood in the port
    slide.box(-7, 7, -7, 7, -187, -186, "steel_light")                    # barrel at the muzzle
    slide.box(-4, 4, -4, 4, -187.5, -187, "rubber")
    slide.box(-11, 11, 16, 17.5, -184, 40, "steel_dark")                  # top chamfer step
    slide.box(12, 12.8, 8, 13, -30, -6, "steel")                          # extractor
    slide.box(-4, 4, -4, 8, 42, 43, "rubber")                             # hammer cut-out
    for z in (-170, -156, -142, -128):                                    # universal rail grooves
        body.box(-14.3, 14.3, -26, -24, z, z + 6, "rubber")
    body.box(-4, 4, -60, -54, -58, -50, p)                                # hooked trigger guard
    body.box(-10, 10, -24, -10, -180, -176, p)                            # dust-cover lip
    body.box(-7, 7, -58, -52, -6, 4, "steel_dark")                        # paddle mag release
    body.box(-13.5, -11, -14, -8, -24, -2, "steel_dark")                  # slide stop
    _grip_texture(body, gp, A, 13, -122, -40, -4, 36)
    body.box(-5, 5, -128, -24, 40, 44, p, rot=(A, 0, 0), pivot=gp)        # backstrap
    body.box(-14.5, 14.5, -138, -132, -12, 42, p, rot=(A, 0, 0), pivot=gp)  # mag-well flare
    body.box(-3, 3, -136, -130, 34, 40, "steel", rot=(A, 0, 0), pivot=gp)   # lanyard loop


def _fiveseven_detail(m, body, gp, A, p="polymer_grey"):
    slide = m["slide"]
    slide.box(-6, 6, -6, 6, -201, -200, "steel_light")                    # barrel at the muzzle
    slide.box(-3.5, 3.5, -3.5, 3.5, -201.5, -201, "rubber")
    slide.box(1, 9, 10, 17.9, -38, -8, "steel_light")                     # barrel hood in the port
    slide.box(-11.7, 11.7, -8, -4, -198, 36, "steel_dark")                # steel lower slide under the cladding
    slide.box(11.5, 12.3, 6, 10, -34, -10, "steel")                       # extractor
    for i in range(4):                                                    # front cocking grooves
        z = -150 + i * 3.6
        for sx in (-1, 1):
            slide.box(sx * 11.7 - 0.2, sx * 11.7 + 0.2, -4, 13, z, z + 1.6, "steel_dark")
    for yy in range(-120, -50, 14):                                       # front-strap grooves
        body.box(-9, 9, yy, yy + 5, -11, -9.5, "rubber", rot=(A, 0, 0), pivot=gp)
    _grip_texture(body, gp, A, 13, -124, -40, -2, 34, mat="polymer")
    body.box(-13, 13, -30, -24, -50, -42, "steel_dark")                   # ambidextrous safety
    body.box(-13.5, -11, -14, -8, -30, -10, "steel_dark")                 # slide stop
    body.box(-13.5, -11, -40, -32, -8, 0, p)                              # mag release
    body.box(-12, -11, -20, -14, -70, -56, "steel_dark")                  # takedown lever
    body.box(-10, 10, -24, -10, -194, -190, p)                            # dust-cover lip
    body.box(-14, 14, -142, -136, -14, 40, p, rot=(A, 0, 0), pivot=gp)    # mag-well flare


def _cz75_detail(m, body, gp, A, st="steel_dark"):
    slide = m["slide"]
    slide.box(-5, 5, 1, 11, -197, -196, "steel_light")                    # barrel / bushingless muzzle
    slide.box(-3, 3, 3, 9, -197.5, -197, "rubber")
    slide.box(1, 8, 9, 17.9, -32, -2, "steel_light")                      # barrel hood in the port
    for i in range(6):                                                    # front serrations
        z = -180 + i * 3.4
        for sx in (-1, 1):
            slide.box(sx * 9.7 - 0.2, sx * 9.7 + 0.2, 5, 15, z, z + 1.5, "steel")
    slide.box(9.5, 10.3, 9, 13, -30, -6, "steel")                         # extractor
    body.box(-10, 10, -22, -14, 38, 52, st)                               # beavertail
    body.box(-13.5, -11, -12, -6, -34, -8, "steel")                       # slide stop
    body.box(11, 12.5, -10, -6, -34, -28, "steel")                        # slide-stop pin
    body.box(-11.2, 11.2, 1, 2.5, -188, 36, "rubber")                     # frame-rail line
    body.box(-13.5, -11, -34, -26, -8, 0, "steel")                        # mag release
    for yy in range(-118, -40, 10):                                       # front-strap checkering
        body.box(-8, 8, yy, yy + 4, -9.5, -8, "rubber", rot=(A, 0, 0), pivot=gp)
    body.box(-13.5, 13.5, -140, -134, -10, 42, "steel", rot=(A, 0, 0), pivot=gp)   # extended mag well
    body.box(-5, 5, -40, -24, 40, 44, st, rot=(A, 0, 0), pivot=gp)


def _famas_detail(m, body, p="polymer"):
    body.box(-14, 14, 14, 20, 210, 300, p)                                # cheek rest
    for sx in (-1, 1):                                                    # folded bipod legs
        body.box(sx * 18, sx * 21, -30, -20, -300, 0, "steel_dark")
        body.box(sx * 17, sx * 22, -34, -18, -310, -300, "rubber")
    body.cyl((0, 0, -478), 24, 6, "steel_dark")                           # grenade rings on the flash hider
    body.cyl((0, 0, -494), 24, 6, "steel_dark")
    body.box(-8, -6, 56, 78, -252, -236, p)                               # front sight wings
    body.box(6, 8, 56, 78, -252, -236, p)
    for z in range(-230, 190, 40):                                        # carry-handle slots
        body.box(-8.4, 8.4, 52, 58, z, z + 10, "rubber")
    body.box(-3, 3, 14, 15, -120, -40, "rubber")                          # charging-handle slot
    body.box(-18.4, -18, -6, 12, 120, 180, "polymer_grey")                # blanked left port
    body.box(-18.4, 18.4, -16, -14, -120, 300, "rubber")                  # receiver seam
    body.box(-3, 3, -86, -76, 334, 344, "steel")                         # sling loop
    body.box(-6, 6, -50, -44, 144, 152, "steel_dark")                     # mag release
    body.box(-17.4, 17.4, 4, 8, -320, -120, "rubber")                     # handguard top line


# =================================================================================================
# Kriss Vector .45 (Gen II SMG)
# =================================================================================================
def vector():
    m = new_gun("vector")
    body = m["body"]
    p = "polymer"
    body.box(-17, 17, -26, 20, -250, 70, p)                                   # upper receiver
    body.box(-16, 16, -62, -26, -150, 70, p)                                  # tall lower (the "Super V" block)
    body.taper(-16, 16, -250, -150, -26, -26, -34, -62, p)                    # sloped front of the lower
    body.box(0, 17.3, -6, 10, -40, 0, "rubber")                               # ejection port
    body.box(-17.5, 17.5, -44, -36, -130, 30, "polymer_grey")                 # side panels
    body.rail(-240, 66, 20, mat="alloy", side="top")
    body.rail(-240, -160, -26, mat="alloy", side="bottom")
    barrel(body, -250, -330, d=18)
    body.cyl((0, 0, -340), 22, 24, "steel_dark")                             # thread protector
    _flip_sights(body, -232, 50, 24)
    pistol_grip(body, 36, top_y=-60, length=84, width=28, depth=36, angle=-12, mat=p)
    trigger_group(m, body, -4, y_top=-62, guard_depth=26, guard_len=56, guard_mat=p)
    sel = body.bone("selector", pivot=(-17, -46, 44))
    sel.box(-20, -17, -50, -42, 38, 52, "steel")
    ch = body.bone("charging_handle", pivot=(-18, 8, -150))
    ch.box(-30, -17, 2, 12, -160, -140, "polymer_grey")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.8, -4, 8, -38, -2, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 70))
    stock.box(-15, 15, -10, 14, 70, 120, p)
    stock.cyl((0, 2, 200), 20, 170, "alloy")
    stock.taper(-18, 18, 260, 340, 16, 16, -40, -66, p)
    stock.box(-19, 19, -70, 18, 336, 348, "rubber")
    mag = m["gun"].bone("magazine", pivot=(0, -62, -110))
    straight_mag(mag, -60, -132, -92, 150, width=24, mat="polymer", base_mat="polymer_grey", round_d=11, round_len=30)
    add_arms(m, right_hand=(8, -100, 52), left_hand=(-10, -40, -200), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -352), optic=(0, 22, -60), under=(0, -28, -200), side=(-17, 6, -210),
                eject=(17, 2, -20), sight=(0, 44, 50))
    cyc = dict(bone="bolt", travel=(0, 0, 28), t_back=0.01, t_fwd=0.032)
    anims = _rifle_anims(m, 0.0, (1.8, 0.3, 0.8), 7, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 60),
                         selector=(-40, 0, 0), mag_sound="smg", rec=0.1, length=0.18)
    return GunAsset(m, anims, _fp(ads=0.16))


# =================================================================================================
# H&K MP7A1
# =================================================================================================
def mp7():
    m = new_gun("mp7")
    body = m["body"]
    p = "polymer"
    body.box(-15, 15, -22, 18, -200, 60, p)                                   # receiver
    body.box(-12, 12, 18, 24, -190, 56, p)
    body.rail(-186, 54, 24, mat="alloy", side="top")
    body.box(0, 15.3, -6, 8, -60, -20, "rubber")                              # ejection port
    barrel(body, -200, -300, d=15)
    body.cyl((0, 0, -306), 18, 14, "steel_dark")
    _flip_sights(body, -176, 40, 28)
    body.box(-14, 14, -40, -22, -200, -120, p)                                 # folding foregrip housing
    fg = body.bone("foregrip", pivot=(0, -40, -150))
    fg.box(-10, 10, -110, -40, -168, -138, p, rot=(-8, 0, 0), pivot=(0, -40, -150))
    # mag goes into the pistol grip
    gp = (0, -22, -10)
    body.box(-15, 15, -130, -22, -36, 10, p, rot=(-10, 0, 0), pivot=gp)
    trigger_group(m, body, -50, y_top=-24, guard_depth=24, guard_len=48, guard_mat=p)
    sel = body.bone("selector", pivot=(-15, -16, 10))
    sel.box(-18, -15, -20, -12, 4, 18, "steel")
    ch = body.bone("charging_handle", pivot=(0, 18, 58))
    ch.box(-14, 14, 14, 24, 56, 68, "polymer_grey")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 14.8, -4, 6, -58, -22, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 60))
    for sx in (-11, 11):
        stock.box(sx - 3, sx + 3, -10, 4, 60, 230, "steel_dark")
    stock.box(-17, 17, -60, 14, 226, 244, p)
    mag = m["gun"].bone("magazine", pivot=(0, -24, -12), rot=(-10, 0, 0))
    straight_mag(mag, -26, -28, 2, 150, width=20, mat="polymer", base_mat="polymer_grey", round_d=7, round_len=26)
    add_arms(m, right_hand=(8, -82, 0), left_hand=(-8, -84, -150), right_rot=(34, 14, 6), left_rot=(10, -18, -4))
    add_sockets(m, muzzle=(0, 0, -314), optic=(0, 26, -60), side=(-15, 4, -170), eject=(15, 0, -40),
                sight=(0, 48, 40))
    cyc = dict(bone="bolt", travel=(0, 0, 24), t_back=0.01, t_fwd=0.03)
    anims = _rifle_anims(m, -10.0, (1.6, 0.3, 0.8), 6, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 40),
                         selector=(0, 0, 0), mag_sound="pistol", rec=0.1, length=0.16, tilt=(10, -8, -24),
                         tilt_pos=(-30, 24, 30))
    return GunAsset(m, anims, _fp(pos=(0.11, -0.1, -0.22), ads=0.17))


# =================================================================================================
# H&K G36C
# =================================================================================================
def g36c():
    m = new_gun("g36c")
    body = m["body"]
    p = "polymer"
    body.box(-17, 17, -36, 18, -150, 140, p)                                   # receiver
    body.box(0, 17.3, -6, 12, -60, -10, "rubber")                             # ejection port
    body.box(-14, 14, 18, 26, -150, 120, p)                                     # carry-handle rail base
    body.rail(-146, 116, 26, mat="alloy", side="top")
    body.box(-18, 18, -40, 12, -300, -150, p)                                  # short handguard
    for z in range(-292, -158, 24):
        body.box(-18.5, 18.5, -26, -6, z, z + 12, "rubber")
    barrel(body, -300, -380, d=16)
    flash_hider_a2(body, -380, d=20, length=40)
    _flip_sights(body, -136, 104, 30)
    body.box(-15, 15, -44, -36, -110, -40, p)                                  # mag well
    pistol_grip(body, 40, top_y=-36, length=90, width=28, depth=36, angle=-16, mat=p)
    trigger_group(m, body, 4, y_top=-36, guard_depth=28, guard_len=60, guard_mat=p)
    sel = body.bone("selector", pivot=(-17, -24, 46))
    sel.box(-20, -17, -28, -20, 40, 54, "steel")
    ch = body.bone("charging_handle", pivot=(0, 22, 30))
    ch.box(-6, 6, 18, 24, 20, 100, "steel_dark")
    ch.box(-6, 30, 18, 26, 96, 106, "polymer_grey")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 16.8, -4, 10, -58, -12, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 140))
    stock.box(-15, 15, -14, 12, 140, 200, p)
    stock.taper(-16, 16, 200, 380, 10, 10, -26, -88, p)
    stock.box(-17, 17, -92, 14, 376, 388, "rubber")
    mag = m["gun"].bone("magazine", pivot=(0, -40, -76))
    curved_mag(mag, -36, -104, 52, 200, curve=18, segs=4, width=26, mat="polymer_clear", rib_mat="polymer",
               round_d=8, round_len=50)
    add_arms(m, right_hand=(8, -94, 60), left_hand=(-10, -40, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -420), optic=(0, 28, -10), under=(0, -40, -230), side=(-18, -6, -260),
                eject=(17, 2, -40), sight=(0, 52, 104))
    cyc = dict(bone="bolt", travel=(0, 0, 64), t_back=0.018, t_fwd=0.052)
    anims = _rifle_anims(m, 9.0, (2.4, 0.4, 1.0), 9, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 70),
                         bolt="bolt", bolt_travel=(0, 0, 64), selector=(-90, 0, 0))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.125, -0.19), ads=0.2))


# =================================================================================================
# FAMAS F1 (bullpup, carry handle with the sights and the charging handle under it)
# =================================================================================================
def famas():
    m = new_gun("famas")
    body = m["body"]
    p = "polymer"
    body.box(-18, 18, -44, 14, -120, 300, p)                                   # receiver / butt
    body.taper(-18, 18, 300, 360, 14, 0, -44, -96, p)                         # butt
    body.box(-19, 19, -100, 4, 356, 368, "rubber")
    body.box(-17, 17, -36, 10, -320, -120, p)                                  # handguard
    for z in range(-310, -130, 30):
        body.box(-17.4, 17.4, -28, -10, z, z + 14, "rubber")
    barrel(body, -320, -470, d=16)
    flash_hider_a2(body, -470, d=20, length=36)
    # the famous carry handle along the top
    body.box(-6, 6, 14, 56, -250, -236, p)
    body.box(-6, 6, 14, 56, 190, 204, p)
    body.box(-8, 8, 50, 62, -250, 204, p)
    body.box(-1.5, 1.5, 62, 74, -246, -240, "steel_dark")                     # front sight
    body.box(-7, 7, 62, 72, 186, 198, "steel_dark")                           # rear drum
    body.box(0, 18.3, -6, 12, 120, 180, "rubber")                             # ejection port (behind the grip)
    body.box(-9, 9, -54, -44, 0, 50, p)                                         # bipod housing
    pistol_grip(body, -60, top_y=-44, length=86, width=28, depth=34, angle=-14, mat=p)
    trigger_group(m, body, -96, y_top=-44, guard_depth=30, guard_len=90, guard_mat=p)
    sel = body.bone("selector", pivot=(0, -50, 40))
    sel.box(-6, 6, -56, -50, 34, 48, "steel")
    ch = body.bone("charging_handle", pivot=(0, 30, -60))
    ch.box(-5, 5, 18, 42, -70, -50, "steel_dark")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 18, -4, 10, 124, 176, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -44, 120))
    straight_mag(mag, -42, 100, 140, 150, width=24, mat="steel_dark", round_d=7, round_len=44)
    _famas_detail(m, body)
    add_arms(m, right_hand=(8, -100, -46), left_hand=(-10, -36, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -506), optic=(0, 62, -40), side=(-17, -10, -250), eject=(18, 4, 150),
                sight=(0, 72, 196))
    cyc = dict(bone="bolt", travel=(0, 0, 60), t_back=0.014, t_fwd=0.044)
    anims = _rifle_anims(m, 0.0, (2.2, 0.4, 1.0), 9, "ar", cyc, ch="charging_handle", ch_travel=(0, 0, 70),
                         selector=(0, 0, 90), tilt=(4, -10, -30), tilt_pos=(-30, 14, 10))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.135, -0.16), ads=0.22))


# =================================================================================================
# IWI Tavor X95 (bullpup)
# =================================================================================================
def x95():
    m = new_gun("x95")
    body = m["body"]
    p = "polymer_tan"
    body.box(-19, 19, -50, 16, -170, 290, p)                                   # body
    body.taper(-19, 19, 290, 330, 16, 6, -50, -100, p)
    body.box(-20, 20, -104, 10, 326, 340, "rubber")
    body.rail(-160, 200, 16, mat="alloy", side="top")
    body.box(-17, 17, -36, 8, -320, -170, p)                                   # handguard
    body.rail(-310, -180, -36, mat="alloy", side="bottom")
    barrel(body, -320, -400, d=16)
    flash_hider_a2(body, -400, d=20, length=40)
    _flip_sights(body, -150, 180, 20)
    body.box(0, 19.3, -6, 12, 100, 170, "rubber")                             # ejection port
    # integrated trigger guard / grip in one sweep
    body.box(-15, 15, -64, -50, -200, -40, p)
    pistol_grip(body, -60, top_y=-50, length=90, width=28, depth=36, angle=-12, mat=p)
    trigger_group(m, body, -96, y_top=-50, guard_depth=30, guard_len=90, guard_mat=p)
    sel = body.bone("selector", pivot=(-19, -40, -40))
    sel.box(-22, -19, -44, -36, -46, -32, "steel")
    ch = body.bone("charging_handle", pivot=(-19, 6, -130))
    ch.box(-32, -19, 0, 12, -140, -120, "steel_dark")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 19, -4, 10, 104, 166, "steel_light")
    mag = m["gun"].bone("magazine", pivot=(0, -50, 110))
    curved_mag(mag, -48, 90, 50, 190, curve=16, segs=4, width=26, mat="polymer", round_d=8, round_len=50)
    add_arms(m, right_hand=(8, -104, -46), left_hand=(-10, -40, -250), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -440), optic=(0, 20, 0), under=(0, -36, -250), side=(-17, -8, -260),
                eject=(19, 4, 130), sight=(0, 40, 180))
    cyc = dict(bone="bolt", travel=(0, 0, 64), t_back=0.016, t_fwd=0.05)
    anims = _rifle_anims(m, 8.0, (2.2, 0.4, 1.0), 9, "ar", cyc, ch="charging_handle", ch_travel=(0, 0, 70),
                         selector=(-60, 0, 0), tilt=(4, -10, -30), tilt_pos=(-30, 14, 10))
    return GunAsset(m, anims, _fp(pos=(0.118, -0.13, -0.16), ads=0.2))


# =================================================================================================
# FN Five-seveN
# =================================================================================================
def fiveseven():
    A = -14.0
    TRAVEL = (0, 0, 40)
    m = new_gun("fiveseven")
    body = m["body"]
    p = "polymer_grey"
    body.box(-11, 11, -24, -8, -190, 30, p)                                     # frame with a rail
    body.rail(-186, -120, -24, mat="polymer_grey", side="bottom")
    body.box(-4, 4, -52, -46, -60, -6, p)                                       # trigger guard
    body.box(-4, 4, -48, -24, -66, -60, p, rot=(14, 0, 0), pivot=(0, -24, -62))
    gp = (0, -18, 16)
    _grip(body, gp, A, 13, -136, -16, -10, 40, p)
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-11.5, 11.5, -8, 15, -200, 38, "polymer")                         # polymer-clad slide
    slide.box(-9, 9, 15, 18, -196, 30, "polymer")
    slide.box(0, 12, 6, 18, -40, -6, "rubber")
    for i in range(8):
        z = 4 + i * 3.6
        for sx in (-1, 1):
            slide.box(sx * 11.7 - 0.2, sx * 11.7 + 0.2, -4, 13, z, z + 1.6, "steel_dark")
    _fixed_sights(slide, -190, 32, 18, front_h=6, rear_h=7)
    trig = body.bone("trigger", pivot=(0, -26, -34))
    trig.box(-3.5, 3.5, -42, -24, -38, -30, p)
    _pistol_mag(m, gp, A, -16, -146, -4, 30, 15, base_mat="polymer", body_mat="steel_dark", round_d=7, round_len=36)
    _fiveseven_detail(m, body, gp, A)
    add_arms(m, right_hand=(6, -70, 34), left_hand=(-14, -74, 24), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -202), optic=(0, 18, -40), under=(0, -24, -160), eject=(12, 12, -20),
                sight=(0, 25, 30))
    return GunAsset(m, _pistol_anims(m, A, TRAVEL, (8, 0.5, 1.2), 12), PISTOL_FP)


# =================================================================================================
# H&K USP .45
# =================================================================================================
def usp():
    A = -18.0
    TRAVEL = (0, 0, 46)
    m = new_gun("usp")
    body = m["body"]
    p = "polymer"
    body.box(-11, 11, -26, -8, -176, 36, p)
    body.box(-14, 14, -28, -22, -176, -120, p)                                  # USP universal rail lugs
    body.box(-4, 4, -54, -48, -56, -4, p)
    body.box(-4, 4, -50, -26, -62, -56, p, rot=(14, 0, 0), pivot=(0, -26, -58))
    gp = (0, -20, 16)
    _grip(body, gp, A, 13, -132, -18, -8, 40, p)
    body.box(-14, -11, -20, -12, 24, 38, "steel_dark")                          # control lever
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-12, 12, -8, 16, -186, 42, "steel_dark")
    slide.box(-9, 9, 16, 19, -182, 36, "steel_dark")
    slide.box(0, 12.2, 8, 19, -34, 4, "rubber")
    for i in range(8):
        z = 8 + i * 3.6
        for sx in (-1, 1):
            slide.box(sx * 12.2 - 0.2, sx * 12.2 + 0.2, -4, 14, z, z + 1.6, "steel")
    _fixed_sights(slide, -176, 36, 19)
    ham = body.bone("hammer", pivot=(0, -4, 42))
    ham.box(-3.5, 3.5, -6, 10, 40, 46, "steel", rot=(24, 0, 0), pivot=(0, -4, 42))
    trig = body.bone("trigger", pivot=(0, -28, -30))
    trig.box(-3.5, 3.5, -44, -26, -34, -26, p)
    _pistol_mag(m, gp, A, -18, -140, -4, 32, 15, base_mat="polymer", round_d=11, round_len=30)
    _usp_detail(m, body, gp, A)
    add_arms(m, right_hand=(6, -68, 34), left_hand=(-14, -72, 24), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -188), optic=(0, 19, -40), under=(0, -28, -150), eject=(12, 12, -14),
                sight=(0, 25, 36))
    return GunAsset(m, _pistol_anims(m, A, TRAVEL, (10, 0.6, 1.4), 15, hammer=-28), PISTOL_FP)


# =================================================================================================
# CZ 75 SP-01 (the slide rides inside the frame rails)
# =================================================================================================
def cz75():
    A = -16.0
    TRAVEL = (0, 0, 40)
    m = new_gun("cz75")
    body = m["body"]
    st = "steel_dark"
    body.box(-11, 11, -24, 4, -190, 38, st)                                     # full-length frame (slide in it)
    body.rail(-186, -130, -24, mat=st, side="bottom")
    body.box(-4, 4, -52, -46, -58, -6, st)
    body.box(-4, 4, -48, -24, -64, -58, st, rot=(16, 0, 0), pivot=(0, -24, -60))
    gp = (0, -18, 18)
    _grip(body, gp, A, 12, -134, -16, -8, 40, st, panel_mat="rubber")
    sf = body.bone("safety", pivot=(-11, -10, 26))
    sf.box(-14, -11, -14, -6, 18, 32, "steel")
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-9.5, 9.5, 4, 16, -196, 40, st)                                   # slide sits low, inside the rails
    slide.box(-7, 7, 16, 18, -192, 34, st)
    slide.box(0, 10, 6, 18, -34, 0, "rubber")
    for i in range(9):
        z = 6 + i * 3.4
        for sx in (-1, 1):
            slide.box(sx * 9.7 - 0.2, sx * 9.7 + 0.2, 5, 15, z, z + 1.5, "steel")
    _fixed_sights(slide, -186, 34, 18, front_h=6, rear_h=6)
    slide.box(-1.2, 1.2, 22, 24, -184, -182, "sight_orange")                    # fibre front sight
    ham = body.bone("hammer", pivot=(0, -4, 42))
    ham.box(-3.5, 3.5, -6, 12, 40, 47, "steel", rot=(28, 0, 0), pivot=(0, -4, 42))
    trig = body.bone("trigger", pivot=(0, -26, -30))
    trig.box(-3.5, 3.5, -42, -24, -34, -26, st)
    _pistol_mag(m, gp, A, -16, -144, -2, 30, 14, round_d=9, round_len=29)
    _cz75_detail(m, body, gp, A)
    add_arms(m, right_hand=(6, -68, 34), left_hand=(-14, -72, 24), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 6, -198), optic=(0, 18, -40), under=(0, -24, -160), eject=(10, 12, -16),
                sight=(0, 24, 34))
    return GunAsset(m, _pistol_anims(m, A, TRAVEL, (7.5, 0.5, 1.2), 12, hammer=-30), PISTOL_FP)


# =================================================================================================
# Franchi SPAS-12 (pump mode)
# =================================================================================================
def spas12():
    m = new_gun("spas12")
    body = m["body"]
    st = "steel_dark"
    body.box(-18, 18, -32, 22, -110, 100, st)                                   # receiver
    body.box(0, 18.3, -6, 14, -80, -10, "rubber")
    body.box(-12, 12, -34, -32, -100, -20, "rubber")
    barrel(body, -110, -560, d=22, y=4)
    body.box(-14, 14, -4, 18, -420, -110, st)                                    # perforated heat shield
    for z in range(-410, -120, 26):
        body.box(-14.5, 14.5, 2, 12, z, z + 12, "rubber")
    body.cyl((0, -22, -320), 24, 420, st)                                        # magazine tube
    body.cyl((0, -22, -532), 28, 10, st)
    body.box(-6, 6, 18, 30, -546, -530, st)
    body.box(-6, 6, 22, 30, 60, 90, st)                                          # rear aperture
    pistol_grip(body, 110, top_y=-32, length=90, width=28, depth=36, angle=-16, mat="polymer")
    trigger_group(m, body, 30, y_top=-32, guard_depth=28, guard_len=64, guard_mat=st)
    sel = body.bone("selector", pivot=(0, -36, 70))
    sel.cyl((0, -36, 70), 8, 40, "steel", axis="x")
    stock = m["gun"].bone("stock", pivot=(0, 0, 100))                            # folding stock (folded down)
    for sx in (-12, 12):
        stock.box(sx - 3, sx + 3, -8, 2, 100, 340, "steel")
    stock.box(-14, 14, -10, 6, 330, 346, "steel")
    stock.box(-20, 20, -60, 6, 340, 352, "rubber")
    pump = m["gun"].bone("pump", pivot=(0, -22, -260))
    pump.box(-24, 24, -46, -4, -340, -180, "polymer")
    for z in range(-334, -186, 14):
        pump.box(-24.4, 24.4, -40, -10, z, z + 6, "rubber")
    pump.box(-6, -3, -14, -6, -180, -60, st)
    pump.box(3, 6, -14, -6, -180, -60, st)
    bolt = pump.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 17.8, -6, 12, -78, -20, "steel_light")
    _shells(m)
    add_arms(m, right_hand=(8, -86, 124), left_hand=(-10, -42, -260), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 4, -562), optic=(0, 26, -20), eject=(18, 4, -50), sight=(0, 30, 76))
    anims = [idle(m), draw(m, 0.8, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(8.5, 0.8, 2.0), push=25, recover=0.34, length=0.42),
             fire_basic(m, "fire_aim", kick=(8.5, 0.8, 2.0), push=25, recover=0.3, length=0.38, aim=True),
             pump_cycle(m, "cycle", travel=(0, 0, 90)), pump_cycle(m, "cycle_aim", travel=(0, 0, 90), aim=True),
             *tube_reload(m), _inspect(m), dry_fire(m)]
    apply_hidden(anims, ["shell_load", "shell_eject"])
    return GunAsset(m, anims, _fp(pos=(0.12, -0.13, -0.2), rot=(0, 3.5, 0), ads=0.13))


# =================================================================================================
# Atchisson AA-12 (box magazine, open bolt full auto)
# =================================================================================================
def aa12():
    m = new_gun("aa12")
    body = m["body"]
    st = "steel_dark"
    body.box(-22, 22, -40, 30, -260, 140, st)                                    # big square receiver tube
    body.box(-24, 24, -10, 8, -250, 130, st)                                     # ribs
    body.rail(-250, 120, 30, mat="alloy", side="top")
    body.box(0, 22.3, -6, 14, -60, 0, "rubber")
    barrel(body, -260, -470, d=24)
    body.cyl((0, 0, -476), 28, 14, st)
    body.box(-6, 6, 30, 60, -150, -140, st)                                      # carry-handle posts
    body.box(-6, 6, 30, 60, 60, 70, st)
    body.box(-8, 8, 56, 64, -150, 70, st)
    pistol_grip(body, 110, top_y=-40, length=92, width=30, depth=38, angle=-16, mat="polymer")
    trigger_group(m, body, 30, y_top=-40, guard_depth=30, guard_len=66, guard_mat=st)
    sel = body.bone("selector", pivot=(-22, -26, 80))
    sel.box(-25, -22, -30, -22, 74, 88, "steel")
    ch = body.bone("charging_handle", pivot=(-22, 14, -120))
    ch.box(-36, -22, 8, 20, -130, -110, "steel")
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(2, 22, -6, 12, -58, -2, "steel_light")
    stock = m["gun"].bone("stock", pivot=(0, 0, 140))
    stock.box(-18, 18, -20, 24, 140, 200, "polymer")
    stock.taper(-19, 19, 200, 360, 24, 18, -30, -92, "polymer")
    stock.box(-20, 20, -96, 22, 356, 368, "rubber")
    mag = m["gun"].bone("magazine", pivot=(0, -40, -100))
    mag.box(-26, 26, -150, -40, -140, -60, "polymer")                            # 8-round box
    mag.box(-27.5, 27.5, -156, -150, -142, -57, "polymer_grey")
    mag.shell12((0, -44, -86), length=64, d=19)
    add_arms(m, right_hand=(8, -100, 124), left_hand=(-10, -44, -220), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -484), optic=(0, 32, -60), eject=(22, 4, -30), sight=(0, 64, 66))
    cyc = dict(bone="bolt", travel=(0, 0, 70), t_back=0.02, t_fwd=0.07)
    anims = _rifle_anims(m, 0.0, (4.5, 0.6, 1.6), 16, "smg", cyc, ch="charging_handle", ch_travel=(0, 0, 80),
                         selector=(-40, 0, 0), rec=0.18, length=0.26, mag_sound="rifle")
    return GunAsset(m, anims, _fp(pos=(0.12, -0.14, -0.21), ads=0.15))


GUNS = {"vector": vector, "mp7": mp7, "g36c": g36c, "famas": famas, "x95": x95, "fiveseven": fiveseven,
        "usp": usp, "cz75": cz75, "spas12": spas12, "aa12": aa12}
