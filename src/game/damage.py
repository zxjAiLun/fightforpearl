"""伤害计算模块 — 崩坏星穹铁道风格"""
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Optional

from .models import Character, Element, ELEMENT_COUNTER, Effect


@dataclass
class DamageResult:
    """伤害计算结果"""
    final_damage: int              # 最终伤害
    is_crit: bool                  # 是否暴击
    base_damage: float             # 基础伤害
    crit_multiplier: float        # 暴击倍率
    def_reduction: float          # 防御减伤系数
    element_multiplier: float     # 元素克制倍率
    damage_increase: float        # 总增伤
    resisted: bool                 # 是否被抵抗


def calculate_def_reduction(defender_def: int, attacker_level: int) -> float:
    """
    防御减伤公式
    DEF_reduction = DEF / (DEF + 200 + 10 × 敌人等级)
    """
    return defender_def / (defender_def + 200 + 10 * attacker_level)


def get_element_multiplier(attacker_element: Element, defender_element: Element) -> float:
    """
    元素克制倍率
    克制造成 1.2 倍伤害，被克制受到 0.8 倍伤害
    """
    countered = ELEMENT_COUNTER.get(attacker_element, set())
    if defender_element in countered:
        return 1.2  # 攻击方克制防御方
    if attacker_element in ELEMENT_COUNTER.get(defender_element, set()):
        return 0.8  # 攻击方被克制
    return 1.0


def calculate_damage(
    attacker: Character,
    defender: Character,
    skill_multiplier: float,
    base_damage_add: float = 0,
    damage_type: Optional[Element] = None,
    ignore_def: float = 0.0,
    fixed_damage: int = 0,
) -> DamageResult:
    """
    伤害计算主公式

    伤害 = ATK × 技能倍率 × (1 - DEF_reduction) × (1 + 增伤) × (1 + 易伤)
           × 属性克制 × (暴击?: CRIT_DMG : 1) × (1 + 伤害加成)
    """
    element = damage_type or attacker.element

    # 1. 基础伤害 = ATK × 技能倍率 + 固定伤害
    atk = attacker.stat.atk
    base_damage = atk * skill_multiplier + base_damage_add

    # 2. 防御减伤
    effective_def = defender.stat.def_ * (1 - ignore_def)
    def_reduction = calculate_def_reduction(int(effective_def), attacker.level)
    after_def = base_damage * (1 - def_reduction)

    # 3. 元素克制
    element_mult = get_element_multiplier(element, defender.element)

    # 4. 增伤（来自 BUFF/装备）
    total_damage_increase = 0.0
    total_damage_reduction = 0.0
    total_vulnerability = 0.0  # 易伤（受到的伤害增加）

    for effect in defender.effects:
        if effect.damage_increase > 0:
            total_damage_increase += effect.damage_increase
        if effect.damage_reduction > 0:
            total_damage_reduction += effect.damage_reduction
        if hasattr(effect, 'vulnerability') and effect.vulnerability:
            total_vulnerability += effect.vulnerability

    for effect in attacker.effects:
        if effect.damage_increase > 0:
            total_damage_increase += effect.damage_increase

    # 5. 暴击判定
    crit_roll = random.random() * 100  # 0-100
    is_crit = crit_roll < (attacker.stat.crit_rate * 100)
    crit_mult = attacker.stat.crit_dmg if is_crit else 1.0

    # 6. 最终伤害 = 基础 × 各项系数
    final_mult = (
        (1 + total_damage_increase)
        * (1 - total_damage_reduction)
        * (1 + total_vulnerability)
        * element_mult
        * crit_mult
    )

    final_damage = int(after_def * final_mult) + fixed_damage
    final_damage = max(1, final_damage)  # 最低保底 1 点伤害

    return DamageResult(
        final_damage=final_damage,
        is_crit=is_crit,
        base_damage=round(base_damage, 2),
        crit_multiplier=crit_mult,
        def_reduction=round(def_reduction, 4),
        element_multiplier=element_mult,
        damage_increase=round(total_damage_increase, 4),
        resisted=False,
    )


def apply_damage(attacker: Character, defender: Character, result: DamageResult) -> int:
    """将伤害结果应用到目标，返回实际伤害"""
    defender.take_damage(result.final_damage)

    # 受到伤害时触发的回复效果
    for effect in defender.effects:
        if effect.heal_on_hit > 0:
            heal_amount = int(result.final_damage * effect.heal_on_hit)
            defender.heal(heal_amount)

    return result.final_damage
