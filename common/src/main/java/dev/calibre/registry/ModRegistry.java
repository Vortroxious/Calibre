package dev.calibre.registry;

import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import dev.calibre.Calibre;
import dev.calibre.attachment.AttachmentItem;
import dev.calibre.ballistics.BulletEntity;
import dev.calibre.ballistics.RocketEntity;
import dev.calibre.entity.MercenaryEntity;
import dev.calibre.gun.AmmoItem;
import dev.calibre.gun.Attachment;
import dev.calibre.gun.Caliber;
import dev.calibre.gun.GunAttachments;
import dev.calibre.gun.GunDefinition;
import dev.calibre.gun.GunItem;
import dev.calibre.gun.GunState;
import dev.calibre.gun.Guns;
import dev.calibre.platform.Platform;
import dev.calibre.workbench.GunWorkbenchBlock;
import dev.calibre.workbench.GunWorkbenchMenu;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.function.UnaryOperator;

public final class ModRegistry {
    private static final Platform P = Platform.INSTANCE;

    private static <T> Supplier<T> reg(net.minecraft.core.Registry<? super T> r, String id, Supplier<T> f) {
        return P.register(r, id, f);
    }

    private static <T> ResourceKey<T> key(ResourceKey<? extends net.minecraft.core.Registry<T>> registry, String id) {
        return ResourceKey.create(registry, Calibre.id(id));
    }

    private static <I extends Item> Supplier<I> item(String id, Function<Item.Properties, I> ctor, UnaryOperator<Item.Properties> props) {
        return reg(BuiltInRegistries.ITEM, id, () -> ctor.apply(props.apply(new Item.Properties().setId(key(Registries.ITEM, id)))));
    }

    private static <T> Supplier<DataComponentType<T>> component(String id, UnaryOperator<DataComponentType.Builder<T>> b) {
        return reg(BuiltInRegistries.DATA_COMPONENT_TYPE, id, () -> b.apply(DataComponentType.builder()).build());
    }

    private static <E extends Entity> Supplier<EntityType<E>> entity(String id, EntityType.EntityFactory<E> f, MobCategory cat,
                                                                    UnaryOperator<EntityType.Builder<E>> b) {
        return reg(BuiltInRegistries.ENTITY_TYPE, id, () -> b.apply(EntityType.Builder.of(f, cat)).build(key(Registries.ENTITY_TYPE, id)));
    }

    // ---- components -----------------------------------------------------------------------------
    public static final Supplier<DataComponentType<GunState>> GUN_STATE =
            component("gun_state", b -> b.persistent(GunState.CODEC).networkSynchronized(GunState.STREAM_CODEC).ignoreSwapAnimation());
    public static final Supplier<DataComponentType<GunAttachments>> GUN_ATTACHMENTS =
            component("gun_attachments", b -> b.persistent(GunAttachments.CODEC).networkSynchronized(GunAttachments.STREAM_CODEC)
                    .ignoreSwapAnimation());

    // ---- items ----------------------------------------------------------------------------------
    public static final Map<String, Supplier<GunItem>> GUNS = new LinkedHashMap<>();
    public static final Map<Caliber, Supplier<AmmoItem>> AMMO = new EnumMap<>(Caliber.class);
    public static final Map<Attachment, Supplier<AttachmentItem>> ATTACHMENTS = new EnumMap<>(Attachment.class);

    static {
        for (GunDefinition def : Guns.all()) {
            GUNS.put(def.id(), item(def.id(), p -> new GunItem(p, def), p -> p.stacksTo(1)
                    .component(GUN_STATE.get(), GunState.full(def))
                    .component(GUN_ATTACHMENTS.get(), GunAttachments.NONE)));
        }
        for (Caliber c : Caliber.values()) {
            int stack = c == Caliber.PG7 ? 4 : (c == Caliber.BMG50 || c == Caliber.WM300 ? 32 : 64);
            AMMO.put(c, item(c.ammoItemId(), p -> new AmmoItem(p, c), p -> p.stacksTo(stack)));
        }
        for (Attachment a : Attachment.values()) {
            ATTACHMENTS.put(a, item(a.id(), p -> new AttachmentItem(p, a), p -> p.stacksTo(1)));
        }
    }

