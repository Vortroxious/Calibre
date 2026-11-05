package dev.calibre.test;

import dev.calibre.Calibre;
import dev.calibre.ballistics.Ballistics;
import dev.calibre.ballistics.BulletEntity;
import dev.calibre.gun.Caliber;
import dev.calibre.gun.GunItem;
import dev.calibre.gun.GunLogic;
import dev.calibre.gun.GunMeta;
import dev.calibre.gun.GunState;
import dev.calibre.gun.Guns;
import dev.calibre.registry.ModRegistry;
import dev.calibre.workbench.GunsmithingRecipes;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.FunctionGameTestInstance;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.gametest.framework.TestData;
import net.minecraft.gametest.framework.TestEnvironmentDefinition;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.zombie.Zombie;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Consumer;

/** GameTests: run with ./gradlew runGameTestServer */
public final class CalibreGameTests {
    /** test name -> function; registered as calibre:&lt;name&gt; test functions, run in the calibre:range structure */
    public static final Map<String, Consumer<GameTestHelper>> TESTS = new LinkedHashMap<>();

    static {
        TESTS.put("bullet_damages_zombie", CalibreGameTests::bulletDamagesZombie);
        TESTS.put("headshot_multiplier", CalibreGameTests::headshot);
        TESTS.put("glass_penetration", CalibreGameTests::glass);
        TESTS.put("every_gun_has_meta", CalibreGameTests::meta);
        TESTS.put("fire_consumes_rounds", CalibreGameTests::consumes);
        TESTS.put("recipes_resolve", CalibreGameTests::recipes);
        TESTS.put("creative_fire_empties_mag", CalibreGameTests::creativeFire);
        TESTS.put("reload_refills_after_event", CalibreGameTests::reloadRefills);
        TESTS.put("stripper_clip_reload_fills_5", CalibreGameTests::clipFillsMosin);
        TESTS.put("sks_loads_two_clips", CalibreGameTests::clipsSks);
        TESTS.put("lever_cycle_chambers", CalibreGameTests::leverCycle);
        TESTS.put("single_action_gate_reload", CalibreGameTests::singleAction);
    }

    /** Registers calibre:&lt;name&gt; test functions (NeoForge; Fabric's gametest API registers its own wrappers). */
    public static void registerFunctions() {
        for (var e : TESTS.entrySet())
            dev.calibre.platform.Platform.INSTANCE.register(net.minecraft.core.registries.BuiltInRegistries.TEST_FUNCTION, e.getKey(), e::getValue);
    }

    private static Zombie zombie(GameTestHelper h, BlockPos at) {
        Zombie z = h.spawn(EntityType.ZOMBIE, at);
        z.setNoAi(true);
        z.setSilent(true);
        return z;
    }

    private static void shootAt(GameTestHelper h, Vec3 from, Vec3 to, Caliber c, float dmg) {
        Zombie shooter = h.spawn(EntityType.ZOMBIE, new BlockPos(0, 1, 0));
        shooter.setNoAi(true);
        shooter.setInvisible(true);
        Vec3 a = h.absoluteVec(from), b = h.absoluteVec(to);
        BulletEntity bullet = new BulletEntity(h.getLevel(), shooter, c, dmg, 100, false);
        bullet.setPos(a);
        bullet.setDeltaMovement(b.subtract(a).normalize().scale(c.blocksPerTick()));
        h.getLevel().addFreshEntity(bullet);
        h.runAfterDelay(2, shooter::discard);
    }

    private static void bulletDamagesZombie(GameTestHelper h) {
        Zombie z = zombie(h, new BlockPos(2, 1, 6));
        float hp = z.getHealth();
        shootAt(h, new Vec3(2.5, 2.0, 1.5), new Vec3(2.5, 2.0, 6.5), Caliber.NATO556, 7f);
        h.succeedWhen(() -> h.assertTrue(z.getHealth() < hp, "zombie was not hurt by the bullet"));
    }

    private static void headshot(GameTestHelper h) {
        Zombie body = zombie(h, new BlockPos(1, 1, 6));
        Zombie head = zombie(h, new BlockPos(3, 1, 6));
        shootAt(h, new Vec3(1.5, 1.9, 1.5), new Vec3(1.5, 1.9, 6.5), Caliber.NINE_MM, 6f);
        shootAt(h, new Vec3(3.5, 2.75, 1.5), new Vec3(3.5, 2.75, 6.5), Caliber.NINE_MM, 6f);
        h.succeedWhen(() -> {
            float bodyLoss = body.getMaxHealth() - body.getHealth();
            float headLoss = head.getMaxHealth() - head.getHealth();
            h.assertTrue(bodyLoss > 0 && headLoss > bodyLoss * 1.5f, "headshot " + headLoss + " vs body " + bodyLoss);
        });
    }

