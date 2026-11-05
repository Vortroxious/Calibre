package dev.calibre.fabric.mixin;

import dev.calibre.client.CalibreClient;
import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Left click fires and right click aims instead of attacking / using (NeoForge: InteractionKeyMappingTriggered). */
@Mixin(Minecraft.class)
abstract class MinecraftMixin {
    @Inject(method = "startAttack", at = @At("HEAD"), cancellable = true)
    private void calibre$noAttack(CallbackInfoReturnable<Boolean> cir) {
        if (CalibreClient.cancelAttack()) cir.setReturnValue(false);
    }

    @Inject(method = "continueAttack", at = @At("HEAD"), cancellable = true)
    private void calibre$noMining(boolean leftClick, CallbackInfo ci) {
        if (CalibreClient.cancelAttack()) ci.cancel();
    }

    @Inject(method = "startUseItem", at = @At("HEAD"), cancellable = true)
    private void calibre$aimInsteadOfUse(CallbackInfo ci) {
        if (CalibreClient.cancelUse()) ci.cancel();
    }
}
