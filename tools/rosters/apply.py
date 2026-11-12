#!/usr/bin/env python3
"""Writes a roster (tools/rosters/expansion2.py, expansion3.py, ...) into the Java and generator sources. Idempotent.
Usage: python3 tools/rosters/apply.py [roster module]   (default: expansion2)"""
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
R = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "expansion2")
CALIBRES, GUNS, LOOT, MERCENARY = R.CALIBRES, R.GUNS, R.LOOT, R.MERCENARY

J = os.path.join(ROOT, "common", "src", "main", "java", "dev", "calibre")
T = os.path.join(ROOT, "tools")
MARK = getattr(R, "MARK", "expansion 2")
TITLE = getattr(R, "TITLE", "modern, WWII, precision and Cold War packs")
G0 = GUNS[0][0]                     # the roster's first gun: "already applied?" probe


def edit(path, fn):
    s = open(path).read()
    n = fn(s)
    if n != s:
        open(path, "w").write(n)
        print("updated", os.path.relpath(path, ROOT))


# --- Caliber enum
def caliber(s):
    if not CALIBRES or CALIBRES[0][0] + "(" in s:
        return s
    lines = [f'    {e}("{i}", "{d}", {dm}f, {v}, {p}, {pen}f, {ap}f, {tr})' for e, i, d, dm, v, p, pen, ap, tr, _, _ in CALIBRES]
    last = list(re.finditer(r"^    [A-Z0-9_]+\(.*\);$", s, flags=re.M))[-1]      # the enum's last constant
    return s[:last.end() - 1] + ",\n" + ",\n".join(lines) + ";" + s[last.end():]


edit(os.path.join(J, "gun", "Caliber.java"), caliber)


# --- Guns.java
def guns(s):
    if f"// ---- {MARK}" in s:
        return s
    out = [f"\n    // ---- {MARK}: {TITLE} " + "-" * max(4, 90 - len(MARK) - len(TITLE))]
    for gid, name, pack, tail, *_ in GUNS:
        const = gid.upper()
        out.append(f'    public static final GunDefinition {const} = add(builder("{gid}", {tail}.build());')
    return s.replace("\n    private Guns() {}", "\n".join(out) + "\n\n    private Guns() {}", 1)


edit(os.path.join(J, "gun", "Guns.java"), guns)

# --- recipes
KIT = {
    "polymer": "in(Items.IRON_INGOT, 10), in(Items.BLACK_DYE, 5), in(Items.COPPER_INGOT, 4), trig",
    "pistol": "in(Items.IRON_INGOT, 5), in(Items.BLACK_DYE, 2), in(Items.COPPER_INGOT, 2), pistol",
    "shotgun": "in(Items.IRON_INGOT, 14), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 4), trig",
    "rifle_wood": "in(Items.IRON_INGOT, 14), in(Items.OAK_PLANKS, 8), in(Items.COPPER_INGOT, 4), rifle",
    "smg": "in(Items.IRON_INGOT, 12), in(Items.COPPER_INGOT, 3), trig",
    "lmg": "in(Items.IRON_INGOT, 28), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 10), in(Items.REDSTONE, 10)",
    "sniper": "in(Items.IRON_INGOT, 20), in(Items.GRAY_DYE, 4), in(Items.GLASS, 3), sniper, rifle",
    "rifle": "in(Items.IRON_INGOT, 16), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 6), rifle",
}


def recipes(s):
    if f"// {MARK}" in s:
        return s
    g = [f"        // {MARK}"] + [f'        gun("{gid}", {KIT[r[-1]]});' for gid, *_, r in [(x[0], x) for x in GUNS] for r in [r]]
    a = [f"        ammo(Caliber.{e}, {c[0]}, in(Items.COPPER_INGOT, {c[1]}), in(Items.GUNPOWDER, {c[2]}), in(Items.IRON_NUGGET, {c[3]}));"
         if pel == 1 else
         f"        ammo(Caliber.{e}, {c[0]}, in(Items.PAPER, 2), in(Items.GUNPOWDER, {c[2]}), in(Items.IRON_NUGGET, {c[3] + 4}), in(Items.COPPER_INGOT, {c[1]}));"
         for e, _i, _d, _dm, _v, pel, *_, c in CALIBRES]
    s = s.replace("\n        // ammo: brass (copper) case", "\n" + "\n".join(g) + "\n\n        // ammo: brass (copper) case", 1)
    return s.replace("\n        ammo(Caliber.PG7,", "\n" + "\n".join(a) + "\n        ammo(Caliber.PG7,", 1)


