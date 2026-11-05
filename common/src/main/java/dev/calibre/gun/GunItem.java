package dev.calibre.gun;

import dev.calibre.Calibre;
import dev.calibre.registry.ModRegistry;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.core.BlockPos;
import org.jspecify.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.client.GeoRenderProvider;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animatable.manager.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.Locale;
import java.util.function.Consumer;

public class GunItem extends Item implements GeoItem {
    public static final String CONTROLLER = "main";
    /** Set by Calibre's client setup: supplies the GeckoLib renderer without touching client classes here. */
    public static Consumer<Consumer<GeoRenderProvider>> RENDER_PROVIDER_FACTORY = c -> {};
    public static java.util.function.Function<GunItem, GeoRenderProvider> RENDERER = g -> GeoRenderProvider.DEFAULT;

    private final GunDefinition def;
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public GunItem(Properties props, GunDefinition def) {
        super(props);
        this.def = def;
    }

    public GunDefinition def() {
        return def;
    }

    public GunMeta meta() {
        return GunMeta.get(def.id());
    }

    public String anim(String name) {
        return "animation." + def.id() + "." + name;
    }

    // ---- state helpers ---------------------------------------------------------------------------
    public static GunState state(ItemStack stack) {
        GunState s = stack.get(ModRegistry.GUN_STATE.get());
        return s == null ? GunState.EMPTY : s;
    }

    public static void setState(ItemStack stack, GunState state) {
        stack.set(ModRegistry.GUN_STATE.get(), state);
    }

    public static GunAttachments attachments(ItemStack stack) {
        GunAttachments a = stack.get(ModRegistry.GUN_ATTACHMENTS.get());
        return a == null ? GunAttachments.NONE : a;
    }

    public GunDefinition.FireMode mode(ItemStack stack) {
        int m = state(stack).mode();
        return def.modes().get(Math.floorMod(m, def.modes().size()));
    }

    // ---- GeckoLib --------------------------------------------------------------------------------
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        final RawAnimation idle = RawAnimation.begin().thenLoop(anim("idle"));
        final RawAnimation idleEmpty = meta().has("idle_empty") ? RawAnimation.begin().thenLoop(anim("idle_empty")) : idle;
        AnimationController<GunItem> main = new AnimationController<>(CONTROLLER, 1, test -> {
            Boolean empty = test.getData(CalibreTickets.EMPTY);
            return test.setAndContinue(Boolean.TRUE.equals(empty) ? idleEmpty : idle);
        });
        for (String action : meta().actions.keySet()) {
            if (action.startsWith("idle")) continue;
            if (action.equals("reload_loop")) {
                main.triggerableAnim(action, RawAnimation.begin().thenPlay(anim(action)));
            } else if (action.startsWith("reload_start")) {
                main.triggerableAnim(action, RawAnimation.begin().thenPlayAndHold(anim(action)));
            } else {
                main.triggerableAnim(action, RawAnimation.begin().thenPlay(anim(action)));
            }
        }
        controllers.add(main);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    @Override
    public void createGeoRenderer(Consumer<GeoRenderProvider> consumer) {
        consumer.accept(RENDERER.apply(this));
    }

    // ---- vanilla behaviour -----------------------------------------------------------------------
    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        return InteractionResult.FAIL; // right click = aim, handled by the client controller
    }

    @Override
    public boolean canDestroyBlock(ItemStack stack, BlockState state, Level level, BlockPos pos, LivingEntity entity) {
        return false;
    }

    // NeoForge picks these two up through IItemExtension; on Fabric mixins call them. No @Override so both compile.
    public boolean onEntitySwing(ItemStack stack, LivingEntity entity, InteractionHand hand) {
        return true; // no arm swing
    }

    public boolean shouldCauseReequipAnimation(ItemStack oldStack, ItemStack newStack, boolean slotChanged) {
        return slotChanged || oldStack.getItem() != newStack.getItem();
    }

    @Override
    public void inventoryTick(ItemStack stack, ServerLevel level, Entity entity, @Nullable EquipmentSlot slot) {
        if (slot == EquipmentSlot.MAINHAND) GeoItem.getOrAssignId(stack, level);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> tip, TooltipFlag flag) {
        GunState s = state(stack);
        GunAttachments att = attachments(stack);
        tip.accept(Component.translatable("tooltip.calibre.caliber", def.caliber().displayName).withStyle(ChatFormatting.GRAY));
        tip.accept(Component.translatable("tooltip.calibre.ammo", s.total(), def.capacity(att)).withStyle(ChatFormatting.GRAY));
        StringBuilder modes = new StringBuilder();
        for (GunDefinition.FireMode m : def.modes()) {
            if (!modes.isEmpty()) modes.append(" / ");
            modes.append(m.name().charAt(0)).append(m.name().substring(1).toLowerCase(Locale.ROOT));
        }
        tip.accept(Component.translatable("tooltip.calibre.modes", modes.toString(), def.rpm()).withStyle(ChatFormatting.DARK_GRAY));
        tip.accept(Component.translatable("tooltip.calibre.weight", String.format(Locale.ROOT, "%.1f", def.weightKg()))
                .withStyle(ChatFormatting.DARK_GRAY));
        for (Attachment a : att.all())
            tip.accept(Component.literal(" + ").append(Component.translatable("item.calibre." + a.id())).withStyle(ChatFormatting.DARK_AQUA));
        if (!def.attachments().isEmpty() && att.isEmpty())
            tip.accept(Component.translatable("tooltip.calibre.attachable").withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
    }

    public static boolean isGun(ItemStack stack) {
        return stack.getItem() instanceof GunItem;
    }

    @Override
    public String toString() {
        return Calibre.MODID + ":" + def.id();
    }
}
