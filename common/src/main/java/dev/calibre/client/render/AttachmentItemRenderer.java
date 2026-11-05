package dev.calibre.client.render;

import dev.calibre.Calibre;
import dev.calibre.attachment.AttachmentItem;
import net.minecraft.resources.Identifier;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import software.bernie.geckolib.renderer.base.GeoRenderState;
import software.bernie.geckolib.renderer.base.RenderPassInfo;

/** 3D item rendering for attachments, reusing the exact models mounted on the guns. */
public class AttachmentItemRenderer extends GeoItemRenderer<AttachmentItem> {
    public AttachmentItemRenderer(AttachmentItem item) {
        super(new GeoModel<>() {
            private final Identifier model = Calibre.id("attachment/" + item.attachment().id());
            private final Identifier tex = Calibre.id("textures/attachment/" + item.attachment().id() + ".png");
            private final Identifier anim = Calibre.id("attachment/" + item.attachment().id());

            @Override
            public Identifier getModelResource(GeoRenderState renderState) {
                return model;
            }

            @Override
            public Identifier getTextureResource(GeoRenderState renderState) {
                return tex;
            }

            @Override
            public Identifier getAnimationResource(AttachmentItem animatable) {
                return anim;
            }
        });
        withScale(GunRenderer.SCALE);
    }

    @Override
    public void adjustRenderPose(RenderPassInfo<GeoRenderState> info) {
        info.poseStack().translate(0.5f / GunRenderer.SCALE, 0.5f / GunRenderer.SCALE, 0.5f / GunRenderer.SCALE);
    }
}
