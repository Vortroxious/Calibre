package dev.calibre.client;

import dev.calibre.CalibreConfig;
import dev.calibre.ballistics.Ballistics;
import dev.calibre.gun.Attachment;
import dev.calibre.gun.Caliber;
import dev.calibre.gun.GunAttachments;
import dev.calibre.gun.GunDefinition;
import dev.calibre.gun.GunItem;
import dev.calibre.gun.GunMeta;
import dev.calibre.gun.GunState;
import dev.calibre.network.Net;
import dev.calibre.registry.ModRegistry;
import dev.calibre.workbench.GunWorkbenchBlock;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.resources.sounds.EntityBoundSoundInstance;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.ItemOwner;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoItem;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

/**
 * Everything the local player's gun does on the client: input, fire-rate timing at frame precision, prediction
 * (animation, sound, recoil happen instantly), ADS, sway/recoil springs and the foley scheduler driven by the
 * generated sound timelines.
 */
public final class ClientGun {
    private ClientGun() {}

    // ---- state -----------------------------------------------------------------------------------
    private static float ads, adsO;              // 0..1 aim progress (frame-smoothed)
    private static boolean aimSent;
    private static boolean triggerWasDown;
    private static int burstLeft;
    private static long lastShotMs;
    private static long busyUntilMs;
    private static String busyAnim = "";
    private static int unconfirmedShots;
    private static GunState lastSeen;
    private static int lastSlot = -1;
    private static ItemStack lastStack = ItemStack.EMPTY;
    private static long flashUntilMs;
    private static final Map<Integer, Long> OTHER_FLASH = new HashMap<>();
    private static long hitMarkerUntil;
    private static int hitKind;
    private static int seq;
    private static long sprintBlockUntil;

    // recoil / sway springs (view space)
    public static final Spring KICK_PITCH = new Spring(170, 18), KICK_YAW = new Spring(170, 18), KICK_BACK = new Spring(260, 22),
            KICK_ROLL = new Spring(140, 14), SWAY_X = new Spring(60, 11), SWAY_Y = new Spring(60, 11), SPRINT = new Spring(40, 12);
    private static float pendingPitch, pendingYaw, recoverPitch;
    private static float lastYaw = Float.NaN, lastPitch;
    private static long lastFrameNs;

    // CS2-style camera motion (render only: never touches the player's aim)
    private static float[] camData;
    private static float camRate = 30, camRollSign = 1;
    private static long camStartNs, camFadeNs;
    private static String camAnim = "";
    private static int camSlot = -1;
    private static net.minecraft.world.item.Item camItem;
    private static final float[] NO_CAMERA = {0, 0, 0};

    private record Scheduled(long atMs, SoundEvent sound, Entity entity, float volume) {}

    private static final List<Scheduled> SOUNDS = new ArrayList<>();

    /** critically-damped-ish spring used for recoil and sway */
    public static final class Spring {
        final float k, d;
        public float x, v;

        Spring(float k, float d) {
            this.k = k;
            this.d = d;
        }

        void impulse(float dv) {
            v += dv;
        }

        void step(float target, float dt) {
            float a = k * (target - x) - d * v;
            v += a * dt;
            x += v * dt;
        }
    }

    // ---- queries ---------------------------------------------------------------------------------
    public static float ads(float pt) {
        return Mth.lerp(pt, adsO, ads);
    }

    public static float adsEased(float pt) {
        float a = ads(pt);
        return a * a * (3 - 2 * a);
    }

    public static boolean isBusy(ItemStack stack) {
        return System.currentTimeMillis() < busyUntilMs && Minecraft.getInstance().player != null
                && Minecraft.getInstance().player.getMainHandItem() == stack && busyAnim.startsWith("reload");
    }

    public static float flashAlpha(float pt) {
        long left = flashUntilMs - System.currentTimeMillis();
        return left <= 0 ? 0 : Math.min(1, left / 40f);
    }

