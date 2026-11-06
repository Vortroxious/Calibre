"""Post-passes that make the hand-authored inspects move like they're held by a person.

fluid_inspect(asset, anim): layers arcs, follow-through, breathing, anticipation and a yaw-aware hold-away distance
                            on top of the authored inspect (authored part timings, sounds and parts untouched).
clearance(asset, anim):     keeps every part of the gun out of the eye (see cs2.py for the inspect choreography).
"""
import math

import numpy as np

from .core import HOLD, bone_local_matrix, cube_matrix, ease, euler_mat

RATE = 120.0

FLOURISH = {
    "pistol": ["glock17", "m9", "ppq", "m1911", "bersa", "deagle", "rugermk3", "fiveseven", "usp", "cz75"],
    "revolver": ["model29", "sw642", "singlesix", "python"],
    "rifle": ["ak47", "akm", "aug", "fal", "hk416", "m14ebr", "m4a1", "scar_h", "mp5", "p90", "ump45", "uzi", "m45",
              "ppsh41", "sks", "svd", "benelli_m4", "vector", "mp7", "g36c", "famas", "x95", "aa12", "garand", "thompson", "mp40", "stg44", "bar", "sr25", "svu", "m16a1", "galil", "g3a3", "sten", "skorpion"],
    "shotgun": ["rem870", "model12", "nova", "cdaly", "spas12", "ks23"],
    "lever": ["win1894", "marlin336"],
    "bolt": ["mosin", "arisaka", "m1917", "m24", "awm", "savage10", "tikka_t3", "mossberg190", "kar98k", "enfield", "intervention", "l96", "rem700", "dsr1"],
    "heavy": ["m249", "pkm", "rpg7", "m82a1", "mg42", "m60"],
}
KIND = {g: k for k, gs in FLOURISH.items() for g in gs}


# ------------------------------------------------------------------------------------------------
# small helpers
# ------------------------------------------------------------------------------------------------
def _env(L, t, ramp_in=0.4, ramp_out=0.6):
    ri, ro = min(ramp_in, L * 0.2), min(ramp_out, L * 0.25)
    if t < ri:
        u = t / ri
    elif t > L - ro:
        u = (L - t) / ro
    else:
        u = 1.0
    u = max(0.0, min(1.0, u))
    return 0.5 - 0.5 * math.cos(math.pi * u)


def curve(keys):
    """Piecewise eased curve: keys = [(t, value, ease_into_this_key)], held before the first / after the last."""
    ks = [(float(t), np.asarray(v, dtype=float), e) for t, v, e in keys]

    def fn(t):
        if t <= ks[0][0]:
            return ks[0][1]
        for (t0, v0, _), (t1, v1, e) in zip(ks, ks[1:]):
            if t <= t1:
                return v0 + (v1 - v0) * ease(e, (t - t0) / max(1e-6, t1 - t0))
        return ks[-1][1]

    return fn


def _ramp(t, t0, t1, e="inoutsine"):
    if t <= t0:
        return 0.0
    if t >= t1:
        return 1.0
    return ease(e, (t - t0) / (t1 - t0))


def _sample(anim, bone, ch, t1):
    anim._memo.clear()
    ts = np.arange(0.0, t1 + 1e-9, 1.0 / RATE)
    vs = np.array([anim._free(bone, ch, t) for t in ts])
    anim._memo.clear()
    return ts, vs


def _interp(ts, vs, t):
    return np.array([np.interp(t, ts, vs[:, k]) for k in range(3)])


def _segments(anim, bone, ch):
    """Authored moves on a track as (t0, t1, v0, v1) with resolved values."""
    tr = anim.tracks.get((bone, ch))
    if tr is None:
        return []
    anim._memo.clear()
    out = []
    keys = tr.keys
    for i in range(1, len(keys)):
        if keys[i][1] is HOLD:
            continue
        t0, t1 = keys[i - 1][0], keys[i][0]
        if t1 - t0 < 0.08:
            continue
        v0 = anim._final_channel(bone, ch, t0)
        v1 = anim._final_channel(bone, ch, t1)
        if np.linalg.norm(v1 - v0) > 1.0:
            out.append((t0, t1, v0, v1))
    anim._memo.clear()
    return out