    private static void glass(GameTestHelper h) {
        h.setBlock(new BlockPos(2, 2, 4), Blocks.GLASS);
        Zombie z = zombie(h, new BlockPos(2, 1, 7));
        float hp = z.getHealth();
        shootAt(h, new Vec3(2.5, 2.5, 1.5), new Vec3(2.5, 2.5, 7.5), Caliber.NATO762, 10f);
        h.succeedWhen(() -> {
            h.assertBlockNotPresent(Blocks.GLASS, new BlockPos(2, 2, 4));
            h.assertTrue(z.getHealth() < hp, "bullet did not continue through the glass");
        });
    }

    private static void meta(GameTestHelper h) {
        for (var def : Guns.all()) {
            GunMeta m = GunMeta.get(def.id());
            h.assertTrue(m.has("idle") && m.has("fire") && m.has("draw") && m.has("inspect"), def.id() + " missing core animations");
            boolean reload = m.has("reload") || m.has("reload_start");
            h.assertTrue(reload, def.id() + " has no reload");
            if (def.cycle().manual()) h.assertTrue(m.has("cycle"), def.id() + " manual action without cycle");
        }
        h.succeed();
    }

    private static void consumes(GameTestHelper h) {
        Zombie shooter = zombie(h, new BlockPos(2, 1, 2));
        ItemStack stack = new ItemStack(ModRegistry.GUNS.get("glock17").get());
        GunItem gun = (GunItem) stack.getItem();
        GunItem.setState(stack, new GunState(3, true, 0));
        GunLogic.fire(shooter, stack, gun, false, 0, 0);
        GunState s = GunItem.state(stack);
        h.assertTrue(s.ammo() == 2 && s.chambered(), "after one shot expected 2+1, got " + s);
        GunItem.setState(stack, new GunState(0, false, 0));
        boolean fired = GunLogic.fire(shooter, stack, gun, false, 0, 0);
        h.assertFalse(fired, "an empty gun fired");
        h.succeed();
    }

    /** Creative players must still empty the magazine (only the reserve is infinite), otherwise R is refused. */
    private static void creativeFire(GameTestHelper h) {
        var player = h.makeMockPlayer(net.minecraft.world.level.GameType.CREATIVE);
        ItemStack stack = new ItemStack(ModRegistry.GUNS.get("glock17").get());
        GunItem gun = (GunItem) stack.getItem();
        GunItem.setState(stack, GunState.full(gun.def()));
        GunLogic.fire(player, stack, gun, false, 0, 0);
        GunState s = GunItem.state(stack);
        h.assertTrue(s.ammo() == 16 && s.chambered(), "creative shot should leave 16+1, got " + s);
        h.succeed();
    }

    /** A half-empty gun with ammo in the inventory is full once the reload's "ammo" moment has passed. */
    private static void reloadRefills(GameTestHelper h) {
        var sp = h.makeMockServerPlayerInLevel();
        sp.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
        ItemStack stack = new ItemStack(ModRegistry.GUNS.get("glock17").get());
        GunItem.setState(stack, new GunState(5, true, 0));
        sp.getInventory().setItem(0, stack);
        sp.getInventory().setSelectedSlot(0);
        sp.getInventory().setItem(1, new ItemStack(ModRegistry.AMMO.get(Caliber.NINE_MM).get(), 64));
        GunLogic.tick(sp);                                    // registers the held gun (starts the draw)
        GunLogic.onRequest(sp, dev.calibre.network.Net.Request.RELOAD);
        h.onEachTick(() -> GunLogic.tick(sp));
        h.succeedWhen(() -> {
            GunState s = GunItem.state(sp.getMainHandItem());
            h.assertTrue(s.ammo() == 17 && s.chambered(), "expected 17+1 after reload, got " + s);
            h.assertTrue(sp.getInventory().getItem(1).getCount() == 64 - 12, "reload should take 12 rounds");
        });
    }

