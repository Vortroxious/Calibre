package dev.calibre.client.render;

import dev.calibre.Calibre;
import dev.calibre.entity.MercenaryEntity;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import net.minecraft.resources.Identifier;

public class MercenaryRenderer extends HumanoidMobRenderer<MercenaryEntity, HumanoidRenderState, HumanoidModel<HumanoidRenderState>> {
    private static final Identifier TEX = Calibre.id("textures/entity/mercenary.png");

    public MercenaryRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new HumanoidModel<>(ctx.bakeLayer(ModelLayers.ZOMBIE)), 0.5f);
    }

    @Override
    public HumanoidRenderState createRenderState() {
        return new HumanoidRenderState();
    }

    @Override
    public void extractRenderState(MercenaryEntity e, HumanoidRenderState s, float pt) {
        super.extractRenderState(e, s, pt);
        if (MercenaryEntity.holdsGun(e)) {
            s.rightArmPose = HumanoidModel.ArmPose.BOW_AND_ARROW;
            s.leftArmPose = HumanoidModel.ArmPose.BOW_AND_ARROW;
        }
    }

    @Override
    public Identifier getTextureLocation(HumanoidRenderState s) {
        return TEX;
    }
}
