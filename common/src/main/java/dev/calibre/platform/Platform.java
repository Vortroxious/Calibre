package dev.calibre.platform;

import net.minecraft.core.Registry;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerPlayer;

import java.nio.file.Path;
import java.util.ServiceLoader;
import java.util.function.Supplier;

/**
 * The few things NeoForge and Fabric do differently. Each loader module ships one implementation, found through
 * {@link ServiceLoader} (META-INF/services/dev.calibre.platform.Platform).
 */
public interface Platform {
    Platform INSTANCE = ServiceLoader.load(Platform.class, Platform.class.getClassLoader()).findFirst()
            .orElseThrow(() -> new IllegalStateException("No Calibre platform implementation on the classpath"));

    /** "neoforge" or "fabric" */
    String loader();

    /**
     * Registers an object. NeoForge defers the factory until its registry event; Fabric registers immediately.
     * The returned supplier is valid once registration has happened.
     */
    <T> Supplier<T> register(Registry<? super T> registry, String id, Supplier<T> factory);

    void sendToServer(CustomPacketPayload payload);

    void sendToPlayer(ServerPlayer player, CustomPacketPayload payload);

    /** false for fake / test players whose connection has no Calibre channel */
    boolean canReceive(ServerPlayer player, CustomPacketPayload.Type<?> type);

    Path configDir();
}