edit(os.path.join(J, "workbench", "GunsmithingRecipes.java"), recipes)


# --- mercenaries
def merc(s):
    if f'"{MERCENARY[0]}"' in s:
        return s
    extra = ", ".join(f'"{g}"' for g in MERCENARY)
    return re.sub(r'("ppq", "m45"[^)]*)\);', lambda mm: mm.group(1) + ", " + extra + ");", s, count=1)


edit(os.path.join(J, "entity", "MercenaryEntity.java"), merc)


def _into_dict(s, key_line, text):
    """Append `text` at the end of the dict literal that contains key_line (before its closing brace line)."""
    end = s.index("\n}", s.index(key_line)) + 1
    return s[:end] + text + s[end:]


# --- gen_data: names, ammo, loot
def gen_data(s):
    if f'"{G0}":' not in s:
        names = "".join(f'    "{gid}": "{name}",\n' for gid, name, *_ in GUNS)
        s = _into_dict(s, '    "singlesix": "Ruger Single-Six",\n', "    # " + MARK + "\n" + names)
    if CALIBRES and f'"{CALIBRES[0][1]}":' not in s:
        ammo = "".join(f'    "{i}": ("{d}", {ic[0]}, {ic[1]}, {ic[2]}, {ic[3]}),\n' for e, i, d, *_, ic, c in CALIBRES)
        s = _into_dict(s, '    "16buck": ("16 Gauge Buckshot"', ammo)
    for key, var in (("common", "guns_common"), ("civ", "guns_civ"), ("ww2", "guns_ww2"), ("mil", "guns_mil"), ("rare", "guns_rare")):
        add = [g for g in LOOT[key] if f'"{g}"' not in s.split(f"{var} = [")[1].split("]")[0]]
        if add:
            s = re.sub(rf'({var} = \[[^\]]*)\]', lambda mm: mm.group(1) + ", " + ", ".join(f'"{g}"' for g in add) + "]", s, count=1)
    return s


edit(os.path.join(T, "gen_data.py"), gen_data)


# --- synthesized gunshot fallbacks
def gen_sounds(s):
    if f'"{G0}":' in s:
        return s
    lines = "".join(f'    "{gid}": {syn},\n' for gid, _, _, _, _, _, syn, _ in GUNS)
    return _into_dict(s, '"singlesix": (0.38, 0.2, 155, 0.45),\n', "    # " + MARK + "\n" + lines)


edit(os.path.join(T, "gen_sounds.py"), gen_sounds)

# --- real gunshots: reuse the cuts of the gun recorded with the same rifle/pistol, pitched
SRC = {"1911": "fire_m1911", "AR-15": "fire_m4a1", "Walther PPQ": "fire_ppq", "Nova": "fire_nova", "Model 12": "fire_model12",
       "Arisaka": "fire_arisaka", "1917": "fire_m1917", "Carl Gustav M45": "fire_m45", "AK-47": "fire_ak47",
       "PPSh": "fire_ppsh41", "Tikka": "fire_tikka_t3", "Savage 10 .300 Blackout": "fire_savage10",
       "Mosin Nagant": "fire_mosin", "Smith & Wesson 642": "fire_sw642", "Bersa": "fire_bersa"}
smp = os.path.join(T, "sound_map.json")
sm = json.load(open(smp))
changed = False
for gid, _, _, _, _, (src, semis, cls), _, _ in GUNS:
    ev = f"fire_{gid}"
    if ev in sm:
        continue
    base = sm[SRC.get(src, src)]
    clips = []
    for c in base:
        c = dict(c)
        p = c.get("pitch", 0)
        c["pitch"] = [round(x + semis, 2) for x in p] if isinstance(p, list) else round(p + semis, 2)
        clips.append(c)
    sm[ev] = clips
    sm["_gun_class"][ev] = cls
    changed = True
if changed:
    json.dump(sm, open(smp, "w"), indent=1)
    print("updated tools/sound_map.json")


# --- inspect styles
def kinds(s):
    if f'"{G0}"' in s:
        return s
    for k in ("pistol", "revolver", "rifle", "shotgun", "lever", "bolt", "heavy"):
        add = [g for g, *_, kind, _s, _y, _r in [(x[0], x[4], x[5], x[6], x[7]) for x in GUNS] if kind == k]
        if not add:
            continue
        s = re.sub(rf'(    "{k}": \[[^\]]*)\]', lambda mm: mm.group(1) + ", " + ", ".join(f'"{g}"' for g in add) + "]", s, count=1)
    return s


edit(os.path.join(T, "calibre_gen", "motion.py"), kinds)
print("done")
