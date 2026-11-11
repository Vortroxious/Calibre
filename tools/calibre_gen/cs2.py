"""Close-up (MW3-style) inspects, generated for every gun from its class and the mechanism parts it actually has.

No tossing, no rolling: the gun is presented slowly and with weight, turned to show one side and then the other,
and the hands do the small detailed things - the support hand slides along and checks the magazine, tugs the
charging handle / bolt / pump / lever a little way, the thumb flicks the selector, and the gun is glanced down
before it goes back to ready. Handguns press-check the slide and turn over; the Desert Eagle and the revolvers
finish with one clean finger spin, revolvers swing the cylinder out and spin it first.

Mechanism travel is read from the gun's own animations (reloads, cycle, firemode), so nothing is tuned per gun.
Times are in seconds, positions in model mm, rotations in degrees (core.Anim conventions).
"""
import numpy as np

from .core import Anim
from . import motion

AK = {"ak47", "akm"}


# ------------------------------------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------------------------------------
def _peak(asset, bone, ch, prefer=("reload_empty", "cycle", "firemode", "reload", "reload_start", "fire")):
    """Largest plain key of a mechanism bone across the gun's own animations (preferred ones first)."""
    if bone not in asset.model.bones:
        return None
    order = sorted((a for a in asset.anims if a.name != "inspect"),
                   key=lambda a: prefer.index(a.name) if a.name in prefer else len(prefer))
    for a in order:
        tr = a.tracks.get((bone, ch))
        if not tr:
            continue
        vs = [v for _, v, _ in tr.keys if isinstance(v, np.ndarray)]
        if vs:
            v = max(vs, key=lambda x: float(np.linalg.norm(x)))
            if float(np.linalg.norm(v)) > 1e-3:
                return np.asarray(v, dtype=float)
    return None


def _box(m, name):
    """Rest-pose bounds (model mm) of a bone's cubes and its children's."""
    root = m.bones[name]
    pts = []
    for b in m.order:
        x = b
        while x is not None and x is not root:
            x = x.parent
        if x is None:
            continue
        for c in b.cubes:
            pts.append((c.x0, c.y0, c.z0))
            pts.append((c.x1, c.y1, c.z1))
    if not pts:
        p = np.asarray(root.pivot, dtype=float)
        return p, p
    P = np.array(pts, dtype=float)
    return P.min(axis=0), P.max(axis=0)


def _handle_point(m, name):
    """Where a bolt handle sticks out: centre of the cube reaching furthest to the side."""
    root = m.bones[name]
    best, far = None, -1.0
    for b in m.order:
        x = b
        while x is not None and x is not root:
            x = x.parent
        if x is None:
            continue
        for c in b.cubes:
            reach = max(abs(c.x0), abs(c.x1))
            if reach > far:
                far = reach
                best = np.array([(c.x0 + c.x1) / 2, (c.y0 + c.y1) / 2, (c.z0 + c.z1) / 2])
    return best if best is not None else np.asarray(root.pivot, dtype=float)


