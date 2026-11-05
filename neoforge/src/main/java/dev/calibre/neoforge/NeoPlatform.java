package dev.calibre.neoforge;

import dev.calibre.Calibre;
import dev.calibre.platform.Platform;
import net.minecraft.core.Registry;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.client.network.ClientPacketDistributor;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Supplier;

public final class NeoPlatform implements Platform {
    private static final Map<ResourceKey<?>, DeferredRegister<?>> REGISTERS = new LinkedHashMap<>();

    @Override
    public String loader() {
        return "neoforge";
    }

    @Override
    @SuppressWarnings({"unchecked", "rawtypes"})
    public <T> Supplier<T> register(Registry<? super T> registry, String id, Supplier<T> factory) {
        DeferredRegister dr = REGISTERS.computeIfAbsent(registry.key(), k -> DeferredRegister.create((Registry) registry, Calibre.MODID));
        return (Supplier<T>) dr.register(id, factory);
    }

    /** Attaches every DeferredRegister created so far to the mod bus. */
    static void registerAll(IEventBus modBus) {
        REGISTERS.values().forEach(r -> r.register(modBus));
    }

    @Override
    public void sendToServer(CustomPacketPayload payload) {
        ClientPacketDistributor.sendToServer(payload);
    }

    @Override
    public void sendToPlayer(ServerPlayer player, CustomPacketPayload payload) {
        PacketDistributor.sendToPlayer(player, payload);
    }

    @Override
    public boolean canReceive(ServerPlayer player, CustomPacketPayload.Type<?> type) {
        return player.connection != null && player.connection.hasChannel(type);
    }

    @Override
    public Path configDir() {
        return FMLPaths.CONFIGDIR.get();
    }
}
