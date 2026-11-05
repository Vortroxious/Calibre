"""CS2-style camera motion for weapon animations.

The view (not the viewmodel, not the player's aim) moves a little with every weapon action:
  - a soft sway that follows the gun, lagging just behind the hands
  - a small jolt on each impact (magazine seated, bolt slammed home, cover shut...), timed from the sound timeline
  - a short, quickly dying shake on each shot

Output per animation: (rate, [[pitch, yaw, roll], ...]) in degrees, in Minecraft camera terms (pitch + = look down,
yaw + = turn right). Ends are exactly 0 so nothing jumps when an animation stops; the client fades it on interrupts.
"""
import math

import numpy as np

from . import motion

RATE = 30          # Hz (fire animations use SHOT_RATE so the shake survives)
SHOT_RATE = 60
LIMIT = np.array([2.0, 2.0, 2.5])

# impact jolts: sound name (or prefix) -> strength in degrees of camera dip
JOLT = [
    (("mag_in", "drum_in", "box_in", "hk_slap", "slide_release", "bolt_close", "bolt_forward",
      "charging_handle_forward", "pump_forward", "cover_close", "cylinder_close", "rocket_seat", "belt_seat"), 0.55),
    (("mag_out", "drum_out", "box_out", "clip_insert", "clip_strip", "lever_close", "tap", "speedloader_insert",
      "charging_handle_lock", "cylinder_open", "cover_open", "stock_lock"), 0.32),
    (("grip", "handle_", "round_insert", "shell_insert", "press_check", "selector", "safety", "lever_open",
      "pump_back", "bolt_back", "bolt_open", "charging_handle_back", "loading_gate", "hammer", "mag_check",
      "slide_forward_light", "dust_cover", "click_small", "dry_fire"), 0.12),
]

# shot shake strength by class
SHOT = {"pistol": 0.35, "revolver": 0.6, "smg": 0.4, "rifle": 0.55, "shotgun": 0.95, "bolt": 0.9, "lever": 0.75,
        "heavy": 1.0}


def _strength(sound):
    for names, s in JOLT:
        if any(sound.startswith(n) for n in names):
            return s
    return 0.0


def _bump(x, tau):
    """Single smooth lobe that rises over ~tau and dies away: no back-and-forth."""
    x = np.maximum(x, 0.0)
    return (x / tau) * np.exp(1.0 - x / tau)


def _shot_class(asset):
    kind = motion.KIND.get(asset.model.name, "rifle")
    lo, hi = asset.model.bounds()
    if kind == "rifle" and float(hi[2] - lo[2]) < 760:
        return "smg"
    if asset.model.name == "deagle":
        return "revolver"
    return kind


def camera_track(asset, anim):
    """Returns (rate, curve[n][3]) for one animation, or None for idles."""
    if anim.name.startswith("idle"):
        return None
    L = float(anim.length)
    shot = anim.name in ("fire", "fire_aim", "fire_last")
    rate = SHOT_RATE if shot else RATE
    fine = np.arange(0.0, L + 1e-9, 1.0 / 60.0)
    anim._memo.clear()
    R = np.array([anim._final_channel("gun", "rot", t) for t in fine])
    P = np.array([anim._final_channel("gun", "pos", t) for t in fine])
    anim._memo.clear()
    # follow sway: sin() keeps it bounded and smooth through whole-turn spins
    S = np.degrees(np.sin(np.radians(R)))
    follow = np.column_stack([
        -0.07 * S[:, 0] - 0.012 * P[:, 1],      # muzzle / gun up -> look up a touch
        -0.05 * S[:, 1] + 0.010 * P[:, 0],      # muzzle swung left -> turn left a touch
        0.06 * S[:, 2],
    ])
    # lag the hands by ~50 ms and soften
    lag = 3
    follow = np.vstack([np.repeat(follow[:1], lag, axis=0), follow[:-lag]]) if len(follow) > lag else follow
    sig = 0.12 * 60
    xs = np.arange(-3 * int(sig), 3 * int(sig) + 1)
    w = np.exp(-0.5 * (xs / sig) ** 2)
    w /= w.sum()
    pad = len(xs) // 2
    follow = np.column_stack([np.convolve(np.pad(follow[:, c], pad, mode="edge"), w, mode="valid")
                              for c in range(3)])
    # subtle: CS2's camera bone moves about a degree; the draw swings in from far away, so it follows even less
    cam = follow * (0.3 if anim.name.startswith("draw") else 0.6)
    # impacts, timed from the sound timeline
    side = 1.0
    for t, snd in sorted(anim.sounds):
        s = _strength(snd)
        if s <= 0:
            continue
        b = _bump(fine - t, 0.05)
        cam = cam + np.column_stack([s * b, 0.25 * s * side * b, 0.6 * s * side * b])
        side = -side
    # the shot: kick up, then a fast decaying shake
    if shot:
        a = SHOT.get(_shot_class(asset), 0.55)
        x = np.maximum(fine, 0.0)
        env = np.exp(-x / 0.06)
        cam = cam + np.column_stack([
            -0.8 * a * _bump(fine, 0.025) + 0.25 * a * env * np.sin(2 * math.pi * 17 * x),
            0.18 * a * env * np.sin(2 * math.pi * 23 * x + 1.0),
            0.5 * a * _bump(fine, 0.03) + 0.3 * a * env * np.sin(2 * math.pi * 13 * x + 2.0),
        ])
    # exactly 0 at both ends
    ramp = np.array([motion._ramp(t, 0.0, 0.0 if shot else 0.12) * (1.0 - motion._ramp(t, L - 0.12, L))
                     for t in fine])
    cam = np.clip(cam * ramp[:, None], -LIMIT, LIMIT)
    cam[0] = 0.0
    cam[-1] = 0.0
    # resample
    n = max(2, int(math.ceil(L * rate)) + 1)
    ts = np.linspace(0.0, L, n)
    out = np.column_stack([np.interp(ts, fine, cam[:, c]) for c in range(3)])
    out[0] = 0.0
    out[-1] = 0.0
    return rate, np.round(out, 3)


def camera_meta(asset):
    meta = {}
    for a in asset.anims:
        tr = camera_track(asset, a)
        if tr is not None:
            rate, curve = tr
            meta[a.name] = {"rate": rate, "d": [float(v) for v in curve.reshape(-1)]}
    return meta
