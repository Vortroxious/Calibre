"""CS2-style inspects, generated for every gun from its class and the mechanism parts it actually has.

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


# ------------------------------------------------------------------------------------------------
# long guns
# ------------------------------------------------------------------------------------------------
def _long(asset, kind):
    m = asset.model
    lo, hi = m.bounds()
    length = float(hi[2] - lo[2])
    heavy = kind == "heavy"
    k = 1.0 if heavy else (0.92 if length < 760 else 1.0)
    k *= 0.84 if "magazine" in m.bones else 0.95      # ~8 s either way: guns without a magazine skip that step
    T = lambda x: x * k
    I = _Inspect(asset, T(8.0) + (0.5 if heavy and "cover" in m.bones else 0.0))
    a = I.a
    ang = 0.7 if heavy else 1.0
    # poses: right (ejection port) side, left side, glance down the top
    # (kept on their own side of the screen: drawn in towards the middle, the stock comes into the face)
    # held out in front and raised into view (searched against the camera: the stock stays clear of the cheek)
    out = -110 if length > 760 else -60
    A = ((-40, 20, out), (14 * ang, -40 * ang, -30 * ang))
    B = ((-20, 56, out), (6 * ang, 40 * ang, 42 * ang))
    C = ((-10, 40, out * 0.6), (12 * ang, 8 * ang, 6 * ang))
    hl = np.asarray(m.bones["arm_left"].pivot, dtype=float)

    D = ((-24, 36, out), (10 * ang, -18 * ang, -62 * ang))          # top of the receiver rolled towards the eye
    E = ((-26, 52, out * 0.8), (22 * ang, 14 * ang, 10 * ang))       # muzzle tipped up towards the crosshair

    # 1) present the right side; the support hand slides back along the handguard; let it sit there a moment
    I.sound(0.0, "grip")
    I.move(0.0, T(0.75), *A)
    a.mv("arm_left", T(0.12), T(0.7), pos=(2, -2, 34))
    I.sound(T(0.08), "cloth")
    I.creep(T(0.75), T(1.45), A, ((-4, 3, -4), (1, -5, 3)))

    # 2) magazine: hold it, a little wiggle, a palm tap from underneath to seat it
    t = T(1.5)
    if I.has("magazine"):
        mlo, mhi = _box(m, "magazine")
        side = np.array([mlo[0] - 12, (mlo[1] + mhi[1]) / 2 + 10, (mlo[2] + mhi[2]) / 2])
        base = np.array([(mlo[0] + mhi[0]) / 2 - 4, mlo[1] - 14, (mlo[2] + mhi[2]) / 2])
        I.reach("arm_left", t, t + T(0.34), side)
        I.grab("arm_left", "magazine", t + T(0.36), t + T(0.78), fade_in=0.04, fade_out=0.05)
        a.key("magazine", t + T(0.36), rot=(0, 0, 0))
        a.key("magazine", t + T(0.47), rot=(0, 0, 2.5))
        a.key("magazine", t + T(0.58), rot=(0, 0, -2.0))
        a.key("magazine", t + T(0.68), rot=(0, 0, 1.0))
        a.key("magazine", t + T(0.76), rot=(0, 0, 0))
        I.sound(t + T(0.45), "mag_check")
        I.sound(t + T(0.64), "mag_check")
        I.reach("arm_left", t + T(0.82), t + T(0.98), base + (0, -16, 0))
        I.reach("arm_left", t + T(0.98), t + T(1.04), base, e="inquad")
        a.key("magazine", t + T(1.02), pos=(0, 0, 0))
        a.key("magazine", t + T(1.05), pos=(0, 3, 0), e="outquad")
        a.key("magazine", t + T(1.13), pos=(0, 0, 0), e="inoutsine")
        I.sound(t + T(1.04), "tap")
        a.kick("gun", "pos", t + T(1.04), (0, 2.5, 0), attack=0.03, recover=0.2)
        t = t + T(1.15)
    else:
        t = t + T(0.3)

    # 3) roll the top of the receiver towards you and look along it
    I.home("arm_left", t, t + T(0.4))
    I.move(t, t + T(0.65), *D)
    I.creep(t + T(0.65), t + T(1.1), D, ((2, 2, -4), (2, 3, -3)))
    t = t + T(1.15)

    # 4) turn it over to show the left side; the hand goes back onto the handguard
    I.sound(t + T(0.12), "cloth")
    # through the middle of the turn the gun dips down and out, so the stock passes under the cheek, not across it
    I.move(t + T(0.02), t + T(0.5), (10, 0, out), (4 * ang, -4 * ang, 6 * ang), e="inoutsine")
    I.gun(t + T(0.5), t + T(1.0), *B, e="inoutsine")
    I.sound(t + T(1.0), "grip")
    I.creep(t + T(1.0), t + T(1.6), B, ((3, 3, -4), (1, 5, -3)))
    t = t + T(1.6)

    # 5) press-check with whatever the gun has
    t = _press_check(I, kind, t, T, hl)

    # 6) selector off and back on
    sel = _peak(asset, "selector", "rot")
    if sel is not None:
        snd = "selector_ak" if m.name in AK else "selector"
        I.tug("selector", t + T(0.06), sel, out=T(0.1), hold=T(0.16), back=T(0.1), ch="rot", snd=(snd, snd))
        a.kick("gun", "rot", t + T(0.12), (0.6, 0, -0.8), attack=0.04, recover=0.25)
        t = t + T(0.5)

    # 7) a glance down the top / along the scope
    I.move(t, t + T(0.6), *C)
    I.creep(t + T(0.6), t + T(1.0), C, ((-2, 2, -3), (1, 2, 1)))
    t = t + T(1.0)

    # 8) tip the muzzle up and look down it at the front sight
    I.move(t, t + T(0.6), *E)
    I.creep(t + T(0.6), t + T(1.05), E, ((0, 3, -3), (2, -2, 2)))
    t = t + T(1.05)

    # 9) back to ready, the support hand takes its place again
    I.move(t, t + T(0.8), (0, 0, 0), (0, 0, 0))
    I.home("arm_left", t + T(0.05), t + T(0.6))
    I.sound(t + T(0.62), "grip")
    a.length = max(a.length, t + T(0.9))
    return a


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
def _pistol(asset):
    m = asset.model
    spin = m.name == "deagle"
    I = _Inspect(asset, 7.0)
    a = I.a
    A = ((-40, 30, 36), (10, -48, -18))
    B = ((-34, 32, 30), (6, 44, 22))
    C = ((-18, 44, 14), (-12, 6, 4))          # muzzle down a touch: rear sights, hammer, back of the slide
    A2 = ((-36, 34, 30), (4, -58, -28))        # right side again, turned further
    E = ((-22, 46, 20), (26, 10, 6))           # muzzle tipped up towards the crosshair
    away = (-46, -56, 46)
    I.sound(0.0, "grip")
    I.move(0.0, 0.55, *A)
    I.sound(0.06, "cloth")
    I.creep(0.55, 1.15, A, ((-3, 2, -3), (2, -5, 3)))
    t = 1.2
    # press-check: pinch the front of the slide and draw it back a little
    if I.has("slide"):
        lo, hi = _box(m, "slide")
        I.reach("arm_left", t - 0.45, t + 0.25, (lo[0] - 16, (lo[1] + hi[1]) / 2 + 6, lo[2] + 26))
        t0 = t + 0.28
        trav = _peak(asset, "slide", "pos")
        trav = trav if trav is not None else np.array([0.0, 0.0, 40.0])
        I.grab("arm_left", "slide", t0, t0 + 0.42, fade_in=0.04, fade_out=0.05)
        end = I.tug("slide", t0 + 0.02, trav * 0.3, out=0.14, hold=0.14, back=0.07,
                    snd=("press_check", "slide_forward_light"))
        a.kick("gun", "rot", end, (1.2, 0, -0.8), attack=0.03, recover=0.2)
        t = end + 0.06
    elif I.has("bolt"):   # Ruger Mk III: tug the rear bolt ears
        lo, hi = _box(m, "bolt")
        I.reach("arm_left", t - 0.45, t + 0.25, (lo[0] - 10, hi[1] + 6, hi[2] - 8))
        t0 = t + 0.28
        trav = _peak(asset, "bolt", "pos")
        trav = trav if trav is not None else np.array([0.0, 0.0, 30.0])
        I.grab("arm_left", "bolt", t0, t0 + 0.42, fade_in=0.04, fade_out=0.05)
        t = I.tug("bolt", t0 + 0.02, trav * 0.35, out=0.14, hold=0.14, back=0.07,
                  snd=("press_check", "slide_forward_light")) + 0.06
    a.mv("arm_left", t, t + 0.25, pos=away)
    # turn it over to the left side and let it sit there
    I.move(t, t + 0.7, *B)
    I.sound(t + 0.15, "cloth")
    I.creep(t + 0.7, t + 1.3, B, ((-2, 3, -3), (1, 5, -3)))
    t += 1.3
    # magazine: a tap on the base plate
    if I.has("magazine"):
        lo, hi = _box(m, "magazine")
        base = np.array([(lo[0] + hi[0]) / 2 - 6, lo[1] - 12, (lo[2] + hi[2]) / 2])
        I.reach("arm_left", t - 0.3, t, base + (0, -14, 0))
        I.reach("arm_left", t, t + 0.06, base, e="inquad")
        a.key("magazine", t + 0.04, pos=(0, 0, 0))
        a.key("magazine", t + 0.07, pos=(0, 2.5, 0), e="outquad")
        a.key("magazine", t + 0.15, pos=(0, 0, 0))
        I.sound(t + 0.06, "tap")
        a.kick("gun", "pos", t + 0.06, (0, 2.5, 0), attack=0.03, recover=0.18)
        a.mv("arm_left", t + 0.14, t + 0.36, pos=away)
        t += 0.36
    # look down at the rear sights and the back of the slide
    I.move(t, t + 0.55, *C)
    I.creep(t + 0.55, t + 1.0, C, ((2, 2, -2), (-2, 3, 2)))
    t += 1.0
    if spin:
        # the right side once more, then back near the hip and one clean finger spin
        I.move(t, t + 0.6, *A2)
        I.creep(t + 0.6, t + 1.0, A2, ((-2, 2, -2), (1, -3, 2)))
        t += 1.0
        I.move(t, t + 0.35, (0, 4, -6), (2, 0, 0))
        _finger_spin(asset, a, t + 0.38)
        t += 0.38 + 1.0
        I.home("arm_left", t - 0.2, t + 0.15)
        a.length = t + 0.3
        return a
    # the right side once more, turned further, then a look down the muzzle, then back to ready
    I.move(t, t + 0.6, *A2)
    I.creep(t + 0.6, t + 1.0, A2, ((-2, 2, -2), (1, -3, 2)))
    t += 1.0
    I.move(t, t + 0.55, *E)
    I.creep(t + 0.55, t + 0.9, E, ((0, 2, -2), (2, -2, 1)))
    t += 0.9
    I.move(t, t + 0.65, (0, 0, 0), (0, 0, 0))
    I.home("arm_left", t + 0.05, t + 0.5)
    I.sound(t + 0.58, "grip")
    a.length = t + 0.75
    return a


def _revolver(asset):
    m = asset.model
    I = _Inspect(asset, 7.4)
    a = I.a
    B = ((-34, 30, 30), (6, 42, 24))          # left side: where the cylinder swings out / the gate is
    A = ((-38, 30, 34), (10, -40, -16))
    C = ((-18, 44, 14), (-12, 6, 4))          # rear sight and hammer
    I.sound(0.0, "grip")
    I.move(0.0, 0.55, *B)
    I.sound(0.06, "cloth")
    I.creep(0.55, 1.1, B, ((-2, 3, -3), (1, 4, -3)))
    t = 1.1
    cyl = "cylinder"
    if I.has("crane"):
        cr = _peak(asset, "crane", "rot")
        cr = cr if cr is not None else np.array([0.0, 0.0, 80.0])
        lo, hi = _box(m, cyl)
        I.reach("arm_left", t - 0.4, t + 0.2, (lo[0] - 12, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2))
        t0 = t + 0.24
        I.grab("arm_left", cyl, t0, t0 + 0.24, fade_in=0.04, fade_out=0.06)
        a.key("crane", t0, rot=(0, 0, 0))
        a.key("crane", t0 + 0.22, rot=cr, e="outquad")
        I.sound(t0 + 0.04, "cylinder_latch")
        I.sound(t0 + 0.18, "cylinder_open")
        # flick the cylinder round with a finger and let it run down
        a.mv("arm_left", t0 + 0.3, t0 + 0.42, pos=(-30, -20, 40))
        t1 = t0 + 0.4
        a.key(cyl, t1, rot=(0, 0, 0))
        a.key(cyl, t1 + 0.35, rot=(0, 0, -400), e="outquad")
        a.key(cyl, t1 + 0.9, rot=(0, 0, -720), e="outcubic")
        I.sound(t1 + 0.02, "cylinder_spin")
        # wrist flick shuts it
        t2 = t1 + 0.95
        a.key("crane", t2, rot=cr)
        a.key("crane", t2 + 0.12, rot=(0, 0, 0), e="inquad")
        a.kick("gun", "rot", t2, (0, -6, -10), attack=0.1, recover=0.3)
        I.sound(t2 + 0.12, "cylinder_close")
        t = t2 + 0.3
    elif I.has("gate"):
        gt = _peak(asset, "gate", "rot")
        gt = gt if gt is not None else np.array([0.0, 0.0, -80.0])
        lo, hi = _box(m, "gate")
        I.reach("arm_left", t - 0.4, t + 0.2, (hi[0] + 10, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2))
        t0 = t + 0.24
        a.key("gate", t0, rot=(0, 0, 0))
        a.key("gate", t0 + 0.12, rot=gt, e="outquad")
        I.sound(t0 + 0.08, "loading_gate")
        step = _peak(asset, cyl, "rot")
        step = step if step is not None else np.array([0.0, 0.0, -60.0])
        n = int(round(360.0 / max(1.0, abs(float(step[2])))))
        tt = t0 + 0.2
        for i in range(n):
            a.key(cyl, tt, rot=step * i)
            a.key(cyl, tt + 0.08, rot=step * (i + 1), e="outquad")
            I.sound(tt + 0.06, "click_small")
            tt += 0.15
        a.key("gate", tt + 0.05, rot=gt)
        a.key("gate", tt + 0.15, rot=(0, 0, 0), e="inquad")
        I.sound(tt + 0.13, "loading_gate")
        t = tt + 0.25
    a.mv("arm_left", t - 0.1, t + 0.2, pos=(-46, -56, 46))
    I.creep(t, t + 0.45, B, ((-3, 4, -4), (2, 6, -2)))
    t += 0.45
    # show the other side, a look at the rear sight and hammer, back near the hip, one clean finger spin
    I.move(t, t + 0.6, *A)
    I.creep(t + 0.6, t + 1.1, A, ((-2, 2, -3), (1, -4, 2)))
    t += 1.1
    I.move(t, t + 0.5, *C)
    I.creep(t + 0.5, t + 0.85, C, ((2, 2, -2), (-2, 3, 2)))
    t += 0.85
    I.move(t, t + 0.35, (0, 4, -6), (2, 0, 0))
    _finger_spin(asset, a, t + 0.38)
    t += 0.38 + 1.0
    if m.name == "singlesix" and I.has("hammer"):
        cock = _peak(asset, "hammer", "rot", prefer=("fire",))
        if cock is not None:
            a.key("hammer", t, rot=(0, 0, 0))
            a.key("hammer", t + 0.12, rot=cock, e="outquad")
            a.key("hammer", t + 0.3, rot=cock)
            a.key("hammer", t + 0.42, rot=(0, 0, 0), e="inquad")
            I.sound(t + 0.1, "hammer_cock")
            t += 0.3
    I.home("arm_left", t - 0.25, t + 0.15)
    a.length = t + 0.35
    return a


def _finger_spin(asset, a, t0):
    """One clean turn on the trigger finger, in a plane angled to the eye, slowing into the catch."""
    hr = np.asarray(asset.model.bones["arm_right"].pivot, dtype=float)
    rig = motion._Rig(a, t0, (0.0, hr[1] + 24.0, hr[2] - 36.0))
    spin = motion._scalar([(0.04, 0.0), (0.14, -40.0), (0.36, -210.0), (0.58, -330.0), (0.74, -360.0)])
    amp = motion._scalar([(0.04, 0.0), (0.2, 1.0), (0.5, 1.0), (0.74, 0.0)])
    tilt = motion.path([(0.0, (0, 0, 0)), (0.14, (0, 26, 10)), (0.4, (0, 34, 4)), (0.74, (0, 24, 8)),
                        (1.0, (0, 0, 0))])

    def rot(u):
        th, w = spin(u), amp(u)
        r = np.radians(th)
        return np.array([th, 8.0 * w * np.cos(r), 10.0 * w * np.sin(r)]) + tilt(u)

    base = motion.path([(0.0, (0, 0, 0)), (0.14, (-12, 24, -70)), (0.42, (-14, 40, -90)), (0.74, (-8, 26, -70)),
                        (1.0, (0, 0, 0))])

    def off(u):
        r, w = np.radians(spin(u)), amp(u)
        return base(u) + w * np.array([0.0, 8.0 * np.sin(r), 8.0 * np.cos(r) - 8.0])

    rig.rot, rig.off = rot, off
    rig.gun()
    rig.hand("arm_right", off)
    a.sound(t0 + 0.06, "grip")
    a.sound(t0 + 0.26, "spin_whoosh")
    a.sound(t0 + 0.5, "spin_whoosh")
    a.sound(t0 + 0.74, "grip")


# ------------------------------------------------------------------------------------------------
def cs2_inspect(asset):
    kind = motion.KIND.get(asset.model.name, "rifle")
    if kind == "pistol":
        return _pistol(asset)
    if kind == "revolver":
        return _revolver(asset)
    return _long(asset, kind)
