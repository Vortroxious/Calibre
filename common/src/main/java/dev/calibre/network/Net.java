package dev.calibre.network;

import dev.calibre.Calibre;
import dev.calibre.gun.GunLogic;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerPlayer;

/** All Calibre packets. */
public final class Net {
    /** Client-side receiver, installed by the client setup so this class never references client code. */
    public interface ClientSink {
        void onAction(ActionPayload p);

        void onHit(HitPayload p);
    }

    public static ClientSink CLIENT = new ClientSink() {
        public void onAction(ActionPayload p) {}

        public void onHit(HitPayload p) {}
    };

    // ---- C2S -------------------------------------------------------------------------------------
    /** One shot. yaw/pitch is the shooter's view when the client fired (clamped against the server's view). */
    public record ShootPayload(float yaw, float pitch, boolean aiming, int seq) implements CustomPacketPayload {
        public static final Type<ShootPayload> TYPE = new Type<>(Calibre.id("shoot"));
        public static final StreamCodec<ByteBuf, ShootPayload> CODEC = StreamCodec.composite(
                ByteBufCodecs.FLOAT, ShootPayload::yaw, ByteBufCodecs.FLOAT, ShootPayload::pitch,
                ByteBufCodecs.BOOL, ShootPayload::aiming, ByteBufCodecs.VAR_INT, ShootPayload::seq, ShootPayload::new);

        @Override
        public Type<? extends CustomPacketPayload> type() {
            return TYPE;
        }
    }

    public enum Request { RELOAD, FIRE_MODE, INSPECT, AIM_ON, AIM_OFF, INTERRUPT, DRAW }

    public record RequestPayload(Request request) implements CustomPacketPayload {
        public static final Type<RequestPayload> TYPE = new Type<>(Calibre.id("request"));
        public static final StreamCodec<ByteBuf, RequestPayload> CODEC = ByteBufCodecs.VAR_INT
                .map(i -> new RequestPayload(Request.values()[Math.floorMod(i, Request.values().length)]), p -> p.request.ordinal());

        @Override
        public Type<? extends CustomPacketPayload> type() {
            return TYPE;
        }
    }

    // ---- S2C -------------------------------------------------------------------------------------
    /** Play animation `anim` (+ its foley) on the gun held by entity `entityId`. */
    public record ActionPayload(int entityId, String anim, boolean shot) implements CustomPacketPayload {
        public static final Type<ActionPayload> TYPE = new Type<>(Calibre.id("action"));
        public static final StreamCodec<ByteBuf, ActionPayload> CODEC = StreamCodec.composite(
                ByteBufCodecs.VAR_INT, ActionPayload::entityId, ByteBufCodecs.STRING_UTF8, ActionPayload::anim,
                ByteBufCodecs.BOOL, ActionPayload::shot, ActionPayload::new);

        @Override
        public Type<? extends CustomPacketPayload> type() {
            return TYPE;
        }
    }

    public record HitPayload(int kind) implements CustomPacketPayload {
        public static final int HIT = 0, HEADSHOT = 1, KILL = 2;
        public static final Type<HitPayload> TYPE = new Type<>(Calibre.id("hit"));
        public static final StreamCodec<ByteBuf, HitPayload> CODEC = ByteBufCodecs.VAR_INT.map(HitPayload::new, HitPayload::kind);

        @Override
        public Type<? extends CustomPacketPayload> type() {
            return TYPE;
        }
    }

    // ---- handlers (each loader registers the codecs above and routes packets here, on the game thread) --
    public static void onShoot(ServerPlayer player, ShootPayload p) {
        GunLogic.onShoot(player, p);
    }

    public static void onRequest(ServerPlayer player, RequestPayload p) {
        GunLogic.onRequest(player, p.request());
    }

    @SuppressWarnings("unused")
    private static StreamCodec<RegistryFriendlyByteBuf, ?> unused() {
        return null;
    }

    private Net() {}
}