class _Inspect:
    def __init__(self, asset, length):
        self.asset, self.m = asset, asset.model
        old = next(a for a in asset.anims if a.name == "inspect")
        self.a = Anim(self.m, "inspect", length)
        self.a.hidden = set(old.hidden)        # spare parts (clips, loose rounds...) stay hidden
        self.a.rest = dict(old.rest)
        self.a.cs2 = True
        kind = motion.KIND.get(self.m.name, "rifle")
        self.handle = {"pistol": "handle_pistol", "revolver": "handle_pistol", "heavy": "handle_heavy"}.get(kind,
                                                                                                          "handle_rifle")

    def move(self, t0, t1, pos, rot, e="inoutcubic", snd=True):
        """A big move of the whole gun, with the gun's own rattle as it starts to turn in the hands."""
        self.gun(t0, t1, pos, rot, e=e)
        if snd:
            self.a.sound(t0 + 0.04, self.handle)

    def creep(self, t0, t1, pose, drift):
        """Hold a pose without freezing: drift slowly by `drift` (pos, rot) over the hold."""
        (p, r), (dp, dr) = pose, drift
        self.gun(t0, t1, np.add(p, dp), np.add(r, dr), e="inoutsine")

    def grab(self, hand, part, t0, t1, fade_in=0.04, fade_out=0.06):
        self.a.grab(hand, part, t0, t1, fade_in=fade_in, fade_out=fade_out)
        self.a.sound(t0, "grip")

    def has(self, bone):
        return bone in self.m.bones

    def reach(self, hand, t0, t1, point, e="inoutcubic"):
        """Move a hand so its pivot sits at `point` (model mm, rest pose of the gun)."""
        h0 = np.asarray(self.m.bones[hand].pivot, dtype=float)
        self.a.mv(hand, t0, t1, pos=np.asarray(point, dtype=float) - h0, e=e)

    def home(self, hand, t0, t1, e="inoutcubic"):
        self.a.mv(hand, t0, t1, pos=(0, 0, 0), e=e)

    def gun(self, t0, t1, pos, rot, e="inoutcubic"):
        self.a.mv("gun", t0, t1, pos=pos, rot=rot, e=e)

    def tug(self, bone, t0, travel, out=0.14, hold=0.1, back=0.08, ch="pos", snd=None):
        """Part pulled `travel` over `out` s, held, let go (snaps home). Returns the end time."""
        z = np.zeros(3)
        kw = lambda v: {ch: v}
        self.a.key(bone, t0, **kw(z))
        self.a.key(bone, t0 + out, **kw(travel), e="outquad")
        self.a.key(bone, t0 + out + hold, **kw(travel))
        self.a.key(bone, t0 + out + hold + back, **kw(z), e="inquad")
        if snd:
            self.a.sound(t0 + out * 0.7, snd[0])
            if len(snd) > 1:
                self.a.sound(t0 + out + hold + back, snd[1])
        return t0 + out + hold + back

    def sound(self, t, name):
        self.a.sound(t, name)


def _fidget(I, t, T=lambda x: x):
    """Work the small controls the gun has (safety, dust cover, forward assist, bolt catch, slide stop), one after
    the other, with a click each. Returns the end time."""
    from .common import part_move
    m, a = I.m, I.a
    for bone, default, snd in (("safety", {"rot": (-35, 0, 0)}, "selector"),
                               ("dust_cover", {"rot": (0, 0, 100)}, "dust_cover"),
                               ("forward_assist", {"pos": (-5, 0, 0)}, "forward_assist"),
                               ("bolt_catch", {"pos": (0, 3.5, 0)}, "click_small"),
                               ("slide_stop", {"pos": (0, 2.5, 0)}, "click_small")):
        if not I.has(bone):
            continue
        d = part_move(m, bone, default)
        for ch, v in d.items():
            I.tug(bone, t + T(0.04), np.asarray(v, dtype=float), out=T(0.08), hold=T(0.14), back=T(0.08), ch=ch,
                  snd=(snd, snd) if ch == list(d)[0] else None)
        a.kick("gun", "rot", t + T(0.1), (0.4, 0, -0.5), attack=0.04, recover=0.2)
        t += T(0.36)
    return t


