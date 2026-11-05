package dev.calibre.fabric;

import dev.calibre.CalibreConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.OptionInstance;
import net.minecraft.client.Options;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.options.OptionsSubScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Settings screen (opened from Mod Menu) built on vanilla's scrolling options list, so it fits at any GUI scale and needs
 * no extra library. Values are written to config/calibre-*.json when the screen closes.
 */
public final class CalibreConfigScreen extends OptionsSubScreen {
    public CalibreConfigScreen(Screen parent) {
        super(parent, Minecraft.getInstance().options, Component.translatable("config.calibre.title"));
    }

    @Override
    protected void addOptions() {
        this.list.addHeader(Component.translatable("config.calibre.server"));
        this.list.addSmall(instances(CalibreConfig.SERVER));
        this.list.addHeader(Component.translatable("config.calibre.client"));
        this.list.addSmall(instances(CalibreConfig.CLIENT));
    }

    @Override
    protected void repositionElements() {
        super.repositionElements();
        // automated screenshots show the client options (camera recoil / motion), not just the world rules
        if (Boolean.getBoolean("calibre.autotest") && this.list != null) this.list.setScrollAmount(this.list.maxScrollAmount());
    }

    @SuppressWarnings("unchecked")
    private static OptionInstance<?>[] instances(List<CalibreConfig.Opt<?>> opts) {
        List<OptionInstance<?>> out = new ArrayList<>();
        for (CalibreConfig.Opt<?> o : opts) {
            String key = "config.calibre." + o.name;
            OptionInstance.TooltipSupplier<Object> tip = OptionInstance.cachedConstantTooltip(Component.literal(o.comment));
            if (o.isBoolean()) {
                out.add(OptionInstance.createBoolean(key, v -> tip.apply(v), (Boolean) FabricConfig.get(o), v -> FabricConfig.set(o, v)));
            } else {
                CalibreConfig.Opt<Double> d = (CalibreConfig.Opt<Double>) o;
                out.add(new OptionInstance<>(key, v -> tip.apply(v),
                        (caption, v) -> Options.genericValueLabel(caption, Component.literal(String.format(Locale.ROOT, "%.2f", v))),
                        OptionInstance.UnitDouble.INSTANCE.xmap(u -> Math.round(Mth.lerp(u, d.min, d.max) * 20) / 20.0,
                                v -> (v - d.min) / (d.max - d.min)),
                        (Double) FabricConfig.get(o), v -> FabricConfig.set(o, v)));
            }
        }
        return out.toArray(OptionInstance[]::new);
    }

    @Override
    public void onClose() {
        FabricConfig.save();
        super.onClose();
    }
}
