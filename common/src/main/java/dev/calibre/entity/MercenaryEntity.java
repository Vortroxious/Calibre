package dev.calibre.entity;

import dev.calibre.gun.GunDefinition;
import dev.calibre.gun.GunItem;
import dev.calibre.gun.GunLogic;
import dev.calibre.gun.GunMeta;
import dev.calibre.gun.GunState;
import dev.calibre.registry.ModRegistry;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.golem.IronGolem;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import org.jspecify.annotations.Nullable;

import java.util.EnumSet;
import java.util.List;

/** A hostile, armed humanoid. Carries a random real gun, shoots in bursts, strafes, takes cover-ish pauses to reload. */
public class MercenaryEntity extends Monster {
    private static final List<String> LOADOUT = List.of(
            "glock17", "glock17", "m9", "m1911", "mp5", "mp5", "uzi", "ump45", "akm", "akm", "m4a1", "m4a1", "rem870", "fal", "svd",
            "ak47", "sks", "mosin", "ppsh41", "nova", "win1894", "ppq", "m45", "stg44", "mp40", "g3a3", "galil", "sten", "kar98k", "ak74m", "aks74u", "rpk", "pps43", "svt40", "makarov");

    public MercenaryEntity(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.xpReward = 12;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 26)
                .add(Attributes.MOVEMENT_SPEED, 0.27)
                .add(Attributes.ARMOR, 4)
                .add(Attributes.FOLLOW_RANGE, 48)
                .add(Attributes.ATTACK_DAMAGE, 3);
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new RangedGunGoal(this));
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 12f));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
    }

    @Override
    public @Nullable SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance diff, EntitySpawnReason reason,
                                                  @Nullable SpawnGroupData data) {
        SpawnGroupData out = super.finalizeSpawn(level, diff, reason, data);
        RandomSource r = level.getRandom();
        String id = LOADOUT.get(r.nextInt(LOADOUT.size()));
        ItemStack gun = new ItemStack(ModRegistry.GUNS.get(id).get());
        GunItem gi = (GunItem) gun.getItem();
        GunItem.setState(gun, GunState.full(gi.def()));
        setItemSlot(EquipmentSlot.MAINHAND, gun);
        setDropChance(EquipmentSlot.MAINHAND, 0.12f);
        if (r.nextFloat() < 0.5f) setItemSlot(EquipmentSlot.HEAD, new ItemStack(Items.LEATHER_HELMET));
        if (r.nextFloat() < 0.35f) setItemSlot(EquipmentSlot.CHEST, new ItemStack(Items.CHAINMAIL_CHESTPLATE));
        setDropChance(EquipmentSlot.HEAD, 0.05f);
        setDropChance(EquipmentSlot.CHEST, 0.05f);
        return out;
    }

    @Override
    protected void dropCustomDeathLoot(ServerLevel level, DamageSource src, boolean recent) {
        super.dropCustomDeathLoot(level, src, recent);
        if (getMainHandItem().getItem() instanceof GunItem gun) {
            int n = 4 + random.nextInt(Math.max(1, gun.def().magSize() / 2));
            spawnAtLocation(level, new ItemStack(ModRegistry.AMMO.get(gun.def().caliber()).get(), n));
        }
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return SoundEvents.PILLAGER_AMBIENT;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource src) {
        return SoundEvents.PILLAGER_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.PILLAGER_DEATH;
    }

    public static boolean holdsGun(Mob m) {
        return m.getMainHandItem().getItem() instanceof GunItem;
    }

    // ------------------------------------------------------------------------------------------------
    static class RangedGunGoal extends Goal {
        private final MercenaryEntity mob;
        private int seeTime, cooldown, burstLeft, reloadTicks, strafeTime;
        private boolean strafeLeft, strafeBack;

        RangedGunGoal(MercenaryEntity mob) {
            this.mob = mob;
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = mob.getTarget();
            return t != null && t.isAlive() && holdsGun(mob);
        }

        @Override
        public void stop() {
            mob.setAggressive(false);
            seeTime = 0;
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            LivingEntity target = mob.getTarget();
            if (target == null) return;
            ItemStack stack = mob.getMainHandItem();
            if (!(stack.getItem() instanceof GunItem gun)) return;
            GunDefinition def = gun.def();
            double dist = mob.distanceToSqr(target);
            boolean sees = mob.getSensing().hasLineOfSight(target);
            seeTime = sees ? seeTime + 1 : Math.max(0, seeTime - 1);
            double ideal = def.category() == GunDefinition.Category.SHOTGUN ? 8 : def.category() == GunDefinition.Category.DMR ? 28 : 16;
            mob.setAggressive(true);
            if (dist > ideal * ideal * 1.6 || !sees) {
                mob.getNavigation().moveTo(target, 1.0);
                strafeTime = -1;
            } else {
                mob.getNavigation().stop();
                strafeTime++;
                if (strafeTime >= 25) {
                    if (mob.getRandom().nextFloat() < 0.35f) strafeLeft = !strafeLeft;
                    if (mob.getRandom().nextFloat() < 0.3f) strafeBack = !strafeBack;
                    strafeTime = 0;
                }
                boolean close = dist < ideal * ideal * 0.4;
                mob.getMoveControl().strafe(close || strafeBack ? -0.45f : 0.2f, strafeLeft ? 0.45f : -0.45f);
            }
            mob.getLookControl().setLookAt(target, 30f, 30f);
            mob.lookAt(target, 30f, 30f);

            if (reloadTicks > 0) {
                if (--reloadTicks == 0) {
                    GunItem.setState(stack, GunState.full(def));
                }
                return;
            }
            GunState s = GunItem.state(stack);
            if (s.total() == 0) {
                GunMeta m = gun.meta();
                String anim = m.has("reload_empty") ? "reload_empty" : m.has("reload") ? "reload" : "reload_start";
                GunMeta.Action a = m.action(anim);
                reloadTicks = a == null ? 60 : a.ticks() + 10;
                GunLogic.broadcast(mob, anim, false, false);
                return;
            }
            if (--cooldown > 0 || !sees || seeTime < 8) return;
            double dx = target.getX() - mob.getX();
            double dy = target.getEyeY() - 0.35 - mob.getEyeY();
            double dz = target.getZ() - mob.getZ();
            float yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90f;
            float pitch = (float) -(Mth.atan2(dy, Math.sqrt(dx * dx + dz * dz)) * Mth.RAD_TO_DEG);
            boolean fired = GunLogic.fire(mob, stack, gun, false, yaw, pitch);
            if (def.cycle().manual()) {
                GunState after = GunItem.state(stack);
                if (!after.chambered() && after.ammo() > 0) GunItem.setState(stack, new GunState(after.ammo() - 1, true, after.mode()));
            }
            if (!fired) return;
            boolean auto = def.modes().contains(GunDefinition.FireMode.AUTO);
            if (burstLeft <= 0) burstLeft = auto ? 3 + mob.getRandom().nextInt(4) : 1;
            burstLeft--;
            int shotTicks = Math.max(def.ticksBetweenShots(), def.cycle().manual() ? 24 : 2);
            cooldown = burstLeft > 0 ? shotTicks : shotTicks + 14 + mob.getRandom().nextInt(16);
            if (!auto) cooldown = Math.max(cooldown, 9 + mob.getRandom().nextInt(10));
        }
    }

    public static boolean checkSpawn(EntityType<? extends Monster> type, ServerLevelAccessor level, EntitySpawnReason reason, BlockPos pos, RandomSource random) {
        return Monster.checkMonsterSpawnRules(type, level, reason, pos, random);
    }
}