# ------------------------------------------------------------------------------------------------
# long guns
# ------------------------------------------------------------------------------------------------
def _press_check(I, kind, t, T, hl):
    asset, m, a = I.asset, I.m, I.a
    if kind == "shotgun" and I.has("pump"):
        trav = _peak(asset, "pump", "pos") if _peak(asset, "pump", "pos") is not None else np.array([0, 0, 80.0])
        I.grab("arm_left", "pump", t, t + T(0.5), fade_in=0.03, fade_out=0.05)
        I.tug("pump", t + T(0.06), trav * 0.45, out=T(0.16), hold=T(0.12), back=T(0.1),
              snd=("pump_back_light", "pump_forward"))
        if I.has("bolt"):
            b = _peak(asset, "bolt", "pos")
            if b is not None:
                I.tug("bolt", t + T(0.06), b * 0.45, out=T(0.16), hold=T(0.12), back=T(0.1))
        return t + T(0.62)
    if kind == "lever" and I.has("lever"):
        lv = _peak(asset, "lever", "rot")
        I.grab("arm_right", "lever", t, t + T(0.6), fade_in=0.03, fade_out=0.05)
        if lv is not None:
            I.tug("lever", t + T(0.06), lv * 0.45, out=T(0.18), hold=T(0.14), back=T(0.12), ch="rot",
                  snd=("lever_open", "lever_close"))
        b = _peak(asset, "bolt", "pos")
        if b is not None:
            I.tug("bolt", t + T(0.06), b * 0.45, out=T(0.18), hold=T(0.14), back=T(0.12))
        hm = _peak(asset, "hammer", "rot")
        if hm is not None:
            a.key("hammer", t + T(0.06), rot=(0, 0, 0))
            a.key("hammer", t + T(0.2), rot=hm, e="outquad")
        return t + T(0.7)
    if kind == "bolt" and I.has("bolt"):
        lift = _peak(asset, "bolt", "rot")
        pull = _peak(asset, "bolt", "pos")
        hp = _handle_point(m, "bolt")
        I.reach("arm_right", t, t + T(0.3), hp + (8, 6, 6))
        t0 = t + T(0.32)
        I.grab("arm_right", "bolt", t0, t0 + T(0.66), fade_in=0.04, fade_out=0.06)
        z = np.zeros(3)
        if lift is not None:
            a.key("bolt", t0, rot=z)
            a.key("bolt", t0 + T(0.12), rot=lift, e="outquad")
            a.key("bolt", t0 + T(0.5), rot=lift)
            a.key("bolt", t0 + T(0.62), rot=z, e="inquad")
        if pull is not None:
            a.key("bolt", t0 + T(0.12), pos=z)
            a.key("bolt", t0 + T(0.26), pos=pull * 0.3, e="outquad")
            a.key("bolt", t0 + T(0.36), pos=pull * 0.3)
            a.key("bolt", t0 + T(0.48), pos=z, e="inquad")
        I.sound(t0 + T(0.1), "bolt_open")
        I.sound(t0 + T(0.6), "bolt_close")
        I.home("arm_right", t0 + T(0.72), t0 + T(0.98))
        return t0 + T(0.9)
    if I.has("cover") and m.name in ("m249", "pkm"):
        cv = _peak(asset, "cover", "rot")
        clo, chi = _box(m, "cover")
        I.reach("arm_left", t, t + T(0.3), ((clo[0] + chi[0]) / 2 - 10, chi[1] + 8, chi[2] - 30))
        t0 = t + T(0.32)
        I.grab("arm_left", "cover", t0, t0 + T(0.2), fade_in=0.04, fade_out=0.08)
        if cv is not None:
            z = np.zeros(3)
            a.key("cover", t0, rot=z)
            a.key("cover", t0 + T(0.2), rot=cv * 0.85, e="outquad")
            a.key("cover", t0 + T(0.72), rot=cv * 0.85)
            a.key("cover", t0 + T(0.86), rot=z, e="inquad")
        I.sound(t0 + T(0.1), "cover_open")
        I.sound(t0 + T(0.86), "cover_close")
        I.reach("arm_left", t0 + T(0.66), t0 + T(0.8), ((clo[0] + chi[0]) / 2 - 10, chi[1] + 14, chi[2] - 40))
        I.home("arm_left", t0 + T(0.9), t0 + T(1.15))
        return t0 + T(1.0)
    part = "charging_handle" if I.has("charging_handle") else ("bolt" if I.has("bolt") else None)
    if part is None:
        return t
    trav = _peak(asset, part, "pos")
    if trav is None or abs(trav[2]) < 1:
        trav = np.array([0.0, 0.0, 60.0])
    lo, hi = _box(m, part)
    if part == "bolt" or m.name in AK:
        p = _handle_point(m, part)
        grip = p + (10 if p[0] >= 0 else -10, 8, 4)   # reach over to the handle
    else:
        grip = np.array([(lo[0] + hi[0]) / 2 - 14, hi[1] + 8, (lo[2] + hi[2]) / 2])
    I.reach("arm_left", t, t + T(0.32), grip)
    t0 = t + T(0.34)
    I.grab("arm_left", part, t0, t0 + T(0.4), fade_in=0.04, fade_out=0.06)
    end = I.tug(part, t0 + T(0.02), trav * 0.38, out=T(0.15), hold=T(0.12), back=T(0.08),
                snd=("charging_handle_back", "charging_handle_forward") if part == "charging_handle"
                else ("bolt_back", "bolt_forward"))
    if part == "charging_handle" and I.has("bolt"):
        I.tug("bolt", t0 + T(0.02), trav * 0.38, out=T(0.15), hold=T(0.12), back=T(0.08))
    a.kick("gun", "rot", end, (0.8, 0, 0.6), attack=0.03, recover=0.22)
    I.home("arm_left", end + T(0.06), end + T(0.36))
    return end + T(0.3)


