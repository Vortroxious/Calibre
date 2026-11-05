"""Walther PPQ, Bersa Thunder 380, Ruger Mark III, S&W 642 Airweight, Ruger Single Six."""
import math

import numpy as np

from ..core import Anim
from ..common import (GunAsset, new_gun, add_arms, add_sockets, idle, draw, fire_basic, dry_fire, apply_hidden)
from ..templates import pistol_reload, revolver_reload, _settle, OFF_LEFT, OFF_LEFT_ROT
from .pistols import _pistol_mag, _grip, _fixed_sights

PISTOL_FP = {"hip": {"pos": [0.1, -0.082, -0.27], "rot": [0, 6, 0]}, "ads": {"dist": 0.34}}


def _pistol_set(m, A, travel, kick, push, hammer=None, release="thumb", reload_len=None, slide="slide"):
    cyc = dict(bone=slide, travel=travel, t_back=0.022, t_fwd=0.058)
    k = dict(kick=kick, push=push, cycle=cyc, hammer=hammer)
    return [idle(m), idle(m, "idle_empty", locked={slide: travel}),
            draw(m, 0.55, sound="draw_pistol", style="pistol"),
            fire_basic(m, "fire", recover=0.24, length=0.32, **k),
            fire_basic(m, "fire_aim", recover=0.2, length=0.28, aim=True, **k),
            fire_basic(m, "fire_last", recover=0.24, length=0.32, lock_back=True, **k),
            pistol_reload(m, "reload", A, empty=False, slide_bone=slide, slide_travel=travel, length=reload_len),
            pistol_reload(m, "reload_empty", A, empty=True, slide_bone=slide, slide_travel=travel, release=release,
                          length=None if reload_len is None else reload_len + 0.5)]