    private static void recipes(GameTestHelper h) {
        h.assertTrue(GunsmithingRecipes.all().size() >= Guns.all().size(), "recipe count");
        for (var r : GunsmithingRecipes.all()) h.assertFalse(r.resultStack().isEmpty(), "empty recipe result");
        h.assertTrue(Ballistics.deviate(0, 0, 0, h.getLevel().getRandom()).z > 0.99, "zero spread must not deviate");
        h.succeed();
    }

    private static net.minecraft.server.level.ServerPlayer holding(GameTestHelper h, String gun, GunState state, Caliber ammo, int n) {
        var sp = h.makeMockServerPlayerInLevel();
        sp.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
        ItemStack stack = new ItemStack(ModRegistry.GUNS.get(gun).get());
        GunItem.setState(stack, state);
        sp.getInventory().setItem(0, stack);
        sp.getInventory().setSelectedSlot(0);
        if (n > 0) sp.getInventory().setItem(1, new ItemStack(ModRegistry.AMMO.get(ammo).get(), n));
        GunLogic.tick(sp);
        h.onEachTick(() -> GunLogic.tick(sp));
        return sp;
    }

    /** Empty Mosin: one stripper clip (5 rounds in one go), then closing the bolt chambers the top round. */
    private static void clipFillsMosin(GameTestHelper h) {
        var sp = holding(h, "mosin", new GunState(0, false, 0), Caliber.R762X54, 20);
        GunLogic.onRequest(sp, dev.calibre.network.Net.Request.RELOAD);
        h.succeedWhen(() -> {
            GunState s = GunItem.state(sp.getMainHandItem());
            h.assertTrue(s.ammo() == 4 && s.chambered(), "expected 4+1 after a clip, got " + s);
            h.assertTrue(sp.getInventory().getItem(1).getCount() == 15, "a clip should take exactly 5 rounds");
            h.assertFalse(GunLogic.isBusy(sp), "reload still running");
        });
    }

    /** SKS from empty takes two 5-round clips (10-round magazine), then the carrier strips one into the chamber. */
    private static void clipsSks(GameTestHelper h) {
        var sp = holding(h, "sks", new GunState(0, false, 0), Caliber.R762X39, 30);
        GunLogic.onRequest(sp, dev.calibre.network.Net.Request.RELOAD);
        h.succeedWhen(() -> {
            GunState s = GunItem.state(sp.getMainHandItem());
            h.assertTrue(s.ammo() == 9 && s.chambered(), "expected 9+1, got " + s);
            h.assertTrue(sp.getInventory().getItem(1).getCount() == 20, "two clips should take 10 rounds");
            h.assertFalse(GunLogic.isBusy(sp), "reload still running");
        });
    }

    /** Firing a lever gun leaves the chamber empty until the lever is worked, which then feeds from the tube. */
    private static void leverCycle(GameTestHelper h) {
        var sp = holding(h, "win1894", new GunState(3, true, 0), Caliber.WIN3030, 0);
        h.runAfterDelay(20, () -> {
            ItemStack st = sp.getMainHandItem();
            boolean fired = GunLogic.fire(sp, st, (GunItem) st.getItem(), false, sp.getYRot(), sp.getXRot());
            h.assertTrue(fired, "loaded Winchester did not fire");
            GunState s = GunItem.state(st);
            h.assertTrue(!s.chambered() && s.ammo() == 3, "the lever must not cycle by itself, got " + s);
        });
        h.runAfterDelay(60, () -> {
            GunState s = GunItem.state(sp.getMainHandItem());
            h.assertTrue(s.ammo() == 2 && s.chambered(), "lever cycle should chamber from the tube, got " + s);
            h.succeed();
        });
    }

    /** Single action: the gate takes one round per loop until all six chambers are full. */
    private static void singleAction(GameTestHelper h) {
        var sp = holding(h, "singlesix", new GunState(2, false, 0), Caliber.LR22, 10);
        GunLogic.onRequest(sp, dev.calibre.network.Net.Request.RELOAD);
        h.succeedWhen(() -> {
            GunState s = GunItem.state(sp.getMainHandItem());
            h.assertTrue(s.ammo() == 6, "expected 6 in the cylinder, got " + s);
            h.assertTrue(sp.getInventory().getItem(1).getCount() == 6, "should take 4 rounds");
            h.assertFalse(GunLogic.isBusy(sp), "reload still running");
        });
    }

    private CalibreGameTests() {}

}
