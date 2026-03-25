"""回合制战斗引擎"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Optional
import json
import os

from .models import (
    Character, BattleState, Element, Skill, SkillType,
    Passive, Effect, BreakEffectType, ELEMENT_BREAK_MAP, Stat,
    DamageSource, FollowUpRule,
)
from .damage import calculate_damage, apply_damage, DamageResult, calculate_break_damage
from .skill import SkillExecutor, build_skills_from_json, assign_default_skills, assign_default_passives


@dataclass
class BattleEvent:
    """战斗事件"""
    turn: int
    actor: Character
    action: str
    detail: str
    damage_result: Optional[DamageResult] = None


class BattleEngine:
    """回合制战斗引擎"""

    def __init__(self, state: BattleState, skills_data: Optional[list] = None):
        self.state = state
        self.events: list[BattleEvent] = []
        self._log_callback: Callable[[BattleEvent], None] | None = None
        self._skill_executor = SkillExecutor()

        if skills_data is None:
            skills_data = self._load_skills_data()
        self._skills_data = skills_data
        self._assign_skills_and_passives_to_teams()

    def _load_skills_data(self) -> list:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.join(base_dir, "data", "skills.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return []

    def _assign_skills_and_passives_to_teams(self) -> None:
        all_chars = self.state.player_team + self.state.enemy_team
        for char in all_chars:
            if not char.skills:
                assign_default_skills(char, self._skills_data)
            if not char.passives:
                assign_default_passives(char)
            if not char.skills:
                char.skills.append(Skill(
                    name="基础攻击",
                    type=SkillType.BASIC,
                    cost=0.0,
                    multiplier=1.0,
                    damage_type=char.element,
                ))

    def set_logger(self, cb: Callable[[BattleEvent], None]):
        self._log_callback = cb

    def _log(self, event: BattleEvent):
        self.events.append(event)
        if self._log_callback:
            self._log_callback(event)

    def start(self) -> str:
        """开始战斗，返回战斗结果描述"""
        self.events = []
        first_char = self.state.player_team[0] if self.state.player_team else None
        self._log(BattleEvent(
            turn=0,
            actor=first_char or Character("N/A"),
            action="START",
            detail="战斗开始！",
        ))

        while True:
            # 速度排序（考虑行动延后）
            alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
            alive.sort(key=lambda c: c.stat.total_spd() * (1 - getattr(c, 'action_delay', 0.0)), reverse=True)

            if not alive:
                break

            over, winner = self.state.is_battle_over()
            if over:
                result_str = "🎉 胜利！" if winner == "player" else "💀 失败..."
                self._log(BattleEvent(
                    turn=self.state.turn,
                    actor=alive[0],
                    action="END",
                    detail=f"战斗结束：{result_str}",
                ))
                return result_str

            for actor in alive:
                if not actor.is_alive():
                    continue

                # 被冻结则跳过本回合
                if not actor.can_act():
                    status = self.state._break_status(actor)
                    if status.is_frozen():
                        self._log(BattleEvent(
                            turn=self.state.turn,
                            actor=actor,
                            action="FROZEN",
                            detail=f"{actor.name} 被冻结，跳过本回合",
                        ))
                    # 冻结回合递减
                    if actor.frozen_turns > 0:
                        actor.frozen_turns -= 1
                        if actor.frozen_turns <= 0:
                            status.freeze_turns = 0
                    continue

                # 结算行动延后
                status = self.state._break_status(actor)
                if actor.action_delay > 0:
                    delay_pct = actor.action_delay
                    actor.action_delay = 0.0
                    # 行动延后不影响本回合，但下回合行动会延后
                    # （已通过排序时 spd*(1-delay) 实现）
                    self._log(BattleEvent(
                        turn=self.state.turn,
                        actor=actor,
                        action="DELAYED",
                        detail=f"{actor.name} 行动延后 {int(delay_pct * 100)}%",
                    ))

                # 再次检查冻结（可能刚解冻）
                if not actor.can_act():
                    continue

                over, winner = self.state.is_battle_over()
                if over:
                    result_str = "🎉 胜利！" if winner == "player" else "💀 失败..."
                    self._log(BattleEvent(
                        turn=self.state.turn,
                        actor=actor,
                        action="END",
                        detail=f"战斗结束：{result_str}",
                    ))
                    return result_str

                # 回合开始：回复能量
                actor.current_energy = min(
                    SkillExecutor.MAX_ENERGY,
                    actor.current_energy + 1.0,
                )

                # 清理过期效果
                for effect in actor.effects:
                    if effect.turns_remaining <= 0:
                        effect.remove_from(actor)
                actor.remove_expired_effects()

                # 当前角色行动
                self._process_action(actor, alive)

            # 回合结束
            all_alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
            for char in all_alive:
                for effect in char.effects:
                    effect.turns_remaining -= 1
                    if effect.turns_remaining <= 0:
                        effect.remove_from(char)
                char.remove_expired_effects()
                char.end_turn_cleanup()

            # 回合结束：击破DOT触发
            dot_results = self.state.tick_break_dots()
            for char, dmg, name in dot_results:
                self._log(BattleEvent(
                    turn=self.state.turn,
                    actor=char,
                    action="BREAK_DOT",
                    detail=f"{char.name} 受到 {name} 伤害 {dmg}",
                ))

            # 回合结束：清理击破状态
            self.state.end_turn_break_cleanup()

            self.state.turn += 1

    def _process_action(self, actor: Character, alive: list[Character]) -> None:
        """处理角色行动"""
        if actor in self.state.player_team:
            opponents = [c for c in alive if c in self.state.enemy_team]
        else:
            opponents = [c for c in alive if c in self.state.player_team]

        if not opponents:
            return

        skill = self._skill_executor.select_best_skill(actor)
        if skill is None:
            return

        # 多目标选择
        targets = skill.get_targets(opponents)
        if not targets:
            return

        results = self._skill_executor.execute(skill, actor, targets)

        if not results:
            return

        action_name = skill.type.name

        # AOE时，汇总伤害信息
        if len(results) > 1:
            total_dmg = sum(r.final_damage for _, r in results)
            target_names = ", ".join(t.name for t, _ in results)
            detail = f"{actor.name} 使用 {skill.name} 攻击 {target_names}，造成共计 {total_dmg} 伤害"
            _, first_result = results[0]
            if first_result.is_crit:
                detail += " ⚡暴击！"
            self._log(BattleEvent(
                turn=self.state.turn,
                actor=actor,
                action=action_name,
                detail=detail,
                damage_result=first_result,
            ))
        else:
            target, result = results[0]
            detail_parts = [
                f"{actor.name} 使用 {skill.name} 攻击 {target.name}，造成 {result.final_damage} 伤害"
            ]
            if result.is_crit:
                detail_parts.append("⚡暴击！")
            self._log(BattleEvent(
                turn=self.state.turn,
                actor=actor,
                action=action_name,
                detail=" ".join(detail_parts),
                damage_result=result,
            ))

        # 每个目标独立结算击破和效果
        for target, result in results:
            break_msg = self._try_break(target, actor, skill)
            if break_msg:
                self._log(BattleEvent(
                    turn=self.state.turn,
                    actor=actor,
                    action="BREAK",
                    detail=f"{target.name}: {break_msg}",
                ))

            # 纠缠受击叠加
            target_status = self.state._break_status(target)
            if target_status.break_type == BreakEffectType.ENTANGLE:
                target_status.entangle_hit_stacks = min(5, target_status.entangle_hit_stacks + 1)
                target.entangle_hit_stacks = target_status.entangle_hit_stacks

        # 触发追击
        self._try_follow_up(actor, skill, results)

    def _try_break(self, target: Character, attacker: Character, skill: Skill) -> str:
        """
        检查技能攻击是否触发弱点击破。
        条件：目标有对应弱点元素 且 韧性值可被削。
        返回击破描述字符串，无击破则返回空。
        """
        if not target.is_enemy:
            return ""  # 玩家角色无法被击破

        # 目标弱点元素列表
        weaknesses = getattr(target, 'weakness_elements', [])
        if not weaknesses:
            return ""

        skill_element = skill.damage_type

        if skill_element not in weaknesses:
            return ""

        # 触发击破！
        break_type = ELEMENT_BREAK_MAP.get(skill_element, BreakEffectType.NONE)
        if break_type == BreakEffectType.NONE:
            return ""

        # 削韧性
        toughness = getattr(target, 'toughness', 0.0)
        break_efficiency = attacker.stat.break_efficiency
        toughness_reduction = 30.0 * break_efficiency  # 每次攻击削30点韧性（简化）
        target.toughness = max(0, target.toughness - toughness_reduction)

        # 韧性清零才触发击破
        if target.toughness > 0:
            return f"[削韧 {target.toughness:.0f}]"

        # 韧性清零，触发击破
        target.toughness = 100.0  # 恢复（下一波攻击可再次击破）
        br = self.state.apply_break(target, attacker, break_type, skill_element)

        msg = f"【击破！{br.detail}】造成 {br.break_damage} 击破伤害"
        return msg

    def _try_follow_up(
        self,
        actor: Character,
        skill: Skill,
        results: list[tuple[Character, DamageResult]],
    ) -> None:
        """
        追击处理：
        在主动技能造成伤害后，检查角色是否有追击规则满足条件。
        追击是独立行动，消耗回合但不回复能量。
        """
        import random

        if not results:
            return

        triggered_any = False
        for rule in actor.follow_up_rules:
            # 检查触发条件：释放了指定类型的技能
            if rule.trigger_skill_type != skill.type:
                continue

            # 概率判定
            if random.random() > rule.chance:
                continue

            # 找到追击目标（优先第一个受伤目标）
            target = results[0][0]

            # 查找追击技能
            follow_up_skill = None
            for s in actor.skills:
                if s.name == rule.follow_up_skill_name:
                    follow_up_skill = s
                    break

            if follow_up_skill is None:
                # 没有找到指定技能，使用普攻作为追击
                for s in actor.skills:
                    if s.type == SkillType.BASIC:
                        follow_up_skill = s
                        break

            if follow_up_skill is None:
                continue

            # 执行追击
            multiplier = rule.multiplier
            dmg_result = calculate_damage(
                actor, target,
                skill_multiplier=multiplier,
                damage_type=rule.damage_type,
                damage_source=DamageSource.FOLLOW_UP,
            )
            apply_damage(actor, target, dmg_result)

            self._log(BattleEvent(
                turn=self.state.turn,
                actor=actor,
                action="FOLLOW_UP",
                detail=f"{actor.name} 追击！对 {target.name} 造成 {dmg_result.final_damage} 追击伤害"
                    + (" ⚡暴击！" if dmg_result.is_crit else ""),
                damage_result=dmg_result,
            ))
            triggered_any = True

        if triggered_any:
            # 追击后，该角色本回合不再行动（追击是独立行动）
            # 注意：追击本身不消耗回合，它只是回合内的一个额外行动
            pass


def create_default_character(name: str, element: Element = Element.PHYSICAL) -> Character:
    """创建默认角色（用于测试）"""
    stat = Stat(
        base_max_hp=1000,
        base_atk=100,
        base_def=50,
        base_spd=100,
    )
    char = Character(
        name=name,
        level=1,
        element=element,
        stat=stat,
        current_hp=stat.total_max_hp(),
        current_energy=0.0,
    )
    return char


def create_enemy(
    name: str,
    level: int,
    element: Element,
    max_hp: int,
    atk: int,
    defense: int,
    spd: int,
    weakness_elements: list[Element],
) -> Character:
    """
    创建敌人（带弱点元素和韧性值）
    """
    stat = Stat(
        base_max_hp=max_hp,
        base_atk=atk,
        base_def=defense,
        base_spd=spd,
    )
    char = Character(
        name=name,
        level=level,
        element=element,
        stat=stat,
        current_hp=max_hp,
        current_energy=0.0,
        is_enemy=True,
        weakness_elements=weakness_elements,
        toughness=100.0,
    )
    return char
