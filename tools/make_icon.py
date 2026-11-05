#!/usr/bin/env python3
"""
Calibre emblem icon: the mod's own AKM and Glock models crossed over a gunmetal shield with brass trim,
a crosshair ring and the name.

  python3 tools/make_icon.py            # writes the in-mod icon (256 px) and tools/modrinth/icon.png (512 px)
"""
import math
import os
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

from build_assets import all_guns  # noqa: E402
from calibre_gen import core, materials, preview as pv  # noqa: E402

S = 2048                        # working resolution (supersampled)
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
BRASS_HI, BRASS_LO = (246, 214, 130), (150, 98, 34)
METAL_HI, METAL_LO = (52, 58, 68), (16, 18, 22)


def gun_sprite(name, width):
    """Side render of a gun with real alpha (rendered on black and on white)."""
    asset = all_guns()[name]()
    m = asset.model
    core.pack_uv(m)
    with tempfile.TemporaryDirectory() as td:
        tex = materials.paint_texture(m, os.path.join(td, "t.png"))
    idle = next(a for a in asset.anims if a.name == "idle")
    pose = idle.pose(0.0)
    lo, hi = m.bounds()
    aspect = float(hi[2] - lo[2]) / float(hi[1] - lo[1])
    w = width
    h = int(w / aspect * 1.15)
    shots = [np.asarray(pv.render(m, pose, tex, "side", size=(w, h), arms=False, bg=bg).convert("RGB"), dtype=float)
             for bg in ((0, 0, 0), (255, 255, 255))]
    k, wh = shots
    alpha = np.clip(1.0 - (wh - k).mean(axis=2) / 255.0, 0, 1)
    rgb = np.where(alpha[..., None] > 1e-3, k / np.maximum(alpha[..., None], 1e-3), 0)
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    return im.crop(im.getbbox())


def vgrad(size, top, bottom):
    w, h = size
    t = np.linspace(0, 1, h)[:, None, None]
    g = np.array(top)[None, None, :] * (1 - t) + np.array(bottom)[None, None, :] * t
    return Image.fromarray(np.repeat(g, w, axis=1).astype(np.uint8), "RGB")


