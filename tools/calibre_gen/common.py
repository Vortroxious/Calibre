"""Shared builders for gun assets: bone contract, arms, metadata, standard animation templates."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .core import Model, Anim


@dataclass
class GunAsset:
    model: Model
    anims: list
    meta: dict = field(default_factory=dict)


def new_gun(name, grip=(0.0, -40.0, 20.0)):
    """Creates root > gun > body plus empty arm bones. `grip` is the right-hand pivot."""
    m = Model(name)
    gun = m.root.bone("gun", pivot=(0, 0, 0))
    gun.bone("body", pivot=(0, 0, 0))
    return m


def add_arms(m: Model, right_hand, left_hand, right_rot=(30, 20, 0), left_rot=(28, -22, 0)):
    gun = m["gun"]
    gun.bone("arm_right", pivot=right_hand, rot=right_rot)
    gun.bone("arm_left", pivot=left_hand, rot=left_rot)


def add_sockets(m: Model, muzzle, optic=None, under=None, side=None, eject=None, sight=None, parent="body"):
    p = m[parent]
    p.bone("muzzle", pivot=muzzle)
    if optic is not None:
        p.bone("mount_optic", pivot=optic)
    if under is not None:
        p.bone("mount_under", pivot=under)
    if side is not None:
        p.bone("mount_side", pivot=side)
    m.meta["muzzle"] = list(muzzle)
    if eject is not None:
        m.meta["eject"] = list(eject)
    if sight is not None:
        m.meta["sight"] = list(sight)


# ------------------------------------------------------------------------------------------------
# Small controls that move by themselves wherever a gun has the bone
# ------------------------------------------------------------------------------------------------
def moving(m: Model, bone, pos=None, rot=None):
    """Declare how a small control moves when it is worked (pressed / flipped / popped up)."""
    m.moves[bone] = {k: tuple(v) for k, v in (("pos", pos), ("rot", rot)) if v is not None}


def part_move(m: Model, bone, default):
    return m.moves.get(bone) or default


def _sound_time(a, prefix):
    ts = [t for t, n in a.sounds if n.startswith(prefix)]
    return min(ts) if ts else None


def auto_moving_parts(asset):
    """
    mag_release: pressed as the magazine leaves.  bolt_catch / slide_stop: up on the last round and while the gun is
    empty, down when the bolt or slide is let go. Any gun that has the bone gets the motion; a gun that keys the bone
    itself is left alone.
    """
    m = asset.model
    if m.follow:
        from .templates import follow_pos
        for src, dst in m.follow:
            follow_pos(asset.anims, src, dst)
    for a in asset.anims:
        def free(bone):
            return m.has(bone) and (bone, "pos") not in a.tracks and (bone, "rot") not in a.tracks

        if a.name in ("reload", "reload_empty") and free("mag_release"):
            ts = _sound_time(a, "mag_out")
            if ts is not None:
                px = m["mag_release"].pivot[0]
                d = part_move(m, "mag_release", {"pos": (-1.6 if px > 1 else (1.6 if px < -1 else 0), 0 if abs(px) > 1 else 1.6, 0)})
                zero = {k: (0, 0, 0) for k in d}
                a.key("mag_release", max(0.0, ts - 0.07), **zero)
                a.key("mag_release", ts, e="outquad", **d)
                a.key("mag_release", ts + 0.16, **d)
                a.key("mag_release", ts + 0.24, e="outquad", **zero)
        for bone, snd, default in (("bolt_catch", "bolt_release", {"pos": (0, 3.5, 0)}),
                                   ("slide_stop", "slide_release", {"pos": (0, 2.5, 0)})):
            if not free(bone):
                continue
            d = part_move(m, bone, default)
            zero = {k: (0, 0, 0) for k in d}
            if a.name == "fire_last":
                a.key(bone, 0.0, **zero)
                a.key(bone, 0.045, e="outquad", **d)
            elif a.name == "idle_empty":
                a.key(bone, 0.0, **d)
            elif a.name == "reload_empty":
                tr = _sound_time(a, snd) or _sound_time(a, "charging_handle_forward") or a.length * 0.8
                a.key(bone, 0.0, **d)
                a.key(bone, max(0.01, tr - 0.05), **d)
                a.key(bone, tr, e="inquad", **zero)
    return asset


def axis_vec(rx_deg):
    """Unit vector pointing 'down the magazine' for a mag well tilted by rx (neg = bottom goes back)."""
    a = math.radians(rx_deg)
    # R_x(a) applied to (0,-1,0)
    return np.array([0.0, -math.cos(a), -math.sin(a)])


def along(rx_deg, dist, extra=(0, 0, 0)):
    return tuple(axis_vec(rx_deg) * dist + np.asarray(extra, dtype=float))


# ------------------------------------------------------------------------------------------------
# Generic animation pieces
# ------------------------------------------------------------------------------------------------
def idle(m, name="idle", locked=None, extra_hidden=()):
    a = Anim(m, name, 4.0, loop=True)
    a.wave("gun", "pos", (0.25, 0.6, 0.0), 4.0)
    a.wave("gun", "rot", (0.35, 0.0, 0.15), 4.0, phase=1.1)
    a.wave("arm_left", "pos", (0.0, 0.25, 0.0), 2.0, phase=0.4)
    if locked:
        for bone, pos in locked.items():
            a.key(bone, 0.0, pos=pos)
    for b in extra_hidden:
        a.hide(b)
    return a


def apply_hidden(anims, bones):
    """Hide spare parts in every animation that doesn't explicitly key their scale."""
    for a in anims:
        for b in bones:
            if b in a.model.bones and (b, "scale") not in a.tracks:
                a.hide(b)


