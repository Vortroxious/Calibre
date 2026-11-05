package dev.calibre.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.calibre.Calibre;
import dev.calibre.ballistics.BulletEntity;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

/** Bullets render as a short streak along their velocity; tracers are long, bright and emissive. */
public class BulletRenderer extends EntityRenderer<BulletEntity, BulletRenderer.State> {
    private static final Identifier TEX = Calibre.id("textures/entity/tracer.png");

    public static class State extends EntityRenderState {
        Vec3 vel = Vec3.ZERO;
        boolean tracer;
        int color;
        int life;
    }

    public BulletRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
    }

    @Override
    public State createRenderState() {
        return new State();
    }

    @Override
    public void extractRenderState(BulletEntity e, State s, float pt) {
        super.extractRenderState(e, s, pt);
        s.vel = e.getDeltaMovement();
        s.tracer = e.isTracer();
        s.color = e.color();
        s.life = e.life();
    }

    @Override
    public void submit(State s, PoseStack ps, SubmitNodeCollector tasks, CameraRenderState cam) {
        if (s.life < 1) return;
        double speed = s.vel.length();
        if (speed < 1e-3) return;
        float len = (float) Math.min(speed * (s.tracer ? 0.9 : 0.5), s.tracer ? 12 : 5);
        float w = s.tracer ? 0.035f : 0.012f;
        int a = s.tracer ? 255 : 90;
        int r = s.tracer ? (s.color >> 16) & 255 : 255, g = s.tracer ? (s.color >> 8) & 255 : 240, b = s.tracer ? s.color & 255 : 200;
        Vector3f dir = new Vector3f((float) (s.vel.x / speed), (float) (s.vel.y / speed), (float) (s.vel.z / speed));
        // camera-facing ribbon
        Vec3 camPos = cam.pos;
        Vector3f toCam = new Vector3f((float) (camPos.x - s.x), (float) (camPos.y - s.y), (float) (camPos.z - s.z));
        Vector3f side = new Vector3f(dir).cross(toCam);
        if (side.lengthSquared() < 1e-6f) side.set(0, 1, 0);
        side.normalize(w);
        Vector3f tail = new Vector3f(dir).mul(-len);
        tasks.submitCustomGeometry(ps, RenderTypes.entityTranslucentEmissive(TEX), (pose, vc) -> {
            v(vc, pose, side.x, side.y, side.z, 0, 0, r, g, b, a);
            v(vc, pose, -side.x, -side.y, -side.z, 0, 1, r, g, b, a);
            v(vc, pose, tail.x - side.x, tail.y - side.y, tail.z - side.z, 1, 1, r, g, b, 0);
            v(vc, pose, tail.x + side.x, tail.y + side.y, tail.z + side.z, 1, 0, r, g, b, 0);
        });
    }

    private static void v(VertexConsumer vc, PoseStack.Pose pose, float x, float y, float z, float u, float v, int r, int g, int b, int a) {
        vc.addVertex(pose, x, y, z).setColor(r, g, b, a).setUv(u, v).setOverlay(OverlayTexture.NO_OVERLAY).setLight(0xF000F0)
                .setNormal(pose, 0, 1, 0);
    }
}
