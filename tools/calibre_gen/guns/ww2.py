"""WWII-era service arms: Mosin-Nagant M91/30, M1917 Enfield, Arisaka Type 99, SKS, PPSh-41."""
import math

import numpy as np

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode,
                      apply_hidden)
from ..templates import (bolt_cycle, bolt_clip_load, carrier_clip_load, follow_pos, _settle, OFF_LEFT, OFF_LEFT_ROT)
from ..parts import trigger_group, barrel, pins, sling_swivel, side_swivel
from ..common import moving
from ..longkit import slot, ring_sight, eared_sight, tangent_sight, peep, aperture_sight
from ..pistolkit import control
from ..riflekit import (mil_stock, stock, line_y, butt_plate, band, handguard, receiver, stepped_barrel, bolt,
                        rides)

RIFLE_FP = {"hip": {"pos": [0.12, -0.14, -0.2], "rot": [0, 3, 0]}, "ads": {"dist": 0.42}}


# -------------------------------------------------------------------------------------------------
# shared bits
# -------------------------------------------------------------------------------------------------
def _military_bolt(m, z_front, z_rear, handle_z, handle_len=52, knob_d=17, bend=0.0, d=18.0, cock=None,
                   mat="steel_light"):
    """Rotating bolt with a handle sticking out to the right. `bend` sweeps the handle back (M1917 dog-leg)."""
    b = m["body"].bone("bolt", pivot=(0, 0, 0))
    b.cyl((0, 0, (z_front + z_rear) / 2), d, z_rear - z_front, mat)
    b.box(-3, 3, d / 2 - 1, d / 2 + 2, z_front + 8, z_rear - 24, "steel")                 # guide rib
    hp = (d / 2 - 2, 0, handle_z)
    b.box(d / 2 - 2, d / 2 + handle_len, -4, 4, handle_z - 4, handle_z + 4, mat, rot=(0, bend, -6), pivot=hp)
    kx = d / 2 + handle_len
    kz = handle_z + math.sin(math.radians(bend)) * handle_len
    b.cyl((kx - 2, -6, kz), knob_d, knob_d, mat, sides=8)                                     # bolt knob
    if cock:
        b.cyl((0, 0, z_rear + cock[1] / 2), cock[0], cock[1], "steel")                         # cocking piece
    return b


def _clip(m, guide, n=5, case_len=54, bullet_len=24, d=11.5, step=10.0):
    """Stripper clip bone (seated in the guide at rest) with a child bone of rounds."""
    gx, gy, gz = guide
    c = m["gun"].bone("clip", pivot=guide)
    c.box(gx - 7, gx + 7, gy, gy + n * step + 6, gz - 1, gz + 4, "steel")
    c.box(gx - 7, gx - 5, gy, gy + n * step + 6, gz - 5, gz + 4, "steel")
    c.box(gx + 5, gx + 7, gy, gy + n * step + 6, gz - 5, gz + 4, "steel")
    r = c.bone("clip_rounds", pivot=guide)
    L = case_len + bullet_len
    for i in range(n):
        x = gx + (1.6 if i % 2 else -1.6)
        r.round_((x, gy + 6 + i * step, gz - 2 - L / 2), L, d)
    return c


def _round_load(m, at, length, d):
    rl = m["gun"].bone("round_load", pivot=at)
    rl.round_(at, length, d)
    br = m["gun"].bone("brass", pivot=(0, 6, at[2] - 10))
    br.cyl((0, 6, at[2]), d, length * 0.65, "brass")


def _bolt_set(m, travel, handle_rot, kick, push, recover=0.45, length=0.55, cycle_len=0.85):
    return [fire_basic(m, "fire", kick=kick, push=push, recover=recover, length=length),
            fire_basic(m, "fire_aim", kick=kick, push=push, recover=recover * 0.9, length=length * 0.9, aim=True),
            bolt_cycle(m, "cycle", travel=travel, handle_rot=handle_rot, length=cycle_len),
            bolt_cycle(m, "cycle_aim", travel=travel, handle_rot=handle_rot, length=cycle_len, aim=True)]


def _disk(b, c, d, thick, mat, n=11):
    """Round disk with its axis along X (a drum magazine): a 16-sided prism."""
    return b.cyl(c, d, thick, mat, axis="x", sides=16)


