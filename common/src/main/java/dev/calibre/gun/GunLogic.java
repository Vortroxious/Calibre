package dev.calibre.gun;

import dev.calibre.CalibreConfig;
import dev.calibre.ballistics.Ballistics;
import dev.calibre.network.Net;
import dev.calibre.registry.ModRegistry;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Server-authoritative gun state machine. Every timed action (reload stages, bolt/pump cycling, inspect, draw) is
 * scheduled from the generated animation timings in {@link GunMeta}, so the magazine is filled exactly when the
 * player sees it seat.
 */
public final class GunLogic {
    private static final class Act {
        final String anim;
        final Item item;
        final int slot;
        final long start, end;
        final boolean interruptible;
        final List<long[]> eventTicks = new ArrayList<>();
        final List<Runnable> eventRuns = new ArrayList<>();
        Runnable onEnd;
        boolean interruptRequested;

        Act(String anim, Item item, int slot, long start, long end, boolean interruptible) {
            this.anim = anim;
            this.item = item;
            this.slot = slot;
            this.start = start;
            this.end = end;
            this.interruptible = interruptible;
        }

        void at(long tick, Runnable r) {
            eventTicks.add(new long[]{tick});
            eventRuns.add(r);
        }
    }

    private static final Map<UUID, Act> ACTS = new HashMap<>();
    private static final Map<UUID, Long> LAST_SHOT = new HashMap<>();
    private static final Map<UUID, Integer> LAST_SLOT = new HashMap<>();
    private static final Map<UUID, Item> LAST_ITEM = new HashMap<>();
    private static final Set<UUID> AIMING = new HashSet<>();

    private GunLogic() {}

    public static boolean isAiming(Player p) {
        return AIMING.contains(p.getUUID());
    }

    public static boolean isBusy(Player p) {
        Act a = ACTS.get(p.getUUID());
        return a != null && !a.interruptible;
    }

    // ---- packets ---------------------------------------------------------------------------------
    public static void onShoot(ServerPlayer player, Net.ShootPayload p) {
        ItemStack stack = player.getMainHandItem();
        if (!(stack.getItem() instanceof GunItem gun)) return;
        UUID id = player.getUUID();
        Act act = ACTS.get(id);
        if (act != null) {
            if (act.interruptible) {
                ACTS.remove(id);
            } else {
                if (act.anim.startsWith("reload_loop") || act.anim.startsWith("reload_clip") || act.anim.startsWith("reload_start"))
                    act.interruptRequested = true;
                return;
            }
        }
        GunDefinition def = gun.def();
        long now = System.currentTimeMillis();
        Long last = LAST_SHOT.get(id);
        if (last != null && now - last < def.msBetweenShots() * 0.7) return;
        LAST_SHOT.put(id, now);
        // clamp the client's view against the server's to stop spoofed angles
        float yaw = p.yaw(), pitch = p.pitch();
        if (Math.abs(Mth.wrapDegrees(yaw - player.getYRot())) > 12 || Math.abs(pitch - player.getXRot()) > 12) {
            yaw = player.getYRot();
            pitch = player.getXRot();
        }
        fire(player, stack, gun, p.aiming() || isAiming(player), yaw, pitch);
    }

    public static void onRequest(ServerPlayer player, Net.Request req) {
        UUID id = player.getUUID();
        switch (req) {
            case AIM_ON -> {
                AIMING.add(id);
                Act a = ACTS.get(id);
                if (a != null && a.anim.equals("inspect")) ACTS.remove(id);
                return;
            }
            case AIM_OFF -> {
                AIMING.remove(id);
                return;
            }
            case INTERRUPT -> {
                Act a = ACTS.get(id);
                if (a != null) a.interruptRequested = true;
                return;
            }
            default -> {}
        }
        ItemStack stack = player.getMainHandItem();
        if (!(stack.getItem() instanceof GunItem gun)) return;
        Act cur = ACTS.get(id);
        if (cur != null && !cur.interruptible) return;
        switch (req) {
            case RELOAD -> reload(player, stack, gun);
            case FIRE_MODE -> {
                GunDefinition def = gun.def();
                if (def.modes().size() < 2) return;
                GunState s = GunItem.state(stack);
                GunItem.setState(stack, s.withMode((s.mode() + 1) % def.modes().size()));
                if (gun.meta().has("firemode")) start(player, gun, "firemode", true, null);
                else player.level().playSound(null, player.blockPosition(), ModRegistry.sound("selector"), SoundSource.PLAYERS, 0.6f, 1f);
            }
            case INSPECT -> {
                if (gun.meta().has("inspect")) start(player, gun, "inspect", true, null);
            }
            default -> {}
        }
    }