# ------------------------------------------------------------------------------------------------
# handguns
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# MW3-style close-ups: the gun is pulled right up to the eye, turned side-on with the muzzle up,
# quick moves between poses and long slow holds; the magazine is taken out and shown to the camera
# ------------------------------------------------------------------------------------------------
from .core import euler_mat, mat_euler  # noqa: E402


class _Close:
    """Poses placed in view space: a focus point on the gun is put at a chosen spot in front of the eye."""

    def __init__(self, I):
        self.I, self.a, self.m = I, I.a, I.m
        hip = I.asset.meta.get("hip", {})
        self.R = euler_mat(hip.get("rot", (0, 0, 0)))
        self.off = np.asarray(hip.get("pos", (0.12, -0.12, -0.3)), dtype=float)
        self.poses = {}          # time -> (pos, rot) of the keyed gun, to place hands/parts in its frame
        self.h0 = {h: np.asarray(self.m.bones[h].pivot, dtype=float) for h in ("arm_left", "arm_right")}

    def world(self, v):
        return self.R.T @ (np.asarray(v, dtype=float) - self.off) * 1000.0

    def pose(self, F, rot, v):
        rot = np.asarray(rot, dtype=float)
        return self.world(v) - euler_mat(rot) @ np.asarray(F, dtype=float), rot

    def at(self, t):
        ts = sorted(self.poses)
        best = max([x for x in ts if x <= t + 1e-6], default=ts[0])
        return self.poses[best]

    def local(self, t, v):
        """View-space point (m) -> gun-local point (mm) for the gun pose keyed at/just before t."""
        gp, gr = self.at(t)
        return euler_mat(gr).T @ (self.world(v) - gp)

    def move(self, t0, t1, pose, snd=True, e="inoutcubic"):
        self.I.move(t0, t1, *pose, e=e, snd=snd)
        self.poses[t1] = pose
        self.poses.setdefault(t0, self.at(t0) if self.poses else pose)

    def creep(self, t0, t1, pose, drift):
        dp, dr = drift
        p = (np.add(pose[0], dp), np.add(pose[1], dr))
        self.I.gun(t0, t1, *p, e="inoutsine")
        self.poses[t1] = p
        return p

    def park(self, t0, t1, hand="arm_left"):
        """Support hand out of the way, just off the bottom-left of the screen."""
        p = self.local(t1, (-0.17, -0.31, -0.15)) - self.h0[hand]
        self.a.mv(hand, t0, t1, pos=p, e="inoutcubic")


def _mag_sounds(asset):
    out = inn = None
    for an in asset.anims:
        if an.name.startswith("reload"):
            for _, s in sorted(an.sounds):
                if out is None and s.startswith(("mag_out", "drum_out", "box_out")):
                    out = s
                if inn is None and s.startswith(("mag_in", "drum_in", "box_in")):
                    inn = s
    return out or "mag_out_rifle", inn or "mag_in_rifle"


def _mag_dir(asset):
    """Direction the magazine leaves the well, from the gun's own reload (first move of the magazine)."""
    for an in asset.anims:
        if not an.name.startswith("reload"):
            continue
        tr = an.tracks.get(("magazine", "pos"))
        if not tr:
            continue
        for _, v, _ in tr.keys:
            if isinstance(v, np.ndarray) and np.linalg.norm(v) > 2:
                return v / np.linalg.norm(v)
    return None