def _size(model):
    lo, hi = model.bounds()
    length = float(hi[2] - lo[2])
    return lo, hi, length, float(hi[2])


# ------------------------------------------------------------------------------------------------
# smooth paths
# ------------------------------------------------------------------------------------------------
def pchip(ts, vs, end_slopes=(0.0, 0.0)):
    """Monotone cubic (Fritsch-Carlson) through (t, value) points: continuous velocity, never overshoots a pose, so
    nothing moves back after it moved forward. Starts / ends with zero velocity unless told otherwise."""
    ts = np.asarray(ts, dtype=float)
    vs = np.asarray(vs, dtype=float)
    if vs.ndim == 1:
        vs = vs[:, None]
    n = len(ts)
    if n == 1:
        return lambda t: vs[0].copy()
    h = np.diff(ts)
    d = np.diff(vs, axis=0) / h[:, None]
    m = np.zeros_like(vs)
    for i in range(1, n - 1):
        a, b = d[i - 1], d[i]
        w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
        with np.errstate(divide="ignore", invalid="ignore"):
            hm = (w1 + w2) / (w1 / a + w2 / b)
        m[i] = np.where(a * b > 0, hm, 0.0)
    m[0], m[-1] = end_slopes

    def fn(t):
        if t <= ts[0]:
            return vs[0].copy()
        if t >= ts[-1]:
            return vs[-1].copy()
        i = int(np.searchsorted(ts, t) - 1)
        hh = h[i]
        u = (t - ts[i]) / hh
        u2, u3 = u * u, u * u * u
        return ((2 * u3 - 3 * u2 + 1) * vs[i] + (u3 - 2 * u2 + u) * hh * m[i]
                + (-2 * u3 + 3 * u2) * vs[i + 1] + (u3 - u2) * hh * m[i + 1])

    return fn


def path(keys):
    """Smooth path through [(t, value)] poses (pchip), held before the first / after the last."""
    ts = [float(k[0]) for k in keys]
    vs = [np.asarray(k[1], dtype=float) for k in keys]
    return pchip(ts, np.array(vs))


def _resolved_keys(anim, bone, ch):
    """Key times and values of a track with only the authored keys (no layers / springs)."""
    tr = anim.tracks.get((bone, ch))
    if tr is None:
        return None
    saved = anim.layers
    anim.layers = [l for l in saved if l[0] != bone]
    anim._memo.clear()
    base = anim.default(bone, ch)
    out = []
    for i, (t, _, _) in enumerate(tr.keys):
        v = np.asarray(anim._resolve(bone, ch, i, base), dtype=float)
        if out and abs(t - out[-1][0]) < 1e-4:
            out[-1] = (t, v)
        else:
            out.append((t, v))
    anim.layers = saved
    anim._memo.clear()
    return out


def _splinify(anim, bone, ch, rate=60.0):
    """Replace a track's pose-to-pose eases (each one stops dead at every key) with one continuous monotone path
    through the same poses at the same times. Holds (two equal poses) still hold."""
    ks = _resolved_keys(anim, bone, ch)
    if not ks or len(ks) < 2:
        return
    vals = [k[1].copy() for k in ks]
    # a held pose creeps a little way towards the next one instead of freezing (still never moves backwards)
    for i in range(len(vals) - 2):
        if np.allclose(vals[i], vals[i + 1], atol=1e-3) and not np.allclose(vals[i + 1], vals[i + 2], atol=1e-3) \
                and ks[i + 1][0] - ks[i][0] > 0.2:
            vals[i + 1] = vals[i] + 0.12 * (vals[i + 2] - vals[i])
    f = pchip([k[0] for k in ks], np.array(vals))
    t0, t1 = ks[0][0], ks[-1][0]
    n = max(2, int(math.ceil((t1 - t0) * rate)) + 1)
    anim.tracks[(bone, ch)].keys = [(t, f(t), "linear") for t in np.linspace(t0, t1, n)]
    anim._memo.clear()


def _is(fn, kind):
    return getattr(fn, "__qualname__", "").startswith(f"Anim.{kind}.")


