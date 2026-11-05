package dev.calibre.fabric.mixin;

import com.mojang.blaze3d.vertex.PoseStack;
import dev.calibre.client.render.FirstPersonRenderer;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** First-person guns (NeoForge: RenderHandEvent). */
@Mixin(ItemInHandRenderer.class)
abstract class ItemInHandRendererMixin {
    @Inject(method = "renderArmWithItem", at = @At("HEAD"), cancellable = true)
    private void calibre$renderGun(AbstractClientPlayer player, float partialTick, float pitch, InteractionHand hand, float swingProgress,
                                   ItemStack item, float equippedProgress, PoseStack poseStack, SubmitNodeCollector collector,
                                   int packedLight, CallbackInfo ci) {
        if (FirstPersonRenderer.renderHand(hand, item, poseStack, collector, packedLight, partialTick, equippedProgress)) ci.cancel();
    }
}
