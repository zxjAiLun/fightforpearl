"""回合制战斗引擎"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

from .models import Character, BattleState, Element, Skill
from .damage import calculate_damage, apply_damage, DamageResult


@dataclass
class BattleEvent:
    """战斗事件"""
    turn: int
    actor: Character
    action: str
    detail: str
    damage_result: DamageResult | None = None


class BattleEngine:
    """回合制战斗引擎"""

    def __init__(self, state: BattleState):
        self.state = state
        self.events: list[BattleEvent] = []
        self._log_callback: Callable[[BattleEvent], None] | None = None

    def set_logger(self, cb: Callable[[BattleEvent], None]):
        self._log_callback = cb

    def _log(self, event: BattleEvent):
        self.events.append(event)
        if self._log_callback:
            self._log_callback(event)

    def start(self) -> str:
        """开始战斗，返回战斗结果描述"""
        self.events = []
        self._log(BattleEvent(
            turn=0,
            actor=self.state.player_team[0] if self.state.player_team else Character("N/A"),
            action="START",
            detail="战斗开始！",
        ))

        while True:
            # 获取所有存活的角色并按速度排序
            alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
            alive.sort(key=lambda c: c.stat.spd, reverse=True)

            for actor in alive:
                if not actor.is_alive():
                    continue

                # 检查战斗是否结束
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

                # 回合开始时：回复能量、大招充能
                actor.current_energy = min(3.0, actor.current_energy + 1.0)

                # 清除到期的效果
                actor.remove_expired_effects()

                # 当前角色行动
                self._process_action(actor, alive)

            # 回合结束：所有效果回合数 -1
            for char in alive:
                for effect in char.effects:
                    effect.turns_remaining -= 1
                char.remove_expired_effects()

            self.state.turn += 1

    def _process_action(self, actor: Character, alive: list[Character]):
        """处理角色行动（默认：普攻血量最低的敌人）"""
        enemies = [c for c in alive if c in self.state.enemy_team]
        if not enemies:
            return

        # 简单 AI：普攻血量最低的敌人
        target = min(enemies, key=lambda c: c.current_hp)

        result = calculate_damage(actor, target, skill_multiplier=1.0)
        apply_damage(actor, target, result)

        self._log(BattleEvent(
            turn=self.state.turn,
            actor=actor,
            action="ATTACK",
            detail=f"{actor.name} 攻击 {target.name}，造成 {result.final_damage} 伤害"
                + (" ⚡暴击！" if result.is_crit else ""),
            damage_result=result,
        ))


def create_default_character(name: str, element: Element = Element.PHYSICAL) -> Character:
    """创建默认角色"""
    from .models import Stat
    return Character(
        name=name,
        level=1,
        element=element,
        stat=Stat(max_hp=1000, atk=100, def_=50, spd=100),
        current_hp=1000,
        current_energy=0.0,
    )
