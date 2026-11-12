"""Expansion 3 roster (30 guns, 4 packs). Read by the registration patcher: python3 tools/rosters/apply.py expansion3"""
MARK = "expansion 3"
TITLE = "modern II, WWII II, machine guns, handguns and specials"

# new calibres: enum, id, display, dmg, m/s, pellets, pen, armorPierce, tracer, ammo icon (case rgb, tip rgb, len px,
# scale), craft (count, copper, gunpowder, iron nuggets)
CALIBRES = [
    ("R545X39", "545x39", "5.45×39mm", 6.8, 880, 1, 1.4, 0.32, "0x60FF60", ((120, 110, 70), (178, 102, 58), 5, 0.72), (24, 1, 2, 3)),
    ("DBP58", "58x42", "5.8×42mm", 7.0, 930, 1, 1.5, 0.34, "0x60FF60", ((120, 110, 70), (178, 102, 58), 5, 0.74), (24, 1, 2, 3)),
    ("CARBINE30", "30carbine", ".30 Carbine", 6.5, 600, 1, 0.9, 0.18, "0xFF7A30", ((196, 152, 62), (178, 102, 58), 5, 0.6), (24, 1, 1, 2)),
    ("MAK9X18", "9x18", "9×18mm Makarov", 5.2, 315, 1, 0.5, 0.07, "0xFFB040", ((120, 110, 70), (178, 102, 58), 4, 0.4), (30, 1, 1, 1)),
    ("MAUSER763", "763x25", "7.63×25mm Mauser", 5.8, 440, 1, 0.8, 0.18, "0xFFB040", ((196, 152, 62), (178, 102, 58), 4, 0.5), (30, 1, 1, 2)),
    ("COLT45", "45colt", ".45 Colt", 8.0, 270, 1, 0.5, 0.08, "0xFFB040", ((196, 152, 62), (120, 120, 126), 6, 0.56), (14, 1, 2, 3)),
    ("SUB9X39", "9x39", "9×39mm", 9.0, 290, 1, 1.6, 0.45, "0x60FF60", ((120, 110, 70), (60, 60, 70), 5, 0.8), (16, 2, 2, 3)),
]

