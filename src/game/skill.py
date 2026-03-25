"""技能系统"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Character, Skill, Effect
    from .damage import DamageResult


class SkillExecutor:
    """技能执行器"""

    def execute(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
    ) -> list[tuple[Character, DamageResult]]:
        """
        执行技能，返回 (目标, 伤害结果) 列表
        """
        if skill.type == BASIC:
            return self._execute_basic(skill, caster, targets)
        elif skill.type == SPECIAL:
            return self._execute_special(skill, caster, targets)
        elif skill.type == ULT:
            return self._execute_ult(skill, caster, targets)
        return []

    def _execute_basic(self, skill, caster, targets):
        from .damage import calculate_damage, apply_damage
        results = []
        for target in targets:
            result = calculate_damage(caster, target, skill.multiplier, damage_type=skill.damage_type)
            apply_damage(caster, target, result)
            results.append((target, result))
        return results

    def _execute_special(self, skill, caster, targets):
        from .damage import calculate_damage, apply_damage
        results = []
        for target in targets:
            result = calculate_damage(caster, target, skill.multiplier, damage_type=skill.damage_type)
            apply_damage(caster, target, result)
            results.append((target, result))
        # 战技消耗能量
        caster.current_energy -= skill.cost
        return results

    def _execute_ult(self, skill, caster, targets):
        from .damage import calculate_damage, apply_damage
        results = []
        for target in targets:
            result = calculate_damage(caster, target, skill.multiplier, damage_type=skill.damage_type)
            apply_damage(caster, target, result)
            results.append((target, result))
        caster.current_energy -= caster.current_energy  # 清空能量
        return results
