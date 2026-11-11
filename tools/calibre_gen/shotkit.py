"""shotkit.py: shared construction for pump / semi-automatic shotguns and lever actions: receivers with a real ejection
opening (the bolt shows through it), barrels with ribs and beads, magazine tubes, pump fore-ends and butt stocks."""
from .core import Bone
from .common import moving
from .parts import barrel, pins
from .riflekit import stock as _stock, butt_plate


def sg_receiver(body: Bone, z0, z1, mat, hw=17.0, y0=-30.0, y1=22.0, port=(-80, -10), load=(-100, -20), r=5.0,
                pin=True, port_y=-8.0):
    """
    Shotgun receiver with rounded top. The ejection port on the right is a real opening: the receiver is built around
    it (front block, rear block, floor, left wall, roof) with a dark back wall, so a bolt placed inside shows through
    and disappears into the rear block when it runs back. Returns the y of the port's upper edge.
    """
    roof = y1 - 2 * r - 0.6
    if port:
        p0, p1 = port
        body.rbox(-hw, hw, y0, y1, z0, p0, mat, r=r, edges="top")
        body.rbox(-hw, hw, y0, y1, p1, z1, mat, r=r, edges="top")
        body.box(-hw, hw, y0, port_y, p0, p1, mat)                                   # floor
        body.box(-hw, 4.0, port_y, roof, p0, p1, mat)                                # left wall
        body.rbox(-hw, hw, roof, y1, p0, p1, mat, r=r, edges="top")                  # roof
        body.box(3.6, 4.4, port_y, roof, p0, p1, "rubber")                           # shadowed back wall
        body.box(4.4, hw, port_y, port_y + 0.4, p0, p1, "rubber")
    else:
        body.rbox(-hw, hw, y0, y1, z0, z1, mat, r=r, edges="top")
    if load:
        body.box(-hw * 0.7, hw * 0.7, y0 - 0.4, y0 + 2, load[0], load[1], "rubber")  # loading port underneath
    if pin:
        pins(body, hw, [(y0 + 12, z0 + 36), (y0 + 9, z1 - 44)], d=4.5, mat="steel")  # trigger plate pins
    return roof


def port_bolt(bone: Bone, port, hw=17.0, y0=-7.5, roof=11.0, mat="steel_light"):
    """The bolt as seen through the ejection opening of `sg_receiver`."""
    p0, p1 = port
    bone.box(4.5, hw - 0.5, y0, roof - 0.4, p0 + 2, p1 - 2, mat)
    bone.box(hw - 0.9, hw - 0.4, (y0 + roof) / 2 - 2, (y0 + roof) / 2 + 2, p0 + 4, p0 + 20, "steel_dark")   # extractor


def sg_barrel(body: Bone, z0, z1, d=22.0, y=4.0, mat="steel", bead=True, rib=None, post_gap=58.0):
    """Barrel with an optional ventilated rib and a brass bead. Returns the height of the top of the bead (or rib)."""
    barrel(body, z0, z1, d=d, mat=mat, y=y)
    top = y + d / 2
    if rib:
        z = z1 + 14
        while z < z0 - 20:
            body.box(-2.2, 2.2, top - 0.6, top + 3.2, z, z + 16, rib)
            z += post_gap
        body.box(-4.2, 4.2, top + 3, top + 5.4, z1 + 6, z0 + 2, rib)
        top += 5.4
    if bead:
        body.box(-1.6, 1.6, top - 0.2, top + 3.2, z1 + 7, z1 + 10.4, "brass")
        top += 3.2
    return top


