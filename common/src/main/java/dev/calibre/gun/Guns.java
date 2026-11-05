package dev.calibre.gun;

import dev.calibre.gun.GunDefinition.Category;
import dev.calibre.gun.GunDefinition.Cycle;
import dev.calibre.gun.GunDefinition.FireMode;
import dev.calibre.gun.GunDefinition.ReloadType;

import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Map;

import static dev.calibre.gun.Attachment.*;
import static dev.calibre.gun.GunDefinition.builder;

/** The roster. Stats follow the real weapons (capacity, cyclic rate, muzzle velocity, weight, fire modes). */
public final class Guns {
    private static final Map<String, GunDefinition> ALL = new LinkedHashMap<>();

    private static GunDefinition add(GunDefinition def) {
        ALL.put(def.id(), def);
        return def;
    }

    // ---- pistols --------------------------------------------------------------------------------
    public static final GunDefinition GLOCK17 = add(builder("glock17", Category.PISTOL, Caliber.NINE_MM)
            .mag(17).rpm(450).spread(2.6f, 0.5f).recoil(2.4f, 0.7f).ads(4).weight(0.9f).range(50)
            .attach(RED_DOT, SUPPRESSOR_PISTOL, COMPENSATOR, LASER, EXTENDED_MAG).build());
    public static final GunDefinition M1911 = add(builder("m1911", Category.PISTOL, Caliber.ACP45)
            .mag(7).rpm(400).spread(2.8f, 0.5f).recoil(3.2f, 0.8f).ads(4).weight(1.1f).range(45)
            .attach(SUPPRESSOR_PISTOL, COMPENSATOR, EXTENDED_MAG).build());
    public static final GunDefinition M9 = add(builder("m9", Category.PISTOL, Caliber.NINE_MM)
            .mag(15).rpm(450).spread(2.6f, 0.5f).recoil(2.3f, 0.6f).ads(4).weight(0.95f).range(50)
            .attach(SUPPRESSOR_PISTOL, COMPENSATOR, EXTENDED_MAG).build());
    public static final GunDefinition DEAGLE = add(builder("deagle", Category.PISTOL, Caliber.AE50)
            .mag(7).rpm(240).spread(3.6f, 0.6f).recoil(7.5f, 1.6f).ads(5).weight(2.0f).range(60)
            .attach(RED_DOT, COMPENSATOR, LASER).build());
    public static final GunDefinition MODEL29 = add(builder("model29", Category.REVOLVER, Caliber.MAG44)
            .mag(6).rpm(180).cycle(Cycle.DOUBLE_ACTION).reload(ReloadType.CYLINDER).spread(3.2f, 0.4f)
            .recoil(8.0f, 1.4f).ads(5).weight(1.4f).range(65).attach(RED_DOT).build());

    // ---- SMGs -----------------------------------------------------------------------------------
    public static final GunDefinition MP5 = add(builder("mp5", Category.SMG, Caliber.NINE_MM)
            .mag(30).rpm(800).modes(FireMode.SEMI, FireMode.BURST, FireMode.AUTO).spread(3.2f, 0.6f).recoil(1.1f, 0.5f)
            .ads(5).weight(2.5f).range(70)
            .attach(RED_DOT, HOLO, SUPPRESSOR_PISTOL, FLASH_HIDER, VERTICAL_GRIP, ANGLED_GRIP, LASER, EXTENDED_MAG).build());
    public static final GunDefinition UMP45 = add(builder("ump45", Category.SMG, Caliber.ACP45)
            .mag(25).rpm(600).modes(FireMode.SEMI, FireMode.BURST, FireMode.AUTO).burst(2).spread(3.4f, 0.7f)
            .recoil(1.4f, 0.6f).ads(5).weight(2.3f).range(60)
            .attach(RED_DOT, HOLO, ACOG, SUPPRESSOR_PISTOL, COMPENSATOR, VERTICAL_GRIP, ANGLED_GRIP, LASER, EXTENDED_MAG).build());
    public static final GunDefinition UZI = add(builder("uzi", Category.SMG, Caliber.NINE_MM)
            .mag(32).rpm(600).modes(FireMode.SEMI, FireMode.AUTO).cycle(Cycle.OPEN_BOLT).spread(4.0f, 0.9f)
            .recoil(1.3f, 0.8f).ads(4).weight(3.5f).range(50).attach(SUPPRESSOR_PISTOL, EXTENDED_MAG).build());
    public static final GunDefinition P90 = add(builder("p90", Category.SMG, Caliber.FN57)
            .mag(50).rpm(900).modes(FireMode.SEMI, FireMode.AUTO).spread(3.0f, 0.5f).recoil(0.9f, 0.4f).ads(5)
            .weight(2.6f).range(90).attach(SUPPRESSOR_RIFLE, FLASH_HIDER).build());

