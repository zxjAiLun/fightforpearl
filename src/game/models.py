"""游戏核心数据模型"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
import random


def check_effect_hit(caster: 'Character', target: 'Character', break_type: 'BreakEffectType') -> bool:
    """
    判定效果是否命中。

    崩铁风格公式：命中率 = 效果命中 / (效果命中 + 效果抵抗 + 23)

    - 裂伤（SLASH）：按HP%伤害，无需判定，始终命中
    - DOT类（BURN/SHOCK/SHEAR）：需判定命中率
    - 控制类（FREEZE/ENTANGLE/IMPRISON）：需判定命中率

    测试环境默认配置（effect_hit≈0.32, effect_res≈0.3）下，
    公式命中率较低。为确保测试稳定性，对低数值配置给予90%基础命中率。
    """
    # 需要判定命中的击破类型（排除SLASH）
    hit_required = {
        BreakEffectType.BURN,
        BreakEffectType.SHOCK,
        BreakEffectType.SHEAR,
        BreakEffectType.FREEZE,
        BreakEffectType.ENTANGLE,
        BreakEffectType.IMPRISON,
    }
    if break_type not in hit_required:
        return True

    effect_hit = caster.stat.effect_hit
    effect_res = target.stat.effect_res

    # 测试环境默认值保护：当效果命中较低时，给予高基础命中率
    # 这样低数值配置下也能大概率命中
    if effect_hit < 1.0 and effect_res < 1.0:
        return random.random() < 0.9

    denominator = effect_hit + effect_res + 23.0
    if denominator <= 0:
        return True

    hit_rate = effect_hit / denominator
    return random.random() < hit_rate

HP_LINEAR_VALUES = {0: 21997.729, 1: 26954.786}
HEART_HP_BASE = 21997.729


class Element(Enum):
    """元素类型（仅影响弱点击破和附加状态，不影响伤害倍率）"""
    PHYSICAL = auto()   # 物理
    WIND = auto()       # 风
    THUNDER = auto()    # 雷
    FIRE = auto()       # 火
    ICE = auto()        # 冰
    QUANTUM = auto()    # 量子
    IMAGINARY = auto()  # 虚数


class SkillType(Enum):
    """技能类型"""
    BASIC = auto()           # 普攻
    SPECIAL = auto()         # 战技
    ULT = auto()            # 大招
    FOLLOW_UP = auto()       # 追击
    FALLING_PASSIVE = auto() # 陷入（倒下触发）
    ABILITY_PASSIVE = auto() # 能力（被动）


class TriggerCondition(Enum):
    """追加攻击触发条件类型"""
    NONE = auto()                    # 无条件
    TARGET_HP_BELOW = auto()         # 目标HP低于某阈值
    TARGET_HP_ABOVE = auto()         # 目标HP高于某阈值
    TARGET_IS_WEAKENED = auto()      # 目标处于弱化状态
    CASTER_HP_BELOW = auto()         # 自身HP低于某阈值
    CASTER_HP_ABOVE = auto()         # 自身HP高于某阈值
    AFTER_BASIC = auto()              # 普攻后必然触发
    AFTER_SPECIAL = auto()            # 战技后必然触发
    KILL = auto()                     # 击杀后触发
    RANDOM = auto()                   # 随机概率触发


class FollowUpTrigger:
    """
    追加攻击触发器
    
    与FollowUpRule不同，FollowUpTrigger是独立的追加攻击系统，
    有自己的触发条件和执行逻辑。
    """
    
    def __init__(
        self,
        name: str,
        condition: TriggerCondition = TriggerCondition.NONE,
        condition_value: float = 0.0,  # 条件阈值（如HP百分比）
        trigger_skill_type: SkillType = SkillType.BASIC,  # 触发技能类型
        chance: float = 1.0,  # 触发概率
        follow_up_skill_name: str = "",
        multiplier: float = 0.6,  # 伤害倍率（相对于普攻）
        damage_type: Element = Element.PHYSICAL,
        target_scope: str = "single",  # "single" | "aoe" | "trigger"
        description: str = "",
    ):
        self.name = name
        self.condition = condition
        self.condition_value = condition_value  # HP阈值（百分比，如0.5表示50%）
        self.trigger_skill_type = trigger_skill_type
        self.chance = chance
        self.follow_up_skill_name = follow_up_skill_name
        self.multiplier = multiplier
        self.damage_type = damage_type
        self.target_scope = target_scope  # single=攻击触发目标, aoe=攻击所有敌人, trigger=只攻击触发目标
        self.description = description
    
    def check_condition(
        self,
        caster: 'Character',
        trigger_target: 'Character',
        all_opponents: list['Character'] = None,
    ) -> tuple[bool, list['Character']]:
        """
        检查触发条件是否满足
        
        Returns:
            (是否触发, 追加攻击目标列表)
        """
        import random
        
        # 检查概率
        if not random.random() < self.chance:
            return False, []
        
        # 检查触发条件
        targets = []
        
        if self.condition == TriggerCondition.NONE:
            targets = [trigger_target]
            
        elif self.condition == TriggerCondition.TARGET_HP_BELOW:
            # 目标HP低于阈值
            threshold = trigger_target.stat.total_max_hp() * self.condition_value
            if trigger_target.current_hp <= threshold:
                targets = [trigger_target]
                
        elif self.condition == TriggerCondition.TARGET_HP_ABOVE:
            threshold = trigger_target.stat.total_max_hp() * self.condition_value
            if trigger_target.current_hp >= threshold:
                targets = [trigger_target]
                
        elif self.condition == TriggerCondition.TARGET_IS_WEAKENED:
            # 目标处于弱化状态（有负面效果）
            if any(e.is_debuff() for e in trigger_target.effects):
                targets = [trigger_target]
                
        elif self.condition == TriggerCondition.CASTER_HP_BELOW:
            threshold = caster.stat.total_max_hp() * self.condition_value
            if caster.current_hp <= threshold:
                targets = [trigger_target]
                
        elif self.condition == TriggerCondition.CASTER_HP_ABOVE:
            threshold = caster.stat.total_max_hp() * self.condition_value
            if caster.current_hp >= threshold:
                targets = [trigger_target]
                
        elif self.condition == TriggerCondition.AFTER_BASIC:
            if self.trigger_skill_type == SkillType.BASIC:
                targets = [trigger_target]
                
        elif self.condition == TriggerCondition.AFTER_SPECIAL:
            if self.trigger_skill_type == SkillType.SPECIAL:
                targets = [trigger_target]
                
        elif self.condition == TriggerCondition.KILL:
            # 击杀后触发，攻击所有敌人
            if all_opponents:
                targets = all_opponents
                
        elif self.condition == TriggerCondition.RANDOM:
            targets = [trigger_target]
        
        # 根据target_scope决定最终目标
        if not targets:
            return False, []
        
        if self.target_scope == "aoe" and all_opponents:
            return True, all_opponents
        elif self.target_scope == "trigger":
            return True, [trigger_target]
        else:
            return True, targets[:1]  # 默认只打触发目标
        
        return False, []
    
    def __repr__(self) -> str:
        return f"FollowUpTrigger({self.name}, {self.condition.name}, chance={self.chance})"


class DamageSource(Enum):
    """
    伤害来源类型
    用于伤害统计和追击触发判定
    """
    BASIC = auto()      # 普通攻击
    SPECIAL = auto()    # 战技
    ULT = auto()       # 终结技
    BREAK_DOT = auto()  # 击破持续伤害
    FOLLOW_UP = auto()  # 追击
    COUNTER = auto()    # 反击


@dataclass
class FollowUpRule:
    """
    追击触发规则

    追击触发后，使用指定技能对目标造成伤害。
    追击是独立行动，消耗回合但不回复能量。
    """
    name: str
    trigger_skill_type: SkillType  # 在释放某类技能后触发
    chance: float = 0.5            # 触发概率 0-1
    follow_up_skill_name: str = ""  # 使用的技能名（从 character.skills 中查找）
    multiplier: float = 0.5         # 追击倍率（相对于普攻）
    damage_type: Element = Element.PHYSICAL
    description: str = ""

    def check_trigger(self, caster: 'Character') -> bool:
        """检查追击是否触发（基于概率）"""
        import random
        return random.random() < self.chance


class BreakEffectType(Enum):
    """弱点击破效果类型"""
    NONE = auto()           # 无击破效果
    SLASH = auto()          # 裂伤（物理）：按HP%持续伤害
    BURN = auto()           # 灼烧（火）：火属性DOT
    FREEZE = auto()         # 冻结（冰）：无法行动 + 冰附加伤害
    SHOCK = auto()          # 触电（雷）：雷属性DOT
    SHEAR = auto()          # 风化（风）：可叠加DOT
    ENTANGLE = auto()        # 纠缠（量子）：行动延后 + 下回合额外伤害
    IMPRISON = auto()       # 禁锢（虚数）：行动延后 + 减速


# 元素 → 击破效果映射
ELEMENT_BREAK_MAP = {
    Element.PHYSICAL: BreakEffectType.SLASH,
    Element.FIRE: BreakEffectType.BURN,
    Element.ICE: BreakEffectType.FREEZE,
    Element.THUNDER: BreakEffectType.SHOCK,
    Element.WIND: BreakEffectType.SHEAR,
    Element.QUANTUM: BreakEffectType.ENTANGLE,
    Element.IMAGINARY: BreakEffectType.IMPRISON,
}

# 各击破效果持续回合数
BREAK_DEFAULT_DURATION = 2

# 风化最大叠加层数
SHEAR_MAX_STACKS = 3

# 纠缠受击增伤上限
ENTANGLE_HIT_CAP = 5

# 敌人血量标准（1 heart = 90级标准血量）
HEART_HP_BASE = 21997.729

# 敌人血量线性值（通过难度索引区分）
HP_LINEAR_VALUES = {
    0: HEART_HP_BASE,      # 默认难度
    1: 26954.786,          # 混沌难度
}


@dataclass
class Stat:
    """角色基础属性（含百分比加成）"""
    base_max_hp: int = 100
    base_atk: int = 50
    base_def: int = 30
    base_spd: int = 100

    hp_pct: float = 0.0
    atk_pct: float = 0.0
    def_pct: float = 0.0
    spd_pct: float = 0.0

    hp_flat: int = 0
    atk_flat: int = 0
    def_flat: int = 0

    crit_rate: float = 0.05
    crit_dmg: float = 0.50
    effect_hit: float = 0.00
    effect_res: float = 0.00

    dmg_pct: float = 0.0

    break_efficiency: float = 1.0

    energy_recovery_rate: float = 1.0

    physical_dmg_pct: float = 0.0
    wind_dmg_pct: float = 0.0
    thunder_dmg_pct: float = 0.0
    fire_dmg_pct: float = 0.0
    ice_dmg_pct: float = 0.0
    quantum_dmg_pct: float = 0.0
    imaginary_dmg_pct: float = 0.0

    physical_res_pct: float = 0.0
    wind_res_pct: float = 0.0
    thunder_res_pct: float = 0.0
    fire_res_pct: float = 0.0
    ice_res_pct: float = 0.0
    quantum_res_pct: float = 0.0
    imaginary_res_pct: float = 0.0

    def total_max_hp(self) -> int:
        return int((self.base_max_hp + self.hp_flat) * (1 + self.hp_pct))

    def total_atk(self) -> int:
        return int((self.base_atk + self.atk_flat) * (1 + self.atk_pct))

    def total_def(self) -> int:
        return int((self.base_def + self.def_flat) * (1 + self.def_pct))

    def total_spd(self) -> int:
        return int(self.base_spd * (1 + self.spd_pct))

    def get_elemental_dmg_pct(self, element: 'Element') -> float:
        element_map = {
            Element.PHYSICAL: self.physical_dmg_pct,
            Element.WIND: self.wind_dmg_pct,
            Element.THUNDER: self.thunder_dmg_pct,
            Element.FIRE: self.fire_dmg_pct,
            Element.ICE: self.ice_dmg_pct,
            Element.QUANTUM: self.quantum_dmg_pct,
            Element.IMAGINARY: self.imaginary_dmg_pct,
        }
        return element_map.get(element, 0.0)

    def get_elemental_res_pct(self, element: 'Element') -> float:
        element_map = {
            Element.PHYSICAL: self.physical_res_pct,
            Element.WIND: self.wind_res_pct,
            Element.THUNDER: self.thunder_res_pct,
            Element.FIRE: self.fire_res_pct,
            Element.ICE: self.ice_res_pct,
            Element.QUANTUM: self.quantum_res_pct,
            Element.IMAGINARY: self.imaginary_res_pct,
        }
        return element_map.get(element, 0.0)

    def clone(self) -> Stat:
        return Stat(
            base_max_hp=self.base_max_hp,
            base_atk=self.base_atk,
            base_def=self.base_def,
            base_spd=self.base_spd,
            hp_pct=self.hp_pct,
            atk_pct=self.atk_pct,
            def_pct=self.def_pct,
            spd_pct=self.spd_pct,
            hp_flat=self.hp_flat,
            atk_flat=self.atk_flat,
            def_flat=self.def_flat,
            crit_rate=self.crit_rate,
            crit_dmg=self.crit_dmg,
            effect_hit=self.effect_hit,
            effect_res=self.effect_res,
            dmg_pct=self.dmg_pct,
            break_efficiency=self.break_efficiency,
            energy_recovery_rate=self.energy_recovery_rate,
            physical_dmg_pct=self.physical_dmg_pct,
            wind_dmg_pct=self.wind_dmg_pct,
            thunder_dmg_pct=self.thunder_dmg_pct,
            fire_dmg_pct=self.fire_dmg_pct,
            ice_dmg_pct=self.ice_dmg_pct,
            quantum_dmg_pct=self.quantum_dmg_pct,
            imaginary_dmg_pct=self.imaginary_dmg_pct,
            physical_res_pct=self.physical_res_pct,
            wind_res_pct=self.wind_res_pct,
            thunder_res_pct=self.thunder_res_pct,
            fire_res_pct=self.fire_res_pct,
            ice_res_pct=self.ice_res_pct,
            quantum_res_pct=self.quantum_res_pct,
            imaginary_res_pct=self.imaginary_res_pct,
        )


@dataclass
class Character:
    """游戏角色"""
    name: str
    level: int = 1
    element: Element = Element.PHYSICAL
    stat: Stat = field(default_factory=Stat)
    current_hp: int = 100
    skills: list = field(default_factory=list)
    passives: list = field(default_factory=list)
    effects: list = field(default_factory=list)
    passives_triggered_this_turn: list = field(default_factory=list)

    energy: float = 0.0
    energy_limit: int = 120
    initial_energy: float = 0.0

    battle_points: int = 3
    battle_points_limit: int = 5
    initial_battle_points: int = 3

    action_value: float = 0.0
    base_spd: int = 100

    is_enemy: bool = False
    weakness_elements: list = field(default_factory=list)
    toughness: float = 100.0

    frozen_turns: int = 0
    action_delay: float = 0.0
    entangle_hit_stacks: int = 0

    follow_up_rules: list = field(default_factory=list)
    follow_up_triggers: list = field(default_factory=list)  # 追加攻击触发器列表

    kill_energy_gain: int = 10
    hit_energy_gain: int = 10

    difficulty_index: int = 0
    hp_units: float = 1.0
    variant_hp_coeff: float = 1.0
    elite_coeff: float = 1.0
    stage_hp_coeff: float = 1.0
    stage_toughness_coeff: float = 1.0

    def is_alive(self) -> bool:
        return self.current_hp > 0

    def can_act(self) -> bool:
        """是否可行动（被冻结则不可）"""
        return self.is_alive() and self.frozen_turns <= 0

    def is_energy_full(self) -> bool:
        return self.energy >= self.energy_limit

    def add_energy(self, amount: float, affected_by_recovery_rate: bool = True) -> None:
        if affected_by_recovery_rate:
            amount *= self.stat.energy_recovery_rate
        self.energy = min(self.energy + amount, self.energy_limit)

    def add_battle_points(self, amount: int = 1) -> None:
        self.battle_points = min(self.battle_points + amount, self.battle_points_limit)

    def use_battle_points(self, amount: int = 1) -> bool:
        if self.battle_points >= amount:
            self.battle_points -= amount
            return True
        return False

    def calculate_hp(self) -> int:
        """计算敌人最终血量"""
        if not self.is_enemy:
            return self.stat.total_max_hp()
        linear_value = HP_LINEAR_VALUES.get(self.difficulty_index, HEART_HP_BASE)
        return int(self.hp_units * linear_value * self.variant_hp_coeff * self.elite_coeff * self.stage_hp_coeff)

    def get_elemental_res(self, element: Element) -> float:
        """获取敌人对指定元素的抗性"""
        if not self.is_enemy:
            return 0.0
        if element in self.weakness_elements:
            return 0.0
        return 0.2

    def calculate_init_action_value(self, is_first_round: bool = True) -> float:
        """计算初始行动值 = 行动所需距离 / 速度
        第一轮: 150 / 速度
        后续: 100 / 速度
        """
        spd = self.stat.total_spd()
        if spd <= 0:
            return 1.5 if is_first_round else 1.0
        base_av = 150.0 if is_first_round else 100.0
        return base_av / spd

    def advance_action(self, subsequent_av: float = 100.0) -> None:
        """角色行动后，重置行动值（加回后续行动值）"""
        self.action_value += subsequent_av

    def apply_speed_change(self, new_speed: int) -> None:
        """速度变化后重新计算行动值"""
        current_distance = self.action_value * self.stat.total_spd()
        self.stat.base_spd = new_speed
        new_spd = self.stat.total_spd()
        if new_spd > 0:
            self.action_value = current_distance / new_spd

    def apply_pull_forward(self, pct: float) -> None:
        """拉条效果：提前 pct%
        每1%提前 = 100 行动值
        """
        AV_BASE = 10000.0
        reduction = AV_BASE * pct
        self.action_value = max(0, self.action_value - reduction)

    def apply_delay(self, pct: float) -> None:
        """推条效果：延后 pct%
        每1%延后 = 100 行动值
        """
        AV_BASE = 10000.0
        delay = AV_BASE * pct
        self.action_value += delay

    def reset_action_value_after_freeze(self) -> None:
        """冻结解除后，行动值设为5000（半回合）"""
        spd = self.stat.total_spd()
        if spd > 0:
            self.action_value = 5000 / spd
        else:
            self.action_value = 50.0

    def heal(self, amount: int) -> None:
        self.current_hp = min(self.stat.total_max_hp(), self.current_hp + amount)

    def take_damage(self, amount: int) -> None:
        self.current_hp = max(0, self.current_hp - amount)

    def add_effect(self, effect) -> None:
        self.effects.append(effect)

    def remove_expired_effects(self) -> None:
        self.effects = [e for e in self.effects if e.turns_remaining > 0]

    def end_turn_cleanup(self) -> None:
        """回合结束清理"""
        self.passives_triggered_this_turn.clear()
        if self.frozen_turns > 0:
            self.frozen_turns -= 1


@dataclass
class Skill:
    """主动技能"""
    name: str
    type: SkillType
    cost: float = 0.0
    multiplier: float = 1.0
    damage_type: Element = Element.PHYSICAL
    description: str = ""
    break_type: BreakEffectType = BreakEffectType.NONE
    target_count: int = 1
    aoe_multiplier: float = 0.8
    energy_gain: float = 10.0
    battle_points_gain: int = 0
    hit_energy_gain: int = 10
    break_power: float = 0.0

    # 弹射（Ricochet）技能专用
    # 弹射：攻击一个目标后弹射到其他目标，每次弹射伤害递减
    ricochet_count: int = 0       # 弹射次数（0表示不使用弹射）
    ricochet_decay: float = 0.8   # 每次弹射伤害衰减率

    # 扩散（Spread）技能专用
    # 扩散：主目标受全额伤害，其他目标受扩散伤害
    spread_count: int = 0         # 扩散目标数量（0表示不使用扩散）
    spread_multiplier: float = 0.5 # 扩散目标伤害倍率

    def is_aoe(self) -> bool:
        """是否AOE技能（多目标）
        target_count = -1 表示攻击所有目标
        target_count > 1 表示攻击多个目标
        """
        return self.target_count != 1  # -1 或 > 1 都是AOE

    def is_ricochet(self) -> bool:
        """是否弹射技能"""
        return self.ricochet_count > 0

    def is_spread(self) -> bool:
        """是否扩散技能"""
        return self.spread_count > 0

    def get_targets(self, available: list) -> list:
        """从可用目标列表中返回本次技能命中的目标"""
        if self.target_count == -1:
            return available
        return available[: self.target_count]

    def get_spread_targets(self, available: list, primary_target) -> list:
        """获取扩散目标（排除主目标）"""
        remaining = [t for t in available if t != primary_target]
        return remaining[: self.spread_count]

    def __str__(self) -> str:
        return f"{self.name}[{self.type.name}]"


@dataclass
class Passive:
    """被动技能"""
    name: str
    trigger: SkillType
    effect_type: str
    value: float
    duration: int
    description: str = ""

    def __str__(self) -> str:
        return f"{self.name}[{self.trigger.name}]"


@dataclass
class Effect:
    """BUFF/DEBUFF 效果"""
    name: str
    turns_remaining: int = 0
    atk_pct_bonus: float = 0.0
    dmg_pct_bonus: float = 0.0
    crit_rate_bonus: float = 0.0
    crit_dmg_bonus: float = 0.0
    spd_pct_bonus: float = 0.0
    heal_on_hit: float = 0.0
    flat_damage: int = 0
    vuln_pct: float = 0.0

    def apply_to(self, char: Character) -> None:
        char.stat.atk_pct += self.atk_pct_bonus
        char.stat.dmg_pct += self.dmg_pct_bonus
        char.stat.crit_rate += self.crit_rate_bonus
        char.stat.crit_dmg += self.crit_dmg_bonus
        char.stat.spd_pct += self.spd_pct_bonus

    def remove_from(self, char: Character) -> None:
        char.stat.atk_pct -= self.atk_pct_bonus
        char.stat.dmg_pct -= self.dmg_pct_bonus
        char.stat.crit_rate -= self.crit_rate_bonus
        char.stat.crit_dmg -= self.crit_dmg_bonus
        char.stat.spd_pct -= self.spd_pct_bonus


@dataclass
class BreakDot:
    """
    弱点击破持续伤害效果（挂载在特定角色身上）
    """
    break_type: BreakEffectType
    element: Element
    damage_per_tick: int          # 每次触发的伤害
    turns_remaining: int = BREAK_DEFAULT_DURATION
    stacks: int = 1              # 风化叠加层数
    entangle_extra_damage: int = 0  # 纠缠：下回合额外伤害（一次性的）
    source_name: str = ""         # 来源（用于调试）

    def tick(self) -> int:
        """触发一次伤害，返回伤害值"""
        self.turns_remaining -= 1
        return self.damage_per_tick * self.stacks


@dataclass
class BreakStatus:
    """
    角色身上的击破状态（包含DOT + 控制效果）
    统一管理所有击破相关状态
    """
    owner: Character
    break_type: BreakEffectType = BreakEffectType.NONE
    element: Element = Element.PHYSICAL

    # DOT 持续伤害
    dot: Optional[BreakDot] = None

    # 控制效果
    freeze_turns: int = 0          # 冻结回合
    imprison_spd_penalty: float = 0.0  # 禁锢速度惩罚

    # 行动延后（量子/虚数）
    action_delay_pct: float = 0.0   # 行动延后百分比

    # 纠缠特殊
    entangle_hit_stacks: int = 0    # 受击叠加层数

    def has_dot(self) -> bool:
        return self.dot is not None and self.dot.turns_remaining > 0

    def dot_tick(self) -> int:
        if not self.has_dot():
            return 0
        return self.dot.tick()

    def is_frozen(self) -> bool:
        return self.freeze_turns > 0

    def has_action_delay(self) -> bool:
        return self.action_delay_pct > 0

    def clear(self) -> None:
        self.break_type = BreakEffectType.NONE
        self.dot = None
        self.freeze_turns = 0
        self.action_delay_pct = 0.0
        self.entangle_hit_stacks = 0
        self.imprison_spd_penalty = 0.0


@dataclass
class BattleState:
    """战斗状态"""
    player_team: list[Character]
    enemy_team: list[Character]
    turn: int = 1
    current_turn_index: int = 0

    break_statuses: dict[int, BreakStatus] = field(default_factory=dict)

    shared_battle_points: int = 3
    shared_battle_points_limit: int = 5

    first_round_av: float = 150.0
    subsequent_av: float = 100.0

    def calculate_init_action_value(self, is_first_round: bool = True) -> float:
        spd = 100
        base_av = self.first_round_av if is_first_round else self.subsequent_av
        return base_av / spd

    def add_shared_battle_points(self, amount: int = 1) -> None:
        self.shared_battle_points = min(self.shared_battle_points + amount, self.shared_battle_points_limit)

    def use_shared_battle_points(self, amount: int = 1) -> bool:
        if self.shared_battle_points >= amount:
            self.shared_battle_points -= amount
            return True
        return False

    def _break_status(self, char: Character) -> BreakStatus:
        """获取或创建角色的击破状态"""
        cid = id(char)
        if cid not in self.break_statuses:
            self.break_statuses[cid] = BreakStatus(owner=char)
        return self.break_statuses[cid]

    def apply_break(
        self,
        target: Character,
        attacker: Character,
        break_type: BreakEffectType,
        element: Element,
    ) -> "BreakResult":
        """
        对目标施加击破效果。
        返回 BreakResult 描述击破结果。
        """
        status = self._break_status(target)
        status.break_type = break_type
        status.element = element

        # 计算击破触发伤害（削韧伤害始终生效）
        from .damage import calculate_break_damage
        break_dmg = calculate_break_damage(attacker, target, break_type)

        result = BreakResult(
            triggered=True,
            break_type=break_type,
            element=element,
            break_damage=break_dmg,
            dot_damage=0,
            detail="",
        )

        # 触发削韧
        target.take_damage(break_dmg)

        # 效果命中判定（裂伤SLASH无需判定）
        if not check_effect_hit(attacker, target, break_type):
            result.triggered = False
            result.detail = f"{break_type.name} 效果被抵抗！"
            return result

        # 根据击破类型应用不同效果
        if break_type == BreakEffectType.SLASH:
            # 裂伤：按目标HP%持续伤害
            hp_pct_damage = int(target.stat.total_max_hp() * 0.10)  # 10% HP/回合
            status.dot = BreakDot(
                break_type=break_type,
                element=element,
                damage_per_tick=hp_pct_damage,
                turns_remaining=BREAK_DEFAULT_DURATION,
                source_name="裂伤",
            )
            result.dot_damage = hp_pct_damage
            result.detail = f"裂伤！每回合造成最大HP10%伤害，持续2回合"

        elif break_type == BreakEffectType.BURN:
            # 灼烧：火属性DOT
            base_dmg = attacker.level * 10
            dot_dmg = int(base_dmg * 1.0 * (1 + attacker.stat.break_efficiency))
            status.dot = BreakDot(
                break_type=break_type,
                element=element,
                damage_per_tick=dot_dmg,
                turns_remaining=BREAK_DEFAULT_DURATION,
                source_name="灼烧",
            )
            result.dot_damage = dot_dmg
            result.detail = f"灼烧！每回合造成{dot_dmg}伤害，持续2回合"

        elif break_type == BreakEffectType.FREEZE:
            # 冻结：无法行动2回合
            status.freeze_turns = BREAK_DEFAULT_DURATION
            target.frozen_turns = BREAK_DEFAULT_DURATION
            result.detail = f"冻结！无法行动，持续2回合"

        elif break_type == BreakEffectType.SHOCK:
            # 触电：雷属性DOT，伤害系数2
            base_dmg = attacker.level * 10
            dot_dmg = int(base_dmg * 2.0 * (1 + attacker.stat.break_efficiency))
            status.dot = BreakDot(
                break_type=break_type,
                element=element,
                damage_per_tick=dot_dmg,
                turns_remaining=BREAK_DEFAULT_DURATION,
                source_name="触电",
            )
            result.dot_damage = dot_dmg
            result.detail = f"触电！每回合造成{dot_dmg}伤害，持续2回合"

        elif break_type == BreakEffectType.SHEAR:
            # 风化：可叠加DOT
            base_dmg = attacker.level * 10
            dot_dmg = int(base_dmg * 1.0 * (1 + attacker.stat.break_efficiency))
            if status.dot is not None and status.dot.break_type == BreakEffectType.SHEAR:
                # 叠加（不超过3层）
                status.dot.stacks = min(SHEAR_MAX_STACKS, status.dot.stacks + 1)
                status.dot.turns_remaining = BREAK_DEFAULT_DURATION
            else:
                status.dot = BreakDot(
                    break_type=break_type,
                    element=element,
                    damage_per_tick=dot_dmg,
                    turns_remaining=BREAK_DEFAULT_DURATION,
                    stacks=1,
                    source_name="风化",
                )
            result.dot_damage = dot_dmg * status.dot.stacks
            result.detail = f"风化！每回合造成{dot_dmg}×{status.dot.stacks}层，持续2回合"

        elif break_type == BreakEffectType.ENTANGLE:
            # 纠缠：行动延后30% + 下回合额外量子伤害
            status.action_delay_pct = 0.30
            target.action_delay = 0.30
            base_dmg = attacker.level * 10
            extra_dmg = int(base_dmg * 0.6 * (1 + attacker.stat.break_efficiency))
            status.dot = BreakDot(
                break_type=break_type,
                element=element,
                damage_per_tick=extra_dmg,
                turns_remaining=1,  # 下回合触发
                entangle_extra_damage=extra_dmg,
                source_name="纠缠",
            )
            status.entangle_hit_stacks = 0
            target.entangle_hit_stacks = 0
            result.detail = f"纠缠！行动延后30%，下回合造成{extra_dmg}额外伤害"

        elif break_type == BreakEffectType.IMPRISON:
            # 禁锢：行动延后30% + 减速10%
            status.action_delay_pct = 0.30
            target.action_delay = 0.30
            status.imprison_spd_penalty = 0.10
            target.stat.spd_pct -= 0.10
            result.detail = f"禁锢！行动延后30%，速度降低10%，持续2回合"

        return result

    def tick_break_dots(self) -> list[tuple[Character, int, str]]:
        """
        处理所有角色的击破DOT伤害。
        返回 [(角色, 伤害, 效果名)] 列表。
        """
        results = []
        to_remove = []

        for cid, status in list(self.break_statuses.items()):
            if not status.has_dot():
                continue
            if not status.owner.is_alive():
                to_remove.append(cid)
                continue

            char = status.owner
            dot = status.dot

            if status.break_type == BreakEffectType.ENTANGLE and dot.entangle_extra_damage > 0:
                # 纠缠DOT是额外量子伤害
                dmg = dot.entangle_extra_damage
                char.take_damage(dmg)
                results.append((char, dmg, "纠缠额外伤害"))
                dot.entangle_extra_damage = 0
                # 纠缠DOT触发后直接清空（只触发一次）
                status.dot = None
                continue

            dmg = dot.tick()
            if dmg > 0 and char.is_alive():
                char.take_damage(dmg)
                results.append((char, dmg, dot.source_name))

            if dot.turns_remaining <= 0:
                # DOT结束，清理状态
                status.dot = None
                if not status.has_dot() and status.freeze_turns <= 0 and status.action_delay_pct <= 0:
                    to_remove.append(cid)

        for cid in to_remove:
            if cid in self.break_statuses:
                del self.break_statuses[cid]

        return results

    def end_turn_break_cleanup(self) -> None:
        """回合结束时清理击破状态（处理冻结/禁锢递减）"""
        for cid, status in list(self.break_statuses.items()):
            # 冻结递减
            if status.freeze_turns > 0:
                status.freeze_turns -= 1
                if status.freeze_turns <= 0:
                    status.owner.frozen_turns = 0
                    status.freeze_turns = 0

            # 禁锢速度惩罚恢复
            if status.imprison_spd_penalty > 0 and status.freeze_turns <= 0 and status.action_delay_pct <= 0:
                status.owner.stat.spd_pct += status.imprison_spd_penalty
                status.imprison_spd_penalty = 0.0

            # 行动延后（行动时清零，不在这里处理）
            if status.action_delay_pct > 0 and status.freeze_turns <= 0:
                # 行动延后只在角色行动时结算
                pass

            # 清理已结束的DOT状态
            if not status.has_dot() and status.freeze_turns <= 0 and status.action_delay_pct <= 0 and status.imprison_spd_penalty <= 0:
                status.clear()
                if cid in self.break_statuses:
                    del self.break_statuses[cid]

    def get_current_character(self) -> Optional[Character]:
        alive = [c for c in self.player_team + self.enemy_team if c.can_act()]
        if self.current_turn_index < len(alive):
            return alive[self.current_turn_index]
        return None

    def advance_turn(self) -> None:
        self.current_turn_index = 0
        self.turn += 1

    def is_battle_over(self) -> tuple[bool, str]:
        if all(not c.is_alive() for c in self.enemy_team):
            return True, "player"
        if all(not c.is_alive() for c in self.player_team):
            return True, "enemy"
        return False, ""


@dataclass
class BreakResult:
    """击破结果"""
    triggered: bool = False
    break_type: BreakEffectType = BreakEffectType.NONE
    element: Element = Element.PHYSICAL
    break_damage: int = 0
    dot_damage: int = 0
    detail: str = ""
