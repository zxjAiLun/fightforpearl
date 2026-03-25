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


@dataclass
class Stat:
    """角色基础属性（含百分比加成）"""
    # --- 基础值 ---
    base_max_hp: int = 100
    base_atk: int = 50
    base_def: int = 30
    base_spd: int = 100

    # --- 百分比加成 ---
    hp_pct: float = 0.0
    atk_pct: float = 0.0
    def_pct: float = 0.0
    spd_pct: float = 0.0

    # --- 固定值加成 ---
    hp_flat: int = 0
    atk_flat: int = 0
    def_flat: int = 0

    # --- 暴击/抵抗 ---
    crit_rate: float = 0.05
    crit_dmg: float = 0.50
    effect_hit: float = 0.00
    effect_res: float = 0.00

    # --- 伤害加成区 ---
    dmg_pct: float = 0.0

    # --- 削韧 ---
    break_efficiency: float = 1.0

    def total_max_hp(self) -> int:
        return int((self.base_max_hp + self.hp_flat) * (1 + self.hp_pct))

    def total_atk(self) -> int:
        return int((self.base_atk + self.atk_flat) * (1 + self.atk_pct))

    def total_def(self) -> int:
        return int((self.base_def + self.def_flat) * (1 + self.def_pct))

    def total_spd(self) -> int:
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
    skills: list = field(default_factory=list)
    passives: list = field(default_factory=list)
    effects: list = field(default_factory=list)
    passives_triggered_this_turn: list = field(default_factory=list)

    # --- 敌人特有 ---
    is_enemy: bool = False
    weakness_elements: list = field(default_factory=list)  # 弱点元素（可破韧）
    toughness: float = 100.0  # 韧性值（削到0触发击破）

    # --- 状态异常 ---
    frozen_turns: int = 0           # 冻结回合数 >0 则无法行动
    action_delay: float = 0.0       # 行动延后值（行动时清零）
    entangle_hit_stacks: int = 0    # 纠缠受击增伤层数（受击时+1，上限5）

    def is_alive(self) -> bool:
        return self.current_hp > 0

    def can_act(self) -> bool:
        """是否可行动（被冻结则不可）"""
        return self.is_alive() and self.frozen_turns <= 0

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
        # 冻结回合递减
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

    # 击破状态（key=角色，value=击破状态）
    break_statuses: dict[int, BreakStatus] = field(default_factory=dict)

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

        # 计算击破触发伤害
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