def draw(m, length=0.75, sound="draw_rifle", style="rifle", locked=None):
    a = Anim(m, "draw", length)
    if style == "pistol":
        a.key("gun", 0.0, pos=(40, -170, 60), rot=(-55, 10, -35))
    else:
        a.key("gun", 0.0, pos=(60, -260, 120), rot=(-40, 25, -45))
    a.key("gun", length * 0.62, pos=(0, 4, -4), rot=(3, 0, 1.5), e="outcubic")
    a.key("gun", length, pos=(0, 0, 0), rot=(0, 0, 0), e="inoutsine")
    a.key("arm_left", 0.0, pos=(-60, -160, 100), rot=(30, -10, 10))
    a.key("arm_left", length * 0.25, pos=(-60, -160, 100), rot=(30, -10, 10))
    a.key("arm_left", length * 0.8, pos=(0, 0, 0), rot=(0, 0, 0), e="outcubic")
    a.spring("gun", "rot", length * 0.62, (1.5, 0, 0.8), freq=3, damp=7)
    a.sound(0.0, sound)
    if locked:
        for bone, pos in locked.items():
            a.key(bone, 0.0, pos=pos)
    return a


def fire_basic(m, name, kick=(4.0, 0.0, 0.0), push=12.0, cycle=None, recover=0.22, length=0.3, aim=False,
               hammer=None, trigger=True, lock_back=False):
    """
    cycle: dict(bone=..., travel=(x,y,z), t_back, t_fwd)  — slide/bolt reciprocation.
    lock_back: leave the reciprocating part to the rear (last round).
    """
    a = Anim(m, name, length)
    k = 0.45 if aim else 1.0
    a.kick("gun", "rot", 0.0, (kick[0] * k, kick[1] * k, kick[2] * k), attack=0.022, recover=recover)
    a.kick("gun", "pos", 0.0, (0, push * 0.12 * k, push * k), attack=0.02, recover=recover * 0.9)
    if not aim:
        a.spring("gun", "rot", 0.03, (0.6, 0.0, 0.9), freq=7, damp=10)
    if cycle:
        b = cycle["bone"]
        tb, tf = cycle.get("t_back", 0.025), cycle.get("t_fwd", 0.06)
        a.key(b, 0.0, pos=(0, 0, 0))
        a.key(b, tb, pos=cycle["travel"], e="outquad")
        if lock_back:
            a.key(b, length, pos=cycle["travel"])
        else:
            a.key(b, tf, pos=(0, 0, 0), e="inquad")
            a.spring(b, "pos", tf, np.asarray(cycle["travel"]) * -0.04, freq=30, damp=40, dur=0.08)
    if trigger and m.has("trigger"):
        a.key("trigger", 0.0, rot=(-12, 0, 0))
        a.key("trigger", 0.08, rot=(0, 0, 0), e="outquad")
    if hammer and m.has("hammer"):
        a.key("hammer", 0.0, rot=(0, 0, 0))
        a.key("hammer", 0.012, rot=(hammer, 0, 0), e="inquad")
        if lock_back:
            a.key("hammer", 0.03, rot=(0, 0, 0), e="outquad")
        else:
            a.key("hammer", 0.032, rot=(0, 0, 0), e="outquad")  # slide re-cocks it
    return a


def dry_fire(m):
    a = Anim(m, "dry", 0.25)
    if m.has("trigger"):
        a.key("trigger", 0.0, rot=(0, 0, 0))
        a.key("trigger", 0.05, rot=(-12, 0, 0))
        a.key("trigger", 0.18, rot=(0, 0, 0))
    a.kick("gun", "rot", 0.05, (0.4, 0, 0), attack=0.02, recover=0.12)
    a.sound(0.05, "dry_fire")
    return a


def firemode(m, selector_rot=(0, 0, 40), thumb_side="right", length=0.55):
    a = Anim(m, "firemode", length)
    a.mv("gun", 0.0, 0.14, rot=(2, -4, 7), pos=(-4, 3, 4))
    if thumb_side == "right":
        a.mv("arm_right", 0.04, 0.16, pos=(-2, 6, -6), rot=(0, -4, 3))
        a.mv("arm_right", 0.26, 0.42, pos=(0, 0, 0), rot=(0, 0, 0))
    else:
        a.mv("arm_left", 0.0, 0.16, pos=(28, 8, 60), rot=(-8, 15, 0))
        a.mv("arm_left", 0.3, 0.48, pos=(0, 0, 0), rot=(0, 0, 0))
    if m.has("selector"):
        a.key("selector", 0.0, rot=(0, 0, 0))
        a.key("selector", 0.19, rot=(0, 0, 0))
        a.key("selector", 0.23, rot=selector_rot, e="outquad")
        a.key("selector", length, rot=selector_rot)
    a.sound(0.21, "selector")
    a.mv("gun", 0.24, length, rot=(0, 0, 0), pos=(0, 0, 0))
    a.spring("gun", "rot", 0.21, (0.6, 0, 0.6), freq=8, damp=12)
    return a


def meta_actions(anims):
    out = {}
    for a in anims:
        out[a.name] = {
            "length": round(a.length, 3),
            "sounds": [[t, s] for t, s in sorted(a.sounds)],
            "events": [[t, e] for t, e in sorted(a.events)],
        }
    return out