# ------------------------------------------------------------------------------------------------
# fluid pass
# ------------------------------------------------------------------------------------------------
def fluid_inspect(asset, anim):
    m = asset.model
    lo, hi, length, rear = _size(m)
    L = anim.length
    long_gun = rear > 250
    pistol = length < 330
    live = 1.2 if pistol else (0.8 if length > 1100 else 1.0)
    env = lambda t: _env(L, t)

    # springs on the gun are a forward-then-back wobble after every move: that reads as the gun jerking back.
    # Authored waves are kept but faded with the inspect so the gun lands exactly on its rest pose.
    layers = []
    for b, ch, fn in anim.layers:
        if b == "gun" and _is(fn, "spring"):
            continue
        if b == "gun" and _is(fn, "wave"):
            fn = (lambda f: (lambda t: f(t) * env(t)))(fn)
        layers.append((b, ch, fn))
    anim.layers = layers

    if long_gun and not getattr(anim, "cs2", False):   # generated (cs2) inspects are already posed for this
        tr = anim.tracks.get(("gun", "rot"))
        if tr is not None:   # turn far enough to see the side, not so far the stock sweeps the face
            # and keep the muzzle within ~20 deg of level: tipped further, the stock comes up into the face
            def tame(v):
                x = v[0] if abs(v[0]) <= 12 else math.copysign(12 + (abs(v[0]) - 12) * 0.3, v[0])
                return np.array([x, v[1] * 0.62, v[2]])
            tr.keys = [(t, (tame(v) if isinstance(v, np.ndarray) else v), e) for t, v, e in tr.keys]
            anim._memo.clear()

    # one continuous path through the authored poses
    rot_keys = _resolved_keys(anim, "gun", "rot") or []
    for ch in ("pos", "rot"):
        _splinify(anim, "gun", ch)

    # hold the gun out a touch while it is turned (clearance() moves it further only where it has to)
    ts, rot = _sample(anim, "gun", "rot", L)

    def hold(t):
        r = _interp(ts, rot, t)
        s_yaw = abs(math.sin(math.radians(r[1])))
        dz = -min(60.0, rear * (0.04 + 0.1 * s_yaw)) if long_gun else -20.0
        return np.array([0.0, 0.0, dz]) * env(t)

    if not getattr(anim, "cs2", False):       # the generated close-ups are placed against the camera already
        anim.layers.append(("gun", "pos", hold))

    # arcs: the gun is carried up a little while it travels between two poses (one smooth lobe, no return swing)
    arcs = []
    for (t0, v0), (t1, v1) in zip(rot_keys, rot_keys[1:]):
        d = float(np.linalg.norm(v1 - v0))
        if t1 - t0 > 0.15 and d > 6.0:
            arcs.append((t0, t1, min(16.0, 0.25 * d) * (0.7 if long_gun else 1.0) * live))

    def arc(t):
        y = 0.0
        for t0, t1, lift in arcs:
            if t0 < t < t1:
                y += lift * math.sin(math.pi * (t - t0) / (t1 - t0)) ** 2
        return np.array([0.0, y, 0.0])

    anim.layers.append(("gun", "pos", arc))

    # living holds: very slow, small drift and breathing so a held pose never looks frozen
    ra = np.array([0.6, 0.5, 0.45]) * live
    anim.layers.append(("gun", "rot", lambda t: env(t) * np.array([
        ra[0] * math.sin(2 * math.pi * t / 3.4 + 0.4),
        ra[1] * math.sin(2 * math.pi * t / 4.1 + 1.9),
        ra[2] * math.sin(2 * math.pi * t / 3.7 + 3.1)])))
    anim.layers.append(("gun", "pos", lambda t: env(t) * np.array([
        0.8 * math.sin(2 * math.pi * t / 4.3 + 0.8),
        1.2 * math.sin(2 * math.pi * t / 4.0),
        0.0])))
    anim._memo.clear()


