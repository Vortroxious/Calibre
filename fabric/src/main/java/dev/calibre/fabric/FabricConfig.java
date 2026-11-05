package dev.calibre.fabric;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.calibre.Calibre;
import dev.calibre.CalibreConfig;
import dev.calibre.platform.Platform;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Fabric has no config system of its own: options live in config/calibre-server.json and config/calibre-client.json
 * (created with defaults and comments on first start) and can be edited in game through Mod Menu.
 */
public final class FabricConfig {
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final Map<CalibreConfig.Opt<?>, Object> VALUES = new ConcurrentHashMap<>();

    private FabricConfig() {}

    @SuppressWarnings("unchecked")
    public static void load() {
        for (CalibreConfig.Opt<?> o : all()) {
            VALUES.put(o, o.def);
            ((CalibreConfig.Opt<Object>) o).bind(() -> VALUES.get(o));
        }
        read(CalibreConfig.SERVER, file("server"));
        read(CalibreConfig.CLIENT, file("client"));
        save();
    }

    public static Object get(CalibreConfig.Opt<?> o) {
        return VALUES.getOrDefault(o, o.def);
    }

    public static void set(CalibreConfig.Opt<?> o, Object value) {
        if (o.isBoolean()) VALUES.put(o, value);
        else VALUES.put(o, Math.max(o.min, Math.min(o.max, ((Number) value).doubleValue())));
    }

    public static void save() {
        write(CalibreConfig.SERVER, file("server"));
        write(CalibreConfig.CLIENT, file("client"));
    }

    private static List<CalibreConfig.Opt<?>> all() {
        return java.util.stream.Stream.concat(CalibreConfig.SERVER.stream(), CalibreConfig.CLIENT.stream()).toList();
    }

    private static Path file(String side) {
        return Platform.INSTANCE.configDir().resolve("calibre-" + side + ".json");
    }

    private static void read(List<CalibreConfig.Opt<?>> opts, Path path) {
        if (!Files.exists(path)) return;
        try {
            JsonObject root = JsonParser.parseString(Files.readString(path, StandardCharsets.UTF_8)).getAsJsonObject();
            for (CalibreConfig.Opt<?> o : opts) {
                JsonObject section = o.section.isEmpty() ? root : root.getAsJsonObject(o.section);
                if (section == null || !section.has(o.name)) continue;
                JsonElement v = section.get(o.name);
                set(o, o.isBoolean() ? (Object) v.getAsBoolean() : (Object) v.getAsDouble());
            }
        } catch (Exception e) {
            Calibre.LOGGER.warn("Could not read {} - using defaults ({})", path, e.toString());
        }
    }

    private static void write(List<CalibreConfig.Opt<?>> opts, Path path) {
        JsonObject root = new JsonObject();
        for (CalibreConfig.Opt<?> o : opts) {
            JsonObject section = root;
            if (!o.section.isEmpty()) {
                if (!root.has(o.section)) root.add(o.section, new JsonObject());
                section = root.getAsJsonObject(o.section);
            }
            section.addProperty("_" + o.name, o.comment + (o.isBoolean() ? "" : " (" + o.min + " - " + o.max + ")"));
            Object v = get(o);
            if (v instanceof Boolean b) section.addProperty(o.name, b);
            else section.addProperty(o.name, ((Number) v).doubleValue());
        }
        try {
            Files.createDirectories(path.getParent());
            Files.writeString(path, GSON.toJson(root), StandardCharsets.UTF_8);
        } catch (IOException e) {
            Calibre.LOGGER.warn("Could not write {} ({})", path, e.toString());
        }
    }
}
