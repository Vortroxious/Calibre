"""Procedural finishes painted into the packed UV islands."""
from __future__ import annotations

import hashlib
import math
import os

import numpy as np
from PIL import Image

# name: (rgb, noise, style)
MATERIALS = {
    # metals
    "steel_dark": ((54, 56, 60), 6, "metal"),        # parkerized / nitrided slide
    "steel": ((86, 89, 96), 7, "metal"),             # blued / bare-ish parts
    "steel_light": ((142, 145, 150), 8, "metal"),    # polished: bolt carriers, barrels
    "chrome": ((182, 186, 192), 8, "metal"),
    "alloy": ((60, 62, 66), 4, "anodized"),          # black hard-anodized aluminium (reads lighter than polymer)
    "alloy_tan": ((158, 136, 102), 5, "anodized"),   # FDE anodized
    "alloy_grey": ((80, 83, 87), 4, "anodized"),
    "stainless": ((168, 170, 170), 8, "metal"),
    # polymers
    "polymer": ((40, 40, 42), 5, "polymer"),
    "polymer_tan": ((162, 140, 106), 6, "polymer"),
    "polymer_od": ((84, 90, 64), 6, "polymer"),
    "polymer_grey": ((76, 78, 81), 5, "polymer"),
    "polymer_clear": ((126, 126, 118), 5, "polymer"),  # AUG translucent mag
    "rubber": ((28, 28, 29), 3, "polymer"),
    # wood
    "wood": ((124, 70, 39), 10, "wood"),             # walnut
    "wood_red": ((138, 63, 36), 10, "wood"),         # AK laminated / SVD
    "wood_light": ((172, 122, 74), 10, "wood"),
    # misc
    "brass": ((204, 160, 68), 8, "metal"),
    "copper": ((186, 108, 62), 7, "metal"),
    "lead": ((116, 116, 122), 7, "metal"),
    "shell_red": ((158, 32, 30), 6, "polymer"),
    "shell_green": ((48, 104, 54), 6, "polymer"),
    "glass": ((34, 50, 74), 3, "glass"),
    "glass_amber": ((146, 102, 34), 3, "glass"),
    "emissive_red": ((255, 40, 30), 0, "flat"),
    "emissive_green": ((60, 255, 90), 0, "flat"),
    "white": ((228, 228, 222), 3, "polymer"),
    "sight_orange": ((238, 124, 24), 2, "flat"),
    "sight_white": ((242, 242, 238), 2, "flat"),
    "tritium": ((120, 255, 90), 2, "flat"),
    "olive": ((80, 88, 54), 6, "paint"),
    "rocket_green": ((76, 86, 56), 6, "paint"),
    "warhead": ((102, 106, 96), 6, "paint"),
    "canvas": ((98, 94, 66), 8, "canvas"),
    "leather": ((98, 60, 34), 8, "canvas"),
    "steel_parked": ((66, 68, 62), 6, "metal"),      # greenish parkerized (FAL, M14)
}


def _rng(seed_text):
    h = hashlib.md5(seed_text.encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "little"))


def _smooth(a, k=3):
    """Cheap separable box blur (keeps grain soft instead of speckled)."""
    out = a.copy()
    for axis in (0, 1):
        acc = np.zeros_like(out)
        for d in range(-(k // 2), k // 2 + 1):
            acc += np.roll(out, d, axis=axis)
        out = acc / k
    return out


def paint_patch(mat, w, h, face, seed, plain=False):
    """
    Clean, high-resolution finish: flat base colour with a soft light falloff, very low-contrast material detail
    (brushing, grain, stipple), and a crisp bevel on every edge — a dark 1 px outline with a light inner line — so parts
    read as machined pieces with clean panel lines. `plain` faces (polygon caps, inner pieces of tapered shapes) get
    no bevel so they blend into their neighbours.
    """
    rgb, noise, style = MATERIALS[mat]
    rng = _rng(f"{mat}:{seed}:{w}x{h}:{face}")
    col = np.array(rgb, dtype=float)
    base = np.ones((h, w, 3), dtype=float) * col
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    fy = yy / max(1, h - 1)
    base *= (1.035 - 0.07 * fy)[..., None]                       # soft top-lit falloff
    along_x = w >= h
    if style == "metal":
        streak = rng.normal(0, 1, (h, 1)) if along_x else rng.normal(0, 1, (1, w))
        streak = np.broadcast_to(streak, (h, w))
        base += (_smooth(streak, 3) * noise * 0.22)[..., None]   # faint brushing along the long axis
    elif style == "anodized":
        base += (_smooth(rng.normal(0, 1, (h, w)), 3) * noise * 0.18)[..., None]
    elif style == "polymer":
        base += (_smooth(rng.normal(0, 1, (h, w)), 3) * noise * 0.3)[..., None]   # fine, soft stipple
    elif style == "wood":
        coord = yy if along_x else xx
        other = xx if along_x else yy
        freq = rng.uniform(0.18, 0.3)
        warp = np.sin(other * rng.uniform(0.015, 0.04) + rng.uniform(0, 6)) * 4.0
        grain = np.sin((coord + warp) * freq + rng.uniform(0, 6)) * 0.5 + 0.5
        grain = grain ** 2
        base *= (0.95 + 0.09 * grain)[..., None]
    elif style == "glass":
        base += (1 - fy)[..., None] * 36
        if w > 3 and h > 3:
            base[1:2, 1:max(2, w // 3)] += 80
    elif style == "paint":
        base += (_smooth(rng.normal(0, 1, (h, w)), 3) * noise * 0.25)[..., None]
    elif style == "canvas":
        base += (((xx.astype(int) + yy.astype(int)) % 2) * 5.0)[..., None]
    # face lighting so the three visible sides of a part separate even under flat light
    base *= {"up": 1.07, "down": 0.86, "east": 1.0, "west": 0.96, "north": 0.98, "south": 0.94}.get(face, 1.0)
    if style != "flat" and not plain and w >= 4 and h >= 4:
        light = np.minimum(255, base * 1.12 + 10)
        base[1, 1:-1] = light[1, 1:-1]                            # inner highlight along the top and left edges
        base[1:-1, 1] = light[1:-1, 1]
        if style in ("metal", "anodized") and w >= 8:
            base[1, 2:-2] = np.minimum(255, base[1, 2:-2] * 1.06 + 8)
        base[-2, 1:-1] *= 0.93                                     # soft inner shadow on the opposite edges
        base[1:-1, -2] *= 0.95
        base[0, :] *= 0.66                                         # crisp dark outline = panel line
        base[-1, :] *= 0.62
        base[:, 0] *= 0.68
        base[:, -1] *= 0.64
    return np.clip(base, 0, 255).astype(np.uint8)


def paint_texture(model, path):
    img = np.zeros((model.tex_h, model.tex_w, 4), dtype=np.uint8)
    for bi, b in enumerate(model.order):
        for ci, c in enumerate(b.cubes):
            for f, (u, v, w, h) in c.uv.items():
                patch = paint_patch(c.mat, w, h, f, f"{model.name}:{b.name}:{ci}", plain=f in getattr(c, "plain", ()))
                img[v:v + h, u:u + w, :3] = patch
                img[v:v + h, u:u + w, 3] = 255
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(img, "RGBA").save(path, optimize=True)
    return img


def material_color(mat):
    return MATERIALS[mat][0]
