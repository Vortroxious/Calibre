package dev.calibre.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import dev.calibre.CalibreConfig;
import dev.calibre.client.ClientGun;
import dev.calibre.gun.Attachment;
import dev.calibre.gun.GunAttachments;
import dev.calibre.gun.GunItem;
import dev.calibre.gun.GunMeta;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import org.joml.Vector3f;
import software.bernie.geckolib.animatable.client.GeoRenderProvider;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import software.bernie.geckolib.renderer.base.GeoRenderState;

/**
 * Replaces vanilla first-person hand rendering for guns. The gun is placed in view space (metres) by blending the
 * generated hip pose with an ADS pose that puts the sight (iron sight, attached optic eye point, or integral scope)
 * exactly on the view axis, then layers sway, recoil springs, sprint and equip motion on top.
 */
public final class FirstPersonRenderer {
    public static boolean RENDERING = false;

    private FirstPersonRenderer() {}

    /** eye point (model space, mm) used for aiming */
    public static float[] eyePoint(GunItem gun, ItemStack stack) {
        GunMeta meta = gun.meta();
        if (meta.integralEye != null) return meta.integralEye;
        GunAttachments att = GunItem.attachments(stack);
        Attachment optic = att.get(Attachment.Slot.OPTIC);
        float[] mount = meta.sockets.get("mount_optic");
        if (optic != null && mount != null) {
            GunMeta.AttachmentMeta am = GunMeta.AttachmentMeta.get(optic.id());
            if (am.eye != null) return new float[]{mount[0] + am.eye[0], mount[1] + am.eye[1], mount[2] + am.eye[2]};
        }
        return meta.sight;
    }

    /**
     * Called for each hand by the loader's first-person hand hook. Returns true when Calibre drew the gun (or hid the
     * off hand) and vanilla must skip this hand.
     */
    public static boolean renderHand(InteractionHand hand, ItemStack handStack, PoseStack ps, SubmitNodeCollector collector,
                                     int packedLight, float pt, float equipProgress) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null) return false;
        ItemStack main = p.getMainHandItem();
        if (hand == InteractionHand.OFF_HAND) return main.getItem() instanceof GunItem; // both hands are on the gun
        if (!(handStack.getItem() instanceof GunItem gun)) return false;
        if (ClientGun.scoped(pt)) return true; // looking through the scope overlay

        GunMeta meta = gun.meta();
        ItemStack stack = handStack;
        float a = ClientGun.adsEased(pt);
        float[] eye = eyePoint(gun, stack);
        float dist = meta.adsDist;
        Vector3f hipPos = new Vector3f(meta.hipPos[0], meta.hipPos[1], meta.hipPos[2]);
        if (gun.def().twoHanded()) hipPos.add(0.005f, -0.012f, -0.075f); // long guns sit a little further out at the hip
        Vector3f adsPos = new Vector3f(-eye[0] * 0.001f, -eye[1] * 0.001f, -dist - eye[2] * 0.001f);
        Vector3f pos = hipPos.lerp(adsPos, a, new Vector3f());
        float rx = Mth.lerp(a, meta.hipRot[0], 0), ry = Mth.lerp(a, meta.hipRot[1], 0), rz = Mth.lerp(a, meta.hipRot[2], 0);

        // sway (lags behind mouse movement)
        rx += ClientGun.SWAY_Y.x * 0.6f;
        ry += ClientGun.SWAY_X.x * 0.6f;
        rz += ClientGun.SWAY_X.x * 0.8f;
        pos.add(ClientGun.SWAY_X.x * -0.0012f, ClientGun.SWAY_Y.x * 0.0012f, 0);
        // walking bob (on top of vanilla view bobbing), reduced when aiming
        float bobMul = (float) CalibreConfig.client(CalibreConfig.BOB, 1.0) * (1 - 0.85f * a);
        float walk = p.avatarState().getBackwardsInterpolatedWalkDistance(pt);
        float speed = p.avatarState().getInterpolatedBob(pt);
        pos.add(Mth.sin(walk * Mth.PI) * speed * 0.012f * bobMul, -Math.abs(Mth.cos(walk * Mth.PI)) * speed * 0.016f * bobMul, 0);
        rz += Mth.sin(walk * Mth.PI) * speed * 1.6f * bobMul;
        // breathing when aiming
        float t = (p.tickCount + pt) / 20f;
        rx += Mth.sin(t * 1.6f) * 0.25f * a;
        ry += Mth.cos(t * 1.1f) * 0.2f * a;
        // recoil springs
        rx += ClientGun.KICK_PITCH.x;
        ry += ClientGun.KICK_YAW.x;
        rz += ClientGun.KICK_ROLL.x;
        pos.z += ClientGun.KICK_BACK.x * 0.012f;
        // sprint pose
        float sp = ClientGun.SPRINT.x;
        pos.add(-0.03f * sp, -0.05f * sp, 0.02f * sp);
        rx += -16 * sp;
        ry += 34 * sp;
        rz += 12 * sp;
        // equip
        pos.y -= equipProgress * 0.5f;

        ps.pushPose();
        ps.translate(pos.x, pos.y, pos.z);
        ps.mulPose(Axis.YP.rotationDegrees(ry));
        ps.mulPose(Axis.XP.rotationDegrees(rx));
        ps.mulPose(Axis.ZP.rotationDegrees(rz));

        @SuppressWarnings("unchecked")
        GeoItemRenderer<GunItem> renderer = (GeoItemRenderer<GunItem>) GeoRenderProvider.of(gun).getGeoItemRenderer();
        if (renderer != null) {
            GeoItemRenderer.RenderData data = new GeoItemRenderer.RenderData(stack, new ItemStackRenderState(),
                    ItemDisplayContext.FIRST_PERSON_RIGHT_HAND, mc.level, p);
            RENDERING = true;
            try {
                GeoRenderState state = renderer.fillRenderState(gun, data, renderer.createRenderState(gun, data), pt);
                state.addGeckolibData(DataTickets.PACKED_LIGHT, packedLight);
                state.addGeckolibData(DataTickets.PACKED_OVERLAY, OverlayTexture.NO_OVERLAY);
                state.addGeckolibData(DataTickets.HAS_GLINT, false);
                renderer.submit(state, ps, collector, 0);
            } finally {
                RENDERING = false;
            }
        }
        ps.popPose();
        return true;
    }
}
