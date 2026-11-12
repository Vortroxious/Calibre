#!/usr/bin/env python3
"""Checks the generated assets: bone contract, animation set, sound references, UVs inside textures, item JSONs."""
import glob
import json
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "common", "src", "main", "resources")  # shared by the neoforge and fabric builds
A = os.path.join(RES, "assets", "calibre")

REQUIRED_BONES = {"root", "gun", "body", "arm_right", "arm_left", "muzzle"}
REQUIRED_ANIMS = {"idle", "draw", "fire", "inspect", "dry"}
MIN_PARTS = 130            # every gun is at least this detailed
LENGTH_TOL = 0.06          # overall length within 6 % of the real gun (tools/rosters/specs.py)

sys.path.insert(0, os.path.join(ROOT, "tools", "rosters"))
from specs import SPECS  # noqa: E402


def main():
    errors = []
    sounds = set(json.load(open(os.path.join(RES, "calibre_gen", "sounds.json"))))
    metas = sorted(glob.glob(os.path.join(RES, "calibre_gen", "guns", "*.json")))
    for mp in metas:
        meta = json.load(open(mp))
        gid = meta["id"]
        bones = set(meta["bones"])
        if not REQUIRED_BONES <= bones:
            errors.append(f"{gid}: missing bones {REQUIRED_BONES - bones}")
        model = meta.get("model")
        if model is None:
            errors.append(f"{gid}: no model facts (rebuild with tools/build_assets.py)")
        else:
            if model["cubes"] < MIN_PARTS:
                errors.append(f"{gid}: only {model['cubes']} parts (minimum {MIN_PARTS})")
            if gid not in SPECS:
                errors.append(f"{gid}: no real dimensions in tools/rosters/specs.py")
            elif abs(model["length_mm"] / SPECS[gid][0] - 1) > LENGTH_TOL:
                errors.append(f"{gid}: {model['length_mm']} mm long, the real one is {SPECS[gid][0]} mm")
            for bn in model["moving"]:
                if bn not in bones:
                    errors.append(f"{gid}: moving part {bn} has no bone")
        acts = set(meta["actions"])
        if not REQUIRED_ANIMS <= acts:
            errors.append(f"{gid}: missing animations {REQUIRED_ANIMS - acts}")
        if not ({"reload", "reload_start"} & acts):
            errors.append(f"{gid}: no reload")
        # CS2-style camera motion: every weapon action has a curve that starts / ends at rest and stays subtle
        cam = meta.get("camera", {})
        for name, act in meta["actions"].items():
            if name.startswith("idle"):
                continue
            c = cam.get(name)
            if c is None:
                errors.append(f"{gid}/{name}: no camera curve")
                continue
            d = c["d"]
            if len(d) % 3 or any(abs(v) > 1e-6 for v in d[:3] + d[-3:]):
                errors.append(f"{gid}/{name}: camera curve does not start/end at rest")
            if max(abs(v) for v in d) > 2.5 + 1e-6:
                errors.append(f"{gid}/{name}: camera curve too strong")
            if abs((len(d) // 3 - 1) / c["rate"] - act["length"]) > 2.0 / c["rate"]:
                errors.append(f"{gid}/{name}: camera curve length {len(d) // 3} != animation {act['length']}s")
        for name, a in meta["actions"].items():
            for _, s in a["sounds"]:
                if s not in sounds:
                    errors.append(f"{gid}/{name}: unknown sound {s}")
        geo = json.load(open(os.path.join(A, "geckolib", "models", "item", f"{gid}.geo.json")))["minecraft:geometry"][0]
        tw, th = geo["description"]["texture_width"], geo["description"]["texture_height"]
        img = Image.open(os.path.join(A, "textures", "gun", f"{gid}.png"))
        if img.size != (tw, th):
            errors.append(f"{gid}: texture {img.size} != geo {tw}x{th}")
        for b in geo["bones"]:
            for c in b.get("cubes", []):
                for f, uv in c["uv"].items():
                    u, v = uv["uv"]
                    w, h = uv["uv_size"]
                    if min(u, u + w) < 0 or max(u, u + w) > tw or min(v, v + h) < 0 or max(v, v + h) > th:
                        errors.append(f"{gid}/{b['name']}: uv out of bounds")
        anims = json.load(open(os.path.join(A, "geckolib", "animations", "item", f"{gid}.animation.json")))["animations"]
        for name in acts:
            if f"animation.{gid}.{name}" not in anims:
                errors.append(f"{gid}: meta action {name} has no animation")
            else:
                for bn in anims[f"animation.{gid}.{name}"]["bones"]:
                    if bn not in bones:
                        errors.append(f"{gid}/{name}: animates unknown bone {bn}")
        for f in (os.path.join(A, "items", f"{gid}.json"), os.path.join(A, "models", "item", f"{gid}.json")):
            if not os.path.exists(f):
                errors.append(f"{gid}: missing {os.path.relpath(f, RES)}")
    sj = json.load(open(os.path.join(A, "sounds.json")))
    for ev, d in sj.items():
        for s in d["sounds"]:
            path = os.path.join(A, "sounds", s["name"].split(":")[1] + ".ogg")
            if not os.path.exists(path):
                errors.append(f"sound {ev}: missing file {path}")
    lang = json.load(open(os.path.join(A, "lang", "en_us.json")))
    for mp in metas:
        gid = os.path.basename(mp)[:-5]
        if f"item.calibre.{gid}" not in lang:
            errors.append(f"lang: missing item.calibre.{gid}")
    print(f"checked {len(metas)} guns, {len(sj)} sound events")
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