    // ---- assault rifles -------------------------------------------------------------------------
    public static final GunDefinition M4A1 = add(builder("m4a1", Category.RIFLE, Caliber.NATO556)
            .mag(30).rpm(800).modes(FireMode.SEMI, FireMode.AUTO).spread(3.4f, 0.25f).recoil(1.5f, 0.55f).ads(6)
            .weight(3.4f).range(180)
            .attach(RED_DOT, HOLO, ACOG, SCOPE_8X, SUPPRESSOR_RIFLE, COMPENSATOR, FLASH_HIDER, VERTICAL_GRIP,
                    ANGLED_GRIP, BIPOD_ATT, LASER, EXTENDED_MAG).build());
    public static final GunDefinition HK416 = add(builder("hk416", Category.RIFLE, Caliber.NATO556)
            .mag(30).rpm(850).modes(FireMode.SEMI, FireMode.AUTO).spread(3.4f, 0.22f).recoil(1.4f, 0.5f).ads(6)
            .weight(3.6f).range(190)
            .attach(RED_DOT, HOLO, ACOG, SCOPE_8X, SUPPRESSOR_RIFLE, COMPENSATOR, FLASH_HIDER, VERTICAL_GRIP,
                    ANGLED_GRIP, BIPOD_ATT, LASER, EXTENDED_MAG).build());
    public static final GunDefinition AKM = add(builder("akm", Category.RIFLE, Caliber.R762X39)
            .mag(30).rpm(600).modes(FireMode.SEMI, FireMode.AUTO).spread(3.8f, 0.35f).recoil(2.2f, 0.9f).ads(6)
            .weight(3.3f).range(160).attach(PSO1, SUPPRESSOR_RIFLE, COMPENSATOR, VERTICAL_GRIP, LASER, EXTENDED_MAG).build());
    public static final GunDefinition AUG = add(builder("aug", Category.RIFLE, Caliber.NATO556)
            .mag(30).rpm(700).modes(FireMode.SEMI, FireMode.AUTO).spread(3.2f, 0.22f).recoil(1.3f, 0.45f).ads(6)
            .weight(3.6f).range(190).attach(RED_DOT, HOLO, ACOG, SCOPE_8X, SUPPRESSOR_RIFLE, FLASH_HIDER, LASER,
                    EXTENDED_MAG).build());

    // ---- battle rifles / DMRs -------------------------------------------------------------------
    public static final GunDefinition FAL = add(builder("fal", Category.BATTLE_RIFLE, Caliber.NATO762)
            .mag(20).rpm(650).modes(FireMode.SEMI, FireMode.AUTO).spread(3.8f, 0.25f).recoil(3.0f, 1.0f).ads(7)
            .weight(4.3f).range(250).attach(ACOG, SCOPE_8X, SUPPRESSOR_RIFLE, FLASH_HIDER, BIPOD_ATT).build());
    public static final GunDefinition SCAR_H = add(builder("scar_h", Category.BATTLE_RIFLE, Caliber.NATO762)
            .mag(20).rpm(600).modes(FireMode.SEMI, FireMode.AUTO).spread(3.6f, 0.22f).recoil(2.8f, 0.9f).ads(7)
            .weight(3.6f).range(260).attach(RED_DOT, HOLO, ACOG, SCOPE_8X, SUPPRESSOR_RIFLE, COMPENSATOR, FLASH_HIDER,
                    VERTICAL_GRIP, ANGLED_GRIP, BIPOD_ATT, LASER, EXTENDED_MAG).build());
    public static final GunDefinition SVD = add(builder("svd", Category.DMR, Caliber.R762X54)
            .mag(10).rpm(300).spread(4.0f, 0.12f).recoil(3.6f, 0.8f).ads(8).weight(4.3f).range(400)
            .attach(SUPPRESSOR_RIFLE, BIPOD_ATT).build());
    public static final GunDefinition M14EBR = add(builder("m14ebr", Category.DMR, Caliber.NATO762)
            .mag(20).rpm(350).spread(3.8f, 0.14f).recoil(3.2f, 0.8f).ads(8).weight(5.1f).range(380)
            .attach(RED_DOT, ACOG, SCOPE_8X, SUPPRESSOR_RIFLE, COMPENSATOR, VERTICAL_GRIP, BIPOD_ATT, LASER,
                    EXTENDED_MAG).build());