def _butt(b, z0, z1, wood, plate, comb_y=-6.0, heel_drop=24.0, toe_y=-130.0, wrist_y=-64.0, w=19.0, n=9):
    """Rifle buttstock: the comb drops towards the heel and the toe line sweeps down from the wrist, as one smooth
    tapered solid, finished with a butt plate."""
    hy = comb_y - heel_drop
    b.taper(-w, w, z0, z1, comb_y, hy, wrist_y, toe_y, wood)
    b.box(-w - 0.5, w + 0.5, toe_y - 2, hy + 1, z1, z1 + 10, plate)


def _band(b, z, top=16, bot=-38, w=17, mat="steel"):
    b.box(-w, w, bot, top, z - 7, z + 7, mat)


# =================================================================================================
# Mosin-Nagant M91/30
# =================================================================================================
def mosin():
    # Mosin-Nagant M91/30: 1232 mm long, 730 mm barrel, hexagonal receiver, straight-wristed stock
    m = new_gun("mosin")
    body = m["body"]
    st, wd = "steel", "wood"
    receiver(body, -104, 96, 32, st, port=(-82, 6), ring=44, tang=(142, -12, -1), sides=8)
    body.box(-10, -7, 14, 22, 6, 16, st)                                # charger guide slots
    body.box(7, 10, 14, 22, 6, 16, st)
    stepped_barrel(body, -100, -831, 25, 17.5, st, reinforce=150, cone=60)
    tangent_sight(body, -252, -168, 11.5, st, w=13, h=9)                # notch top at 20.5
    ring_sight(body, -812, 8, st, r=7, depth=14, post_h=10.5, base_w=12)
    top, bot = mil_stock(body, wd, nose=-736, butt=(397, -36, -128), fore=(2, -28, -38), belly=-50, wrist=(-14, -60))
    handguard(body, -700, -262, 13, 2, 14, wd, caps=st)
    for z in (-700, -480):
        band(body, z, line_y(bot, z) - 0.8, 15.5, 16, st, w=10)
        body.box(15.6, 16.6, -6, -3, z - 22, z - 5, st)                 # band spring
    body.rbox(-15.6, 15.6, line_y(bot, -736) - 0.6, 3, -744, -728, st, r=4)       # nose cap
    body.cyl((0, -14, -772), 5, 92, "steel_light")                      # cleaning rod
    body.cyl((0, -14, -820), 7, 7, "steel_light", sides=8)
    for z, hw in ((-560, 15), (300, 17)):                               # sling slots with their escutcheons
        yc = (line_y(top, z) + line_y(bot, z)) / 2 + (0 if z < 0 else 4)
        for sx in (-1, 1):
            body.box(sx * hw - 0.3, sx * hw + 0.3, yc - 9, yc + 9, z - 15, z + 15, st)
            slot(body, sx * hw, yc - 6, yc + 6, z - 12, z + 12)
    # single-stack magazine housing in front of the guard, with its hinged floorplate and catch
    body.profile(-8.5, 8.5, [(-86, -48), (6, -48)], [(-86, -66), (-60, -88), (6, -92)], st)
    body.box(-9, 9, -93.5, -91, -64, 8, "steel_dark")
    body.box(-3, 3, -97, -92, -2, 8, st)
    trigger_group(m, body, 40, y_top=-50, guard_depth=24, guard_len=56, guard_mat=st)
    butt_plate(body, 397, -128, -36, 17, st)
    b = bolt(m, -70, 104, 98, d=18, handle_len=38, droop=4, knob_d=17, cock=(21, 20))
    b.cyl((0, 0, 128), 25, 8, st)                                       # knurled cocking knob
    for i in range(8):
        b.box(-12.8, 12.8, -1, 1, 124.6, 131.4, "steel_dark", rot=(0, 0, i * 22.5), pivot=(0, 0, 128))
    _clip(m, (0, 15, 12), case_len=54, bullet_len=23, d=11.5)
    _round_load(m, (0, 12, -26), 77, 11.5)
    add_arms(m, right_hand=(10, -74, 168), left_hand=(-14, -46, -330), right_rot=(30, 12, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -832), eject=(16, 10, -30), sight=(0, 19.5, -168))

    travel, hrot = (0, 0, 92), (0, 0, 84)

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             *_bolt_set(m, travel, hrot, kick=(7.5, 0.7, 1.6), push=24, cycle_len=0.9),
             *bolt_clip_load(m, travel=travel, handle_rot=hrot, push=52), Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    return GunAsset(m, anims, RIFLE_FP)


