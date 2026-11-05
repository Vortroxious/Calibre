package dev.calibre.client;

import dev.calibre.attachment.AttachmentItem;
import dev.calibre.gun.Attachment;
import dev.calibre.gun.GunAttachments;
import dev.calibre.gun.GunItem;
import dev.calibre.workbench.GunWorkbenchMenu;
import dev.calibre.workbench.GunsmithingRecipes;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Gun Workbench: tabs for Guns / Ammo / Attachments (craft from inventory) and Modify (attachments on the held gun).
 * Drawn entirely with fills, no texture.
 */
public class WorkbenchScreen extends AbstractContainerScreen<GunWorkbenchMenu> {
    private enum Tab { GUNS, AMMO, ATTACHMENTS, MODIFY }

    private static final int ROWS = 7, ROW_H = 18, LIST_W = 120;
    private Tab tab = Tab.GUNS;
    private int scroll, selected = -1;
    private Button craft;

    public WorkbenchScreen(GunWorkbenchMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        this.imageWidth = 256;
        this.imageHeight = 236;
        this.inventoryLabelY = 143;
        this.inventoryLabelX = 48;
    }

    @Override
    protected void init() {
        super.init();
        int x = leftPos, y = topPos;
        int i = 0;
        for (Tab t : Tab.values()) {
            addRenderableWidget(Button.builder(Component.translatable("gui.calibre.tab." + t.name().toLowerCase(Locale.ROOT)), b -> {
                tab = t;
                scroll = 0;
                selected = -1;
            }).bounds(x + 4 + i * 62, y - 18, 60, 16).build());
            i++;
        }
        craft = addRenderableWidget(Button.builder(Component.translatable("gui.calibre.craft"), b -> doCraft())
                .bounds(x + 190, y + 116, 60, 18).build());
    }

    private List<GunsmithingRecipes.Recipe> recipes() {
        return switch (tab) {
            case GUNS -> GunsmithingRecipes.tab(GunsmithingRecipes.Tab.GUNS);
            case AMMO -> GunsmithingRecipes.tab(GunsmithingRecipes.Tab.AMMO);
            case ATTACHMENTS -> GunsmithingRecipes.tab(GunsmithingRecipes.Tab.ATTACHMENTS);
            case MODIFY -> List.of();
        };
    }

    private void doCraft() {
        List<GunsmithingRecipes.Recipe> list = recipes();
        if (selected < 0 || selected >= list.size()) return;
        int id = GunsmithingRecipes.all().indexOf(list.get(selected));
        click(id);
    }

    private void click(int id) {
        if (menu.clickMenuButton(minecraft.player, id) && minecraft.gameMode != null)
            minecraft.gameMode.handleInventoryButtonClick(menu.containerId, id);
    }

