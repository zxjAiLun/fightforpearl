"""技能系统 + 被动技能触发"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .models import Character, Skill, SkillType, Element, Passive, Effect, BreakEffectType, ELEMENT_BREAK_MAP, DamageSource, BattleState

if TYPE_CHECKING:
    from .damage import DamageResult


class SkillExecutor:
    """技能执行器"""

    def execute(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
        battle_state: 'BattleState' = None,
    ) -> list[tuple[Character, 'DamageResult']]:
        """
        执行技能，返回 (目标, 伤害结果) 列表。
        不满足能量条件时返回空列表。
        技能执行后触发对应被动。
        """
        from .damage import calculate_damage, apply_damage

        if skill.type == SkillType.BASIC:
            return self._execute_basic(skill, caster, targets, battle_state)
        elif skill.type == SkillType.SPECIAL:
            return self._execute_special(skill, caster, targets, battle_state)
        elif skill.type == SkillType.ULT:
            return self._execute_ult(skill, caster, targets, battle_state)
        return []

    def _effective_multiplier(self, skill: Skill) -> float:
        """计算有效倍率：AOE时应用 aoe_multiplier 折扣"""
        if skill.is_aoe():
            return skill.multiplier * skill.aoe_multiplier
        return skill.multiplier

    def _execute_basic(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
        battle_state: 'BattleState' = None,
    ) -> list[tuple[Character, 'DamageResult']]:
        """普攻：ATK × 1.0 倍率，回复能量和战绩点"""
        from .damage import calculate_damage, apply_damage
        eff_mult = self._effective_multiplier(skill)
        results = []
        attacker_is_player = not caster.is_enemy
        for target in targets:
            result = calculate_damage(
                caster, target,
                skill_multiplier=eff_mult,
                damage_type=skill.damage_type,
                damage_source=DamageSource.BASIC,
                attacker_is_player=attacker_is_player,
            )
            apply_damage(caster, target, result)
            results.append((target, result))
        caster.add_energy(skill.energy_gain)
        if battle_state is not None and skill.battle_points_gain > 0 and not caster.is_enemy:
            battle_state.add_shared_battle_points(skill.battle_points_gain)
        self._trigger_passives(caster, SkillType.BASIC)
        return results

    def _execute_special(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
        battle_state: 'BattleState' = None,
    ) -> list[tuple[Character, 'DamageResult']]:
        """战技：ATK × 1.5 倍率，回复能量"""
        from .damage import calculate_damage, apply_damage

        eff_mult = self._effective_multiplier(skill)
        results = []
        attacker_is_player = not caster.is_enemy
        for target in targets:
            result = calculate_damage(
                caster, target,
                skill_multiplier=eff_mult,
                damage_type=skill.damage_type,
                damage_source=DamageSource.SPECIAL,
                attacker_is_player=attacker_is_player,
            )
            apply_damage(caster, target, result)
            results.append((target, result))

        caster.add_energy(skill.energy_gain)
        self._trigger_passives(caster, SkillType.SPECIAL)
        return results

    def _execute_ult(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
        battle_state: 'BattleState' = None,
    ) -> list[tuple[Character, 'DamageResult']]:
        """大招：ATK × 3.0 倍率，需能量满（≥120），释放后能量重置为0"""
        from .damage import calculate_damage, apply_damage

        if not caster.is_energy_full():
            return []

        eff_mult = self._effective_multiplier(skill)
        results = []
        attacker_is_player = not caster.is_enemy
        for target in targets:
            result = calculate_damage(
                caster, target,
                skill_multiplier=eff_mult,
                damage_type=skill.damage_type,
                damage_source=DamageSource.ULT,
                attacker_is_player=attacker_is_player,
            )
            apply_damage(caster, target, result)
            results.append((target, result))

        caster.energy = 0.0
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
            return True
        elif skill.type == SkillType.ULT:
            return caster.is_energy_full()
        return False

    def select_best_skill(self, caster: Character, battle_state=None) -> Optional[Skill]:
        """
        根据当前能量和战绩点选择最优技能：
        - 大招优先（能量满）
        - 战技次之（战绩点足够）
        - 普攻最后
        """
        for skill in caster.skills:
            if skill.type == SkillType.ULT and self.can_use_skill(skill, caster):
                return skill

        if battle_state is not None and not caster.is_enemy:
            bp = battle_state.shared_battle_points
            if bp >= 1:
                for skill in caster.skills:
                    if skill.type == SkillType.SPECIAL:
                        return skill

        for skill in caster.skills:
            if skill.type == SkillType.BASIC:
                return skill

        for skill in caster.skills:
            if skill.type == SkillType.SPECIAL:
                return skill
        return None


def select_player_skill(caster: Character, battle_state=None) -> Optional[Skill]:
    """
    玩家角色技能选择逻辑：
    - 大招优先（能量满）
    - 战技次之（战绩点足够）
    - 普攻最后
    """
    for skill in caster.skills:
        if skill.type == SkillType.ULT and caster.is_energy_full():
            return skill

    if battle_state is not None:
        bp = battle_state.shared_battle_points
        if bp >= 1:
            for skill in caster.skills:
                if skill.type == SkillType.SPECIAL:
                    return skill

    for skill in caster.skills:
        if skill.type == SkillType.BASIC:
            return skill

    for skill in caster.skills:
        if skill.type == SkillType.SPECIAL:
            return skill
    return None


def select_enemy_skill(caster: Character) -> Optional[Skill]:
    """
    敌人技能选择逻辑：
    - 敌人固定使用普攻
    - 确保敌人总是能执行行动
    """
    for skill in caster.skills:
        if skill.type == SkillType.BASIC:
            return skill

    for skill in caster.skills:
        if skill.type == SkillType.SPECIAL:
            return skill

    if caster.skills:
        return caster.skills[0]
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
                energy_gain=float(s.get("energy_gain", 10.0)),
                battle_points_gain=int(s.get("battle_points_gain", 0)),
                hit_energy_gain=int(s.get("hit_energy_gain", 10)),
                break_power=float(s.get("break_power", 0.0)),
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
                    energy_gain=float(s.get("energy_gain", 10.0)),
                    battle_points_gain=int(s.get("battle_points_gain", 0)),
                    hit_energy_gain=int(s.get("hit_energy_gain", 10)),
                    break_power=float(s.get("break_power", 0.0)),
                ))
            return
    # Fallback: 添加默认普攻
    char.skills.append(Skill(
        name="基础攻击",
        type=SkillType.BASIC,
        cost=0.0,
        multiplier=1.0,
        damage_type=char.element,
        energy_gain=20.0,
        battle_points_gain=1,
        hit_energy_gain=10,
        break_power=10.0,
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
