package dev.calibre.ballistics;

import dev.calibre.CalibreConfig;
import dev.calibre.gun.Caliber;
import dev.calibre.network.Net;
import dev.calibre.registry.ModRegistry;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.HashSet;
import java.util.Set;

/**
 * A real projectile: sub-stepped ray cast every tick with gravity and drag, so long shots drop and take time to arrive.
 * Penetrates glass, leaves, wood and (for heavy calibres) masonry, and can over-penetrate soft targets.
 */
public class BulletEntity extends Projectile {
    // conventional "c:" tags, shared by NeoForge and Fabric
    private static final net.minecraft.tags.TagKey<net.minecraft.world.level.block.Block> GLASS_BLOCKS = net.minecraft.tags.TagKey.create(
            net.minecraft.core.registries.Registries.BLOCK, net.minecraft.resources.Identifier.fromNamespaceAndPath("c", "glass_blocks"));
    private static final net.minecraft.tags.TagKey<net.minecraft.world.level.block.Block> GLASS_PANES = net.minecraft.tags.TagKey.create(
            net.minecraft.core.registries.Registries.BLOCK, net.minecraft.resources.Identifier.fromNamespaceAndPath("c", "glass_panes"));

    private static final EntityDataAccessor<Boolean> TRACER = SynchedEntityData.defineId(BulletEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> COLOR = SynchedEntityData.defineId(BulletEntity.class, EntityDataSerializers.INT);
    /** 9.81 m/s² in blocks/tick² */
    private static final double GRAVITY = 9.81 / 400.0;
    private static final double DRAG = 0.996;

    private float damage = 6;
    private float penetration = 1;
    private float range = 100;
    private float armorPierce = 0;
    private int pierce = 1;
    private int life;
    private double traveled;
    private boolean whizzed;
    private final Set<Integer> hitEntities = new HashSet<>();

    public BulletEntity(EntityType<? extends BulletEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public BulletEntity(Level level, LivingEntity shooter, Caliber caliber, float damage, float range, boolean tracer) {
        this(ModRegistry.BULLET.get(), level);
        setOwner(shooter);
        this.damage = damage;
        this.range = range;
        this.penetration = caliber.penetration;
        this.armorPierce = caliber.armorPierce;
        this.pierce = caliber.penetration >= 2 ? 2 : 1;
        this.entityData.set(TRACER, tracer);
        this.entityData.set(COLOR, caliber.tracerColor);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder b) {
        b.define(TRACER, false);
        b.define(COLOR, 0xFFB040);
    }

    public boolean isTracer() {
        return entityData.get(TRACER);
    }

    public int color() {
        return entityData.get(COLOR);
    }

    public int life() {
        return life;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double d) {
        return d < 256 * 256;
    }

    @Override
    public void tick() {
        // no super.tick(): we integrate ourselves
        this.xOld = getX();
        this.yOld = getY();
        this.zOld = getZ();
        this.xo = getX();
        this.yo = getY();
        this.zo = getZ();
        life++;
        Vec3 vel = getDeltaMovement();
        if (level().isClientSide()) {
            setPos(position().add(vel));
            setDeltaMovement(vel.scale(DRAG).subtract(0, GRAVITY, 0));
            if (life > 60) discard();
            return;
        }
        Vec3 start = position();
        Vec3 end = start.add(vel);
        int guard = 0;
        while (guard++ < 8 && !isRemoved()) {
            BlockHitResult bhr = level().clip(new ClipContext(start, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
            Vec3 stop = bhr.getType() == HitResult.Type.MISS ? end : bhr.getLocation();
            EntityHitResult ehr = ProjectileUtil.getEntityHitResult(level(), this, start, stop,
                    new AABB(start, stop).inflate(1.0), e -> e.isPickable() && !e.isSpectator() && e != getOwner() && !hitEntities.contains(e.getId()),
                    0.05f);
            if (ehr != null) {
                hitEntity(ehr, start);
                if (pierce <= 0 || isRemoved()) {
                    discard();
                    return;
                }
                start = ehr.getLocation();
                continue;
            }
            if (bhr.getType() == HitResult.Type.BLOCK) {
                if (!hitBlock(bhr, vel)) {
                    discard();
                    return;
                }
                start = bhr.getLocation().add(vel.normalize().scale(0.05));
                continue;
            }
            break;
        }
        whiz(start, end);
        traveled += vel.length();
        setPos(end);
        setDeltaMovement(vel.scale(DRAG).subtract(0, GRAVITY, 0));
        if (life > 80 || traveled > range * 3 || getY() < level().getMinY() - 16) discard();
    }

    private float falloff() {
        double d = traveled;
        if (d <= range * 0.5) return 1f;
        return (float) Math.max(0.35, 1 - (d - range * 0.5) / (range * 2.0));
    }

    private void hitEntity(EntityHitResult ehr, Vec3 from) {
        Entity target = ehr.getEntity();
        hitEntities.add(target.getId());
        float dmg = damage * falloff();
        boolean head = false;
        if (target instanceof LivingEntity le) {
            double hitY = ehr.getLocation().y;
            // the hit point from ProjectileUtil is the entity centre; refine with the bounding box clip
            var clip = target.getBoundingBox().clip(from, from.add(getDeltaMovement().scale(2)));
            if (clip.isPresent()) hitY = clip.get().y;
            double headStart = le.getEyeY() - 0.25 * (le.getBbHeight() / 1.8);
            head = hitY >= headStart && le.getBbHeight() > 0.9;
            if (head) dmg *= (float) CalibreConfig.headshotMultiplier();
            dmg *= 1 + armorPierce * Math.min(1, le.getArmorValue() / 20f);
        }
        DamageSource src = level().damageSources().source(head ? ModRegistry.BULLET_HEADSHOT : ModRegistry.BULLET_DAMAGE, this, getOwner());
        target.invulnerableTime = 0;
        boolean wasAlive = target.isAlive();
        boolean hurt = target.hurtServer((ServerLevel) level(), src, dmg);
        target.invulnerableTime = 0;
        if (hurt && target instanceof LivingEntity le) {
            ((ServerLevel) level()).sendParticles(ParticleTypes.DAMAGE_INDICATOR, ehr.getLocation().x, ehr.getLocation().y, ehr.getLocation().z,
                    2, 0.1, 0.1, 0.1, 0.1);
            play(ehr.getLocation(), "impact_flesh", 0.8f);
            if (getOwner() instanceof ServerPlayer sp) {
                int kind = wasAlive && !le.isAlive() ? Net.HitPayload.KILL : head ? Net.HitPayload.HEADSHOT : Net.HitPayload.HIT;
                if (dev.calibre.platform.Platform.INSTANCE.canReceive(sp, Net.HitPayload.TYPE))
                    dev.calibre.platform.Platform.INSTANCE.sendToPlayer(sp, new Net.HitPayload(kind));
            }
        }
        pierce--;
        damage *= 0.55f;
    }

    /** @return true if the bullet continues through the block. */
    private boolean hitBlock(BlockHitResult hit, Vec3 vel) {
        ServerLevel sl = (ServerLevel) level();
        BlockPos pos = hit.getBlockPos();
        BlockState state = sl.getBlockState(pos);
        Vec3 p = hit.getLocation();
        boolean glass = state.is(GLASS_BLOCKS) || state.is(GLASS_PANES) || state.is(BlockTags.ICE);
        if (glass) {
            if (CalibreConfig.bulletsBreakGlass()) {
                sl.destroyBlock(pos, false, getOwner());
            }
            play(p, "impact_glass", 0.9f);
            penetration -= 0.2f;
            damage *= 0.85f;
            return penetration > 0 && CalibreConfig.bulletsBreakGlass();
        }
        sl.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, state), p.x, p.y, p.z, 8, 0.05, 0.05, 0.05, 0.15);
        sl.sendParticles(ParticleTypes.SMOKE, p.x, p.y, p.z, 2, 0.02, 0.02, 0.02, 0.01);
        if (state.is(BlockTags.LEAVES)) {
            penetration -= 0.1f;
            return penetration > 0;
        }
        float h = state.getDestroySpeed(sl, pos);
        boolean soft = state.is(BlockTags.PLANKS) || state.is(BlockTags.LOGS) || state.is(BlockTags.WOOL) || state.is(BlockTags.WOODEN_DOORS)
                || state.is(BlockTags.WOODEN_TRAPDOORS) || state.is(BlockTags.WOODEN_FENCES) || state.is(BlockTags.WOODEN_SLABS);
        boolean masonry = penetration >= 4 && h >= 0 && h <= 2.0f;
        SoundType st = state.getSoundType();
        String snd = st == SoundType.WOOD || st == SoundType.BAMBOO_WOOD || st == SoundType.CHERRY_WOOD || st == SoundType.NETHER_WOOD ? "impact_wood"
                : st == SoundType.METAL || st == SoundType.ANVIL || st == SoundType.CHAIN || st == SoundType.COPPER ? "impact_metal"
                : st == SoundType.GRASS || st == SoundType.SAND || st == SoundType.GRAVEL || st == SoundType.SNOW || st == SoundType.ROOTED_DIRT
                || st == SoundType.WOOL || st == SoundType.MUD ? "impact_soft" : "impact_hard";
        play(p, snd, 0.7f);
        if ((soft || masonry) && h >= 0 && h <= penetration) {
            penetration -= Math.max(0.6f, h * 0.75f);
            damage *= 0.6f;
            return true;
        }
        return false;
    }

    private void whiz(Vec3 a, Vec3 b) {
        if (whizzed || traveled < 4) return;
        Vec3 seg = b.subtract(a);
        double len = seg.length();
        if (len < 1e-4) return;
        Vec3 dir = seg.scale(1 / len);
        for (ServerPlayer sp : ((ServerLevel) level()).players()) {
            if (sp == getOwner()) continue;
            Vec3 rel = sp.getEyePosition().subtract(a);
            double t = rel.dot(dir);
            if (t < 0 || t > len) continue;
            Vec3 closest = a.add(dir.scale(t));
            if (closest.distanceToSqr(sp.getEyePosition()) < 3.0 * 3.0) {
                SoundEvent s = ModRegistry.sound("bullet_whiz");
                if (s != null) sp.connection.send(new net.minecraft.network.protocol.game.ClientboundSoundPacket(
                        net.minecraft.core.registries.BuiltInRegistries.SOUND_EVENT.wrapAsHolder(s), SoundSource.PLAYERS,
                        closest.x, closest.y, closest.z, 0.9f, 0.9f + random.nextFloat() * 0.2f, random.nextLong()));
                whizzed = true;
            }
        }
    }

    private void play(Vec3 at, String name, float vol) {
        SoundEvent s = ModRegistry.sound(name);
        if (s != null) level().playSound(null, at.x, at.y, at.z, s, SoundSource.NEUTRAL, vol, 0.9f + random.nextFloat() * 0.2f);
    }

    @Override
    protected void readAdditionalSaveData(ValueInput input) {}

    @Override
    protected void addAdditionalSaveData(ValueOutput output) {}
}
