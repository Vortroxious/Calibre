package dev.calibre.gun;

import java.util.Locale;

/** Every attachment with its stat modifiers. Multipliers are applied to the gun's base values. */
public enum Attachment {
    //            slot                 ads   recoil hipSpr adsSpr zoom  supp   magMul  velMul
    RED_DOT(Slot.OPTIC, 1.00f, 1.00f, 1.00f, 0.85f, 1.25f, false, 1.0f, 1.0f),
    HOLO(Slot.OPTIC, 1.05f, 1.00f, 1.00f, 0.80f, 1.35f, false, 1.0f, 1.0f),
    ACOG(Slot.OPTIC, 1.15f, 1.00f, 1.05f, 0.70f, 4.0f, false, 1.0f, 1.0f),
    SCOPE_8X(Slot.OPTIC, 1.30f, 1.00f, 1.15f, 0.50f, 8.0f, false, 1.0f, 1.0f),
    PSO1(Slot.OPTIC, 1.20f, 1.00f, 1.10f, 0.60f, 4.0f, false, 1.0f, 1.0f),
    SUPPRESSOR_PISTOL(Slot.MUZZLE, 1.05f, 0.92f, 1.00f, 1.00f, 1.0f, true, 1.0f, 0.95f),
    SUPPRESSOR_RIFLE(Slot.MUZZLE, 1.08f, 0.90f, 1.00f, 1.00f, 1.0f, true, 1.0f, 0.95f),
    COMPENSATOR(Slot.MUZZLE, 1.00f, 0.78f, 1.05f, 1.00f, 1.0f, false, 1.0f, 1.0f),
    FLASH_HIDER(Slot.MUZZLE, 1.00f, 0.92f, 1.00f, 0.95f, 1.0f, false, 1.0f, 1.0f),
    VERTICAL_GRIP(Slot.UNDER, 1.05f, 0.82f, 0.95f, 1.00f, 1.0f, false, 1.0f, 1.0f),
    ANGLED_GRIP(Slot.UNDER, 0.90f, 0.90f, 1.00f, 1.00f, 1.0f, false, 1.0f, 1.0f),
    BIPOD_ATT(Slot.UNDER, 1.10f, 0.95f, 1.00f, 1.00f, 1.0f, false, 1.0f, 1.0f),
    LASER(Slot.SIDE, 1.00f, 1.00f, 0.65f, 1.00f, 1.0f, false, 1.0f, 1.0f),
    EXTENDED_MAG(Slot.MAG, 1.05f, 1.00f, 1.00f, 1.00f, 1.0f, false, 1.5f, 1.0f);

    public enum Slot { OPTIC, MUZZLE, UNDER, SIDE, MAG }

    public final Slot slot;
    public final float adsTime, recoil, hipSpread, adsSpread, zoom, magMul, velocity;
    public final boolean suppressed;

    Attachment(Slot slot, float adsTime, float recoil, float hipSpread, float adsSpread, float zoom, boolean suppressed,
               float magMul, float velocity) {
        this.slot = slot;
        this.adsTime = adsTime;
        this.recoil = recoil;
        this.hipSpread = hipSpread;
        this.adsSpread = adsSpread;
        this.zoom = zoom;
        this.suppressed = suppressed;
        this.magMul = magMul;
        this.velocity = velocity;
    }

    public String id() {
        return name().toLowerCase(Locale.ROOT);
    }

    /** true when this attachment has a 3D model (everything but the extended mag). */
    public boolean hasModel() {
        return this != EXTENDED_MAG;
    }

    public static Attachment byId(String id) {
        for (Attachment a : values()) if (a.id().equals(id)) return a;
        return null;
    }
}
