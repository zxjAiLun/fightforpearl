"""游戏核心数据模型"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


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
    FALLING_PASSIVE = auto() # 陷入（倒下触发）
    ABILITY_PASSIVE = auto() # 能力（被动）


class BreakEffectType(Enum):
    """弱点击破效果类型"""
    NONE = auto()           # 无击破效果（普通）
    SLASH = auto()          # 裂伤（物理）：持续伤害
    BURN = auto()           # 灼烧（火）：持续伤害
    FREEZE = auto()         # 冻结（冰）：无法行动 + 冰属性附加伤害
    SHOCK = auto()          # 触电（雷）：持续伤害
    SHEAR = auto()          # 风化（风）：持续伤害，可叠加
    ENTANGLE = auto()       # 纠缠（量子）：行动延后 + 附加伤害
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

# 基础属性成长表（每级增加）- 暂时不用（无养成线）
BASE_GROWTH = {
    "hp": 100,
    "atk": 10,
    "def": 8,
    "spd": 2,
}


@dataclass
class Stat:
    """
    角色基础属性（含百分比加成）

    崩铁/原神属性分为两类：
    - 基础值（base）：如 base_atk = 100
    - 百分比加成（percent）：如 atk_pct = 0.3（+30% ATK）

    最终攻击力 = (base_atk) × (1 + atk_pct) + flat_bonus
    最终伤害同理分区域加成
    """
    # --- 基础值 ---
    base_max_hp: int = 100
    base_atk: int = 50
    base_def: int = 30
    base_spd: int = 100

    # --- 百分比加成（来自遗器/光锥/被动等） ---
    hp_pct: float = 0.0      # 生命值百分比加成（+30% → 0.3）
    atk_pct: float = 0.0     # 攻击力百分比加成
    def_pct: float = 0.0     # 防御力百分比加成
    spd_pct: float = 0.0     # 速度百分比加成

    # --- 固定值加成 ---
    hp_flat: int = 0         # 生命值固定加成
    atk_flat: int = 0        # 攻击力固定加成
    def_flat: int = 0        # 防御力固定加成

    # --- 暴击/效果命中/抵抗 ---
    crit_rate: float = 0.05   # 暴击率 0-1
    crit_dmg: float = 0.50   # 暴击伤害倍率 0-3
    effect_hit: float = 0.00  # 效果命中
    effect_res: float = 0.00  # 效果抵抗

    # --- 伤害加成区（各类增伤相加） ---
    dmg_pct: float = 0.0     # 伤害加成百分比（所有属性伤害加成相加）

    # --- 削韧能力 ---
    break_efficiency: float = 1.0  # 击破特攻（影响break伤害）

    def total_max_hp(self) -> int:
        """最终生命值 = (基础 + 固定) × (1 + 百分比)"""
        return int((self.base_max_hp + self.hp_flat) * (1 + self.hp_pct))

    def total_atk(self) -> int:
        """最终攻击力 = (基础 + 固定) × (1 + 百分比)"""
        return int((self.base_atk + self.atk_flat) * (1 + self.atk_pct))

    def total_def(self) -> int:
        """最终防御力 = (基础 + 固定) × (1 + 百分比)"""
        return int((self.base_def + self.def_flat) * (1 + self.def_pct))

    def total_spd(self) -> int:
        """最终速度 = 基础 × (1 + 百分比)"""
        return int(self.base_spd * (1 + self.spd_pct))

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
        )


@dataclass
class Character:
    """游戏角色"""
    name: str
    level: int = 1
    element: Element = Element.PHYSICAL
    stat: Stat = field(default_factory=Stat)
    current_hp: int = 100
    current_energy: float = 0.0
    skills: list = field(default_factory=list)      # 主动技能
    passives: list = field(default_factory=list)    # 被动技能（释放后触发）
    effects: list = field(default_factory=list)      # 当前 BUFF/DEBUFF
    passives_triggered_this_turn: list = field(default_factory=list)  # 本回合已触发的被动

    def is_alive(self) -> bool:
        return self.current_hp > 0

    def is_energy_full(self) -> bool:
        return self.current_energy >= 3.0

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


@dataclass
class Skill:
    """主动技能"""
    name: str
    type: SkillType
    cost: float = 0.0          # 能量消耗
    multiplier: float = 1.0     # ATK 倍率
    damage_type: Element = Element.PHYSICAL
    description: str = ""
    break_type: BreakEffectType = BreakEffectType.NONE  # 击破效果类型

    def __str__(self) -> str:
        return f"{self.name}[{self.type.name}]"


@dataclass
class Passive:
    """被动技能"""
    name: str
    trigger: SkillType           # 触发条件：释放哪类技能时触发
    effect_type: str             # "dmg_increase" | "atk_increase"
    value: float                # 效果值（如 0.3 = +30%）
    duration: int                # 持续回合数
    description: str = ""

    def __str__(self) -> str:
        return f"{self.name}[{self.trigger.name}]"


@dataclass
class Effect:
    """BUFF/DEBUFF 效果"""
    name: str
    turns_remaining: int = 0
    # 属性加成（叠加到 Stat 上，使用时直接修改角色属性）
    atk_pct_bonus: float = 0.0    # 攻击力百分比加成
    dmg_pct_bonus: float = 0.0     # 伤害加成百分比
    crit_rate_bonus: float = 0.0   # 暴击率加成
    crit_dmg_bonus: float = 0.0    # 暴击伤害加成
    spd_pct_bonus: float = 0.0    # 速度百分比加成
    # 特殊效果
    heal_on_hit: float = 0.0      # 受到伤害时回复
    flat_damage: int = 0          # 固定附加伤害
    vuln_pct: float = 0.0         # 易伤（受到伤害+%，与其他易伤相加）

    def apply_to(self, char: Character) -> None:
        """将效果应用到角色属性"""
        char.stat.atk_pct += self.atk_pct_bonus
        char.stat.dmg_pct += self.dmg_pct_bonus
        char.stat.crit_rate += self.crit_rate_bonus
        char.stat.crit_dmg += self.crit_dmg_bonus
        char.stat.spd_pct += self.spd_pct_bonus

    def remove_from(self, char: Character) -> None:
        """从角色属性移除效果"""
        char.stat.atk_pct -= self.atk_pct_bonus
        char.stat.dmg_pct -= self.dmg_pct_bonus
        char.stat.crit_rate -= self.crit_rate_bonus
        char.stat.crit_dmg -= self.crit_dmg_bonus
        char.stat.spd_pct -= self.spd_pct_bonus


@dataclass
class BreakDotEffect:
    """弱点击破持续伤害效果"""
    name: str
    element: Element
    break_type: BreakEffectType
    damage_per_tick: int          # 每回合固定伤害
    turns_remaining: int = 2     # 默认持续2回合
    stacks: int = 1              # 叠加层数（风化用）

    def tick(self) -> int:
        """执行一次伤害，返回伤害值"""
        self.turns_remaining -= 1
        return self.damage_per_tick * self.stacks


@dataclass
class BattleState:
    """战斗状态"""
    player_team: list[Character]
    enemy_team: list[Character]
    turn: int = 1
    current_turn_index: int = 0
    break_effects: list[BreakDotEffect] = field(default_factory=list)  # 场上击破效果

    def get_current_character(self) -> Optional[Character]:
        alive = [c for c in self.player_team + self.enemy_team if c.is_alive()]
        if self.current_turn_index < len(alive):
            return alive[self.current_turn_index]
        return None

    def advance_turn(self) -> None:
        self.current_turn_index = 0
        self.turn += 1

    def is_battle_over(self) -> tuple[bool, str]:
        """返回 (是否结束, 胜利方)"""
        if all(not c.is_alive() for c in self.enemy_team):
            return True, "player"
        if all(not c.is_alive() for c in self.player_team):
            return True, "enemy"
        return False, ""

    def tick_break_effects(self) -> list[tuple[Character, int]]:
        """处理击破持续伤害，返回 [(角色, 伤害)]"""
        results = []
        for dot in self.break_effects[:]:
            for char in self.player_team + self.enemy_team:
                if char.element == dot.element and char.is_alive():
                    dmg = dot.tick()
                    char.take_damage(dmg)
                    results.append((char, dmg))
            self.break_effects = [d for d in self.break_effects if d.turns_remaining > 0]
        return results
