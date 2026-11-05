package dev.calibre.ballistics;

import dev.calibre.CalibreConfig;
import dev.calibre.gun.Attachment;
import dev.calibre.gun.Caliber;
import dev.calibre.gun.GunAttachments;
import dev.calibre.gun.GunDefinition;
import dev.calibre.gun.GunItem;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Spawns projectiles for a shot: spread, pellets, tracers. */
public final class Ballistics {
    private static final Map<UUID, Integer> SHOT_COUNT = new HashMap<>();

    private Ballistics() {}

    /** Current cone (full angle, degrees) for a shooter. Shared with the client crosshair. */
    public static float spread(LivingEntity shooter, GunDefinition def, GunAttachments att, boolean aiming) {
        float s = aiming ? def.adsSpread() * att.product(a -> a.adsSpread) : def.hipSpread() * att.product(a -> a.hipSpread);
        Vec3 v = shooter.getDeltaMovement();
        double horiz = Math.sqrt(v.x * v.x + v.z * v.z);
        if (horiz > 0.05) s *= aiming ? 1.6f : 1.35f;
        if (shooter.isSprinting()) s *= 1.5f;
        if (!shooter.onGround()) s *= 2.2f;
        if (shooter.isCrouching()) {
            s *= 0.75f;
            if (att.has(Attachment.BIPOD_ATT) || def.category() == GunDefinition.Category.LMG) s *= 0.6f;
        }
        return s;
    }

    public static void fire(LivingEntity shooter, ItemStack stack, GunDefinition def, boolean aiming, float yaw, float pitch) {
        if (!(shooter.level() instanceof ServerLevel level)) return;
        GunAttachments att = GunItem.attachments(stack);
        RandomSource rnd = shooter.getRandom();
        Vec3 eye = shooter.getEyePosition();
        float cone = spread(shooter, def, att, aiming);
        if (!(shooter instanceof Player)) cone = cone * 1.8f + 0.8f;
        Caliber c = def.caliber();
        if (c == Caliber.PG7) {
            Vec3 dir = deviate(yaw, pitch, cone, rnd);
            RocketEntity r = new RocketEntity(level, shooter);
            r.setPos(eye.add(dir.scale(0.8)).add(0, -0.1, 0));
            r.launch(dir);
            level.addFreshEntity(r);
            return;
        }
        int n = SHOT_COUNT.merge(shooter.getUUID(), 1, Integer::sum);
        boolean tracer = CalibreConfig.allTracers() || (def.category() == GunDefinition.Category.LMG ? n % 3 == 0 : n % 5 == 0);
        float vel = c.blocksPerTick() * def.velocityMul() * att.product(a -> a.velocity);
        float dmg = c.damage * def.damageMul() * (float) CalibreConfig.damageMultiplier();
        if (!(shooter instanceof Player)) dmg *= (float) CalibreConfig.mobDamageMultiplier();
        for (int i = 0; i < c.pellets; i++) {
            float pelletCone = c.pellets > 1 ? Math.max(cone, 3.2f) : cone;
            Vec3 dir = deviate(yaw, pitch, pelletCone, rnd);
            BulletEntity b = new BulletEntity(level, shooter, c, dmg, def.range(), tracer && i == 0);
            b.setPos(eye.x, eye.y - 0.06, eye.z);
            b.setDeltaMovement(dir.scale(vel));
            b.setYRot((float) (Mth.atan2(dir.x, dir.z) * Mth.RAD_TO_DEG));
            b.setXRot((float) (Mth.atan2(dir.y, dir.horizontalDistance()) * Mth.RAD_TO_DEG));
            level.addFreshEntity(b);
        }
    }

    /** direction from yaw/pitch, randomly deviated inside a cone of `coneDeg` (gaussian, ~95% inside). */
    public static Vec3 deviate(float yaw, float pitch, float coneDeg, RandomSource rnd) {
        float r = (float) (Math.abs(rnd.nextGaussian()) * coneDeg * 0.25f);
        float a = rnd.nextFloat() * Mth.TWO_PI;
        float y = yaw + Mth.cos(a) * r;
        float p = pitch + Mth.sin(a) * r;
        return Vec3.directionFromRotation(p, y);
    }
}
