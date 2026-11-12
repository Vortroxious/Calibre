#!/usr/bin/env python3
"""
Generates the remaining resources of Calibre: item model definitions + display transforms, lang, damage types & tags,
loot modifiers, biome modifier, workbench block assets & recipe, procedural textures (ammo icons, mercenary skin,
scope reticles, muzzle flash, tracer), the rocket entity model and the GameTest structure.

  python3 tools/gen_data.py
"""
import gzip
import io
import json
import math
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "common", "src", "main", "resources")  # shared by the neoforge and fabric builds
NEO_RES = os.path.join(ROOT, "neoforge", "src", "main", "resources")  # NeoForge-only data (loot modifiers, biome modifier)
A = os.path.join(RES, "assets", "calibre")
D = os.path.join(RES, "data", "calibre")

from calibre_gen import core, materials  # noqa: E402

GUN_NAMES = {
    "glock17": "Glock 17", "m1911": "M1911A1", "m9": "Beretta M9", "deagle": "Desert Eagle .50",
    "model29": "S&W Model 29", "mp5": "H&K MP5A3", "ump45": "H&K UMP45", "uzi": "IMI Uzi", "p90": "FN P90",
    "m4a1": "Colt M4A1", "hk416": "H&K HK416", "akm": "AKM", "aug": "Steyr AUG A3", "fal": "FN FAL",
    "scar_h": "FN SCAR-H", "svd": "SVD Dragunov", "m14ebr": "M14 EBR", "m24": "M24 SWS", "awm": "AI AWM",
    "m82a1": "Barrett M82A1", "rem870": "Remington 870", "benelli_m4": "Benelli M4", "m249": "FN M249 SAW",
    "pkm": "PKM", "rpg7": "RPG-7",
    # expansion
    "mosin": "Mosin-Nagant M91/30", "m1917": "M1917 Enfield", "arisaka": "Arisaka Type 99", "sks": "SKS",
    "ppsh41": "PPSh-41", "m45": "Carl Gustaf m/45", "ak47": "AK-47 (Type 3)", "win1894": "Winchester Model 1894",
    "marlin336": "Marlin 336", "tikka_t3": "Tikka T3", "savage10": "Savage Model 10", "model12": "Winchester Model 12",
    "nova": "Benelli Nova", "cdaly": "Charles Daly 300 Field", "mossberg190": "Mossberg 190", "ppq": "Walther PPQ",
    "bersa": "Bersa Thunder 380", "rugermk3": "Ruger Mark III", "sw642": "S&W 642 Airweight",
    "singlesix": "Ruger Single-Six",
    # expansion 2
    "vector": "Kriss Vector .45",
    "mp7": "H&K MP7A1",
    "g36c": "H&K G36C",
    "famas": "FAMAS F1",
    "x95": "IWI Tavor X95",
    "fiveseven": "FN Five-seveN",
    "usp": "H&K USP .45",
    "cz75": "CZ 75 SP-01",
    "spas12": "Franchi SPAS-12",
    "aa12": "Atchisson AA-12",
    "kar98k": "Mauser Kar98k",
    "garand": "M1 Garand",
    "enfield": "Lee-Enfield No.4 Mk I",
    "thompson": "Thompson M1A1",
    "mp40": "MP 40",
    "stg44": "StG 44",
    "mg42": "MG 42",
    "bar": "M1918 BAR",
    "intervention": "CheyTac M200 Intervention",
    "l96": "Accuracy International L96A1",
    "rem700": "Remington 700",
    "sr25": "KAC SR-25",
    "svu": "SVU",
    "dsr1": "DSR-Precision DSR-1",
    "m60": "M60",
    "m16a1": "M16A1",
    "galil": "IMI Galil ARM",
    "g3a3": "H&K G3A3",
    "sten": "Sten Mk II",
    "python": "Colt Python",
    "skorpion": "Skorpion vz. 61",
    "ks23": "KS-23",
    # expansion 3
    "ak74m": "AK-74M",
    "aks74u": "AKS-74U",
    "ak12": "AK-12",
    "mcx": "SIG MCX",
    "l85a2": "L85A2",
    "qbz95": "QBZ-95",
    "f2000": "FN F2000",
    "hk417": "H&K HK417",
    "m1carbine": "M1 Carbine",
    "svt40": "SVT-40",
    "g43": "Gewehr 43",
    "fg42": "FG 42",
    "m3grease": "M3 Grease Gun",
    "pps43": "PPS-43",
    "luger": "Luger P08",
    "p38": "Walther P38",
    "rpk": "RPK",
    "rpd": "RPD",
    "m240b": "M240B",
    "dp28": "DP-28",
    "mg34": "MG 34",
    "bren": "Bren Mk II",
    "p226": "SIG Sauer P226",
    "makarov": "Makarov PM",
    "c96": "Mauser C96",
    "saa": "Colt Single Action Army",
    "mac10": "Ingram MAC-10",
    "vss": "VSS Vintorez",
    "ksg": "Kel-Tec KSG",
    "doublebarrel": "Double-Barrel Shotgun",
}
AMMO = {
    "9mm": ("9×19mm Parabellum", (196, 152, 62), (178, 102, 58), 6, 0.45),
    "45acp": (".45 ACP", (196, 152, 62), (120, 120, 126), 7, 0.45),
    "50ae": (".50 Action Express", (205, 165, 70), (178, 102, 58), 8, 0.55),
    "44mag": (".44 Magnum", (196, 152, 62), (120, 120, 126), 7, 0.6),
    "57x28": ("5.7×28mm", (196, 152, 62), (60, 60, 70), 4, 0.65),
    "556": ("5.56×45mm NATO", (196, 152, 62), (178, 102, 58), 4, 0.85),
    "762x39": ("7.62×39mm", (120, 110, 70), (178, 102, 58), 5, 0.8),
    "762": ("7.62×51mm NATO", (196, 152, 62), (178, 102, 58), 5, 0.95),
    "762x54": ("7.62×54mmR", (120, 110, 70), (178, 102, 58), 5, 1.0),
    "300wm": (".300 Win Mag", (205, 165, 70), (178, 102, 58), 5, 1.05),
    "50bmg": (".50 BMG", (205, 165, 70), (60, 60, 60), 7, 1.1),
    "12buck": ("12 Gauge 00 Buck", (150, 28, 26), (205, 165, 70), 8, 0.7),
    "12slug": ("12 Gauge Slug", (44, 98, 50), (205, 165, 70), 8, 0.7),
    "pg7": ("PG-7V Rocket", (70, 80, 52), (96, 100, 90), 9, 1.15),
    "762x25": ("7.62×25mm Tokarev", (120, 110, 70), (178, 102, 58), 5, 0.5),
    "3006": (".30-06 Springfield", (196, 152, 62), (178, 102, 58), 5, 1.0),
    "77x58": ("7.7×58mm Arisaka", (196, 152, 62), (178, 102, 58), 5, 0.95),
    "3030": (".30-30 Winchester", (205, 165, 70), (120, 120, 126), 5, 0.8),
    "38spl": (".38 Special", (196, 152, 62), (120, 120, 126), 6, 0.5),
    "22lr": (".22 Long Rifle", (205, 165, 70), (120, 120, 126), 3, 0.35),
    "380acp": (".380 ACP", (196, 152, 62), (178, 102, 58), 5, 0.38),
    "300blk": (".300 AAC Blackout", (196, 152, 62), (60, 60, 70), 5, 0.75),
    "16buck": ("16 Gauge Buckshot", (200, 170, 40), (205, 165, 70), 7, 0.68),
    "46x30": ("4.6×30mm", (196, 152, 62), (60, 60, 70), 4, 0.55),
    "792x57": ("7.92×57mm Mauser", (120, 110, 70), (178, 102, 58), 5, 1.0),
    "792x33": ("7.92×33mm Kurz", (120, 110, 70), (178, 102, 58), 5, 0.75),
    "303": (".303 British", (196, 152, 62), (178, 102, 58), 5, 1.0),
    "408": (".408 CheyTac", (205, 165, 70), (60, 60, 60), 6, 1.1),
    "338lm": (".338 Lapua Magnum", (205, 165, 70), (178, 102, 58), 6, 1.08),
    "357mag": (".357 Magnum", (196, 152, 62), (120, 120, 126), 6, 0.55),
    "32acp": (".32 ACP", (196, 152, 62), (178, 102, 58), 4, 0.34),
    "23mm": ("23×75mmR Buckshot", (60, 70, 60), (205, 165, 70), 9, 0.8),
    "545x39": ("5.45×39mm", (120, 110, 70), (178, 102, 58), 5, 0.72),
    "58x42": ("5.8×42mm", (120, 110, 70), (178, 102, 58), 5, 0.74),
    "30carbine": (".30 Carbine", (196, 152, 62), (178, 102, 58), 5, 0.6),
    "9x18": ("9×18mm Makarov", (120, 110, 70), (178, 102, 58), 4, 0.4),
    "763x25": ("7.63×25mm Mauser", (196, 152, 62), (178, 102, 58), 4, 0.5),
    "45colt": (".45 Colt", (196, 152, 62), (120, 120, 126), 6, 0.56),
    "9x39": ("9×39mm", (120, 110, 70), (60, 60, 70), 5, 0.8),
}
ATT_NAMES = {
    "red_dot": "Red Dot Sight", "holo": "Holographic Sight", "acog": "ACOG 4× Scope", "scope_8x": "8× Rifle Scope",
    "pso1": "PSO-1 4× Scope", "suppressor_pistol": "Pistol Suppressor", "suppressor_rifle": "Rifle Suppressor",
    "compensator": "Compensator", "flash_hider": "Flash Hider", "vertical_grip": "Vertical Foregrip",
    "angled_grip": "Angled Foregrip", "bipod_att": "Bipod", "laser": "Laser Sight", "extended_mag": "Extended Magazine",
}