# =================================================================================================
# M1917 Enfield
# =================================================================================================
def m1917():
    # M1917 Enfield: 1175 mm long, 660 mm barrel, eared aperture sight on the bridge, dog-leg bolt handle
    m = new_gun("m1917")
    body = m["body"]
    st, wd = "steel_parked", "wood_light"
    receiver(body, -106, 104, 34, st, port=(-84, 8), ring=46, tang=(146, -12, -1))
    body.box(-10, -7, 16, 23, 8, 18, st)
    body.box(7, 10, 16, 23, 8, 18, st)
    body.rbox(-16, 16, 9, 22, 28, 74, st, r=3, edges="top")             # receiver bridge
    for sx in (-1, 1):                                                  # the protective ears
        body.rbox(sx * 16 - (4 if sx > 0 else 0), sx * 16 + (4 if sx < 0 else 0), 20, 44, 32, 72, st, r=1.8,
                  axis="x", edges="top")
    lad = body.bone("rear_sight", pivot=(0, 22, 68))
    lad.box(-5, 5, 22, 25, 34, 62, st)                                  # ladder folded forward
    peep(lad, 64, 22, 38, st, w=10, hole=4, depth=3, hole_y=31)
    stepped_barrel(body, -100, -760, 27, 17.5, st, reinforce=120, cone=60)
    eared_sight(body, -742, 8.5, 26.2, st, w=16, depth=14, lean=6)      # post top at 31
    top, bot = mil_stock(body, wd, nose=-650, butt=(411, -36, -132), fore=(2, -30, -42), belly=-56, wrist=(-14, -62),
                         grip=True)
    for sx in (-1, 1):                                                  # finger grooves
        body.box(sx * 15 - 0.2, sx * 15 + 0.2, -14, -9, -320, -220, "wood")
    handguard(body, -640, -444, 13, 2, 15, wd)
    handguard(body, -426, -128, 13, 2, 16, wd)
    band(body, -435, line_y(bot, -435) - 0.8, 17, 16, st, w=12, swivel=True)
    band(body, -628, line_y(bot, -628) - 0.8, 16.5, 16, st, w=24)
    body.box(-5, 5, line_y(bot, -628) - 10, line_y(bot, -628), -642, -616, st)        # bayonet lug
    sling_swivel(body, 0, line_y(bot, -606) - 1, -606, along="x", w=18, drop=10, mat=st)   # stacking swivel
    body.rbox(-15.6, 15.6, line_y(bot, -650) - 0.6, 3, -660, -648, st, r=4)
    body.profile(-12, 12, [(-88, -55), (8, -55)], [(-88, -60), (8, -74)], st)         # belly of the 6-round magazine
    trigger_group(m, body, 40, y_top=-56, guard_depth=24, guard_len=60, guard_mat=st)
    butt_plate(body, 411, -132, -36, 17, st)
    sling_swivel(body, 0, line_y(bot, 330), 330, along="x", w=22, drop=12, mat=st)
    control(body, "safety", (15, 0, 118), [(13, 17, -4, 6, 114, 122, "steel"), (15, 19.5, 4, 10, 106, 124, "steel")],
            turn=(-50, 0, 0))
    bolt(m, -76, 112, 100, d=18, handle_len=38, droop=22, sweep=30, knob_d=17, cock=(20, 26))
    _clip(m, (0, 17, 14), case_len=63, bullet_len=21, d=12)
    _round_load(m, (0, 12, -30), 84, 12)
    add_arms(m, right_hand=(10, -86, 148), left_hand=(-14, -48, -330), right_rot=(34, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -761), eject=(16, 10, -30), sight=(0, 31, 64))

    travel, hrot = (0, 0, 100), (0, 0, 88)

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             *_bolt_set(m, travel, hrot, kick=(8, 0.7, 1.6), push=25, cycle_len=0.88),
             *bolt_clip_load(m, travel=travel, handle_rot=hrot, push=54), Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    return GunAsset(m, anims, {"hip": RIFLE_FP["hip"], "ads": {"dist": 0.2}})


