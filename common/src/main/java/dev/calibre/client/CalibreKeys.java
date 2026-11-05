package dev.calibre.client;

import com.mojang.blaze3d.platform.InputConstants;
import dev.calibre.Calibre;
import net.minecraft.client.KeyMapping;
import org.lwjgl.glfw.GLFW;

import java.util.List;

/** Key mappings; each loader registers {@link #ALL} and {@link #CATEGORY}. */
public final class CalibreKeys {
    public static final KeyMapping.Category CATEGORY = new KeyMapping.Category(Calibre.id("calibre"));
    public static final KeyMapping RELOAD = new KeyMapping("key.calibre.reload", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_R, CATEGORY);
    public static final KeyMapping FIRE_MODE = new KeyMapping("key.calibre.fire_mode", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_V, CATEGORY);
    public static final KeyMapping INSPECT = new KeyMapping("key.calibre.inspect", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_H, CATEGORY);
    public static final List<KeyMapping> ALL = List.of(RELOAD, FIRE_MODE, INSPECT);

    private CalibreKeys() {}
}