    // ---- snipers --------------------------------------------------------------------------------
    public static final GunDefinition M24 = add(builder("m24", Category.SNIPER, Caliber.NATO762)
            .mag(5).rpm(60).cycle(Cycle.BOLT_ACTION).reload(ReloadType.SHELL_BY_SHELL).damage(1.15f).velocity(1.05f)
            .spread(5.0f, 0.04f).recoil(5.0f, 0.6f).ads(9).weight(5.4f).range(600).attach(SUPPRESSOR_RIFLE).build());
    public static final GunDefinition AWM = add(builder("awm", Category.SNIPER, Caliber.WM300)
            .mag(5).rpm(50).cycle(Cycle.BOLT_ACTION).spread(5.0f, 0.03f).recoil(6.5f, 0.7f).ads(10).weight(6.5f)
            .range(800).attach(SUPPRESSOR_RIFLE).build());
    public static final GunDefinition M82A1 = add(builder("m82a1", Category.SNIPER, Caliber.BMG50)
            .mag(10).rpm(120).spread(6.0f, 0.05f).recoil(9.0f, 1.2f).ads(12).weight(14.0f).range(1000).build());

    // ---- shotguns -------------------------------------------------------------------------------
    public static final GunDefinition REM870 = add(builder("rem870", Category.SHOTGUN, Caliber.BUCK12)
            .mag(6).rpm(70).cycle(Cycle.PUMP).reload(ReloadType.SHELL_BY_SHELL).spread(4.5f, 3.2f).recoil(6.0f, 1.2f)
            .ads(6).weight(3.6f).range(40).attach(RED_DOT, LASER).build());
    public static final GunDefinition BENELLI_M4 = add(builder("benelli_m4", Category.SHOTGUN, Caliber.BUCK12)
            .mag(7).rpm(300).reload(ReloadType.SHELL_BY_SHELL).spread(4.5f, 3.0f).recoil(5.0f, 1.2f).ads(6)
            .weight(3.8f).range(40).attach(RED_DOT, HOLO, LASER).build());

