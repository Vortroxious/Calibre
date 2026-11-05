package dev.calibre.gun;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;

import java.util.function.Consumer;

public class AmmoItem extends Item {
    private final Caliber caliber;

    public AmmoItem(Properties props, Caliber caliber) {
        super(props);
        this.caliber = caliber;
    }

    public Caliber caliber() {
        return caliber;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> tip, TooltipFlag flag) {
        tip.accept(Component.literal(caliber.displayName).withStyle(ChatFormatting.GRAY));
        StringBuilder users = new StringBuilder();
        for (GunDefinition g : Guns.all()) {
            if (g.caliber() == caliber) {
                if (!users.isEmpty()) users.append(", ");
                users.append(Component.translatable("item.calibre." + g.id()).getString());
            }
        }
        if (!users.isEmpty()) tip.accept(Component.literal(users.toString()).withStyle(ChatFormatting.DARK_GRAY));
    }
}
