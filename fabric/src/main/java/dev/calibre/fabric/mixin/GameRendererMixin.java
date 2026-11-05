package dev.calibre.fabric.mixin;

import dev.calibre.client.CalibreClient;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.renderer.GameRenderer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Per-frame gun motion (NeoForge: RenderFrameEvent.Pre). */
@Mixin(GameRenderer.class)
abstract class GameRendererMixin {
    @Inject(method = "render", at = @At("HEAD"))
    private void calibre$frame(DeltaTracker deltaTracker, boolean renderLevel, CallbackInfo ci) {
        CalibreClient.frame();
    }
}
