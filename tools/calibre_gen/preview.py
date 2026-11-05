"""Tiny software renderer replicating GeckoLib's bone math, for visual QA of generated assets."""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .core import Model, bone_local_matrix, cube_matrix, euler_mat, affine, T

# Arm proxy, in arm-bone local space (mm). Must match ArmsRenderLayer in Java.
ARM_BOX = (-40.0, 40.0, -40.0, 40.0, -45.0, 520.0)

FACE_IDX = {
    "north": (0, 2, 6, 4), "south": (1, 5, 7, 3),
    "west": (0, 1, 3, 2), "east": (4, 6, 7, 5),
    "down": (0, 4, 5, 1), "up": (2, 3, 7, 6),
}
LIGHT = np.array([0.35, 0.8, 0.5])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def _cube_verts(x0, y0, z0, x1, y1, z1):
    return np.array([[x, y, z, 1.0] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)])


def _avg_color(tex, uv):
    u, v, w, h = uv
    if tex is None:
        return np.array([120, 120, 120])
    patch = tex[v:v + h, u:u + w, :3]
    return patch.reshape(-1, 3).mean(axis=0)


def collect_quads(model: Model, pose=None, tex=None, arms=True, extra=None):
    """Return list of (world_pts[4,3], color)."""
    quads = []
    mats = {}
    hands = {}
    for b in model.order:
        pm = mats[b.parent.name] if b.parent else np.eye(4)
        anim = pose.get(b.name) if pose else None
        m = pm @ bone_local_matrix(b, anim)
        mats[b.name] = m
        if anim is not None and np.allclose(anim[2], 0):
            mats[b.name] = m  # children of hidden bones are hidden too (scale 0 collapses them)
        for c in b.cubes:
            cm = m @ cube_matrix(c)
            v = (cm @ _cube_verts(c.x0, c.y0, c.z0, c.x1, c.y1, c.z1).T).T[:, :3]
            for f, idx in FACE_IDX.items():
                col = _avg_color(tex, c.uv[f]) if c.uv else np.array([128, 128, 128])
                quads.append((v[list(idx)], col))
        if b.name in ("arm_right", "arm_left"):
            hands[b.name] = m @ T(np.asarray(b.pivot))
    if extra:
        quads.extend(extra)
    return quads, hands


# Shoulder anchors in view space (metres). Must match ArmsRenderLayer in Java.
SHOULDERS = {"arm_right": np.array([0.22, -0.55, 0.02]), "arm_left": np.array([-0.2, -0.55, 0.02])}
ARM_W = 60.0        # mm
ARM_FIST = 40.0     # how far the arm box extends beyond the hand pivot
ARM_LEN = 330.0


def arm_quads(hand_m, shoulder_model, side):
    """Arm box from the hand pivot towards the shoulder (both in model space, mm)."""
    hand = hand_m[:3, 3]
    d = shoulder_model - hand
    ln = np.linalg.norm(d)
    if ln < 1e-6:
        return []
    fwd = d / ln
    up = hand_m[:3, :3] @ np.array([0, 1, 0.0])
    side_v = np.cross(up, fwd)
    if np.linalg.norm(side_v) < 1e-6:
        side_v = np.array([1.0, 0, 0])
    side_v /= np.linalg.norm(side_v)
    up = np.cross(fwd, side_v)
    h = ARM_W / 2
    pts = []
    for a in (-ARM_FIST, max(ARM_LEN - ARM_FIST, ln)):
        for sx in (-h, h):
            for sy in (-h, h):
                pts.append(hand + fwd * a + side_v * sx + up * sy)
    pts = np.array(pts)
    col = np.array([196, 150, 120]) if side == "arm_right" else np.array([186, 140, 112])
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return [(pts[list(f)], col) for f in faces]


def clip_near(poly, zn):
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ina, inb = a[2] <= zn, b[2] <= zn
        if ina:
            out.append(a)
        if ina != inb:
            t = (zn - a[2]) / (b[2] - a[2])
            out.append(a + (b - a) * t)
    return np.array(out) if len(out) >= 3 else None


