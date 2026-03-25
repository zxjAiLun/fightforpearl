"""游戏核心数据模型"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class Element(Enum):
    """元素类型"""
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


# 元素克制关系：key 克制 value（崩铁循环：物理→风→雷→火→冰→量子→虚数→物理）
# 即：key 攻击 value 时，key 获得 1.2 倍伤害加成
# ELEMENT_COUNTER[key] = {被 key 克制的元素}
ELEMENT_COUNTER = {
    Element.PHYSICAL: {Element.WIND},       # 物理克风
    Element.WIND: {Element.THUNDER},        # 风克雷
    Element.THUNDER: {Element.FIRE},        # 雷克火
    Element.FIRE: {Element.ICE},            # 火克冰
    Element.ICE: {Element.QUANTUM},        # 冰克量子
    Element.QUANTUM: {Element.IMAGINARY},  # 量子克虚数
    Element.IMAGINARY: {Element.PHYSICAL}, # 虚数克物理
}

# 基础属性成长表（每级增加）
BASE_GROWTH = {
    "hp": 100,
    "atk": 10,
    "def": 8,
    "spd": 2,
}


@dataclass
class Stat:
    """角色基础属性"""
    max_hp: int = 100
    atk: int = 50
    def_: int = 30      # def 是 Python 关键字，用 def_
    spd: int = 100
    crit_rate: float = 0.05   # 0-1
    crit_dmg: float = 0.50    # 0-3（150%）
    effect_hit: float = 0.00  # 效果命中
    effect_res: float = 0.00  # 效果抵抗

    def total_value(self) -> int:
        return self.max_hp + self.atk + self.def_ + self.spd

    def clone(self) -> Stat:
        return Stat(
            max_hp=self.max_hp,
            atk=self.atk,
            def_=self.def_,
            spd=self.spd,
            crit_rate=self.crit_rate,
            crit_dmg=self.crit_dmg,
            effect_hit=self.effect_hit,
            effect_res=self.effect_res,
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
    skills: list = field(default_factory=list)
    effects: list = field(default_factory=list)  # 当前 BUFF/DEBUFF

    def is_alive(self) -> bool:
        return self.current_hp > 0

    def is_energy_full(self) -> bool:
        return self.current_energy >= 3.0

    def heal(self, amount: int) -> None:
        self.current_hp = min(self.stat.max_hp, self.current_hp + amount)

    def take_damage(self, amount: int) -> None:
        self.current_hp = max(0, self.current_hp - amount)

    def add_effect(self, effect) -> None:
        self.effects.append(effect)

    def remove_expired_effects(self) -> None:
        self.effects = [e for e in self.effects if e.turns_remaining > 0]


@dataclass
class Skill:
    """技能"""
    name: str
    type: SkillType
    cost: float = 0.0          # 能量消耗
    multiplier: float = 1.0     # ATK 倍率
    damage_type: Element = Element.PHYSICAL
    description: str = ""
    effects: list = field(default_factory=list)  # 附加效果

    def __str__(self) -> str:
        return f"{self.name}[{self.type.name}]"


@dataclass
class Effect:
    """BUFF/DEBUFF 效果"""
    name: str
    turns_remaining: int = 0
    stat_bonus: Optional[Stat] = None  # 属性加成
    damage_increase: float = 0.0       # 增伤倍率
    damage_reduction: float = 0.0      # 减伤
    heal_on_hit: float = 0.0           # 受到伤害时回复


@dataclass
class BattleState:
    """战斗状态"""
    player_team: list[Character]
    enemy_team: list[Character]
    turn: int = 1
    current_turn_index: int = 0  # 当前行动角色索引

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