# ------------------------------------------------------------------------------------------------
# flourishes
# ------------------------------------------------------------------------------------------------
class _Rig:
    """Closed-form gun motion for a flourish: world = O(t) + P + R(t)(x - P), plus hand targets in world space."""

    def __init__(self, anim, T0, pivot):
        self.anim, self.T0, self.P = anim, T0, np.asarray(pivot, dtype=float)
        self.rot = lambda u: np.zeros(3)
        self.off = lambda u: np.zeros(3)

    def gun(self):
        T0, P = self.T0, self.P

        def rot(t):
            return self.rot(t - T0) if t >= T0 else np.zeros(3)

        def pos(t):
            if t < T0:
                return np.zeros(3)
            u = t - T0
            return self.off(u) + P - euler_mat(self.rot(u)) @ P

        self.anim.layers.append(("gun", "rot", rot))
        self.anim.layers.append(("gun", "pos", pos))

    def hand(self, bone, world, attach=None):
        """`world(u)`: where the hand pivot should be, as an offset from where it sits at rest.
        `attach(u)` (0..1): how much the hand is simply holding the gun where it normally does instead."""
        T0, P = self.T0, self.P
        h0 = np.asarray(self.anim.model.bones[bone].pivot, dtype=float)

        def pos(t):
            if t < T0:
                return np.zeros(3)
            u = t - T0
            target = h0 + world(u) - self.off(u) - P
            local = P + euler_mat(self.rot(u)).T @ target - h0
            return local * (1.0 - attach(u)) if attach is not None else local

        self.anim.layers.append((bone, "pos", pos))


def _peak(asset, anim_name, bone, ch):
    a = next((x for x in asset.anims if x.name == anim_name), None)
    if a is None or (bone, ch) not in a.tracks:
        return None
    vs = [v for _, v, _ in a.tracks[(bone, ch)].keys if isinstance(v, np.ndarray)]
    return max(vs, key=lambda v: float(np.linalg.norm(v))) if vs else None


def _replay(asset, anim, src_name, bones, t_at, sounds=()):
    """Copy the plain keys of a mechanism (pump, lever, bolt, hammer) from another animation, shifted to t_at."""
    src = next((x for x in asset.anims if x.name == src_name), None)
    if src is None:
        return 0.0
    end = 0.0
    for b in bones:
        for ch in ("pos", "rot"):
            tr = src.tracks.get((b, ch))
            if tr is None:
                continue
            for t, v, e in tr.keys:
                if isinstance(v, np.ndarray):
                    anim.key(b, t_at + t, **{ch: v}, e=e)
                    end = max(end, t)
    for t, s in src.sounds:
        if s in sounds:
            anim.sound(t_at + t, s)
    return end


def _scalar(keys):
    f = path([(t, (v,)) for t, v in keys])
    return lambda u: float(f(u)[0])


def _blend(a, b, w):
    return lambda u: a(u) + (b(u) - a(u)) * w(u)


# ------------------------------------------------------------------------------------------------
# camera clearance
# ------------------------------------------------------------------------------------------------
TAN_V = math.tan(math.radians(35.0))   # 70 deg vertical fov
TAN_H = TAN_V * 16 / 9 * 1.05


def _points(model, pose):
    """World (gun-parent space, mm) cube corners of every visible bone."""
    mats, hidden, out, vis = {}, {}, [], []
    corners = np.array([[x, y, z, 1.0] for x in (0, 1) for y in (0, 1) for z in (0, 1)])
    for b in model.order:
        pm = mats[b.parent.name] if b.parent else np.eye(4)
        a = pose.get(b.name)
        mats[b.name] = pm @ bone_local_matrix(b, a)
        hidden[b.name] = (hidden[b.parent.name] if b.parent else False) or (a is not None and np.allclose(a[2], 0))
        if b.name.startswith("arm_"):
            continue
        for c in b.cubes:
            lo = np.array([c.x0, c.y0, c.z0]); hi = np.array([c.x1, c.y1, c.z1])
            v = np.column_stack([lo + (hi - lo) * corners[:, :3], np.ones(8)])
            out.append(((mats[b.name] @ cube_matrix(c)) @ v.T).T[:, :3])
            vis.append(np.full(8, not hidden[b.name]))
    if not out:
        return np.zeros((0, 3)), np.zeros(0, dtype=bool)
    return np.concatenate(out), np.concatenate(vis)


def _in_view(V):
    x, y, d = V[:, 0], V[:, 1], -V[:, 2]
    return (d > 0.0) & (np.abs(x) < TAN_H * d + 0.02) & (np.abs(y) < TAN_V * d + 0.02), d


# ways to get a part out of the face, view space, with a cost weight: lowering the gun or moving it out reads as
# the hands bringing it down to look at it; pushing it far forward shrinks it and strands the arms
_DIRS = [(np.array([0.0, -1.0, 0.0]), 1.0, 0.07), (np.array([0.45, -0.89, 0.0]), 1.05, 0.09),
         (np.array([0.0, -0.71, -0.71]), 1.15, 0.16), (np.array([0.0, 0.0, -1.0]), 1.5, 0.5)]   # dir, cost, max m


