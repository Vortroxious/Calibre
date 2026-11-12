#!/usr/bin/env python3
"""
Generates every gun / attachment asset of the Calibre mod.

  python3 tools/build_assets.py            # all guns
  python3 tools/build_assets.py glock17    # one gun
  python3 tools/build_assets.py --preview glock17   # + PNG previews in build/preview

Outputs (committed, so the mod builds without Python):
  assets/calibre/geo/item/<gun>.geo.json
  assets/calibre/animations/item/<gun>.animation.json
  assets/calibre/textures/item/<gun>.png
  calibre_gen/guns/<gun>.json          (timings, sound timelines, sockets - read by Java)
"""
import importlib
import json
import os
import pkgutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "common", "src", "main", "resources")  # shared by the neoforge and fabric builds
ASSETS = os.path.join(RES, "assets", "calibre")

from calibre_gen import camera, core, cs2, materials, motion, templates  # noqa: E402
from calibre_gen.common import auto_moving_parts, meta_actions  # noqa: E402
import calibre_gen.guns as guns_pkg  # noqa: E402


def _finished(fn):
    def build():
        return auto_moving_parts(fn())
    return build


def all_guns():
    out = {}
    for info in pkgutil.iter_modules(guns_pkg.__path__):
        if not info.name.startswith("_"):
            mod = importlib.import_module(f"calibre_gen.guns.{info.name}")
            out.update({k: _finished(v) for k, v in getattr(mod, "GUNS", {}).items()})
    return out