    // ---- firing ----------------------------------------------------------------------------------
    /** Shared by players and mercenaries. Returns true if a round was fired. */
    public static boolean fire(LivingEntity shooter, ItemStack stack, GunItem gun, boolean aiming, float yaw, float pitch) {
        GunDefinition def = gun.def();
        GunMeta meta = gun.meta();
        GunState s = GunItem.state(stack);
        // Only the explicit server option keeps magazines full. Creative players still empty their magazine and
        // reload (with the animation); they just never use up ammo items (see available()/take()).
        boolean infinite = CalibreConfig.infiniteAmmo();
        boolean hasRound = def.cycle().hasChamber() ? s.chambered() : s.ammo() > 0;
        if (!hasRound) {
            broadcast(shooter, "dry", false, true);
            if (def.cycle().manual() && s.ammo() > 0 && shooter instanceof ServerPlayer sp) startCycle(sp, gun, 0);
            return false;
        }
        GunState after;
        if (def.cycle().hasChamber()) {
            after = s.withChambered(false);
            if (!def.cycle().manual() && after.ammo() > 0) after = new GunState(after.ammo() - 1, true, after.mode());
        } else {
            after = s.withAmmo(s.ammo() - 1);
        }
        if (infinite) after = def.cycle().manual() ? s.withChambered(false) : s;
        GunItem.setState(stack, after);

        Ballistics.fire(shooter, stack, def, aiming, yaw, pitch);

        // gunshot: everyone but the shooter (who already heard it locally)
        GunAttachments att = GunItem.attachments(stack);
        SoundEvent shot = att.suppressed() ? ModRegistry.sound(def.category() == GunDefinition.Category.PISTOL
                || def.caliber() == Caliber.NINE_MM || def.caliber() == Caliber.ACP45 ? "suppressed_pistol" : "suppressed_rifle")
                : ModRegistry.sound(def.caliber() == Caliber.PG7 ? "rocket_launch" : "fire_" + def.id());
        if (shot != null) {
            float vol = att.suppressed() ? 1.0f : 4.0f;
            shooter.level().playSound(shooter instanceof Player pl ? pl : null, shooter.getX(), shooter.getEyeY(), shooter.getZ(),
                    shot, shooter instanceof Player ? SoundSource.PLAYERS : SoundSource.HOSTILE, vol, 0.95f + shooter.getRandom().nextFloat() * 0.1f);
        }
        String anim = aiming && meta.has("fire_aim") ? "fire_aim" : "fire";
        if (after.total() == 0 && meta.has("fire_last")) anim = "fire_last";
        broadcast(shooter, anim, true, false);
        if (def.cycle().manual() && shooter instanceof ServerPlayer sp && (after.ammo() > 0 || infinite)) {
            GunMeta.Action fa = meta.action(anim);
            startCycle(sp, gun, fa == null ? 6 : Math.round(fa.length() * 20 * 0.55f));
        }
        return true;
    }

    private static void startCycle(ServerPlayer player, GunItem gun, int delay) {
        String anim = isAiming(player) && gun.meta().has("cycle_aim") ? "cycle_aim" : "cycle";
        if (!gun.meta().has(anim)) {
            chamberFromMag(player.getMainHandItem(), gun);
            return;
        }
        long now = player.level().getGameTime();
        Act wait = new Act("wait", gun, player.getInventory().getSelectedSlot(), now, now + delay, false);
        wait.onEnd = () -> start(player, gun, anim, false, () -> chamberFromMag(player.getMainHandItem(), gun));
        if (delay <= 0) wait.onEnd.run();
        else ACTS.put(player.getUUID(), wait);
    }

    private static void chamberFromMag(ItemStack stack, GunItem gun) {
        if (stack.getItem() != gun) return;
        GunState s = GunItem.state(stack);
        if (gun.def().cycle().hasChamber() && !s.chambered() && s.ammo() > 0)
            GunItem.setState(stack, new GunState(s.ammo() - 1, true, s.mode()));
    }