    // ---- workbench ------------------------------------------------------------------------------
    public static final Supplier<GunWorkbenchBlock> WORKBENCH = reg(BuiltInRegistries.BLOCK, "gun_workbench",
            () -> new GunWorkbenchBlock(BlockBehaviour.Properties.of().mapColor(MapColor.METAL).strength(3.5f).sound(SoundType.METAL)
                    .noOcclusion().requiresCorrectToolForDrops().setId(key(Registries.BLOCK, "gun_workbench"))));
    public static final Supplier<BlockItem> WORKBENCH_ITEM = item("gun_workbench", p -> new BlockItem(WORKBENCH.get(), p),
            Item.Properties::useBlockDescriptionPrefix);
    public static final Supplier<MenuType<GunWorkbenchMenu>> WORKBENCH_MENU = reg(BuiltInRegistries.MENU, "gun_workbench",
            () -> new MenuType<>(GunWorkbenchMenu::new, FeatureFlags.VANILLA_SET));

    // ---- entities -------------------------------------------------------------------------------
    public static final Supplier<EntityType<BulletEntity>> BULLET = entity("bullet", BulletEntity::new, MobCategory.MISC,
            b -> b.sized(0.1f, 0.1f).clientTrackingRange(16).updateInterval(1).noSave());
    public static final Supplier<EntityType<RocketEntity>> ROCKET = entity("rocket", RocketEntity::new, MobCategory.MISC,
            b -> b.sized(0.3f, 0.3f).clientTrackingRange(16).updateInterval(1));
    public static final Supplier<EntityType<MercenaryEntity>> MERCENARY = entity("mercenary", MercenaryEntity::new, MobCategory.MONSTER,
            b -> b.sized(0.6f, 1.95f).eyeHeight(1.62f).clientTrackingRange(10));

    // ---- damage ---------------------------------------------------------------------------------
    public static final ResourceKey<DamageType> BULLET_DAMAGE = ResourceKey.create(Registries.DAMAGE_TYPE, Calibre.id("bullet"));
    public static final ResourceKey<DamageType> BULLET_HEADSHOT = ResourceKey.create(Registries.DAMAGE_TYPE, Calibre.id("bullet_headshot"));

    // ---- sounds (names generated by tools/gen_sounds.py) ----------------------------------------
    public static final Map<String, Supplier<SoundEvent>> SOUND_EVENTS = new LinkedHashMap<>();

    static {
        try (var in = ModRegistry.class.getResourceAsStream("/calibre_gen/sounds.json")) {
            JsonArray names = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonArray();
            for (var e : names) {
                String n = e.getAsString();
                SOUND_EVENTS.put(n, reg(BuiltInRegistries.SOUND_EVENT, n, () -> SoundEvent.createVariableRangeEvent(Calibre.id(n))));
            }
        } catch (Exception ex) {
            throw new IllegalStateException("calibre_gen/sounds.json missing - run tools/gen_sounds.py", ex);
        }
    }

    public static SoundEvent sound(String name) {
        var h = SOUND_EVENTS.get(name);
        return h == null ? null : h.get();
    }

    // ---- creative tabs --------------------------------------------------------------------------
    public static final Supplier<CreativeModeTab> TAB_GUNS = reg(BuiltInRegistries.CREATIVE_MODE_TAB, "guns", () -> CreativeModeTab.builder(CreativeModeTab.Row.TOP, 0)
            .title(Component.translatable("itemGroup.calibre.guns"))
            .icon(() -> new ItemStack(GUNS.get("m4a1").get()))
            .displayItems((params, out) -> GUNS.values().forEach(g -> out.accept(g.get())))
            .build());
    public static final Supplier<CreativeModeTab> TAB_GEAR = reg(BuiltInRegistries.CREATIVE_MODE_TAB, "gear", () -> CreativeModeTab.builder(CreativeModeTab.Row.TOP, 1)
            .title(Component.translatable("itemGroup.calibre.gear"))
            .icon(() -> new ItemStack(ATTACHMENTS.get(Attachment.ACOG).get()))
            .displayItems((params, out) -> {
                out.accept(WORKBENCH_ITEM.get());
                AMMO.values().forEach(a -> out.accept(a.get()));
                ATTACHMENTS.values().forEach(a -> out.accept(a.get()));
            })
            .build());

    private ModRegistry() {}

    /** Forces class initialisation, i.e. every entry above is handed to the platform's registry. */
    public static void init() {}

    public static Supplier<Item> gun(String id) {
        return () -> GUNS.get(id).get();
    }
}