def _shade(pts, col):
    n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
    ln = np.linalg.norm(n)
    if ln < 1e-9:
        return None
    n = n / ln
    k = 0.45 + 0.55 * abs(float(n @ LIGHT))
    return tuple(int(min(255, c * k)) for c in col)


def render(model, pose=None, tex=None, view="side", size=(900, 420), fp=None, arms=True, title=None, bg=(32, 34, 40),
           frame=None):
    W, H = size
    ss = 2
    img = Image.new("RGB", (W * ss, H * ss), bg)
    dr = ImageDraw.Draw(img)
    quads, hands = collect_quads(model, pose, tex)
    cfg = fp or {}
    rot = euler_mat(cfg.get("rot", (0, 0, 0)))
    pos = np.asarray(cfg.get("pos", (0.12, -0.12, -0.3)))
    if arms and (view == "fp" or frame is not None):
        for side, hm in hands.items():
            # shoulder (view space, m) -> model space (mm)
            sh = rot.T @ (SHOULDERS[side] - pos) * 1000.0
            quads.extend(arm_quads(hm, sh, side))
    if view == "fp":
        fov = math.radians(cfg.get("fov", 70.0))
        f = (H * ss / 2) / math.tan(fov / 2)
        proj = []
        for pts, col in quads:
            vp = (rot @ (pts.T * 0.001)).T + pos
            if np.any(vp[:, 2] > -0.02):
                vp = clip_near(vp, -0.02)
                if vp is None:
                    continue
            sx = W * ss / 2 + f * vp[:, 0] / -vp[:, 2]
            sy = H * ss / 2 - f * vp[:, 1] / -vp[:, 2]
            proj.append((float(-vp[:, 2].mean()), list(zip(sx, sy)), _shade(pts, col)))
        proj.sort(key=lambda p: -p[0])
    else:
        side = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]], dtype=float)
        if view == "side":
            R = side
        elif view == "iso":
            a = math.radians(-22)
            tilt = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
            R = tilt @ side @ euler_mat((0, 28, 0))
        elif view == "top":
            R = np.array([[0, 0, 1], [-1, 0, 0], [0, 1, 0]], dtype=float)
        elif view == "left":
            R = np.array([[0, 0, -1], [0, 1, 0], [-1, 0, 0]], dtype=float)
        elif view == "front":
            R = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]], dtype=float)
        else:
            raise ValueError(view)
        if frame is not None:
            cx, cy, span = frame
            sc = ss / span
        else:
            allp = np.concatenate([q[0] for q in quads]) if quads else np.zeros((1, 3))
            tp = (R @ allp.T).T
            lo, hi = tp.min(axis=0), tp.max(axis=0)
            span = max((hi[0] - lo[0]) / (W * 0.9), (hi[1] - lo[1]) / (H * 0.8), 1e-6)
            sc = ss / span
            cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
        proj = []
        for pts, col in quads:
            p = (R @ pts.T).T
            sx = W * ss / 2 + (p[:, 0] - cx) * sc
            sy = H * ss / 2 - (p[:, 1] - cy) * sc
            proj.append((float(p[:, 2].mean()), list(zip(sx, sy)), _shade(pts, col)))
        proj.sort(key=lambda p: p[0])
    for depth, pts, col in proj:
        if col is None:
            continue
        dr.polygon(pts, fill=col, outline=tuple(max(0, c - 25) for c in col))
    img = img.resize((W, H), Image.LANCZOS)
    if title:
        d2 = ImageDraw.Draw(img)
        d2.text((8, 6), title, fill=(230, 230, 230))
    if view == "fp":
        d2 = ImageDraw.Draw(img)
        d2.line([(W / 2 - 6, H / 2), (W / 2 + 6, H / 2)], fill=(255, 255, 255))
        d2.line([(W / 2, H / 2 - 6), (W / 2, H / 2 + 6)], fill=(255, 255, 255))
    return img


def sheet(images, cols=4):
    w, h = images[0].size
    rows = math.ceil(len(images) / cols)
    out = Image.new("RGB", (w * cols, h * rows), (20, 20, 20))
    for i, im in enumerate(images):
        out.paste(im, ((i % cols) * w, (i // cols) * h))
    return out
