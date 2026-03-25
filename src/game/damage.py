"""伤害计算模块 — 崩坏星穹铁道风格

伤害公式：
FinalDMG = ATK × Multiplier × (1 - DEF_RED) × (1 + DMG%) × CRIT_MULT × (1 + VULN)

崩铁没有元素克制！元素只影响弱点击破效果。
"""
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Optional

from .models import Character, Element, Effect, BreakDot, BreakEffectType


@dataclass
class DamageResult:
    """伤害计算结果"""
    final_damage: int
    is_crit: bool
    base_damage: float
    crit_multiplier: float
    def_reduction: float
    dmg_pct_total: float
    vuln_multiplier: float
    break_triggered: bool = False
    break_result: Optional[object] = None
    resisted: bool = False


def calculate_def_reduction(defender_def: int, attacker_level: int) -> float:
    """防御减伤 = DEF / (DEF + 200 + 10 × Level)"""
    return defender_def / (defender_def + 200.0 + 10.0 * attacker_level)


def calculate_break_damage(attacker: Character, defender: Character, break_type: BreakEffectType) -> int:
    """
    击破触发伤害（弱点击破时瞬间造成）
    BreakDMG = Level × 10 × 击破系数 × 韧性系数 × (1 + 击破特攻)
    """
    base = attacker.level * 10
    break_coeffs = {
        BreakEffectType.SLASH: 2.0,
        BreakEffectType.BURN: 2.0,
        BreakEffectType.FREEZE: 1.0,
        BreakEffectType.SHOCK: 1.0,
        BreakEffectType.SHEAR: 1.5,
        BreakEffectType.ENTANGLE: 0.5,
        BreakEffectType.IMPRISON: 0.5,
    }
    coeff = break_coeffs.get(break_type, 1.0)
    # 韧性系数：普通敌人韧性60，精英更高，这里简化
    toughness_coeff = (60 + 2) / 4.0  # 约15.5
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
) -> DamageResult:
    """
    伤害计算主公式

    FinalDMG = ATK × Multiplier × (1 - DEF_RED) × (1 + DMG%) × CRIT × (1 + VULN) + 固定伤害
    """
    element = damage_type or attacker.element

    # === 1. 攻击力 ===
    atk = attacker.stat.total_atk()

    # === 2. 基础伤害 ===
    base_damage = atk * skill_multiplier + base_damage_add

    # === 3. 防御减伤 ===
    effective_def = defender.stat.total_def() * (1 - ignore_def)
    def_reduction = calculate_def_reduction(int(effective_def), attacker.level)
    after_def = base_damage * (1 - def_reduction)

    # === 4. 增伤区 ===
    total_dmg_pct = 1.0 + attacker.stat.dmg_pct
    for effect in attacker.effects:
        total_dmg_pct += effect.dmg_pct_bonus

    # === 5. 暴击 ===
    crit_roll = random.random()
    is_crit = crit_roll < attacker.stat.crit_rate
    crit_mult = attacker.stat.crit_dmg if is_crit else 1.0

    # === 6. 易伤区 ===
    total_vuln = 1.0
    for effect in defender.effects:
        total_vuln += effect.vuln_pct

    # === 7. 最终伤害 ===
    final_mult = total_dmg_pct * crit_mult * total_vuln
    final_damage = int(after_def * final_mult) + fixed_damage
    final_damage = max(1, final_damage)

    return DamageResult(
        final_damage=final_damage,
        is_crit=is_crit,
        base_damage=round(base_damage, 2),
        crit_multiplier=crit_mult,
        def_reduction=round(def_reduction, 4),
        dmg_pct_total=round(total_dmg_pct - 1, 4),
        vuln_multiplier=round(total_vuln - 1, 4),
    )


def apply_damage(attacker: Character, defender: Character, result: DamageResult) -> int:
    """将伤害结果应用到目标，返回实际伤害"""
    defender.take_damage(result.final_damage)

    for effect in defender.effects:
        if effect.heal_on_hit > 0:
            heal_amount = int(result.final_damage * effect.heal_on_hit)
            defender.heal(heal_amount)

    return result.final_damage