def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


# ------------------------------------------------------------------------------------------------ item models
def geo_bounds(path):
    with open(path) as fh:
        g = json.load(fh)["minecraft:geometry"][0]
    lo = np.array([1e9] * 3)
    hi = -lo
    for b in g["bones"]:
        for c in b.get("cubes", []):
            o = np.array(c["origin"], dtype=float)
            s = np.array(c["size"], dtype=float)
            x0, x1 = -(o[0] + s[0]), -o[0]
            lo = np.minimum(lo, [x0, o[1], o[2]])
            hi = np.maximum(hi, [x1, o[1] + s[1], o[2] + s[2]])
    return lo * 10, hi * 10  # cm -> mm


def rot_y(a):
    a = math.radians(a)
    return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])


def rot_x(a):
    a = math.radians(a)
    return np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])


def display_for(lo_mm, hi_mm):
    """Display transforms for a GeckoLib item rendered at 1 mm = 0.001 block."""
    c = (lo_mm + hi_mm) / 2 * 0.001
    size = (hi_mm - lo_mm) * 0.001
    out = {}

    def fit(rot_deg, target, maxscale=4.0):
        R = rot_x(rot_deg[0]) @ rot_y(rot_deg[1])
        ext = np.abs(R) @ size
        s = min(maxscale, target / max(ext[0], ext[1], 1e-3))
        t = -(R @ (c * s)) * 16
        return {"rotation": list(rot_deg), "translation": [round(float(v), 3) for v in t], "scale": [round(s, 4)] * 3}

    out["gui"] = fit([0, -90, 0], 0.95)
    out["fixed"] = fit([0, -90, 0], 0.9)
    out["ground"] = fit([0, -90, 0], 0.5)
    # held: the model origin is the firing grip, keep it in the hand; guns are real size (scale 1)
    # seat the pistol grip in the fist: bore ~5 cm above the hand, grip centre ~3 cm behind the origin.
    # Guns are drawn 1.5x real size in third person so they read next to Minecraft's chunky arms.
    out["thirdperson_righthand"] = {"rotation": [0, 0, 0], "translation": [0, 1.4, -1.0], "scale": [1.5, 1.5, 1.5]}
    out["thirdperson_lefthand"] = {"rotation": [0, 0, 0], "translation": [0, 1.4, -1.0], "scale": [1.5, 1.5, 1.5]}
    out["firstperson_righthand"] = {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]}
    out["firstperson_lefthand"] = {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]}
    out["head"] = fit([0, -90, 0], 0.6)
    return out