def sg_tube(body: Bone, z0, z1, y=-22.0, d=22.0, mat="steel", cap=True, ring=None, barrel_y=4.0, barrel_d=22.0):
    """Magazine tube from the receiver (z0) forward to z1, with its knurled cap and an optional barrel clamp at `ring`."""
    body.cyl((0, y, (z0 + z1) / 2), d, z0 - z1, mat)
    if cap:
        body.cyl((0, y, z1 - 5), d + 4, 10, mat)
        for k in range(8):
            body.box(-d / 2 - 2.3, d / 2 + 2.3, y - 1, y + 1, z1 - 9, z1 - 1, "steel_dark", rot=(0, 0, k * 22.5),
                     pivot=(0, y, z1 - 5))
        body.cyl((0, y, z1 - 10.3), 6, 0.6, "steel_dark", sides=8)
    if ring is not None:
        body.cyl((0, barrel_y, ring), barrel_d + 4, 14, mat)
        body.rbox(-6, 6, y + d / 2 - 3, barrel_y - barrel_d / 2 + 2, ring - 8, ring + 8, mat, r=2)


def forend(pump: Bone, z0, z1, mat, hw=21.0, y0=-42.0, y1=-4.0, grooves=8, groove_mat="rubber", bars_to=-60.0,
           bar_y=-10.0, bar_mat="steel", r=9.0):
    """Pump fore-end (z0 < z1) with finger grooves and the two action bars running back into the receiver."""
    pump.rbox(-hw, hw, y0, y1, z0, z1, mat, r=r)
    if grooves:
        step = (z1 - z0 - 16) / grooves
        for i in range(grooves):
            z = z0 + 8 + i * step
            for sx in (-1, 1):
                pump.box(sx * hw - 0.35, sx * hw + 0.35, y0 + r * 0.7, y1 - r * 0.7, z + step * 0.25, z + step * 0.7,
                         groove_mat)
    for sx in (-1, 1):
        pump.box(sx * 4.5 - 1.5, sx * 4.5 + 1.5, bar_y - 4, bar_y + 4, z1, bars_to, bar_mat)


def sg_butt(b: Bone, mat, z0, zb, *, top0=16.0, bot0=-30.0, comb=-8.0, heel=-34.0, toe=-124.0, grip=True,
            hw=(15.0, 17.5), pad="rubber", pad_th=14.0, plate="polymer", spacer=None, checker=None):
    """
    Shotgun / carbine butt from the back of the receiver (z0) to zb (the rear-most point, pad included): wrist, an
    optional pistol-grip curve, the comb falling to the heel and the toe line. Returns (top, bot).
    """
    ze = zb - 3 - (pad_th if pad else 0) - (1.6 if spacer else 0)
    top = [(z0, top0), (z0 + 44, top0 - 16), (z0 + 100, comb), (ze, heel)]
    bot = [(z0, bot0), (z0 + 10, bot0 - 6)]
    if grip:
        bot += [(z0 + 44, bot0 - 38), (z0 + 66, bot0 - 39), (z0 + 84, bot0 - 26)]
    else:
        bot += [(z0 + 70, bot0 - 18)]
    bot.append((ze, toe))
    _stock(b, top, bot, [(z0, z0 + 100, hw[0]), (z0 + 100, ze, hw[1])], mat)
    butt_plate(b, ze, toe, heel, hw[1], plate, th=3, pad=pad, pad_th=pad_th, spacer=spacer)
    if checker and grip:
        for sx in (-1, 1):
            b.box(sx * hw[0] - 0.3, sx * hw[0] + 0.3, bot0 - 24, bot0 + 2, z0 + 36, z0 + 62, checker)
    return top, bot


def crossbolt(body: Bone, z, y, hw=5.0, name="safety", d=7.0):
    """Cross-bolt safety button through the trigger guard; pressing it slides it across."""
    b = body.bone(name, pivot=(0, y, z))
    b.cyl((0.8, y, z), d, hw * 2 + 3, "steel", axis="x", sides=8)
    b.cyl((-hw - 1.2, y, z), d + 0.6, 0.8, "shell_red", axis="x", sides=8)
    moving(body.model, name, pos=(-2.4, 0, 0))
    return b
