package dev.calibre.fabric.mixin;

import dev.calibre.client.CalibreClient;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Aim-down-sights zoom (NeoForge: ComputeFovModifierEvent). */
@Mixin(AbstractClientPlayer.class)
abstract class AbstractClientPlayerMixin {
    @Inject(method = "getFieldOfViewModifier", at = @At("RETURN"), cancellable = true)
    private void calibre$adsFov(boolean isFirstPerson, float fovEffectScale, CallbackInfoReturnable<Float> cir) {
        cir.setReturnValue(CalibreClient.fovModifier((Player) (Object) this, cir.getReturnValue()));
    }
}
