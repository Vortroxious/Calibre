package dev.calibre.fabric;

import dev.calibre.Calibre;
import dev.calibre.client.CalibreClient;
import dev.calibre.client.CalibreKeys;
import dev.calibre.client.GunHud;
import dev.calibre.client.WorkbenchScreen;
import dev.calibre.client.render.BulletRenderer;
import dev.calibre.client.render.MercenaryRenderer;
import dev.calibre.network.Net;
import dev.calibre.registry.ModRegistry;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;
import software.bernie.geckolib.renderer.specialty.DirectionalProjectileRenderer;

/** Fabric client entry point. */
public final class CalibreFabricClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        CalibreClient.init();
        dev.calibre.client.ClientAutoTest.CONFIG_SCREEN = CalibreConfigScreen::new;
        ClientPlayNetworking.registerGlobalReceiver(Net.ActionPayload.TYPE, (p, ctx) -> Net.CLIENT.onAction(p));
        ClientPlayNetworking.registerGlobalReceiver(Net.HitPayload.TYPE, (p, ctx) -> Net.CLIENT.onHit(p));

        CalibreKeys.ALL.forEach(KeyBindingHelper::registerKeyBinding);

        EntityRendererRegistry.register(ModRegistry.BULLET.get(), BulletRenderer::new);
        EntityRendererRegistry.register(ModRegistry.ROCKET.get(), (EntityRendererProvider.Context ctx) ->
                new DirectionalProjectileRenderer<>(ctx, new DefaultedEntityGeoModel<>(Calibre.id("rocket"))));
        EntityRendererRegistry.register(ModRegistry.MERCENARY.get(), MercenaryRenderer::new);
        MenuScreens.register(ModRegistry.WORKBENCH_MENU.get(), WorkbenchScreen::new);

        HudElementRegistry.attachElementBefore(VanillaHudElements.HOTBAR, GunHud.SCOPE_LAYER, GunHud::renderScope);
        HudElementRegistry.attachElementAfter(VanillaHudElements.CROSSHAIR, GunHud.LAYER, GunHud::render);
        HudElementRegistry.replaceElement(VanillaHudElements.CROSSHAIR, vanilla -> (HudElement) (g, dt) -> {
            if (!GunHud.hideVanillaCrosshair()) vanilla.render(g, dt);
        });

        ClientTickEvents.END_CLIENT_TICK.register(mc -> CalibreClient.clientTick());
    }
}
