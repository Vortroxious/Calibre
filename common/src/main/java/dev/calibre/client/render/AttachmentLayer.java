package dev.calibre.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import dev.calibre.Calibre;
import dev.calibre.gun.Attachment;
import dev.calibre.gun.CalibreTickets;
import dev.calibre.gun.GunAttachments;
import dev.calibre.gun.GunItem;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;
import software.bernie.geckolib.cache.GeckoLibResources;
import software.bernie.geckolib.cache.model.BakedGeoModel;
import software.bernie.geckolib.cache.model.GeoBone;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import software.bernie.geckolib.renderer.base.GeoRenderState;
import software.bernie.geckolib.renderer.base.PerBoneRender;
import software.bernie.geckolib.renderer.base.RenderPassInfo;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

import java.util.function.BiConsumer;

/** Draws installed attachments at the gun's socket bones (mount_optic, muzzle, mount_under, mount_side). */
public class AttachmentLayer<T extends GunItem> extends GeoRenderLayer<T, GeoItemRenderer.RenderData, GeoRenderState> {
    public AttachmentLayer(GeoItemRenderer<T> renderer) {
        super(renderer);
    }

    public static String socketFor(Attachment.Slot slot) {
        return switch (slot) {
            case OPTIC -> "mount_optic";
            case MUZZLE -> "muzzle";
            case UNDER -> "mount_under";
            case SIDE -> "mount_side";
            case MAG -> "";
        };
    }

    @Override
    public void addPerBoneRender(RenderPassInfo<GeoRenderState> info, BiConsumer<GeoBone, PerBoneRender<GeoRenderState>> consumer) {
        GunAttachments att = info.getGeckolibData(CalibreTickets.ATTACHMENTS);
        if (att == null || att.isEmpty()) return;
        for (Attachment a : att.all()) {
            if (!a.hasModel()) continue;
            String socket = socketFor(a.slot);
            var bone = info.model().getBone(socket);
            if (bone.isEmpty() && a.slot == Attachment.Slot.SIDE) bone = info.model().getBone("mount_under");
            if (bone.isEmpty()) continue;
            BakedGeoModel model = GeckoLibResources.getBakedModels().getModel(Calibre.id("attachment/" + a.id()));
            if (model == null) continue;
            Identifier tex = Calibre.id("textures/attachment/" + a.id() + ".png");
            consumer.accept(bone.get(), (i, b, tasks) -> tasks.submitCustomGeometry(i.poseStack(), RenderTypes.entityCutoutNoCull(tex),
                    (pose, vc) -> {
                        PoseStack ps = i.poseStack();
                        ps.pushPose();
                        ps.last().set(pose);
                        model.render(i, vc, i.packedLight(), i.packedOverlay(), 0xFFFFFFFF);
                        ps.popPose();
                    }));
        }
    }
}
