package dev.calibre.gun;

/**
 * Real-world cartridge data. Velocity is muzzle velocity (m/s), damage is in half-hearts for a
 * centre-mass hit at point blank, penetration is a "block hardness budget" used by {@link dev.calibre.ballistics.BulletEntity}.
 */
public enum Caliber {
    //            id            name               dmg    m/s   pellets pen   armorPierce tracerColor
    NINE_MM("9mm", "9×19mm Parabellum", 6.0f, 360, 1, 0.6f, 0.10f, 0xFFB040),
    ACP45("45acp", ".45 ACP", 7.0f, 260, 1, 0.5f, 0.08f, 0xFFB040),
    AE50("50ae", ".50 Action Express", 11.0f, 470, 1, 1.0f, 0.20f, 0xFFB040),
    MAG44("44mag", ".44 Magnum", 10.0f, 440, 1, 0.9f, 0.18f, 0xFFB040),
    FN57("57x28", "5.7×28mm", 5.5f, 715, 1, 1.0f, 0.35f, 0xFFB040),
    NATO556("556", "5.56×45mm NATO", 7.0f, 910, 1, 1.4f, 0.30f, 0xFF7A30),
    R762X39("762x39", "7.62×39mm", 8.0f, 715, 1, 1.5f, 0.30f, 0x60FF60),
    NATO762("762", "7.62×51mm NATO", 10.0f, 840, 1, 2.2f, 0.40f, 0xFF7A30),
    R762X54("762x54", "7.62×54mmR", 10.5f, 830, 1, 2.3f, 0.40f, 0x60FF60),
    WM300("300wm", ".300 Winchester Magnum", 17.0f, 880, 1, 3.0f, 0.55f, 0xFF7A30),
    BMG50("50bmg", ".50 BMG", 30.0f, 853, 1, 5.0f, 0.80f, 0xFF7A30),
    BUCK12("12buck", "12 Gauge 00 Buckshot", 2.4f, 400, 9, 0.2f, 0.0f, 0xFFB040),
    SLUG12("12slug", "12 Gauge Slug", 14.0f, 480, 1, 0.8f, 0.15f, 0xFFB040),
    PG7("pg7", "PG-7V Rocket", 0f, 115, 1, 0f, 0f, 0xFFFFFF),
    R762X25("762x25", "7.62×25mm Tokarev", 6.0f, 488, 1, 0.9f, 0.20f, 0xFFB040),
    SPR3006("3006", ".30-06 Springfield", 11.5f, 853, 1, 2.4f, 0.45f, 0xFF7A30),
    ARI77("77x58", "7.7×58mm Arisaka", 10.5f, 730, 1, 2.1f, 0.38f, 0xFF7A30),
    WIN3030("3030", ".30-30 Winchester", 9.0f, 730, 1, 1.6f, 0.25f, 0xFFB040),
    SPL38("38spl", ".38 Special", 6.0f, 270, 1, 0.5f, 0.06f, 0xFFB040),
    LR22("22lr", ".22 Long Rifle", 3.0f, 330, 1, 0.2f, 0.0f, 0xFFB040),
    ACP380("380acp", ".380 ACP", 4.8f, 290, 1, 0.4f, 0.05f, 0xFFB040),
    BLK300("300blk", ".300 AAC Blackout", 8.0f, 670, 1, 1.3f, 0.25f, 0xFF7A30),
    BUCK16("16buck", "16 Gauge Buckshot", 2.2f, 390, 8, 0.2f, 0.0f, 0xFFB040),
    HK46("46x30", "4.6×30mm", 5.0f, 735, 1, 1.1f, 0.35f, 0xFFB040),
    MAUSER792("792x57", "7.92×57mm Mauser", 11.0f, 760, 1, 2.2f, 0.42f, 0xFF7A30),
    KURZ792("792x33", "7.92×33mm Kurz", 8.5f, 685, 1, 1.5f, 0.3f, 0xFF7A30),
    BRIT303("303", ".303 British", 10.5f, 744, 1, 2.1f, 0.38f, 0xFF7A30),
    CHEY408("408", ".408 CheyTac", 24.0f, 900, 1, 4.0f, 0.7f, 0xFF7A30),
    LAPUA338("338lm", ".338 Lapua Magnum", 20.0f, 915, 1, 3.5f, 0.6f, 0xFF7A30),
    MAG357("357mag", ".357 Magnum", 8.5f, 440, 1, 0.8f, 0.15f, 0xFFB040),
    ACP32("32acp", ".32 ACP", 4.0f, 300, 1, 0.3f, 0.03f, 0xFFB040),
    SHELL23("23mm", "23×75mmR Buckshot", 3.6f, 300, 10, 0.2f, 0.0f, 0xFFB040),
    R545X39("545x39", "5.45×39mm", 6.8f, 880, 1, 1.4f, 0.32f, 0x60FF60),
    DBP58("58x42", "5.8×42mm", 7.0f, 930, 1, 1.5f, 0.34f, 0x60FF60),
    CARBINE30("30carbine", ".30 Carbine", 6.5f, 600, 1, 0.9f, 0.18f, 0xFF7A30),
    MAK9X18("9x18", "9×18mm Makarov", 5.2f, 315, 1, 0.5f, 0.07f, 0xFFB040),
    MAUSER763("763x25", "7.63×25mm Mauser", 5.8f, 440, 1, 0.8f, 0.18f, 0xFFB040),
    COLT45("45colt", ".45 Colt", 8.0f, 270, 1, 0.5f, 0.08f, 0xFFB040),
    SUB9X39("9x39", "9×39mm", 9.0f, 290, 1, 1.6f, 0.45f, 0x60FF60);

    public final String id;
    public final String displayName;
    public final float damage;
    public final float velocity;
    public final int pellets;
    public final float penetration;
    public final float armorPierce;
    public final int tracerColor;

    Caliber(String id, String displayName, float damage, float velocity, int pellets, float penetration, float armorPierce, int tracerColor) {
        this.id = id;
        this.displayName = displayName;
        this.damage = damage;
        this.velocity = velocity;
        this.pellets = pellets;
        this.penetration = penetration;
        this.armorPierce = armorPierce;
        this.tracerColor = tracerColor;
    }

    public String ammoItemId() {
        return "ammo_" + id;
    }

    /** blocks per tick */
    public float blocksPerTick() {
        return velocity / 20f;
    }
}
