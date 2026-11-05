package dev.calibre.neoforge;

import dev.calibre.CalibreConfig;
import net.neoforged.neoforge.common.ModConfigSpec;

import java.util.List;
import java.util.function.Supplier;

/** Builds NeoForge config specs from {@link CalibreConfig}'s option list and binds the options to them. */
final class NeoConfig {
    private static final java.util.Map<ModConfigSpec, java.util.List<Runnable>> SPECS = new java.util.IdentityHashMap<>();
    static final ModConfigSpec SERVER = build(CalibreConfig.SERVER);
    static final ModConfigSpec CLIENT = build(CalibreConfig.CLIENT);

    private NeoConfig() {}

    @SuppressWarnings("unchecked")
    private static ModConfigSpec build(List<CalibreConfig.Opt<?>> opts) {
        ModConfigSpec.Builder b = new ModConfigSpec.Builder();
        String section = "";
        java.util.List<Runnable> binds = new java.util.ArrayList<>();
        for (CalibreConfig.Opt<?> o : opts) {
            if (!o.section.equals(section)) {
                if (!section.isEmpty()) b.pop();
                if (!o.section.isEmpty()) b.push(o.section);
                section = o.section;
            }
            b.comment(o.comment);
            if (o.isBoolean()) {
                ModConfigSpec.BooleanValue v = b.define(o.name, ((Boolean) o.def).booleanValue());
                binds.add(() -> ((CalibreConfig.Opt<Boolean>) o).bind(guard(v)));
            } else {
                ModConfigSpec.DoubleValue v = b.defineInRange(o.name, ((Double) o.def).doubleValue(), o.min, o.max);
                binds.add(() -> ((CalibreConfig.Opt<Double>) o).bind(guard(v)));
            }
        }
        if (!section.isEmpty()) b.pop();
        ModConfigSpec spec = b.build();
        SPECS.put(spec, binds);
        return spec;
    }


    private static <T> Supplier<T> guard(ModConfigSpec.ConfigValue<T> v) {
        return v::get;
    }

    private static Supplier<Boolean> guard(ModConfigSpec.BooleanValue v) {
        // reading an unloaded spec throws; CalibreConfig.Opt falls back to the default then
        return v::get;
    }

    static void bindAll() {
        SPECS.values().forEach(l -> l.forEach(Runnable::run));
    }
}
