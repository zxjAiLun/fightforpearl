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

    def _effective_multiplier(self, skill: Skill, target_index: int = 0) -> float:
        """计算有效倍率：AOE时应用 aoe_multiplier 折扣"""
        if skill.is_aoe():
            # AOE技能：对所有目标应用aoe_multiplier折扣
            return skill.multiplier * skill.aoe_multiplier
        elif skill.is_ricochet():
            # 弹射技能：每次弹射递减
            return skill.multiplier * (skill.ricochet_decay ** target_index)
        elif skill.is_spread() and target_index > 0:
            # 扩散技能：主目标全额，扩散目标应用spread_multiplier
            return skill.multiplier * skill.spread_multiplier
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
        results = []
        attacker_is_player = not caster.is_enemy

        # 处理弹射技能
        if skill.is_ricochet():
            results = self._execute_ricochet(skill, caster, targets, battle_state, DamageSource.BASIC)
        # 处理扩散技能
        elif skill.is_spread():
            results = self._execute_spread(skill, caster, targets, battle_state, DamageSource.BASIC)
        # 普通或AOE技能
        else:
            for idx, target in enumerate(targets):
                eff_mult = self._effective_multiplier(skill, idx)
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
        """战技：ATK × 1.5 倍率，消耗战绩点，回复能量"""
        from .damage import calculate_damage, apply_damage

        # 战技消耗战绩点（玩家角色）
        if not caster.is_enemy and battle_state is not None:
            if not battle_state.use_shared_battle_points(1):
                # 战绩点不足，战技无法使用
                return []

        results = []
        attacker_is_player = not caster.is_enemy

        # 处理辅助技能（不造成伤害，应用Modifier）
        if skill.is_support_skill:
            results = self._execute_support_skill(skill, caster, targets, battle_state, DamageSource.SPECIAL)
        # 处理弹射技能
        elif skill.is_ricochet():
            results = self._execute_ricochet(skill, caster, targets, battle_state, DamageSource.SPECIAL)
        # 处理扩散技能
        elif skill.is_spread():
            results = self._execute_spread(skill, caster, targets, battle_state, DamageSource.SPECIAL)
        # 普通或AOE技能
        else:
            for idx, target in enumerate(targets):
                eff_mult = self._effective_multiplier(skill, idx)
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

        results = []
        attacker_is_player = not caster.is_enemy

        # 处理辅助技能（不造成伤害，应用Modifier）
        if skill.is_support_skill:
            results = self._execute_support_skill(skill, caster, targets, battle_state, DamageSource.ULT)
        # 处理弹射技能
        elif skill.is_ricochet():
            results = self._execute_ricochet(skill, caster, targets, battle_state, DamageSource.ULT)
        # 处理扩散技能
        elif skill.is_spread():
            results = self._execute_spread(skill, caster, targets, battle_state, DamageSource.ULT)
        # 普通或AOE技能
        else:
            for idx, target in enumerate(targets):
                eff_mult = self._effective_multiplier(skill, idx)
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

    def _execute_ricochet(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
        battle_state: 'BattleState' = None,
        damage_source: 'DamageSource' = DamageSource.SPECIAL,
    ) -> list[tuple[Character, 'DamageResult']]:
        """
        弹射技能执行：攻击一个目标后弹射到其他目标
        弹射伤害逐次递减（ricochet_decay）
        """
        from .damage import calculate_damage, apply_damage

        results = []
        attacker_is_player = not caster.is_enemy

        if not targets:
            return results

        # 首先对第一个目标造成伤害（主目标）
        primary_target = targets[0]
        eff_mult = self._effective_multiplier(skill, 0)  # 主目标无衰减
        result = calculate_damage(
            caster, primary_target,
            skill_multiplier=eff_mult,
            damage_type=skill.damage_type,
            damage_source=damage_source,
            attacker_is_player=attacker_is_player,
        )
        apply_damage(caster, primary_target, result)
        results.append((primary_target, result))

        # 然后弹射到其他目标
        bounce_targets = targets[1:skill.ricochet_count] if skill.ricochet_count > 0 else []
        for i, target in enumerate(bounce_targets):
            eff_mult = self._effective_multiplier(skill, i + 1)  # 弹射目标有衰减
            result = calculate_damage(
                caster, target,
                skill_multiplier=eff_mult,
                damage_type=skill.damage_type,
                damage_source=damage_source,
                attacker_is_player=attacker_is_player,
            )
            apply_damage(caster, target, result)
            results.append((target, result))

        return results

    def _execute_spread(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
        battle_state: 'BattleState' = None,
        damage_source: 'DamageSource' = DamageSource.SPECIAL,
    ) -> list[tuple[Character, 'DamageResult']]:
        """
        扩散技能执行：主目标受全额伤害，其他目标受扩散伤害
        """
        from .damage import calculate_damage, apply_damage

        results = []
        attacker_is_player = not caster.is_enemy

        if not targets:
            return results

        # 主目标受全额伤害
        primary_target = targets[0]
        eff_mult = self._effective_multiplier(skill, 0)  # 主目标全额
        result = calculate_damage(
            caster, primary_target,
            skill_multiplier=eff_mult,
            damage_type=skill.damage_type,
            damage_source=damage_source,
            attacker_is_player=attacker_is_player,
        )
        apply_damage(caster, primary_target, result)
        results.append((primary_target, result))

        # 扩散目标受扩散伤害
        spread_targets = skill.get_spread_targets(targets, primary_target)
        for i, target in enumerate(spread_targets):
            eff_mult = self._effective_multiplier(skill, i + 1)  # 扩散目标有衰减
            result = calculate_damage(
                caster, target,
                skill_multiplier=eff_mult,
                damage_type=skill.damage_type,
                damage_source=damage_source,
                attacker_is_player=attacker_is_player,
            )
            apply_damage(caster, target, result)
            results.append((target, result))

        return results

    def _execute_support_skill(
        self,
        skill: Skill,
        caster: Character,
        targets: list[Character],
        battle_state: 'BattleState' = None,
        damage_source: 'DamageSource' = DamageSource.SPECIAL,
    ) -> list[tuple[Character, 'DamageResult']]:
        """
        辅助技能执行：不造成伤害，应用Modifier效果
        
        辅助技能如布洛妮娅的"指令"（拉条）和"轮契"（加爆伤）
        """
        from .modifier import Modifier
        from .damage import DamageResult
        
        results = []
        
        if not targets:
            return results
        
        # 根据技能名称应用对应的Modifier
        modifier_name = skill.support_modifier_name
        
        for target in targets:
            mod = None
            
            # 布洛妮娅的技能
            if skill.name == "指令":
                # 拉条100% Modifier
                mod = Modifier(
                    name="指令-拉条",
                    source_skill="指令",
                    duration=1,
                    modifier_type=ModifierType.BUFF,
                    pull_forward_pct=1.0,  # 100%拉条
                )
            elif skill.name == "轮契":
                # 爆伤加成 Modifier
                mod = Modifier(
                    name="轮契-爆伤",
                    source_skill="轮契",
                    duration=2,
                    modifier_type=ModifierType.BUFF,
                    crit_dmg_pct=0.6,  # +60%爆伤
                )
            
            if mod:
                target.add_modifier(mod)
                # 创建空的DamageResult表示技能成功施放
                result = DamageResult(
                    final_damage=0,
                    is_crit=False,
                    base_damage=0.0,
                    crit_multiplier=1.0,
                    def_reduction=0.0,
                    dmg_pct_total=0.0,
                    vuln_multiplier=0.0,
                    damage_source=damage_source,
                    break_triggered=False,
                    break_result=None,
                    resisted=False,
                )
                results.append((target, result))
        
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


