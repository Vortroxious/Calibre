package dev.calibre.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import dev.calibre.gun.CalibreTickets;
import dev.calibre.gun.GunItem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.player.PlayerModel;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.player.PlayerModelPart;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import software.bernie.geckolib.cache.model.GeoBone;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import software.bernie.geckolib.renderer.base.GeoRenderState;
import software.bernie.geckolib.renderer.base.PerBoneRender;
import software.bernie.geckolib.renderer.base.RenderPassInfo;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

import java.util.function.BiConsumer;

/**
 * First-person arms, drawn with the player's own skin at the gun model's arm_right / arm_left bones.
 * The hand sits at the bone pivot; the forearm always points back to a fixed shoulder anchor in view space, so
 * whatever the animation does with the hands, the arms stay anatomically plausible (same rule as tools/preview.py).
 */
public class ArmsLayer extends GeoRenderLayer<GunItem, GeoItemRenderer.RenderData, GeoRenderState> {
    /** shoulder anchors, view space, metres */
    private static final Vector3f SHOULDER_R = new Vector3f(0.22f, -0.55f, 0.02f);
    private static final Vector3f SHOULDER_L = new Vector3f(-0.2f, -0.55f, 0.02f);
    /** model-space mm -> GeckoLib local units (1 cm per unit, /16) */
    private static final float MM = 0.1f / 16f;
    private static final float ARM_W = 60f, ARM_FIST = 40f, ARM_LEN = 330f;

    public ArmsLayer(GeoItemRenderer<GunItem> renderer) {
        super(renderer);
    }

    @Override
    public void addPerBoneRender(RenderPassInfo<GeoRenderState> info, BiConsumer<GeoBone, PerBoneRender<GeoRenderState>> consumer) {
        if (!Boolean.TRUE.equals(info.getGeckolibData(CalibreTickets.FIRST_PERSON))) return;
        if (Boolean.TRUE.equals(info.getGeckolibData(CalibreTickets.HIDE_ARMS))) return;
        info.model().getBone("arm_right").ifPresent(b -> consumer.accept(b, (i, bone, tasks) -> arm(i, tasks, true)));
        info.model().getBone("arm_left").ifPresent(b -> consumer.accept(b, (i, bone, tasks) -> arm(i, tasks, false)));
    }

    private static void arm(RenderPassInfo<GeoRenderState> info, SubmitNodeCollector tasks, boolean right) {
        Minecraft mc = Minecraft.getInstance();
        if (!(mc.player instanceof AbstractClientPlayer player) || player.isInvisible()) return;
        PoseStack ps = info.poseStack();
        Matrix4f inv = new Matrix4f(ps.last().pose()).invert();
        Vector3f shoulder = inv.transformPosition(new Vector3f(right ? SHOULDER_R : SHOULDER_L));
        float len = shoulder.length();
        if (len < 1e-4f) return;
        Vector3f fwd = new Vector3f(shoulder).normalize();            // hand -> shoulder, bone local
        Vector3f up = new Vector3f(0, 1, 0);
        Vector3f side = new Vector3f(up).cross(fwd);
        if (side.lengthSquared() < 1e-6f) side.set(1, 0, 0);
        side.normalize();
        up.set(fwd).cross(side).normalize();
        // ModelPart arm: +Y runs from the shoulder (top) to the hand (y = 10 px). Columns: X->side, Y->-fwd, Z->up
        Matrix3f basis = new Matrix3f(side.x, side.y, side.z, -fwd.x, -fwd.y, -fwd.z, up.x, up.y, up.z);
        Quaternionf rot = basis.getNormalizedRotation(new Quaternionf());

        PlayerModel model = mc.getEntityRenderDispatcher().getPlayerRenderer(player).getModel();
        ModelPart part = right ? model.rightArm : model.leftArm;
        part.resetPose();
        part.x = part.y = part.z = 0;
        part.xRot = part.yRot = part.zRot = 0;
        part.visible = true;
        model.rightSleeve.visible = player.isModelPartShown(PlayerModelPart.RIGHT_SLEEVE);
        model.leftSleeve.visible = player.isModelPartShown(PlayerModelPart.LEFT_SLEEVE);
        boolean slim = isSlim(player);
        float cubeCentreX = (right ? -1f : 1f) * (slim ? 0.5f : 1f);
        float cubeWidthMm = slim ? 30f : 40f;
        // always reach the shoulder anchor (below the screen edge), so a hand that is moved out never leaves the
        // forearm hanging in the air
        float visibleMm = Math.max(ARM_LEN, len / MM + ARM_FIST);

        ps.pushPose();
        Vector3f handEnd = new Vector3f(fwd).mul(-ARM_FIST * MM);
        ps.translate(handEnd.x, handEnd.y, handEnd.z);
        ps.mulPose(rot);
        ps.scale(ARM_W / cubeWidthMm, visibleMm / 120f, ARM_W / 40f);
        ps.translate(-cubeCentreX / 16f, -10f / 16f, 0);
        Identifier skin = player.getSkin().body().texturePath();
        tasks.submitModelPart(part, ps, RenderTypes.entityTranslucent(skin), info.packedLight(), OverlayTexture.NO_OVERLAY, null);
        ps.popPose();
    }

    private static boolean isSlim(AbstractClientPlayer p) {
        return p.getSkin().model() == net.minecraft.world.entity.player.PlayerModelType.SLIM;
    }
}
