package dev.calibre.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.calibre.Calibre;
import dev.calibre.gun.CalibreTickets;
import dev.calibre.gun.GunItem;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import software.bernie.geckolib.cache.model.GeoBone;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import software.bernie.geckolib.renderer.base.GeoRenderState;
import software.bernie.geckolib.renderer.base.PerBoneRender;
import software.bernie.geckolib.renderer.base.RenderPassInfo;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

import java.util.function.BiConsumer;

/** Emissive star-shaped muzzle flash at the `muzzle` bone for a couple of frames after each shot. */
public class MuzzleFlashLayer extends GeoRenderLayer<GunItem, GeoItemRenderer.RenderData, GeoRenderState> {
    private static final Identifier FLASH = Calibre.id("textures/effect/muzzle_flash.png");
    private static final Identifier FLASH_SIDE = Calibre.id("textures/effect/muzzle_flash_side.png");

    public MuzzleFlashLayer(GeoItemRenderer<GunItem> renderer) {
        super(renderer);
    }

    @Override
    public void addPerBoneRender(RenderPassInfo<GeoRenderState> info, BiConsumer<GeoBone, PerBoneRender<GeoRenderState>> consumer) {
        Float f = info.getGeckolibData(CalibreTickets.FLASH);
        if (f == null || f <= 0.01f) return;
        float alpha = f;
        info.model().getBone("muzzle").ifPresent(bone -> consumer.accept(bone, (i, b, tasks) -> {
            float size = 1.6f + 0.4f * (float) Math.random();   // local units (1 = 16 cm)
            float spin = (float) (Math.random() * 360);
            PoseStack ps = i.poseStack();
            ps.pushPose();
            ps.mulPose(com.mojang.math.Axis.ZP.rotationDegrees(spin));
            tasks.submitCustomGeometry(ps, RenderTypes.entityTranslucentEmissive(FLASH), (pose, vc) -> {
                quad(vc, pose, -size * 0.5f, -size * 0.5f, -0.02f, size * 0.5f, size * 0.5f, -0.02f, alpha, true);
            });
            tasks.submitCustomGeometry(ps, RenderTypes.entityTranslucentEmissive(FLASH_SIDE), (pose, vc) -> {
                float len = size * 1.3f;
                // two crossed side-on planes along -Z
                sideQuad(vc, pose, size * 0.35f, len, alpha, false);
                sideQuad(vc, pose, size * 0.35f, len, alpha, true);
            });
            ps.popPose();
        }));
    }

    private static void quad(VertexConsumer vc, PoseStack.Pose pose, float x0, float y0, float z0, float x1, float y1, float z1, float a,
                             boolean front) {
        int alpha = (int) (a * 255);
        v(vc, pose, x0, y0, z0, 0, 1, alpha);
        v(vc, pose, x1, y0, z0, 1, 1, alpha);
        v(vc, pose, x1, y1, z1, 1, 0, alpha);
        v(vc, pose, x0, y1, z1, 0, 0, alpha);
    }

    private static void sideQuad(VertexConsumer vc, PoseStack.Pose pose, float h, float len, float a, boolean vertical) {
        int alpha = (int) (a * 255);
        if (vertical) {
            v(vc, pose, 0, -h, 0, 0, 1, alpha);
            v(vc, pose, 0, -h, -len, 1, 1, alpha);
            v(vc, pose, 0, h, -len, 1, 0, alpha);
            v(vc, pose, 0, h, 0, 0, 0, alpha);
        } else {
            v(vc, pose, -h, 0, 0, 0, 1, alpha);
            v(vc, pose, -h, 0, -len, 1, 1, alpha);
            v(vc, pose, h, 0, -len, 1, 0, alpha);
            v(vc, pose, h, 0, 0, 0, 0, alpha);
        }
    }

    private static void v(VertexConsumer vc, PoseStack.Pose pose, float x, float y, float z, float u, float vv, int alpha) {
        vc.addVertex(pose, x, y, z).setColor(255, 240, 200, alpha).setUv(u, vv).setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(0xF000F0).setNormal(pose, 0, 0, 1);
    }
}
