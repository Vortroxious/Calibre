package dev.calibre.neoforge;

import dev.calibre.Calibre;
import dev.calibre.client.CalibreClient;
import dev.calibre.client.CalibreKeys;
import dev.calibre.client.GunHud;
import dev.calibre.client.WorkbenchScreen;
import dev.calibre.client.render.BulletRenderer;
import dev.calibre.client.render.FirstPersonRenderer;
import dev.calibre.client.render.MercenaryRenderer;
import dev.calibre.registry.ModRegistry;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.client.event.CalculatePlayerTurnEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.ComputeFovModifierEvent;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.InputEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import net.neoforged.neoforge.client.event.RenderFrameEvent;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import net.neoforged.neoforge.client.event.RenderHandEvent;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;
import net.neoforged.neoforge.client.extensions.common.RegisterClientExtensionsEvent;
import net.neoforged.neoforge.client.gui.ConfigurationScreen;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.common.NeoForge;
import org.jspecify.annotations.Nullable;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;
import software.bernie.geckolib.renderer.specialty.DirectionalProjectileRenderer;

/** NeoForge client entry point. */
@Mod(value = Calibre.MODID, dist = Dist.CLIENT)
public class CalibreNeoClient {
    public CalibreNeoClient(IEventBus modBus, ModContainer container) {
        CalibreClient.init();
        container.registerExtensionPoint(IConfigScreenFactory.class, ConfigurationScreen::new);
        dev.calibre.client.ClientAutoTest.CONFIG_SCREEN = parent -> new ConfigurationScreen(container, parent);
        modBus.addListener((RegisterKeyMappingsEvent e) -> {
            e.registerCategory(CalibreKeys.CATEGORY);
            CalibreKeys.ALL.forEach(e::register);
        });
        modBus.addListener(CalibreNeoClient::renderers);
        modBus.addListener((RegisterMenuScreensEvent e) -> e.register(ModRegistry.WORKBENCH_MENU.get(), WorkbenchScreen::new));
        modBus.addListener((RegisterGuiLayersEvent e) -> {
            e.registerBelow(VanillaGuiLayers.HOTBAR, GunHud.SCOPE_LAYER, GunHud::renderScope);
            e.registerAbove(VanillaGuiLayers.CROSSHAIR, GunHud.LAYER, GunHud::render);
        });
        modBus.addListener(CalibreNeoClient::extensions);

        NeoForge.EVENT_BUS.addListener((ClientTickEvent.Post e) -> CalibreClient.clientTick());
        NeoForge.EVENT_BUS.addListener((RenderFrameEvent.Pre e) -> CalibreClient.frame());
        NeoForge.EVENT_BUS.addListener((RenderHandEvent e) -> {
            if (FirstPersonRenderer.renderHand(e.getHand(), e.getItemStack(), e.getPoseStack(), e.getSubmitNodeCollector(),
                    e.getPackedLight(), e.getPartialTick(), e.getEquipProgress())) e.setCanceled(true);
        });
        NeoForge.EVENT_BUS.addListener((RenderGuiLayerEvent.Pre e) -> {
            if (e.getName().equals(VanillaGuiLayers.CROSSHAIR) && GunHud.hideVanillaCrosshair()) e.setCanceled(true);
        });
        NeoForge.EVENT_BUS.addListener(CalibreNeoClient::onInput);
        NeoForge.EVENT_BUS.addListener((ComputeFovModifierEvent e) ->
                e.setNewFovModifier(CalibreClient.fovModifier(e.getPlayer(), e.getNewFovModifier())));
        NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.client.event.ViewportEvent.ComputeCameraAngles e) -> {
            float[] o = CalibreClient.cameraShake();
            if (o[0] == 0 && o[1] == 0 && o[2] == 0) return;
            e.setPitch(e.getPitch() + o[0]);
            e.setYaw(e.getYaw() + o[1]);
            e.setRoll(e.getRoll() + o[2]);
        });
        NeoForge.EVENT_BUS.addListener((CalculatePlayerTurnEvent e) ->
                e.setMouseSensitivity(CalibreClient.sensitivity(e.getMouseSensitivity())));
    }

    private static void renderers(EntityRenderersEvent.RegisterRenderers e) {
        e.registerEntityRenderer(ModRegistry.BULLET.get(), BulletRenderer::new);
        e.registerEntityRenderer(ModRegistry.ROCKET.get(),
                (EntityRendererProvider.Context ctx) -> new DirectionalProjectileRenderer<>(ctx,
                        new DefaultedEntityGeoModel<>(Calibre.id("rocket"))));
        e.registerEntityRenderer(ModRegistry.MERCENARY.get(), MercenaryRenderer::new);
    }

    private static void extensions(RegisterClientExtensionsEvent e) {
        IClientItemExtensions ext = new IClientItemExtensions() {
            @Override
            public HumanoidModel.@Nullable ArmPose getArmPose(LivingEntity entity, InteractionHand hand, ItemStack stack) {
                return HumanoidModel.ArmPose.BOW_AND_ARROW;
            }
        };
        e.registerItem(ext, ModRegistry.GUNS.values().stream().map(h -> (Item) h.get()).toArray(Item[]::new));
    }

    private static void onInput(InputEvent.InteractionKeyMappingTriggered e) {
        if (e.getHand() != InteractionHand.MAIN_HAND) return;
        boolean cancel = e.isAttack() ? CalibreClient.cancelAttack() : e.isUseItem() && CalibreClient.cancelUse();
        if (cancel) {
            e.setCanceled(true);
            e.setSwingHand(false);
        }
    }
}