def build_gun(name, preview=False):
    asset = all_guns()[name]()
    m = asset.model
    # inspects: a CS2-style presentation generated from the gun's class and parts (cs2.py), on one smooth path,
    # kept clear of the eye
    for i, a in enumerate(asset.anims):
        if a.name == "inspect":
            a = asset.anims[i] = cs2.cs2_inspect(asset)
            for src, dst in m.follow:
                templates.follow_pos([a], src, dst)
            motion.fluid_inspect(asset, a)
            motion.clearance(asset, a, dmin=0.07)   # close-ups: only keep parts out of the near plane
    core.pack_uv(m)
    core.export_geo(m, os.path.join(ASSETS, "geckolib", "models", "item", f"{m.name}.geo.json"))
    tex = materials.paint_texture(m, os.path.join(ASSETS, "textures", "gun", f"{m.name}.png"))
    core.export_anims(m, asset.anims, os.path.join(ASSETS, "geckolib", "animations", "item", f"{m.name}.animation.json"))
    meta = dict(m.meta)
    meta.update(asset.meta)
    meta["id"] = m.name
    meta["bones"] = [b.name for b in m.order]
    meta["actions"] = meta_actions(asset.anims)
    meta["camera"] = camera.camera_meta(asset)       # CS2-style view motion per animation (render only)
    # parts that only exist during an animation (stripper clip, spare round, ejected brass, shells, speedloader):
    # the renderer keeps them hidden whenever no animation explicitly shows them
    idle_anim = next(a for a in asset.anims if a.name == "idle")
    meta["spare_bones"] = sorted(idle_anim.hidden)
    # parts that are not there when the gun is empty (the RPG's rocket): hidden whenever it is, outside reloads
    empty_anim = next((a for a in asset.anims if a.name == "idle_empty"), None)
    if empty_anim is not None:
        meta["empty_hidden"] = sorted(empty_anim.hidden - idle_anim.hidden)
    # model facts for tools/validate.py: part count, overall length (loose projectiles excluded), moving controls
    skip = set(idle_anim.hidden) | {"rocket"}
    meta["model"] = {"cubes": sum(len(b.cubes) for b in m.order), "length_mm": round(float(m.length(skip=skip)), 1),
                     "moving": sorted(m.moves)}
    for s in ("mount_optic", "mount_under", "mount_side", "muzzle"):
        if m.has(s):
            meta.setdefault("sockets", {})[s] = m.socket(s)
    out = os.path.join(RES, "calibre_gen", "guns", f"{m.name}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        json.dump(meta, fh, indent=1)
    if preview:
        make_preview(asset, tex)
    return asset


def make_preview(asset, tex, frames=None):
    from calibre_gen import preview as pv
    m = asset.model
    outdir = os.path.join(ROOT, "build", "preview")
    os.makedirs(outdir, exist_ok=True)
    idle = next(a for a in asset.anims if a.name == "idle")
    rest = idle.pose(0.0)
    hip = asset.meta.get("hip", {})
    sight = m.meta.get("sight", [0, 20, 0])
    ads_d = asset.meta.get("ads", {}).get("dist", 0.2)
    ads = {"pos": [-sight[0] * 0.001, -sight[1] * 0.001, -ads_d - sight[2] * 0.001], "rot": [0, 0, 0]}
    imgs = [
        pv.render(m, rest, tex, "side", title=f"{m.name} side"),
        pv.render(m, rest, tex, "iso", title="iso"),
        pv.render(m, rest, tex, "fp", fp=hip, title="first person (hip)"),
        pv.render(m, rest, tex, "fp", fp=ads, title="first person (ADS)"),
    ]
    pv.sheet(imgs, cols=2).save(os.path.join(outdir, f"{m.name}_views.png"))
    lo, hi = m.bounds()
    span_mm = float(max(hi - lo)) * 2.4
    for a in asset.anims:
        if a.name.startswith("idle"):
            continue
        n = 16 if a.length > 1 else 8
        ts = [a.length * i / (n - 1) for i in range(n)]
        fr = []
        for t in ts:
            p = a.pose(t)
            fr.append(pv.render(m, p, tex, "left", size=(420, 300), title=f"{a.name} t={t:.2f}", fp=hip,
                                frame=(-(lo[2] + hi[2]) / 2, (lo[1] + hi[1]) / 2 - span_mm * 0.05, span_mm / 420)))
            fr.append(pv.render(m, p, tex, "fp", fp=hip, size=(420, 300), title="fp"))
        pv.sheet(fr, cols=4).save(os.path.join(outdir, f"{m.name}_{a.name}.png"))

def build_attachments(preview=False):
    from calibre_gen.attachments import ATTACHMENTS
    from calibre_gen import preview as pv
    imgs = []
    for name, fn in ATTACHMENTS.items():
        m = fn()
        m.name = name
        core.pack_uv(m, density=1.0)
        core.export_geo(m, os.path.join(ASSETS, "geckolib", "models", "attachment", f"{name}.geo.json"))
        tex = materials.paint_texture(m, os.path.join(ASSETS, "textures", "attachment", f"{name}.png"))
        meta = dict(m.meta)
        meta["id"] = name
        out = os.path.join(RES, "calibre_gen", "attachments", f"{name}.json")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as fh:
            json.dump(meta, fh, indent=1)
        if preview:
            imgs.append(pv.render(m, None, tex, "iso", size=(360, 240), title=name))
    if preview:
        outdir = os.path.join(ROOT, "build", "preview")
        os.makedirs(outdir, exist_ok=True)
        pv.sheet(imgs, cols=5).save(os.path.join(outdir, "attachments.png"))
    print(f"built {len(ATTACHMENTS)} attachments")


def main(argv):
    preview = "--preview" in argv
    if "--attachments" in argv:
        build_attachments(preview)
        return
    names = [a for a in argv if not a.startswith("--")] or sorted(all_guns())
    for n in names:
        asset = build_gun(n, preview)
        print(f"built {n}: {len(asset.model.order)} bones, "
              f"{sum(len(b.cubes) for b in asset.model.order)} cubes, tex {asset.model.tex_w}x{asset.model.tex_h}, "
              f"anims {[a.name for a in asset.anims]}")


if __name__ == "__main__":
    main(sys.argv[1:])
