package dev.calibre.neoforge;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.calibre.gun.GunItem;
import dev.calibre.gun.GunState;
import it.unimi.dsi.fastutil.objects.ObjectArrayList;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.predicates.LootItemCondition;
import net.neoforged.neoforge.common.loot.IGlobalLootModifier;
import net.neoforged.neoforge.common.loot.LootModifier;

import java.util.List;
import dev.calibre.loot.CalibreLoot;

/** Adds weighted Calibre items to a loot table (guns spawn partially loaded). */
public class AddItemsModifier extends LootModifier {
    public static final MapCodec<AddItemsModifier> CODEC = RecordCodecBuilder.mapCodec(i -> codecStart(i).and(i.group(
            CalibreLoot.Entry.CODEC.listOf().fieldOf("entries").forGetter(m -> m.entries),
            Codec.FLOAT.optionalFieldOf("chance", 0.3f).forGetter(m -> m.chance),
            Codec.INT.optionalFieldOf("rolls", 1).forGetter(m -> m.rolls)
    )).apply(i, AddItemsModifier::new));

    private final List<CalibreLoot.Entry> entries;
    private final float chance;
    private final int rolls;

    public AddItemsModifier(LootItemCondition[] conditions, List<CalibreLoot.Entry> entries, float chance, int rolls) {
        super(conditions);
        this.entries = entries;
        this.chance = chance;
        this.rolls = rolls;
    }

    @Override
    protected ObjectArrayList<ItemStack> doApply(ObjectArrayList<ItemStack> loot, LootContext ctx) {
        CalibreLoot.roll(entries, chance, rolls, ctx.getRandom(), loot::add);
        return loot;
    }

    @Override
    public MapCodec<? extends IGlobalLootModifier> codec() {
        return CODEC;
    }
}
