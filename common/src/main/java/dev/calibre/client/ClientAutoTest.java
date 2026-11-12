package dev.calibre.client;

import dev.calibre.Calibre;
import dev.calibre.gun.Attachment;
import dev.calibre.gun.Caliber;
import dev.calibre.gun.GunAttachments;
import dev.calibre.gun.GunItem;
import dev.calibre.gun.GunState;
import dev.calibre.network.Net;
import dev.calibre.registry.ModRegistry;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.WorldDataConfiguration;
import net.minecraft.world.level.gamerules.GameRules;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.flag.FeatureFlags;

/**
 * Dev-only scripted client run (enabled with -Dcalibre.autotest=true, see the `autotest` Gradle run): creates a flat
 * world, cycles through guns and states and writes screenshots to run/screenshots/, then quits.
 */
public final class ClientAutoTest {
    public static final boolean ENABLED = Boolean.getBoolean("calibre.autotest");
    private static boolean created;
    private static int t = -1;
    private static int shots;

    private ClientAutoTest() {}

    public static int pendingShots() {
        return shots;
    }

    public static void consumeShot() {
        shots--;
    }

    public static boolean forceAim;
    /** the loader's settings screen (NeoForge ConfigurationScreen / Fabric CalibreConfigScreen), for the screenshot tour */
    public static java.util.function.Function<net.minecraft.client.gui.screens.Screen, net.minecraft.client.gui.screens.Screen> CONFIG_SCREEN = null;
    private static BlockPos workbenchPos = BlockPos.ZERO;

