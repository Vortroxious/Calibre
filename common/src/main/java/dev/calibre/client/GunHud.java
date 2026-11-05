package dev.calibre.client;

import dev.calibre.Calibre;
import dev.calibre.CalibreConfig;
import dev.calibre.gun.GunDefinition;
import dev.calibre.gun.GunItem;
import dev.calibre.gun.GunMeta;
import dev.calibre.gun.GunLogic;
import dev.calibre.gun.Attachment;
import dev.calibre.network.Net;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemStack;

import java.util.Locale;

/** Ammo counter, dynamic crosshair, hit markers and the scope overlay. */
public final class GunHud {
    public static final Identifier LAYER = Calibre.id("gun_hud");
    public static final Identifier SCOPE_LAYER = Calibre.id("scope");

    private GunHud() {}

    /** the vanilla crosshair is replaced by {@link #render} while a gun is held */
    public static boolean hideVanillaCrosshair() {
        return ClientGun.holdingGun();
    }

    public static void renderScope(GuiGraphics g, DeltaTracker dt) {
        float pt = dt.getGameTimeDeltaPartialTick(true);
        if (!ClientGun.scoped(pt)) return;
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null || !(p.getMainHandItem().getItem() instanceof GunItem gun)) return;
        String reticle = gun.meta().integralReticle;
        Attachment optic = GunItem.attachments(p.getMainHandItem()).get(Attachment.Slot.OPTIC);
        if (reticle == null && optic != null) reticle = GunMeta.AttachmentMeta.get(optic.id()).reticle;
        if (reticle == null) reticle = "mildot";
        int w = g.guiWidth(), h = g.guiHeight();
        int size = h;
        int x0 = (w - size) / 2;
        g.fill(0, 0, x0, h, 0xFF000000);
        g.fill(x0 + size, 0, w, h, 0xFF000000);
        // subtle scope sway
        float sx = ClientGun.SWAY_X.x * 1.5f, sy = ClientGun.SWAY_Y.x * 1.5f;
        g.blit(Calibre.id("textures/gui/scope_" + reticle + ".png"), (int) (x0 + sx), (int) sy, (int) (x0 + size + sx), (int) (size + sy), 0, 1, 0, 1);
    }

    public static void render(GuiGraphics g, DeltaTracker dt) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null || mc.options.hideGui) return;
        ItemStack stack = p.getMainHandItem();
        if (!(stack.getItem() instanceof GunItem gun)) return;
        GunDefinition def = gun.def();
        Font font = mc.font;
        int w = g.guiWidth(), h = g.guiHeight();
        float pt = dt.getGameTimeDeltaPartialTick(true);

        // crosshair
        if (CalibreConfig.client(CalibreConfig.CROSSHAIR, true) && !ClientGun.scoped(pt) && ClientGun.adsEased(pt) < 0.5f) {
            float spread = ClientGun.currentSpread();
            double fov = mc.options.fov().get();
            int gap = 3 + (int) (Math.tan(Math.toRadians(spread * 0.5)) / Math.tan(Math.toRadians(fov * 0.5)) * h * 0.5);
            int cx = w / 2, cy = h / 2;
            int col = 0xE0FFFFFF;
            int len = 5;
            g.fill(cx - gap - len, cy, cx - gap, cy + 1, col);
            g.fill(cx + gap + 1, cy, cx + gap + 1 + len, cy + 1, col);
            g.fill(cx, cy - gap - len, cx + 1, cy - gap, col);
            g.fill(cx, cy + gap + 1, cx + 1, cy + gap + 1 + len, col);
            g.fill(cx, cy, cx + 1, cy + 1, 0x90FFFFFF);
        }
        // hit marker
        float hm = ClientGun.hitMarker();
        if (hm > 0) {
            int cx = w / 2, cy = h / 2;
            int c = ClientGun.hitKind() == Net.HitPayload.KILL ? 0xFFFF3030 : ClientGun.hitKind() == Net.HitPayload.HEADSHOT ? 0xFFFFD040 : 0xFFFFFFFF;
            int a = (int) (Mth.clamp(hm, 0, 1) * 255) << 24 | (c & 0xFFFFFF);
            for (int i = 4; i < 9; i++) {
                g.fill(cx - i, cy - i, cx - i + 1, cy - i + 1, a);
                g.fill(cx + i, cy - i, cx + i + 1, cy - i + 1, a);
                g.fill(cx - i, cy + i, cx - i + 1, cy + i + 1, a);
                g.fill(cx + i, cy + i, cx + i + 1, cy + i + 1, a);
            }
        }
        if (!CalibreConfig.client(CalibreConfig.HUD, true)) return;
        // ammo counter (bottom right)
        int rounds = ClientGun.predictedRounds(stack);
        int cap = def.capacity(GunItem.attachments(stack));
        int reserve = GunLogic.available(p, def.caliber());
        String big = String.valueOf(rounds);
        String small = " / " + (reserve > 9000 ? "∞" : String.valueOf(reserve));
        int x = w - 12;
        int y = h - 82; // above the hotbar status bars
        g.fill(x - 128, y - 6, x + 6, y + 34, 0x60000000);
        int col = rounds == 0 ? 0xFFFF5050 : rounds <= Math.max(1, cap / 4) ? 0xFFFFC040 : 0xFFFFFFFF;
        g.pose().pushMatrix();
        g.pose().translate(x - font.width(small) - font.width(big) * 2, y);
        g.pose().scale(2, 2);
        g.drawString(font, big, 0, 0, col, true);
        g.pose().popMatrix();
        g.drawString(font, small, x - font.width(small), y + 7, 0xFFC0C0C0, true);
        Component name = Component.translatable("item.calibre." + def.id());
        g.drawString(font, name, x - font.width(name), y + 20, 0xFFE0E0E0, true);
        String mode = gun.mode(stack).name().toUpperCase(Locale.ROOT);
        if (def.cycle().manual() && gun.mode(stack) == GunDefinition.FireMode.AUTO) mode = "SLAM FIRE";
        String info = def.caliber().displayName + "  " + mode;
        g.drawString(font, info, x - 124, y - 2, 0xFF909090, false);
        // round pips for small magazines
        if (cap <= 30) {
            int px = x - 124;
            for (int i = 0; i < cap; i++) {
                int c = i < rounds ? 0xFFE0C070 : 0x50FFFFFF;
                g.fill(px + i * 4, y + 30, px + i * 4 + 3, y + 33, c);
            }
        }
    }
}
