package dev.calibre.fabric;

import dev.calibre.Calibre;
import dev.calibre.entity.MercenaryEntity;
import dev.calibre.loot.CalibreLoot;
import dev.calibre.network.Net;
import dev.calibre.registry.ModRegistry;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.levelgen.Heightmap;

import java.util.List;

/** Fabric entry point: wires the loader-neutral code in dev.calibre into Fabric API. */
public final class CalibreFabric implements ModInitializer {
    @Override
    public void onInitialize() {
        FabricConfig.load();
        Calibre.init();

        // networking (handlers run on the server thread)
        PayloadTypeRegistry.playC2S().register(Net.ShootPayload.TYPE, Net.ShootPayload.CODEC);
        PayloadTypeRegistry.playC2S().register(Net.RequestPayload.TYPE, Net.RequestPayload.CODEC);
        PayloadTypeRegistry.playS2C().register(Net.ActionPayload.TYPE, Net.ActionPayload.CODEC);
        PayloadTypeRegistry.playS2C().register(Net.HitPayload.TYPE, Net.HitPayload.CODEC);
        ServerPlayNetworking.registerGlobalReceiver(Net.ShootPayload.TYPE, (p, ctx) -> Net.onShoot(ctx.player(), p));
        ServerPlayNetworking.registerGlobalReceiver(Net.RequestPayload.TYPE, (p, ctx) -> Net.onRequest(ctx.player(), p));

        // the mercenary
        FabricDefaultAttributeRegistry.register(ModRegistry.MERCENARY.get(), MercenaryEntity.createAttributes());
        SpawnPlacements.register(ModRegistry.MERCENARY.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Calibre::mercenaryCanSpawn);
        BiomeModifications.addSpawn(BiomeSelectors.foundInOverworld(), MobCategory.MONSTER, ModRegistry.MERCENARY.get(), 5, 1, 3);

        // chest loot: the same pools the NeoForge global loot modifiers add
        List<CalibreLoot.Pool> pools = CalibreLoot.load();
        LootTableEvents.MODIFY_DROPS.register((entry, context, drops) -> entry.unwrapKey().ifPresent(key -> {
            Identifier id = key.identifier();
            for (CalibreLoot.Pool pool : pools)
                if (pool.tables().contains(id)) CalibreLoot.roll(pool.entries(), pool.chance(), pool.rolls(), context.getRandom(), drops::add);
        }));

        ServerTickEvents.END_SERVER_TICK.register(server -> server.getPlayerList().getPlayers().forEach(Calibre::playerTick));
        ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> Calibre.playerLogout(handler.player));
        Calibre.LOGGER.info("Calibre {} initialised on Fabric ({} guns)", "1.0.0", ModRegistry.GUNS.size());
    }
}
