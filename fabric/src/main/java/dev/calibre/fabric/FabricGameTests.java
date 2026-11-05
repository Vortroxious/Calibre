package dev.calibre.fabric;

import dev.calibre.test.CalibreGameTests;
import net.fabricmc.fabric.api.gametest.v1.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;

/**
 * Fabric gametest-API wrappers around the shared tests in {@link CalibreGameTests} (the same functions NeoForge runs).
 * Run with ./gradlew :fabric:runGametest
 */
public final class FabricGameTests {
    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void bullet_damages_zombie(GameTestHelper h) {
        CalibreGameTests.TESTS.get("bullet_damages_zombie").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void headshot_multiplier(GameTestHelper h) {
        CalibreGameTests.TESTS.get("headshot_multiplier").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void glass_penetration(GameTestHelper h) {
        CalibreGameTests.TESTS.get("glass_penetration").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void every_gun_has_meta(GameTestHelper h) {
        CalibreGameTests.TESTS.get("every_gun_has_meta").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void fire_consumes_rounds(GameTestHelper h) {
        CalibreGameTests.TESTS.get("fire_consumes_rounds").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void recipes_resolve(GameTestHelper h) {
        CalibreGameTests.TESTS.get("recipes_resolve").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void creative_fire_empties_mag(GameTestHelper h) {
        CalibreGameTests.TESTS.get("creative_fire_empties_mag").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void reload_refills_after_event(GameTestHelper h) {
        CalibreGameTests.TESTS.get("reload_refills_after_event").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void stripper_clip_reload_fills_5(GameTestHelper h) {
        CalibreGameTests.TESTS.get("stripper_clip_reload_fills_5").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void sks_loads_two_clips(GameTestHelper h) {
        CalibreGameTests.TESTS.get("sks_loads_two_clips").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void lever_cycle_chambers(GameTestHelper h) {
        CalibreGameTests.TESTS.get("lever_cycle_chambers").accept(h);
    }

    @GameTest(structure = "calibre:range", maxTicks = 200)
    public void single_action_gate_reload(GameTestHelper h) {
        CalibreGameTests.TESTS.get("single_action_gate_reload").accept(h);
    }
}
