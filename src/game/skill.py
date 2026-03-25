"""技能系统 + 被动技能触发"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .models import Character, Skill, SkillType, Element, Passive, Effect, BreakEffectType, ELEMENT_BREAK_MAP

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
        技能执行后触发对应被动。
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
        # 触发普攻被动（如果有）
        self._trigger_passives(caster, SkillType.BASIC)
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
        # 触发战技被动
        self._trigger_passives(caster, SkillType.SPECIAL)
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
        # 触发大招被动
        self._trigger_passives(caster, SkillType.ULT)
        return results

    def _trigger_passives(self, caster: Character, trigger_type: SkillType) -> None:
        """
        触发被动技能
        被动触发后添加对应 BUFF 效果到角色身上，持续指定回合
        """
        for passive in caster.passives:
            if passive.trigger == trigger_type:
                # 避免同一回合重复触发同名被动
                if passive.name in caster.passives_triggered_this_turn:
                    continue

                # 创建 BUFF 效果
                effect = Effect(
                    name=passive.name,
                    turns_remaining=passive.duration,
                )
                if passive.effect_type == "dmg_increase":
                    effect.dmg_pct_bonus = passive.value
                elif passive.effect_type == "atk_increase":
                    effect.atk_pct_bonus = passive.value

                # 应用到角色（修改属性）
                effect.apply_to(caster)
                caster.effects.append(effect)
                caster.passives_triggered_this_turn.append(passive.name)

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
    """从 JSON 数据构建技能字典。"""
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


def assign_default_passives(char: Character) -> None:
    """
    给角色分配默认被动技能（战技增伤 + 大招加攻）
    - 被动1：释放战技后，造成伤害+30%，持续2回合
    - 被动2：释放大招后，攻击力+30%，持续2回合
    """
    char.passives.append(Passive(
        name="战技·增伤",
        trigger=SkillType.SPECIAL,
        effect_type="dmg_increase",
        value=0.30,
        duration=2,
        description="释放战技后，造成伤害增加30%，持续2回合",
    ))
    char.passives.append(Passive(
        name="大招·加攻",
        trigger=SkillType.ULT,
        effect_type="atk_increase",
        value=0.30,
        duration=2,
        description="释放大招后，攻击力增加30%，持续2回合",
    ))