def shield_points(cx, top, w, bottom, n=60):
    """Heater shield: flat top with rounded shoulders, sides curving to a point."""
    hw = w / 2
    pts = []
    r = w * 0.09
    for i in range(n // 6 + 1):          # left shoulder
        a = math.pi + (math.pi / 2) * i / (n // 6)
        pts.append((cx - hw + r + r * math.cos(a), top + r + r * math.sin(a)))
    for i in range(n // 6 + 1):          # right shoulder
        a = 1.5 * math.pi + (math.pi / 2) * i / (n // 6)
        pts.append((cx + hw - r + r * math.cos(a), top + r + r * math.sin(a)))
    side_top = top + (bottom - top) * 0.42
    pts.append((cx + hw, side_top))
    for i in range(1, n + 1):            # right curve down to the point
        u = i / n
        pts.append((cx + hw * (1 - u) ** 1.6 * math.cos(u * 0.35), side_top + (bottom - side_top) * u))
    for i in range(n, 0, -1):            # left curve back up
        u = i / n
        pts.append((cx - hw * (1 - u) ** 1.6 * math.cos(u * 0.35), side_top + (bottom - side_top) * u))
    pts.append((cx - hw, side_top))
    return pts


def mask_from(points):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).polygon(points, fill=255)
    return m


def paste_rot(canvas, sprite, angle, center, shadow=True):
    sp = sprite.rotate(angle, resample=Image.BICUBIC, expand=True)
    x, y = int(center[0] - sp.width / 2), int(center[1] - sp.height / 2)
    # thin light rim so the dark steel separates from the dark field
    a0 = sp.split()[3]
    rim_a = a0.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(2))
    rim = Image.new("RGBA", sp.size, (236, 214, 160, 0))
    rim.putalpha(rim_a.point(lambda v: int(v * 0.85)))
    if shadow:
        a = sp.split()[3].filter(ImageFilter.GaussianBlur(S * 0.012))
        sh = Image.new("RGBA", sp.size, (0, 0, 0, 0))
        sh.putalpha(a.point(lambda v: int(v * 0.75)))
        canvas.alpha_composite(sh, (x + int(S * 0.012), y + int(S * 0.02)))
    canvas.alpha_composite(rim, (x, y))
    canvas.alpha_composite(sp, (x, y))


def circle_mask(c, r):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=255)
    return m


def make():
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = (S / 2, S * 0.46)
    R = S * 0.44
    # brass rim, a dark groove, gunmetal field
    canvas.paste(vgrad((S, S), BRASS_HI, BRASS_LO).convert("RGBA"), (0, 0), circle_mask(c, R))
    canvas.paste(Image.new("RGBA", (S, S), (24, 18, 8, 255)), (0, 0), circle_mask(c, R * 0.925))
    canvas.paste(vgrad((S, S), METAL_HI, METAL_LO).convert("RGBA"), (0, 0), circle_mask(c, R * 0.905))
    # soft sheen on the upper half of the field
    sheen = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sheen).ellipse((c[0] - R * 0.8, c[1] - R * 1.05, c[0] + R * 0.8, c[1] - R * 0.05), fill=34)
    sheen = sheen.filter(ImageFilter.GaussianBlur(S * 0.04))
    sheen = Image.composite(sheen, Image.new("L", (S, S), 0), circle_mask(c, R * 0.905))
    canvas.alpha_composite(Image.merge("RGBA", (Image.new("L", (S, S), 255),) * 3 + (sheen,)))
    # crosshair ring behind the guns
    ring_r = R * 0.62
    ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rw = int(S * 0.012)
    col = BRASS_HI + (120,)
    rd.ellipse((c[0] - ring_r, c[1] - ring_r, c[0] + ring_r, c[1] + ring_r), outline=col, width=rw)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        r0, r1 = ring_r * 0.72, ring_r * 1.2
        rd.line((c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a), c[0] + r1 * math.cos(a), c[1] + r1 * math.sin(a)),
                fill=col, width=rw)
    rd.ellipse((c[0] - S * 0.01, c[1] - S * 0.01, c[0] + S * 0.01, c[1] + S * 0.01), fill=col)
    canvas.alpha_composite(ring)
    # crossed guns forming an X: rifle muzzle up-right, pistol muzzle up-left in front of it
    rifle = gun_sprite("akm", int(S * 0.9)).transpose(Image.FLIP_LEFT_RIGHT)
    rifle = rifle.resize((int(S * 0.8), int(S * 0.8 * rifle.height / rifle.width)), Image.LANCZOS)
    pistol = gun_sprite("glock17", int(S * 0.5))
    pistol = pistol.resize((int(S * 0.34), int(S * 0.34 * pistol.height / pistol.width)), Image.LANCZOS)
    paste_rot(canvas, rifle, 30, (c[0] - S * 0.01, c[1] + S * 0.01))
    paste_rot(canvas, pistol, -30, (c[0] - S * 0.1, c[1] + S * 0.1))
    # ribbon banner with the name, overlapping the bottom of the medallion
    d = ImageDraw.Draw(canvas)
    y0, y1 = S * 0.74, S * 0.9
    bw = S * 0.41
    tail = S * 0.065
    for side in (-1, 1):   # ribbon tails, darker, folded behind
        x_in, x_out = c[0] + side * (bw - S * 0.02), c[0] + side * (bw + tail)
        pts = [(x_in, y0 + S * 0.035), (x_out, y0 + S * 0.035), (x_out - side * tail * 0.45, (y0 + y1) / 2 + S * 0.035),
               (x_out, y1 + S * 0.035), (x_in, y1 + S * 0.035)]
        d.polygon(pts, fill=(118, 76, 24, 255))
    band = [(c[0] - bw, y0), (c[0] + bw, y0), (c[0] + bw, y1), (c[0] - bw, y1)]
    canvas.paste(vgrad((S, S), BRASS_HI, BRASS_LO).convert("RGBA"), (0, 0), mask_from(band))
    d.line([band[0], band[1]], fill=(255, 240, 190, 255), width=int(S * 0.006))
    d.line([band[3], band[2]], fill=(80, 50, 14, 255), width=int(S * 0.006))
    font = ImageFont.truetype(FONT, int(S * 0.115))
    text = "CALIBRE"
    tb = d.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    tx, ty = c[0] - tw / 2 - tb[0], (y0 + y1) / 2 - th / 2 - tb[1]
    d.text((tx, ty + S * 0.006), text, font=font, fill=(255, 238, 190, 150))
    d.text((tx, ty), text, font=font, fill=(28, 20, 10, 255))
    return canvas


def main():
    icon = make()
    out_mod = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "calibre", "icon.png")
    out_mr = os.path.join(HERE, "modrinth", "icon.png")
    os.makedirs(os.path.dirname(out_mr), exist_ok=True)
    icon.resize((512, 512), Image.LANCZOS).save(out_mr, optimize=True)
    icon.resize((256, 256), Image.LANCZOS).save(out_mod, optimize=True)
    for p in (out_mr, out_mod):
        print(p, os.path.getsize(p) // 1024, "KiB")


if __name__ == "__main__":
    main()