def item_models():
    for gid in GUN_NAMES:
        lo, hi = geo_bounds(os.path.join(A, "geckolib", "models", "item", f"{gid}.geo.json"))
        w(os.path.join(A, "items", f"{gid}.json"), {"model": {"type": "minecraft:special", "base": f"calibre:item/{gid}",
                                                             "model": {"type": "geckolib:geckolib"}}})
        w(os.path.join(A, "models", "item", f"{gid}.json"), {"textures": {"particle": "minecraft:block/iron_block"},
                                                             "gui_light": "front", "display": display_for(lo, hi)})
    for aid in ATT_NAMES:
        if aid == "extended_mag":
            continue
        lo, hi = geo_bounds(os.path.join(A, "geckolib", "models", "attachment", f"{aid}.geo.json"))
        disp = display_for(lo, hi)
        disp["thirdperson_righthand"] = {"rotation": [0, -90, 0], "translation": [0, 2, 0], "scale": [0.6] * 3}
        disp["firstperson_righthand"] = {"rotation": [0, -90, 20], "translation": [2, 3, 0], "scale": [0.9] * 3}
        w(os.path.join(A, "items", f"{aid}.json"), {"model": {"type": "minecraft:special", "base": f"calibre:item/{aid}",
                                                             "model": {"type": "geckolib:geckolib"}}})
        w(os.path.join(A, "models", "item", f"{aid}.json"), {"textures": {"particle": "minecraft:block/iron_block"},
                                                             "gui_light": "front", "display": disp})
        w(os.path.join(A, "geckolib", "animations", "attachment", f"{aid}.animation.json"),
          {"format_version": "1.8.0", "animations": {}})
    # extended mag + ammo: flat sprites
    flat = [f"ammo_{k}" for k in AMMO] + ["extended_mag"]
    for iid in flat:
        w(os.path.join(A, "items", f"{iid}.json"), {"model": {"type": "minecraft:model", "model": f"calibre:item/{iid}"}})
        w(os.path.join(A, "models", "item", f"{iid}.json"), {"parent": "minecraft:item/generated",
                                                            "textures": {"layer0": f"calibre:item/{iid}"}})
    w(os.path.join(A, "items", "gun_workbench.json"), {"model": {"type": "minecraft:model", "model": "calibre:block/gun_workbench"}})


