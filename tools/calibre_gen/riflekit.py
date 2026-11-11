"""riflekit.py: shared construction for bolt-action and wood-stocked rifles: stock silhouettes, bands, hand guards,
round receivers, turn bolts and stepped barrels."""
import numpy as np

from .core import Bone, euler_mat
from .parts import barrel, screw, sling_swivel


def cut(line, z0, z1):
    """Clip a polyline [(z, y), ...] to z0..z1, interpolating the end points."""
    def at(z):
        for (za, ya), (zb, yb) in zip(line, line[1:]):
            if za - 1e-6 <= z <= zb + 1e-6:
                return ya + (yb - ya) * (z - za) / max(1e-6, zb - za)
        return line[-1][1] if z > line[-1][0] else line[0][1]
    return [(z0, at(z0))] + [(z, y) for z, y in line if z0 + 0.5 < z < z1 - 0.5] + [(z1, at(z1))]


def stock(b: Bone, top, bot, widths, mat):
    """Stock from a side silhouette (top / bottom polylines) with a half-width per z band: [(z0, z1, hw), ...]."""
    for z0, z1, hw in widths:
        b.profile(-hw, hw, cut(top, z0, z1), cut(bot, z0, z1), mat)


def mil_stock(b: Bone, mat, *, nose, butt, action=(-110, 110), fore=(2, -30, -40), belly=-52, wrist=(-14, -60),
              grip=False, comb=None, hw=(15, 18, 14.5, 17), bottom_at=None):
    """
    One-piece military stock: fore-end from `nose` to the action, a deeper belly under the receiver, the wrist and the
    butt. butt = (z_end, heel_y, toe_y); grip=True adds a semi pistol grip; comb = y of a raised comb nose.
    Returns (top, bot) so callers can place bands and swivels on the outline.
    """
    a0, a1 = action
    zb, heel, toe = butt
    ab = a1 if bottom_at is None else bottom_at          # where the underside leaves the action (SKS: well forward)
    top = [(nose, fore[0]), (a1 - 12, fore[0]), (a1 + 30, wrist[0] + 2), (a1 + 74, wrist[0] - 4)]
    if comb is not None:
        top.append((a1 + 116, comb))
    top.append((zb, heel))
    bot = [(nose, fore[1]), (a0, fore[2]), (a0 + 14, belly), (ab - 12, belly), (ab + 30, wrist[1] + 3)]
    if grip:
        bot += [(ab + 74, wrist[1] - 23), (ab + 100, wrist[1] - 24), (ab + 116, wrist[1] - 10)]
    else:
        bot.append((ab + 74, wrist[1] - 2))
    bot.append((zb, toe))
    w = [(nose, a0, hw[0]), (a0, a1 + 30, hw[1]), (a1 + 30, a1 + 116, hw[2]), (a1 + 116, zb, hw[3])]
    stock(b, top, bot, [x for x in w if x[1] - x[0] > 1], mat)
    return top, bot


def line_y(line, z):
    return cut(line, z, z + 1)[0][1]


def butt_plate(b: Bone, z, y0, y1, hw, mat="steel", th=4.0, pad=None, pad_th=14.0, spacer=None):
    """Butt plate (and optional recoil pad) closing a stock at z. Returns the rear-most z."""
    b.rbox(-hw - 0.4, hw + 0.4, y0 - 0.6, y1 + 0.6, z - 0.5, z + th, mat, r=2.5, axis="z")
    ze = z + th
    if spacer:
        b.box(-hw - 0.5, hw + 0.5, y0 - 0.7, y1 + 0.7, ze, ze + 1.6, spacer)
        ze += 1.6
    if pad:
        b.rbox(-hw - 0.6, hw + 0.6, y0 - 0.8, y1 + 0.8, ze, ze + pad_th, pad, r=4.0, axis="z")
        for i in range(5):
            yy = y0 + (y1 - y0) * (i + 0.5) / 5
            b.box(-hw + 3, hw - 3, yy - 1.6, yy + 1.6, ze + pad_th, ze + pad_th + 0.5, "polymer")
        ze += pad_th
    else:
        for yy in (y1 - (y1 - y0) * 0.2, y0 + (y1 - y0) * 0.2):
            b.cyl((0, yy, ze + 0.2), 6, 0.6, "steel_light", sides=8)
            b.box(-2.4, 2.4, yy - 0.4, yy + 0.4, ze + 0.45, ze + 0.65, "rubber")
    return ze


def band(b: Bone, z, y0, y1, hw, mat, w=12.0, swivel=False, screw_side=1):
    """Barrel band clamping fore-end and hand guard, with its screw and optionally a sling swivel underneath."""
    b.rbox(-hw, hw, y0, y1, z - w / 2, z + w / 2, mat, r=min(5.0, hw * 0.35), axis="z")
    if screw_side:
        screw(b, screw_side * hw, y0 + (y1 - y0) * 0.3, z, d=4.0)
    if swivel:
        sling_swivel(b, 0, y0, z, along="x", w=22.0, drop=12.0, mat=mat)


def handguard(b: Bone, z0, z1, hw, y0, y1, mat, caps=None):
    """Upper hand guard: a half-round wooden cover over the barrel, optionally with metal end caps."""
    b.rbox(-hw, hw, y0, y1, z0, z1, mat, r=min(6.5, hw * 0.5, (y1 - y0) * 0.8), axis="z", edges="top")
    if caps:
        for z in (z0, z1):
            b.rbox(-hw - 0.4, hw + 0.4, y0, y1 + 0.4, z - 3, z + 3, caps, r=min(6.5, hw * 0.5), axis="z", edges="top")


