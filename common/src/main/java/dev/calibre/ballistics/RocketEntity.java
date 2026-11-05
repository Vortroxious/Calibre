package dev.calibre.ballistics;

import dev.calibre.CalibreConfig;
import dev.calibre.registry.ModRegistry;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animatable.manager.AnimatableManager;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * PG-7V: 115 m/s launch, sustainer burns up to ~295 m/s, arms after 5 m (dud before that), HEAT warhead.
 */
public class RocketEntity extends Projectile implements GeoEntity {
    private static final double LAUNCH = 115 / 20.0, SUSTAIN = 295 / 20.0, ARM_DISTANCE = 5.0;
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private int life;
    private double traveled;

    public RocketEntity(EntityType<? extends RocketEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public RocketEntity(Level level, LivingEntity shooter) {
        this(ModRegistry.ROCKET.get(), level);
        setOwner(shooter);
    }

    public void launch(Vec3 dir) {
        setDeltaMovement(dir.scale(LAUNCH));
        faceVelocity();
    }

    private void faceVelocity() {
        Vec3 v = getDeltaMovement();
        setYRot((float) Math.toDegrees(Math.atan2(v.x, v.z)));
        setXRot((float) Math.toDegrees(Math.atan2(v.y, v.horizontalDistance())));
    }

    @Override
    protected void defineSynchedData(net.minecraft.network.syncher.SynchedEntityData.Builder builder) {}

    @Override
    public void tick() {
        this.xOld = getX();
        this.yOld = getY();
        this.zOld = getZ();
        this.xo = getX();
        this.yo = getY();
        this.zo = getZ();
        this.yRotO = getYRot();
        this.xRotO = getXRot();
        life++;
        Vec3 vel = getDeltaMovement();
        double speed = vel.length();
        if (life > 3 && speed < SUSTAIN) vel = vel.scale(Math.min(SUSTAIN, speed + 1.4) / speed);
        vel = vel.subtract(0, 0.006, 0);
        if (level().isClientSide()) {
            Vec3 back = position().subtract(vel.normalize().scale(0.6));
            level().addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE, back.x, back.y, back.z, 0, 0.01, 0);
            level().addParticle(ParticleTypes.FLAME, back.x, back.y, back.z, -vel.x * 0.05, -vel.y * 0.05, -vel.z * 0.05);
            setPos(position().add(vel));
            setDeltaMovement(vel);
            faceVelocity();
            return;
        }
        Vec3 start = position();
        Vec3 end = start.add(vel);
        BlockHitResult bhr = level().clip(new ClipContext(start, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.ANY, this));
        Vec3 stop = bhr.getType() == HitResult.Type.MISS ? end : bhr.getLocation();
        EntityHitResult ehr = ProjectileUtil.getEntityHitResult(level(), this, start, stop, new AABB(start, stop).inflate(1.0),
                e -> e.isPickable() && !e.isSpectator() && e != getOwner(), 0.3f);
        if (ehr != null) {
            detonate(ehr.getLocation(), ehr.getEntity());
            return;
        }
        if (bhr.getType() == HitResult.Type.BLOCK) {
            detonate(bhr.getLocation(), null);
            return;
        }
        traveled += vel.length();
        setPos(end);
        setDeltaMovement(vel);
        faceVelocity();
        if (life > 160) detonate(position(), null); // self-destruct at ~900 m
    }

    private void detonate(Vec3 at, net.minecraft.world.entity.Entity direct) {
        ServerLevel sl = (ServerLevel) level();
        if (traveled + 1 < ARM_DISTANCE) {
            // not armed yet: dud
            SoundEvent s = ModRegistry.sound("impact_metal");
            if (s != null) sl.playSound(null, at.x, at.y, at.z, s, SoundSource.NEUTRAL, 1f, 0.6f);
            if (direct != null) direct.hurtServer(sl, sl.damageSources().source(ModRegistry.BULLET_DAMAGE, this, getOwner()), 8f);
            discard();
            return;
        }
        if (direct != null) {
            direct.invulnerableTime = 0;
            direct.hurtServer(sl, sl.damageSources().source(ModRegistry.BULLET_DAMAGE, this, getOwner()), 30f);
        }
        sl.explode(this, sl.damageSources().explosion(this, getOwner()), null, at.x, at.y, at.z, 3.2f, false,
                CalibreConfig.explosionsBreakBlocks() ? Level.ExplosionInteraction.MOB : Level.ExplosionInteraction.NONE);
        SoundEvent s = ModRegistry.sound("explosion");
        if (s != null) sl.playSound(null, at.x, at.y, at.z, s, SoundSource.NEUTRAL, 6f, 1f);
        discard();
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double d) {
        return d < 256 * 256;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {}

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput input) {
        life = input.getIntOr("life", 0);
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput output) {
        output.putInt("life", life);
    }
}
