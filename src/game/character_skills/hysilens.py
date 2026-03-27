"""
海瑟音 (Hysilens) 角色技能设计

基于 https://starrailstation.com/cn/character/hysilens 数据

==============================
角色定位
==============================
- 属性：虚无 + 物理
- 定位：持续伤害 (DOT) 输出
- 核心机制：裂伤(物理DOT) + 结界追加DOT + DOT叠加

==============================
技能
==============================

【普攻】小调，止水中回响
- 对指定敌方单体造成50% ATK物理属性伤害

【战技】泛音，暗流后齐鸣
- 100%基础概率使敌方全体受到的伤害提高10%，持续3回合
- 对敌方全体造成70% ATK物理属性伤害

【终结技】绝海回涛，噬魂舞曲
- 展开结界(3回合)
- 敌方全体攻击力-15%，防御力-15%
- 对敌方全体造成120% ATK物理属性伤害
- 结界内敌人每受1次持续伤害，海瑟音对其造成32% ATK物理DOT(最多8次)
- 结界持续3回合，自身每回合开始时结界持续回合数减1

【天赋】海妖在欢唱
- 我方目标攻击时，100%基础概率使被击中敌人陷入：
  风化(风DOT)/裂伤(物理DOT)/灼烧(火DOT)/触电(雷DOT)其中1种
- 优先陷入不同状态
- 风化/灼烧/触电：10% ATK持续伤害，2回合
- 裂伤：自身20% Max HP物理DOT(上限为海瑟音10% ATK)，2回合

【秘技】于海的栖息地
- 制造持续20秒的特殊领域，使敌人陷入【醉心】状态

==============================
行迹/被动
==============================

【A2】征服的剑旗
- 战斗开始时展开与终结技相同的结界，持续3回合
- 每当海瑟音展开结界时，恢复1个战技点

【A4】盛会的泡沫
- 海瑟音施放终结技时，若敌方目标处于持续伤害状态，
  使其当前承受的所有持续伤害立即产生相当于原伤害150%的伤害

【A6】珍珠的琴弦
- 若海瑟音的效果命中高于60%，每超过10%可使自身造成的伤害提高15%，最多提高90%

==============================
命座（简化实现）
==============================

【1命】
- 海瑟音在场时，我方目标造成的持续伤害为原伤害的116%
- 当海瑟音通过天赋使敌人陷入状态时，有100%基础概率额外使敌人陷入1种可同时存在的状态

【6命】
- 结界持续期间，每回合触发物理持续伤害效果的次数上限提高至12次
- 造成的伤害倍率提高20%
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import (
    Character, Element, Skill, SkillType, Passive,
    BreakEffectType, BreakDot, Effect,
)
from src.game.damage import calculate_damage, apply_damage, DamageSource


# ============================================================
# DOT类型枚举（扩展现有击破类型）
# ============================================================
class HysilensDotType:
    """海瑟音DOT类型，用于天赋应用"""
    WOUND = "裂伤"           # 物理DOT
    WIND = "风化"            # 风DOT
    FIRE = "灼烧"            # 火DOT
    THUNDER = "触电"          # 雷DOT


# ============================================================
# 海瑟音结界Modifier
# ============================================================
class HysilensBarrierModifier(Modifier):
    """
    海瑟音的结界(Barrier)效果
    
    追踪：
    - 受影响敌人列表
    - 剩余持续回合
    - 已触发次数（每敌人）
    - 最大触发次数
    """
    
    def __init__(
        self,
        owner: Character,
        max_triggers: int = 8,
        dot_damage_mult: float = 0.32,
        duration: int = 3,
    ):
        super().__init__(
            name="绝海回涛结界",
            source_skill="绝海回涛，噬魂舞曲",
            duration=duration,
            modifier_type=ModifierType.DEBUFF,
            # 攻击力和防御力降低在应用时处理
        )
        self.owner = owner
        self._enemies_in_barrier: set[int] = set()  # 敌人ID集合
        self._trigger_counts: dict[int, int] = {}     # 每敌人的触发次数
        self._max_triggers = max_triggers
        self._dot_damage_mult = dot_damage_mult
        self._atb4_stacks: dict[int, int] = {}        # A4: 每个敌人已触发"盛会泡沫"的次数
    
    @property
    def remaining_duration(self) -> int:
        return self.duration
    
    @property
    def is_active(self) -> bool:
        return self.duration > 0
    
    def add_enemy(self, enemy: Character) -> None:
        """将敌人加入结界"""
        eid = id(enemy)
        if eid not in self._enemies_in_barrier:
            self._enemies_in_barrier.add(eid)
            self._trigger_counts[eid] = 0
    
    def on_tick(self) -> dict:
        """每回合减少持续时间"""
        if self.duration > 0:
            self.duration -= 1
        return {}
    
    def trigger_dot(
        self,
        enemy: Character,
        dot_source_name: str,
    ) -> tuple[bool, int]:
        """
        当结界内敌人受到DOT伤害时触发追加伤害
        
        Returns:
            (是否触发成功, 伤害值)
        """
        eid = id(enemy)
        if eid not in self._enemies_in_barrier:
            return False, 0
        
        if self._trigger_counts.get(eid, 0) >= self._max_triggers:
            return False, 0
        
        # 计算追加DOT伤害 (32% ATK)
        atk = self.owner.stat.total_atk()
        damage = int(atk * self._dot_damage_mult)
        
        self._trigger_counts[eid] = self._trigger_counts.get(eid, 0) + 1
        
        return True, damage


# ============================================================
# 海瑟音DOT状态管理器
# ============================================================
class HysilensDotManager:
    """
    管理海瑟音施加的所有DOT效果
    
    支持同一敌人身上叠加多个不同类型的DOT。
    每个DOT类型独立追踪。
    """
    
    def __init__(self, battle_state):
        self._battle_state = battle_state
        # {enemy_id: {dot_type: BreakDot}}
        self._dots: dict[int, dict[str, BreakDot]] = {}
        # 活跃DOT列表，用于快速遍历
        self._active_dots: list[tuple[int, str, BreakDot]] = []
    
    def apply_dot(
        self,
        enemy: Character,
        caster: Character,
        dot_type: str,
        damage_per_tick: int,
        duration: int = 2,
    ) -> None:
        """
        对敌人应用DOT
        
        Args:
            enemy: 目标敌人
            caster: 施加者（海瑟音）
            dot_type: DOT类型标识
            damage_per_tick: 每次触发的伤害
            duration: 持续回合数
        """
        eid = id(enemy)
        
        if eid not in self._dots:
            self._dots[eid] = {}
        
        existing = self._dots[eid].get(dot_type)
        if existing:
            # 已存在该类型DOT，叠加（最多2层）
            existing.stacks = min(2, existing.stacks + 1)
            existing.turns_remaining = duration
        else:
            # 判断是否为裂伤(Laceration)
            is_laceration = (dot_type == HysilensDotType.WOUND)
            
            # 新建DOT
            new_dot = BreakDot(
                break_type=BreakEffectType.SLASH,  # 统一用SLASH类型
                element=Element.PHYSICAL,
                damage_per_tick=damage_per_tick,
                turns_remaining=duration,
                stacks=1,
                source_name=dot_type,
            )
            
            # 裂伤需要特殊标记和cap
            if is_laceration:
                new_dot.dot_tag = "laceration"
                # laceration_cap = 10% of Hysilens ATK
                new_dot.laceration_cap = int(caster.stat.total_atk() * 0.10)
            
            self._dots[eid][dot_type] = new_dot
            self._active_dots.append((eid, dot_type, new_dot))
    
    def tick_all(self) -> list[tuple[Character, int, str]]:
        """
        触发所有DOT伤害
        
        Returns:
            [(敌人, 伤害, DOT名称), ...]
        """
        results = []
        to_remove = []
        
        for eid, dot_type, dot in self._active_dots[:]:
            # 查找敌人对象
            enemy = self._find_enemy(eid)
            if enemy is None:
                to_remove.append((eid, dot_type))
                continue
            
            # 裂伤(Laceration)：每回合重新计算伤害
            if dot.dot_tag == "laceration":
                dot.turns_remaining -= 1
                current_max_hp = enemy.stat.total_max_hp()
                hp_based_dmg = int(current_max_hp * 0.20)
                actual_dmg = min(hp_based_dmg, dot.laceration_cap)
                actual_dmg *= dot.stacks
                if actual_dmg > 0:
                    enemy.take_damage(actual_dmg)
                    results.append((enemy, actual_dmg, dot.source_name))
                if dot.turns_remaining <= 0:
                    to_remove.append((eid, dot_type))
                continue
            
            dmg = dot.tick()
            if dmg > 0:
                # 实际伤害 = 基础伤害 × 层数
                total_dmg = dmg * dot.stacks
                enemy.take_damage(total_dmg)
                results.append((enemy, total_dmg, dot.source_name))
            
            if dot.turns_remaining <= 0:
                to_remove.append((eid, dot_type))
        
        for eid, dot_type in to_remove:
            self._remove_dot(eid, dot_type)
        
        return results
    
    def _remove_dot(self, eid: int, dot_type: str) -> None:
        """移除DOT"""
        if eid in self._dots and dot_type in self._dots[eid]:
            del self._dots[eid][dot_type]
            if not self._dots[eid]:
                del self._dots[eid]
        self._active_dots = [
            (eid, dt, dot) for eid, dt, dot in self._active_dots
            if not (eid == eid and dt == dot_type)
        ]
    
    def _find_enemy(self, eid: int) -> Character:
        """通过ID查找敌人"""
        for char in self._battle_state.player_team + self._battle_state.enemy_team:
            if id(char) == eid:
                return char
        return None
    
    def get_dot_count(self, enemy: Character) -> int:
        """获取敌人身上的DOT数量"""
        eid = id(enemy)
        if eid not in self._dots:
            return 0
        return len(self._dots[eid])
    
    def has_dot_type(self, enemy: Character, dot_type: str) -> bool:
        """检查敌人是否有特定类型的DOT"""
        eid = id(enemy)
        if eid not in self._dots:
            return False
        return dot_type in self._dots[eid]
    
    def clear(self) -> None:
        """清除所有DOT"""
        self._dots.clear()
        self._active_dots.clear()


# ============================================================
# 天赋DOT应用系统
# ============================================================
class HysilensTalentSystem:
    """
    海瑟音天赋：海妖在欢唱
    
    我方目标攻击时，100%基础概率使被击中目标陷入
    风化/裂伤/灼烧/触电其中1种状态，优先陷入不同状态。
    """
    
    DOT_TYPES = [
        HysilensDotType.WOUND,   # 物理
        HysilensDotType.WIND,    # 风
        HysilensDotType.FIRE,    # 火
        HysilensDotType.THUNDER, # 雷
    ]
    
    def __init__(self, hysilens: Character, battle_state):
        self.hysilens = hysilens
        self.battle_state = battle_state
        self.dot_manager = HysilensDotManager(battle_state)
        self._applied_this_attack: set = set()  # 本次攻击已触发的DOT类型
    
    def on_ally_attack(
        self,
        ally: Character,
        target: Character,
    ) -> list[str]:
        """
        当我方目标攻击时调用此方法
        返回应用的DOT类型列表
        """
        if target is None or not target.is_alive():
            return []
        
        # 检查海瑟音是否存活
        if not self.hysilens.is_alive():
            return []
        
        # 本次攻击重置
        self._applied_this_attack.clear()
        
        # 选择要应用的DOT类型（优先不同类型）
        chosen_type = self._select_dot_type(target)
        if chosen_type is None:
            return []
        
        self._applied_this_attack.add(chosen_type)
        
        # 应用DOT
        damage = self._calculate_dot_damage(target, chosen_type)
        self.dot_manager.apply_dot(
            enemy=target,
            caster=self.hysilens,
            dot_type=chosen_type,
            damage_per_tick=damage,
            duration=2,
        )
        
        return [chosen_type]
    
    def _select_dot_type(self, target: Character) -> str:
        """选择要应用的DOT类型（优先不同类型）"""
        # 获取目标已有的DOT类型
        existing_types = set()
        for dt in self.DOT_TYPES:
            if self.dot_manager.has_dot_type(target, dt):
                existing_types.add(dt)
        
        # 优先选择目标没有的类型
        available = [dt for dt in self.DOT_TYPES if dt not in existing_types]
        
        if not available:
            # 全部已有，随机选1个
            import random
            return random.choice(self.DOT_TYPES)
        
        # 从可用的中随机选择
        import random
        return random.choice(available)
    
    def _calculate_dot_damage(self, target: Character, dot_type: str) -> int:
        """计算DOT每次触发的伤害"""
        hysilens_atk = self.hysilens.stat.total_atk()
        
        if dot_type == HysilensDotType.WOUND:
            # 裂伤：20%敌人Max HP，上限10%海瑟音ATK
            target_max_hp = target.stat.total_max_hp()
            hp_based = int(target_max_hp * 0.20)
            cap = int(hysilens_atk * 0.10)
            return min(hp_based, cap)
        else:
            # 风化/灼烧/触电：10%海瑟音ATK
            return int(hysilens_atk * 0.10)


# ============================================================
# 海瑟音技能工厂函数
# ============================================================

def create_hysilens_basic_skill() -> Skill:
    """普攻：小调，止水中回响 - 50% ATK物理伤害"""
    return Skill(
        name="小调，止水中回响",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.PHYSICAL,
        description="对指定敌方单体造成50% ATK物理属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_hysilens_special_skill() -> Skill:
    """战技：泛音，暗流后齐鸣
    - 100%基础概率使敌方全体受到伤害提高10%，持续3回合
    - 对敌方全体造成70% ATK物理伤害
    """
    return Skill(
        name="泛音，暗流后齐鸣",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.70,
        damage_type=Element.PHYSICAL,
        description="使敌方全体受到伤害提高10%持续3回合，对敌方全体造成70% ATK物理伤害",
        energy_gain=30.0,
        break_power=30,
        target_count=-1,  # AOE
        aoe_multiplier=1.0,
    )


def create_hysilens_ult_skill() -> Skill:
    """终结技：绝海回涛，噬魂舞曲
    - 展开结界(3回合)
    - 敌方攻击力-15%，防御力-15%
    - 对敌方全体造成120% ATK物理伤害
    - 结界内敌人受DOT伤害时追加物理DOT
    """
    return Skill(
        name="绝海回涛，噬魂舞曲",
        type=SkillType.ULT,
        multiplier=1.20,
        damage_type=Element.PHYSICAL,
        description="展开结界(3回合)，降低敌方攻击防御各15%，全体120% ATK伤害，DOT触发追加伤害",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,  # AOE
        aoe_multiplier=1.0,
        is_support_skill=False,
    )


def create_hysilens_talent_skill() -> Skill:
    """天赋：海妖在欢唱"""
    return Skill(
        name="海妖在欢唱",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.PHYSICAL,
        description="我方攻击时100%概率使敌人陷入风化/裂伤/灼烧/触电其中1种DOT",
        energy_gain=0.0,
        break_power=0,
        is_follow_up=True,
    )


def create_hysilens_passives() -> list[Passive]:
    """海瑟音的行迹/被动技能"""
    return [
        # A2: 征服的剑旗 - 战斗开始时展开结界(3回合)
        Passive(
            name="征服的剑旗",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="barrier_on_battle_start",
            value=3.0,  # 3回合
            duration=0,
            description="战斗开始时展开与终结技相同的结界，持续3回合",
        ),
        # A4: 盛会的泡沫 - 终结技引爆DOT 150%
        Passive(
            name="盛会的泡沫",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dot_explosion_on_ult",
            value=1.50,  # 150%
            duration=0,
            description="施放终结技时，若敌方处于持续伤害状态，使其DOT立即产生150%伤害",
        ),
        # A6: 珍珠的琴弦 - 效果命中转伤害
        Passive(
            name="珍珠的琴弦",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_hit_to_dmg",
            value=0.15,  # 每10%效果命中+15%伤害
            duration=0,
            description="效果命中>60%时，每超10%使我方伤害+15%，最多90%",
        ),
        # A2: 攻击力+4%
        Passive(
            name="攻击力+4%",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_pct",
            value=0.04,
            duration=0,
            description="攻击力+4%",
        ),
        # A3: 速度+2, 效果命中+4%
        Passive(
            name="速度+2",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_flat",
            value=2.0,
            duration=0,
            description="速度+2",
        ),
        Passive(
            name="效果命中+4%",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_hit_pct",
            value=0.04,
            duration=0,
            description="效果命中+4%",
        ),
        # A4: 速度+3, 攻击力+6%
        Passive(
            name="速度+3",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_flat",
            value=3.0,
            duration=0,
            description="速度+3",
        ),
        Passive(
            name="攻击力+6%",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_pct",
            value=0.06,
            duration=0,
            description="攻击力+6%",
        ),
        # A5: 速度+3, 攻击强化+6%
        Passive(
            name="速度+3",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_flat",
            value=3.0,
            duration=0,
            description="速度+3",
        ),
        Passive(
            name="攻击强化+6%",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_pct",
            value=0.06,
            duration=0,
            description="攻击强化+6%",
        ),
        # A6: 效果命中+6%, 攻击力+8%
        Passive(
            name="效果命中+6%",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_hit_pct",
            value=0.06,
            duration=0,
            description="效果命中+6%",
        ),
        Passive(
            name="攻击力+8%",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_pct",
            value=0.08,
            duration=0,
            description="攻击力+8%",
        ),
    ]


def create_all_hysilens_skills() -> list[Skill]:
    """创建海瑟音所有技能"""
    return [
        create_hysilens_basic_skill(),
        create_hysilens_special_skill(),
        create_hysilens_ult_skill(),
        create_hysilens_talent_skill(),
    ]
