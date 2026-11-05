package dev.calibre.gun;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.calibre.Calibre;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Generated per-gun data (tools/build_assets.py -> calibre_gen/guns/&lt;id&gt;.json): animation lengths, sound timelines,
 * logic events (when the round actually goes in), sockets and first-person offsets. Loaded from the classpath on both
 * sides so the server times reloads exactly like the client animates them.
 */
public final class GunMeta {
    public record Timed(float time, String name) {}

    public record Action(float length, List<Timed> sounds, List<Timed> events) {
        public float event(String name, float fallback) {
            for (Timed t : events) if (t.name.equals(name)) return t.time;
            return fallback;
        }

        public int ticks() {
            return Math.max(1, Math.round(length * 20f));
        }
    }

    public final String id;
    public final Map<String, Action> actions = new HashMap<>();
    public final Map<String, float[]> sockets = new HashMap<>();
    public float[] hipPos = {0.12f, -0.13f, -0.2f};
    public float[] hipRot = {0, 3, 0};
    public float adsDist = 0.1f;
    public float[] sight = {0, 30, 0};
    public float[] muzzle = {0, 0, -300};
    public float integralZoom = 0f;
    public float[] integralEye = null;
    public String integralReticle = null;
    /** bones hidden unless an animation shows them (clip, spare round, ejected brass, shells, speedloader) */
    public final List<String> spareBones = new ArrayList<>();
    /** bones that do not exist while the gun is empty (e.g. the RPG-7's rocket) */
    public final List<String> emptyHidden = new ArrayList<>();
    /** CS2-style view motion per animation: flat [pitch, yaw, roll] degrees at cameraRate[anim] samples/s */
    public final Map<String, float[]> camera = new HashMap<>();
    public final Map<String, Float> cameraRate = new HashMap<>();

    // read from both the integrated server thread and the render thread
    private static final Map<String, GunMeta> CACHE = new java.util.concurrent.ConcurrentHashMap<>();

    private GunMeta(String id) {
        this.id = id;
    }

    public static GunMeta get(String id) {
        GunMeta m = CACHE.get(id);
        if (m == null) {
            m = load(id);   // loading outside the map: a racing thread may load the same file once more, which is harmless
            GunMeta prev = CACHE.putIfAbsent(id, m);
            if (prev != null) m = prev;
        }
        return m;
    }

    public Action action(String name) {
        return actions.get(name);
    }

    public boolean has(String name) {
        return actions.containsKey(name);
    }

    private static float[] arr(JsonElement e) {
        JsonArray a = e.getAsJsonArray();
        float[] out = new float[a.size()];
        for (int i = 0; i < out.length; i++) out[i] = a.get(i).getAsFloat();
        return out;
    }

    private static GunMeta load(String id) {
        GunMeta meta = new GunMeta(id);
        String path = "/calibre_gen/guns/" + id + ".json";
        try (InputStream in = GunMeta.class.getResourceAsStream(path)) {
            if (in == null) {
                Calibre.LOGGER.error("Missing generated gun meta {}", path);
                return meta;
            }
            JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            JsonObject actions = root.getAsJsonObject("actions");
            for (Map.Entry<String, JsonElement> e : actions.entrySet()) {
                JsonObject a = e.getValue().getAsJsonObject();
                meta.actions.put(e.getKey(), new Action(a.get("length").getAsFloat(), timed(a.getAsJsonArray("sounds")),
                        timed(a.getAsJsonArray("events"))));
            }
            if (root.has("sockets")) {
                for (Map.Entry<String, JsonElement> e : root.getAsJsonObject("sockets").entrySet())
                    meta.sockets.put(e.getKey(), arr(e.getValue()));
            }
            if (root.has("hip")) {
                JsonObject hip = root.getAsJsonObject("hip");
                meta.hipPos = arr(hip.get("pos"));
                meta.hipRot = arr(hip.get("rot"));
            }
            if (root.has("ads")) meta.adsDist = root.getAsJsonObject("ads").get("dist").getAsFloat();
            if (root.has("sight")) meta.sight = arr(root.get("sight"));
            if (root.has("spare_bones")) for (JsonElement e : root.getAsJsonArray("spare_bones")) meta.spareBones.add(e.getAsString());
            if (root.has("empty_hidden")) for (JsonElement e : root.getAsJsonArray("empty_hidden")) meta.emptyHidden.add(e.getAsString());
            if (root.has("muzzle")) meta.muzzle = arr(root.get("muzzle"));
            if (root.has("camera")) {
                for (Map.Entry<String, JsonElement> e : root.getAsJsonObject("camera").entrySet()) {
                    JsonObject c = e.getValue().getAsJsonObject();
                    meta.camera.put(e.getKey(), arr(c.get("d")));
                    meta.cameraRate.put(e.getKey(), c.get("rate").getAsFloat());
                }
            }
            if (root.has("integral_optic")) {
                JsonObject o = root.getAsJsonObject("integral_optic");
                meta.integralZoom = o.get("zoom").getAsFloat();
                meta.integralEye = arr(o.get("eye"));
                meta.integralReticle = o.get("reticle").getAsString();
            }
        } catch (Exception ex) {
            Calibre.LOGGER.error("Failed to read gun meta {}", path, ex);
        }
        return meta;
    }

    private static List<Timed> timed(JsonArray arr) {
        List<Timed> out = new ArrayList<>();
        if (arr == null) return out;
        for (JsonElement e : arr) {
            JsonArray p = e.getAsJsonArray();
            out.add(new Timed(p.get(0).getAsFloat(), p.get(1).getAsString()));
        }
        return out;
    }

    /** Attachment eye heights etc. (calibre_gen/attachments/&lt;id&gt;.json) */
    public static final class AttachmentMeta {
        private static final Map<String, AttachmentMeta> CACHE = new java.util.concurrent.ConcurrentHashMap<>();
        public float[] eye = null;
        public float zoom = 1f;
        public String reticle = "dot";
        public float length = 0f;

        public static AttachmentMeta get(String id) {
            AttachmentMeta cached = CACHE.get(id);
            if (cached != null) return cached;
            AttachmentMeta loaded = load(id);
            AttachmentMeta prev = CACHE.putIfAbsent(id, loaded);
            return prev != null ? prev : loaded;
        }

        private static AttachmentMeta load(String k) {
            {
                AttachmentMeta m = new AttachmentMeta();
                try (InputStream in = GunMeta.class.getResourceAsStream("/calibre_gen/attachments/" + k + ".json")) {
                    if (in == null) return m;
                    JsonObject o = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
                    if (o.has("eye")) m.eye = arr(o.get("eye"));
                    if (o.has("zoom")) m.zoom = o.get("zoom").getAsFloat();
                    if (o.has("reticle")) m.reticle = o.get("reticle").getAsString();
                    if (o.has("length")) m.length = o.get("length").getAsFloat();
                } catch (Exception ex) {
                    Calibre.LOGGER.error("Failed to read attachment meta {}", k, ex);
                }
                return m;
            }
        }
    }
}
