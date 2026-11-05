package dev.calibre.fabric.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import dev.calibre.client.CalibreClient;
import net.minecraft.client.MouseHandler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Lower mouse sensitivity through magnified optics (NeoForge: CalculatePlayerTurnEvent). */
@Mixin(MouseHandler.class)
abstract class MouseHandlerMixin {
    @ModifyExpressionValue(method = "turnPlayer",
            at = @At(value = "INVOKE", target = "Lnet/minecraft/client/OptionInstance;get()Ljava/lang/Object;", ordinal = 0))
    private Object calibre$adsSensitivity(Object sensitivity) {
        return sensitivity instanceof Double d ? CalibreClient.sensitivity(d) : sensitivity;
    }
}