    // ---- reloading -------------------------------------------------------------------------------
    private static void reload(ServerPlayer player, ItemStack stack, GunItem gun) {
        GunDefinition def = gun.def();
        GunMeta meta = gun.meta();
        GunState s = GunItem.state(stack);
        int cap = def.capacity(GunItem.attachments(stack));
        boolean needsChamber = def.cycle().hasChamber() && !s.chambered();
        boolean creative = player.getAbilities().instabuild;
        if (s.ammo() >= cap && !needsChamber && !creative) {
            player.displayClientMessage(Component.translatable("message.calibre.mag_full"), true);
            return;
        }
        if (s.ammo() >= cap && needsChamber) { // full mag but empty chamber: just cycle
            if (def.cycle().manual() || meta.has("cycle")) startCycle(player, gun, 0);
            else chamberFromMag(stack, gun);
            return;
        }
        // creative + full magazine falls through: the reload plays as a showcase and the mag simply stays full
        if (available(player, def.caliber()) <= 0) {
            player.level().playSound(null, player.blockPosition(), ModRegistry.sound("dry_fire"), SoundSource.PLAYERS, 0.5f, 0.8f);
            player.displayClientMessage(Component.translatable("message.calibre.no_ammo", def.caliber().displayName), true);
            return;
        }
        if (def.reloadType().staged()) {
            shellStage(player, gun, "reload_start");
            return;
        }
        boolean empty = s.total() == 0;
        String anim = empty && meta.has("reload_empty") ? "reload_empty" : "reload";
        GunMeta.Action a = meta.action(anim);
        if (a == null) return;
        Act act = start(player, gun, anim, false, () -> {
            ItemStack st = player.getMainHandItem();
            GunState ns = GunItem.state(st);
            if (def.cycle().manual() && !ns.chambered() && ns.ammo() > 0) startCycle(player, gun, 0);
        });
        if (act == null) return;
        long t = act.start + Math.round(a.event("ammo", a.length() * 0.6f) * 20);
        boolean rackOnReload = anim.equals("reload_empty") && def.cycle() == GunDefinition.Cycle.CLOSED_BOLT;
        act.at(t, () -> {
            ItemStack st = player.getMainHandItem();
            if (st.getItem() != gun) return;
            GunState ns = GunItem.state(st);
            int capNow = def.capacity(GunItem.attachments(st));
            int want = capNow - ns.ammo();
            int got = take(player, def.caliber(), want);
            GunState out = ns.withAmmo(ns.ammo() + got);
            if (rackOnReload && !out.chambered() && out.ammo() > 0) out = new GunState(out.ammo() - 1, true, out.mode());
            GunItem.setState(st, out);
        });
    }

    private static void shellStage(ServerPlayer player, GunItem gun, String stage) {
        GunDefinition def = gun.def();
        GunMeta meta = gun.meta();
        if (!meta.has(stage)) return;
        switch (stage) {
            case "reload_start" -> start(player, gun, stage, false, () -> shellStage(player, gun, nextLoad(player, gun)));
            case "reload_loop", "reload_clip" -> {
                GunMeta.Action a = meta.action(stage);
                Act act = start(player, gun, stage, false, null);
                if (act == null) return;
                int per = stage.equals("reload_clip") ? Math.max(1, def.clipSize()) : 1;
                act.at(act.start + Math.round(a.event("ammo", a.length() * 0.7f) * 20), () -> {
                    ItemStack st = player.getMainHandItem();
                    if (st.getItem() != gun) return;
                    GunState s = GunItem.state(st);
                    int room = def.capacity(GunItem.attachments(st)) - s.ammo();
                    int got = take(player, def.caliber(), Math.min(per, room));
                    if (got > 0) GunItem.setState(st, s.withAmmo(s.ammo() + got));
                });
                act.onEnd = () -> {
                    ItemStack st = player.getMainHandItem();
                    GunState s = GunItem.state(st);
                    boolean more = s.ammo() < def.capacity(GunItem.attachments(st)) && available(player, def.caliber()) > 0;
                    shellStage(player, gun, more && !act.interruptRequested ? nextLoad(player, gun) : "reload_end");
                };
            }
            case "reload_end" -> start(player, gun, stage, false, () -> {
                ItemStack st = player.getMainHandItem();
                if (st.getItem() != gun) return;
                GunState s = GunItem.state(st);
                if (def.cycle().hasChamber() && !s.chambered() && s.ammo() > 0) {
                    if (def.cycle() == GunDefinition.Cycle.BOLT_ACTION) chamberFromMag(st, gun); // reload_end closes the bolt
                    else startCycle(player, gun, 0);
                }
            });
            default -> {}
        }
    }

    /** Stripper-clip guns load a full clip whenever one fits, and top up with single rounds otherwise. */
    private static String nextLoad(ServerPlayer player, GunItem gun) {
        GunDefinition def = gun.def();
        int clip = def.clipSize();
        if (def.reloadType() == GunDefinition.ReloadType.STRIPPER_CLIP && clip > 0 && gun.meta().has("reload_clip")) {
            ItemStack st = player.getMainHandItem();
            int room = def.capacity(GunItem.attachments(st)) - GunItem.state(st).ammo();
            if (room >= clip && available(player, def.caliber()) >= clip) return "reload_clip";
        }
        return "reload_loop";
    }