# ------------------------------------------------------------------------------------------------ textures
def ammo_icons():
    for k, (_, case, tip, width, length) in AMMO.items():
        img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        if k.startswith("12") or k.startswith("16"):
            for i, x in enumerate((2, 7)):
                d.rectangle([x, 3 + i, x + 5, 12 + i], fill=case + (255,))
                d.rectangle([x, 10 + i, x + 5, 13 + i], fill=tip + (255,))
                d.line([x + 1, 4 + i, x + 1, 9 + i], fill=tuple(min(255, c + 50) for c in case) + (255,))
        elif k == "pg7":
            d.polygon([(8, 0), (12, 5), (12, 9), (4, 9), (4, 5)], fill=case + (255,))
            d.rectangle([6, 9, 10, 15], fill=tip + (255,))
            d.line([5, 5, 5, 8], fill=(110, 120, 90, 255))
        else:
            n = 3 if width <= 5 else 2
            for i in range(n):
                x = 2 + i * (12 // n)
                h = int(12 * length)
                y0 = 15 - h
                cw = max(2, width // 2)
                d.rectangle([x, y0 + h // 3, x + cw, 15], fill=case + (255,))
                d.polygon([(x, y0 + h // 3), (x + cw, y0 + h // 3), (x + cw // 2 + 0.5, y0)], fill=tip + (255,))
                d.line([x, y0 + h // 3 + 1, x, 14], fill=tuple(min(255, c + 45) for c in case) + (255,))
        img.save(os.path.join(A, "textures", "item", f"ammo_{k}.png"))
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(5, 1), (11, 1), (12, 14), (4, 14)], fill=(48, 48, 52, 255))
    d.rectangle([3, 13, 13, 15], fill=(30, 30, 30, 255))
    d.line([6, 2, 6, 12], fill=(80, 80, 86, 255))
    d.rectangle([6, 0, 10, 1], fill=(196, 152, 62, 255))
    img.save(os.path.join(A, "textures", "item", "extended_mag.png"))


def effects():
    os.makedirs(os.path.join(A, "textures", "effect"), exist_ok=True)
    os.makedirs(os.path.join(A, "textures", "entity"), exist_ok=True)
    # star flash
    n = 64
    yy, xx = np.mgrid[0:n, 0:n] - (n - 1) / 2
    r = np.sqrt(xx ** 2 + yy ** 2) / (n / 2)
    ang = np.arctan2(yy, xx)
    star = np.clip(1 - r / (0.35 + 0.65 * np.abs(np.cos(ang * 2.5)) ** 6), 0, 1)
    core_ = np.clip(1 - r / 0.35, 0, 1)
    a = np.clip(star * 0.9 + core_, 0, 1)
    rgb = np.stack([np.full_like(a, 255), 200 + 55 * core_, 90 + 160 * core_], -1)
    Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), "RGBA").save(os.path.join(A, "textures", "effect", "muzzle_flash.png"))
    # side cone
    h, wdt = 32, 64
    yy, xx = np.mgrid[0:h, 0:wdt]
    u = xx / (wdt - 1)
    v = np.abs(yy - (h - 1) / 2) / (h / 2)
    width = 0.25 + 0.75 * np.sin(np.pi * np.clip(u * 1.1, 0, 1)) * (1 - u * 0.4)
    a = np.clip(1 - v / width, 0, 1) * (1 - u) ** 0.7
    rng = np.random.default_rng(3)
    a *= 0.75 + 0.25 * rng.random(a.shape)
    rgb = np.stack([np.full_like(a, 255), 160 + 90 * (1 - u), 60 + 120 * (1 - u) * (1 - v)], -1)
    Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), "RGBA").save(os.path.join(A, "textures", "effect", "muzzle_flash_side.png"))
    # tracer
    t = Image.new("RGBA", (32, 8), (255, 255, 255, 255))
    t.save(os.path.join(A, "textures", "entity", "tracer.png"))


def scopes():
    os.makedirs(os.path.join(A, "textures", "gui"), exist_ok=True)
    n = 512
    for name in ("mildot", "pso1", "acog", "dot", "holo"):
        img = Image.new("RGBA", (n, n), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        d.ellipse([18, 18, n - 18, n - 18], fill=(0, 0, 0, 0))
        c = n // 2
        k = (0, 0, 0, 235)
        if name == "mildot":
            d.line([30, c, c - 40, c], fill=k, width=5)
            d.line([c + 40, c, n - 30, c], fill=k, width=5)
            d.line([c, 30, c, c - 40], fill=k, width=5)
            d.line([c, c + 40, c, n - 30], fill=k, width=5)
            d.line([c - 40, c, c + 40, c], fill=k, width=1)
            d.line([c, c - 40, c, c + 40], fill=k, width=1)
            for i in range(1, 5):
                for sgn in (-1, 1):
                    d.ellipse([c + sgn * i * 24 - 3, c - 3, c + sgn * i * 24 + 3, c + 3], fill=k)
                    d.ellipse([c - 3, c + sgn * i * 24 - 3, c + 3, c + sgn * i * 24 + 3], fill=k)
        elif name == "pso1":
            d.polygon([(c, c), (c - 7, c + 14), (c + 7, c + 14)], fill=k)
            for i in (1, 2, 3):
                y = c + 22 + i * 22
                d.polygon([(c, y), (c - 6, y + 12), (c + 6, y + 12)], fill=k)
            d.line([c - 120, c, c - 20, c], fill=k, width=2)
            d.line([c + 20, c, c + 120, c], fill=k, width=2)
            for i in range(-5, 6):
                d.line([c + i * 20, c - 4, c + i * 20, c + 4], fill=k, width=2)
            # rangefinder curve
            pts = [(c - 140 + x, c + 90 - int(30 * math.exp(-x / 60.0))) for x in range(0, 100, 4)]
            d.line(pts, fill=k, width=2)
        elif name == "acog":
            d.polygon([(c, c - 2), (c - 22, c + 26), (c - 14, c + 26), (c, c + 8), (c + 14, c + 26), (c + 22, c + 26)], fill=(220, 40, 30, 240))
            d.line([c, c + 30, c, n - 40], fill=k, width=3)
            for i in range(1, 6):
                y = c + 30 + i * 26
                d.line([c - 16 + i * 2, y, c + 16 - i * 2, y], fill=k, width=2)
        elif name == "dot":
            d.ellipse([c - 4, c - 4, c + 4, c + 4], fill=(255, 30, 30, 255))
        else:
            d.ellipse([c - 60, c - 60, c + 60, c + 60], outline=(255, 40, 30, 230), width=3)
            d.ellipse([c - 4, c - 4, c + 4, c + 4], fill=(255, 40, 30, 255))
        # vignette edge
        arr = np.array(img).astype(float)
        yy, xx = np.mgrid[0:n, 0:n] - (n - 1) / 2
        r = np.sqrt(xx ** 2 + yy ** 2) / (n / 2 - 18)
        vig = np.clip((r - 0.8) / 0.2, 0, 1)
        arr[..., 3] = np.maximum(arr[..., 3], vig * 255)
        Image.fromarray(arr.astype(np.uint8), "RGBA").save(os.path.join(A, "textures", "gui", f"scope_{name}.png"))


def mercenary_skin():
    rng = np.random.default_rng(11)
    img = np.zeros((64, 64, 4), dtype=np.uint8)

    def camo(x, y, w_, h_, base=(84, 92, 64)):
        cols = [base, (64, 70, 48), (110, 104, 76), (46, 50, 38)]
        patch = np.zeros((h_, w_, 4), dtype=np.uint8)
        blobs = rng.integers(0, 4, (h_ // 2 + 1, w_ // 2 + 1))
        for j in range(h_):
            for i in range(w_):
                c = cols[blobs[j // 2, i // 2]]
                n = rng.integers(-6, 6)
                patch[j, i] = [max(0, min(255, c[0] + n)), max(0, min(255, c[1] + n)), max(0, min(255, c[2] + n)), 255]
        img[y:y + h_, x:x + w_] = patch

    def fill(x, y, w_, h_, c):
        img[y:y + h_, x:x + w_] = list(c) + [255]

    camo(0, 16, 16, 16)                       # right leg
    fill(0, 28, 16, 4, (40, 34, 28))          # boots
    camo(16, 16, 24, 16, (90, 96, 70))        # body
    fill(16, 26, 24, 2, (50, 44, 34))         # belt
    fill(20, 20, 8, 5, (60, 66, 48))          # plate carrier
    fill(21, 21, 6, 3, (52, 56, 42))
    camo(40, 16, 16, 16)                      # right arm
    fill(40, 29, 16, 3, (196, 150, 120))      # hands
    fill(44, 16, 4, 4, (84, 92, 64))
    fill(48, 16, 4, 4, (196, 150, 120))
    # head: dark balaclava with an eye slit
    fill(0, 0, 32, 16, (34, 34, 36))
    fill(8, 11, 8, 2, (196, 150, 120))
    fill(9, 11, 2, 1, (240, 240, 240))
    fill(13, 11, 2, 1, (240, 240, 240))
    fill(10, 11, 1, 1, (40, 30, 20))
    fill(14, 11, 1, 1, (40, 30, 20))
    # hat layer: helmet
    fill(32, 0, 32, 8, (70, 76, 56))
    fill(32, 8, 32, 3, (70, 76, 56))
    os.makedirs(os.path.join(A, "textures", "entity"), exist_ok=True)
    Image.fromarray(img, "RGBA").save(os.path.join(A, "textures", "entity", "mercenary.png"))


def workbench():
    os.makedirs(os.path.join(A, "textures", "block"), exist_ok=True)
    rng = np.random.default_rng(5)

    def tex(name, painter):
        arr = np.zeros((16, 16, 3), dtype=float)
        painter(arr)
        arr += rng.normal(0, 4, arr.shape)
        Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").save(os.path.join(A, "textures", "block", f"gun_workbench_{name}.png"))

    def top(a):
        a[:] = (70, 72, 76)
        a[0, :] = a[-1, :] = a[:, 0] = a[:, -1] = (48, 49, 52)
        a[3:5, 2:12] = (40, 40, 42)        # rifle silhouette on the mat
        a[5:8, 9:11] = (40, 40, 42)
        a[4, 12:14] = (40, 40, 42)
        a[10:13, 3:6] = (150, 120, 60)     # brass
        a[10:12, 9:14] = (110, 70, 40)     # wood stock blank

    def side(a):
        a[:] = (110, 74, 44)
        for y in (3, 8, 13):
            a[y, :] = (80, 52, 30)
        a[0:2, :] = (70, 72, 76)
        a[:, 0] = a[:, -1] = (60, 60, 64)

    def front(a):
        side(a)
        a[4:7, 3:13] = (60, 62, 66)
        a[9:12, 3:13] = (60, 62, 66)
        a[5, 7:9] = (170, 170, 170)
        a[10, 7:9] = (170, 170, 170)

    def bottom(a):
        a[:] = (90, 60, 36)

    tex("top", top)
    tex("side", side)
    tex("front", front)
    tex("bottom", bottom)
    w(os.path.join(A, "models", "block", "gun_workbench.json"), {
        "parent": "minecraft:block/orientable_with_bottom",
        "textures": {"top": "calibre:block/gun_workbench_top", "side": "calibre:block/gun_workbench_side",
                     "front": "calibre:block/gun_workbench_front", "bottom": "calibre:block/gun_workbench_bottom",
                     "particle": "calibre:block/gun_workbench_side"}})
    w(os.path.join(A, "blockstates", "gun_workbench.json"), {"variants": {
        "facing=north": {"model": "calibre:block/gun_workbench"},
        "facing=east": {"model": "calibre:block/gun_workbench", "y": 90},
        "facing=south": {"model": "calibre:block/gun_workbench", "y": 180},
        "facing=west": {"model": "calibre:block/gun_workbench", "y": 270}}})
    w(os.path.join(D, "loot_table", "blocks", "gun_workbench.json"), {"type": "minecraft:block", "pools": [{
        "rolls": 1, "entries": [{"type": "minecraft:item", "name": "calibre:gun_workbench"}],
        "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    w(os.path.join(RES, "data", "minecraft", "tags", "block", "mineable", "pickaxe.json"), {"values": ["calibre:gun_workbench"]})
    w(os.path.join(D, "recipe", "gun_workbench.json"), {
        "type": "minecraft:crafting_shaped", "category": "misc",
        "pattern": ["III", "ICI", "PRP"],
        "key": {"I": "minecraft:iron_ingot", "C": "minecraft:crafting_table", "P": "#minecraft:planks", "R": "minecraft:redstone"},
        "result": {"id": "calibre:gun_workbench", "count": 1}})


def rocket_model():
    m = core.Model("rocket")
    b = m.root.bone("body", pivot=(0, 0, 0))
    # the entity renderer faces +Z along travel; rocket nose towards +Z here
    b.cyl((0, 0, 30), 84, 70, "rocket_green", sides=12)
    b.cyl((0, 0, 100), 70, 70, "rocket_green", sides=12)
    b.cyl((0, 0, 160), 46, 50, "rocket_green", sides=12)
    b.cyl((0, 0, 200), 24, 40, "warhead", sides=12)
    b.cyl((0, 0, 222), 12, 12, "steel")
    b.cyl((0, 0, -60), 40, 120, "warhead", sides=12)
    for ang in (0, 45, 90, 135):
        b.box(-60, 60, -1.5, 1.5, -130, -100, "steel_dark", rot=(0, 0, ang), pivot=(0, 0, -115))
    core.pack_uv(m, density=0.6)
    core.export_geo(m, os.path.join(A, "geckolib", "models", "entity", "rocket.geo.json"))
    materials.paint_texture(m, os.path.join(A, "textures", "entity", "rocket.png"))
    w(os.path.join(A, "geckolib", "animations", "entity", "rocket.animation.json"), {"format_version": "1.8.0", "animations": {}})


# ------------------------------------------------------------------------------------------------ data
def damage_and_tags():
    w(os.path.join(D, "damage_type", "bullet.json"), {"message_id": "calibre.bullet", "scaling": "never", "exhaustion": 0.1})
    w(os.path.join(D, "damage_type", "bullet_headshot.json"), {"message_id": "calibre.headshot", "scaling": "never", "exhaustion": 0.1})
    for tag in ("is_projectile", "no_knockback"):
        w(os.path.join(RES, "data", "minecraft", "tags", "damage_type", f"{tag}.json"),
          {"replace": False, "values": ["calibre:bullet", "calibre:bullet_headshot"]})


def loot():
    def cond(tables):
        return [{"condition": "minecraft:any_of", "terms": [
            {"condition": "neoforge:loot_table_id", "loot_table_id": t} for t in tables]}]

    guns_common = ["glock17", "m1911", "m9", "rem870", "uzi", "mp5", "akm", "usp", "cz75", "mp40", "sten", "spas12", "makarov", "p38", "m3grease", "pps43", "doublebarrel"]
    # hunting / civilian guns turn up where villagers and sailors live, old service arms in ruins and strongholds
    guns_civ = ["win1894", "marlin336", "nova", "cdaly", "mossberg190", "ppq", "bersa", "rugermk3", "sw642", "singlesix",
                "tikka_t3", "rem700", "python", "saa", "doublebarrel", "m1carbine"]
    guns_ww2 = ["mosin", "m1917", "arisaka", "sks", "ppsh41", "m45", "ak47", "model12", "kar98k", "garand", "enfield", "thompson", "mp40", "stg44", "bar", "sten", "m1carbine", "svt40", "g43", "fg42", "m3grease", "pps43", "luger", "p38", "c96", "bren", "dp28"]
    guns_mil = ["m4a1", "hk416", "akm", "fal", "scar_h", "m14ebr", "svd", "m249", "ump45", "p90", "aug", "benelli_m4", "vector", "mp7", "g36c", "famas", "x95", "fiveseven", "m16a1", "galil", "g3a3", "sr25", "aa12", "skorpion", "ak74m", "aks74u", "ak12", "mcx", "l85a2", "qbz95", "f2000", "hk417", "p226", "mac10", "ksg", "rpk"]
    guns_rare = ["deagle", "model29", "m24", "awm", "m82a1", "pkm", "rpg7", "mg42", "m60", "intervention", "l96", "dsr1", "svu", "ks23", "rpd", "m240b", "mg34", "vss"]
    ammo_all = [f"ammo_{k}" for k in AMMO if k != "pg7"]
    atts = [k for k in ATT_NAMES]
    mods = {
        "weaponsmith": (["minecraft:chests/village/village_weaponsmith"], guns_common + guns_civ, 0.55, 2),
        "outpost": (["minecraft:chests/pillager_outpost"], guns_common + guns_mil + guns_ww2, 0.7, 2),
        "shipwreck": (["minecraft:chests/shipwreck_supply", "minecraft:chests/shipwreck_treasure"],
                      guns_common + guns_civ[:5] + ["model12", "m1917", "arisaka"], 0.35, 1),
        "dungeon": (["minecraft:chests/simple_dungeon", "minecraft:chests/abandoned_mineshaft", "minecraft:chests/desert_pyramid",
                     "minecraft:chests/jungle_temple"], guns_common + guns_mil[:4] + guns_ww2, 0.4, 2),
        "stronghold": (["minecraft:chests/stronghold_corridor", "minecraft:chests/stronghold_crossing",
                        "minecraft:chests/woodland_mansion"], guns_mil + guns_rare[:3] + guns_ww2 + ["savage10"],
                       0.45, 2),
        "endgame": (["minecraft:chests/bastion_treasure", "minecraft:chests/bastion_other", "minecraft:chests/ancient_city",
                     "minecraft:chests/end_city_treasure", "minecraft:chests/trial_chambers/reward_rare",
                     "minecraft:chests/trial_chambers/reward_ominous_rare"], guns_mil + guns_rare + ["savage10", "tikka_t3"],
                    0.6, 2),
    }
    names = []
    fabric_loot = {}
    for name, (tables, guns, chance, rolls) in mods.items():
        entries = [{"item": f"calibre:{g}", "weight": 3} for g in guns]
        entries += [{"item": f"calibre:{a}", "weight": 4, "min": 8, "max": 32} for a in ammo_all]
        entries += [{"item": f"calibre:{a}", "weight": 2} for a in atts]
        if name in ("endgame", "stronghold"):
            entries.append({"item": "calibre:ammo_pg7", "weight": 2, "min": 1, "max": 2})
        fabric_loot[name] = {"tables": tables, "entries": entries, "chance": chance, "rolls": rolls}
        w(os.path.join(NEO_RES, "data", "calibre", "loot_modifiers", f"{name}.json"), {"type": "calibre:add_items", "conditions": cond(tables),
                                                              "entries": entries, "chance": chance, "rolls": rolls})
        names.append(f"calibre:{name}")
    w(os.path.join(NEO_RES, "data", "neoforge", "loot_modifiers", "global_loot_modifiers.json"), {"replace": False, "entries": names})
    # Fabric applies the same pools from code (dev.calibre.loot.CalibreLoot)
    w(os.path.join(RES, "calibre_gen", "loot.json"), fabric_loot)
    w(os.path.join(D, "loot_table", "entities", "mercenary.json"), {"type": "minecraft:entity", "pools": [
        {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:gunpowder",
                                  "functions": [{"function": "minecraft:set_count", "count": {"min": 0, "max": 2}}]}]},
        {"rolls": 1, "conditions": [{"condition": "minecraft:killed_by_player"},
                                    {"condition": "minecraft:random_chance", "chance": 0.08}],
         "entries": [{"type": "minecraft:item", "name": f"calibre:{a}"} for a in atts if a != "pso1"]}]})
    w(os.path.join(NEO_RES, "data", "calibre", "neoforge", "biome_modifier", "mercenary_spawns.json"), {
        "type": "neoforge:add_spawns", "biomes": "#minecraft:is_overworld",
        "spawners": {"type": "calibre:mercenary", "weight": 5, "minCount": 1, "maxCount": 3}})


def lang():
    L = {
        "itemGroup.calibre.guns": "Calibre: Firearms", "itemGroup.calibre.gear": "Calibre: Ammo & Attachments",
        # Fabric (Mod Menu) settings screen
        "config.calibre.title": "Calibre Settings", "config.calibre.server": "World rules", "config.calibre.client": "Client",
        "config.calibre.damageMultiplier": "Damage", "config.calibre.mobDamageMultiplier": "Mob damage",
        "config.calibre.headshotMultiplier": "Headshot multiplier", "config.calibre.bulletsBreakGlass": "Bullets break glass",
        "config.calibre.explosionsBreakBlocks": "Explosions break blocks", "config.calibre.mercenarySpawns": "Mercenary spawns",
        "config.calibre.infiniteAmmo": "Infinite ammo", "config.calibre.creativeInfiniteAmmo": "Creative infinite ammo",
        "config.calibre.allTracers": "All tracers", "config.calibre.hud": "Ammo HUD", "config.calibre.crosshair": "Dynamic crosshair",
        "config.calibre.hitMarkers": "Hit markers", "config.calibre.sway": "Weapon sway", "config.calibre.bob": "Weapon bob",
        "config.calibre.cameraRecoil": "Camera recoil", "config.calibre.adsSensitivity": "ADS sensitivity",
        "block.calibre.gun_workbench": "Gun Workbench", "container.calibre.gun_workbench": "Gun Workbench",
        "entity.calibre.mercenary": "Mercenary", "entity.calibre.bullet": "Bullet", "entity.calibre.rocket": "Rocket",
        "key.categories.calibre.calibre": "Calibre", "key.category.calibre.calibre": "Calibre",
        "key.calibre.reload": "Reload", "key.calibre.fire_mode": "Switch Fire Mode", "key.calibre.inspect": "Inspect Weapon",
        "tooltip.calibre.caliber": "Calibre: %s", "tooltip.calibre.ammo": "Rounds: %s / %s",
        "tooltip.calibre.modes": "%s  •  %s RPM", "tooltip.calibre.weight": "Weight: %s kg",
        "tooltip.calibre.attachable": "Customise at a Gun Workbench", "tooltip.calibre.zoom": "Magnification: %s×",
        "tooltip.calibre.suppressed": "Suppressed: no muzzle flash, quiet report", "tooltip.calibre.mag": "+%s%% magazine capacity",
        "tooltip.calibre.fits": "Fits %s guns",
        "message.calibre.mag_full": "Magazine full",
        "message.calibre.no_ammo": "No %s rounds — craft them at a Gun Workbench",
        "tooltip.calibre.stat.recoil": "Recoil %s", "tooltip.calibre.stat.hip_spread": "Hip-fire spread %s",
        "tooltip.calibre.stat.ads_spread": "ADS spread %s", "tooltip.calibre.stat.ads_time": "Aim time %s",
        "tooltip.calibre.slot.optic": "Optic", "tooltip.calibre.slot.muzzle": "Muzzle", "tooltip.calibre.slot.under": "Underbarrel",
        "tooltip.calibre.slot.side": "Side rail", "tooltip.calibre.slot.mag": "Magazine",
        "gui.calibre.tab.guns": "Guns", "gui.calibre.tab.ammo": "Ammo", "gui.calibre.tab.attachments": "Parts",
        "gui.calibre.tab.modify": "Modify", "gui.calibre.craft": "Craft", "gui.calibre.select": "Select a recipe",
        "gui.calibre.hold_gun": "Hold a gun in your main hand to modify it.", "gui.calibre.installed": "Installed (click to remove)",
        "gui.calibre.available": "In inventory (click to install)", "gui.calibre.none": "No compatible attachments",
        "gui.calibre.modify_hint": "Attachments change recoil, spread, aim speed and zoom.",
        "death.attack.calibre.bullet": "%1$s was shot", "death.attack.calibre.bullet.player": "%1$s was shot by %2$s",
        "death.attack.calibre.bullet.item": "%1$s was shot by %2$s using %3$s",
        "death.attack.calibre.headshot": "%1$s took a headshot", "death.attack.calibre.headshot.player": "%1$s was headshot by %2$s",
        "death.attack.calibre.headshot.item": "%1$s was headshot by %2$s using %3$s",
        "subtitles.calibre.fire": "Gunshot",
        "calibre.configuration.title": "Calibre Configuration",
    }
    for k, v in GUN_NAMES.items():
        L[f"item.calibre.{k}"] = v
    for k, (name, *_rest) in AMMO.items():
        L[f"item.calibre.ammo_{k}"] = name + (" Rounds" if k not in ("pg7",) else "")
    for k, v in ATT_NAMES.items():
        L[f"item.calibre.{k}"] = v
    w(os.path.join(A, "lang", "en_us.json"), L)


# ------------------------------------------------------------------------------------------------ test structure
def nbt_structure(path, size=(9, 5, 12)):
    """Minimal structure NBT: stone floor, air above."""
    def tag_string(s):
        b = s.encode()
        return struct.pack(">H", len(b)) + b

    def named(tid, name, payload):
        return bytes([tid]) + tag_string(name) + payload

    def int_tag(name, v):
        return named(3, name, struct.pack(">i", v))

    def list_tag(name, tid, items):
        return named(9, name, bytes([tid]) + struct.pack(">i", len(items)) + b"".join(items))

    def compound(entries):
        return b"".join(entries) + b"\x00"

    sx, sy, sz = size
    palette = [compound([named(8, "Name", tag_string("minecraft:stone"))]),
               compound([named(8, "Name", tag_string("minecraft:air"))])]
    blocks = []
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                pos = list_tag("pos", 3, [struct.pack(">i", x), struct.pack(">i", y), struct.pack(">i", z)])
                blocks.append(compound([pos, int_tag("state", 0 if y == 0 else 1)]))
    root = compound([
        int_tag("DataVersion", 4671),
        list_tag("size", 3, [struct.pack(">i", v) for v in size]),
        list_tag("palette", 10, palette),
        list_tag("blocks", 10, blocks),
        list_tag("entities", 10, []),
    ])
    data = named(10, "", root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wb") as fh:
        fh.write(data)


def main():
    item_models()
    ammo_icons()
    effects()
    scopes()
    mercenary_skin()
    workbench()
    rocket_model()
    damage_and_tags()
    loot()
    lang()
    nbt_structure(os.path.join(D, "structure", "range.nbt"))
    print("data generated")


if __name__ == "__main__":
    main()