    public static float flashFor(ItemOwner owner) {
        if (!(owner instanceof Entity e)) return 0;
        Long t = OTHER_FLASH.get(e.getId());
        if (t == null) return 0;
        long left = t - System.currentTimeMillis();
        return left <= 0 ? 0 : Math.min(1, left / 40f);
    }

    public static float hitMarker() {
        long left = hitMarkerUntil - System.currentTimeMillis();
        return left <= 0 ? 0 : left / 220f;
    }

    public static int hitKind() {
        return hitKind;
    }

    /** Effective magnification of what the player is looking through. */
    public static float zoom(ItemStack stack) {
        if (!(stack.getItem() instanceof GunItem gun)) return 1;
        GunMeta meta = gun.meta();
        if (meta.integralZoom > 0) return meta.integralZoom;
        Attachment optic = GunItem.attachments(stack).get(Attachment.Slot.OPTIC);
        if (optic != null) return optic.zoom;
        return gun.def().category() == GunDefinition.Category.PISTOL ? 1.08f : 1.15f;
    }

    public static boolean scoped(float pt) {
        LocalPlayer p = Minecraft.getInstance().player;
        return p != null && zoom(p.getMainHandItem()) >= 3.5f && adsEased(pt) > 0.92f;
    }

    public static int predictedRounds(ItemStack stack) {
        GunState s = GunItem.state(stack);
        return Math.max(0, s.total() - unconfirmedShots);
    }

    public static float currentSpread() {
        LocalPlayer p = Minecraft.getInstance().player;
        if (p == null || !(p.getMainHandItem().getItem() instanceof GunItem gun)) return 0;
        return Ballistics.spread(p, gun.def(), GunItem.attachments(p.getMainHandItem()), ads > 0.9f);
    }

