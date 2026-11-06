package dev.calibre.workbench;

import dev.calibre.gun.Attachment;
import dev.calibre.gun.Caliber;
import dev.calibre.gun.GunDefinition;
import dev.calibre.gun.Guns;
import dev.calibre.registry.ModRegistry;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * The gunsmithing recipe book. Defined in code (identical on client and server, no recipe sync needed) and crafted
 * at the Gun Workbench straight from the player's inventory.
 */
public final class GunsmithingRecipes {
    public enum Tab { GUNS, AMMO, ATTACHMENTS }

    public record Ingredient(Supplier<Item> item, int count) {}

    public record Recipe(Tab tab, Supplier<Item> result, int count, List<Ingredient> ingredients) {
        public ItemStack resultStack() {
            return new ItemStack(result.get(), count);
        }

        public boolean canCraft(Player p) {
            if (p.getAbilities().instabuild) return true;
            for (Ingredient in : ingredients) if (GunsmithingRecipes.count(p, in.item.get()) < in.count) return false;
            return true;
        }

        public void consume(Player p) {
            if (p.getAbilities().instabuild) return;
            for (Ingredient in : ingredients) {
                int need = in.count;
                var inv = p.getInventory();
                for (int i = 0; i < inv.getContainerSize() && need > 0; i++) {
                    ItemStack st = inv.getItem(i);
                    if (st.is(in.item.get())) {
                        int n = Math.min(need, st.getCount());
                        st.shrink(n);
                        need -= n;
                    }
                }
            }
        }
    }

    public static int count(Player p, Item item) {
        int n = 0;
        for (ItemStack st : p.getInventory()) if (st.is(item)) n += st.getCount();
        return n;
    }

    private static final List<Recipe> ALL = new ArrayList<>();

    private static Ingredient in(Item item, int n) {
        return new Ingredient(() -> item, n);
    }

    private static void gun(String id, Ingredient... ins) {
        ALL.add(new Recipe(Tab.GUNS, ModRegistry.gun(id), 1, List.of(ins)));
    }

    private static void ammo(Caliber c, int count, Ingredient... ins) {
        ALL.add(new Recipe(Tab.AMMO, () -> ModRegistry.AMMO.get(c).get(), count, List.of(ins)));
    }

    private static void att(Attachment a, Ingredient... ins) {
        ALL.add(new Recipe(Tab.ATTACHMENTS, () -> ModRegistry.ATTACHMENTS.get(a).get(), 1, List.of(ins)));
    }