# =================================================================================================
# Arisaka Type 99
# =================================================================================================
def arisaka():
    # Arisaka Type 99: 1118 mm long, 657 mm barrel, sliding bolt cover, anti-aircraft sight arms, wire monopod
    m = new_gun("arisaka")
    body = m["body"]
    st, wd = "steel", "wood"
    receiver(body, -104, 96, 32, st, port=(-82, 8), ring=44, tang=(140, -12, -1))
    body.box(-10, -7, 15, 22, 8, 18, st)
    body.box(7, 10, 15, 22, 8, 18, st)
    stepped_barrel(body, -100, -757, 25, 17, st, reinforce=150, cone=60)
    eared_sight(body, -738, 8, 19.2, st, w=15, depth=13, lean=7)        # post top at 24.5
    tangent_sight(body, -246, -174, 11.5, st, w=12, h=13)               # notch top at 24.5
    for side, name in ((-1, "aa_left"), (1, "aa_right")):               # folding lead arms
        aa = body.bone(name, pivot=(side * 9, 17, -214))
        aa.cyl((side * 9, 17, -214), 5, 4, st, axis="y", sides=8)
        aa.box(side * 9 - 1, side * 9 + 1, 16, 18, -214, -166, st)     # folded back along the leaf
        for k in (0.4, 0.7, 1.0):
            aa.box(side * 9 - 1.6, side * 9 + 1.6, 15.4, 18.6, -214 + 47 * k - 1, -214 + 47 * k + 1, st)
    top, bot = mil_stock(body, wd, nose=-690, butt=(357, -34, -122), fore=(2, -28, -38), belly=-50, wrist=(-14, -60),
                         grip=True)
    handguard(body, -676, -262, 13, 2, 14, wd)
    band(body, -676, line_y(bot, -676) - 0.8, 15.5, 16, st, w=22)
    body.box(-5, 5, line_y(bot, -676) - 10, line_y(bot, -676), -690, -664, st)        # bayonet lug
    band(body, -470, line_y(bot, -470) - 0.8, 15.5, 16, st, w=11)
    side_swivel(body, -16, -12, -470, h=18, mat=st)
    body.rbox(-15.6, 15.6, line_y(bot, -690) - 0.6, 3, -698, -686, st, r=4)
    body.cyl((0, -14, -726), 5, 56, "steel_light")                      # cleaning rod
    mono = body.bone("monopod", pivot=(0, line_y(bot, -470) - 2, -470))
    my = line_y(bot, -470) - 3
    for sx in (-1, 1):
        mono.box(sx * 6 - 1.2, sx * 6 + 1.2, my - 2.4, my, -470, -336, "steel_light")
    mono.box(-7.2, 7.2, my - 2.4, my, -338, -334, "steel_light")
    body.box(-12, 12, -54, -50, -80, 2, st)                             # hinged floorplate
    body.box(-3, 3, -57, -53, 2, 10, st)
    trigger_group(m, body, 40, y_top=-50, guard_depth=24, guard_len=58, guard_mat=st)
    butt_plate(body, 357, -122, -34, 17, st)
    side_swivel(body, -17, -70, 290, h=18, mat=st)
    b = bolt(m, -70, 104, 96, d=18, handle_len=36, droop=2, knob_d=19, cock=(28, 16))
    for i in range(10):                                                 # knurled safety knob
        b.box(-14.4, 14.4, -1, 1, 106, 119, "steel_dark", rot=(0, 0, i * 18), pivot=(0, 0, 112))
    dc = body.bone("bolt_cover", pivot=(0, 0, 0))                       # rides with the bolt, does not turn
    dc.rbox(-15, 15, 6, 18.6, -84, 58, "steel_dark", r=7, edges="top")
    dc.box(-15.3, 15.3, 6, 8, -84, 58, "steel")
    _clip(m, (0, 15, 12), case_len=57, bullet_len=23, d=12)
    _round_load(m, (0, 12, -28), 80, 12)
    add_arms(m, right_hand=(10, -84, 150), left_hand=(-14, -46, -320), right_rot=(34, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -758), eject=(16, 10, -30), sight=(0, 24, -176))

    travel, hrot = (0, 0, 94), (0, 0, 86)

    anims = [idle(m), draw(m, 0.85, sound="draw_rifle"),
             *_bolt_set(m, travel, hrot, kick=(7.5, 0.7, 1.6), push=24, cycle_len=0.88),
             *bolt_clip_load(m, travel=travel, handle_rot=hrot, push=52), Anim(m, "inspect", 1.0), dry_fire(m)]
    follow_pos(anims, "bolt", "bolt_cover")
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    return GunAsset(m, anims, RIFLE_FP)