    // ---- per tick --------------------------------------------------------------------------------
    public static void tick() {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null) return;
        ItemStack stack = p.getMainHandItem();
        int slot = p.getInventory().getSelectedSlot();
        boolean isGun = stack.getItem() instanceof GunItem;
        if (slot != lastSlot || stack.getItem() != lastStack.getItem()) {
            lastSlot = slot;
            lastStack = stack;
            busyUntilMs = 0;
            unconfirmedShots = 0;
            burstLeft = 0;
            SOUNDS.removeIf(s -> s.entity == p);
            if (isGun) {
                GunItem gun = (GunItem) stack.getItem();
                play(p, stack, gun, "draw", true);
                GunMeta.Action d = gun.meta().action("draw");
                if (d != null) setBusy("draw", Math.round(d.length() * 1000) - 150);
            }
        }
        lastStack = stack;
        GunState s = isGun ? GunItem.state(stack) : null;
        if (s != null && !s.equals(lastSeen)) {
            lastSeen = s;
            unconfirmedShots = 0;
        }
        // the server always answers a shot within a few ticks; if it didn't change the gun (e.g. the infiniteAmmo
        // server option, or a refused shot) drop the prediction so the HUD never drifts from the real count
        if (unconfirmedShots > 0 && System.currentTimeMillis() - lastShotMs > 600) unconfirmedShots = 0;
        boolean wantAim = isGun && mc.screen == null && (mc.options.keyUse.isDown() || ClientAutoTest.forceAim) && !p.isSprinting() && !lookingAtWorkbench(mc)
                && !(System.currentTimeMillis() < busyUntilMs && busyAnim.startsWith("reload"));
        if (wantAim != aimSent) {
            aimSent = wantAim;
            dev.calibre.platform.Platform.INSTANCE.sendToServer(new Net.RequestPayload(wantAim ? Net.Request.AIM_ON : Net.Request.AIM_OFF));
        }
        if (isGun && p.isSprinting()) sprintBlockUntil = System.currentTimeMillis() + 180;
        while (CalibreKeys.RELOAD.consumeClick()) {
            if (isGun) dev.calibre.platform.Platform.INSTANCE.sendToServer(new Net.RequestPayload(Net.Request.RELOAD));
        }
        while (CalibreKeys.FIRE_MODE.consumeClick()) {
            if (isGun) dev.calibre.platform.Platform.INSTANCE.sendToServer(new Net.RequestPayload(Net.Request.FIRE_MODE));
        }
        while (CalibreKeys.INSPECT.consumeClick()) {
            if (isGun && ads < 0.1f) dev.calibre.platform.Platform.INSTANCE.sendToServer(new Net.RequestPayload(Net.Request.INSPECT));
        }
        OTHER_FLASH.values().removeIf(t -> t < System.currentTimeMillis());
    }

    private static boolean lookingAtWorkbench(Minecraft mc) {
        HitResult hr = mc.hitResult;
        return hr instanceof BlockHitResult bhr && hr.getType() == HitResult.Type.BLOCK && mc.level != null
                && mc.level.getBlockState(bhr.getBlockPos()).getBlock() instanceof GunWorkbenchBlock;
    }

    // ---- per frame -------------------------------------------------------------------------------
    public static void frame() {
        Minecraft mc = Minecraft.getInstance();
        long ns = System.nanoTime();
        float dt = lastFrameNs == 0 ? 0.016f : Math.min(0.05f, (ns - lastFrameNs) / 1e9f);
        lastFrameNs = ns;
        LocalPlayer p = mc.player;
        runSounds();
        if (p == null) return;
        ItemStack stack = p.getMainHandItem();
        boolean isGun = stack.getItem() instanceof GunItem;
        // ADS progress
        adsO = ads;
        if (isGun) {
            GunItem gun = (GunItem) stack.getItem();
            float adsTime = gun.def().adsTicks() * 0.05f * GunItem.attachments(stack).product(a -> a.adsTime);
            ads = Mth.clamp(ads + (aimSent ? dt : -dt) / Math.max(0.05f, adsTime), 0, 1);
        } else {
            ads = 0;
        }
        adsO = ads; // frame-smoothed already
        // firing (frame precision)
        boolean down = isGun && mc.screen == null && mc.options.keyAttack.isDown() && !mc.player.isSpectator();
        if (isGun && ClientAutoTest.pendingShots() > 0 && System.currentTimeMillis() - lastShotMs > 260
                && System.currentTimeMillis() >= busyUntilMs) {
            ClientAutoTest.consumeShot();
            lastShotMs = System.currentTimeMillis();
            shoot(p, stack, (GunItem) stack.getItem());
        }
        if (isGun) handleTrigger(p, stack, (GunItem) stack.getItem(), down);
        triggerWasDown = down;
        // camera recoil: apply pending kick over a few frames, then partial recovery
        float apply = Math.min(1, dt * 28);
        float dp = pendingPitch * apply, dy = pendingYaw * apply;
        pendingPitch -= dp;
        pendingYaw -= dy;
        if (dp != 0 || dy != 0) {
            p.setXRot(Mth.clamp(p.getXRot() - dp, -90, 90));
            p.setYRot(p.getYRot() + dy);
            p.xRotO = p.getXRot();
            p.yRotO = p.getYRot();
        }
        if (!down && recoverPitch > 0.01f && System.currentTimeMillis() - lastShotMs > 120) {
            float r = recoverPitch * Math.min(1, dt * 6);
            recoverPitch -= r;
            p.setXRot(Mth.clamp(p.getXRot() + r, -90, 90));
            p.xRotO = p.getXRot();
        }
        // sway from mouse movement
        float yaw = p.getYRot(), pitch = p.getXRot();
        if (Float.isNaN(lastYaw)) {
            lastYaw = yaw;
            lastPitch = pitch;
        }
        float swayMul = (float) CalibreConfig.client(CalibreConfig.SWAY, 1.0) * (1 - 0.75f * adsEased(1));
        float dYaw = Mth.wrapDegrees(yaw - lastYaw), dPitch = pitch - lastPitch;
        lastYaw = yaw;
        lastPitch = pitch;
        SWAY_X.step(Mth.clamp(-dYaw * 0.9f, -8, 8) * swayMul, dt);
        SWAY_Y.step(Mth.clamp(-dPitch * 0.9f, -8, 8) * swayMul, dt);
        SPRINT.step(isGun && p.isSprinting() && ads < 0.1f ? 1 : 0, dt);
        KICK_PITCH.step(0, dt);
        KICK_YAW.step(0, dt);
        KICK_BACK.step(0, dt);
        KICK_ROLL.step(0, dt);
    }

    private static void handleTrigger(LocalPlayer p, ItemStack stack, GunItem gun, boolean down) {
        GunDefinition def = gun.def();
        long now = System.currentTimeMillis();
        boolean pressed = down && !triggerWasDown;
        if (now < sprintBlockUntil) return;
        if (now < busyUntilMs) {
            if (pressed && (busyAnim.startsWith("reload_loop") || busyAnim.startsWith("reload_clip"))) dev.calibre.platform.Platform.INSTANCE.sendToServer(new Net.RequestPayload(Net.Request.INTERRUPT));
            if (!busyAnim.equals("inspect")) return;
        }
        GunDefinition.FireMode mode = gun.mode(stack);
        boolean want;
        switch (mode) {
            case SEMI -> want = pressed;
            case BURST -> {
                if (pressed && burstLeft == 0) burstLeft = def.burstCount();
                want = burstLeft > 0;
            }
            default -> want = down;
        }
        if (!want) return;
        double interval = def.msBetweenShots();
        if (now - lastShotMs < interval) return;
        lastShotMs = now;
        if (mode == GunDefinition.FireMode.BURST) burstLeft--;
        shoot(p, stack, gun);
    }

    private static void shoot(LocalPlayer p, ItemStack stack, GunItem gun) {
        GunDefinition def = gun.def();
        GunMeta meta = gun.meta();
        if (p.isSprinting()) p.setSprinting(false);
        int rounds = predictedRounds(stack);
        GunState s = GunItem.state(stack);
        boolean hasRound = def.cycle().manual() ? s.chambered() && unconfirmedShots == 0 : rounds > 0;
        dev.calibre.platform.Platform.INSTANCE.sendToServer(new Net.ShootPayload(p.getYRot(), p.getXRot(), ads > 0.85f, seq++));
        if (!hasRound) {
            burstLeft = 0;
            return; // the server answers with the dry-fire click
        }
        unconfirmedShots++;
        boolean aiming = ads > 0.5f;
        String anim = aiming && meta.has("fire_aim") ? "fire_aim" : "fire";
        if (rounds - 1 <= 0 && meta.has("fire_last")) anim = "fire_last";
        play(p, stack, gun, anim, false);
        GunAttachments att = GunItem.attachments(stack);
        String snd = att.suppressed() ? (def.caliber() == Caliber.NINE_MM || def.caliber() == Caliber.ACP45
                || def.category() == GunDefinition.Category.PISTOL ? "suppressed_pistol" : "suppressed_rifle")
                : def.caliber() == Caliber.PG7 ? "rocket_launch" : "fire_" + def.id();
        SoundEvent se = ModRegistry.sound(snd);
        if (se != null) Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(se, 0.97f + p.getRandom().nextFloat() * 0.06f, 1.0f));
        if (!att.suppressed()) flashUntilMs = System.currentTimeMillis() + 55;
        // recoil
        float mul = att.product(a -> a.recoil) * (aiming ? 0.8f : 1f) * (p.isCrouching() ? 0.8f : 1f)
                * (float) CalibreConfig.client(CalibreConfig.CAMERA_RECOIL, 1.0);
        if (p.isCrouching() && (att.has(Attachment.BIPOD_ATT) || def.category() == GunDefinition.Category.LMG)) mul *= 0.55f;
        float v = def.recoilV() * mul * (0.85f + p.getRandom().nextFloat() * 0.3f);
        float h = def.recoilH() * mul * (p.getRandom().nextFloat() * 2 - 0.8f);
        pendingPitch += v;
        pendingYaw += h;
        recoverPitch = Math.min(recoverPitch + v * 0.45f, 12);
        float visual = Math.min(1.5f, def.recoilV() / 4f) * (aiming ? 0.45f : 1f);
        KICK_PITCH.impulse(60 * visual);
        KICK_YAW.impulse(20 * visual * (p.getRandom().nextFloat() - 0.5f));
        KICK_BACK.impulse(1.4f * visual);
        KICK_ROLL.impulse(30 * visual * (p.getRandom().nextFloat() - 0.4f));
        if (def.cycle().manual()) setBusy("cycle", 400);
        // ejected brass smoke puff
        Vec3 eye = p.getEyePosition();
        Vec3 look = p.getLookAngle();
        p.level().addParticle(ParticleTypes.SMOKE, eye.x + look.x * 0.9, eye.y - 0.15 + look.y * 0.9, eye.z + look.z * 0.9,
                look.x * 0.02, 0.02, look.z * 0.02);
    }

    private static void setBusy(String anim, long ms) {
        busyAnim = anim;
        busyUntilMs = System.currentTimeMillis() + ms;
    }

    // ---- server actions ---------------------------------------------------------------------------
    public static void onAction(Net.ActionPayload pkt) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) return;
        Entity e = mc.level.getEntity(pkt.entityId());
        if (!(e instanceof LivingEntity le)) return;
        ItemStack stack = le.getMainHandItem();
        if (!(stack.getItem() instanceof GunItem gun)) return;
        boolean self = e == mc.player;
        if (self) {
            if (pkt.shot()) return; // predicted locally
            play(le, stack, gun, pkt.anim(), true);
            GunMeta.Action a = gun.meta().action(pkt.anim());
            if (a != null && !pkt.anim().equals("inspect") && !pkt.anim().equals("dry")) setBusy(pkt.anim(), Math.round(a.length() * 1000));
            if (pkt.anim().equals("inspect")) setBusy("inspect", Math.round(a.length() * 1000));
            if (pkt.anim().startsWith("reload")) unconfirmedShots = 0;
            return;
        }
        play(le, stack, gun, pkt.anim(), true);
        if (pkt.shot()) {
            OTHER_FLASH.put(e.getId(), System.currentTimeMillis() + 55);
            Vec3 look = le.getLookAngle();
            mc.level.addParticle(ParticleTypes.SMOKE, le.getX() + look.x, le.getEyeY() - 0.2 + look.y, le.getZ() + look.z, 0, 0.02, 0);
        }
    }

    public static void onHit(Net.HitPayload pkt) {
        if (!CalibreConfig.client(CalibreConfig.HIT_MARKERS, true)) return;
        hitKind = pkt.kind();
        hitMarkerUntil = System.currentTimeMillis() + 220;
        SoundEvent s = ModRegistry.sound(pkt.kind() == Net.HitPayload.HEADSHOT ? "headshot" : "hitmarker");
        if (s != null) Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(s, pkt.kind() == Net.HitPayload.KILL ? 0.8f : 1f, 0.5f));
    }

    /** trigger the GeckoLib animation on the entity's held gun and schedule the animation's foley */
    private static void play(LivingEntity e, ItemStack stack, GunItem gun, String anim, boolean withFoley) {
        GunMeta meta = gun.meta();
        if (!meta.has(anim)) return;
        long id = GeoItem.getId(stack);
        gun.triggerAnim(e, id, GunItem.CONTROLLER, anim);
        if (e == Minecraft.getInstance().player) startCamera((LocalPlayer) e, meta, anim);
        if (!withFoley && !anim.startsWith("fire")) return;
        long now = System.currentTimeMillis();
        boolean self = e == Minecraft.getInstance().player;
        for (GunMeta.Timed t : meta.action(anim).sounds()) {
            SoundEvent s = ModRegistry.sound(t.name());
            if (s != null) SOUNDS.add(new Scheduled(now + Math.round(t.time() * 1000), s, e, self ? 0.55f : 0.8f));
        }
        if (anim.equals("dry")) busyUntilMs = Math.max(busyUntilMs, now);
    }

    private static void startCamera(LocalPlayer p, GunMeta meta, String anim) {
        float[] d = meta.camera.get(anim);
        if (d == null) {
            if (camData != null && camFadeNs == 0) camFadeNs = System.nanoTime();
            return;
        }
        camData = d;
        camRate = meta.cameraRate.getOrDefault(anim, 30f);
        camStartNs = System.nanoTime();
        camFadeNs = 0;
        camAnim = anim;
        camSlot = p.getInventory().getSelectedSlot();
        camItem = p.getMainHandItem().getItem();
        camRollSign = anim.startsWith("fire") && p.getRandom().nextBoolean() ? -1 : 1;
    }

    /** View rotation offset {pitch, yaw, roll} in degrees for this frame (0 when nothing is playing). */
    public static float[] cameraOffset() {
        float[] d = camData;
        if (d == null) return NO_CAMERA;
        LocalPlayer p = Minecraft.getInstance().player;
        long now = System.nanoTime();
        if (camFadeNs == 0 && (p == null || p.getInventory().getSelectedSlot() != camSlot
                || p.getMainHandItem().getItem() != camItem || (camAnim.equals("inspect") && ads > 0.3f)))
            camFadeNs = now;   // switched away / aimed out of an inspect: ease out instead of snapping
        float k = (float) CalibreConfig.client(CalibreConfig.CAMERA_MOTION, 1.0) * (1 - 0.6f * adsEased(1));
        if (camFadeNs != 0) {
            float f = 1 - (now - camFadeNs) / 1.5e8f;
            if (f <= 0) {
                camData = null;
                return NO_CAMERA;
            }
            k *= f * f * (3 - 2 * f);
        }
        int n = d.length / 3;
        float idx = (now - camStartNs) / 1e9f * camRate;
        if (idx >= n - 1) {
            camData = null;
            return NO_CAMERA;
        }
        int i = Math.max(0, (int) idx);
        float f = idx - i;
        return new float[]{Mth.lerp(f, d[i * 3], d[i * 3 + 3]) * k, Mth.lerp(f, d[i * 3 + 1], d[i * 3 + 4]) * k,
                Mth.lerp(f, d[i * 3 + 2], d[i * 3 + 5]) * k * camRollSign};
    }

    private static void runSounds() {
        if (SOUNDS.isEmpty()) return;
        Minecraft mc = Minecraft.getInstance();
        long now = System.currentTimeMillis();
        for (Iterator<Scheduled> it = SOUNDS.iterator(); it.hasNext(); ) {
            Scheduled s = it.next();
            if (s.atMs > now) continue;
            it.remove();
            if (s.entity == null || s.entity.isRemoved()) continue;
            if (s.entity == mc.player) {
                mc.getSoundManager().play(SimpleSoundInstance.forUI(s.sound, 0.95f + mc.player.getRandom().nextFloat() * 0.1f, s.volume));
            } else {
                mc.getSoundManager().play(new EntityBoundSoundInstance(s.sound, SoundSource.PLAYERS, s.volume, 1f, s.entity,
                        mc.level == null ? 0 : mc.level.random.nextLong()));
            }
        }
    }

    public static boolean holdingGun() {
        LocalPlayer p = Minecraft.getInstance().player;
        return p != null && p.getMainHandItem().getItem() instanceof GunItem;
    }

    public static boolean isLocalAiming() {
        return aimSent;
    }
}
