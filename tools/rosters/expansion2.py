"""Expansion 2 roster (32 guns, 4 packs). Single source for the registration patcher (tools/rosters/apply.py)."""

# new calibres: enum, id, display, dmg, m/s, pellets, pen, armorPierce, tracer, ammo icon (case rgb, tip rgb, len px,
# scale), craft (count, copper, gunpowder, iron nuggets)
CALIBRES = [
    ("HK46", "46x30", "4.6×30mm", 5.0, 735, 1, 1.1, 0.35, "0xFFB040", ((196, 152, 62), (60, 60, 70), 4, 0.55), (30, 1, 1, 2)),
    ("MAUSER792", "792x57", "7.92×57mm Mauser", 11.0, 760, 1, 2.2, 0.42, "0xFF7A30", ((120, 110, 70), (178, 102, 58), 5, 1.0), (16, 2, 2, 3)),
    ("KURZ792", "792x33", "7.92×33mm Kurz", 8.5, 685, 1, 1.5, 0.30, "0xFF7A30", ((120, 110, 70), (178, 102, 58), 5, 0.75), (24, 1, 2, 3)),
    ("BRIT303", "303", ".303 British", 10.5, 744, 1, 2.1, 0.38, "0xFF7A30", ((196, 152, 62), (178, 102, 58), 5, 1.0), (16, 2, 2, 3)),
    ("CHEY408", "408", ".408 CheyTac", 24.0, 900, 1, 4.0, 0.70, "0xFF7A30", ((205, 165, 70), (60, 60, 60), 6, 1.1), (6, 3, 3, 4)),
    ("LAPUA338", "338lm", ".338 Lapua Magnum", 20.0, 915, 1, 3.5, 0.60, "0xFF7A30", ((205, 165, 70), (178, 102, 58), 6, 1.08), (8, 3, 3, 4)),
    ("MAG357", "357mag", ".357 Magnum", 8.5, 440, 1, 0.8, 0.15, "0xFFB040", ((196, 152, 62), (120, 120, 126), 6, 0.55), (14, 1, 2, 3)),
    ("ACP32", "32acp", ".32 ACP", 4.0, 300, 1, 0.3, 0.03, "0xFFB040", ((196, 152, 62), (178, 102, 58), 4, 0.34), (30, 1, 1, 1)),
    ("SHELL23", "23mm", "23×75mmR Buckshot", 3.6, 300, 10, 0.2, 0.0, "0xFFB040", ((60, 70, 60), (205, 165, 70), 9, 0.8), (6, 2, 2, 4)),
]