def _show_mag(C, t, T, down_pose, back_pose, show_v=(0.0, 0.025, -0.25)):
    """Take the magazine out, bring it up to the eye (the gun drops away), look at the rounds, put it back,
    palm-seat it. Returns the end time, or None if the gun has no detachable magazine."""
    I, a, m = C.I, C.a, C.m
    d = _mag_dir(I.asset)
    if not I.has("magazine") or d is None:
        return None
    mo, mi = _mag_sounds(I.asset)
    mag = m.bones["magazine"]
    piv = np.asarray(mag.pivot, dtype=float)
    rest_rot = np.asarray(mag.rot, dtype=float)
    mlo, mhi = _box(m, "magazine")
    side = np.array([mlo[0] - 10, (mlo[1] + mhi[1]) / 2, (mlo[2] + mhi[2]) / 2])
    base = np.array([(mlo[0] + mhi[0]) / 2 - 4, mlo[1] - 14, (mlo[2] + mhi[2]) / 2])
    out = d * 75.0
    z = np.zeros(3)
    # hand onto the magazine, from underneath (so the arm hangs below it and the magazine stays in view)
    I.reach("arm_left", t, t + T(0.3), base)
    tg = t + T(0.32)
    I.grab("arm_left", "magazine", tg, tg + T(2.0), fade_in=0.04, fade_out=0.05)
    a.key("magazine", tg, pos=z, rot=z)
    a.key("magazine", tg + T(0.2), pos=out, rot=z, e="outquad")
    I.sound(tg + T(0.08), mo)
    # gun drops away to the bottom-right, the magazine comes up to the eye, rounds towards the camera
    t1 = tg + T(0.22)
    t2 = t1 + T(0.42)
    C.move(t1, t2, down_pose)
    gp, gr = down_pose
    target = euler_mat(gr).T @ (C.world(show_v) - gp)
    Rt = euler_mat((38, 32, -6))          # in view space: top tipped towards the eye, three-quarter turn
    Rm = (C.R @ euler_mat(gr)).T @ Rt
    mrot = mat_euler(Rm) - rest_rot
    a.key("magazine", t2, pos=target - piv, rot=mrot, e="inoutcubic")
    # look at it: a slow turn of the wrist and a little shake to hear the rounds
    t3 = t2 + T(1.0)
    a.key("magazine", t2 + T(0.45), pos=target - piv + (0, 4, -6), rot=mrot + (6, -14, 4), e="inoutsine")
    a.key("magazine", t2 + T(0.62), pos=target - piv + (0, 6, -4), rot=mrot + (9, -10, 2), e="inoutsine")
    a.key("magazine", t2 + T(0.7), pos=target - piv + (0, 3, -6), rot=mrot + (4, -12, 3), e="inoutsine")
    a.key("magazine", t3, pos=target - piv + (2, 2, -2), rot=mrot + (2, -6, 2), e="inoutsine")
    I.sound(t2 + T(0.6), "mag_check")
    I.sound(t2 + T(0.7), "mag_check")
    C.creep(t2, t3, down_pose, ((4, -3, 2), (1, 2, -2)))
    # gun comes back up, magazine goes back to the well, pushed home, then palm-seated
    t4 = t3 + T(0.42)
    C.move(t3, t4, back_pose)
    a.key("magazine", t4, pos=out, rot=z, e="inoutcubic")
    t5 = t4 + T(0.14)
    a.key("magazine", t5, pos=z, rot=z, e="inquad")
    I.sound(t5 - T(0.02), mi)
    I.a.grabs[-1].t1 = t5
    a.key("arm_left", t5, pos=base - C.h0["arm_left"])
    I.reach("arm_left", t5 + T(0.04), t5 + T(0.18), base + (0, -18, 0))
    I.reach("arm_left", t5 + T(0.18), t5 + T(0.24), base, e="inquad")
    a.key("magazine", t5 + T(0.22), pos=z)
    a.key("magazine", t5 + T(0.25), pos=(0, 3, 0), e="outquad")
    a.key("magazine", t5 + T(0.33), pos=z, e="inoutsine")
    I.sound(t5 + T(0.24), "tap")
    a.kick("gun", "pos", t5 + T(0.24), (0, 3, 0), attack=0.03, recover=0.2)
    return t5 + T(0.36)