    public static void tick() {
        if (!ENABLED) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            if (!created && mc.screen != null && !(mc.screen instanceof TitleScreen)
                    && mc.screen.getClass().getSimpleName().contains("Onboarding")) {
                mc.options.onboardAccessibility = false;
                mc.setScreen(new TitleScreen());
                return;
            }
            if (!created && mc.screen instanceof TitleScreen) {
                created = true;
                // keep software-GL test runs fast
                mc.options.renderDistance().set(4);
                mc.options.simulationDistance().set(5);
                mc.options.menuBackgroundBlurriness().set(0);
                mc.options.cloudStatus().set(net.minecraft.client.CloudStatus.OFF);
                GameType mode = Boolean.getBoolean("calibre.autotest.survival") ? GameType.SURVIVAL : GameType.CREATIVE;
                LevelSettings settings = new LevelSettings("calibre_autotest_" + System.currentTimeMillis(), mode, false,
                        Difficulty.EASY, true, new GameRules(FeatureFlags.DEFAULT_FLAGS), WorldDataConfiguration.DEFAULT);
                mc.createWorldOpenFlows().createFreshLevel(settings.levelName(), settings, new WorldOptions(42, false, false),
                        WorldPresets::createFlatWorldDimensions, mc.screen);
            }
            return;
        }
        if (mc.player == null) return;
        t++;
        var server = mc.getSingleplayerServer();
        ServerPlayer sp = server == null ? null : server.getPlayerList().getPlayer(mc.player.getUUID());
        if (GUN_LIST != null && t >= 20) {
            gunTour(mc, server, sp);
            return;
        }
        switch (t) {
            case 20 -> server.execute(() -> setup(sp));
            case 60 -> shot("01_glock_hip");
            case 62 -> forceAim = true;
            case 85 -> shot("02_glock_ads");
            case 88 -> forceAim = false;
            case 92 -> shots = 3;
            case 96 -> shot("03_glock_fire");
            case 110 -> request(Net.Request.RELOAD);
            case 125 -> shot("04_glock_reload_mid");
            case 136 -> shot("04b_glock_reload_late");
            case 170 -> request(Net.Request.INSPECT);
            case 190 -> shot("05_glock_inspect_a");
            case 215 -> shot("06_glock_inspect_b");
            case 260 -> select(1);
            case 290 -> shot("07_m4_hip");
            case 292 -> forceAim = true;
            case 318 -> shot("08_m4_acog_ads");
            case 320 -> forceAim = false;
            case 326 -> shots = 4;
            case 331 -> shot("08b_m4_fire");
            case 345 -> request(Net.Request.RELOAD);
            case 368 -> shot("09_m4_reload");
            case 420 -> request(Net.Request.INSPECT);
            case 445 -> shot("10_m4_inspect_a");
            case 470 -> shot("10_m4_inspect_b");
            case 520 -> select(2);
            case 548 -> shot("11_awm_hip");
            case 550 -> forceAim = true;
            case 585 -> shot("12_awm_scope");
            case 588 -> forceAim = false;
            case 600 -> select(3);
            case 628 -> shot("13_870_hip");
            case 630 -> shots = 1;
            case 640 -> shot("13b_870_pump");
            case 660 -> request(Net.Request.RELOAD);
            case 690 -> shot("14_870_reload");
            case 760 -> select(4);
            case 762 -> server.execute(() -> {
                ItemStack st = sp.getInventory().getItem(4);
                GunItem.setState(st, new GunState(0, false, 0));
            });
            case 790 -> request(Net.Request.RELOAD);
            case 812 -> shot("15_akm_reload_empty_a");
            case 840 -> shot("15_akm_reload_empty_b");
            case 900 -> select(5);
            case 930 -> request(Net.Request.RELOAD);
            case 950 -> shot("16_model29_reload_a");
            case 975 -> shot("16_model29_reload_b");
            case 1010 -> select(6);
            case 1040 -> shot("17_m249_hip");
            case 1042 -> request(Net.Request.RELOAD);
            case 1080 -> shot("17_m249_reload_cover");
            case 1160 -> select(1);
            case 1190 -> mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
            case 1210 -> shot("18_third_person");
            case 1215 -> mc.options.setCameraType(CameraType.FIRST_PERSON);
            case 1220 -> mc.setScreen(new InventoryScreen(mc.player));
            case 1230 -> shot("19_inventory_icons");
            case 1234 -> mc.setScreen(null);
            case 1240 -> server.execute(() -> {
                BlockPos wb = workbenchPos;
                sp.openMenu(sp.level().getBlockState(wb).getMenuProvider(sp.level(), wb));
            });
            case 1255 -> shot("20_workbench");
            case 1256 -> mc.setScreen(CONFIG_SCREEN == null ? null : CONFIG_SCREEN.apply(null));
            case 1259 -> {
                if (CONFIG_SCREEN != null) shot("20b_config_screen");
            }
            case 1260 -> mc.setScreen(null);
            case 1262 -> server.execute(() -> sp.setYRot(sp.getYRot() + 180));
            case 1265 -> mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            case 1285 -> shot("21_mercenary_third_person");
            case 1290 -> mc.options.setCameraType(CameraType.FIRST_PERSON);
            case 1300 -> select(0);
            case 1330 -> shot("22_mercenary_first_person");
            case 1400 -> {
                Calibre.LOGGER.info("[autotest] finished");
                mc.stop();
            }
            default -> {}
        }
    }

    /** -Dcalibre.autotest.guns=a,b,c : per gun hip / ADS / empty reload (two frames) / fire / inspect (two frames). */
    private static final String[] GUN_LIST = System.getProperty("calibre.autotest.guns", "").isBlank() ? null
            : System.getProperty("calibre.autotest.guns").split(",");
    /** -Dcalibre.autotest.film=true: instead of the usual shots, film the inspect every 3 ticks (fluidity review) */
    private static final boolean FILM = Boolean.getBoolean("calibre.autotest.film");
    private static final int TOUR = FILM ? 250 : 250;
    /** -Dcalibre.autotest.perf=N: instead of the usual shots, put N mercenaries carrying the gun in view and log the
     *  frame rate, to compare how much each model costs to draw. */
    private static final int PERF = Integer.getInteger("calibre.autotest.perf", -1);
    private static final java.util.List<net.minecraft.world.entity.Entity> perfMobs = new java.util.ArrayList<>();
    private static int perfSum, perfN;

    private static void gunTour(Minecraft mc, net.minecraft.client.server.IntegratedServer server, ServerPlayer sp) {
        // clean screenshots: no tutorial hints or recipe toasts
        mc.getTutorial().setStep(net.minecraft.client.tutorial.TutorialSteps.NONE);
        mc.getToastManager().clear();
        if (t == 20) {
            server.execute(() -> setup(sp));
            return;
        }
        if (t < 40) return;
        int idx = (t - 40) / TOUR, k = (t - 40) % TOUR;
        if (idx >= GUN_LIST.length) {
            Calibre.LOGGER.info("[autotest] finished");
            mc.stop();
            return;
        }
        String g = GUN_LIST[idx];
        String n = String.format("g%02d_%s_", idx, g);
        if (PERF >= 0) {
            if (k == 0) {
                mc.options.framerateLimit().set(260);
                mc.options.enableVsync().set(false);
                perfSum = perfN = 0;
                server.execute(() -> {
                    for (var e : perfMobs) e.discard();
                    perfMobs.clear();
                    var level = sp.level();
                    ItemStack own = new ItemStack(ModRegistry.GUNS.get(g).get());
                    GunItem.setState(own, GunState.full(((GunItem) own.getItem()).def()));
                    sp.getInventory().setItem(0, own);
                    sp.getInventory().setSelectedSlot(0);
                    for (int i = 0; i < PERF; i++) {
                        var merc = ModRegistry.MERCENARY.get().create(level, EntitySpawnReason.COMMAND);
                        if (merc == null) continue;
                        merc.snapTo(0.5 + (i % 6 - 2.5) * 1.6, sp.getY(), 5.5 + (i / 6) * 2.0, 180, 0);
                        merc.finalizeSpawn(level, level.getCurrentDifficultyAt(merc.blockPosition()),
                                EntitySpawnReason.COMMAND, null);
                        merc.setNoAi(true);
                        ItemStack st = new ItemStack(ModRegistry.GUNS.get(g).get());
                        GunItem.setState(st, GunState.full(((GunItem) st.getItem()).def()));
                        merc.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND, st);
                        level.addFreshEntity(merc);
                        perfMobs.add(merc);
                    }
                });
            }
            if (k == 1) select(0);
            if (k >= 100 && k % 20 == 0 && k <= 240) {
                perfSum += mc.getFps();
                perfN++;
            }
            if (k == 200) shot(n + "perf");
            if (k == 241) Calibre.LOGGER.info("[autotest] perf {} x{}: {} fps", g, PERF, perfSum / Math.max(1, perfN));
            return;
        }
        if (FILM) {
            switch (k) {
                case 0 -> server.execute(() -> {
                    ItemStack st = new ItemStack(ModRegistry.GUNS.get(g).get());
                    GunItem.setState(st, GunState.full(((GunItem) st.getItem()).def()));
                    sp.getInventory().setItem(0, st);
                    sp.getInventory().setSelectedSlot(0);
                });
                case 1 -> select(0);
                case 40 -> request(Net.Request.INSPECT);
                default -> {
                    if (k > 40 && (k - 40) % 3 == 0 && k <= 40 + 3 * 62) shot(n + String.format("f%02d", (k - 40) / 3));
                }
            }
            return;
        }
        switch (k) {
            case 0 -> server.execute(() -> {
                ItemStack st = new ItemStack(ModRegistry.GUNS.get(g).get());
                GunItem.setState(st, new GunState(0, false, 0));
                sp.getInventory().setItem(0, st);
                sp.getInventory().setSelectedSlot(0);
            });
            case 1 -> select(0);
            case 34 -> shot(n + "1_hip");
            case 36 -> forceAim = true;
            case 58 -> shot(n + "2_ads");
            case 60 -> forceAim = false;
            case 66 -> request(Net.Request.RELOAD);
            case 82 -> shot(n + "3_reload_a");
            case 104 -> shot(n + "4_reload_b");
            case 160 -> shots = 1;
            case 164 -> shot(n + "5_fire");
            case 190 -> request(Net.Request.INSPECT);
            case 212 -> shot(n + "6_inspect_a");
            case 236 -> shot(n + "7_inspect_b");
            case 12 -> shot(n + "0_draw");
            case 248 -> shot(n + "8_idle_late");
            default -> {}
        }
    }

    private static void request(Net.Request r) {
        dev.calibre.platform.Platform.INSTANCE.sendToServer(new Net.RequestPayload(r));
    }

    private static void select(int slot) {
        Minecraft mc = Minecraft.getInstance();
        mc.player.getInventory().setSelectedSlot(slot);
    }

    private static void shot(String name) {
        Minecraft mc = Minecraft.getInstance();
        Screenshot.grab(mc.gameDirectory, "calibre_" + name + ".png", mc.getMainRenderTarget(), 1, c -> {});
        Calibre.LOGGER.info("[autotest] screenshot {}", name);
    }

    private static void setup(ServerPlayer sp) {
        var level = sp.level();
        level.setDayTime(6000);
        sp.getAbilities().invulnerable = true;
        sp.onUpdateAbilities();
        sp.teleportTo(0.5, sp.getY(), 0.5);
        sp.setYRot(180);
        sp.setXRot(0);
        var inv = sp.getInventory();
        inv.clearContent();
        String[] guns = {"glock17", "m4a1", "awm", "rem870", "akm", "model29", "m249"};
        for (int i = 0; i < guns.length; i++) {
            ItemStack st = new ItemStack(ModRegistry.GUNS.get(guns[i]).get());
            GunItem g = (GunItem) st.getItem();
            GunItem.setState(st, GunState.full(g.def()));
            if (guns[i].equals("m4a1")) st.set(ModRegistry.GUN_ATTACHMENTS.get(),
                    GunAttachments.NONE.with(Attachment.ACOG).with(Attachment.VERTICAL_GRIP).with(Attachment.SUPPRESSOR_RIFLE));
            if (guns[i].equals("glock17")) GunItem.setState(st, new GunState(10, true, 0));
            inv.setItem(i, st);
        }
        int slot = 9;
        for (Caliber c : Caliber.values()) inv.setItem(slot++, new ItemStack(ModRegistry.AMMO.get(c).get(), c == Caliber.PG7 ? 4 : 64));
        for (Attachment a : new Attachment[]{Attachment.RED_DOT, Attachment.HOLO, Attachment.LASER, Attachment.COMPENSATOR})
            inv.setItem(slot++, new ItemStack(ModRegistry.ATTACHMENTS.get(a).get()));
        inv.setSelectedSlot(0);
        BlockPos front = sp.blockPosition().relative(sp.getDirection(), 2);
        level.setBlockAndUpdate(front.east(), ModRegistry.WORKBENCH.get().defaultBlockState());
        level.setBlockAndUpdate(front, ModRegistry.WORKBENCH.get().defaultBlockState());
        workbenchPos = front;
        var merc = ModRegistry.MERCENARY.get().create(level, EntitySpawnReason.COMMAND);
        if (merc != null) {
            merc.snapTo(0.5, sp.getY(), 8.5, 0, 0);
            merc.finalizeSpawn(level, level.getCurrentDifficultyAt(merc.blockPosition()), EntitySpawnReason.COMMAND, null);
            merc.setNoAi(true);
            merc.setYRot(0);
            merc.setYHeadRot(0);
            level.addFreshEntity(merc);
        }
        // put the mercenary behind the player; the player initially faces north (-Z) at the workbench
        if (merc != null) merc.snapTo(0.5, sp.getY(), 6.5, 180, 0);
    }
}
