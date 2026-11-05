"""FN M249 SAW and Kalashnikov PKM - belt fed from ammo boxes."""
from ..core import Anim
from ..common import GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden
from ..templates import belt_reload, _settle
from ..parts import pistol_grip, trigger_group, barrel, flash_hider_a2, bipod

LMG_FP = {"hip": {"pos": [0.13, -0.15, -0.2], "rot": [0, 3.5, 0]}, "ads": {"dist": 0.1}}


def _belt(bone, x0, y0, z, n=8, dx=-7.0, dy=-9.0, case="brass", tip="copper", d=8.0, length=56.0):
    """A dangling belt: n rounds stepping from the feed tray down to the box."""
    for i in range(n):
        x = x0 + dx * i
        y = y0 + dy * i
        bone.round_((x, y, z), length, d, case=case, tip=tip)
        bone.box(x - 3, x + 3, y - d / 2 - 1, y + d / 2 + 1, z + length * 0.15, z + length * 0.3, "steel_dark")


def m249():
    m = new_gun("m249")
    body = m["body"]
    st = "steel_dark"
    body.box(-22, 22, -40, 12, -160, 130, st)                                      # receiver
    body.box(-22, 22, 12, 22, 40, 130, st)
    body.box(0, 22.3, -30, -10, -80, -20, "rubber")                                # ejection port (bottom right)
    body.box(-30, -22, -10, 8, -150, -90, st)                                     # feed tray guide (left)
    pistol_grip(body, 60, top_y=-40, length=96, width=28, depth=38, angle=-18, mat="polymer")
    trigger_group(m, body, 20, y_top=-40, guard_depth=28, guard_len=70, guard_mat=st)
    sel = body.bone("selector", pivot=(0, -40, 50))
    sel.cyl((0, -40, 50), 8, 50, "steel", axis="x")
    # barrel, heat shield, carry handle, gas block, bipod
    barrel(body, -160, -620, d=20)
    body.box(-14, 14, 14, 22, -340, -160, "steel")                                # heat shield
    body.box(-6, 6, 22, 60, -260, -250, "steel")                                  # carry handle
    body.box(-6, 6, 52, 62, -260, -170, "polymer")
    body.box(-6, 6, 22, 60, -180, -170, "steel")
    body.box(-12, 12, -26, -6, -420, -380, st)
    bipod(body, -440, y=-26, legs_len=220, folded=True)
    flash_hider_a2(body, -620, d=22, length=50)
    body.box(-8, 8, 12, 36, -600, -590, st)                                       # front sight
    # polymer handguard under the receiver front
    body.box(-24, 24, -70, -40, -160, -60, "polymer")
    # stock
    stock = m["gun"].bone("stock", pivot=(0, 0, 130))
    stock.taper(-19, 19, 130, 418, 12, 10, -56, -102, "polymer")
    stock.box(-21, 21, -106, 14, 416, 430, "rubber")
    # feed cover hinged at the rear (front lifts)
    cover = body.bone("cover", pivot=(0, 22, 40))
    cover.box(-21, 21, 12, 30, -150, 40, st)
    cover.box(-8, 8, 30, 36, -30, 30, st)                                         # rear sight
    cover.rail(-140, 20, 30, mat="alloy")
    # charging handle (right side)
    ch = body.bone("charging_handle", pivot=(22, -10, -120))
    ch.box(22, 36, -14, -4, -126, -114, "steel")
    ch.box(32, 40, -18, 0, -128, -112, "polymer")
    # ammo box (200 rd) on the left underside + belt
    box = m["gun"].bone("box", pivot=(-14, -40, -70))
    box.box(-46, 18, -150, -40, -130, -20, "polymer_od")
    box.box(-44, 16, -152, -150, -128, -22, "canvas")
    box.box(-48, -46, -120, -60, -110, -40, "canvas")
    belt = m["gun"].bone("belt", pivot=(-24, -4, -110))
    _belt(belt, -22, -2, -130, n=6, dx=-5, dy=-7)
    add_arms(m, right_hand=(8, -96, 82), left_hand=(-10, -70, -110), right_rot=(34, 14, 6), left_rot=(30, -18, -4))
    add_sockets(m, muzzle=(0, 0, -670), optic=(0, 33, -60), under=None, eject=(10, -32, -50), sight=(0, 36, 30))

    def inspect():
        a = Anim(m, "inspect", 4.4)
        a.mv("gun", 0.0, 0.45, pos=(-30, 20, 40), rot=(8, -12, 24))
        a.mv("arm_left", 0.1, 0.45, pos=(40, 120, 150), rot=(-40, 10, 20))
        a.grab("arm_left", "cover", 0.48, 2.6, fade_in=0.03, fade_out=0.06)
        a.key("cover", 0.0, rot=(0, 0, 0))
        a.key("cover", 0.5, rot=(0, 0, 0))
        a.key("cover", 0.56, rot=(3, 0, 0), e="outquad")
        a.sound(0.54, "cover_open")
        a.key("cover", 0.9, rot=(62, 0, 0), e="outback")
        a.mv("gun", 0.9, 1.4, pos=(-40, 30, 50), rot=(18, -16, 34))              # look at the belt on the tray
        a.wave("gun", "rot", (0.5, 0.5, 0.3), 1.4)
        a.shake("belt", "rot", 1.2, 1.9, (0, 0, 4), freq=7, seed=2)
        a.sound(1.4, "belt_rattle")
        a.key("cover", 2.3, rot=(62, 0, 0))
        a.key("cover", 2.5, rot=(0, 0, 0), e="inquad")
        a.sound(2.5, "cover_close")
        a.spring("gun", "rot", 2.5, (-2.4, 0, 1.2), freq=6, damp=8)
        a.mv("arm_left", 2.65, 3.1, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.0, 4.35)
        return a

    anims = [idle(m), draw(m, 0.95, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(2.8, 0.6, 1.2), push=12, recover=0.12, length=0.2),
             fire_basic(m, "fire_aim", kick=(2.8, 0.6, 1.2), push=12, recover=0.1, length=0.18, aim=True),
             belt_reload(m, "reload", False, cover_rot=(75, 0, 0)),
             belt_reload(m, "reload_empty", True, cover_rot=(75, 0, 0), ch_travel=(0, 0, 110)),
             inspect(), dry_fire(m)]
    return GunAsset(m, anims, LMG_FP)