def receiver(b: Bone, z0, z1, d, mat, port=None, ring=None, bridge=None, tang=None, sides=None, side_port=True):
    """
    Tubular bolt-action receiver. port = (z0, z1) of the loading / ejection opening, ring = length of the thicker
    front ring, bridge = (z0, z1, height) of the rear bridge, tang = (z_end, y0, y1).
    """
    b.cyl((0, 0, (z0 + z1) / 2), d, z1 - z0, mat, sides=sides)
    r = d / 2
    if ring:
        b.cyl((0, 0, z0 + ring / 2), d + 2.4, ring, mat, sides=sides)
        b.cyl((0, r + 0.9, z0 + ring * 0.5), 3, 0.8, "rubber", axis="y", sides=8)          # gas escape hole
    if port:
        b.box(-r * 0.36, r * 0.36, r - 2, r + 0.45, port[0], port[1], "rubber")
        if side_port:
            b.box(0, r * 0.82, r * 0.1, r * 0.7, port[0] + 4, port[1], "rubber")
    if bridge:
        b.rbox(-r * 0.62, r * 0.62, r - 4, r + bridge[2], bridge[0], bridge[1], mat, r=2.5, axis="z", edges="top")
    if tang:
        b.rbox(-6, 6, tang[1], tang[2], z1 - 2, tang[0], mat, r=2.0, axis="z", edges="top")
        b.cyl((0, tang[2] + 0.2, (z1 + tang[0]) / 2 + 6), 6, 0.6, "steel", axis="y", sides=8)   # tang screw


def stepped_barrel(b: Bone, z_breech, z_muzzle, d_breech, d_muzzle, mat, reinforce=110.0, cone=60.0, taper=1.25):
    """Military barrel: thick chamber reinforce, a short cone, then a gentle taper to the crowned muzzle."""
    z1 = z_breech - reinforce
    z2 = z1 - cone
    d_mid = d_muzzle * taper
    b.cyl((0, 0, (z_breech + z1) / 2), d_breech, reinforce, mat, sides=16)
    b.cyl((0, 0, (z1 + z2) / 2), d_mid, cone + 0.3, mat, d2=d_breech, steps=2, sides=16)
    zt = z_muzzle + 60
    b.cyl((0, 0, (z2 + zt) / 2), d_muzzle, z2 - zt + 0.3, mat, d2=d_mid, steps=3, sides=16)
    barrel(b, zt, z_muzzle, d=d_muzzle, mat=mat)


def bolt(m, z_front, z_rear, handle_z, *, parent="body", d=18.0, mat="steel_light", handle_len=44.0, droop=6.0,
         sweep=0.0, knob_d=18.0, knob="ball", knob_mat=None, cock=None, cock_mat="steel"):
    """
    Turn bolt as the `bolt` bone: body with locking lugs, extractor rib, handle root collar, a round handle shank and
    its knob ('ball' or a long 'tactical' cylinder), plus the cocking piece (d, length) behind it.
    droop tilts the handle down, sweep rakes it back. Returns the bone.
    """
    b = m[parent].bone("bolt", pivot=(0, 0, 0))
    b.cyl((0, 0, (z_front + z_rear) / 2), d, z_rear - z_front, mat)
    b.box(-d / 2 - 2.5, d / 2 + 2.5, -3.5, 3.5, z_front, z_front + 10, mat)                 # locking lugs
    b.cyl((0, 0, z_front - 0.3), d * 0.6, 0.6, "steel_dark", sides=8)                        # bolt face
    b.box(-3, 3, d / 2 - 1, d / 2 + 1.6, z_front + 10, handle_z - 12, "steel")              # guide rib
    b.cyl((0, 0, handle_z), d + 3, 9, mat)                                                   # handle collar
    root = np.array([d / 2 - 2, 0.0, handle_z])
    rot = (0, -sweep, -droop)
    b.rbox(d / 2 - 2, d / 2 + handle_len, -3.6, 3.6, handle_z - 3.6, handle_z + 3.6, mat, r=2.4, axis="x", rot=rot,
           pivot=tuple(root))
    R = euler_mat(rot)
    km = knob_mat or mat
    if knob == "tactical":
        kc = root + R @ np.array([handle_len + 8.0, 0, 0])
        b.rbox(kc[0] - 14, kc[0] + 14, kc[1] - knob_d / 2, kc[1] + knob_d / 2, kc[2] - knob_d / 2, kc[2] + knob_d / 2,
               km, r=knob_d * 0.3, axis="x", rot=(0, 0, -droop), pivot=tuple(kc))
    else:
        kc = root + R @ np.array([handle_len + knob_d * 0.25, 0, 0])
        b.cyl(tuple(kc), knob_d, knob_d * 0.4, km, axis="x", sides=16)
        b.cyl((kc[0] + knob_d * 0.34, kc[1], kc[2]), knob_d * 0.94, knob_d * 0.3, km, axis="x", d2=knob_d * 0.5, steps=2,
              sides=16)
        b.cyl((kc[0] - knob_d * 0.34, kc[1], kc[2]), knob_d * 0.5, knob_d * 0.3, km, axis="x", d2=knob_d * 0.94, steps=2,
              sides=16)
    if cock:
        b.cyl((0, 0, z_rear + cock[1] / 2), cock[0], cock[1], cock_mat)
        b.cyl((0, 0, z_rear + cock[1] + 0.3), cock[0] * 0.5, 0.6, "steel_dark", sides=8)
    return b


def rides(m, dst, src="bolt"):
    """Make bone `dst` slide with `src` in every animation without turning with it (bolt shrouds, safety flags,
    dust covers)."""
    m.follow.append((src, dst))
