"""Reload / action choreography templates shared between guns of the same mechanical family.

All positions are offsets (mm) from the bone's rest pose, in the parent bone's space.
Arms are children of `gun`, so hand offsets are expressed in gun space.
"""
from __future__ import annotations

import numpy as np

from .core import Anim
from .common import along

OFF_LEFT = (-70, -300, 120)     # left hand "at the belt pouch", out of view
OFF_LEFT_ROT = (45, -10, 25)


def _settle(a, t0, t1, amp=(1.2, 0.0, 0.8)):
    a.mv("gun", t0, t1, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")
    a.spring("gun", "rot", t1 - 0.05, amp, freq=4, damp=8)


# ------------------------------------------------------------------------------------------------
# Pistols
# ------------------------------------------------------------------------------------------------
def pistol_reload(m, name, mag_angle, empty, slide_bone="slide", slide_travel=(0, 0, 40),
                  release="overhand", mag_drop=150, length=None, tilt=(10, -8, -24), tilt_pos=(-34, 26, 34),
                  mag_sound="pistol", hammer=None):
    """Drop-free magazine swap. `release`: 'overhand' | 'thumb' (slide stop)."""
    L = length or (2.25 if empty else 1.75)
    a = Anim(m, name, L)
    # 1. bring the gun in and cant it so the mag well faces the support hand
    a.mv("gun", 0.0, 0.24, pos=tilt_pos, rot=tilt, e="inoutsine")
    if empty:
        a.key(slide_bone, 0.0, pos=slide_travel)
    # support hand leaves
    a.mv("arm_left", 0.04, 0.22, pos=(-40, -40, 30), rot=(20, -10, 10), e="inquad")
    a.mv("arm_left", 0.22, 0.46, pos=OFF_LEFT, rot=OFF_LEFT_ROT, e="outquad")
    # 2. thumb the release
    a.mv("arm_right", 0.16, 0.21, pos=(-3, 3, -3), rot=(0, -3, 2), e="outquad")
    a.mv("arm_right", 0.25, 0.34, pos=(0, 0, 0), rot=(0, 0, 0))
    a.sound(0.21, f"mag_out_{mag_sound}")
    # 3. magazine drops free
    a.key("magazine", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
    a.key("magazine", 0.21, pos=(0, 0, 0), rot=(0, 0, 0))
    a.key("magazine", 0.27, pos=along(mag_angle, 30), e="outquad")
    a.key("magazine", 0.56, pos=along(mag_angle, mag_drop + 30, (-6, -mag_drop, 25)), rot=(14, 0, -30), e="inquad")
    a.spring("gun", "rot", 0.22, (0.0, 0.0, -1.2), freq=6, damp=9)
    # 4. new magazine arrives in the support hand from out of view
    t_in0, t_in1 = 0.6, 0.98 + (0.05 if empty else 0)
    a.key("magazine", 0.57, pos=along(mag_angle, 300, (-50, -150, 80)), rot=(30, 0, 25))
    a.grab("arm_left", "magazine", 0.6, t_in1 + 0.1, fade_in=0.14, fade_out=0.05)
    a.key("magazine", t_in1 - 0.12, pos=along(mag_angle, 48, (-2, -4, 2)), rot=(4, 0, 4), e="outcubic")
    a.key("magazine", t_in1 - 0.04, pos=along(mag_angle, 14), rot=(0, 0, 0), e="inoutsine")
    a.key("magazine", t_in1, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")  # palm seats it
    a.sound(t_in1, f"mag_in_{mag_sound}")
    a.spring("gun", "rot", t_in1, (-2.2, 0.0, 1.0), freq=7, damp=10)
    a.kick("gun", "pos", t_in1, (0, 5, 0), attack=0.03, recover=0.18)
    a.event(t_in1, "ammo")
    t = t_in1 + 0.1
    if empty:
        if release == "overhand":
            # support hand goes over the top, grips the rear of the slide and racks it
            a.mv("arm_left", t, t + 0.22, pos=(6, 92, 26), rot=(-35, -18, 55), e="inoutsine")
            a.mv("gun", t, t + 0.22, pos=(tilt_pos[0] * 0.4, tilt_pos[1] * 0.7, tilt_pos[2]), rot=(4, 12, 10))
            a.grab("arm_left", slide_bone, t + 0.22, t + 0.38, fade_in=0.02, fade_out=0.03)
            a.key(slide_bone, t + 0.22, pos=slide_travel)
            a.key(slide_bone, t + 0.34, pos=np.asarray(slide_travel) * 1.12, e="outquad")
            a.key(slide_bone, t + 0.38, pos=(0, 0, 0), e="inquad")
            a.sound(t + 0.37, "slide_release")
            a.spring("gun", "rot", t + 0.38, (1.8, 0.0, -1.2), freq=6, damp=8)
            a.mv("arm_left", t + 0.4, t + 0.55, pos=(-30, 50, 50), rot=(-10, -10, 30), e="outquad")
            a.mv("arm_left", t + 0.55, t + 0.8, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")
            _settle(a, t + 0.4, L - 0.02)
        else:
            # thumb the slide stop
            a.mv("arm_left", t, t + 0.3, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")
            a.mv("arm_right", t + 0.12, t + 0.2, pos=(-4, 8, -10), rot=(-3, -4, 3), e="outquad")
            a.mv("arm_right", t + 0.26, t + 0.36, pos=(0, 0, 0), rot=(0, 0, 0))
            a.key(slide_bone, t + 0.2, pos=slide_travel)
            a.key(slide_bone, t + 0.24, pos=(0, 0, 0), e="inquad")
            a.sound(t + 0.23, "slide_release")
            a.spring("gun", "rot", t + 0.24, (1.8, 0.0, -1.2), freq=6, damp=8)
            _settle(a, t + 0.25, L - 0.02)
        if hammer and m.has("hammer"):
            a.key("hammer", 0.0, rot=(hammer, 0, 0))
    else:
        a.mv("arm_left", t, t + 0.32, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")
        _settle(a, t + 0.05, L - 0.02)
    return a


def revolver_reload(m, name, length=3.2):
    """Swing out cylinder, eject with rod, speedloader, close. Bones: crane (cylinder+crane), ejector, speedloader."""
    a = Anim(m, name, length)
    # tilt gun muzzle-up to the left, thumb the latch
    a.mv("gun", 0.0, 0.25, pos=(-40, 30, 30), rot=(18, -10, 28))
    a.mv("arm_right", 0.12, 0.2, pos=(-2, 6, -8), rot=(0, -3, 3))
    a.mv("arm_right", 0.26, 0.36, pos=(0, 0, 0), rot=(0, 0, 0))
    a.sound(0.2, "cylinder_latch")
    # support fingers push the cylinder out
    a.mv("arm_left", 0.05, 0.24, pos=(14, 10, -30), rot=(0, 10, -10))
    a.key("crane", 0.0, rot=(0, 0, 0))
    a.key("crane", 0.26, rot=(0, 0, 0))
    a.key("crane", 0.38, rot=(0, 0, 80), e="outback")
    a.sound(0.34, "cylinder_open")
    # point the muzzle up, slap the ejector rod
    a.mv("gun", 0.4, 0.62, pos=(-30, 60, 40), rot=(62, -6, 18), e="inoutsine")
    a.mv("arm_left", 0.42, 0.64, pos=(10, 30, -130), rot=(-60, 10, 0))
    a.key("ejector", 0.0, pos=(0, 0, 0))
    a.key("ejector", 0.66, pos=(0, 0, 0))
    a.key("ejector", 0.74, pos=(0, 0, 22), e="outquad")
    a.key("ejector", 0.86, pos=(0, 0, 0), e="inoutsine")
    a.sound(0.72, "ejector_rod")
    a.key("brass", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
    a.key("brass", 0.68, pos=(0, 0, 0))
    a.key("brass", 0.76, pos=(0, 0, 30), e="outquad")
    a.key("brass", 1.15, pos=(0, -120, 160), rot=(60, 0, 40), e="inquad")
    a.show("brass", 0.0, 1.15)
    if m.has("rounds"):
        a.show("rounds", 1.9)
    a.spring("gun", "rot", 0.74, (3.0, 0, 0), freq=6, damp=8)
    # muzzle down, speedloader arrives
    a.mv("gun", 0.9, 1.25, pos=(-30, 30, 30), rot=(-38, -6, 20), e="inoutsine")
    a.mv("arm_left", 0.85, 1.15, pos=OFF_LEFT, rot=OFF_LEFT_ROT, e="inoutsine")
    a.show("speedloader", 1.15, 2.1)
    a.at_hand("speedloader", 1.15, rot=(40, 0, 20))
    a.grab("arm_left", "speedloader", 1.18, 2.05, fade_in=0.08, fade_out=0.08)
    a.key("speedloader", 1.62, pos=(0, 0, 32), rot=(0, 0, 8), e="outcubic")
    a.key("speedloader", 1.72, pos=(0, 0, 4), rot=(0, 0, 0), e="inoutsine")
    a.sound(1.72, "speedloader_insert")
    a.key("speedloader", 1.82, pos=(0, 0, 4), rot=(0, 0, 0))
    a.key("speedloader", 1.92, pos=(0, 0, 4), rot=(0, 0, 0))   # twist knob
    a.sound(1.9, "speedloader_release")
    a.event(1.9, "ammo")
    a.key("speedloader", 2.08, pos=(-30, -120, 90), rot=(20, 0, 30), e="inquad")
    # close cylinder with the support thumb, flick back
    a.mv("arm_left", 2.1, 2.3, pos=(14, 10, -30), rot=(0, 10, -10))
    a.mv("gun", 2.05, 2.28, pos=(-30, 25, 25), rot=(4, -6, 22))
    a.key("crane", 2.25, rot=(0, 0, 80))
    a.key("crane", 2.36, rot=(0, 0, 0), e="inquad")
    a.sound(2.36, "cylinder_close")
    a.spring("gun", "rot", 2.36, (0, 0, -2.4), freq=7, damp=9)
    a.mv("arm_left", 2.4, 2.75, pos=(0, 0, 0), rot=(0, 0, 0))
    _settle(a, 2.4, length - 0.02)
    a.spring("crane", "rot", 0.38, (0, 0, -5), freq=8, damp=10)
    return a


# ------------------------------------------------------------------------------------------------
# Rifles / SMGs with box magazines
# ------------------------------------------------------------------------------------------------
def rifle_reload(m, name, mag_angle, empty, style="ar", length=None, mag_out=60.0,
                 bolt=None, bolt_travel=(0, 0, 70), ch=None, ch_travel=(0, 0, 70),
                 tilt=(6, -6, -26), tilt_pos=(-20, 16, 24), mag_sound="rifle", rock=0.0,
                 bolt_hold_open=True, slap_side="left", ch_hand="right"):
    """
    style:
      'ar'      straight-in mag, bolt catch paddle (AR15, SCAR, HK416)
      'ak'      rock-in mag (front hooks, rotate rear up). `rock` = rock angle.
      'hk'      MP5/G3 roller-delayed: cock + HK slap
      'smg'     straight-in, charging handle on top/side (UMP, Uzi)
      'bullpup' mag behind grip (AUG, P90 handled separately)
    bolt: bone that is held open (empty) / released at the end
    ch: charging handle bone to pull on empty reload (if different from bolt)
    """
    L = length or ((2.9 if empty else 2.35) + (0.25 if style == "hk" else 0))
    a = Anim(m, name, L)
    locked = empty and bolt_hold_open and bolt
    if locked:
        a.key(bolt, 0.0, pos=bolt_travel)
    if style == "hk" and empty is False:
        pass
    # 1. tilt
    a.mv("gun", 0.0, 0.3, pos=tilt_pos, rot=tilt, e="inoutsine")
    hk_lock = 0.0
    if style == "hk" and m.has("charging_handle"):
        # lock the cocking lever back first (HK style)
        a.mv("arm_left", 0.05, 0.3, pos=(10, 36, -40), rot=(-20, -20, 20))
        a.grab("arm_left", "charging_handle", 0.3, 0.5, fade_in=0.02, fade_out=0.04)
        a.key("charging_handle", 0.3, pos=(0, 0, 0))
        a.key("charging_handle", 0.42, pos=ch_travel, e="inoutquad")
        a.key("charging_handle", 0.5, pos=np.asarray(ch_travel) + (0, 6, 0))
        if bolt:
            a.key(bolt, 0.3, pos=(0, 0, 0))
            a.key(bolt, 0.42, pos=bolt_travel, e="inoutquad")
        a.sound(0.44, "charging_handle_lock")
        hk_lock = 0.5
    t0 = hk_lock
    # 2. support hand goes to the magazine
    a.mv("arm_left", t0 + 0.05, t0 + 0.3, pos=along(mag_angle, 40, (6, 0, 0)) if style != "hk" else (0, -40, 30),
         rot=(10, 10, 10), e="inoutsine")
    if style in ("ak",):
        # thumb pushes the mag catch, rock the mag forward/out
        a.grab("arm_left", "magazine", t0 + 0.3, t0 + 0.75, fade_in=0.05, fade_out=0.05)
        a.key("magazine", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("magazine", t0 + 0.32, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("magazine", t0 + 0.44, pos=(0, -4, -6), rot=(-rock, 0, 0), e="outquad")
        a.sound(t0 + 0.42, f"mag_out_{mag_sound}")
        a.key("magazine", t0 + 0.72, pos=along(mag_angle, 200, (-30, -60, 60)), rot=(-rock - 10, 10, 30), e="inoutsine")
        a.spring("gun", "rot", t0 + 0.42, (-1.5, 0, 1.2), freq=6, damp=9)
    else:
        a.grab("arm_left", "magazine", t0 + 0.3, t0 + 0.7, fade_in=0.05, fade_out=0.05)
        a.key("magazine", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("magazine", t0 + 0.32, pos=(0, 0, 0))
        # right index finger / thumb presses the mag release
        a.mv("arm_right", t0 + 0.24, t0 + 0.3, pos=(-3, 4, -4), rot=(0, -3, 2), e="outquad")
        a.mv("arm_right", t0 + 0.34, t0 + 0.44, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("magazine", t0 + 0.42, pos=along(mag_angle, mag_out * 0.5), e="outquad")
        a.sound(t0 + 0.33, f"mag_out_{mag_sound}")
        a.key("magazine", t0 + 0.7, pos=along(mag_angle, mag_out + 220, (-30, -60, 60)), rot=(12, 10, 30), e="inoutsine")
        a.spring("gun", "rot", t0 + 0.34, (-1.0, 0, 1.0), freq=6, damp=9)
    # 3. old mag goes to the pouch, new mag comes up
    ts = t0 + 0.75
    a.mv("arm_left", ts, ts + 0.22, pos=OFF_LEFT, rot=OFF_LEFT_ROT, e="inoutsine")
    a.key("magazine", ts + 0.22, pos=along(mag_angle, 360, (-60, -200, 120)), rot=(30, 10, 30))
    a.key("magazine", ts + 0.23, pos=along(mag_angle, 360, (-60, -200, 120)), rot=(30, 10, 30))
    a.sound(ts + 0.25, "pouch")
    ti = ts + 0.75   # moment the new magazine is seated
    a.grab("arm_left", "magazine", ts + 0.26, ti + 0.08, fade_in=0.04, fade_out=0.06)
    if style == "ak":
        a.key("magazine", ti - 0.24, pos=along(mag_angle, 70, (0, 0, -16)), rot=(-rock - 6, 2, 6), e="outcubic")
        a.key("magazine", ti - 0.12, pos=(0, -5, -6), rot=(-rock, 0, 0), e="inoutsine")   # hook the front lug
        a.key("magazine", ti, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")                  # rock it back
    else:
        a.key("magazine", ti - 0.22, pos=along(mag_angle, mag_out * 0.9, (-2, 0, 0)), rot=(4, 2, 6), e="outcubic")
        a.key("magazine", ti - 0.08, pos=along(mag_angle, mag_out * 0.3), rot=(0, 0, 0), e="inoutsine")
        a.key("magazine", ti, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
    a.sound(ti, f"mag_in_{mag_sound}")
    a.event(ti, "ammo")
    a.spring("gun", "rot", ti, (-2.5, 0.0, 1.2), freq=6, damp=9)
    a.kick("gun", "pos", ti, (0, 6, 0), attack=0.03, recover=0.2)
    # tug test
    a.key("magazine", ti + 0.08, pos=along(mag_angle, 1.5), rot=(0, 0, 0))
    a.key("magazine", ti + 0.12, pos=(0, 0, 0), rot=(0, 0, 0))
    t = ti + 0.14
    if empty:
        if locked and style == "ar":
            # palm the bolt catch
            a.mv("arm_left", t, t + 0.16, pos=(12, 30, 70), rot=(-10, 30, 40), e="inoutsine")
            a.key(bolt, t + 0.18, pos=bolt_travel)
            a.key(bolt, t + 0.22, pos=(0, 0, 0), e="inquad")
            a.sound(t + 0.2, "bolt_release")
            a.spring("gun", "rot", t + 0.22, (1.6, 0, -1.6), freq=6, damp=8)
            a.mv("arm_left", t + 0.26, t + 0.55, pos=(0, 0, 0), rot=(0, 0, 0))
            _settle(a, t + 0.26, L - 0.02)
        else:
            chb = ch or bolt
            # rack the charging handle
            if ch_hand == "right":
                a.mv("arm_left", t, t + 0.3, pos=(0, 0, 0), rot=(0, 0, 0))
                a.mv("gun", t, t + 0.2, pos=(-10, 10, 18), rot=(2, -8, -36))
                a.mv("arm_right", t + 0.02, t + 0.18, pos=(8, 40, -40), rot=(-30, -10, -20))
                hand = "arm_right"
            else:
                a.mv("arm_left", t, t + 0.18, pos=(10, 46, 20), rot=(-30, 20, 30))
                a.mv("gun", t, t + 0.2, pos=(-10, 10, 18), rot=(2, -4, 14))
                hand = "arm_left"
            if chb:
                a.grab(hand, chb, t + 0.18, t + 0.34, fade_in=0.02, fade_out=0.05)
                a.key(chb, t + 0.18, pos=(0, 0, 0) if not locked or chb != bolt else bolt_travel)
                a.key(chb, t + 0.3, pos=ch_travel if chb == ch else bolt_travel, e="inoutquad")
                if bolt and chb != bolt:
                    a.key(bolt, t + 0.18, pos=(0, 0, 0) if not locked else bolt_travel)
                    a.key(bolt, t + 0.3, pos=bolt_travel, e="inoutquad")
                    a.key(bolt, t + 0.36, pos=(0, 0, 0), e="inquad")
                a.sound(t + 0.28, "charging_handle_back")
                if style == "hk":
                    a.key(chb, t + 0.34, pos=(0, 0, 0), e="inquad")
                else:
                    a.key(chb, t + 0.36, pos=(0, 0, 0), e="inquad")
                a.sound(t + 0.36, "charging_handle_forward")
            if style == "hk":
                # the HK slap: lever is already locked back, slap it down
                pass
            a.spring("gun", "rot", t + 0.36, (1.6, 0, -1.6), freq=6, damp=8)
            a.mv(hand, t + 0.38, t + 0.65, pos=(0, 0, 0), rot=(0, 0, 0))
            _settle(a, t + 0.4, L - 0.02)
    else:
        if style == "hk" and m.has("charging_handle"):
            # slap the lever down
            a.mv("arm_left", t, t + 0.18, pos=(10, 50, -30), rot=(-20, -20, 30))
            a.key("charging_handle", t + 0.18, pos=np.asarray(ch_travel) + (0, 6, 0))
            a.key("charging_handle", t + 0.22, pos=(0, 0, 0), e="inquad")
            if bolt:
                a.key(bolt, t + 0.18, pos=bolt_travel)
                a.key(bolt, t + 0.23, pos=(0, 0, 0), e="inquad")
            a.sound(t + 0.21, "hk_slap")
            a.spring("gun", "rot", t + 0.22, (2.0, 0, -2.0), freq=6, damp=8)
            a.mv("arm_left", t + 0.24, t + 0.55, pos=(0, 0, 0), rot=(0, 0, 0))
            _settle(a, t + 0.28, L - 0.02)
        else:
            a.mv("arm_left", t, t + 0.35, pos=(0, 0, 0), rot=(0, 0, 0))
            _settle(a, t + 0.05, L - 0.02)
    return a


def hk_slap_fix(a):
    return a


# ------------------------------------------------------------------------------------------------
# Manual actions
# ------------------------------------------------------------------------------------------------
def bolt_cycle(m, name, bolt="bolt", handle_rot=(0, 0, 70), travel=(0, 0, 85), length=0.85, aim=False):
    """Bolt action: lift, pull, push, lower. Right hand works the bolt."""
    a = Anim(m, name, length)
    a.mv("gun", 0.0, 0.12, pos=(-8, 2, 10), rot=(1, -2, -8) if not aim else (0.5, -1, -3))
    a.mv("arm_right", 0.0, 0.12, pos=(20, 40, -30), rot=(-25, -20, -20))
    a.grab("arm_right", bolt, 0.12, 0.66, fade_in=0.03, fade_out=0.06)
    a.key(bolt, 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
    a.key(bolt, 0.12, pos=(0, 0, 0), rot=(0, 0, 0))
    a.key(bolt, 0.2, pos=(0, 0, 0), rot=handle_rot, e="outquad")
    a.sound(0.18, "bolt_open")
    a.key(bolt, 0.34, pos=travel, rot=handle_rot, e="inoutquad")
    a.sound(0.33, "bolt_back")
    a.key(bolt, 0.48, pos=(0, 0, 0), rot=handle_rot, e="inoutquad")
    a.sound(0.47, "bolt_forward")
    a.key(bolt, 0.58, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
    a.sound(0.57, "bolt_close")
    if m.has("brass"):
        a.show("brass", 0.0, 0.62)
        a.key("brass", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("brass", 0.3, pos=(0, 0, 0))
        a.key("brass", 0.36, pos=(10, 25, 40), rot=(30, 0, -60), e="outquad")
        a.key("brass", 0.62, pos=(160, -120, 220), rot=(200, 0, -300), e="inquad")
    a.spring("gun", "rot", 0.34, (-0.8, 0.6, 0), freq=5, damp=9)
    a.spring("gun", "rot", 0.48, (0.8, -0.6, 0), freq=5, damp=9)
    a.mv("arm_right", 0.62, 0.8, pos=(0, 0, 0), rot=(0, 0, 0))
    a.mv("gun", 0.6, length - 0.01, pos=(0, 0, 0), rot=(0, 0, 0))
    return a


def pump_cycle(m, name, pump="pump", travel=(0, 0, 80), length=0.6, aim=False):
    a = Anim(m, name, length)
    k = 0.5 if aim else 1.0
    a.grab("arm_left", pump, 0.0, 0.5, fade_in=0.0, fade_out=0.05)
    a.key(pump, 0.0, pos=(0, 0, 0))
    a.key(pump, 0.08, pos=(0, 0, 0))
    a.key(pump, 0.2, pos=travel, e="outquad")
    a.sound(0.18, "pump_back")
    a.key(pump, 0.34, pos=(0, 0, 0), e="inquad")
    a.sound(0.33, "pump_forward")
    a.mv("gun", 0.05, 0.2, pos=(-4 * k, -3 * k, 6 * k), rot=(-2 * k, 0, -6 * k))
    a.mv("gun", 0.24, 0.5, pos=(0, 0, 0), rot=(0, 0, 0))
    a.spring("gun", "rot", 0.34, (1.2 * k, 0, 0.8 * k), freq=6, damp=9)
    if m.has("shell_eject"):
        a.show("shell_eject", 0.17, 0.5)
        a.key("shell_eject", 0.17, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("shell_eject", 0.24, pos=(30, 30, 20), rot=(0, 0, -80), e="outquad")
        a.key("shell_eject", 0.5, pos=(200, -100, 200), rot=(120, 0, -320), e="inquad")
    return a


# ------------------------------------------------------------------------------------------------
# Shell-by-shell (tube shotguns, internal-mag bolt rifles)
# ------------------------------------------------------------------------------------------------
def tube_reload(m, port_tilt=(14, 6, -38), port_pos=(-30, 30, 40), load_bone="shell_load", empty_extra=None,
                loop_len=0.52, push=(0, 0, -45), sound="shell_insert", prefix="reload"):
    """Returns [reload_start, reload_loop, reload_end]. load_bone sits at the loading port at rest."""
    s = Anim(m, f"{prefix}_start", 0.45)
    s.mv("gun", 0.0, 0.32, pos=port_pos, rot=port_tilt)
    s.mv("arm_left", 0.0, 0.18, pos=(-10, -40, 40), rot=(10, 0, 0))
    s.mv("arm_left", 0.18, 0.42, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
    s.sound(0.05, "cloth")
    s.hide(load_bone)

    lp = Anim(m, f"{prefix}_loop", loop_len, rest={"gun": {"pos": port_pos, "rot": port_tilt},
                                                   "arm_left": {"pos": OFF_LEFT, "rot": OFF_LEFT_ROT}})
    lp.show(load_bone, 0.02, loop_len * 0.78)
    lp.at_hand(load_bone, 0.0, rot=(40, 0, 30))
    lp.at_hand(load_bone, 0.02, rot=(40, 0, 30))
    lp.grab("arm_left", load_bone, 0.03, loop_len * 0.72, fade_in=0.02, fade_out=0.05)
    lp.key(load_bone, loop_len * 0.5, pos=(0, -6, 6), rot=(6, 0, 0), e="outcubic")
    lp.key(load_bone, loop_len * 0.62, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")
    lp.key(load_bone, loop_len * 0.76, pos=push, rot=(0, 0, 0), e="inquad")
    lp.sound(loop_len * 0.72, sound)
    lp.event(loop_len * 0.72, "ammo")
    lp.kick("gun", "pos", loop_len * 0.72, (0, 3, -3), attack=0.02, recover=0.14)
    lp.spring("gun", "rot", loop_len * 0.72, (0.8, 0, 0.8), freq=7, damp=10)
    lp.mv("arm_left", loop_len * 0.78, loop_len, pos=OFF_LEFT, rot=OFF_LEFT_ROT, e="inoutsine")

    e = Anim(m, f"{prefix}_end", 0.55, rest={"gun": {"pos": port_pos, "rot": port_tilt},
                                            "arm_left": {"pos": OFF_LEFT, "rot": OFF_LEFT_ROT}})
    e.mv("arm_left", 0.0, 0.35, pos=(0, 0, 0), rot=(0, 0, 0))
    e.mv("gun", 0.05, 0.5, pos=(0, 0, 0), rot=(0, 0, 0))
    e.spring("gun", "rot", 0.45, (1.0, 0, 0.6), freq=4, damp=8)
    e.hide(load_bone)
    s.hide(load_bone)
    return [s, lp, e]


def bolt_load(m, bolt="bolt", handle_rot=(0, 0, 70), travel=(0, 0, 85), load_bone="round_load"):
    """Internal magazine bolt rifle: start (open bolt), loop (thumb in a round), end (close bolt)."""
    tilt_pos, tilt = (-20, 20, 30), (6, -4, -24)
    s = Anim(m, "reload_start", 0.7)
    s.mv("gun", 0.0, 0.3, pos=tilt_pos, rot=tilt)
    s.mv("arm_right", 0.0, 0.14, pos=(20, 40, -30), rot=(-25, -20, -20))
    s.grab("arm_right", bolt, 0.14, 0.5, fade_in=0.03, fade_out=0.06)
    s.key(bolt, 0.14, pos=(0, 0, 0), rot=(0, 0, 0))
    s.key(bolt, 0.24, pos=(0, 0, 0), rot=handle_rot, e="outquad")
    s.sound(0.22, "bolt_open")
    s.key(bolt, 0.42, pos=travel, rot=handle_rot, e="inoutquad")
    s.sound(0.4, "bolt_back")
    s.mv("arm_right", 0.5, 0.68, pos=(0, 0, 0), rot=(0, 0, 0))
    s.mv("arm_left", 0.1, 0.5, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
    s.hide(load_bone)
    base = {"gun": {"pos": tilt_pos, "rot": tilt}, "arm_left": {"pos": OFF_LEFT, "rot": OFF_LEFT_ROT},
            bolt: {"pos": travel, "rot": handle_rot}}
    lp = Anim(m, "reload_loop", 0.6, rest=base)
    lp.show(load_bone, 0.02, 0.46)
    lp.at_hand(load_bone, 0.0, rot=(30, 0, 30))
    lp.at_hand(load_bone, 0.02, rot=(30, 0, 30))
    lp.grab("arm_left", load_bone, 0.03, 0.44, fade_in=0.02, fade_out=0.05)
    lp.key(load_bone, 0.3, pos=(0, 16, 4), rot=(0, 0, 4), e="outcubic")
    lp.key(load_bone, 0.42, pos=(0, -6, 0), rot=(0, 0, 0), e="inquad")
    lp.sound(0.4, "round_insert")
    lp.event(0.4, "ammo")
    lp.mv("arm_left", 0.46, 0.6, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
    e = Anim(m, "reload_end", 0.75, rest=base)
    e.mv("arm_right", 0.0, 0.14, pos=(20, 40, -30), rot=(-25, -20, -20))
    e.grab("arm_right", bolt, 0.14, 0.5, fade_in=0.03, fade_out=0.06)
    e.key(bolt, 0.16, pos=travel, rot=handle_rot)
    e.key(bolt, 0.3, pos=(0, 0, 0), rot=handle_rot, e="inoutquad")
    e.sound(0.29, "bolt_forward")
    e.key(bolt, 0.4, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
    e.sound(0.39, "bolt_close")
    e.mv("arm_right", 0.5, 0.65, pos=(0, 0, 0), rot=(0, 0, 0))
    e.mv("arm_left", 0.2, 0.6, pos=(0, 0, 0), rot=(0, 0, 0))
    e.mv("gun", 0.35, 0.74, pos=(0, 0, 0), rot=(0, 0, 0))
    e.hide(load_bone)
    return [s, lp, e]


# ------------------------------------------------------------------------------------------------
# Belt fed
# ------------------------------------------------------------------------------------------------
def belt_reload(m, name, empty, cover_rot=(75, 0, 0), box_drop=(0, -260, 40), ch="charging_handle",
                ch_travel=(0, 0, 110), bolt="bolt", length=None):
    L = length or (5.2 if empty else 4.6)
    a = Anim(m, name, L)
    if empty and m.has(bolt):
        a.key(bolt, 0.0, pos=(0, 0, 0))
    # 1. cant the gun, hand to the feed cover latch
    a.mv("gun", 0.0, 0.4, pos=(-30, 20, 40), rot=(8, -10, 22))
    a.mv("arm_left", 0.05, 0.4, pos=(40, 120, 230), rot=(-40, 10, 20))
    a.grab("arm_left", "cover", 0.42, 0.8, fade_in=0.03, fade_out=0.06)
    a.key("cover", 0.42, rot=(0, 0, 0))
    a.key("cover", 0.52, rot=(4, 0, 0), e="outquad")
    a.sound(0.5, "cover_open")
    a.key("cover", 0.78, rot=cover_rot, e="outback")
    # 2. strip the old belt, unlatch & drop the box
    a.mv("arm_left", 0.85, 1.1, pos=(10, 60, 180), rot=(-20, 0, 20))
    a.grab("arm_left", "belt", 1.1, 1.4, fade_in=0.03, fade_out=0.04)
    a.key("belt", 1.1, pos=(0, 0, 0), rot=(0, 0, 0))
    a.key("belt", 1.38, pos=(-30, 30, 0), rot=(0, 0, 30), e="inoutsine")
    a.sound(1.25, "belt_rattle")
    a.show("belt", 0.0, 1.4)
    a.mv("arm_left", 1.4, 1.62, pos=box_drop, rot=(10, 0, 0))
    a.grab("arm_left", "box", 1.62, 1.95, fade_in=0.05, fade_out=0.06)
    a.key("box", 0.0, pos=(0, 0, 0), rot=(0, 0, 0))
    a.key("box", 1.64, pos=(0, 0, 0), rot=(0, 0, 0))
    a.key("box", 1.72, pos=(0, -10, 0), rot=(0, 0, 0), e="outquad")
    a.sound(1.7, "box_out")
    a.key("box", 1.95, pos=(-40, -300, 120), rot=(20, 0, 20), e="inquad")
    a.mv("arm_left", 1.98, 2.25, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
    a.key("box", 2.25, pos=(-60, -380, 160), rot=(30, 0, 20))
    a.grab("arm_left", "box", 2.3, 2.9, fade_in=0.06, fade_out=0.06)
    a.key("box", 2.72, pos=(0, -16, 0), rot=(2, 0, 0), e="outcubic")
    a.key("box", 2.82, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")
    a.sound(2.82, "box_in")
    a.spring("gun", "rot", 2.82, (-1.6, 0, 1.0), freq=6, damp=9)
    # 3. lay the new belt on the feed tray
    a.mv("arm_left", 2.95, 3.2, pos=(10, 60, 180), rot=(-20, 0, 20))
    a.show("belt", 3.2)
    a.key("belt", 3.2, pos=(-30, 30, 0), rot=(0, 0, 30))
    a.grab("arm_left", "belt", 3.22, 3.55, fade_in=0.03, fade_out=0.05)
    a.key("belt", 3.5, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")
    a.sound(3.48, "belt_seat")
    a.event(3.5, "ammo")
    # 4. slam the cover
    a.mv("arm_left", 3.55, 3.78, pos=(30, 150, 220), rot=(-50, 10, 20))
    a.key("cover", 3.7, rot=cover_rot)
    a.key("cover", 3.86, rot=(0, 0, 0), e="inquad")
    a.sound(3.86, "cover_close")
    a.spring("gun", "rot", 3.86, (-2.6, 0, 1.2), freq=6, damp=8)
    a.spring("cover", "rot", 3.86, (-2.0, 0, 0), freq=14, damp=18)
    t = 3.95
    if empty and m.has(ch):
        a.mv("arm_left", t, t + 0.18, pos=(0, 0, 0), rot=(0, 0, 0))
        a.mv("arm_right", t, t + 0.2, pos=(30, 30, -120), rot=(-20, -20, -20))
        a.grab("arm_right", ch, t + 0.2, t + 0.48, fade_in=0.02, fade_out=0.06)
        a.key(ch, t + 0.2, pos=(0, 0, 0))
        a.key(ch, t + 0.36, pos=ch_travel, e="inoutquad")
        a.sound(t + 0.34, "charging_handle_back")
        a.key(ch, t + 0.48, pos=(0, 0, 0), e="inoutsine")
        if m.has(bolt):
            a.key(bolt, t + 0.2, pos=(0, 0, 0))
            a.key(bolt, t + 0.36, pos=ch_travel)
        a.mv("arm_right", t + 0.5, t + 0.72, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, t + 0.5, L - 0.02)
    else:
        a.mv("arm_left", t, t + 0.4, pos=(0, 0, 0), rot=(0, 0, 0))
        _settle(a, t + 0.1, L - 0.02)
    return a


# ------------------------------------------------------------------------------------------------
# Stripper clips (Mosin, Mauser-pattern bolt rifles, SKS)
# ------------------------------------------------------------------------------------------------
def clip_stage(m, rest, clip="clip", clip_rounds="clip_rounds", push=50.0, length=1.55, name="reload_clip",
               thumb_rot=(-30, 0, 20)):
    """
    One stripper clip: the support hand brings a clip from the pouch, seats it in the charger guide, thumbs all the
    rounds down into the magazine in one stroke and plucks the empty clip out. `rest` is the open-action pose the
    surrounding reload stages hold. The 'ammo' event is the moment the rounds clear the clip.
    """
    a = Anim(m, name, length, rest=rest)
    a.show(clip, 0.02, 1.32)
    a.show(clip_rounds, 0.02, 1.0)
    a.at_hand(clip, 0.0, rot=(30, 0, 40))
    a.at_hand(clip, 0.02, rot=(30, 0, 40))
    a.grab("arm_left", clip, 0.04, 0.58, fade_in=0.03, fade_out=0.04)
    a.key(clip, 0.38, pos=(-4, 36, -6), rot=(-8, 0, 6), e="outcubic")      # line up over the guide
    a.key(clip, 0.5, pos=(0, 6, 0), rot=(0, 0, 0), e="inoutsine")
    a.key(clip, 0.56, pos=(0, 0, 0), rot=(0, 0, 0), e="inquad")            # click into the charger guide
    a.sound(0.55, "clip_insert")
    a.kick("gun", "pos", 0.56, (0, -3, 0), attack=0.02, recover=0.12)
    # thumb goes on top of the rounds and strips them down — a stiff first push, then they rush into the well
    p, r = a.pin("arm_left", 0.58)
    a.key("arm_left", 0.64, pos=p + np.array([4.0, 26.0, 24.0]), rot=r + np.array([-24.0, 0, 10]))
    a.grab("arm_left", clip_rounds, 0.64, 0.96, fade_in=0.0, fade_out=0.05)
    a.key(clip_rounds, 0.0, pos=(0, 0, 0))
    a.key(clip_rounds, 0.66, pos=(0, 0, 0))
    a.key(clip_rounds, 0.76, pos=(0, -push * 0.22, 0), e="inquad")
    a.key(clip_rounds, 0.82, pos=(0, -push * 0.28, 0), e="linear")
    a.key(clip_rounds, 0.94, pos=(0, -push, 0), e="outquad")
    a.sound(0.7, "clip_strip")
    a.event(0.94, "ammo")
    a.kick("gun", "pos", 0.7, (0, -6, 0), attack=0.05, recover=0.3)
    a.spring("gun", "rot", 0.94, (-1.8, 0, 0.8), freq=6, damp=9)
    # pluck the empty clip and toss it
    p, r = a.pin("arm_left", 0.96)
    a.key("arm_left", 1.02, pos=p + np.array([0.0, 30.0, -10.0]), rot=r + np.array([20.0, 0, -10]))
    a.grab("arm_left", clip, 1.02, 1.2, fade_in=0.0, fade_out=0.04)
    a.key(clip, 1.04, pos=(0, 0, 0), rot=(0, 0, 0))
    a.key(clip, 1.12, pos=(0, 40, 4), rot=(0, 0, 0), e="outquad")
    a.sound(1.1, "clip_eject")
    a.key(clip, 1.3, pos=(-90, 60, 60), rot=(30, 0, 120), e="inquad")
    a.pin("arm_left", 1.22)
    a.mv("arm_left", 1.22, length, pos=OFF_LEFT, rot=OFF_LEFT_ROT, e="inoutsine")
    return a


def bolt_clip_load(m, bolt="bolt", handle_rot=(0, 0, 70), travel=(0, 0, 85), load_bone="round_load",
                   push=50.0, follow=()):
    """Bolt rifle with charger guides: [reload_start, reload_clip, reload_loop, reload_end]."""
    s, lp, e = bolt_load(m, bolt=bolt, handle_rot=handle_rot, travel=travel, load_bone=load_bone)
    rest = dict(lp.rest)
    c = clip_stage(m, rest, push=push)
    for a in (s, lp, e):
        a.hide("clip")
        a.hide("clip_rounds")
    return [s, c, lp, e]


def carrier_clip_load(m, carrier="bolt", travel=(0, 0, 100), load_bone="round_load", push=46.0,
                      tilt_pos=(-20, 20, 30), tilt=(6, -4, -24)):
    """Semi-auto with a carrier-mounted charger guide (SKS): carrier is locked back, clips, then released."""
    s = Anim(m, "reload_start", 0.7)
    s.mv("gun", 0.0, 0.3, pos=tilt_pos, rot=tilt)
    s.mv("arm_right", 0.0, 0.16, pos=(24, 52, -60), rot=(-30, -20, -24))
    s.grab("arm_right", carrier, 0.16, 0.46, fade_in=0.03, fade_out=0.06)
    s.key(carrier, 0.16, pos=(0, 0, 0))
    s.key(carrier, 0.36, pos=np.asarray(travel) * 1.04, e="inoutquad")
    s.key(carrier, 0.42, pos=travel, e="outquad")                    # rides forward onto the hold-open
    s.sound(0.32, "charging_handle_back")
    s.sound(0.42, "bolt_release")
    s.spring("gun", "rot", 0.42, (0.8, 0, -0.8), freq=7, damp=10)
    s.mv("arm_right", 0.5, 0.68, pos=(0, 0, 0), rot=(0, 0, 0))
    s.mv("arm_left", 0.1, 0.5, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
    rest = {"gun": {"pos": tilt_pos, "rot": tilt}, "arm_left": {"pos": OFF_LEFT, "rot": OFF_LEFT_ROT},
            carrier: {"pos": travel}}
    c = clip_stage(m, rest, push=push)
    lp = Anim(m, "reload_loop", 0.6, rest=rest)
    lp.show(load_bone, 0.02, 0.46)
    lp.at_hand(load_bone, 0.0, rot=(30, 0, 30))
    lp.at_hand(load_bone, 0.02, rot=(30, 0, 30))
    lp.grab("arm_left", load_bone, 0.03, 0.44, fade_in=0.02, fade_out=0.05)
    lp.key(load_bone, 0.3, pos=(0, 16, 4), rot=(0, 0, 4), e="outcubic")
    lp.key(load_bone, 0.42, pos=(0, -10, 0), rot=(0, 0, 0), e="inquad")
    lp.sound(0.4, "round_insert")
    lp.event(0.4, "ammo")
    lp.mv("arm_left", 0.46, 0.6, pos=OFF_LEFT, rot=OFF_LEFT_ROT)
    e = Anim(m, "reload_end", 0.8, rest=rest)
    # tug the carrier off the hold-open and let it fly
    e.mv("arm_right", 0.0, 0.16, pos=(24, 52, -60), rot=(-30, -20, -24))
    e.grab("arm_right", carrier, 0.16, 0.3, fade_in=0.03, fade_out=0.04)
    e.key(carrier, 0.16, pos=travel)
    e.key(carrier, 0.26, pos=np.asarray(travel) * 1.05, e="outquad")
    e.key(carrier, 0.32, pos=(0, 0, 0), e="inquad")
    e.sound(0.31, "charging_handle_forward")
    e.spring("gun", "rot", 0.32, (1.8, 0, -1.4), freq=6, damp=8)
    e.spring(carrier, "pos", 0.32, np.asarray(travel) * -0.04, freq=30, damp=40, dur=0.08)
    e.mv("arm_right", 0.36, 0.56, pos=(0, 0, 0), rot=(0, 0, 0))
    e.mv("arm_left", 0.2, 0.62, pos=(0, 0, 0), rot=(0, 0, 0))
    e.mv("gun", 0.36, 0.79, pos=(0, 0, 0), rot=(0, 0, 0))
    for a in (s, lp, e):
        a.hide("clip")
        a.hide("clip_rounds")
        a.hide(load_bone)
    s.hide(load_bone)
    return [s, c, lp, e]


def follow_pos(anims, src, dst, scale=1.0):
    """Make `dst` copy the translation of `src` in every animation (e.g. an Arisaka dust cover riding the bolt)."""
    import copy
    for a in anims:
        if (src, "pos") in a.tracks and (dst, "pos") not in a.tracks:
            a.tracks[(dst, "pos")] = copy.deepcopy(a.tracks[(src, "pos")])
            if scale != 1.0:
                tr = a.tracks[(dst, "pos")]
                tr.keys = [(t, v * scale if isinstance(v, np.ndarray) else v, e) for t, v, e in tr.keys]
            for lb, lch, fn in list(a.layers):
                if lb == src and lch == "pos":
                    a.layers.append((dst, "pos", fn))
        if src in a.rest and "pos" in a.rest[src]:
            a.rest.setdefault(dst, {})["pos"] = a.rest[src]["pos"]


# ------------------------------------------------------------------------------------------------
# Lever actions (Winchester 1894, Marlin 336)
# ------------------------------------------------------------------------------------------------
def lever_cycle(m, name, lever="lever", lever_rot=(62, 0, 0), bolt="bolt", travel=(0, 0, 72), hammer="hammer",
                hammer_down=(-38, 0, 0), length=0.72, aim=False, eject=(10, 160, 60), eject_rot=(-120, 0, 30)):
    """Throw the lever down and forward with the hand inside the loop: bolt runs back, hammer is cocked,
    the empty case flies, then the lever snaps closed and a fresh round is chambered."""
    a = Anim(m, name, length)
    k = 0.5 if aim else 1.0
    a.grab("arm_right", lever, 0.04, length - 0.12, fade_in=0.04, fade_out=0.08)
    a.key(lever, 0.0, rot=(0, 0, 0))
    a.key(lever, 0.06, rot=(0, 0, 0))
    a.key(lever, 0.22, rot=lever_rot, e="outquad")
    a.sound(0.1, "lever_open")
    a.key(lever, 0.3, rot=np.asarray(lever_rot) * 1.03)
    a.key(lever, 0.46, rot=(0, 0, 0), e="inquad")
    a.sound(0.45, "lever_close")
    a.spring(lever, "rot", 0.46, (-3.0, 0, 0), freq=14, damp=16)
    if m.has(bolt):
        a.key(bolt, 0.0, pos=(0, 0, 0))
        a.key(bolt, 0.07, pos=(0, 0, 0))
        a.key(bolt, 0.22, pos=travel, e="outquad")
        a.key(bolt, 0.3, pos=travel)
        a.key(bolt, 0.45, pos=(0, 0, 0), e="inquad")
    if m.has(hammer):
        a.key(hammer, 0.0, rot=hammer_down)
        a.key(hammer, 0.08, rot=hammer_down)
        a.key(hammer, 0.2, rot=(8, 0, 0), e="outquad")       # pushed past full cock by the bolt
        a.key(hammer, 0.46, rot=(8, 0, 0))
        a.key(hammer, 0.5, rot=(0, 0, 0), e="outquad")       # settles on the sear
    if m.has("brass"):
        a.show("brass", 0.15, 0.62)
        a.key("brass", 0.15, pos=(0, 0, 0), rot=(0, 0, 0))
        a.key("brass", 0.24, pos=np.asarray(eject) * 0.2, rot=np.asarray(eject_rot) * 0.2, e="outquad")
        a.key("brass", 0.62, pos=eject, rot=eject_rot, e="linear")
    # the rifle dips and rolls a touch as the lever is thrown; the support hand holds it steady
    a.mv("gun", 0.0, 0.2, pos=(-2 * k, -6 * k, 4 * k), rot=(-3 * k, 1 * k, -5 * k))
    a.mv("gun", 0.26, 0.5, pos=(0, 2 * k, 0), rot=(1.5 * k, 0, 2 * k))
    a.mv("gun", 0.5, length - 0.01, pos=(0, 0, 0), rot=(0, 0, 0))
    a.spring("gun", "rot", 0.46, (1.4 * k, 0, -1.0 * k), freq=6, damp=9)
    return a


def lever_fire(m, name, kick, push, recover=0.3, length=0.4, aim=False, hammer="hammer", hammer_down=(-38, 0, 0)):
    """Fire for an exposed-hammer gun whose hammer stays down until the action is cycled."""
    from .common import fire_basic
    a = fire_basic(m, name, kick=kick, push=push, recover=recover, length=length, aim=aim)
    if m.has(hammer):
        a.key(hammer, 0.0, rot=(0, 0, 0))
        a.key(hammer, 0.014, rot=hammer_down, e="inquad")
        a.spring(hammer, "rot", 0.014, (-4, 0, 0), freq=20, damp=24)
        a.key(hammer, length, rot=hammer_down)
    return a
