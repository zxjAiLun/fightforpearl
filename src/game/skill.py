"""技能系统"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .models import Character, Skill, SkillType, Element

if TYPE_CHECKING:
    from .damage import DamageResult


class SkillExecutor:
    """技能执行器"""

    MAX_ENERGY = 3.0
    ULT_COST = 3.0
    SPECIAL_COST = 1.0
    BASIC_COST = 0.0

    def execute(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
    ) -> list[tuple[Character, 'DamageResult']]:
        """
        执行技能，返回 (目标, 伤害结果) 列表。
        不满足能量条件时返回空列表。
        """
        from .damage import calculate_damage, apply_damage

        if skill.type == SkillType.BASIC:
            return self._execute_basic(skill, caster, targets)
        elif skill.type == SkillType.SPECIAL:
            return self._execute_special(skill, caster, targets)
        elif skill.type == SkillType.ULT:
            return self._execute_ult(skill, caster, targets)
        return []

    def _execute_basic(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
    ) -> list[tuple[Character, 'DamageResult']]:
        """普攻：ATK × 1.0 倍率，不消耗能量"""
        from .damage import calculate_damage, apply_damage
        results = []
        for target in targets:
            result = calculate_damage(
                caster, target,
                skill_multiplier=skill.multiplier,
                damage_type=skill.damage_type,
            )
            apply_damage(caster, target, result)
            results.append((target, result))
        return results

    def _execute_special(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
    ) -> list[tuple[Character, 'DamageResult']]:
        """战技：ATK × 1.5 倍率，消耗 1 点能量"""
        from .damage import calculate_damage, apply_damage

        if caster.current_energy < self.SPECIAL_COST:
            return []

        results = []
        for target in targets:
            result = calculate_damage(
                caster, target,
                skill_multiplier=skill.multiplier,
                damage_type=skill.damage_type,
            )
            apply_damage(caster, target, result)
            results.append((target, result))

        caster.current_energy -= self.SPECIAL_COST
        return results

    def _execute_ult(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
    ) -> list[tuple[Character, 'DamageResult']]:
        """大招：ATK × 3.0 倍率，消耗全部能量（需 ≥3 点）"""
        from .damage import calculate_damage, apply_damage

        if caster.current_energy < self.ULT_COST:
            return []

        results = []
        for target in targets:
            result = calculate_damage(
                caster, target,
                skill_multiplier=skill.multiplier,
                damage_type=skill.damage_type,
            )
            apply_damage(caster, target, result)
            results.append((target, result))

        caster.current_energy = 0.0
        return results

    def can_use_skill(self, skill: Skill, caster: Character) -> bool:
        """检查角色是否满足技能释放条件"""
        if skill.type == SkillType.BASIC:
            return True
        elif skill.type == SkillType.SPECIAL:
            return caster.current_energy >= self.SPECIAL_COST
        elif skill.type == SkillType.ULT:
            return caster.current_energy >= self.ULT_COST
        return False

    def select_best_skill(self, caster: Character) -> Optional[Skill]:
        """
        根据当前能量选择最优技能：
        - 大招优先（能量 ≥ 3）
        - 战技次之（能量 ≥ 1）
        - 普攻兜底
        """
        for skill in caster.skills:
            if skill.type == SkillType.ULT and self.can_use_skill(skill, caster):
                return skill
        for skill in caster.skills:
            if skill.type == SkillType.SPECIAL and self.can_use_skill(skill, caster):
                return skill
        for skill in caster.skills:
            if skill.type == SkillType.BASIC:
                return skill
        return None


def build_skills_from_json(data: list[dict]) -> dict[str, list[Skill]]:
    """
    从 JSON 数据构建技能字典。
    返回 {"角色名": [Skill, ...]}
    """
    result = {}
    for entry in data:
        char_name = entry["character"]
        skills = []
        for s in entry["skills"]:
            skills.append(Skill(
                name=s["name"],
                type=SkillType[s["type"]],
                cost=float(s.get("cost", 0)),
                multiplier=float(s["multiplier"]),
                damage_type=Element[s["damage_type"]],
                description=s.get("description", ""),
            ))
        result[char_name] = skills
    return result


def assign_default_skills(char: Character, skills_data: list[dict]) -> None:
    """根据角色名从技能数据中分配技能，未找到时使用默认普攻"""
    for entry in skills_data:
        if entry["character"] == char.name:
            for s in entry["skills"]:
                char.skills.append(Skill(
                    name=s["name"],
                    type=SkillType[s["type"]],
                    cost=float(s.get("cost", 0)),
                    multiplier=float(s["multiplier"]),
                    damage_type=Element[s["damage_type"]],
                    description=s.get("description", ""),
                ))
            return
    # Fallback: 添加默认普攻
    char.skills.append(Skill(
        name="基础攻击",
        type=SkillType.BASIC,
        cost=0.0,
        multiplier=1.0,
        damage_type=char.element,
    ))