    // ---- actions ---------------------------------------------------------------------------------
    private static Act start(ServerPlayer player, GunItem gun, String anim, boolean interruptible, Runnable onEnd) {
        GunMeta.Action a = gun.meta().action(anim);
        if (a == null) return null;
        long now = player.level().getGameTime();
        Act act = new Act(anim, gun, player.getInventory().getSelectedSlot(), now, now + a.ticks(), interruptible);
        act.onEnd = onEnd;
        ACTS.put(player.getUUID(), act);
        broadcast(player, anim, false, true);
        return act;
    }

    /** Sends the animation to everyone tracking the entity (and the entity itself if it's a player and includeSelf). */
    public static void broadcast(LivingEntity e, String anim, boolean shot, boolean includeSelf) {
        Net.ActionPayload pl = new Net.ActionPayload(e.getId(), anim, shot);
        if (!(e.level() instanceof net.minecraft.server.level.ServerLevel level)) return;
        // everyone in view range, but skip fake / test players whose connection has no Calibre channel
        double range = Math.max(64, level.getServer().getPlayerList().getViewDistance() * 16.0);
        for (ServerPlayer p : level.players()) {
            if (p == e ? !includeSelf : p.distanceToSqr(e) > range * range) continue;
            if (dev.calibre.platform.Platform.INSTANCE.canReceive(p, Net.ActionPayload.TYPE)) dev.calibre.platform.Platform.INSTANCE.sendToPlayer(p, pl);
        }
    }

    public static void tick(ServerPlayer player) {
        UUID id = player.getUUID();
        ItemStack held = player.getMainHandItem();
        int slot = player.getInventory().getSelectedSlot();
        Item item = held.getItem();
        boolean switched = !Integer.valueOf(slot).equals(LAST_SLOT.get(id)) || LAST_ITEM.get(id) != item;
        if (switched) {
            LAST_SLOT.put(id, slot);
            LAST_ITEM.put(id, item);
            ACTS.remove(id);
            if (item instanceof GunItem gun && gun.meta().has("draw")) {
                GunMeta.Action a = gun.meta().action("draw");
                long now = player.level().getGameTime();
                ACTS.put(id, new Act("draw", gun, slot, now, now + Math.max(1, a.ticks() - 4), true));
                broadcast(player, "draw", false, false);
            }
            if (!(item instanceof GunItem)) AIMING.remove(id);
            return;
        }
        Act act = ACTS.get(id);
        if (act == null) return;
        long now = player.level().getGameTime();
        for (int i = 0; i < act.eventTicks.size(); i++) {
            long[] t = act.eventTicks.get(i);
            if (t[0] >= 0 && now >= t[0]) {
                t[0] = -1;
                act.eventRuns.get(i).run();
            }
        }
        if (now >= act.end) {
            if (ACTS.get(id) == act) ACTS.remove(id);
            if (act.onEnd != null) act.onEnd.run();
        }
    }

    public static void clear(Player p) {
        UUID id = p.getUUID();
        ACTS.remove(id);
        LAST_SHOT.remove(id);
        LAST_SLOT.remove(id);
        LAST_ITEM.remove(id);
        AIMING.remove(id);
    }

    // ---- ammo ------------------------------------------------------------------------------------
    public static int available(Player p, Caliber c) {
        if (CalibreConfig.infiniteAmmo() || (p.getAbilities().instabuild && CalibreConfig.creativeInfinite())) return 9999;
        Item ammo = ModRegistry.AMMO.get(c).get();
        int n = 0;
        for (ItemStack st : p.getInventory()) if (st.is(ammo)) n += st.getCount();
        return n;
    }

    public static int take(Player p, Caliber c, int want) {
        if (want <= 0) return 0;
        if (CalibreConfig.infiniteAmmo() || (p.getAbilities().instabuild && CalibreConfig.creativeInfinite())) return want;
        Item ammo = ModRegistry.AMMO.get(c).get();
        int got = 0;
        var inv = p.getInventory();
        for (int i = 0; i < inv.getContainerSize() && got < want; i++) {
            ItemStack st = inv.getItem(i);
            if (st.is(ammo)) {
                int n = Math.min(want - got, st.getCount());
                st.shrink(n);
                got += n;
            }
        }
        return got;
    }
}
