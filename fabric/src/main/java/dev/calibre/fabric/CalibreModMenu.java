package dev.calibre.fabric;

import com.terraformersmc.modmenu.api.ConfigScreenFactory;
import com.terraformersmc.modmenu.api.ModMenuApi;

/** Optional Mod Menu integration: the "Config" button opens {@link CalibreConfigScreen}. */
public final class CalibreModMenu implements ModMenuApi {
    @Override
    public ConfigScreenFactory<?> getModConfigScreenFactory() {
        return CalibreConfigScreen::new;
    }
}
