package dev.calibre.fabric.mixin;

import dev.calibre.client.CalibreClient;
import net.minecraft.client.Camera;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** CS2-style camera motion on the first-person view only (NeoForge: ViewportEvent.ComputeCameraAngles). */
@Mixin(Camera.class)
abstract class CameraMixin {
    @Shadow private float xRot;
    @Shadow private float yRot;
    @Shadow @Final private Quaternionf rotation;
    @Shadow @Final private Vector3f forwards;
    @Shadow @Final private Vector3f up;
    @Shadow @Final private Vector3f left;
    @Shadow @Final private static Vector3f FORWARDS;
    @Shadow @Final private static Vector3f UP;
    @Shadow @Final private static Vector3f LEFT;

    @Inject(method = "setup", at = @At("TAIL"))
    private void calibre$cameraMotion(Level level, Entity entity, boolean detached, boolean mirror, float partialTick,
                                      CallbackInfo ci) {
        if (detached) return;
        float[] o = CalibreClient.cameraShake();
        if (o[0] == 0 && o[1] == 0 && o[2] == 0) return;
        // same as vanilla setRotation, with roll
        this.xRot += o[0];
        this.yRot += o[1];
        this.rotation.rotationYXZ((float) Math.PI - this.yRot * (float) (Math.PI / 180.0),
                -this.xRot * (float) (Math.PI / 180.0), -o[2] * (float) (Math.PI / 180.0));
        FORWARDS.rotate(this.rotation, this.forwards);
        UP.rotate(this.rotation, this.up);
        LEFT.rotate(this.rotation, this.left);
    }
}
