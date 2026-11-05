package dev.calibre.gun;

import java.util.EnumSet;
import java.util.List;
import java.util.Set;

/**
 * Static, real-world derived stats of one firearm. Animation timings come from {@link GunMeta} (generated), so the
 * game logic always lines up with what the player sees.
 */
public record GunDefinition(
        String id,
        Category category,
        Caliber caliber,
        int magSize,
        int rpm,
        List<FireMode> modes,
        Cycle cycle,
        ReloadType reloadType,
        float damageMul,
        float velocityMul,
        float hipSpread,
        float adsSpread,
        float recoilV,
        float recoilH,
        int adsTicks,
        float weightKg,
        Set<Attachment> attachments,
        int burstCount,
        float range,
        int clipSize
) {
    public enum Category { PISTOL, REVOLVER, SMG, RIFLE, BATTLE_RIFLE, DMR, SNIPER, SHOTGUN, LMG, LAUNCHER }

    public enum FireMode { SEMI, BURST, AUTO }

    public enum Cycle {
        CLOSED_BOLT, OPEN_BOLT, BOLT_ACTION, PUMP, DOUBLE_ACTION, SINGLE_SHOT, LEVER, SINGLE_ACTION;

        /** a round can sit in the chamber on top of a full magazine */
        public boolean hasChamber() {
            return this == CLOSED_BOLT || this == BOLT_ACTION || this == PUMP || this == LEVER;
        }

        /** the shooter cycles the action by hand after every shot (plays the "cycle" animation) */
        public boolean manual() {
            return this == BOLT_ACTION || this == PUMP || this == LEVER;
        }
    }

    /**
     * STRIPPER_CLIP loads like SHELL_BY_SHELL but uses a whole clip ("reload_clip") whenever there is room for one,
     * falling back to single rounds ("reload_loop") to top up.
     */
    public enum ReloadType {
        MAGAZINE, SHELL_BY_SHELL, CYLINDER, BELT, ROCKET, STRIPPER_CLIP;

        public boolean staged() {
            return this == SHELL_BY_SHELL || this == STRIPPER_CLIP;
        }
    }

    public boolean allows(Attachment a) {
        return attachments.contains(a);
    }

    public int capacity(GunAttachments att) {
        Attachment mag = att.get(Attachment.Slot.MAG);
        if (mag != null && allows(mag)) return Math.round(magSize * mag.magMul);
        return magSize;
    }

    public int ticksBetweenShots() {
        return Math.max(1, Math.round(1200f / rpm));
    }

    public double msBetweenShots() {
        return 60000.0 / rpm;
    }

    public boolean twoHanded() {
        return category != Category.PISTOL && category != Category.REVOLVER;
    }

    // ------------------------------------------------------------------------------------------------
    public static Builder builder(String id, Category category, Caliber caliber) {
        return new Builder(id, category, caliber);
    }

    public static final class Builder {
        private final String id;
        private final Category category;
        private final Caliber caliber;
        private int mag = 30, rpm = 600, burst = 3;
        private List<FireMode> modes = List.of(FireMode.SEMI);
        private Cycle cycle = Cycle.CLOSED_BOLT;
        private ReloadType reload = ReloadType.MAGAZINE;
        private float dmg = 1, vel = 1, hip = 3, ads = 0.4f, rv = 1.5f, rh = 0.5f, kg = 3, range = 120;
        private int adsTicks = 5, clip = 0;
        private final Set<Attachment> att = EnumSet.noneOf(Attachment.class);

        private Builder(String id, Category category, Caliber caliber) {
            this.id = id;
            this.category = category;
            this.caliber = caliber;
        }

        public Builder mag(int v) { mag = v; return this; }
        public Builder rpm(int v) { rpm = v; return this; }
        public Builder modes(FireMode... v) { modes = List.of(v); return this; }
        public Builder burst(int v) { burst = v; return this; }
        public Builder cycle(Cycle v) { cycle = v; return this; }
        public Builder reload(ReloadType v) { reload = v; return this; }
        public Builder damage(float v) { dmg = v; return this; }
        public Builder velocity(float v) { vel = v; return this; }
        public Builder spread(float hipDeg, float adsDeg) { hip = hipDeg; ads = adsDeg; return this; }
        public Builder recoil(float vertical, float horizontal) { rv = vertical; rh = horizontal; return this; }
        public Builder ads(int ticks) { adsTicks = ticks; return this; }
        public Builder weight(float v) { kg = v; return this; }
        public Builder range(float v) { range = v; return this; }
        public Builder attach(Attachment... v) { att.addAll(List.of(v)); return this; }
        /** stripper clip capacity; implies {@link ReloadType#STRIPPER_CLIP} */
        public Builder clip(int v) { clip = v; reload = ReloadType.STRIPPER_CLIP; return this; }

        public GunDefinition build() {
            return new GunDefinition(id, category, caliber, mag, rpm, modes, cycle, reload, dmg, vel, hip, ads, rv, rh,
                    adsTicks, kg, Set.copyOf(att.isEmpty() ? EnumSet.noneOf(Attachment.class) : att), burst, range, clip);
        }
    }
}
