package dev.calibre.client.render;

import dev.calibre.Calibre;
import dev.calibre.client.ClientGun;
import dev.calibre.gun.CalibreTickets;
import dev.calibre.gun.GunItem;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;
import software.bernie.geckolib.model.DefaultedItemGeoModel;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import software.bernie.geckolib.renderer.base.BoneSnapshots;
import software.bernie.geckolib.renderer.base.GeoRenderState;
import software.bernie.geckolib.renderer.base.RenderPassInfo;
import software.bernie.geckolib.constant.DataTickets;

/**
 * GeckoLib renderer for every gun. Models are authored at 1 unit = 1 cm, so a uniform {@link #SCALE} brings them to
 * real-world size (1 block = 1 m). First-person placement is done by {@link FirstPersonRenderer}; every other context
 * uses the item model display transforms.
 */
public class GunRenderer extends GeoItemRenderer<GunItem> {
    public static final float SCALE = 0.16f;
    private final String[] spareBones;

    public GunRenderer(GunItem item) {
        super(new DefaultedItemGeoModel<GunItem>(Calibre.id(item.def().id())) {
            // gun textures live outside textures/item so they stay out of the vanilla item atlas
            @Override
            public net.minecraft.resources.Identifier buildFormattedTexturePath(net.minecraft.resources.Identifier base) {
                return base.withPath("textures/gun/" + base.getPath() + ".png");
            }
        });
        spareBones = item.meta().spareBones.toArray(String[]::new);
        withScale(SCALE);
        withRenderLayer(new ArmsLayer(this));
        withRenderLayer(new AttachmentLayer<>(this));
        withRenderLayer(new MuzzleFlashLayer(this));
    }

    @Override
    public void addRenderData(GunItem gun, @Nullable RenderData data, GeoRenderState state, float partialTick) {
        if (data == null) return;
        ItemStack stack = data.itemStack();
        boolean fp = FirstPersonRenderer.RENDERING && data.renderPerspective().firstPerson();
        state.addGeckolibData(CalibreTickets.EMPTY, GunItem.state(stack).total() == 0 && !ClientGun.isBusy(stack));
        state.addGeckolibData(CalibreTickets.FIRST_PERSON, fp);
        state.addGeckolibData(CalibreTickets.ATTACHMENTS, GunItem.attachments(stack));
        float flash = 0;
        if (fp) flash = ClientGun.flashAlpha(partialTick);
        else if (data.itemOwner() != null && data.renderPerspective() != ItemDisplayContext.GUI) flash = ClientGun.flashFor(data.itemOwner());
        state.addGeckolibData(CalibreTickets.FLASH, GunItem.attachments(stack).suppressed() ? 0f : flash);
    }

    private static ItemDisplayContext ctx(RenderPassInfo<GeoRenderState> info) {
        ItemDisplayContext c = info.getGeckolibData(DataTickets.ITEM_RENDER_PERSPECTIVE);
        return c == null ? ItemDisplayContext.NONE : c;
    }

    @Override
    public void adjustRenderPose(RenderPassInfo<GeoRenderState> info) {
        if (Boolean.TRUE.equals(info.getGeckolibData(CalibreTickets.FIRST_PERSON))) return;
        // GeoItemRenderer centres the model with +0.5; compensate because we are already scaled down
        info.poseStack().translate(0.5f / SCALE, 0.5f / SCALE, 0.5f / SCALE);
    }

    @Override
    public void applyAnimationControllers(RenderPassInfo<GeoRenderState> info, BoneSnapshots snapshots) {
        ItemDisplayContext c = ctx(info);
        boolean fp = Boolean.TRUE.equals(info.getGeckolibData(CalibreTickets.FIRST_PERSON));
        boolean third = c == ItemDisplayContext.THIRD_PERSON_RIGHT_HAND || c == ItemDisplayContext.THIRD_PERSON_LEFT_HAND;
        // Spare parts (stripper clip, loose round, ejected brass, shells, speedloader) are modelled at the place they
        // are used. Start them collapsed: an animation that uses them keys their scale back to 1, and any frame without
        // an animation (icons, the first frame after a draw, a controller in transition) never shows them floating.
        for (String b : spareBones) snapshots.ifPresent(b, sn -> sn.setScale(0, 0, 0));
        if (!fp && !third) return; // icons, item frames, dropped items: static rest pose
        super.applyAnimationControllers(info, snapshots);
        if (third) {
            // in third person the whole-gun motion is carried by the player's arms; keep only the mechanisms
            snapshots.ifPresent("gun", s -> {
                s.setTranslation(0, 0, 0);
                s.setRotation(0, 0, 0);
            });
        }
    }
}
