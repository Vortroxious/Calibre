package dev.calibre.attachment;

import dev.calibre.gun.Attachment;
import dev.calibre.gun.GunDefinition;
import dev.calibre.gun.Guns;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.client.GeoRenderProvider;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animatable.manager.AnimatableManager;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.Locale;
import java.util.function.Consumer;
import java.util.function.Function;

/** An attachment as an item. Rendered in 3D by GeckoLib using the same model that is mounted on the gun. */
public class AttachmentItem extends Item implements GeoItem {
    public static Function<AttachmentItem, GeoRenderProvider> RENDERER = a -> GeoRenderProvider.DEFAULT;
    private final Attachment attachment;
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public AttachmentItem(Properties props, Attachment attachment) {
        super(props);
        this.attachment = attachment;
    }

    public Attachment attachment() {
        return attachment;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {}

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    @Override
    public void createGeoRenderer(Consumer<GeoRenderProvider> consumer) {
        consumer.accept(RENDERER.apply(this));
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> tip, TooltipFlag flag) {
        tip.accept(Component.translatable("tooltip.calibre.slot." + attachment.slot.name().toLowerCase(Locale.ROOT))
                .withStyle(ChatFormatting.GRAY));
        line(tip, "recoil", attachment.recoil, true);
        line(tip, "hip_spread", attachment.hipSpread, true);
        line(tip, "ads_spread", attachment.adsSpread, true);
        line(tip, "ads_time", attachment.adsTime, true);
        if (attachment.zoom > 1.01f) tip.accept(Component.translatable("tooltip.calibre.zoom",
                String.format(Locale.ROOT, "%.1f", attachment.zoom)).withStyle(ChatFormatting.BLUE));
        if (attachment.suppressed) tip.accept(Component.translatable("tooltip.calibre.suppressed").withStyle(ChatFormatting.BLUE));
        if (attachment.magMul > 1.01f) tip.accept(Component.translatable("tooltip.calibre.mag",
                Math.round((attachment.magMul - 1) * 100)).withStyle(ChatFormatting.BLUE));
        int n = 0;
        for (GunDefinition g : Guns.all()) if (g.allows(attachment)) n++;
        tip.accept(Component.translatable("tooltip.calibre.fits", n).withStyle(ChatFormatting.DARK_GRAY));
    }

    private static void line(Consumer<Component> tip, String key, float mul, boolean lowerIsBetter) {
        if (Math.abs(mul - 1) < 0.005f) return;
        int pct = Math.round((mul - 1) * 100);
        boolean good = lowerIsBetter ? pct < 0 : pct > 0;
        tip.accept(Component.translatable("tooltip.calibre.stat." + key, (pct > 0 ? "+" : "") + pct + "%")
                .withStyle(good ? ChatFormatting.GREEN : ChatFormatting.RED));
    }
}