# id, name, pack, java builder tail, kind (inspect style), shot sound (recording dir/file, at, len, pitch, class),
# synth fallback (size, crack, bass, tail), recipe extras
P = "free_firearm_library/x/Prepared SFX Library/"
GUNS = [
    # ---------------------------------------------------------------- modern
    ("vector", "Kriss Vector .45", "modern", 'Category.SMG, Caliber.ACP45).mag(25).rpm(1200).modes(FireMode.SEMI, FireMode.BURST, FireMode.AUTO).burst(2).spread(3.2f, 0.55f).recoil(0.8f, 0.4f).ads(5).weight(2.7f).range(60).attach(RED_DOT, HOLO, SUPPRESSOR_PISTOL, FLASH_HIDER, VERTICAL_GRIP, LASER, EXTENDED_MAG)', "rifle", ("1911", 1.0, "smg"), (0.66, 0.0, 105, 0.6), "polymer"),
    ("mp7", "H&K MP7A1", "modern", 'Category.SMG, Caliber.HK46).mag(30).rpm(950).modes(FireMode.SEMI, FireMode.AUTO).spread(3.0f, 0.5f).recoil(0.9f, 0.4f).ads(5).weight(1.9f).range(80).attach(RED_DOT, HOLO, SUPPRESSOR_PISTOL, VERTICAL_GRIP, LASER, EXTENDED_MAG)', "rifle", ("AR-15", 3.0, "smg"), (0.55, 0.6, 140, 0.6), "polymer"),
    ("g36c", "H&K G36C", "modern", 'Category.RIFLE, Caliber.NATO556).mag(30).rpm(750).modes(FireMode.SEMI, FireMode.BURST, FireMode.AUTO).spread(3.4f, 0.3f).recoil(1.4f, 0.55f).ads(6).weight(3.3f).range(160).attach(RED_DOT, HOLO, ACOG, SUPPRESSOR_RIFLE, COMPENSATOR, FLASH_HIDER, VERTICAL_GRIP, ANGLED_GRIP, LASER, EXTENDED_MAG)', "rifle", ("AR-15", 0.8, "rifle"), (0.95, 0.9, 95, 1.0), "polymer"),
    ("famas", "FAMAS F1", "modern", 'Category.RIFLE, Caliber.NATO556).mag(25).rpm(1000).modes(FireMode.SEMI, FireMode.BURST, FireMode.AUTO).spread(3.3f, 0.3f).recoil(1.6f, 0.6f).ads(6).weight(3.6f).range(170).attach(RED_DOT, HOLO, ACOG, SUPPRESSOR_RIFLE, FLASH_HIDER)', "rifle", ("AR-15", 0.4, "rifle"), (0.95, 0.9, 95, 1.0), "polymer"),
    ("x95", "IWI Tavor X95", "modern", 'Category.RIFLE, Caliber.NATO556).mag(30).rpm(850).modes(FireMode.SEMI, FireMode.AUTO).spread(3.3f, 0.28f).recoil(1.4f, 0.5f).ads(6).weight(3.3f).range(170).attach(RED_DOT, HOLO, ACOG, SUPPRESSOR_RIFLE, COMPENSATOR, FLASH_HIDER, VERTICAL_GRIP, LASER, EXTENDED_MAG)', "rifle", ("AR-15", -0.3, "rifle"), (0.95, 0.9, 95, 1.0), "polymer"),
    ("fiveseven", "FN Five-seveN", "modern", 'Category.PISTOL, Caliber.FN57).mag(20).rpm(450).spread(2.4f, 0.4f).recoil(1.6f, 0.5f).ads(4).weight(0.74f).range(60).attach(RED_DOT, SUPPRESSOR_PISTOL, COMPENSATOR, LASER, EXTENDED_MAG)', "pistol", ("Walther PPQ", 1.5, "pistol"), (0.55, 0.6, 140, 0.6), "pistol"),
    ("usp", "H&K USP .45", "modern", 'Category.PISTOL, Caliber.ACP45).mag(12).rpm(420).spread(2.6f, 0.45f).recoil(3.0f, 0.8f).ads(4).weight(0.85f).range(50).attach(RED_DOT, SUPPRESSOR_PISTOL, COMPENSATOR, LASER, EXTENDED_MAG)', "pistol", ("1911", -0.3, "pistol"), (0.7, 0.0, 100, 0.8), "pistol"),
    ("cz75", "CZ 75 SP-01", "modern", 'Category.PISTOL, Caliber.NINE_MM).mag(18).rpm(460).spread(2.4f, 0.4f).recoil(2.0f, 0.55f).ads(4).weight(1.1f).range(50).attach(RED_DOT, SUPPRESSOR_PISTOL, COMPENSATOR, LASER, EXTENDED_MAG)', "pistol", ("Walther PPQ", -0.6, "pistol"), (0.6, 0.1, 120, 0.7), "pistol"),
    ("spas12", "Franchi SPAS-12", "modern", 'Category.SHOTGUN, Caliber.BUCK12).mag(8).rpm(75).cycle(Cycle.PUMP).reload(ReloadType.SHELL_BY_SHELL).spread(4.6f, 3.4f).recoil(6.6f, 1.4f).ads(6).weight(4.4f).range(38).attach(RED_DOT)', "shotgun", ("Nova", -0.6, "shotgun"), (1.3, 0.0, 70, 1.2), "shotgun"),
    ("aa12", "Atchisson AA-12", "modern", 'Category.SHOTGUN, Caliber.BUCK12).mag(8).rpm(300).modes(FireMode.SEMI, FireMode.AUTO).cycle(Cycle.OPEN_BOLT).spread(4.8f, 3.6f).recoil(3.2f, 1.2f).ads(6).weight(5.2f).range(35).attach(RED_DOT, HOLO, EXTENDED_MAG)', "rifle", ("Model 12", 0.5, "shotgun"), (1.28, 0.0, 72, 1.2), "shotgun"),
    # ---------------------------------------------------------------- WWII
    ("kar98k", "Mauser Kar98k", "ww2", 'Category.SNIPER, Caliber.MAUSER792).mag(5).clip(5).rpm(45).cycle(Cycle.BOLT_ACTION).spread(5.0f, 0.07f).recoil(5.8f, 0.7f).ads(8).weight(3.9f).range(500)', "bolt", ("Arisaka", -0.4, "big"), (1.35, 1.0, 70, 1.5), "rifle_wood"),
    ("garand", "M1 Garand", "ww2", 'Category.DMR, Caliber.SPR3006).mag(8).rpm(420).spread(3.8f, 0.12f).recoil(3.2f, 0.8f).ads(7).weight(4.3f).range(350)', "rifle", ("1917", 0.6, "battle"), (1.3, 1.0, 72, 1.4), "rifle_wood"),
    ("enfield", "Lee-Enfield No.4 Mk I", "ww2", 'Category.SNIPER, Caliber.BRIT303).mag(10).clip(5).rpm(55).cycle(Cycle.BOLT_ACTION).spread(5.0f, 0.08f).recoil(5.4f, 0.7f).ads(8).weight(4.1f).range(500)', "bolt", ("1917", -0.3, "big"), (1.35, 1.0, 70, 1.5), "rifle_wood"),
    ("thompson", "Thompson M1A1", "ww2", 'Category.SMG, Caliber.ACP45).mag(30).rpm(700).modes(FireMode.SEMI, FireMode.AUTO).cycle(Cycle.OPEN_BOLT).spread(3.8f, 0.7f).recoil(1.5f, 0.7f).ads(5).weight(4.8f).range(60).attach(EXTENDED_MAG)', "rifle", ("Carl Gustav M45", -1.5, "smg"), (0.66, 0.0, 105, 0.6), "rifle_wood"),
    ("mp40", "MP 40", "ww2", 'Category.SMG, Caliber.NINE_MM).mag(32).rpm(550).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).spread(3.6f, 0.6f).recoil(1.0f, 0.5f).ads(5).weight(4.0f).range(60)', "rifle", ("Carl Gustav M45", 0.5, "smg"), (0.58, 0.1, 125, 0.6), "smg"),
    ("stg44", "StG 44", "ww2", 'Category.RIFLE, Caliber.KURZ792).mag(30).rpm(550).modes(FireMode.SEMI, FireMode.AUTO).spread(3.6f, 0.35f).recoil(1.7f, 0.7f).ads(6).weight(4.6f).range(160)', "rifle", ("AK-47", -0.8, "rifle"), (1.05, 0.7, 85, 1.1), "rifle_wood"),
    ("mg42", "MG 42", "ww2", 'Category.LMG, Caliber.MAUSER792).mag(50).rpm(1200).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).reload(ReloadType.BELT).spread(4.4f, 1.0f).recoil(1.6f, 0.9f).ads(10).weight(11.6f).range(220)', "heavy", ("PPSh", -3.0, "lmg"), (1.2, 1.0, 76, 1.1), "lmg"),
    ("bar", "M1918 BAR", "ww2", 'Category.LMG, Caliber.SPR3006).mag(20).rpm(550).modes(FireMode.SEMI, FireMode.AUTO).cycle(Cycle.OPEN_BOLT).spread(4.0f, 0.5f).recoil(2.4f, 0.8f).ads(8).weight(8.8f).range(250).attach(BIPOD_ATT)', "rifle", ("1917", -0.8, "battle"), (1.3, 1.0, 72, 1.4), "rifle_wood"),
    # ---------------------------------------------------------------- sniper / precision
    ("intervention", "CheyTac M200 Intervention", "sniper", 'Category.SNIPER, Caliber.CHEY408).mag(7).rpm(40).cycle(Cycle.BOLT_ACTION).spread(6.0f, 0.02f).recoil(8.0f, 1.0f).ads(10).weight(14.0f).range(900).attach(SUPPRESSOR_RIFLE)', "bolt", ("Tikka", -3.0, "sniper"), (1.8, 1.0, 55, 2.0), "sniper"),
    ("l96", "Accuracy International L96A1", "sniper", 'Category.SNIPER, Caliber.NATO762).mag(10).rpm(50).cycle(Cycle.BOLT_ACTION).spread(5.2f, 0.04f).recoil(4.5f, 0.6f).ads(9).weight(6.5f).range(700).attach(SUPPRESSOR_RIFLE)', "bolt", ("Tikka", -0.8, "sniper"), (1.35, 1.0, 70, 1.6), "sniper"),
    ("rem700", "Remington 700", "sniper", 'Category.SNIPER, Caliber.NATO762).mag(4).rpm(55).cycle(Cycle.BOLT_ACTION).reload(ReloadType.SHELL_BY_SHELL).spread(5.0f, 0.05f).recoil(4.6f, 0.6f).ads(8).weight(3.9f).range(600).attach(SUPPRESSOR_RIFLE)', "bolt", ("Savage 10 .300 Blackout", -1.5, "sniper"), (1.3, 1.0, 72, 1.5), "rifle_wood"),
    ("sr25", "KAC SR-25", "sniper", 'Category.DMR, Caliber.NATO762).mag(20).rpm(300).spread(3.8f, 0.1f).recoil(3.0f, 0.8f).ads(7).weight(4.9f).range(450).attach(RED_DOT, HOLO, ACOG, SCOPE_8X, SUPPRESSOR_RIFLE, FLASH_HIDER, BIPOD_ATT, VERTICAL_GRIP)', "rifle", ("AR-15", -2.0, "battle"), (1.25, 1.0, 75, 1.3), "sniper"),
    ("svu", "SVU", "sniper", 'Category.DMR, Caliber.R762X54).mag(10).rpm(300).modes(FireMode.SEMI, FireMode.AUTO).spread(4.0f, 0.14f).recoil(3.4f, 0.8f).ads(8).weight(4.4f).range(400).attach(SUPPRESSOR_RIFLE)', "rifle", ("Mosin Nagant", 0.4, "battle"), (1.3, 1.0, 72, 1.4), "sniper"),
    ("dsr1", "DSR-Precision DSR-1", "sniper", 'Category.SNIPER, Caliber.LAPUA338).mag(5).rpm(45).cycle(Cycle.BOLT_ACTION).spread(5.5f, 0.02f).recoil(7.0f, 0.8f).ads(10).weight(5.9f).range(850).attach(SUPPRESSOR_RIFLE)', "bolt", ("Tikka", -2.0, "sniper"), (1.6, 1.0, 62, 1.8), "sniper"),
    # ---------------------------------------------------------------- Cold War / misc
    ("m60", "M60", "coldwar", 'Category.LMG, Caliber.NATO762).mag(100).rpm(550).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).reload(ReloadType.BELT).spread(4.6f, 0.7f).recoil(2.0f, 1.0f).ads(10).weight(10.5f).range(240)', "heavy", ("1917", -1.5, "lmg"), (1.25, 1.0, 74, 1.2), "lmg"),
    ("m16a1", "M16A1", "coldwar", 'Category.RIFLE, Caliber.NATO556).mag(20).rpm(750).modes(FireMode.SEMI, FireMode.AUTO).spread(3.4f, 0.25f).recoil(1.5f, 0.55f).ads(6).weight(3.3f).range(200).attach(SUPPRESSOR_RIFLE, BIPOD_ATT)', "rifle", ("AR-15", 0.2, "rifle"), (0.95, 0.9, 95, 1.0), "rifle"),
    ("galil", "IMI Galil ARM", "coldwar", 'Category.RIFLE, Caliber.NATO556).mag(35).rpm(650).modes(FireMode.SEMI, FireMode.AUTO).spread(3.5f, 0.3f).recoil(1.6f, 0.6f).ads(6).weight(4.4f).range(180).attach(SUPPRESSOR_RIFLE, FLASH_HIDER, BIPOD_ATT)', "rifle", ("AK-47", 1.2, "rifle"), (1.0, 0.8, 90, 1.0), "rifle"),
    ("g3a3", "H&K G3A3", "coldwar", 'Category.BATTLE_RIFLE, Caliber.NATO762).mag(20).rpm(550).modes(FireMode.SEMI, FireMode.AUTO).spread(3.8f, 0.22f).recoil(3.0f, 1.0f).ads(7).weight(4.4f).range(260).attach(ACOG, SCOPE_8X, SUPPRESSOR_RIFLE, FLASH_HIDER, BIPOD_ATT)', "rifle", ("1917", 0.3, "battle"), (1.25, 1.0, 75, 1.3), "rifle"),
    ("sten", "Sten Mk II", "coldwar", 'Category.SMG, Caliber.NINE_MM).mag(32).rpm(550).modes(FireMode.SEMI, FireMode.AUTO).cycle(Cycle.OPEN_BOLT).spread(4.0f, 0.8f).recoil(1.1f, 0.6f).ads(5).weight(3.2f).range(50).attach(SUPPRESSOR_PISTOL)', "rifle", ("Carl Gustav M45", 1.0, "smg"), (0.6, 0.1, 120, 0.6), "smg"),
    ("python", "Colt Python", "coldwar", 'Category.REVOLVER, Caliber.MAG357).mag(6).rpm(200).cycle(Cycle.DOUBLE_ACTION).reload(ReloadType.CYLINDER).spread(3.0f, 0.4f).recoil(5.6f, 1.2f).ads(5).weight(1.2f).range(60).attach(RED_DOT)', "revolver", ("Smith & Wesson 642", -2.0, "magnum"), (1.0, 0.2, 85, 1.0), "pistol"),
    ("skorpion", "Skorpion vz. 61", "coldwar", 'Category.SMG, Caliber.ACP32).mag(20).rpm(850).modes(FireMode.SEMI, FireMode.AUTO).spread(3.4f, 0.8f).recoil(0.8f, 0.5f).ads(4).weight(1.3f).range(40).attach(SUPPRESSOR_PISTOL)', "rifle", ("Bersa", 1.0, "smg"), (0.5, 0.0, 130, 0.6), "smg"),
    ("ks23", "KS-23", "coldwar", 'Category.SHOTGUN, Caliber.SHELL23).mag(3).rpm(60).cycle(Cycle.PUMP).reload(ReloadType.SHELL_BY_SHELL).spread(5.2f, 3.8f).recoil(9.5f, 1.8f).ads(7).weight(3.9f).range(35)', "shotgun", ("Model 12", -3.0, "shotgun"), (1.6, 0.0, 60, 1.4), "shotgun"),
]

LOOT = {
    "common": ["usp", "cz75", "mp40", "sten", "spas12"],
    "civ": ["rem700", "python"],
    "ww2": ["kar98k", "garand", "enfield", "thompson", "mp40", "stg44", "bar", "sten"],
    "mil": ["vector", "mp7", "g36c", "famas", "x95", "fiveseven", "m16a1", "galil", "g3a3", "sr25", "aa12", "skorpion"],
    "rare": ["mg42", "m60", "intervention", "l96", "dsr1", "svu", "ks23"],
}
MERCENARY = ["stg44", "mp40", "g3a3", "galil", "sten", "kar98k"]