    static {
        // guns: iron for steel parts, copper for springs/pins, redstone for the trigger group, wood/leather/dye for furniture
        Ingredient pistol = in(Items.REDSTONE, 2);
        gun("glock17", in(Items.IRON_INGOT, 4), in(Items.BLACK_DYE, 2), in(Items.COPPER_INGOT, 2), pistol);
        gun("m1911", in(Items.IRON_INGOT, 6), in(Items.DARK_OAK_PLANKS, 2), in(Items.COPPER_INGOT, 2), pistol);
        gun("m9", in(Items.IRON_INGOT, 5), in(Items.BLACK_DYE, 1), in(Items.COPPER_INGOT, 2), pistol);
        gun("deagle", in(Items.IRON_INGOT, 10), in(Items.IRON_BLOCK, 1), in(Items.COPPER_INGOT, 3), pistol);
        gun("model29", in(Items.IRON_INGOT, 9), in(Items.SPRUCE_PLANKS, 2), in(Items.COPPER_INGOT, 3), pistol);
        Ingredient trig = in(Items.REDSTONE, 4);
        gun("mp5", in(Items.IRON_INGOT, 12), in(Items.BLACK_DYE, 3), in(Items.COPPER_INGOT, 4), trig);
        gun("ump45", in(Items.IRON_INGOT, 9), in(Items.BLACK_DYE, 6), in(Items.COPPER_INGOT, 4), trig);
        gun("uzi", in(Items.IRON_INGOT, 14), in(Items.COPPER_INGOT, 3), trig);
        gun("p90", in(Items.IRON_INGOT, 8), in(Items.BLACK_DYE, 8), in(Items.GLASS_PANE, 2), in(Items.COPPER_INGOT, 4), trig);
        Ingredient rifle = in(Items.REDSTONE, 6);
        gun("m4a1", in(Items.IRON_INGOT, 16), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 6), rifle);
        gun("hk416", in(Items.IRON_INGOT, 18), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 6), rifle);
        gun("akm", in(Items.IRON_INGOT, 14), in(Items.ACACIA_PLANKS, 6), in(Items.COPPER_INGOT, 4), rifle);
        gun("aug", in(Items.IRON_INGOT, 12), in(Items.GREEN_DYE, 6), in(Items.GLASS_PANE, 1), in(Items.COPPER_INGOT, 6), rifle);
        gun("fal", in(Items.IRON_INGOT, 20), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 6), rifle);
        gun("scar_h", in(Items.IRON_INGOT, 18), in(Items.BROWN_DYE, 6), in(Items.COPPER_INGOT, 6), rifle);
        gun("svd", in(Items.IRON_INGOT, 18), in(Items.ACACIA_PLANKS, 8), in(Items.GLASS, 2), in(Items.COPPER_INGOT, 6), rifle);
        gun("m14ebr", in(Items.IRON_INGOT, 22), in(Items.BLACK_DYE, 6), in(Items.COPPER_INGOT, 6), rifle);
        Ingredient sniper = in(Items.DIAMOND, 1);
        gun("m24", in(Items.IRON_INGOT, 18), in(Items.GREEN_DYE, 4), in(Items.GLASS, 3), sniper, rifle);
        gun("awm", in(Items.IRON_INGOT, 22), in(Items.GREEN_DYE, 6), in(Items.GLASS, 3), in(Items.DIAMOND, 2), rifle);
        gun("m82a1", in(Items.IRON_BLOCK, 4), in(Items.GLASS, 3), in(Items.DIAMOND, 3), in(Items.COPPER_INGOT, 10), rifle);
        gun("rem870", in(Items.IRON_INGOT, 12), in(Items.OAK_PLANKS, 6), in(Items.COPPER_INGOT, 3), trig);
        gun("benelli_m4", in(Items.IRON_INGOT, 16), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 4), rifle);
        gun("m249", in(Items.IRON_INGOT, 28), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 10), in(Items.REDSTONE, 10));
        gun("pkm", in(Items.IRON_INGOT, 26), in(Items.ACACIA_PLANKS, 6), in(Items.COPPER_INGOT, 10), in(Items.REDSTONE, 10));
        gun("rpg7", in(Items.IRON_INGOT, 16), in(Items.OAK_PLANKS, 4), in(Items.GLASS, 1), in(Items.REDSTONE, 4));
        // expansion
        gun("mosin", in(Items.IRON_INGOT, 14), in(Items.BIRCH_PLANKS, 8), in(Items.COPPER_INGOT, 3), rifle);
        gun("m1917", in(Items.IRON_INGOT, 16), in(Items.OAK_PLANKS, 8), in(Items.COPPER_INGOT, 3), rifle);
        gun("arisaka", in(Items.IRON_INGOT, 14), in(Items.DARK_OAK_PLANKS, 8), in(Items.COPPER_INGOT, 3), rifle);
        gun("sks", in(Items.IRON_INGOT, 14), in(Items.ACACIA_PLANKS, 6), in(Items.COPPER_INGOT, 4), rifle);
        gun("ppsh41", in(Items.IRON_INGOT, 16), in(Items.DARK_OAK_PLANKS, 4), in(Items.COPPER_INGOT, 4), trig);
        gun("m45", in(Items.IRON_INGOT, 12), in(Items.BLACK_DYE, 2), in(Items.COPPER_INGOT, 3), trig);
        gun("ak47", in(Items.IRON_INGOT, 16), in(Items.DARK_OAK_PLANKS, 6), in(Items.COPPER_INGOT, 4), rifle);
        gun("win1894", in(Items.IRON_INGOT, 12), in(Items.DARK_OAK_PLANKS, 6), in(Items.GOLD_NUGGET, 2), trig);
        gun("marlin336", in(Items.IRON_INGOT, 12), in(Items.OAK_PLANKS, 6), in(Items.COPPER_INGOT, 3), trig);
        gun("tikka_t3", in(Items.IRON_INGOT, 14), in(Items.GRAY_DYE, 4), in(Items.GLASS, 3), sniper, rifle);
        gun("savage10", in(Items.IRON_INGOT, 16), in(Items.BLACK_DYE, 4), in(Items.GLASS, 3), sniper, rifle);
        gun("model12", in(Items.IRON_INGOT, 14), in(Items.DARK_OAK_PLANKS, 6), in(Items.COPPER_INGOT, 3), trig);
        gun("nova", in(Items.IRON_INGOT, 10), in(Items.BLACK_DYE, 6), in(Items.COPPER_INGOT, 3), trig);
        gun("cdaly", in(Items.IRON_INGOT, 12), in(Items.OAK_PLANKS, 6), in(Items.COPPER_INGOT, 3), trig);
        gun("mossberg190", in(Items.IRON_INGOT, 10), in(Items.BIRCH_PLANKS, 6), in(Items.COPPER_INGOT, 2), trig);
        gun("ppq", in(Items.IRON_INGOT, 4), in(Items.BLACK_DYE, 2), in(Items.COPPER_INGOT, 2), pistol);
        gun("bersa", in(Items.IRON_INGOT, 4), in(Items.GRAY_DYE, 1), in(Items.COPPER_INGOT, 2), pistol);
        gun("rugermk3", in(Items.IRON_INGOT, 6), in(Items.BLACK_DYE, 1), in(Items.COPPER_INGOT, 1), pistol);
        gun("sw642", in(Items.IRON_INGOT, 5), in(Items.BLACK_DYE, 1), in(Items.COPPER_INGOT, 2), pistol);
        gun("singlesix", in(Items.IRON_INGOT, 6), in(Items.SPRUCE_PLANKS, 2), in(Items.GOLD_NUGGET, 2), pistol);

        // expansion 2
        gun("vector", in(Items.IRON_INGOT, 10), in(Items.BLACK_DYE, 5), in(Items.COPPER_INGOT, 4), trig);
        gun("mp7", in(Items.IRON_INGOT, 10), in(Items.BLACK_DYE, 5), in(Items.COPPER_INGOT, 4), trig);
        gun("g36c", in(Items.IRON_INGOT, 10), in(Items.BLACK_DYE, 5), in(Items.COPPER_INGOT, 4), trig);
        gun("famas", in(Items.IRON_INGOT, 10), in(Items.BLACK_DYE, 5), in(Items.COPPER_INGOT, 4), trig);
        gun("x95", in(Items.IRON_INGOT, 10), in(Items.BLACK_DYE, 5), in(Items.COPPER_INGOT, 4), trig);
        gun("fiveseven", in(Items.IRON_INGOT, 5), in(Items.BLACK_DYE, 2), in(Items.COPPER_INGOT, 2), pistol);
        gun("usp", in(Items.IRON_INGOT, 5), in(Items.BLACK_DYE, 2), in(Items.COPPER_INGOT, 2), pistol);
        gun("cz75", in(Items.IRON_INGOT, 5), in(Items.BLACK_DYE, 2), in(Items.COPPER_INGOT, 2), pistol);
        gun("spas12", in(Items.IRON_INGOT, 14), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 4), trig);
        gun("aa12", in(Items.IRON_INGOT, 14), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 4), trig);
        gun("kar98k", in(Items.IRON_INGOT, 14), in(Items.OAK_PLANKS, 8), in(Items.COPPER_INGOT, 4), rifle);
        gun("garand", in(Items.IRON_INGOT, 14), in(Items.OAK_PLANKS, 8), in(Items.COPPER_INGOT, 4), rifle);
        gun("enfield", in(Items.IRON_INGOT, 14), in(Items.OAK_PLANKS, 8), in(Items.COPPER_INGOT, 4), rifle);
        gun("thompson", in(Items.IRON_INGOT, 14), in(Items.OAK_PLANKS, 8), in(Items.COPPER_INGOT, 4), rifle);
        gun("mp40", in(Items.IRON_INGOT, 12), in(Items.COPPER_INGOT, 3), trig);
        gun("stg44", in(Items.IRON_INGOT, 14), in(Items.OAK_PLANKS, 8), in(Items.COPPER_INGOT, 4), rifle);
        gun("mg42", in(Items.IRON_INGOT, 28), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 10), in(Items.REDSTONE, 10));
        gun("bar", in(Items.IRON_INGOT, 14), in(Items.OAK_PLANKS, 8), in(Items.COPPER_INGOT, 4), rifle);
        gun("intervention", in(Items.IRON_INGOT, 20), in(Items.GRAY_DYE, 4), in(Items.GLASS, 3), sniper, rifle);
        gun("l96", in(Items.IRON_INGOT, 20), in(Items.GRAY_DYE, 4), in(Items.GLASS, 3), sniper, rifle);
        gun("rem700", in(Items.IRON_INGOT, 14), in(Items.OAK_PLANKS, 8), in(Items.COPPER_INGOT, 4), rifle);
        gun("sr25", in(Items.IRON_INGOT, 20), in(Items.GRAY_DYE, 4), in(Items.GLASS, 3), sniper, rifle);
        gun("svu", in(Items.IRON_INGOT, 20), in(Items.GRAY_DYE, 4), in(Items.GLASS, 3), sniper, rifle);
        gun("dsr1", in(Items.IRON_INGOT, 20), in(Items.GRAY_DYE, 4), in(Items.GLASS, 3), sniper, rifle);
        gun("m60", in(Items.IRON_INGOT, 28), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 10), in(Items.REDSTONE, 10));
        gun("m16a1", in(Items.IRON_INGOT, 16), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 6), rifle);
        gun("galil", in(Items.IRON_INGOT, 16), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 6), rifle);
        gun("g3a3", in(Items.IRON_INGOT, 16), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 6), rifle);
        gun("sten", in(Items.IRON_INGOT, 12), in(Items.COPPER_INGOT, 3), trig);
        gun("python", in(Items.IRON_INGOT, 5), in(Items.BLACK_DYE, 2), in(Items.COPPER_INGOT, 2), pistol);
        gun("skorpion", in(Items.IRON_INGOT, 12), in(Items.COPPER_INGOT, 3), trig);
        gun("ks23", in(Items.IRON_INGOT, 14), in(Items.BLACK_DYE, 4), in(Items.COPPER_INGOT, 4), trig);

        // ammo: brass (copper) case + gunpowder + lead (iron nugget) projectile
        ammo(Caliber.NINE_MM, 24, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 1), in(Items.IRON_NUGGET, 2));
        ammo(Caliber.ACP45, 20, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 1), in(Items.IRON_NUGGET, 3));
        ammo(Caliber.AE50, 12, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 3));
        ammo(Caliber.MAG44, 12, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 3));
        ammo(Caliber.FN57, 30, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 1), in(Items.IRON_NUGGET, 2));
        ammo(Caliber.NATO556, 30, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 3));
        ammo(Caliber.R762X39, 30, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 4));
        ammo(Caliber.NATO762, 20, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 3), in(Items.IRON_NUGGET, 4));
        ammo(Caliber.R762X54, 20, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 3), in(Items.IRON_NUGGET, 4));
        ammo(Caliber.WM300, 10, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 3), in(Items.IRON_NUGGET, 4));
        ammo(Caliber.BMG50, 5, in(Items.COPPER_INGOT, 3), in(Items.GUNPOWDER, 4), in(Items.IRON_INGOT, 1));
        ammo(Caliber.BUCK12, 12, in(Items.PAPER, 2), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 6), in(Items.COPPER_INGOT, 1));
        ammo(Caliber.SLUG12, 12, in(Items.PAPER, 2), in(Items.GUNPOWDER, 2), in(Items.IRON_INGOT, 1), in(Items.COPPER_INGOT, 1));
        ammo(Caliber.R762X25, 30, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 1), in(Items.IRON_NUGGET, 2));
        ammo(Caliber.SPR3006, 15, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 3), in(Items.IRON_NUGGET, 4));
        ammo(Caliber.ARI77, 15, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 3), in(Items.IRON_NUGGET, 4));
        ammo(Caliber.WIN3030, 20, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 3));
        ammo(Caliber.SPL38, 24, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 1), in(Items.IRON_NUGGET, 2));
        ammo(Caliber.LR22, 50, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 1), in(Items.IRON_NUGGET, 1));
        ammo(Caliber.ACP380, 28, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 1), in(Items.IRON_NUGGET, 2));
        ammo(Caliber.BLK300, 20, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 3));
        ammo(Caliber.BUCK16, 12, in(Items.PAPER, 2), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 5), in(Items.COPPER_INGOT, 1));
        ammo(Caliber.HK46, 30, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 1), in(Items.IRON_NUGGET, 2));
        ammo(Caliber.MAUSER792, 16, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 3));
        ammo(Caliber.KURZ792, 24, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 3));
        ammo(Caliber.BRIT303, 16, in(Items.COPPER_INGOT, 2), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 3));
        ammo(Caliber.CHEY408, 6, in(Items.COPPER_INGOT, 3), in(Items.GUNPOWDER, 3), in(Items.IRON_NUGGET, 4));
        ammo(Caliber.LAPUA338, 8, in(Items.COPPER_INGOT, 3), in(Items.GUNPOWDER, 3), in(Items.IRON_NUGGET, 4));
        ammo(Caliber.MAG357, 14, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 3));
        ammo(Caliber.ACP32, 30, in(Items.COPPER_INGOT, 1), in(Items.GUNPOWDER, 1), in(Items.IRON_NUGGET, 1));
        ammo(Caliber.SHELL23, 6, in(Items.PAPER, 2), in(Items.GUNPOWDER, 2), in(Items.IRON_NUGGET, 8), in(Items.COPPER_INGOT, 2));
        ammo(Caliber.PG7, 1, in(Items.TNT, 1), in(Items.IRON_INGOT, 2), in(Items.GUNPOWDER, 4), in(Items.GREEN_DYE, 1));

        att(Attachment.RED_DOT, in(Items.IRON_INGOT, 2), in(Items.GLASS_PANE, 1), in(Items.REDSTONE, 1));
        att(Attachment.HOLO, in(Items.IRON_INGOT, 3), in(Items.GLASS_PANE, 2), in(Items.REDSTONE, 2));
        att(Attachment.ACOG, in(Items.IRON_INGOT, 3), in(Items.GLASS, 2), in(Items.GLOWSTONE_DUST, 1));
        att(Attachment.SCOPE_8X, in(Items.IRON_INGOT, 4), in(Items.GLASS, 3), in(Items.AMETHYST_SHARD, 1));
        att(Attachment.PSO1, in(Items.IRON_INGOT, 4), in(Items.GLASS, 2), in(Items.AMETHYST_SHARD, 1));
        att(Attachment.SUPPRESSOR_PISTOL, in(Items.IRON_INGOT, 4), in(Items.WHITE_WOOL, 2));
        att(Attachment.SUPPRESSOR_RIFLE, in(Items.IRON_INGOT, 6), in(Items.WHITE_WOOL, 3));
        att(Attachment.COMPENSATOR, in(Items.IRON_INGOT, 3));
        att(Attachment.FLASH_HIDER, in(Items.IRON_INGOT, 2), in(Items.IRON_NUGGET, 4));
        att(Attachment.VERTICAL_GRIP, in(Items.IRON_INGOT, 1), in(Items.BLACK_DYE, 2));
        att(Attachment.ANGLED_GRIP, in(Items.IRON_INGOT, 1), in(Items.BLACK_DYE, 2));
        att(Attachment.BIPOD_ATT, in(Items.IRON_INGOT, 4));
        att(Attachment.LASER, in(Items.IRON_INGOT, 1), in(Items.REDSTONE, 2), in(Items.GLASS_PANE, 1));
        att(Attachment.EXTENDED_MAG, in(Items.IRON_INGOT, 4), in(Items.COPPER_INGOT, 2));
    }

    public static List<Recipe> all() {
        return ALL;
    }

    public static List<Recipe> tab(Tab t) {
        List<Recipe> out = new ArrayList<>();
        for (Recipe r : ALL) if (r.tab == t) out.add(r);
        return out;
    }

    public static GunDefinition defFor(Recipe r) {
        return r.tab == Tab.GUNS ? Guns.get(net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(r.result.get()).getPath()) : null;
    }

    private GunsmithingRecipes() {}
}