def _close_long(asset, kind):
    m = asset.model
    lo, hi = m.bounds()
    length = float(hi[2] - lo[2])
    heavy = kind == "heavy"
    k = 1.1 if heavy else (0.92 if length < 760 else 1.0)
    T = lambda x: x * k
    I = _Inspect(asset, T(9.0))
    a = I.a
    C = _Close(I)
    ej = m.meta.get("eject", [0, 0, -40])
    F = np.array([0.0, 0.0, float(ej[2])])
    d = 0.36 if heavy else (0.27 if length < 760 else 0.30)
    ang = 0.8 if heavy else 1.0
    A = C.pose(F, (10 * ang, -60 * ang, 50 * ang), (0.07, 0.08, -d))           # right side, muzzle up
    B = C.pose(F, (10 * ang, 60 * ang, -50 * ang), (-0.01, 0.08, -d))          # left side
    DOWN = C.pose(F, (4, -40, 30), (0.16, -0.16, -d - 0.05))                  # dropped away for the magazine
    MID = C.pose(F, (55 * ang, 0, 0), (0.03, 0.03, -d - 0.02))                # upright, halfway through the turn
    C.poses[0.0] = (np.zeros(3), np.zeros(3))
    # 1) snapped up to the eye, right side; the support hand lets go and drops away
    I.sound(0.0, "grip")
    C.move(0.0, T(0.5), A)
    C.park(T(0.05), T(0.45))
    I.sound(T(0.06), "cloth")
    A1 = C.creep(T(0.5), T(2.0), A, ((-3, 4, -3), (2, -5, 3)))
    t = T(2.05)
    # 2) magazine out and up to the eye
    end = _show_mag(C, t, T, DOWN, A1)
    if end is None:      # no detachable magazine: a longer look, rolled a little further towards the eye
        C.creep(t, t + T(1.4), A1, ((2, 4, -4), (4, -8, 6)))
        end = t + T(1.45)
    t = end
    # 3) turned over to the left side through upright (the stock swings down, out of the face), held
    C.move(t, t + T(0.28), MID, snd=True, e="inoutsine")
    C.move(t + T(0.28), t + T(0.55), B, snd=False, e="inoutsine")
    t += T(0.05)
    C.park(t + T(0.05), t + T(0.5))
    C.creep(t + T(0.5), t + T(2.0), B, ((3, 3, -3), (1, 5, -3)))
    t += T(2.0)
    # 4) press-check with whatever the gun has (the hand comes in big, close to the eye)
    t = _press_check(I, kind, t, T, C.h0["arm_left"])
    t = _fidget(I, t, T)
    # 5) selector off and back on
    sel = _peak(asset, "selector", "rot")
    if sel is not None:
        snd = "selector_ak" if m.name in AK else "selector"
        I.tug("selector", t + T(0.06), sel, out=T(0.1), hold=T(0.16), back=T(0.1), ch="rot", snd=(snd, snd))
        a.kick("gun", "rot", t + T(0.12), (0.6, 0, -0.8), attack=0.04, recover=0.25)
        t += T(0.5)
    # 6) back to ready
    I.move(t, t + T(0.65), (0, 0, 0), (0, 0, 0))
    I.home("arm_left", t + T(0.05), t + T(0.55))
    I.sound(t + T(0.6), "grip")
    a.length = t + T(0.75)
    return a


