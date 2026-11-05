package dev.calibre.gun;

import com.mojang.serialization.Codec;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/** Installed attachments, one per slot. Immutable. */
public final class GunAttachments {
    public static final GunAttachments NONE = new GunAttachments(new EnumMap<>(Attachment.Slot.class));

    public static final Codec<GunAttachments> CODEC = Codec.STRING.listOf().xmap(GunAttachments::fromIds, GunAttachments::ids);
    public static final StreamCodec<ByteBuf, GunAttachments> STREAM_CODEC =
            ByteBufCodecs.STRING_UTF8.apply(ByteBufCodecs.list()).map(GunAttachments::fromIds, GunAttachments::ids);

    private final EnumMap<Attachment.Slot, Attachment> map;

    private GunAttachments(EnumMap<Attachment.Slot, Attachment> map) {
        this.map = map;
    }

    public Attachment get(Attachment.Slot slot) {
        return map.get(slot);
    }

    public boolean has(Attachment a) {
        return map.get(a.slot) == a;
    }

    public GunAttachments with(Attachment a) {
        EnumMap<Attachment.Slot, Attachment> m = new EnumMap<>(Attachment.Slot.class);
        m.putAll(map);
        m.put(a.slot, a);
        return new GunAttachments(m);
    }

    public GunAttachments without(Attachment.Slot slot) {
        EnumMap<Attachment.Slot, Attachment> m = new EnumMap<>(Attachment.Slot.class);
        m.putAll(map);
        m.remove(slot);
        return new GunAttachments(m);
    }

    public Iterable<Attachment> all() {
        return map.values();
    }

    public boolean isEmpty() {
        return map.isEmpty();
    }

    public boolean suppressed() {
        for (Attachment a : map.values()) if (a.suppressed) return true;
        return false;
    }

    public float product(java.util.function.ToDoubleFunction<Attachment> f) {
        double v = 1;
        for (Attachment a : map.values()) v *= f.applyAsDouble(a);
        return (float) v;
    }

    private List<String> ids() {
        List<String> out = new ArrayList<>();
        for (Attachment a : map.values()) out.add(a.id());
        return out;
    }

    private static GunAttachments fromIds(List<String> ids) {
        EnumMap<Attachment.Slot, Attachment> m = new EnumMap<>(Attachment.Slot.class);
        for (String id : ids) {
            Attachment a = Attachment.byId(id);
            if (a != null) m.put(a.slot, a);
        }
        return m.isEmpty() ? NONE : new GunAttachments(m);
    }

    @Override
    public boolean equals(Object o) {
        return o instanceof GunAttachments other && other.map.equals(map);
    }

    @Override
    public int hashCode() {
        return map.hashCode();
    }

    public Map<Attachment.Slot, Attachment> asMap() {
        return java.util.Collections.unmodifiableMap(map);
    }
}