    // ---- LMGs -----------------------------------------------------------------------------------
    public static final GunDefinition M249 = add(builder("m249", Category.LMG, Caliber.NATO556)
            .mag(200).rpm(800).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).reload(ReloadType.BELT).spread(4.6f, 0.5f)
            .recoil(1.5f, 0.8f).ads(10).weight(7.5f).range(220).attach(RED_DOT, HOLO, ACOG, LASER).build());
    public static final GunDefinition PKM = add(builder("pkm", Category.LMG, Caliber.R762X54)
            .mag(100).rpm(650).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).reload(ReloadType.BELT).spread(4.8f, 0.55f)
            .recoil(2.3f, 1.0f).ads(10).weight(7.5f).range(260).attach(PSO1).build());

    // ---- launcher -------------------------------------------------------------------------------
    public static final GunDefinition RPG7 = add(builder("rpg7", Category.LAUNCHER, Caliber.PG7)
            .mag(1).rpm(20).cycle(Cycle.SINGLE_SHOT).reload(ReloadType.ROCKET).spread(2.0f, 0.4f).recoil(9.0f, 1.0f)
            .ads(10).weight(7.0f).range(300).build());

    // =============================================================================================
    // Expansion: guns from the Free Firearm Sound Library, each with its own recorded report
    // =============================================================================================
    // ---- WWII / Cold War service arms -----------------------------------------------------------
    public static final GunDefinition MOSIN = add(builder("mosin", Category.SNIPER, Caliber.R762X54)
            .mag(5).clip(5).rpm(45).cycle(Cycle.BOLT_ACTION).damage(1.1f).spread(5.0f, 0.08f).recoil(5.6f, 0.7f)
            .ads(8).weight(4.0f).range(500).build());
    public static final GunDefinition M1917 = add(builder("m1917", Category.SNIPER, Caliber.SPR3006)
            .mag(6).clip(5).rpm(45).cycle(Cycle.BOLT_ACTION).spread(5.0f, 0.08f).recoil(5.8f, 0.7f).ads(8)
            .weight(4.2f).range(500).build());
    public static final GunDefinition ARISAKA = add(builder("arisaka", Category.SNIPER, Caliber.ARI77)
            .mag(5).clip(5).rpm(45).cycle(Cycle.BOLT_ACTION).spread(5.0f, 0.09f).recoil(5.4f, 0.7f).ads(8)
            .weight(3.7f).range(480).build());
    public static final GunDefinition SKS = add(builder("sks", Category.DMR, Caliber.R762X39)
            .mag(10).clip(10).rpm(350).spread(3.8f, 0.18f).recoil(2.6f, 0.7f).ads(7).weight(3.9f).range(300)
            .build());
    public static final GunDefinition PPSH41 = add(builder("ppsh41", Category.SMG, Caliber.R762X25)
            .mag(71).rpm(1000).modes(FireMode.AUTO, FireMode.SEMI).cycle(Cycle.OPEN_BOLT).spread(4.2f, 0.9f)
            .recoil(1.0f, 0.7f).ads(6).weight(5.4f).range(80).build());
    public static final GunDefinition M45 = add(builder("m45", Category.SMG, Caliber.NINE_MM)
            .mag(36).rpm(600).modes(FireMode.AUTO).cycle(Cycle.OPEN_BOLT).spread(3.8f, 0.8f).recoil(1.0f, 0.6f)
            .ads(5).weight(3.6f).range(65).attach(SUPPRESSOR_PISTOL).build());
    public static final GunDefinition AK47 = add(builder("ak47", Category.RIFLE, Caliber.R762X39)
            .mag(30).rpm(600).modes(FireMode.SEMI, FireMode.AUTO).spread(3.9f, 0.36f).recoil(2.1f, 0.85f).ads(6)
            .weight(4.3f).range(160).attach(PSO1, SUPPRESSOR_RIFLE, COMPENSATOR, EXTENDED_MAG).build());

    // ---- lever actions --------------------------------------------------------------------------
    public static final GunDefinition WIN1894 = add(builder("win1894", Category.RIFLE, Caliber.WIN3030)
            .mag(7).rpm(90).cycle(Cycle.LEVER).reload(ReloadType.SHELL_BY_SHELL).spread(4.4f, 0.14f).recoil(4.0f, 0.6f)
            .ads(6).weight(3.0f).range(220).build());
    public static final GunDefinition MARLIN336 = add(builder("marlin336", Category.RIFLE, Caliber.WIN3030)
            .mag(6).rpm(90).cycle(Cycle.LEVER).reload(ReloadType.SHELL_BY_SHELL).spread(4.4f, 0.12f).recoil(4.0f, 0.6f)
            .ads(6).weight(3.2f).range(230).attach(RED_DOT, ACOG).build());

    // ---- hunting / precision bolt guns ----------------------------------------------------------
    public static final GunDefinition TIKKA_T3 = add(builder("tikka_t3", Category.SNIPER, Caliber.SPR3006)
            .mag(3).rpm(55).cycle(Cycle.BOLT_ACTION).spread(5.0f, 0.04f).recoil(5.4f, 0.6f).ads(9).weight(3.4f)
            .range(600).attach(SUPPRESSOR_RIFLE).build());
    public static final GunDefinition SAVAGE10 = add(builder("savage10", Category.SNIPER, Caliber.BLK300)
            .mag(10).rpm(60).cycle(Cycle.BOLT_ACTION).spread(5.0f, 0.05f).recoil(3.6f, 0.5f).ads(8).weight(4.1f)
            .range(400).attach(SUPPRESSOR_RIFLE).build());

    // ---- shotguns -------------------------------------------------------------------------------
    // the Model 12 has no disconnector: hold the trigger (AUTO = "slam fire") and it fires every time the slide closes
    public static final GunDefinition MODEL12 = add(builder("model12", Category.SHOTGUN, Caliber.BUCK12)
            .mag(6).rpm(110).modes(FireMode.SEMI, FireMode.AUTO).cycle(Cycle.PUMP).reload(ReloadType.SHELL_BY_SHELL)
            .spread(4.6f, 3.4f).recoil(6.2f, 1.3f).ads(6).weight(3.6f).range(38).build());
    public static final GunDefinition NOVA = add(builder("nova", Category.SHOTGUN, Caliber.BUCK12)
            .mag(4).rpm(70).cycle(Cycle.PUMP).reload(ReloadType.SHELL_BY_SHELL).spread(4.5f, 3.2f).recoil(6.4f, 1.3f)
            .ads(6).weight(3.6f).range(40).attach(RED_DOT, HOLO).build());
    public static final GunDefinition CDALY = add(builder("cdaly", Category.SHOTGUN, Caliber.BUCK12)
            .mag(4).rpm(70).cycle(Cycle.PUMP).reload(ReloadType.SHELL_BY_SHELL).spread(4.2f, 2.6f).recoil(6.0f, 1.2f)
            .ads(6).weight(3.3f).range(45).attach(RED_DOT).build());
    public static final GunDefinition MOSSBERG190 = add(builder("mossberg190", Category.SHOTGUN, Caliber.BUCK16)
            .mag(2).rpm(45).cycle(Cycle.BOLT_ACTION).spread(4.2f, 2.8f).recoil(5.2f, 1.0f).ads(6).weight(3.1f)
            .range(40).build());

    // ---- handguns -------------------------------------------------------------------------------
    public static final GunDefinition PPQ = add(builder("ppq", Category.PISTOL, Caliber.NINE_MM)
            .mag(15).rpm(460).spread(2.5f, 0.45f).recoil(2.2f, 0.6f).ads(4).weight(0.7f).range(50)
            .attach(RED_DOT, SUPPRESSOR_PISTOL, COMPENSATOR, LASER, EXTENDED_MAG).build());
    public static final GunDefinition BERSA = add(builder("bersa", Category.PISTOL, Caliber.ACP380)
            .mag(7).rpm(420).spread(2.8f, 0.6f).recoil(1.8f, 0.6f).ads(3).weight(0.57f).range(35)
            .attach(SUPPRESSOR_PISTOL).build());
    public static final GunDefinition RUGERMK3 = add(builder("rugermk3", Category.PISTOL, Caliber.LR22)
            .mag(10).rpm(500).spread(2.2f, 0.3f).recoil(0.8f, 0.3f).ads(4).weight(1.0f).range(45)
            .attach(RED_DOT, SUPPRESSOR_PISTOL).build());
    public static final GunDefinition SW642 = add(builder("sw642", Category.REVOLVER, Caliber.SPL38)
            .mag(5).rpm(200).cycle(Cycle.DOUBLE_ACTION).reload(ReloadType.CYLINDER).spread(3.4f, 0.7f)
            .recoil(4.0f, 1.0f).ads(4).weight(0.43f).range(30).build());
    public static final GunDefinition SINGLESIX = add(builder("singlesix", Category.REVOLVER, Caliber.LR22)
            .mag(6).rpm(85).cycle(Cycle.SINGLE_ACTION).reload(ReloadType.SHELL_BY_SHELL).spread(2.8f, 0.35f)
            .recoil(1.4f, 0.4f).ads(4).weight(0.95f).range(45).build());

    private Guns() {}

    public static Collection<GunDefinition> all() {
        return ALL.values();
    }

    public static GunDefinition get(String id) {
        return ALL.get(id);
    }
}
