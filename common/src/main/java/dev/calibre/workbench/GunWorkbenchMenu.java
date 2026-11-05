package dev.calibre.workbench;

import dev.calibre.attachment.AttachmentItem;
import dev.calibre.gun.Attachment;
import dev.calibre.gun.GunAttachments;
import dev.calibre.gun.GunItem;
import dev.calibre.gun.GunState;
import dev.calibre.registry.ModRegistry;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

import java.util.List;

/**
 * Gunsmithing: craft guns/ammo/attachments from the inventory, and modify the gun in your main hand.
 * Button ids: [0,1000) craft recipe, [1000,1100) remove attachment slot, [2000,2100) install from inventory slot.
 */
public class GunWorkbenchMenu extends AbstractContainerMenu {
    public static final int REMOVE = 1000, INSTALL = 2000;
    private final ContainerLevelAccess access;
    private final Player player;

    public GunWorkbenchMenu(int id, Inventory inv) {
        this(id, inv, ContainerLevelAccess.NULL);
    }

    public GunWorkbenchMenu(int id, Inventory inv, ContainerLevelAccess access) {
        super(ModRegistry.WORKBENCH_MENU.get(), id);
        this.access = access;
        this.player = inv.player;
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 9; c++)
                addSlot(new Slot(inv, c + r * 9 + 9, 48 + c * 18, 154 + r * 18));
        for (int c = 0; c < 9; c++)
            addSlot(new Slot(inv, c, 48 + c * 18, 212));
    }

    @Override
    public boolean clickMenuButton(Player p, int id) {
        if (id >= 0 && id < REMOVE) {
            List<GunsmithingRecipes.Recipe> all = GunsmithingRecipes.all();
            if (id >= all.size()) return false;
            GunsmithingRecipes.Recipe r = all.get(id);
            if (!r.canCraft(p)) return false;
            if (!p.level().isClientSide()) {
                r.consume(p);
                ItemStack out = r.resultStack();
                if (out.getItem() instanceof GunItem gun) GunItem.setState(out, new GunState(0, false, 0));
                if (!p.getInventory().add(out)) p.drop(out, false);
                access.execute((level, pos) -> level.playSound(null, pos, SoundEvents.SMITHING_TABLE_USE, SoundSource.BLOCKS, 1f, 1f));
            }
            return true;
        }
        ItemStack gunStack = p.getMainHandItem();
        if (!(gunStack.getItem() instanceof GunItem gun)) return false;
        GunAttachments att = GunItem.attachments(gunStack);
        if (id >= REMOVE && id < REMOVE + Attachment.Slot.values().length) {
            Attachment.Slot slot = Attachment.Slot.values()[id - REMOVE];
            Attachment a = att.get(slot);
            if (a == null) return false;
            if (!p.level().isClientSide()) {
                gunStack.set(ModRegistry.GUN_ATTACHMENTS.get(), att.without(slot));
                clampAmmo(gunStack, gun);
                ItemStack back = new ItemStack(ModRegistry.ATTACHMENTS.get(a).get());
                if (!p.getInventory().add(back)) p.drop(back, false);
                access.execute((level, pos) -> level.playSound(null, pos, SoundEvents.ARMOR_EQUIP_IRON.value(), SoundSource.BLOCKS, 0.8f, 1.3f));
            }
            return true;
        }
        if (id >= INSTALL && id < INSTALL + p.getInventory().getContainerSize()) {
            ItemStack st = p.getInventory().getItem(id - INSTALL);
            if (!(st.getItem() instanceof AttachmentItem ai) || !gun.def().allows(ai.attachment())) return false;
            if (gun.meta().integralZoom > 0 && ai.attachment().slot == Attachment.Slot.OPTIC) return false;
            if (!p.level().isClientSide()) {
                Attachment old = att.get(ai.attachment().slot);
                gunStack.set(ModRegistry.GUN_ATTACHMENTS.get(), att.with(ai.attachment()));
                st.shrink(1);
                if (old != null) {
                    ItemStack back = new ItemStack(ModRegistry.ATTACHMENTS.get(old).get());
                    if (!p.getInventory().add(back)) p.drop(back, false);
                }
                clampAmmo(gunStack, gun);
                access.execute((level, pos) -> level.playSound(null, pos, SoundEvents.ARMOR_EQUIP_NETHERITE.value(), SoundSource.BLOCKS, 0.8f, 1.2f));
            }
            return true;
        }
        return false;
    }

    /** Removing an extended mag drops the extra rounds back into the inventory. */
    private void clampAmmo(ItemStack gunStack, GunItem gun) {
        GunState s = GunItem.state(gunStack);
        int cap = gun.def().capacity(GunItem.attachments(gunStack));
        if (s.ammo() > cap) {
            int extra = s.ammo() - cap;
            GunItem.setState(gunStack, s.withAmmo(cap));
            ItemStack back = new ItemStack(ModRegistry.AMMO.get(gun.def().caliber()).get(), extra);
            if (!player.getInventory().add(back)) player.drop(back, false);
        }
    }

    @Override
    public ItemStack quickMoveStack(Player p, int index) {
        return ItemStack.EMPTY;
    }

    @Override
    public boolean stillValid(Player p) {
        return stillValid(access, p, ModRegistry.WORKBENCH.get());
    }
}
