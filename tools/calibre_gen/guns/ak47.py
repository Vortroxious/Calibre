"""AK-47 Type 3 — the original milled-receiver Kalashnikov (slab-sided wood, no slant brake, slab magazine)."""
from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, firemode)
from ..templates import rifle_reload, _settle
from ..parts import pistol_grip, trigger_group, curved_mag, barrel


def ak47():
    MAG_A = 10.0
    m = new_gun("ak47")
    body = m["body"]
    st = "steel"
    wd = "wood"
    # milled receiver: thicker walls with the long lightening cut above the magazine
    body.box(-15, 15, -36, 12, -96, 196, st)
    body.box(-15.4, 15.4, -22, -6, -60, 60, "steel_dark")                    # lightening cut (both sides)
    body.box(-15.6, -15, -20, -8, -56, 56, "rubber")
    body.box(15, 15.6, -20, -8, -56, 56, "rubber")
    body.box(-15.5, 15.5, -42, -36, -100, -40, st)                          # mag well
    body.box(-6, 6, -48, -36, -40, -34, st)
    body.box(0, 15.3, -6, 10, -50, 40, "rubber")
    # dust cover (comes off in the inspect) — its button sits at the rear
    cover = body.bone("cover", pivot=(0, 12, 196))
    cover.box(-13, 13, 12, 22, -60, 196, st)
    cover.box(-13.3, 13.3, 14, 20, 120, 190, st)
    body.box(-3, 3, 10, 18, 196, 204, "steel_light")                         # recoil spring guide button
    # trunnion, rear sight block
    body.box(-15, 15, -22, 24, -126, -96, st)
    body.box(-8, 8, 24, 36, -126, -96, st)
    body.box(-6, 6, 36, 40, -126, -100, st)
    # slab-sided furniture (no finger swells)
    body.box(-16, 16, -34, 6, -330, -126, wd)
    body.box(-13, 13, 6, 22, -310, -126, wd)
    body.cyl((0, 14, -340), 14, 40, st)
    body.box(-6, 6, -14, 30, -350, -330, st)
    body.cyl((0, -18, -410), 6, 150, "steel_light")                          # cleaning rod
    barrel(body, -330, -430, d=16)
    # front sight post, plain muzzle nut instead of the slant brake
    body.box(-8, 8, -8, 10, -420, -398, st)
    body.box(-8, -5, 10, 40, -416, -402, st)
    body.box(5, 8, 10, 40, -416, -402, st)
    body.box(-1, 1, 10, 34, -410, -408, st)
    body.cyl((0, 0, -440), 18, 20, st)
    body.box(-6, 6, -20, -10, -395, -380, st)                                # bayonet lug
    pistol_grip(body, 20, top_y=-36, length=96, width=26, depth=34, angle=-18, mat=wd, checker=False)
    trigger_group(m, body, -6, y_top=-36, guard_depth=30, guard_len=70, guard_mat=st)
    stock = m["gun"].bone("stock", pivot=(0, 0, 196))
    stock.taper(-17, 17, 196, 470, 8, -30, -36, -128, wd)                 # comb drops to the heel, toe sweeps down
    stock.box(-18.5, 18.5, -130, -28, 470, 481, st)                        # steel butt plate
    stock.box(-6, 6, -4, 10, 196, 240, st)                                   # receiver tang
    sel = body.bone("selector", pivot=(15, 4, 0))
    sel.box(15, 17, -4, 8, 0, 120, "steel")
    sel.box(15, 19, -8, 0, 110, 124, "steel")
    bolt = body.bone("bolt", pivot=(18, 2, -60))
    bolt.box(1, 13, -6, 8, -60, -14, "steel_light")
    bolt.box(14, 28, -2, 6, -64, -54, "steel_light")
    bolt.box(26, 32, -4, 8, -66, -52, "steel_light")
    bolt.box(-10, 10, 8, 12, -50, 120, "steel_light")                        # carrier top (seen with the cover off)
    mag = m["gun"].bone("magazine", pivot=(0, -42, -70))
    curved_mag(mag, -36, -100, 60, 230, curve=30, segs=6, width=26, mat="steel_dark", rib_mat=None,
               round_d=10, round_len=56)
    add_arms(m, right_hand=(8, -90, 40), left_hand=(-12, -44, -240), right_rot=(34, 14, 6), left_rot=(20, -18, -4))
    add_sockets(m, muzzle=(0, 0, -450), optic=None, under=None, side=(-16, 10, 0), eject=(15, 6, -40),
                sight=(0, 40, -110))

    def inspect():
        # press the spring-guide button, lift the top cover off, look at the carrier, drop it back and slap it home
        a = Anim(m, "inspect", 4.8)
        a.mv("gun", 0.0, 0.45, pos=(-20, -60, -260), rot=(8, -10, -18), e="inoutsine")
        a.mv("arm_left", 0.2, 0.55, pos=(14, 64, 420), rot=(-60, 10, 20))
        a.sound(0.6, "click_small")
        a.grab("arm_left", "cover", 0.62, 2.6, fade_in=0.03, fade_out=0.06)
        a.key("cover", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("cover", 0.64, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("cover", 0.8, pos=(0, 4, 2), rot=(14, 0, 0), e="outquad")
        a.sound(0.8, "dust_cover")
        a.key("cover", 1.1, pos=(-70, 50, 0), rot=(20, 0, 40), e="inoutsine")
        a.mv("gun", 1.0, 1.5, pos=(-30, -56, -250), rot=(12, -18, -30))          # look in at the carrier
        a.wave("gun", "rot", (0.5, 0.5, 0), 1.3)
        a.key("cover", 2.0, pos=(-70, 50, 0), rot=(20, 0, 40))
        a.key("cover", 2.35, pos=(0, 4, 2), rot=(10, 0, 0), e="inoutsine")
        a.key("cover", 2.5, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
        a.sound(2.5, "dust_cover")
        a.spring("gun", "rot", 2.5, (-2.0, 0, 1.0), freq=7, damp=9)
        a.mv("arm_left", 2.6, 2.75, pos=(14, 92, 380), rot=(-60, 10, 20))
        a.mv("arm_left", 2.75, 2.82, pos=(14, 80, 380), rot=(-60, 10, 20), e="inquad")   # palm-slap it seated
        a.sound(2.82, "tap")
        a.kick("gun", "pos", 2.82, (0, -4, 0), attack=0.02, recover=0.16)
        a.mv("arm_left", 2.95, 3.4, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 2.7, 3.2, pos=(-30, 24, 40), rot=(0, -30, -10))
        _settle(a, 3.4, 4.75)
        return a

    cyc = dict(bone="bolt", travel=(0, 0, 112), t_back=0.022, t_fwd=0.06)
    kk = dict(kick=(3.6, 0.6, 1.4), push=13, cycle=cyc)
    anims = [
        idle(m), draw(m, 0.72, sound="draw_rifle"),
        fire_basic(m, "fire", recover=0.15, length=0.24, **kk),
        fire_basic(m, "fire_aim", recover=0.13, length=0.22, aim=True, **kk),
        rifle_reload(m, "reload", MAG_A, empty=False, style="ak", rock=14, mag_out=70),
        rifle_reload(m, "reload_empty", MAG_A, empty=True, style="ak", rock=14, mag_out=70, bolt="bolt",
                     ch="bolt", bolt_travel=(0, 0, 112), ch_travel=(0, 0, 112), bolt_hold_open=False, ch_hand="right"),
        firemode(m, selector_rot=(-14, 0, 0)), inspect(), dry_fire(m),
    ]
    fp = {"hip": {"pos": [0.118, -0.128, -0.17], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.24}}
    return GunAsset(m, anims, fp)


GUNS = {"ak47": ak47}