# =================================================================================================
# SKS (Type 45 pattern, folding blade bayonet)
# =================================================================================================
def sks():
    # SKS: 1020 mm long, 520 mm barrel, fixed 10-round magazine, folding blade bayonet
    m = new_gun("sks")
    body = m["body"]
    st, wd = "steel", "wood_red"
    body.rbox(-14, 14, -30, 12, -100, 150, st, r=3, edges="bottom")     # milled receiver
    body.rbox(-12.5, 12.5, 12, 25, -6, 172, st, r=6.5, edges="top")     # receiver cover
    body.box(-13, 13, 12, 26, 164, 172, st)
    body.cyl((13.4, 18, 156), 7, 1.2, "steel", axis="x", sides=8)       # cover pin lever
    body.box(13, 16, 15, 21, 140, 158, st)
    body.box(8, 14.4, 5, 12, -66, -6, "rubber")                         # ejection port
    pins(body, 14, [(-18, -80), (-20, 110)], d=4.5, mat="steel")
    body.cyl((0, 0, -125), 22, 52, st)
    barrel(body, -148, -620, d=16)
    body.rbox(-8, 8, -9, 30, -362, -340, st, r=3, edges="top")          # gas block
    body.cyl((0, 20, -226), 13, 230, st)                                # gas tube
    body.rbox(-13, 13, 6, 31, -332, -152, wd, r=7, edges="top")         # hand guard over the gas tube
    for z in (-332, -152):
        body.rbox(-13.5, 13.5, 6, 31.5, z - 3, z + 3, st, r=7, edges="top")
    body.rbox(-11, 11, 9, 30, -150, -104, st, r=3, edges="top")         # rear sight base
    tangent_sight(body, -148, -70, 30, st, w=12, h=10)                  # notch top at 40
    body.rbox(-6, 6, 6, 27, -602, -578, st, r=2.5, edges="top")         # front sight tower
    ring_sight(body, -590, 26, st, r=7.5, depth=14, post_h=12, base_w=12)
    top, bot = mil_stock(body, wd, nose=-340, butt=(396, -36, -128), action=(-100, 140), fore=(6, -30, -36),
                         belly=-46, wrist=(-14, -58), grip=True, hw=(16, 17, 15, 17), bottom_at=70)
    band(body, -334, -31, 8, 17, st, w=12, swivel=True)
    body.cyl((0, -11, -470), 4.5, 250, "steel_light")                   # cleaning rod
    body.profile(-12, 12, [(-92, -44), (-8, -44)], [(-92, -74), (-62, -90), (-8, -84)], st)   # fixed magazine
    body.box(-12.5, 12.5, -72, -70, -90, -10, "steel_dark")
    body.box(-3, 3, -62, -46, -8, -2, st)                               # magazine latch
    trigger_group(m, body, 26, y_top=-46, guard_depth=26, guard_len=60, guard_mat=st)
    control(body, "safety", (6, -48, 56), [(4, 8, -64, -48, 53.5, 57.5, "steel")], turn=(40, 0, 0))
    butt_plate(body, 396, -128, -36, 17, st)
    body.cyl((0, -60, 400.3), 14, 0.6, "steel_dark", sides=16)          # trap for the cleaning kit
    side_swivel(body, -17, -78, 300, h=18, mat=st)
    # carrier with the charger guide and right-hand handle
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.rbox(-10.5, 10.5, 0, 14, -70, -6, "steel_light", r=4, edges="top")
    bolt.box(-9, -5.5, 14, 18, -22, -8, "steel_light")                  # charger guide
    bolt.box(5.5, 9, 14, 18, -22, -8, "steel_light")
    bolt.box(-6, 6, 13.6, 14.4, -64, -30, "steel_dark")
    bolt.box(10, 24, 2, 9, -46, -36, "steel_light")
    bolt.cyl((28, 5.5, -41), 13, 10, "steel_light", axis="x", sides=16)
    # folding blade bayonet, hinged under the muzzle and lying back in the fore-end
    bay = body.bone("bayonet", pivot=(0, -14, -524))
    bay.rbox(-7, 7, -22, 9, -532, -516, st, r=3)
    bay.box(-1.6, 1.6, -27, -15, -516, -300, "steel_light")
    bay.box(-2.4, 2.4, -24, -18, -516, -470, st)
    _clip(m, (0, 13, -14), n=10, case_len=39, bullet_len=17, d=11, step=5.0)
    _round_load(m, (0, 10, -40), 56, 11)
    add_arms(m, right_hand=(8, -82, 170), left_hand=(-14, -40, -280), right_rot=(34, 14, 6),
             left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -621), eject=(15, 6, -30), sight=(0, 39.5, -72))

    travel = (0, 0, 100)

    cyc = dict(bone="bolt", travel=travel, t_back=0.024, t_fwd=0.07)
    kk = dict(kick=(4.2, 0.6, 1.4), push=16, cycle=cyc)
    anims = [idle(m), draw(m, 0.75, sound="draw_rifle"),
             fire_basic(m, "fire", recover=0.2, length=0.3, **kk),
             fire_basic(m, "fire_aim", recover=0.18, length=0.28, aim=True, **kk),
             *carrier_clip_load(m, travel=travel, push=40), Anim(m, "inspect", 1.0), dry_fire(m)]
    apply_hidden(anims, ["round_load", "brass", "clip", "clip_rounds"])
    return GunAsset(m, anims, {"hip": RIFLE_FP["hip"], "ads": {"dist": 0.38}})


