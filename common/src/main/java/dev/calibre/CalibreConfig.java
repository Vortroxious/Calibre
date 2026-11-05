package dev.calibre;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * All settings. Each loader binds the options to its own config system (NeoForge: ModConfigSpec, Fabric: JSON files +
 * an optional Mod Menu screen) through {@link Opt#bind}; until then every option reads as its default.
 */
public final class CalibreConfig {
    public enum Side { SERVER, CLIENT }

    public static final class Opt<T> {
        public final Side side;
        public final String section, name, comment;
        public final T def;
        public final double min, max;
        private volatile Supplier<T> source;

        private Opt(Side side, String section, String name, String comment, T def, double min, double max) {
            this.side = side;
            this.section = section;
            this.name = name;
            this.comment = comment;
            this.def = def;
            this.min = min;
            this.max = max;
            (side == Side.SERVER ? SERVER : CLIENT).add(this);
        }

        public boolean isBoolean() {
            return def instanceof Boolean;
        }

        public void bind(Supplier<T> source) {
            this.source = source;
        }

        public T get() {
            Supplier<T> s = source;
            if (s == null) return def;
            try {
                T v = s.get();
                return v == null ? def : v;
            } catch (Exception e) {
                return def;
            }
        }
    }

    public static final List<Opt<?>> SERVER = new ArrayList<>(), CLIENT = new ArrayList<>();

    private static Opt<Double> d(Side side, String section, String name, String comment, double def, double min, double max) {
        return new Opt<>(side, section, name, comment, def, min, max);
    }

    private static Opt<Boolean> b(Side side, String section, String name, String comment, boolean def) {
        return new Opt<>(side, section, name, comment, def, 0, 1);
    }

    // ---- server (world rules) -------------------------------------------------------------------
    public static final Opt<Double> DAMAGE_MUL = d(Side.SERVER, "damage", "damageMultiplier", "Multiplier for all bullet damage", 1.0, 0.0, 20.0);
    public static final Opt<Double> MOB_DAMAGE_MUL = d(Side.SERVER, "damage", "mobDamageMultiplier", "Multiplier for damage dealt by armed mobs", 0.6, 0.0, 20.0);
    public static final Opt<Double> HEADSHOT_MUL = d(Side.SERVER, "damage", "headshotMultiplier", "Damage multiplier for headshots", 2.0, 1.0, 10.0);
    public static final Opt<Boolean> BREAK_GLASS = b(Side.SERVER, "world", "bulletsBreakGlass", "Bullets shatter glass and panes", true);
    public static final Opt<Boolean> EXPLOSION_BLOCKS = b(Side.SERVER, "world", "explosionsBreakBlocks", "Rocket explosions destroy blocks (still respects mobGriefing)", true);
    public static final Opt<Boolean> MERCENARIES = b(Side.SERVER, "world", "mercenarySpawns", "Armed mercenaries spawn at night", true);
    public static final Opt<Boolean> INFINITE_AMMO = b(Side.SERVER, "ammo", "infiniteAmmo", "Never consume ammo", false);
    public static final Opt<Boolean> CREATIVE_INFINITE = b(Side.SERVER, "ammo", "creativeInfiniteAmmo", "Creative players never consume ammo", true);
    public static final Opt<Boolean> ALL_TRACERS = b(Side.SERVER, "ammo", "allTracers", "Every round is a tracer", false);

    // ---- client ---------------------------------------------------------------------------------
    public static final Opt<Boolean> HUD = b(Side.CLIENT, "", "hud", "Show the ammo counter", true);
    public static final Opt<Boolean> CROSSHAIR = b(Side.CLIENT, "", "crosshair", "Dynamic spread crosshair while holding a gun", true);
    public static final Opt<Boolean> HIT_MARKERS = b(Side.CLIENT, "", "hitMarkers", "Hit and kill markers", true);
    public static final Opt<Double> SWAY = d(Side.CLIENT, "", "sway", "Weapon sway / inertia amount", 1.0, 0.0, 3.0);
    public static final Opt<Double> BOB = d(Side.CLIENT, "", "bob", "Extra weapon bob when walking", 1.0, 0.0, 3.0);
    public static final Opt<Double> CAMERA_RECOIL = d(Side.CLIENT, "", "cameraRecoil", "How much recoil kicks the camera", 1.0, 0.0, 3.0);
    public static final Opt<Double> CAMERA_MOTION = d(Side.CLIENT, "", "cameraMotion", "CS2-style camera motion during weapon animations (inspect, reload, draw, shots)", 1.0, 0.0, 2.0);
    public static final Opt<Double> ADS_SENSITIVITY = d(Side.CLIENT, "", "adsSensitivity", "Mouse sensitivity multiplier per zoom level while aiming through optics", 1.0, 0.1, 2.0);

    public static double damageMultiplier() { return DAMAGE_MUL.get(); }
    public static double mobDamageMultiplier() { return MOB_DAMAGE_MUL.get(); }
    public static double headshotMultiplier() { return HEADSHOT_MUL.get(); }
    public static boolean bulletsBreakGlass() { return BREAK_GLASS.get(); }
    public static boolean explosionsBreakBlocks() { return EXPLOSION_BLOCKS.get(); }
    public static boolean infiniteAmmo() { return INFINITE_AMMO.get(); }
    public static boolean creativeInfinite() { return CREATIVE_INFINITE.get(); }
    public static boolean allTracers() { return ALL_TRACERS.get(); }
    public static boolean mercenarySpawns() { return MERCENARIES.get(); }

    public static double client(Opt<Double> v, double def) {
        return v.get();
    }

    public static boolean client(Opt<Boolean> v, boolean def) {
        return v.get();
    }

    private CalibreConfig() {}
}