def _hand_pose(asset, I, C):
    m = asset.model
    lo, hi = m.bounds()
    length = float(hi[2] - lo[2])
    part = next((p for p in ("slide", "cylinder", "bolt") if p in m.bones), None)
    if part:
        plo, phi = _box(m, part)
        F = np.array([0.0, (plo[1] + phi[1]) / 2, (plo[2] + phi[2]) / 2])
    else:
        F = np.array([0.0, 0.0, (lo[2] + hi[2]) / 2])
    d = 0.14 + 0.00038 * length
    y = 0.04
    if part == "cylinder":          # revolvers: a little lower and further, so barrel and cylinder both show
        d, y = d + 0.04, 0.0
    A = C.pose(F, (8, -80, 30), (0.04, y, -d))              # right side, side-on, muzzle up a little
    B = C.pose(F, (8, 80, -30), (0.0, y, -d))               # left side
    DOWN = C.pose(F, (0, -40, 20), (0.12, -0.14, -d - 0.04))
    B2 = C.pose(F, (-8, 70, -16), (0.0, 0.05, -d - 0.02))   # left side again, muzzle dipped: top of the slide
    return A, B, DOWN, B2


def _close_pistol(asset):
    m = asset.model
    T = lambda x: x
    I = _Inspect(asset, 8.0)
    a = I.a
    C = _Close(I)
    A, B, DOWN, REAR = _hand_pose(asset, I, C)
    C.poses[0.0] = (np.zeros(3), np.zeros(3))
    # 1) left side up close, held
    I.sound(0.0, "grip")
    C.move(0.0, 0.45, B)
    C.park(0.05, 0.4)
    I.sound(0.06, "cloth")
    C.creep(0.45, 1.6, B, ((-2, 3, -2), (2, 5, -3)))
    t = 1.65
    # 2) press-check: pinch the front of the slide, draw it back a little
    part = "slide" if I.has("slide") else ("bolt" if I.has("bolt") else None)
    if part is not None:
        lo, hi = _box(m, part)
        I.reach("arm_left", t, t + 0.3, (lo[0] - 14, (lo[1] + hi[1]) / 2 + 6, lo[2] + 26))
        t0 = t + 0.32
        trav = _peak(asset, part, "pos")
        trav = trav if trav is not None else np.array([0.0, 0.0, 40.0])
        I.grab("arm_left", part, t0, t0 + 0.45, fade_in=0.04, fade_out=0.05)
        end = I.tug(part, t0 + 0.02, trav * 0.3, out=0.15, hold=0.18, back=0.07,
                    snd=("press_check", "slide_forward_light"))
        a.kick("gun", "rot", end, (1.2, 0, -0.8), attack=0.03, recover=0.2)
        t = end + 0.1
        C.park(t, t + 0.3)
    # 3) turned over, right side held
    C.move(t, t + 0.45, A)
    C.park(t + 0.05, t + 0.45)
    A1 = C.creep(t + 0.45, t + 1.5, A, ((-2, 2, -2), (1, -5, 3)))
    t += 1.55
    # 4) magazine out and up to the eye
    end = _show_mag(C, t, T, DOWN, A1, show_v=(0.0, 0.03, -0.21))
    t = end if end is not None else t
    t = _fidget(I, t)
    # 5) a look at the rear sights and the back of the slide
    C.move(t, t + 0.45, REAR)
    C.park(t + 0.05, t + 0.45)
    C.creep(t + 0.45, t + 1.2, REAR, ((2, 2, -2), (-2, 3, 2)))
    t += 1.25
    I.move(t, t + 0.6, (0, 0, 0), (0, 0, 0))
    I.home("arm_left", t + 0.05, t + 0.5)
    I.sound(t + 0.55, "grip")
    a.length = t + 0.7
    return a