# id, name, pack, java builder tail, kind (inspect style), shot sound (source recording or an existing fire_<gun>
# event, pitch shift in semitones, class), synth fallback (size, crack, bass, tail), recipe kit
SA = "FireMode.SEMI, FireMode.AUTO"
GUNS = [
    # ---------------------------------------------------------------- modern II
    ("ak74m", "AK-74M", "modern2", f'Category.RIFLE, Caliber.R545X39).mag(30).rpm(650).modes({SA}).spread(3.5f, 0.3f).recoil(1.5f, 0.6f).ads(6).weight(3.4f).range(180).attach(PSO1, SUPPRESSOR_RIFLE, COMPENSATOR, VERTICAL_GRIP, LASER, EXTENDED_MAG)', "rifle", ("AK-47", 1.5, "rifle"), (0.98, 0.9, 92, 1.0), "polymer"),
    ("aks74u", "AKS-74U", "modern2", f'Category.RIFLE, Caliber.R545X39).mag(30).rpm(700).modes({SA}).spread(3.6f, 0.5f).recoil(1.8f, 0.8f).ads(5).weight(2.7f).range(110).attach(SUPPRESSOR_RIFLE, LASER, EXTENDED_MAG)', "rifle", ("AK-47", 2.4, "rifle"), (0.95, 0.9, 98, 0.9), "rifle"),
    ("ak12", "AK-12", "modern2", 'Category.RIFLE, Caliber.R545X39).mag(30).rpm(700).modes(FireMode.SEMI, FireMode.BURST, FireMode.AUTO).burst(2).spread(3.3f, 0.27f).recoil(1.4f, 0.55f).ads(6).weight(3.5f).range(190).attach(RED_DOT, HOLO, ACOG, SUPPRESSOR_RIFLE, COMPENSATOR, VERTICAL_GRIP, ANGLED_GRIP, LASER, EXTENDED_MAG)', "rifle", ("AK-47", 1.0, "rifle"), (0.98, 0.9, 92, 1.0), "polymer"),
    ("mcx", "SIG MCX", "modern2", f'Category.RIFLE, Caliber.BLK300).mag(30).rpm(800).modes({SA}).spread(3.3f, 0.28f).recoil(1.5f, 0.55f).ads(6).weight(2.9f).range(150).attach(RED_DOT, HOLO, ACOG, SUPPRESSOR_RIFLE, COMPENSATOR, FLASH_HIDER, VERTICAL_GRIP, ANGLED_GRIP, LASER, EXTENDED_MAG)', "rifle", ("Savage 10 .300 Blackout", 0.5, "rifle"), (1.0, 0.8, 90, 1.0), "polymer"),
    ("l85a2", "L85A2", "modern2", f'Category.RIFLE, Caliber.NATO556).mag(30).rpm(650).modes({SA}).spread(3.2f, 0.22f).recoil(1.3f, 0.5f).ads(6).weight(4.6f).range(200).attach(RED_DOT, HOLO, ACOG, SUPPRESSOR_RIFLE, FLASH_HIDER, VERTICAL_GRIP, LASER)', "rifle", ("AR-15", -0.6, "rifle"), (0.95, 0.9, 95, 1.0), "polymer"),
    ("qbz95", "QBZ-95", "modern2", f'Category.RIFLE, Caliber.DBP58).mag(30).rpm(650).modes({SA}).spread(3.3f, 0.28f).recoil(1.4f, 0.5f).ads(6).weight(3.3f).range(180).attach(RED_DOT, SUPPRESSOR_RIFLE, FLASH_HIDER)', "rifle", ("AR-15", 0.6, "rifle"), (0.95, 0.9, 95, 1.0), "polymer"),
    ("f2000", "FN F2000", "modern2", f'Category.RIFLE, Caliber.NATO556).mag(30).rpm(850).modes({SA}).spread(3.2f, 0.25f).recoil(1.3f, 0.5f).ads(6).weight(3.6f).range(180).attach(RED_DOT, HOLO, ACOG, SUPPRESSOR_RIFLE, FLASH_HIDER, LASER)', "rifle", ("AR-15", 0.3, "rifle"), (0.95, 0.9, 95, 1.0), "polymer"),
    ("hk417", "H&K HK417", "modern2", f'Category.BATTLE_RIFLE, Caliber.NATO762).mag(20).rpm(600).modes({SA}).spread(3.7f, 0.18f).recoil(2.8f, 0.9f).ads(7).weight(4.4f).range(300).attach(RED_DOT, HOLO, ACOG, SCOPE_8X, SUPPRESSOR_RIFLE, COMPENSATOR, FLASH_HIDER, VERTICAL_GRIP, ANGLED_GRIP, BIPOD_ATT, LASER, EXTENDED_MAG)', "rifle", ("AR-15", -2.4, "battle"), (1.25, 1.0, 75, 1.3), "rifle"),
    # ---------------------------------------------------------------- WWII II
    ("m1carbine", "M1 Carbine", "ww2b", 'Category.RIFLE, Caliber.CARBINE30).mag(15).rpm(450).spread(3.4f, 0.3f).recoil(1.6f, 0.6f).ads(5).weight(2.4f).range(150).attach(EXTENDED_MAG)', "rifle", ("AR-15", -1.5, "rifle"), (0.9, 0.6, 100, 0.9), "rifle_wood"),
    ("svt40", "SVT-40", "ww2b", 'Category.DMR, Caliber.R762X54).mag(10).rpm(350).spread(3.8f, 0.14f).recoil(3.2f, 0.8f).ads(7).weight(3.9f).range(350)', "rifle", ("Mosin Nagant", 0.6, "battle"), (1.3, 1.0, 72, 1.4), "rifle_wood"),
    ("g43", "Gewehr 43", "ww2b", 'Category.DMR, Caliber.MAUSER792).mag(10).rpm(350).spread(3.8f, 0.14f).recoil(3.2f, 0.8f).ads(7).weight(4.4f).range(350)', "rifle", ("Arisaka", 0.2, "battle"), (1.3, 1.0, 72, 1.4), "rifle_wood"),
    ("fg42", "FG 42", "ww2b", f'Category.BATTLE_RIFLE, Caliber.MAUSER792).mag(20).rpm(750).modes({SA}).spread(4.0f, 0.3f).recoil(3.2f, 1.1f).ads(7).weight(4.9f).range(280)', "rifle", ("Arisaka", 0.8, "battle"), (1.3, 1.0, 72, 1.3), "rifle_wood"),
    ("m3grease", "M3 Grease Gun", "ww2b", 'Category.SMG, Caliber.ACP45).mag(30).rpm(450).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).spread(3.9f, 0.8f).recoil(1.2f, 0.6f).ads(5).weight(3.7f).range(50).attach(SUPPRESSOR_PISTOL)', "rifle", ("Carl Gustav M45", -2.2, "smg"), (0.66, 0.0, 105, 0.6), "smg"),
    ("pps43", "PPS-43", "ww2b", 'Category.SMG, Caliber.R762X25).mag(35).rpm(650).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).spread(3.8f, 0.7f).recoil(1.0f, 0.5f).ads(5).weight(3.0f).range(70)', "rifle", ("PPSh", 0.6, "smg"), (0.58, 0.3, 125, 0.6), "smg"),
    ("luger", "Luger P08", "ww2b", 'Category.PISTOL, Caliber.NINE_MM).mag(8).rpm(380).spread(2.5f, 0.4f).recoil(2.4f, 0.7f).ads(4).weight(0.87f).range(50)', "pistol", ("Walther PPQ", -1.0, "pistol"), (0.6, 0.1, 120, 0.7), "pistol"),
    ("p38", "Walther P38", "ww2b", 'Category.PISTOL, Caliber.NINE_MM).mag(8).rpm(400).spread(2.6f, 0.45f).recoil(2.3f, 0.65f).ads(4).weight(0.8f).range(50)', "pistol", ("Walther PPQ", -0.3, "pistol"), (0.6, 0.1, 120, 0.7), "pistol"),
    # ---------------------------------------------------------------- machine guns
    ("rpk", "RPK", "mg", f'Category.LMG, Caliber.R762X39).mag(40).rpm(600).modes({SA}).spread(4.0f, 0.4f).recoil(2.0f, 0.8f).ads(8).weight(4.8f).range(220).attach(PSO1, EXTENDED_MAG)', "rifle", ("AK-47", -0.6, "lmg"), (1.1, 0.7, 82, 1.1), "rifle_wood"),
    ("rpd", "RPD", "mg", 'Category.LMG, Caliber.R762X39).mag(100).rpm(700).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).reload(ReloadType.BELT).spread(4.4f, 0.55f).recoil(1.8f, 0.9f).ads(9).weight(7.4f).range(220)', "heavy", ("AK-47", -1.2, "lmg"), (1.1, 0.7, 82, 1.1), "lmg"),
    ("m240b", "M240B", "mg", 'Category.LMG, Caliber.NATO762).mag(100).rpm(650).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).reload(ReloadType.BELT).spread(4.5f, 0.55f).recoil(2.0f, 0.9f).ads(10).weight(12.5f).range(260).attach(RED_DOT, HOLO, ACOG)', "heavy", ("1917", -1.0, "lmg"), (1.25, 1.0, 74, 1.2), "lmg"),
    ("dp28", "DP-28", "mg", 'Category.LMG, Caliber.R762X54).mag(47).rpm(550).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).spread(4.4f, 0.55f).recoil(2.1f, 0.9f).ads(9).weight(9.1f).range(250)', "heavy", ("Mosin Nagant", -1.2, "lmg"), (1.25, 1.0, 74, 1.2), "lmg"),
    ("mg34", "MG 34", "mg", f'Category.LMG, Caliber.MAUSER792).mag(50).rpm(900).modes({SA}).cycle(Cycle.OPEN_BOLT).reload(ReloadType.BELT).spread(4.3f, 0.8f).recoil(1.7f, 0.9f).ads(10).weight(12.1f).range(230)', "heavy", ("PPSh", -3.6, "lmg"), (1.2, 1.0, 76, 1.1), "lmg"),
    ("bren", "Bren Mk II", "mg", f'Category.LMG, Caliber.BRIT303).mag(30).rpm(520).modes({SA}).cycle(Cycle.OPEN_BOLT).spread(4.0f, 0.4f).recoil(2.0f, 0.8f).ads(9).weight(10.2f).range(260)', "heavy", ("1917", -0.5, "lmg"), (1.25, 1.0, 74, 1.2), "lmg"),
    # ---------------------------------------------------------------- handguns and specials
    ("p226", "SIG Sauer P226", "special", 'Category.PISTOL, Caliber.NINE_MM).mag(15).rpm(450).spread(2.5f, 0.42f).recoil(2.2f, 0.6f).ads(4).weight(0.96f).range(50).attach(RED_DOT, SUPPRESSOR_PISTOL, COMPENSATOR, LASER, EXTENDED_MAG)', "pistol", ("Walther PPQ", 0.4, "pistol"), (0.6, 0.1, 120, 0.7), "pistol"),
    ("makarov", "Makarov PM", "special", 'Category.PISTOL, Caliber.MAK9X18).mag(8).rpm(400).spread(2.8f, 0.55f).recoil(2.0f, 0.6f).ads(3).weight(0.73f).range(35).attach(SUPPRESSOR_PISTOL)', "pistol", ("Bersa", -0.5, "pistol"), (0.52, 0.0, 128, 0.6), "pistol"),
    ("c96", "Mauser C96", "special", 'Category.PISTOL, Caliber.MAUSER763).mag(10).clip(10).rpm(380).spread(2.8f, 0.4f).recoil(2.4f, 0.8f).ads(4).weight(1.13f).range(70)', "pistol", ("Walther PPQ", 1.2, "pistol"), (0.58, 0.3, 125, 0.7), "pistol"),
    ("saa", "Colt Single Action Army", "special", 'Category.REVOLVER, Caliber.COLT45).mag(6).rpm(80).cycle(Cycle.SINGLE_ACTION).reload(ReloadType.SHELL_BY_SHELL).spread(3.0f, 0.4f).recoil(5.0f, 1.2f).ads(4).weight(1.05f).range(55)', "revolver", ("1911", -1.8, "magnum"), (0.9, 0.1, 90, 0.9), "pistol"),
    ("mac10", "Ingram MAC-10", "special", f'Category.SMG, Caliber.ACP45).mag(30).rpm(1100).modes({SA}).cycle(Cycle.OPEN_BOLT).spread(4.6f, 1.1f).recoil(1.3f, 0.9f).ads(4).weight(2.8f).range(40).attach(SUPPRESSOR_PISTOL, EXTENDED_MAG)', "rifle", ("1911", 0.6, "smg"), (0.66, 0.0, 105, 0.6), "smg"),
    ("vss", "VSS Vintorez", "special", f'Category.DMR, Caliber.SUB9X39).mag(10).rpm(700).modes({SA}).spread(3.6f, 0.14f).recoil(1.6f, 0.5f).ads(6).weight(2.6f).range(250).attach(EXTENDED_MAG)', "rifle", ("Savage 10 .300 Blackout", -2.0, "rifle"), (0.5, 0.0, 110, 0.5), "sniper"),
    ("ksg", "Kel-Tec KSG", "special", 'Category.SHOTGUN, Caliber.BUCK12).mag(14).rpm(70).cycle(Cycle.PUMP).reload(ReloadType.SHELL_BY_SHELL).spread(4.4f, 3.2f).recoil(6.4f, 1.4f).ads(6).weight(3.1f).range(38).attach(RED_DOT, HOLO, VERTICAL_GRIP, LASER)', "shotgun", ("Nova", 0.4, "shotgun"), (1.3, 0.0, 70, 1.2), "shotgun"),
    ("doublebarrel", "Double-Barrel Shotgun", "special", 'Category.SHOTGUN, Caliber.BUCK12).mag(2).rpm(220).cycle(Cycle.DOUBLE_ACTION).spread(4.8f, 3.6f).recoil(7.0f, 1.6f).ads(5).weight(3.2f).range(34)', "shotgun", ("Model 12", -1.0, "shotgun"), (1.35, 0.0, 66, 1.3), "shotgun"),
]

LOOT = {
    "common": ["makarov", "p38", "m3grease", "pps43", "doublebarrel"],
    "civ": ["saa", "doublebarrel", "m1carbine"],
    "ww2": ["m1carbine", "svt40", "g43", "fg42", "m3grease", "pps43", "luger", "p38", "c96", "bren", "dp28"],
    "mil": ["ak74m", "aks74u", "ak12", "mcx", "l85a2", "qbz95", "f2000", "hk417", "p226", "mac10", "ksg", "rpk"],
    "rare": ["rpd", "m240b", "mg34", "vss"],
}
MERCENARY = ["ak74m", "aks74u", "rpk", "pps43", "svt40", "makarov"]