    @Override
    protected void renderBg(GuiGraphics g, float pt, int mx, int my) {
        int x = leftPos, y = topPos;
        g.fill(x, y, x + imageWidth, y + imageHeight, 0xF0202226);
        g.fill(x + 1, y + 1, x + imageWidth - 1, y + 140, 0xFF2A2D33);
        g.fill(x + 1, y + 141, x + imageWidth - 1, y + imageHeight - 1, 0xFF25272C);
        // inventory slot wells
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 9; c++) {
                int sx = x + 47 + c * 18, sy = y + (r < 3 ? 153 + r * 18 : 211);
                g.fill(sx, sy, sx + 18, sy + 18, 0xFF15161A);
                g.fill(sx + 1, sy + 1, sx + 17, sy + 17, 0xFF33363D);
            }
    }

    @Override
    public void render(GuiGraphics g, int mx, int my, float pt) {
        super.render(g, mx, my, pt);
        int x = leftPos, y = topPos;
        craft.visible = tab != Tab.MODIFY;
        if (tab == Tab.MODIFY) {
            renderModify(g, mx, my);
        } else {
            renderRecipes(g, mx, my);
        }
        renderTooltip(g, mx, my);
    }

    private void renderRecipes(GuiGraphics g, int mx, int my) {
        int x = leftPos + 4, y = topPos + 6;
        List<GunsmithingRecipes.Recipe> list = recipes();
        g.fill(x, y, x + LIST_W, y + ROWS * ROW_H + 2, 0xFF1B1D21);
        for (int i = 0; i < ROWS && i + scroll < list.size(); i++) {
            int idx = i + scroll;
            GunsmithingRecipes.Recipe r = list.get(idx);
            int ry = y + 1 + i * ROW_H;
            boolean hover = mx >= x && mx < x + LIST_W && my >= ry && my < ry + ROW_H;
            if (idx == selected) g.fill(x + 1, ry, x + LIST_W - 1, ry + ROW_H, 0xFF3D5A80);
            else if (hover) g.fill(x + 1, ry, x + LIST_W - 1, ry + ROW_H, 0xFF30343B);
            ItemStack out = r.resultStack();
            g.renderItem(out, x + 2, ry + 1);
            int col = r.canCraft(minecraft.player) ? 0xFFFFFFFF : 0xFF9A9A9A;
            String name = font.plainSubstrByWidth(out.getHoverName().getString(), LIST_W - 24);
            g.drawString(font, name, x + 21, ry + 5, col, false);
        }
        if (list.size() > ROWS) {
            int barH = ROWS * ROW_H;
            int knob = Math.max(10, barH * ROWS / list.size());
            int ky = y + (barH - knob) * scroll / Math.max(1, list.size() - ROWS);
            g.fill(x + LIST_W + 1, y, x + LIST_W + 4, y + barH, 0xFF15161A);
            g.fill(x + LIST_W + 1, ky, x + LIST_W + 4, ky + knob, 0xFF6A7080);
        }
        // detail panel
        int dx = leftPos + 130, dy = topPos + 6;
        if (selected >= 0 && selected < list.size()) {
            GunsmithingRecipes.Recipe r = list.get(selected);
            ItemStack out = r.resultStack();
            g.pose().pushMatrix();
            g.pose().translate(dx + 2, dy + 2);
            g.pose().scale(2.5f, 2.5f);
            g.renderItem(out, 0, 0);
            g.pose().popMatrix();
            g.drawString(font, out.getHoverName(), dx + 46, dy + 4, 0xFFFFFFFF, false);
            if (out.getCount() > 1) g.drawString(font, "x" + out.getCount(), dx + 46, dy + 16, 0xFFB0B0B0, false);
            if (out.getItem() instanceof GunItem gi) {
                g.drawString(font, gi.def().caliber().displayName, dx + 46, dy + 16, 0xFFB0B0B0, false);
                g.drawString(font, gi.def().magSize() + " rds  " + gi.def().rpm() + " rpm", dx + 46, dy + 28, 0xFF909090, false);
            }
            int iy = dy + 48;
            for (GunsmithingRecipes.Ingredient in : r.ingredients()) {
                ItemStack st = new ItemStack(in.item().get());
                int have = GunsmithingRecipes.count(minecraft.player, st.getItem());
                g.renderItem(st, dx, iy);
                boolean ok = have >= in.count() || minecraft.player.getAbilities().instabuild;
                g.drawString(font, have + "/" + in.count(), dx + 20, iy + 5, ok ? 0xFF70E070 : 0xFFE07070, false);
                g.drawString(font, font.plainSubstrByWidth(st.getHoverName().getString(), 70), dx + 52, iy + 5, 0xFFC0C0C0, false);
                iy += 17;
            }
            craft.active = r.canCraft(minecraft.player);
        } else {
            craft.active = false;
            g.drawString(font, Component.translatable("gui.calibre.select"), dx, dy + 4, 0xFF909090, false);
        }
    }

    private final List<int[]> modifyHotspots = new ArrayList<>();

    private void renderModify(GuiGraphics g, int mx, int my) {
        modifyHotspots.clear();
        int x = leftPos + 6, y = topPos + 6;
        ItemStack gunStack = minecraft.player.getMainHandItem();
        if (!(gunStack.getItem() instanceof GunItem gun)) {
            g.drawString(font, Component.translatable("gui.calibre.hold_gun"), x, y + 4, 0xFFE0A060, false);
            return;
        }
        g.pose().pushMatrix();
        g.pose().translate(x, y);
        g.pose().scale(3f, 3f);
        g.renderItem(gunStack, 0, 0);
        g.pose().popMatrix();
        g.drawString(font, gunStack.getHoverName(), x + 56, y + 4, 0xFFFFFFFF, false);
        GunAttachments att = GunItem.attachments(gunStack);
        int sy = y + 56;
        g.drawString(font, Component.translatable("gui.calibre.installed").withStyle(ChatFormatting.GRAY), x, sy - 10, 0xFFB0B0B0, false);
        for (Attachment.Slot slot : Attachment.Slot.values()) {
            boolean any = false;
            for (Attachment a : Attachment.values()) if (a.slot == slot && gun.def().allows(a)) any = true;
            if (!any) continue;
            Attachment cur = att.get(slot);
            String label = Component.translatable("tooltip.calibre.slot." + slot.name().toLowerCase(Locale.ROOT)).getString() + ": ";
            g.drawString(font, label, x, sy + 4, 0xFF909090, false);
            int lx = x + font.width(label);
            if (cur != null) {
                ItemStack cs = new ItemStack(dev.calibre.registry.ModRegistry.ATTACHMENTS.get(cur).get());
                g.renderItem(cs, lx, sy);
                boolean hover = mx >= lx && mx < lx + 16 && my >= sy && my < sy + 16;
                g.drawString(font, cs.getHoverName(), lx + 18, sy + 4, hover ? 0xFFFF8080 : 0xFFFFFFFF, false);
                modifyHotspots.add(new int[]{lx, sy, 100, 16, GunWorkbenchMenu.REMOVE + slot.ordinal()});
            } else {
                g.drawString(font, "-", lx, sy + 4, 0xFF606060, false);
            }
            sy += 17;
        }
        // compatible attachments in the inventory
        int ax = leftPos + 140, ay = topPos + 56;
        g.drawString(font, Component.translatable("gui.calibre.available").withStyle(ChatFormatting.GRAY), ax, ay - 10, 0xFFB0B0B0, false);
        var inv = minecraft.player.getInventory();
        int n = 0;
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack st = inv.getItem(i);
            if (st.getItem() instanceof AttachmentItem ai && gun.def().allows(ai.attachment())) {
                int px = ax + (n % 5) * 20, py = ay + (n / 5) * 20;
                boolean hover = mx >= px && mx < px + 18 && my >= py && my < py + 18;
                g.fill(px - 1, py - 1, px + 17, py + 17, hover ? 0xFF3D5A80 : 0xFF1B1D21);
                g.renderItem(st, px, py);
                modifyHotspots.add(new int[]{px, py, 16, 16, GunWorkbenchMenu.INSTALL + i});
                n++;
            }
        }
        if (n == 0) g.drawString(font, Component.translatable("gui.calibre.none"), ax, ay + 4, 0xFF606060, false);
        g.drawString(font, Component.translatable("gui.calibre.modify_hint"), leftPos + 6, topPos + 128, 0xFF707070, false);
    }

    @Override
    public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
        double mx = event.x(), my = event.y();
        if (tab == Tab.MODIFY) {
            for (int[] h : modifyHotspots) {
                if (mx >= h[0] && mx < h[0] + h[2] && my >= h[1] && my < h[1] + h[3]) {
                    click(h[4]);
                    return true;
                }
            }
        } else {
            int x = leftPos + 4, y = topPos + 7;
            if (mx >= x && mx < x + LIST_W && my >= y && my < y + ROWS * ROW_H) {
                int idx = (int) ((my - y) / ROW_H) + scroll;
                if (idx < recipes().size()) {
                    selected = idx;
                    Minecraft.getInstance().getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(
                            net.minecraft.sounds.SoundEvents.UI_BUTTON_CLICK, 1f));
                    return true;
                }
            }
        }
        return super.mouseClicked(event, doubleClick);
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double sx, double sy) {
        int max = Math.max(0, recipes().size() - ROWS);
        scroll = Math.max(0, Math.min(max, scroll - (int) Math.signum(sy)));
        return true;
    }

    @Override
    protected void renderLabels(GuiGraphics g, int mx, int my) {
        g.drawString(font, playerInventoryTitle, inventoryLabelX, inventoryLabelY, 0xFFA0A0A0, false);
    }
}