# =================================================================================================
# PPSh-41 with the 71-round drum
# =================================================================================================
def ppsh41():
    m = new_gun("ppsh41")
    body = m["body"]
    st = "steel_dark"
    wd = "wood"
    body.box(-15, 15, -24, 18, -110, 120, st)                              # receiver
    body.box(-12, 12, 18, 22, -60, 110, st)
    body.box(14.6, 15.4, 0, 10, -40, 60, "rubber")                       # charging slot
    body.box(-6, 6, 22, 30, 50, 70, st)                                    # L-flip rear sight
    body.box(-5, 5, 30, 32, 60, 66, st)
    body.box(-5, -1.4, 32, 37, 60, 66, st)
    body.box(1.4, 5, 32, 37, 60, 66, st)
    # ventilated barrel jacket with the slanted muzzle brake
    body.cyl((0, 0, -250), 30, 280, st, sides=8)                           # -110 .. -390
    for z in range(-380, -130, 32):
        for y in (8, -8):
            body.box(-15.4, 15.4, y - 4, y + 4, z, z + 16, "rubber")
        body.box(-6, 6, 14.6, 15.4, z, z + 16, "rubber")
    barrel(body, -110, -385, d=14, mat="steel_light")
    body.box(-15, 15, -15, 15, -420, -390, st, rot=(-30, 0, 0), pivot=(0, 15, -390))   # slanted brake
    body.box(-5, -3, 15, 38, -404, -392, st)                                # front sight hood
    body.box(3, 5, 15, 38, -404, -392, st)
    body.box(-5, 5, 36, 38, -404, -392, st)
    body.box(-1, 1, 15, 33, -398, -396, st)
    # wood stock: receiver bed, drum cut, wrist, butt
    body.box(-17, 17, -46, -8, -110, -40, wd)
    body.box(-17, 17, -46, -8, 30, 150, wd)
    body.box(-15, 15, -64, -12, 140, 236, wd, rot=(5, 0, 0), pivot=(0, -12, 140))
    _butt(body, 232, 450, wd, st, comb_y=-18, heel_drop=18, toe_y=-124, wrist_y=-68, w=18)

    body.box(-8, 8, -40, -24, -40, 30, st)                                 # mag housing / catch
    trigger_group(m, body, 70, y_top=-46, guard_depth=26, guard_len=58, guard_mat=st)
    sel = body.bone("selector", pivot=(0, -52, 40))
    sel.box(-3, 3, -58, -48, 38, 46, "steel")                              # fire selector inside the guard
    bolt = body.bone("bolt", pivot=(0, 0, 0))
    bolt.box(-10, 10, -10, 12, -40, 70, "steel_light")
    ch = bolt.bone("charging_handle", pivot=(15, 5, 40))
    ch.box(15, 28, 0, 10, 34, 46, "steel_light")
    ch.box(26, 30, -2, 12, 32, 48, "steel_light")
    # 71-round drum
    dc = (0, -118, -6)
    mag = m["gun"].bone("magazine", pivot=(0, -30, -6))
    mag.box(-8, 8, -42, -24, -30, 18, st)                                 # feed tower
    _disk(mag, dc, 192, 42, st, n=13)
    _disk(mag, (dc[0] + 22.5, dc[1], dc[2]), 176, 3, "steel", n=11)                    # lid
    _disk(mag, (dc[0] - 22.5, dc[1], dc[2]), 176, 3, "steel", n=11)
    for i in range(12):                                                    # lid ribs
        a = math.radians(i * 30)
        mag.box(22, 25, dc[1] + math.sin(a) * 72 - 4, dc[1] + math.sin(a) * 70 + 4,
                dc[2] + math.cos(a) * 72 - 4, dc[2] + math.cos(a) * 72 + 4, st)
    key = mag.bone("drum_key", pivot=(dc[0] + 26, dc[1], dc[2]))
    key.box(24, 30, dc[1] - 6, dc[1] + 6, dc[2] - 6, dc[2] + 6, "steel_light")
    key.box(28, 32, dc[1] - 22, dc[1] + 22, dc[2] - 4, dc[2] + 4, "steel_light")
    add_arms(m, right_hand=(8, -66, 170), left_hand=(-14, -60, -210), right_rot=(30, 12, 6),
             left_rot=(24, -18, -4))
    add_sockets(m, muzzle=(0, 0, -420), eject=(15, 10, -30), sight=(0, 33, 62))
    travel = (0, 0, 92)

    def reload(name, empty):
        L = 3.3 if empty else 3.0
        a = Anim(m, name, L)
        if empty:
            a.key("bolt", 0.0, pos=(0, 0, 0))
        a.mv("gun", 0.0, 0.35, pos=(-30, 30, 30), rot=(6, -14, -30))
        # left hand grabs the drum, thumb on the catch, pull it forward off the housing
        a.mv("arm_left", 0.05, 0.36, pos=(-20, -60, 150), rot=(10, 10, 20))
        a.grab("arm_left", "magazine", 0.38, 1.1, fade_in=0.04, fade_out=0.06)
        a.key("magazine", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("magazine", 0.4, pos=(0, 0, 0), rot=(0, 0, 0))
        a.sound(0.42, "drum_out")
        a.key("magazine", 0.5, pos=(0, -4, -14), rot=(4, 0, 0), e="outquad")
        a.key("magazine", 0.68, pos=(0, -60, -40), rot=(16, 0, 10), e="inoutsine")
        a.spring("gun", "rot", 0.45, (-2.0, 0, 1.4), freq=5, damp=8)
        a.kick("gun", "pos", 0.5, (0, 10, 0), attack=0.05, recover=0.3)           # the gun gets lighter
        a.key("magazine", 1.1, pos=(-60, -360, 120), rot=(40, 0, 30), e="inoutsine")
        a.mv("arm_left", 1.1, 1.35, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
        a.sound(1.3, "pouch")
        a.at_hand("magazine", 1.36, grip=(0, 60, -10), rot=(40, 0, 30))
        a.grab("arm_left", "magazine", 1.4, 2.2, fade_in=0.06, fade_out=0.06)
        a.key("magazine", 1.85, pos=(0, -50, -30), rot=(14, 0, 8), e="outcubic")
        a.key("magazine", 2.0, pos=(0, -10, -4), rot=(3, 0, 0), e="inoutsine")
        a.key("magazine", 2.1, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")         # heel of the hand drives it home
        a.sound(2.1, "drum_in")
        a.event(2.1, "ammo")
        a.spring("gun", "rot", 2.1, (-3.0, 0, 1.6), freq=5, damp=8)
        a.kick("gun", "pos", 2.1, (0, -10, 0), attack=0.03, recover=0.25)
        t = 2.25
        if empty:
            # cock the bolt with the right-hand handle
            a.mv("arm_left", t, t + 0.3, pos=(0, 0, 0), rot=(0, 0, 0))
            a.mv("arm_right", t, t + 0.16, pos=(24, 70, -110), rot=(-30, -20, -20))
            a.grab("arm_right", "charging_handle", t + 0.16, t + 0.42, fade_in=0.02, fade_out=0.05)
            a.key("bolt", t + 0.16, pos=(0, 0, 0))
            a.key("bolt", t + 0.32, pos=travel, e="inoutquad")
            a.sound(t + 0.3, "charging_handle_back")
            a.spring("gun", "rot", t + 0.32, (1.4, 0, -1.4), freq=6, damp=8)
            a.mv("arm_right", t + 0.45, t + 0.7, pos=(0, 0, 0), rot=(0, 0, 0))
            _settle(a, t + 0.45, L - 0.02)
        else:
            a.mv("arm_left", t, t + 0.4, pos=(0, 0, 0), rot=(0, 0, 0))
            _settle(a, t + 0.05, L - 0.02)
        return a

    def inspect():
        # roll it over to show the drum, crank the winding key (ratchet clicks), then look down the jacket
        a = Anim(m, "inspect", 4.8)
        a.mv("gun", 0.0, 0.45, pos=(-40, 30, 30), rot=(10, 30, 50), e="inoutsine")
        a.mv("arm_left", 0.2, 0.55, pos=(30, -90, 140), rot=(0, 40, 40))
        a.key("drum_key", 0.0, rot=(0, 0, 0))
        a.key("drum_key", 0.6, rot=(0, 0, 0))
        for i in range(4):
            t = 0.7 + i * 0.32
            a.key("drum_key", t + 0.2, rot=(-(i + 1) * 80, 0, 0), e="inoutsine")
            a.sound(t + 0.08, "click_small")
            a.sound(t + 0.16, "click_small")
            a.spring("gun", "rot", t + 0.1, (0, 0.4, 0.6), freq=8, damp=12)
        a.mv("arm_left", 2.0, 2.35, pos=(0, 0, 0), rot=(0, 0, 0))
        # sight down the perforated jacket, then flip the L rear sight
        a.mv("gun", 2.0, 2.6, pos=(-20, -40, -40), rot=(-10, -6, -4), e="inoutsine")
        a.sound(2.7, "click_small")
        a.mv("arm_right", 2.7, 2.9, pos=(-6, 20, -20), rot=(-10, -10, 0))
        a.sound(3.0, "selector")
        a.key("selector", 0.0, pos=(0, 0, 0))
        a.key("selector", 2.95, pos=(0, 0, 0))
        a.key("selector", 3.02, pos=(0, 0, -6), e="outquad")
        a.key("selector", 3.3, pos=(0, 0, -6))
        a.key("selector", 3.37, pos=(0, 0, 0), e="outquad")
        a.sound(3.37, "selector")
        a.mv("arm_right", 3.45, 3.7, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.5, 4.75)
        return a

    cyc = dict(bone="bolt", travel=travel, t_back=0.018, t_fwd=0.045)
    kk = dict(kick=(2.0, 0.6, 1.2), push=9, cycle=cyc)
    fm = Anim(m, "firemode", 0.55)
    fm.mv("gun", 0.0, 0.14, rot=(4, -4, 10), pos=(-4, 3, 4))
    fm.mv("arm_right", 0.04, 0.18, pos=(-2, 10, -36), rot=(0, -6, 4))
    fm.key("selector", 0.0, pos=(0, 0, 0))
    fm.key("selector", 0.2, pos=(0, 0, 0))
    fm.key("selector", 0.25, pos=(0, 0, -6), e="outquad")
    fm.key("selector", 0.55, pos=(0, 0, -6))
    fm.sound(0.23, "selector")
    fm.mv("arm_right", 0.28, 0.45, pos=(0, 0, 0), rot=(0, 0, 0))
    fm.mv("gun", 0.26, 0.55, rot=(0, 0, 0), pos=(0, 0, 0))
    anims = [idle(m), draw(m, 0.7, sound="draw_rifle"),
             fire_basic(m, "fire", recover=0.09, length=0.14, **kk),
             fire_basic(m, "fire_aim", recover=0.08, length=0.13, aim=True, **kk),
             reload("reload", False), reload("reload_empty", True), fm, inspect(), dry_fire(m)]
    return GunAsset(m, anims, {"hip": {"pos": [0.115, -0.12, -0.2], "rot": [0, 4, 0]}, "ads": {"dist": 0.26}})


GUNS = {"mosin": mosin, "m1917": m1917, "arisaka": arisaka, "sks": sks, "ppsh41": ppsh41}