def _load_enemy_ai_config() -> dict:
    """加载敌人AI配置"""
    try:
        import json
        from pathlib import Path
        path = Path(__file__).parent.parent.parent / "data" / "enemy_ai.json"
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_ENEMY_AI_CONFIG = _load_enemy_ai_config()


def select_enemy_targets(caster: Character, opponents: list[Character]) -> list[Character]:
    """
    敌人选择目标的逻辑：
    - 优先选择血量最低的目标
    - 存活角色按当前HP从小到大排序
    """
    if not opponents:
        return []

    alive = [c for c in opponents if c.is_alive()]
    if not alive:
        return []

    # 按当前HP升序排列：血量最低的排前面
    sorted_opponents = sorted(alive, key=lambda c: c.current_hp)
    return sorted_opponents


def select_enemy_skill(caster: Character, opponents: list[Character] = None) -> Optional[Skill]:
    """
    敌人技能选择逻辑（崩坏星穹铁道风格）：
    1. 大招优先（能量满时） - ULT优先级最高
    2. AOE技能优先（当有多个目标时）
    3. 战技次之
    4. 普攻最后（保底）

    Args:
        caster: 敌人角色
        opponents: 可用目标列表（用于判断是否使用AOE）
    """
    if not caster.skills:
        return None

    # 按优先级分组技能
    ult_skills = [s for s in caster.skills if s.type == SkillType.ULT]
    special_skills = [s for s in caster.skills if s.type == SkillType.SPECIAL]
    basic_skills = [s for s in caster.skills if s.type == SkillType.BASIC]

    # 1. 能量满时优先使用大招
    if caster.is_energy_full() and ult_skills:
        # 如果有多目标，优先选择AOE大招
        opponent_count = len([c for c in (opponents or []) if c.is_alive()]) if opponents else 0
        aoe_ults = [s for s in ult_skills if s.is_aoe()]
        non_aoe_ults = [s for s in ult_skills if not s.is_aoe()]

        if opponent_count >= 2 and aoe_ults:
            return aoe_ults[0]
        return ult_skills[0]

    # 2. 有多个目标时，优先使用AOE技能
    if opponents:
        opponent_count = len([c for c in opponents if c.is_alive()])
        if opponent_count >= 2:
            # 收集所有AOE技能（含大招、战技）
            aoe_skills = []
            if caster.is_energy_full():
                aoe_skills.extend(aoe_ults)
            aoe_skills.extend([s for s in special_skills if s.is_aoe()])
            aoe_skills.extend([s for s in basic_skills if s.is_aoe()])

            if aoe_skills:
                return aoe_skills[0]

    # 3. 战技次之
    if special_skills:
        return special_skills[0]

    # 4. 普攻保底
    if basic_skills:
        return basic_skills[0]

    # 最后保险：返回任意技能
    return caster.skills[0] if caster.skills else None


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
                target_count=int(s.get("target_count", 1)),
                aoe_multiplier=float(s.get("aoe_multiplier", 0.8)),
                ricochet_count=int(s.get("ricochet_count", 0)),
                ricochet_decay=float(s.get("ricochet_decay", 0.8)),
                spread_count=int(s.get("spread_count", 0)),
                spread_multiplier=float(s.get("spread_multiplier", 0.5)),
                is_support_skill=bool(s.get("is_support_skill", False)),
                support_modifier_name=s.get("support_modifier_name", ""),
            ))
        result[char_name] = skills
    return result


def assign_default_skills(char: Character, skills_data: list[dict]) -> None:
    """根据角色名从技能数据中分配技能，未找到时使用默认普攻"""
    # 如果角色已经有技能，跳过（避免重复分配）
    if char.skills:
        return
    
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
                    target_count=int(s.get("target_count", 1)),
                    aoe_multiplier=float(s.get("aoe_multiplier", 0.8)),
                    ricochet_count=int(s.get("ricochet_count", 0)),
                    ricochet_decay=float(s.get("ricochet_decay", 0.8)),
                    spread_count=int(s.get("spread_count", 0)),
                    spread_multiplier=float(s.get("spread_multiplier", 0.5)),
                    is_support_skill=bool(s.get("is_support_skill", False)),
                    support_modifier_name=s.get("support_modifier_name", ""),
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