def _close_revolver(asset):
    m = asset.model
    I = _Inspect(asset, 8.0)
    a = I.a
    C = _Close(I)
    A, B, DOWN, REAR = _hand_pose(asset, I, C)
    C.poses[0.0] = (np.zeros(3), np.zeros(3))
    I.sound(0.0, "grip")
    C.move(0.0, 0.45, B)
    C.park(0.05, 0.4)
    I.sound(0.06, "cloth")
    C.creep(0.45, 1.3, B, ((-2, 3, -2), (1, 4, -3)))
    t = 1.35
    cyl = "cylinder"
    if I.has("crane"):
        cr = _peak(asset, "crane", "rot")
        cr = cr if cr is not None else np.array([0.0, 0.0, 80.0])
        lo, hi = _box(m, cyl)
        I.reach("arm_left", t, t + 0.3, (lo[0] - 12, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2))
        t0 = t + 0.32
        I.grab("arm_left", cyl, t0, t0 + 0.26, fade_in=0.04, fade_out=0.06)
        a.key("crane", t0, rot=(0, 0, 0))
        a.key("crane", t0 + 0.24, rot=cr, e="outquad")
        I.sound(t0 + 0.04, "cylinder_latch")
        I.sound(t0 + 0.2, "cylinder_open")
        t1 = t0 + 0.42
        C.park(t0 + 0.3, t1 + 0.2)
        a.key(cyl, t1, rot=(0, 0, 0))
        a.key(cyl, t1 + 0.35, rot=(0, 0, -400), e="outquad")
        a.key(cyl, t1 + 1.0, rot=(0, 0, -720), e="outcubic")
        I.sound(t1 + 0.02, "cylinder_spin")
        C.creep(t0, t1 + 1.0, B, ((-3, 4, -2), (2, 6, -2)))
        t2 = t1 + 1.1
        a.key("crane", t2, rot=cr)
        a.key("crane", t2 + 0.12, rot=(0, 0, 0), e="inquad")
        a.kick("gun", "rot", t2, (0, -6, -10), attack=0.1, recover=0.3)
        I.sound(t2 + 0.12, "cylinder_close")
        t = t2 + 0.35
    elif I.has("gate"):
        gt = _peak(asset, "gate", "rot")
        gt = gt if gt is not None else np.array([0.0, 0.0, -80.0])
        lo, hi = _box(m, "gate")
        I.reach("arm_left", t, t + 0.3, (hi[0] + 10, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2))
        t0 = t + 0.32
        a.key("gate", t0, rot=(0, 0, 0))
        a.key("gate", t0 + 0.12, rot=gt, e="outquad")
        I.sound(t0 + 0.08, "loading_gate")
        step = _peak(asset, cyl, "rot")
        step = step if step is not None else np.array([0.0, 0.0, -60.0])
        n = int(round(360.0 / max(1.0, abs(float(step[2])))))
        tt = t0 + 0.22
        for i in range(n):
            a.key(cyl, tt, rot=step * i)
            a.key(cyl, tt + 0.08, rot=step * (i + 1), e="outquad")
            I.sound(tt + 0.06, "click_small")
            tt += 0.16
        a.key("gate", tt + 0.05, rot=gt)
        a.key("gate", tt + 0.15, rot=(0, 0, 0), e="inquad")
        I.sound(tt + 0.13, "loading_gate")
        C.creep(t0, tt + 0.15, B, ((-2, 3, -2), (1, 4, -2)))
        t = tt + 0.3
    C.park(t - 0.1, t + 0.25)
    C.move(t, t + 0.45, A)
    C.creep(t + 0.45, t + 1.6, A, ((-2, 2, -2), (1, -5, 3)))
    t += 1.65
    C.move(t, t + 0.45, REAR)
    C.creep(t + 0.45, t + 1.2, REAR, ((2, 2, -2), (-2, 3, 2)))
    t += 1.25
    if m.name == "singlesix" and I.has("hammer"):
        cock = _peak(asset, "hammer", "rot", prefer=("fire",))
        if cock is not None:
            a.key("hammer", t - 0.6, rot=(0, 0, 0))
            a.key("hammer", t - 0.48, rot=cock, e="outquad")
            a.key("hammer", t - 0.3, rot=cock)
            a.key("hammer", t - 0.18, rot=(0, 0, 0), e="inquad")
            I.sound(t - 0.5, "hammer_cock")
    I.move(t, t + 0.6, (0, 0, 0), (0, 0, 0))
    I.home("arm_left", t + 0.05, t + 0.5)
    I.sound(t + 0.55, "grip")
    a.length = t + 0.7
    return a


# ------------------------------------------------------------------------------------------------
def cs2_inspect(asset):
    kind = motion.KIND.get(asset.model.name, "rifle")
    if kind == "pistol":
        return _close_pistol(asset)
    if kind == "revolver":
        return _close_revolver(asset)
    return _close_long(asset, kind)