def pkm():
    m = new_gun("pkm")
    body = m["body"]
    st = "steel_dark"
    body.box(-20, 20, -40, 14, -160, 150, st)
    for z in range(-150, 140, 40):
        body.box(-20.3, 20.3, -30, 4, z, z + 14, "steel")
    body.box(0, 20.3, -30, -10, -60, -10, "rubber")
    body.box(18, 30, -16, 6, -150, -100, st)                                       # feed (right side)
    pistol_grip(body, 50, top_y=-40, length=92, width=26, depth=34, angle=-18, mat="polymer")
    trigger_group(m, body, 10, y_top=-40, guard_depth=28, guard_len=70, guard_mat=st)
    sel = body.bone("selector", pivot=(-20, -30, 50))
    sel.box(-24, -20, -34, -26, 40, 60, "steel")
    barrel(body, -160, -620, d=20)
    for z in range(-560, -200, 40):
        body.box(-11, 11, -11, 11, z, z + 8, "steel")                               # fluted barrel look
    body.box(-6, 6, 20, 50, -240, -230, "steel")                                   # carry handle
    body.box(-6, 6, 44, 54, -240, -170, "wood_red")
    body.box(-6, 6, 20, 50, -180, -170, "steel")
    body.cyl((0, -22, -380), 16, 400, st)                                          # gas tube
    body.box(-8, 8, -10, 40, -608, -596, st)
    body.box(-10, 10, -10, 10, -680, -620, st)                                     # flash hider
    for z in (-668, -650, -632):
        body.box(-10.4, 10.4, -6, 6, z, z + 6, "rubber")
    bp = body.bone("bipod", pivot=(0, -30, -520))
    bipod(bp, -520, y=-30, legs_len=240, folded=True)
    stock = m["gun"].bone("stock", pivot=(0, 0, 150))
    stock.box(-16, 16, -20, 10, 150, 420, "wood_red")
    stock.box(-16, 16, -110, -84, 220, 420, "wood_red")
    stock.box(-16, 16, -110, 10, 400, 430, "wood_red")
    stock.box(-17, 17, -118, 14, 426, 438, st)
    # cover hinged at the FRONT (rear lifts)
    cover = body.bone("cover", pivot=(0, 14, -150))
    cover.box(-19, 19, 14, 26, -150, 90, st)
    cover.box(-6, 6, 26, 36, -100, -80, st)                                        # rear sight leaf
    ch = body.bone("charging_handle", pivot=(20, -20, -60))
    ch.box(20, 34, -26, -16, -66, -54, "steel")
    box = m["gun"].bone("box", pivot=(14, -40, -100))
    box.box(-4, 44, -170, -40, -160, -40, "olive")
    box.box(-6, 46, -172, -168, -158, -42, "steel_dark")
    box.box(10, 30, -170, -160, -110, -90, "steel")                                # latch
    belt = m["gun"].bone("belt", pivot=(26, -6, -130))
    _belt(belt, 24, -4, -150, n=6, dx=4, dy=-7, case="steel", tip="copper", d=9, length=60)
    add_arms(m, right_hand=(8, -94, 72), left_hand=(-10, -50, -200), right_rot=(34, 14, 6), left_rot=(26, -18, -4))
    add_sockets(m, muzzle=(0, 0, -680), optic=(-22, 6, 0), under=None, eject=(-14, -32, -30), sight=(0, 36, -90))

    def inspect():
        a = Anim(m, "inspect", 4.6)
        # belt shake: lift the dangling belt and let it swing
        a.mv("gun", 0.0, 0.45, pos=(-40, 20, 40), rot=(6, -20, -30))
        a.mv("arm_left", 0.1, 0.45, pos=(40, -20, 40), rot=(0, 20, 0))
        a.grab("arm_left", "belt", 0.48, 1.6, fade_in=0.03, fade_out=0.06)
        a.key("belt", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("belt", 0.5, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("belt", 0.75, pos=(10, 16, 0), rot=(0, 0, 18), e="inoutsine")
        a.shake("belt", "rot", 0.8, 1.5, (4, 0, 8), freq=6, seed=5)
        a.sound(0.85, "belt_rattle")
        a.sound(1.2, "belt_rattle")
        a.key("belt", 1.55, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")
        # flip the bipod legs down and up
        a.mv("arm_left", 1.65, 2.0, pos=(20, -40, -300), rot=(10, 0, 0))
        a.mv("gun", 1.6, 2.2, pos=(-60, 30, -40), rot=(-10, 34, 10), e="inoutsine")
        a.key("bipod", 0.0, rot=(0, 0, 0))
        a.key("bipod", 2.1, rot=(0, 0, 0))
        a.key("bipod", 2.4, rot=(-80, 0, 0), e="outback")
        a.sound(2.4, "click_small")
        a.key("bipod", 2.9, rot=(-80, 0, 0))
        a.key("bipod", 3.15, rot=(0, 0, 0), e="inoutsine")
        a.sound(3.15, "click_small")
        a.mv("arm_left", 3.2, 3.7, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.3, 4.55)
        return a

    anims = [idle(m), draw(m, 0.95, sound="draw_rifle"),
             fire_basic(m, "fire", kick=(3.4, 0.7, 1.4), push=13, recover=0.14, length=0.22),
             fire_basic(m, "fire_aim", kick=(3.4, 0.7, 1.4), push=13, recover=0.12, length=0.2, aim=True),
             belt_reload(m, "reload", False, cover_rot=(-70, 0, 0), box_drop=(30, -260, 20)),
             belt_reload(m, "reload_empty", True, cover_rot=(-70, 0, 0), box_drop=(30, -260, 20),
                         ch_travel=(0, 0, 120)),
             inspect(), dry_fire(m)]
    return GunAsset(m, anims, LMG_FP)


GUNS = {"m249": m249, "pkm": pkm}