# =================================================================================================
# Walther PPQ M2
# =================================================================================================
def ppq():
    A = -16.0
    TRAVEL = (0, 0, 42)
    m = new_gun("ppq")
    body = m["body"]
    pl = "polymer"
    body.box(-12, 12, -26, -10, -146, 34, pl)
    body.box(-10, 10, -31, -26, -142, -96, pl)
    for z in (-136, -124, -112):
        body.box(-10.5, 10.5, -32, -30, z, z + 4, pl)
    body.box(-12.5, 12.5, -26, -12, 24, 42, pl)                               # beavertail
    body.box(-5, 5, -58, -26, -52, -45, pl)                                   # trigger guard
    body.box(-5, 5, -58, -52, -52, -6, pl)
    body.box(-5, 5, -52, -40, -10, -4, pl)
    gp = (0, -18, 14)
    body.box(-14.5, 14.5, -128, -18, -12, 40, pl, rot=(A, 0, 0), pivot=gp)
    body.box(-15, 15, -112, -46, -8, 36, "polymer_grey", rot=(A, 0, 0), pivot=gp)   # textured panels
    body.box(-5, 5, -124, -24, 40, 46, pl, rot=(A, 0, 0), pivot=gp)                  # backstrap
    body.box(-13.5, -12, -18, -12, -18, -2, "steel_dark")                     # slide stop
    # ambidextrous paddle magazine release at the back of the trigger guard
    pad = body.bone("paddle", pivot=(0, -40, -4))
    pad.box(-9, 9, -48, -40, -6, -2, pl)
    body.cyl((0, 0, -100), 13, 104, "steel_light")
    body.box(-7, 7, 4, 14, -24, 8, "steel_light")
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-12.5, 12.5, -10, 14, -150, 38, "steel_dark")
    slide.box(-10.5, 10.5, 14, 17, -148, 36, "steel_dark")
    slide.box(-7.5, 7.5, -7.5, 7.5, -151, -150, "rubber")
    slide.box(0, 12.7, 10, 17.1, -24, 10, "rubber")
    slide.box(1, 9, 12, 17.2, -22, 8, "steel_light")
    for i in range(6):                                                         # rear and front serrations
        z = 8 + i * 4.2
        slide.box(-12.7, 12.7, -4, 12, z, z + 1.8, "steel")
        z = -140 + i * 4.2
        slide.box(-12.7, 12.7, -4, 12, z, z + 1.8, "steel")
    _fixed_sights(slide, -142, 34, 17, front_h=6, rear_h=6.5)
    trig = body.bone("trigger", pivot=(0, -27, -27))
    trig.box(-3, 3, -46, -27, -31, -26, pl, rot=(-6, 0, 0), pivot=(0, -27, -27))
    _pistol_mag(m, gp, A, -18, -134, -6, 28, 22, base_mat="polymer")
    add_arms(m, right_hand=(6, -66, 30), left_hand=(-14, -70, 20), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -152), under=(0, -31, -118), eject=(13, 12, -6), sight=(0, 23, 34))

    def inspect():
        # press-check with the front serrations, then flick the paddle so the mag drops a little and slap it home
        a = Anim(m, "inspect", 3.6)
        a.mv("gun", 0.0, 0.35, pos=(-40, 30, 40), rot=(8, 20, -28))
        a.mv("arm_left", 0.05, 0.4, pos=(26, 70, -140), rot=(-30, 30, 50))
        a.grab("arm_left", "slide", 0.42, 0.9, fade_in=0.04, fade_out=0.06)
        a.key("slide", 0.0, pos=(0, 0, 0))
        a.key("slide", 0.45, pos=(0, 0, 0))
        a.key("slide", 0.62, pos=(0, 0, 14), e="inoutquad")
        a.sound(0.6, "press_check")
        a.mv("gun", 0.45, 0.65, pos=(-44, 34, 44), rot=(12, 26, -46))
        a.key("slide", 0.85, pos=(0, 0, 14))
        a.key("slide", 0.92, pos=(0, 0, 0), e="inquad")
        a.sound(0.92, "slide_forward_light")
        a.mv("arm_left", 0.95, 1.3, pos=(-40, -60, 60), rot=(20, -20, 10))
        a.mv("gun", 1.0, 1.5, pos=(-50, 40, 30), rot=(10, -50, -10))
        # trigger finger pushes the paddle down
        a.mv("arm_right", 1.5, 1.6, pos=(0, -3, -4), rot=(4, 0, 0))
        a.key("paddle", 0.0, rot=(0, 0, 0))
        a.key("paddle", 1.56, rot=(0, 0, 0))
        a.key("paddle", 1.62, rot=(24, 0, 0), e="outquad")
        a.key("paddle", 1.75, rot=(0, 0, 0))
        a.sound(1.62, "mag_release")
        a.mv("arm_right", 1.7, 1.8, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("magazine", 0.0, pos=(0, 0, 0))
        a.key("magazine", 1.62, pos=(0, 0, 0))
        a.key("magazine", 1.72, pos=(0, -14, 4), e="outquad")
        a.mv("arm_left", 1.8, 2.1, pos=(10, -60, 60), rot=(10, 0, 0))
        a.key("magazine", 2.15, pos=(0, -14, 4))
        a.key("magazine", 2.22, pos=(0, 0, 0), e="inquad")
        a.sound(2.22, "mag_in_pistol")
        a.spring("gun", "rot", 2.22, (-2.0, 0, 0.8), freq=7, damp=10)
        a.mv("arm_left", 2.3, 2.8, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 2.5, 3.55)
        return a

    anims = _pistol_set(m, A, TRAVEL, kick=(9, 0.5, 1.5), push=14, release="thumb") + [inspect(), dry_fire(m)]
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Bersa Thunder 380 (DA/SA, exposed hammer, trigger-guard takedown)
# =================================================================================================
def bersa():
    A = -14.0
    TRAVEL = (0, 0, 34)
    m = new_gun("bersa")
    body = m["body"]
    al = "alloy"
    body.box(-10, 10, -22, -8, -122, 30, al)
    body.box(-10.5, 10.5, -20, -8, 28, 40, al)
    tg = body.bone("guard", pivot=(0, -24, -44))
    tg.box(-4, 4, -50, -44, -46, -6, al)                                     # trigger guard (takedown lever)
    tg.box(-4, 4, -48, -24, -48, -42, al, rot=(16, 0, 0), pivot=(0, -24, -46))
    gp = (0, -16, 14)
    _grip(body, gp, A, 11, -104, -16, -6, 36, al, panel_mat="rubber")
    body.box(-12.5, -10, -12, -6, -20, -4, "steel_dark")
    body.box(-12.5, -10, -38, -30, -8, 0, "steel_dark")
    body.cyl((0, 0, -80), 12, 84, "steel_light")
    slide = m["gun"].bone("slide", pivot=(0, 0, 0))
    slide.box(-10.5, 10.5, -8, 13, -124, 38, "steel_dark")
    slide.box(-8.5, 8.5, 13, 15, -122, 34, "steel_dark")
    slide.box(-6, 6, -6, 6, -125, -124, "rubber")
    slide.box(0, 10.7, 8, 15.2, -24, 6, "rubber")
    for i in range(7):
        z = 8 + i * 3.6
        slide.box(-10.7, -10.5, -4, 11, z, z + 1.6, "steel")
        slide.box(10.5, 10.7, -4, 11, z, z + 1.6, "steel")
    _fixed_sights(slide, -118, 34, 15, front_h=5, rear_h=5)
    saf = slide.bone("safety", pivot=(0, 9, 26))
    saf.box(-13, -10.5, 6, 11, 20, 32, "steel_dark")
    ham = body.bone("hammer", pivot=(0, -4, 40))
    ham.box(-3.5, 3.5, -6, 11, 38, 44, "steel", rot=(26, 0, 0), pivot=(0, -4, 40))
    ham.box(-4, 4, 7, 13, 42, 50, "steel", rot=(26, 0, 0), pivot=(0, -4, 40))
    trig = body.bone("trigger", pivot=(0, -24, -26))
    trig.box(-3, 3, -42, -22, -30, -23, "steel_dark", rot=(-8, 0, 0), pivot=(0, -24, -26))
    _pistol_mag(m, gp, A, -16, -112, -2, 28, 15, base_mat="polymer", round_d=8.5, round_len=25)
    add_arms(m, right_hand=(6, -60, 30), left_hand=(-14, -64, 20), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -126), under=None, eject=(11, 10, -8), sight=(0, 20, 34))

    def inspect():
        # pull the trigger guard down (the Bersa's takedown), ease the slide back and up off the rails, put it back
        a = Anim(m, "inspect", 4.0)
        a.mv("gun", 0.0, 0.4, pos=(-40, 30, 30), rot=(10, 40, 10))
        a.mv("arm_left", 0.2, 0.5, pos=(20, 10, -60), rot=(0, 20, 30))
        a.key("guard", 0.0, rot=(0, 0, 0))
        a.key("guard", 0.55, rot=(0, 0, 0))
        a.key("guard", 0.68, rot=(-18, 0, 0), e="outquad")
        a.sound(0.66, "click_small")
        a.mv("arm_left", 0.7, 0.95, pos=(20, 70, -60), rot=(-30, 20, 40))
        a.grab("arm_left", "slide", 0.95, 2.1, fade_in=0.04, fade_out=0.06)
        a.key("slide", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("slide", 1.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("slide", 1.25, pos=(0, 0, 34), e="inoutsine")
        a.sound(1.22, "slide_release")
        a.key("slide", 1.45, pos=(0, 8, 36), rot=(-8, 0, 0), e="inoutsine")     # rear lifts off the rails
        a.mv("gun", 1.3, 1.7, pos=(-50, 40, 30), rot=(16, 56, 14))
        a.key("slide", 1.75, pos=(0, 8, 36), rot=(-8, 0, 0))
        a.key("slide", 1.95, pos=(0, 0, 34), rot=(0, 0, 0), e="inoutsine")
        a.key("slide", 2.06, pos=(0, 0, 0), e="inquad")
        a.sound(2.06, "slide_release")
        a.spring("gun", "rot", 2.06, (1.4, 0, -1.0), freq=6, damp=8)
        a.mv("arm_left", 2.1, 2.3, pos=(20, 10, -60), rot=(0, 20, 30))
        a.key("guard", 2.3, rot=(-18, 0, 0))
        a.key("guard", 2.4, rot=(0, 0, 0), e="inquad")
        a.sound(2.4, "click_small")
        a.mv("arm_left", 2.5, 2.9, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 2.6, 3.95)
        return a

    anims = _pistol_set(m, A, TRAVEL, kick=(7.5, 0.5, 1.3), push=12, hammer=-34, release="thumb") + [inspect(),
                                                                                                    dry_fire(m)]
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Ruger Mark III target (bull barrel, tubular receiver, rear bolt ears)
# =================================================================================================
def rugermk3():
    A = -22.0
    TRAVEL = (0, 0, 30)
    m = new_gun("rugermk3")
    body = m["body"]
    st = "steel_dark"
    body.cyl((0, 0, -30), 24, 140, st, sides=12)                              # receiver tube -100 .. 40
    body.cyl((0, 0, -170), 22, 140, st, sides=12)                             # bull barrel
    body.box(-7.5, 7.5, -7.5, 7.5, -241, -240, "rubber")
    body.box(0, 12.6, -2, 8, -70, -30, "rubber")                              # ejection port
    body.box(-3, 3, 11, 18, -236, -226, st)                                  # front blade
    body.box(-8, 8, 11, 14, 22, 36, st)                                      # adjustable rear sight
    body.box(-8, -1.6, 14, 19, 30, 36, st)
    body.box(1.6, 8, 14, 19, 30, 36, st)
    body.box(-10, 10, -22, -10, -96, 34, st)                                  # frame
    body.box(-4, 4, -50, -44, -60, -14, st)
    body.box(-4, 4, -50, -22, -64, -58, st, rot=(14, 0, 0), pivot=(0, -22, -60))
    gp = (0, -16, 6)
    _grip(body, gp, A, 11, -118, -16, -8, 34, st, panel_mat="polymer")
    body.box(-13, -10, -14, -8, -40, -26, "steel")                           # bolt stop
    saf = body.bone("safety", pivot=(-11, -14, 30))
    saf.box(-14, -10, -18, -10, 24, 34, "steel")
    bolt = m["gun"].bone("bolt", pivot=(0, 0, 0))
    bolt.box(-6, 6, -6, 6, -70, 40, "steel_light")
    bolt.box(-15, 15, -3, 7, 40, 52, "steel_light")                         # the ears
    trig = body.bone("trigger", pivot=(0, -22, -36))
    trig.box(-3, 3, -42, -22, -40, -33, "steel", rot=(-8, 0, 0), pivot=(0, -22, -36))
    _pistol_mag(m, gp, A, -16, -124, -2, 24, 12, base_mat="polymer", round_d=6, round_len=25)
    add_arms(m, right_hand=(6, -64, 24), left_hand=(-14, -68, 14), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -242), optic=(0, 12, -20), under=None, eject=(12, 6, -50), sight=(0, 18, 34))

    def inspect():
        # pinch the bolt ears to look into the chamber, ride it home, then sight down the bull barrel
        a = Anim(m, "inspect", 3.8)
        a.mv("gun", 0.0, 0.4, pos=(-40, 20, -40), rot=(8, -20, -26))
        a.mv("arm_left", 0.1, 0.45, pos=(14, 74, 30), rot=(-40, 10, 40))
        a.grab("arm_left", "bolt", 0.46, 1.2, fade_in=0.04, fade_out=0.06)
        a.key("bolt", 0.0, pos=(0, 0, 0))
        a.key("bolt", 0.48, pos=(0, 0, 0))
        a.key("bolt", 0.66, pos=(0, 0, 18), e="inoutquad")
        a.sound(0.64, "press_check")
        a.mv("gun", 0.6, 0.85, pos=(-44, 24, -30), rot=(12, -40, -46))
        a.key("bolt", 1.05, pos=(0, 0, 18))
        a.key("bolt", 1.16, pos=(0, 0, 0), e="inoutsine")
        a.sound(1.16, "slide_forward_light")
        a.mv("arm_left", 1.25, 1.6, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 1.3, 1.9, pos=(-10, -20, -60), rot=(-6, -4, 0))
        a.wave("gun", "rot", (0.2, 0.3, 0), 1.2)
        a.mv("arm_right", 2.2, 2.32, pos=(-6, 12, -2), rot=(0, -6, 4))
        a.key("safety", 0.0, rot=(0, 0, 0))
        a.key("safety", 2.3, rot=(0, 0, 0))
        a.key("safety", 2.36, rot=(-30, 0, 0), e="outquad")
        a.sound(2.36, "safety")
        a.key("safety", 2.7, rot=(-30, 0, 0))
        a.key("safety", 2.76, rot=(0, 0, 0), e="outquad")
        a.sound(2.76, "safety")
        a.mv("arm_right", 2.8, 2.95, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 2.6, 3.75)
        return a

    anims = _pistol_set(m, A, TRAVEL, kick=(4.5, 0.3, 0.8), push=6, slide="bolt", release="thumb") + [inspect(),
                                                                                                     dry_fire(m)]
    return GunAsset(m, anims, PISTOL_FP)


# =================================================================================================
# Revolver helpers
# =================================================================================================
def _cylinder(m, crane_parent, c_y, n, d_cyl, length, z0, chamber_r, case_d, case_len, flutes=True,
              speedloader=True, mat="steel"):
    crane = m["gun"].bone("crane", pivot=(-9, c_y - 18, 0))
    crane.box(-12, -5, c_y - 22, c_y - 14, z0 - 4, z0 + length + 2, mat)
    cyl = crane.bone("cylinder", pivot=(0, c_y, 0))
    cyl.cyl((0, c_y, z0 + length / 2), d_cyl, length, mat, sides=12)
    if flutes:
        for i in range(n):
            a = math.radians(180 / n + 360 / n * i)
            x = math.cos(a) * (d_cyl / 2 - 2)
            y = c_y + math.sin(a) * (d_cyl / 2 - 2)
            cyl.box(x - 2.2, x + 2.2, y - 2.2, y + 2.2, z0 + 4, z0 + length - 8, "steel_dark")
    rounds = cyl.bone("rounds", pivot=(0, c_y, 0))
    brass = cyl.bone("brass", pivot=(0, c_y, 0))
    for i in range(n):
        a = math.radians(90 + 360 / n * i)
        x = math.cos(a) * chamber_r
        y = c_y + math.sin(a) * chamber_r
        rounds.cyl((x, y, z0 + length + 0.5), case_d + 0.8, 1.5, "brass")
        rounds.cyl((x, y, z0 + length + 0.6), case_d * 0.45, 1.4, "copper")
        brass.cyl((x, y, z0 + length - case_len / 2), case_d, case_len, "brass")
    ej = crane.bone("ejector", pivot=(0, c_y, 0))
    ej.cyl((0, c_y, z0 - 24), 6, 50, "steel_light")
    ej.cyl((0, c_y, z0 + length - 1), d_cyl * 0.55, 2, "steel_light", sides=12)
    if speedloader:
        sl = crane.bone("speedloader", pivot=(0, c_y, 0))
        sl.cyl((0, c_y, z0 + length + 14), d_cyl * 1.02, 10, "polymer", sides=12)
        sl.cyl((0, c_y, z0 + length + 24), 14, 10, "polymer")
        for i in range(n):
            a = math.radians(90 + 360 / n * i)
            x = math.cos(a) * chamber_r
            y = c_y + math.sin(a) * chamber_r
            sl.round_((x, y, z0 + length - case_len / 2 + 6), case_len + 8, case_d)
    return crane


# =================================================================================================
# S&W 642 Airweight (J-frame, enclosed hammer, 5 shots)
# =================================================================================================
def sw642():
    m = new_gun("sw642")
    body = m["body"]
    al = "stainless"
    cy = -13.0
    body.box(-11, 11, 10, 18, -10, 30, al)                                  # top strap
    body.box(-11, 11, -34, -26, -12, 30, al)
    body.box(-11, 11, -34, 18, -18, -10, al)
    body.box(-11, 11, -34, 22, 28, 50, al)                                  # humpback (enclosed hammer)
    body.box(-9, 9, 22, 26, 30, 48, al)
    body.cyl((0, 0, -40), 15, 56, al)                                       # 1.875" barrel
    body.box(-7, 7, -26, -6, -66, -12, al)                                  # ejector shroud
    body.box(-1.5, 1.5, 8, 20, -66, -56, al)                                # ramp front sight
    body.box(-4, 4, 18, 20, 20, 30, al)
    body.box(-1.4, 1.4, 18, 20.2, 20, 50, "rubber")                         # sight groove
    body.box(-4, 4, -58, -52, -30, 20, al)
    body.box(-4, 4, -58, -34, -34, -28, al)
    trig = body.bone("trigger", pivot=(0, -34, -4))
    trig.box(-3.5, 3.5, -56, -34, -8, 0, al, rot=(-10, 0, 0), pivot=(0, -34, -4))
    gp = (0, -26, 46)
    body.box(-13, 13, -108, -26, 32, 64, "rubber", rot=(-20, 0, 0), pivot=gp)   # boot grip
    body.box(-14, 14, -100, -40, 30, 66, "rubber", rot=(-20, 0, 0), pivot=gp)
    body.box(-14, -11, -6, 2, 30, 40, al)                                   # thumb latch
    _cylinder(m, "gun", cy, 5, 36, 38, -10, 11.5, 10, 30)
    add_arms(m, right_hand=(6, -66, 50), left_hand=(-14, -70, 40), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -68), eject=None, sight=(0, 20, 40))

    def fire(name, aim):
        a = Anim(m, name, 0.42)
        k = 0.45 if aim else 1.0
        a.key("trigger", 0.0, rot=(-16, 0, 0))
        a.key("trigger", 0.12, rot=(0, 0, 0), e="outquad")
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.08, rot=(0, 0, 0))
        a.key("cylinder", 0.2, rot=(0, 0, -72), e="outquad")
        a.kick("gun", "rot", 0.0, (26 * k, 2 * k, 5 * k), attack=0.025, recover=0.36)    # light frame, big flip
        a.kick("gun", "pos", 0.0, (0, 4 * k, 18 * k), attack=0.022, recover=0.32)
        a.spring("gun", "rot", 0.05, (2.4 * k, 0, 1.8 * k), freq=5, damp=8)
        return a

    def inspect():
        # slow double-action press on a cleared gun: watch the cylinder index chamber by chamber
        a = Anim(m, "inspect", 3.8)
        a.mv("gun", 0.0, 0.4, pos=(-40, 30, 30), rot=(6, 46, 16))
        a.key("trigger", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        for i in range(3):
            t = 0.55 + i * 0.6
            a.key("trigger", t, rot=(0, 0, 0))
            a.key("trigger", t + 0.36, rot=(-16, 0, 0), e="inoutsine")
            a.key("trigger", t + 0.5, rot=(0, 0, 0), e="outquad")
            a.key("cylinder", t + 0.04, rot=(0, 0, -72 * i))
            a.key("cylinder", t + 0.34, rot=(0, 0, -72 * (i + 1)), e="inoutsine")
            a.sound(t + 0.36, "dry_fire")
            a.spring("gun", "rot", t + 0.36, (0.6, 0, 0), freq=9, damp=12)
        a.mv("gun", 1.2, 1.9, pos=(-44, 34, 26), rot=(10, 30, 26))
        a.mv("gun", 2.3, 2.7, pos=(-40, 40, 20), rot=(14, -40, -10))           # show the stainless side
        _settle(a, 2.9, 3.75)
        return a

    anims = [idle(m), draw(m, 0.5, sound="draw_pistol", style="pistol"), fire("fire", False), fire("fire_aim", True),
             revolver_reload(m, "reload", length=3.0), inspect(), dry_fire(m)]
    apply_hidden(anims, ["speedloader", "brass"])
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.08, -0.3], "rot": [0, 6, 0]}, "ads": {"dist": 0.36}})