def _ok(V, shown, floor, dmin):
    vis, dd = _in_view(V)
    central = (np.abs(V[:, 0]) < 0.7 * TAN_H * dd) & (np.abs(V[:, 1]) < 0.7 * TAN_V * dd)
    return not np.any(vis & shown & ((dd < floor) | (central & (dd < 0.8 * dmin))))


def _shift_needed(V, shown, floor, grid, dmin):
    """Cheapest view-space shift (m) after which no visible part is nearer than its floor."""
    if _ok(V, shown, floor, dmin):
        return np.zeros(3)
    best, cost = None, 1e9
    for d, w, cap in _DIRS:
        for g in grid:
            if g * w >= cost or g > cap:
                break
            if _ok(V + d * g, shown, floor, dmin):
                best, cost = d * g, g * w
                break
    return best if best is not None else _DIRS[-1][0] * grid[-1]


def clearance(asset, anim, dmin=0.15, rate=30.0):
    """Wherever the inspect would bring part of the gun nearer the eye than `dmin` (or than it is at rest, if that's
    nearer already), ease the gun down / out / forward by just enough, smoothed so it reads as the hands moving it."""
    m = asset.model
    hip = asset.meta.get("hip", {})
    R = euler_mat(hip.get("rot", (0, 0, 0)))
    off = np.asarray(hip.get("pos", (0.12, -0.12, -0.3)), dtype=float)
    grid = np.arange(0.005, 0.5, 0.005)

    def view(t):
        P, shown = _points(m, anim.pose(t))
        return (R @ (P.T * 0.001)).T + off, shown

    anim._memo.clear()
    # a part that already sits close at rest (receiver end, sights) may stay as close as it is at rest
    rest, _ = view(0.0)
    vis0, d0 = _in_view(rest)
    floor = np.where(vis0, np.minimum(dmin, d0), dmin)
    ts = np.arange(0.0, anim.length + 1e-9, 1.0 / rate)
    need = np.array([_shift_needed(*view(t), floor, grid, dmin) for t in ts])
    anim._memo.clear()
    mag = np.linalg.norm(need, axis=1)
    if mag.max() <= 0.0:
        return 0.0
    # hold the biggest shift a little either side, then smooth it
    k = int(round(0.2 * rate))
    held = np.array([need[max(0, i - k) + int(np.argmax(mag[max(0, i - k):i + k + 1]))] for i in range(len(need))])
    sig = 0.14 * rate
    xs = np.arange(-3 * int(sig), 3 * int(sig) + 1)
    w = np.exp(-0.5 * (xs / sig) ** 2)
    w /= w.sum()
    pad = len(xs) // 2

    def smooth(arr):
        return np.column_stack([np.convolve(np.pad(arr[:, c], pad), w, mode="valid") for c in range(3)])

    sm = smooth(held)
    # top up wherever smoothing fell short, with a smoothed top-up so no corner appears
    deficit = np.zeros_like(sm)
    for i in range(len(sm)):
        if mag[i] > 0:
            u = need[i] / mag[i]
            short = mag[i] - float(sm[i] @ u)
            if short > 0:
                deficit[i] = u * short
    if deficit.any():
        held_d = np.array([deficit[max(0, i - k) + int(np.argmax(np.linalg.norm(deficit[max(0, i - k):i + k + 1],
                                                                                 axis=1)))]
                           for i in range(len(deficit))])
        sm = sm + smooth(held_d) * 1.3
    # starts and ends at rest with zero velocity: the pose there is the rest pose, so nothing is needed anyway
    ramp = np.array([_ramp(t, 0.0, 0.25) * (1.0 - _ramp(t, anim.length - 0.25, anim.length)) for t in ts])
    sm = sm * ramp[:, None]
    sm_model = (R.T @ (sm.T * 1000.0)).T   # view metres -> gun-parent mm

    def push(t):
        return np.array([np.interp(t, ts, sm_model[:, c]) for c in range(3)])

    anim.layers.append(("gun", "pos", push))
    anim._memo.clear()
    return float(mag.max())
