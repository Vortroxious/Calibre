package dev.calibre.client;

import dev.calibre.CalibreConfig;
import dev.calibre.attachment.AttachmentItem;
import dev.calibre.client.render.AttachmentItemRenderer;
import dev.calibre.client.render.GunRenderer;
import dev.calibre.gun.GunItem;
import dev.calibre.network.Net;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.HitResult;
import software.bernie.geckolib.animatable.client.GeoRenderProvider;
import software.bernie.geckolib.renderer.GeoItemRenderer;

/** Loader-neutral client setup and input/camera rules; the loader modules wire these into their events or mixins. */
public final class CalibreClient {
    private CalibreClient() {}

    public static void init() {
        GunItem.RENDERER = gun -> new GeoRenderProvider() {
            private GunRenderer renderer;

            @Override
            public GeoItemRenderer<?> getGeoItemRenderer() {
                if (renderer == null) renderer = new GunRenderer(gun);
                return renderer;
            }
        };
        AttachmentItem.RENDERER = att -> new GeoRenderProvider() {
            private AttachmentItemRenderer renderer;

            @Override
            public GeoItemRenderer<?> getGeoItemRenderer() {
                if (renderer == null) renderer = new AttachmentItemRenderer(att);
                return renderer;
            }
        };
        Net.CLIENT = new Net.ClientSink() {
            @Override
            public void onAction(Net.ActionPayload p) {
                ClientGun.onAction(p);
            }

            @Override
            public void onHit(Net.HitPayload p) {
                ClientGun.onHit(p);
            }
        };
    }

    public static void clientTick() {
        ClientGun.tick();
        ClientAutoTest.tick();
    }

    public static void frame() {
        ClientGun.frame();
    }

    /** Left click while holding a gun fires instead of attacking / breaking blocks. */
    public static boolean cancelAttack() {
        return ClientGun.holdingGun();
    }

    /** Right click aims, except on a block (workbench, doors, chests) when not already aiming. */
    public static boolean cancelUse() {
        if (!ClientGun.holdingGun()) return false;
        HitResult hr = Minecraft.getInstance().hitResult;
        boolean block = hr != null && hr.getType() == HitResult.Type.BLOCK && !ClientGun.isLocalAiming();
        return !block;
    }

    /** FOV modifier while aiming (zoom of the sight or optic). */
    /** CS2-style camera motion {pitch, yaw, roll} to add to the first-person view this frame. */
    public static float[] cameraShake() {
        net.minecraft.client.Minecraft mc = net.minecraft.client.Minecraft.getInstance();
        if (mc.player == null || !mc.options.getCameraType().isFirstPerson()) return new float[]{0, 0, 0};
        return ClientGun.cameraOffset();
    }

    public static float fovModifier(Player player, float current) {
        if (!ClientGun.holdingGun()) return current;
        float a = ClientGun.adsEased(1);
        if (a <= 0) return current;
        ItemStack st = player.getMainHandItem();
        float target = 1f / ClientGun.zoom(st);
        return current * (1 + (target - 1) * a);
    }

    /** Mouse sensitivity while aiming through magnified optics. */
    public static double sensitivity(double current) {
        if (!ClientGun.holdingGun()) return current;
        float a = ClientGun.adsEased(1);
        if (a <= 0) return current;
        float zoom = ClientGun.zoom(Minecraft.getInstance().player.getMainHandItem());
        double mul = 1 + (Math.pow(1 / zoom, 0.85) * CalibreConfig.ADS_SENSITIVITY.get() - 1) * a;
        return current * mul;
    }
}
