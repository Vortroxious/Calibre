package dev.calibre.gun;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;

/**
 * Per-stack gun state.
 * @param ammo      rounds in the magazine / tube / belt / cylinder
 * @param chambered a round is in the chamber (closed bolt, bolt and pump guns)
 * @param mode      index into {@link GunDefinition#modes()}
 */
public record GunState(int ammo, boolean chambered, int mode) {
    public static final GunState EMPTY = new GunState(0, false, 0);

    public static final Codec<GunState> CODEC = RecordCodecBuilder.create(i -> i.group(
            Codec.INT.optionalFieldOf("ammo", 0).forGetter(GunState::ammo),
            Codec.BOOL.optionalFieldOf("chambered", false).forGetter(GunState::chambered),
            Codec.INT.optionalFieldOf("mode", 0).forGetter(GunState::mode)
    ).apply(i, GunState::new));

    public static final StreamCodec<ByteBuf, GunState> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.VAR_INT, GunState::ammo,
            ByteBufCodecs.BOOL, GunState::chambered,
            ByteBufCodecs.VAR_INT, GunState::mode,
            GunState::new);

    public int total() {
        return ammo + (chambered ? 1 : 0);
    }

    public GunState withAmmo(int a) {
        return new GunState(a, chambered, mode);
    }

    public GunState withChambered(boolean c) {
        return new GunState(ammo, c, mode);
    }

    public GunState withMode(int m) {
        return new GunState(ammo, chambered, m);
    }

    /** A freshly crafted / spawned gun comes fully loaded. */
    public static GunState full(GunDefinition def) {
        boolean ch = def.cycle().hasChamber();
        return new GunState(def.magSize(), ch, 0);
    }
}