# =================================================================================================
# Ruger Single Six (single action, loading gate, ejector rod)
# =================================================================================================
def singlesix():
    m = new_gun("singlesix")
    body = m["body"]
    bl = "steel"
    cy = -12.0
    body.box(-11, 11, 8, 16, -26, 30, bl)                                    # top strap
    body.box(-11, 11, -32, -24, -26, 30, bl)
    body.box(-11, 11, -32, 16, -32, -26, bl)
    body.box(-11, 11, -30, 14, 30, 44, bl)                                    # recoil shield
    body.cyl((0, 0, -120), 14, 180, bl)                                       # 5.5" barrel
    body.box(-1.5, 1.5, 7, 18, -206, -192, bl)
    body.box(-6, 6, 14, 18, 30, 40, bl)
    body.box(-6, -1.4, 18, 21, 34, 40, bl)
    body.box(1.4, 6, 18, 21, 34, 40, bl)
    # ejector rod housing on the right of the barrel
    body.cyl((9, -14, -110), 10, 140, bl)
    ej = body.bone("ejector", pivot=(9, -14, 0))
    ej.cyl((9, -14, -100), 5, 150, "steel_light")
    ej.box(12, 18, -18, -10, -184, -170, "steel_light")                        # rod head
    gate = body.bone("gate", pivot=(11, -24, 36))
    gate.box(9, 12, -26, -4, 30, 42, bl)
    # trigger guard, birdshead-free plow-handle grip
    body.box(-4, 4, -56, -50, -24, 22, "brass")
    body.box(-4, 4, -56, -32, -28, -22, "brass")
    trig = body.bone("trigger", pivot=(0, -32, 0))
    trig.box(-3, 3, -50, -32, -4, 2, bl, rot=(-10, 0, 0), pivot=(0, -32, 0))
    gp = (0, -24, 50)
    body.box(-12, 12, -114, -24, 36, 66, "wood", rot=(-14, 0, 0), pivot=gp)
    body.box(-13, 13, -110, -34, 32, 70, "wood", rot=(-14, 0, 0), pivot=gp)
    body.box(-6, 6, -114, -24, 64, 70, bl, rot=(-14, 0, 0), pivot=gp)       # backstrap
    ham = body.bone("hammer", pivot=(0, -16, 48))
    ham.box(-3.5, 3.5, -16, 18, 44, 52, bl, rot=(30, 0, 0), pivot=(0, -16, 48))
    ham.box(-4.5, 4.5, 14, 22, 50, 64, bl, rot=(30, 0, 0), pivot=(0, -16, 48))   # wide spur
    cyl = body.bone("cylinder", pivot=(0, cy, 0))
    cyl.cyl((0, cy, 4), 40, 56, bl, sides=12)
    rounds = cyl.bone("rounds", pivot=(0, cy, 0))
    for i in range(6):
        a = math.radians(90 + 60 * i)
        x, y = math.cos(a) * 12.5, cy + math.sin(a) * 12.5
        rounds.cyl((x, y, 32.4), 7.2, 1.2, "brass")
    # the chamber lined up with the gate sits at 4:30 seen from behind (right, low)
    gx, gy = math.cos(math.radians(-30)) * 12.5, cy + math.sin(math.radians(-30)) * 12.5
    rl = m["gun"].bone("round_load", pivot=(gx, gy, 34))
    rl.round_((gx, gy, 34 + 12), 25, 6)
    br = m["gun"].bone("brass", pivot=(gx, gy, 34))
    br.cyl((gx, gy, 24), 6, 15, "brass")
    add_arms(m, right_hand=(6, -70, 54), left_hand=(-14, -74, 44), right_rot=(34, 18, 6), left_rot=(34, -26, -6))
    add_sockets(m, muzzle=(0, 0, -210), eject=None, sight=(0, 19, 40))

    def fire(name, aim):
        a = Anim(m, name, 0.7)
        k = 0.45 if aim else 1.0
        a.key("trigger", 0.0, rot=(-10, 0, 0))
        a.key("trigger", 0.08, rot=(0, 0, 0), e="outquad")
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 0.012, rot=(-44, 0, 0), e="inquad")
        a.kick("gun", "rot", 0.0, (12 * k, 1 * k, 2 * k), attack=0.025, recover=0.3)
        a.kick("gun", "pos", 0.0, (0, 3 * k, 10 * k), attack=0.022, recover=0.28)
        a.spring("gun", "rot", 0.04, (1.2 * k, 0, 1.0 * k), freq=5, damp=8)
        # thumb rides the hammer spur back to full cock; the cylinder indexes as the hand rises
        a.mv("arm_right", 0.24, 0.34, pos=(-3, 18, 2), rot=(-14, -6, 0))
        a.key("hammer", 0.34, rot=(-44, 0, 0))
        a.key("hammer", 0.5, rot=(4, 0, 0), e="inoutsine")
        a.key("hammer", 0.54, rot=(0, 0, 0), e="outquad")
        a.sound(0.52, "hammer_thumb")
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.36, rot=(0, 0, 0))
        a.key("cylinder", 0.5, rot=(0, 0, -60), e="inoutsine")
        a.mv("arm_right", 0.54, 0.68, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 0.3, 0.45, pos=(0, 0, 0), rot=(-2 * k, 0, 0))
        a.mv("gun", 0.5, 0.69, pos=(0, 0, 0), rot=(0, 0, 0))
        return a

    def dry():
        a = dry_fire(m)
        a.key("hammer", 0.04, rot=(0, 0, 0))
        a.key("hammer", 0.06, rot=(-44, 0, 0), e="inquad")
        a.key("hammer", 0.25, rot=(-44, 0, 0))
        return a

    port_pos, port_tilt = (-30, 30, 40), (8, -16, 48)
    rest = {"gun": {"pos": port_pos, "rot": port_tilt}, "arm_left": {"pos": OFF_LEFT, "rot": OFF_LEFT_ROT},
            "gate": {"rot": (0, 0, -80)}, "hammer": {"rot": (-14, 0, 0)}}

    def reload_start():
        a = Anim(m, "reload_start", 0.7)
        a.mv("gun", 0.0, 0.35, pos=port_pos, rot=port_tilt)
        # thumb the hammer to half-cock so the cylinder spins free, flip the gate open
        a.mv("arm_right", 0.05, 0.16, pos=(-3, 18, 2), rot=(-14, -6, 0))
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 0.14, rot=(0, 0, 0))
        a.key("hammer", 0.22, rot=(-14, 0, 0), e="inoutsine")
        a.sound(0.22, "hammer_thumb")
        a.mv("arm_right", 0.26, 0.4, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_left", 0.0, 0.3, pos=(30, 20, 120), rot=(-20, 30, 40))
        a.key("gate", 0.0, rot=(0, 0, 0))
        a.key("gate", 0.36, rot=(0, 0, 0))
        a.key("gate", 0.46, rot=(0, 0, -80), e="outquad")
        a.sound(0.44, "loading_gate")
        a.mv("arm_left", 0.5, 0.68, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
        return a

    def reload_loop():
        # one chamber: punch the empty out with the rod, thumb a round in, click the cylinder round to the next one
        L = 0.95
        a = Anim(m, "reload_loop", L, rest=rest)
        a.mv("arm_right", 0.0, 0.12, pos=(-2, 6, -60), rot=(0, -10, 0))
        a.key("ejector", 0.0, pos=(0, 0, 0))
        a.key("ejector", 0.12, pos=(0, 0, 0))
        a.key("ejector", 0.22, pos=(0, 0, 52), e="outquad")
        a.sound(0.2, "ejector_rod")
        a.key("ejector", 0.32, pos=(0, 0, 0), e="inoutsine")
        a.mv("arm_right", 0.32, 0.42, pos=(0, 0, 0), rot=(0, 0, 0))
        a.show("brass", 0.12, 0.6)
        a.key("brass", 0.12, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("brass", 0.22, pos=(0, 0, 30), e="outquad")
        a.key("brass", 0.6, pos=(40, -160, 120), rot=(80, 0, 60), e="inquad")
        a.show("round_load", 0.3, 0.7)
        a.at_hand("round_load", 0.3, rot=(30, 0, 30))
        a.grab("arm_left", "round_load", 0.32, 0.66, fade_in=0.02, fade_out=0.05)
        a.key("round_load", 0.56, pos=(0, 0, 10), rot=(0, 0, 0), e="outcubic")
        a.key("round_load", 0.66, pos=(0, 0, -10), rot=(0, 0, 0), e="inquad")
        a.sound(0.64, "round_insert")
        a.event(0.64, "ammo")
        a.mv("arm_left", 0.7, 0.85, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.72, rot=(0, 0, 0))
        a.key("cylinder", 0.86, rot=(0, 0, -60), e="inoutsine")
        a.sound(0.86, "click_small")
        a.spring("gun", "rot", 0.64, (0.6, 0, 0.4), freq=8, damp=10)
        return a

    def reload_end():
        a = Anim(m, "reload_end", 0.8, rest=rest)
        a.mv("arm_left", 0.0, 0.18, pos=(30, 20, 120), rot=(-20, 30, 40))
        a.key("gate", 0.18, rot=(0, 0, -80))
        a.key("gate", 0.26, rot=(0, 0, 0), e="inquad")
        a.sound(0.26, "loading_gate")
        a.mv("arm_right", 0.3, 0.4, pos=(-3, 18, 2), rot=(-14, -6, 0))
        a.key("hammer", 0.4, rot=(-14, 0, 0))
        a.key("hammer", 0.5, rot=(4, 0, 0), e="inoutsine")
        a.key("hammer", 0.54, rot=(0, 0, 0))
        a.sound(0.5, "hammer_cock")
        a.mv("arm_right", 0.55, 0.68, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_left", 0.3, 0.65, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("gun", 0.3, 0.78, pos=(0, 0, 0), rot=(0, 0, 0))
        return a

    def inspect():
        # half-cock, open the gate and spin the cylinder past the clicks, close up and ease the hammer
        a = Anim(m, "inspect", 4.2)
        a.mv("gun", 0.0, 0.4, pos=(-40, 30, 30), rot=(6, -30, -24))
        a.mv("arm_right", 0.3, 0.4, pos=(-3, 18, 2), rot=(-14, -6, 0))
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 0.38, rot=(0, 0, 0))
        a.key("hammer", 0.46, rot=(-14, 0, 0))
        a.sound(0.46, "hammer_thumb")
        a.mv("arm_right", 0.5, 0.62, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_left", 0.3, 0.6, pos=(30, 20, 120), rot=(-20, 30, 40))
        a.key("gate", 0.0, rot=(0, 0, 0))
        a.key("gate", 0.6, rot=(0, 0, 0))
        a.key("gate", 0.7, rot=(0, 0, -80), e="outquad")
        a.sound(0.68, "loading_gate")
        a.mv("arm_left", 0.75, 0.9, pos=(34, 0, 110), rot=(-20, 30, 60))
        a.key("cylinder", 0.0, rot=(0, 0, 0))
        a.key("cylinder", 0.9, rot=(0, 0, 0))
        a.key("cylinder", 2.1, rot=(0, 0, -720), e="outcubic")
        for i in range(8):
            a.sound(0.95 + 0.06 * i + 0.012 * i * i, "click_small")
        a.mv("gun", 0.9, 1.6, pos=(-50, 40, 30), rot=(10, -50, -36))
        a.key("gate", 2.3, rot=(0, 0, -80))
        a.key("gate", 2.38, rot=(0, 0, 0), e="inquad")
        a.sound(2.38, "loading_gate")
        a.mv("arm_left", 2.4, 2.8, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_right", 2.7, 2.8, pos=(-3, 18, 2), rot=(-14, -6, 0))
        a.key("hammer", 2.8, rot=(-14, 0, 0))
        a.key("hammer", 2.9, rot=(4, 0, 0), e="inoutsine")
        a.key("hammer", 2.94, rot=(0, 0, 0))
        a.sound(2.9, "hammer_cock")
        a.mv("arm_right", 2.95, 3.1, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, 3.0, 4.15)
        return a

    anims = [idle(m), draw(m, 0.55, sound="draw_pistol", style="pistol"), fire("fire", False), fire("fire_aim", True),
             reload_start(), reload_loop(), reload_end(), inspect(), dry()]
    apply_hidden(anims, ["round_load", "brass"])
    return GunAsset(m, anims, {"hip": {"pos": [0.1, -0.08, -0.29], "rot": [0, 6, 0]}, "ads": {"dist": 0.36}})


GUNS = {"ppq": ppq, "bersa": bersa, "rugermk3": rugermk3, "sw642": sw642, "singlesix": singlesix}
