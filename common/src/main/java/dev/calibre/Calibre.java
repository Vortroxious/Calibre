package dev.calibre;

import dev.calibre.entity.MercenaryEntity;
import dev.calibre.gun.GunLogic;
import dev.calibre.registry.ModRegistry;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Loader-neutral entry points; the NeoForge and Fabric modules call these from their own lifecycle hooks. */
public final class Calibre {
    public static final String MODID = "calibre";
    public static final Logger LOGGER = LoggerFactory.getLogger("Calibre");

    private Calibre() {}

    public static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(MODID, path);
    }

    /** Hands every registry entry to the platform. Call once, during mod construction. */
    public static void init() {
        ModRegistry.init();
    }

    public static void playerTick(ServerPlayer player) {
        GunLogic.tick(player);
    }

    public static void playerLogout(Player player) {
        GunLogic.clear(player);
    }

    public static boolean mercenaryCanSpawn(EntityType<? extends MercenaryEntity> type, ServerLevelAccessor level,
                                            EntitySpawnReason reason, BlockPos pos, RandomSource random) {
        return CalibreConfig.mercenarySpawns() && Monster.checkMonsterSpawnRules(type, level, reason, pos, random);
    }
}
