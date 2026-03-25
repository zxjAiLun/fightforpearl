"""伤害计算模块 — 崩坏星穹铁道风格

伤害公式：
FinalDMG = ATK × Multiplier × (1 - DEF_RED) × (1 + DMG%) × CRIT_MULT × BREAK × (1 + VULN)

其中：
- ATK: 角色最终攻击力（基础ATK × (1+百分比) + 固定）
- Multiplier: 技能倍率
- DEF_RED: 防御减伤 = DEF / (DEF + 200 + 10 × Level)
- DMG%: 增伤区（所有伤害加成相加，如 30% + 20% = 50% → 1.5）
- CRIT_MULT: 暴击区（暴击? CRIT_DMG : 1）
- BREAK: 击破伤害（独立乘法区）
- VULN: 易伤区（所有易伤相加，如 10% + 15% = 25% → 1.25）

崩铁没有元素克制！元素只影响弱点击破效果。
"""
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Optional

from .models import Character, Element, Effect, BreakDotEffect


@dataclass
class DamageResult:
    """伤害计算结果"""
    final_damage: int              # 最终伤害
    is_crit: bool                  # 是否暴击
    base_damage: float             # 基础伤害 = ATK × 倍率
    crit_multiplier: float         # 暴击倍率
    def_reduction: float           # 防御减伤系数
    dmg_pct_total: float           # 总增伤倍率
    break_damage: int              # 击破伤害（独立计算）
    vuln_multiplier: float         # 易伤倍率
    resisted: bool                 # 是否被抵抗


def calculate_def_reduction(defender_def: int, attacker_level: int) -> float:
    """
    防御减伤公式（崩铁）
    DEF_reduction = DEF / (DEF + 200 + 10 × Level)
    """
    return defender_def / (defender_def + 200.0 + 10.0 * attacker_level)


def calculate_break_damage(
    attacker: Character,
    defender: Character,
    break_type,
) -> int:
    """
    击破伤害（弱点击破触发）
    BreakDMG = 基础伤害 × 击破系数 × 韧性系数 × (1 + 击破特攻)
    基础伤害与角色等级挂钩，这里简化为 level × 10
    """
    base = attacker.level * 10
    # 不同属性的击破系数
    break_coeffs = {
        "SLASH": 2.0,    # 物理：2.0
        "BURN": 1.0,     # 火：1.0
        "FREEZE": 1.0,   # 冰：1.0（冻结主要控制，伤害低）
        "SHOCK": 1.0,    # 雷：1.0
        "SHEAR": 1.5,    # 风：1.5
        "ENTANGLE": 0.5,  # 量子：0.5
        "IMPRISON": 0.5, # 虚数：0.5
    }
    coeff = break_coeffs.get(break_type.name, 1.0)
    # 韧性系数（假设敌人韧性为5）
    toughness_coeff = (5 + 2) / 4.0
    efficiency = 1.0 + attacker.stat.break_efficiency
    return int(base * coeff * toughness_coeff * efficiency)


def calculate_damage(
    attacker: Character,
    defender: Character,
    skill_multiplier: float,
    base_damage_add: float = 0,
    damage_type: Optional[Element] = None,
    ignore_def: float = 0.0,
    fixed_damage: int = 0,
    break_dot: Optional[BreakDotEffect] = None,
) -> DamageResult:
    """
    伤害计算主公式

    FinalDMG = ATK × Multiplier × (1 - DEF_RED) × (1 + DMG%) × CRIT × (1 + VULN) + 固定伤害 + 击破伤害
    """
    element = damage_type or attacker.element

    # === 1. 攻击力（最终值 = 基础×百分比 + 固定） ===
    atk = attacker.stat.total_atk()

    # === 2. 基础伤害 = ATK × 技能倍率 + 固定伤害 ===
    base_damage = atk * skill_multiplier + base_damage_add

    # === 3. 防御减伤 ===
    effective_def = defender.stat.total_def() * (1 - ignore_def)
    def_reduction = calculate_def_reduction(int(effective_def), attacker.level)
    after_def = base_damage * (1 - def_reduction)

    # === 4. 增伤区 DMG% = 1 + sum(所有伤害加成) ===
    # 包括：角色dmg_pct属性 + 被动/光锥等提供的dmg_pct
    total_dmg_pct = 1.0 + attacker.stat.dmg_pct

    # 加上效果中的伤害加成
    for effect in attacker.effects:
        total_dmg_pct += effect.dmg_pct_bonus

    # === 5. 暴击判定 ===
    crit_roll = random.random()  # 0-1
    is_crit = crit_roll < attacker.stat.crit_rate
    crit_mult = attacker.stat.crit_dmg if is_crit else 1.0

    # === 6. 易伤区 VULN = 1 + sum(所有易伤) ===
    total_vuln = 1.0
    for effect in defender.effects:
        total_vuln += effect.vuln_pct

    # === 7. 击破伤害（独立计算，加在最终伤害上） ===
    break_damage = 0
    if break_dot:
        break_damage = break_dot.damage_per_tick * break_dot.stacks

    # === 8. 最终伤害 ===
    final_mult = total_dmg_pct * crit_mult * total_vuln
    final_damage = int(after_def * final_mult) + fixed_damage + break_damage
    final_damage = max(1, final_damage)  # 最低保底 1 点伤害

    return DamageResult(
        final_damage=final_damage,
        is_crit=is_crit,
        base_damage=round(base_damage, 2),
        crit_multiplier=crit_mult,
        def_reduction=round(def_reduction, 4),
        dmg_pct_total=round(total_dmg_pct - 1, 4),  # 显示加成的百分比部分
        break_damage=break_damage,
        vuln_multiplier=round(total_vuln - 1, 4),   # 显示易伤百分比
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
