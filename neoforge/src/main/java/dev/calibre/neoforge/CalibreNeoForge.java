package dev.calibre.neoforge;

import com.mojang.serialization.MapCodec;
import dev.calibre.Calibre;
import dev.calibre.entity.MercenaryEntity;
import dev.calibre.network.Net;
import dev.calibre.registry.ModRegistry;
import dev.calibre.test.CalibreGameTests;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.FunctionGameTestInstance;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.gametest.framework.TestData;
import net.minecraft.gametest.framework.TestEnvironmentDefinition;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.loot.IGlobalLootModifier;
import net.neoforged.neoforge.event.RegisterGameTestsEvent;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.RegisterSpawnPlacementsEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

import java.util.function.Consumer;

/** NeoForge entry point: wires the loader-neutral code in dev.calibre into NeoForge's buses. */
@Mod(Calibre.MODID)
public class CalibreNeoForge {
    private static final DeferredRegister<MapCodec<? extends IGlobalLootModifier>> LOOT_MODIFIERS =
            DeferredRegister.create(NeoForgeRegistries.Keys.GLOBAL_LOOT_MODIFIER_SERIALIZERS, Calibre.MODID);

    static {
        LOOT_MODIFIERS.register("add_items", () -> AddItemsModifier.CODEC);
    }

    public CalibreNeoForge(IEventBus modBus, ModContainer container) {
        Calibre.init();
        CalibreGameTests.registerFunctions();
        NeoPlatform.registerAll(modBus);
        LOOT_MODIFIERS.register(modBus);
        container.registerConfig(ModConfig.Type.SERVER, NeoConfig.SERVER);
        container.registerConfig(ModConfig.Type.CLIENT, NeoConfig.CLIENT);
        NeoConfig.bindAll();
        modBus.addListener(CalibreNeoForge::payloads);
        modBus.addListener(CalibreNeoForge::attributes);
        modBus.addListener(CalibreNeoForge::spawnPlacements);
        modBus.addListener(CalibreNeoForge::gameTests);
        NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post e) -> {
            if (e.getEntity() instanceof ServerPlayer sp) Calibre.playerTick(sp);
        });
        NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> Calibre.playerLogout(e.getEntity()));
    }

    private static void payloads(RegisterPayloadHandlersEvent event) {
        PayloadRegistrar r = event.registrar("1");
        r.playToServer(Net.ShootPayload.TYPE, Net.ShootPayload.CODEC, (p, ctx) -> Net.onShoot((ServerPlayer) ctx.player(), p));
        r.playToServer(Net.RequestPayload.TYPE, Net.RequestPayload.CODEC, (p, ctx) -> Net.onRequest((ServerPlayer) ctx.player(), p));
        r.playToClient(Net.ActionPayload.TYPE, Net.ActionPayload.CODEC, (p, ctx) -> Net.CLIENT.onAction(p));
        r.playToClient(Net.HitPayload.TYPE, Net.HitPayload.CODEC, (p, ctx) -> Net.CLIENT.onHit(p));
    }

    private static void attributes(EntityAttributeCreationEvent e) {
        e.put(ModRegistry.MERCENARY.get(), MercenaryEntity.createAttributes().build());
    }

    private static void spawnPlacements(RegisterSpawnPlacementsEvent e) {
        e.register(ModRegistry.MERCENARY.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Calibre::mercenaryCanSpawn, RegisterSpawnPlacementsEvent.Operation.REPLACE);
    }

    private static void gameTests(RegisterGameTestsEvent event) {
        Holder<TestEnvironmentDefinition> env = event.registerEnvironment(Calibre.id("default"));
        for (String name : CalibreGameTests.TESTS.keySet()) {
            ResourceKey<Consumer<GameTestHelper>> fn = ResourceKey.create(Registries.TEST_FUNCTION, Calibre.id(name));
            event.registerTest(Calibre.id(name), new FunctionGameTestInstance(fn,
                    new TestData<>(env, Calibre.id("range"), 200, 0, true)));
        }
    }
}
