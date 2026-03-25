"""回合制战斗引擎"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Optional
import json
import os

from .models import Character, BattleState, Element, Skill, SkillType
from .damage import calculate_damage, apply_damage, DamageResult
from .skill import SkillExecutor, build_skills_from_json, assign_default_skills


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

        # 加载技能数据并分配给角色
        if skills_data is None:
            skills_data = self._load_skills_data()
        self._skills_data = skills_data
        self._assign_skills_to_teams()

    def _load_skills_data(self) -> list:
        """从 data/skills.json 加载技能数据"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.join(base_dir, "data", "skills.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return []

    def _assign_skills_to_teams(self) -> None:
        """为队伍中所有角色分配技能"""
        all_chars = self.state.player_team + self.state.enemy_team
        for char in all_chars:
            if not char.skills:
                assign_default_skills(char, self._skills_data)
            # 如果角色没有任何技能，添加默认普攻
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
            # 获取所有存活的角色并按速度排序（SPD 高的先行动）
            alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
            alive.sort(key=lambda c: c.stat.spd, reverse=True)

            if not alive:
                break

            # 检查战斗是否结束
            over, winner = self.state.is_battle_over()
            if over:
                result = "🎉 胜利！" if winner == "player" else "💀 失败..."
                self._log(BattleEvent(
                    turn=self.state.turn,
                    actor=alive[0],
                    action="END",
                    detail=f"战斗结束：{result}",
                ))
                return result

            for actor in alive:
                if not actor.is_alive():
                    continue

                # 再次检查（可能上一轮被其他人击杀）
                over, winner = self.state.is_battle_over()
                if over:
                    result = "🎉 胜利！" if winner == "player" else "💀 失败..."
                    self._log(BattleEvent(
                        turn=self.state.turn,
                        actor=actor,
                        action="END",
                        detail=f"战斗结束：{result}",
                    ))
                    return result

                # 回合开始：回复 1 点能量（上限 3）
                actor.current_energy = min(
                    SkillExecutor.MAX_ENERGY,
                    actor.current_energy + 1.0,
                )

                # 清除到期的效果
                actor.remove_expired_effects()

                # 当前角色行动
                self._process_action(actor, alive)

            # 回合结束：所有效果回合数 -1
            all_alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
            for char in all_alive:
                for effect in char.effects:
                    effect.turns_remaining -= 1
                char.remove_expired_effects()

            self.state.turn += 1

    def _process_action(self, actor: Character, alive: list[Character]) -> None:
        """处理角色行动：使用 SkillExecutor 选择并执行最优技能"""
        # 选择目标：对手队伍中的存活角色
        if actor in self.state.player_team:
            opponents = [c for c in alive if c in self.state.enemy_team]
        else:
            opponents = [c for c in alive if c in self.state.player_team]

        if not opponents:
            return

        # 选择最优技能
        skill = self._skill_executor.select_best_skill(actor)
        if skill is None:
            return

        targets = [opponents[0]]  # 简单 AI：默认攻击第一个敌人

        results = self._skill_executor.execute(skill, actor, targets)

        if results:
            target, result = results[0]
            action_name = skill.type.name
            detail = (
                f"{actor.name} 使用 {skill.name} 攻击 {target.name}，"
                f"造成 {result.final_damage} 伤害"
                + (" ⚡暴击！" if result.is_crit else "")
                + (f" [{skill.damage_type.name} 属性]" if skill.damage_type != actor.element else "")
            )
            self._log(BattleEvent(
                turn=self.state.turn,
                actor=actor,
                action=action_name,
                detail=detail,
                damage_result=result,
            ))


def create_default_character(name: str, element: Element = Element.PHYSICAL) -> Character:
    """创建默认角色（已分配属性，技能待 battle 引擎分配）"""
    from .models import Stat
    return Character(
        name=name,
        level=1,
        element=element,
        stat=Stat(max_hp=1000, atk=100, def_=50, spd=100),
        current_hp=1000,
        current_energy=0.0,
    )
