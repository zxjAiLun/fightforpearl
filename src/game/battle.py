"""战斗引擎"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Optional
import json

from .models import (
    Character, BattleState, Skill, SkillType, BreakEffectType,
    BreakResult, BreakStatus, Effect, Passive,
)
from .skill import SkillExecutor
from .damage import calculate_damage, apply_damage, DamageSource, DamageResult
from .config.battle import FIRST_ROUND_AV, SUBSEQUENT_AV, AV_BASE

ACTION_COST = AV_BASE  # 行动值基准 = 10000


@dataclass
class BattleEvent:
    """战斗事件"""
    turn: int
    actor: Character
    action: str
    detail: str
    damage_result: Optional[DamageResult] = None
    action_value: float = 0.0
    shared_battle_points: int = 0
    shared_battle_points_limit: int = 5
    hp_before: Optional[float] = None
    energy_before: Optional[float] = None
    bp_before: Optional[int] = None


@dataclass
class RoundMarker:
    """回合结束标记（中立Dummy角色）"""
    round_num: int
    action_value: float

    @property
    def name(self) -> str:
        return f"round{self.round_num}end"

    @property
    def is_round_marker(self) -> bool:
        return True

    @property
    def is_enemy(self) -> bool:
        return False

    def is_alive(self) -> bool:
        return True

    def can_act(self) -> bool:
        return True


class BattleEngine:
    """回合制战斗引擎"""

    DAMAGE_ONLY = "damage_only"
    FULL_DETAIL = "full_detail"

    def __init__(self, state: BattleState, skills_data=None, log_level: str = DAMAGE_ONLY):
        self.state = state
        self.events: list[BattleEvent] = []
        self._log_callback: Callable[[BattleEvent], None] | None = None
        self._skill_executor = SkillExecutor()
        self._log_level = log_level
        self._total_action_value = 0.0
        self._current_turn = 1
        self._round_marker: RoundMarker | None = None

        if skills_data is None:
            skills_data = self._load_skills_data()
        self._skills_data = skills_data
        self._assign_skills_and_passives_to_teams()
        self._create_round_marker()

    def _load_skills_data(self) -> list:
        try:
            import json
            from pathlib import Path
            path = Path(__file__).parent.parent.parent / "data" / "skills.json"
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            import sys
            print(f"Failed to load skills: {e}", file=sys.stderr)
            return []

    def _assign_skills_and_passives_to_teams(self):
        from .skill import assign_default_skills, assign_default_passives
        for char in self.state.player_team + self.state.enemy_team:
            if not char.skills:
                assign_default_skills(char, self._skills_data)
            if not char.passives:
                assign_default_passives(char)

    def set_logger(self, cb: Callable[[BattleEvent], None]):
        self._log_callback = cb

    def _log(self, event: BattleEvent, show_detail: bool = False):
        event.action_value = self._total_action_value
        event.shared_battle_points = self.state.shared_battle_points
        event.shared_battle_points_limit = self.state.shared_battle_points_limit
        self.events.append(event)

        if self._log_level == self.DAMAGE_ONLY:
            if event.action in ["BASIC", "SPECIAL", "ULT", "FOLLOW_UP", "START", "END", "ROUND_MARKER"]:
                if self._log_callback:
                    self._log_callback(event)
        elif self._log_level == self.FULL_DETAIL:
            if self._log_callback:
                self._log_callback(event)

    def _init_action_values(self) -> None:
        all_chars = self.state.player_team + self.state.enemy_team
        for char in all_chars:
            if char.is_alive():
                spd = char.stat.total_spd()
                char.action_value = ACTION_COST / spd if spd > 0 else ACTION_COST
                char.base_spd = char.stat.base_spd

    def _get_current_time(self) -> float:
        alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
        if alive:
            return max(c.action_value for c in alive)
        return 0.0

    def _get_next_action_time(self, current_time: float) -> float:
        alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
        if not alive:
            return float('inf')
        return min(c.action_value for c in alive)

    def _get_round_end_time(self, round_num: int) -> float:
        return FIRST_ROUND_AV if round_num == 1 else SUBSEQUENT_AV

    def _create_round_marker(self) -> None:
        self._round_marker = RoundMarker(
            round_num=self._current_turn,
            action_value=self._get_round_end_time(self._current_turn)
        )

    def get_full_state_info(self) -> dict:
        player_info = []
        for char in self.state.player_team:
            player_info.append({
                "name": char.name,
                "hp": char.current_hp,
                "max_hp": char.stat.total_max_hp(),
                "energy": int(char.energy),
                "energy_limit": char.energy_limit,
                "spd": char.stat.total_spd(),
                "action_value": round(char.action_value, 2),
            })
        
        enemy_info = []
        for char in self.state.enemy_team:
            enemy_info.append({
                "name": char.name,
                "hp": char.current_hp,
                "max_hp": char.stat.total_max_hp(),
                "toughness": char.toughness,
                "spd": char.stat.total_spd(),
                "action_value": round(char.action_value, 2),
            })
        
        return {
            "total_action_value": round(self._total_action_value, 2),
            "shared_battle_points": self.state.shared_battle_points,
            "shared_battle_points_limit": self.state.shared_battle_points_limit,
            "players": player_info,
            "enemies": enemy_info,
        }

    def export_to_json(self, filepath: str = "battle_log.json"):
        events_data = []
        for e in self.events:
            event_data = {
                "turn": e.turn,
                "actor": e.actor.name,
                "action": e.action,
                "detail": e.detail,
                "action_value": round(e.action_value, 2),
                "shared_battle_points": e.shared_battle_points,
            }
            if e.damage_result:
                event_data["damage"] = e.damage_result.final_damage
                event_data["is_crit"] = e.damage_result.is_crit
            events_data.append(event_data)
        
        output = {
            "final_state": self.get_full_state_info(),
            "events": events_data,
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    def _process_single_action(self) -> Optional[BattleEvent]:
        over, winner = self.state.is_battle_over()
        if over:
            self._log(BattleEvent(
                turn=self._current_turn,
                actor=Character("N/A"),
                action="END",
                detail="Victory!" if winner == "player" else "Defeat...",
            ))
            return None

        alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
        if not alive:
            self._log(BattleEvent(
                turn=self._current_turn,
                actor=Character("N/A"),
                action="END",
                detail="战斗结束，无存活角色",
            ))
            return None

        round_end_time = self._get_round_end_time(self._current_turn)
        next_action_time = min(c.action_value for c in alive)

        if next_action_time >= round_end_time:
            return self._process_round_marker_action()

        actor = min(alive, key=lambda c: c.action_value)

        if not actor.can_act():
            frozen_turns = getattr(actor, 'frozen_turns', 0)
            if frozen_turns > 0:
                actor.frozen_turns -= 1
                if actor.frozen_turns <= 0:
                    self.state._break_status(actor).freeze_turns = 0
                    actor.reset_action_value_after_freeze()
                    self._log(BattleEvent(
                        turn=self._current_turn,
                        actor=actor,
                        action="UNFROZEN",
                        detail=f"{actor.name} 解除冻结",
                    ))
                else:
                    self._log(BattleEvent(
                        turn=self._current_turn,
                        actor=actor,
                        action="FROZEN",
                        detail=f"{actor.name} 被冻结，剩余 {actor.frozen_turns} 回合",
                    ))
            actor.action_value += ACTION_COST / actor.stat.total_spd()
            return self.events[-1] if self.events else None

        for effect in actor.effects:
            if effect.turns_remaining <= 0:
                effect.remove_from(actor)
        actor.remove_expired_effects()

        if actor.action_delay > 0:
            delay_pct = actor.action_delay
            actor.action_delay = 0.0
            actor.apply_delay(delay_pct)

        if not actor.can_act():
            actor.action_value += ACTION_COST / actor.stat.total_spd()
            return self.events[-1] if self.events else None

        if actor in self.state.player_team:
            opponents = [c for c in alive if c in self.state.enemy_team]
        else:
            opponents = [c for c in alive if c in self.state.player_team]

        if not opponents:
            actor.action_value += ACTION_COST / actor.stat.total_spd()
            return self.events[-1] if self.events else None

        from .skill import select_enemy_skill, select_player_skill, select_enemy_targets
        if actor.is_enemy:
            # 敌人智能：选择最优技能（考虑AOE/能量），选择血量最低的目标
            skill = select_enemy_skill(actor, opponents)
            sorted_targets = select_enemy_targets(actor, opponents)
            # AOE技能打全部目标，单目标技能打血量最低的
            targets = sorted_targets if (skill and skill.is_aoe()) else sorted_targets[:1]
        else:
            skill = select_player_skill(actor, self.state)
            targets = skill.get_targets(opponents)

        if skill is None or not targets:
            actor.action_value += ACTION_COST / actor.stat.total_spd()
            return self.events[-1] if self.events else None

        results = self._skill_executor.execute(skill, actor, targets, self.state)

        if not results:
            actor.action_value += ACTION_COST / actor.stat.total_spd()
            return self.events[-1] if self.events else None

        actor.action_value += ACTION_COST / actor.stat.total_spd()
        self._log_action_event(actor, skill, results)

        for target, result in results:
            break_msg = self._try_break(target, actor, skill)
            if break_msg:
                self._log(BattleEvent(
                    turn=self._current_turn,
                    actor=actor,
                    action="BREAK",
                    detail=f"{target.name}: {break_msg}",
                ))

            if not target.is_alive():
                if actor in self.state.player_team:
                    kill_gain = getattr(actor, 'kill_energy_gain', 10)
                    actor.add_energy(kill_gain, affected_by_recovery_rate=True)
                    self._log(BattleEvent(
                        turn=self._current_turn,
                        actor=actor,
                        action="KILL",
                        detail=f"{actor.name} 击杀目标",
                    ))

            target_status = self.state._break_status(target)
            if target_status.break_type == BreakEffectType.ENTANGLE:
                target_status.entangle_hit_stacks = min(5, target_status.entangle_hit_stacks + 1)
                target.entangle_hit_stacks = target_status.entangle_hit_stacks

        self._try_follow_up(actor, skill, results, self._current_turn)

        return self.events[-1] if self.events else None

    def _process_round_marker_action(self) -> Optional[BattleEvent]:
        self._log(BattleEvent(
            turn=self._current_turn,
            actor=self._round_marker,
            action="ROUND_MARKER",
            detail=f"round{self._current_turn}end",
        ))

        alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
        for char in alive:
            for effect in char.effects:
                effect.turns_remaining -= 1
                if effect.turns_remaining <= 0:
                    effect.remove_from(char)
            char.remove_expired_effects()
            char.end_turn_cleanup()

        dot_results = self.state.tick_break_dots()
        for char, dmg, name in dot_results:
            self._log(BattleEvent(
                turn=self._current_turn,
                actor=char,
                action="DOT",
                detail=f"{char.name} 受到 {name} 伤害 {dmg}",
            ))

        self.state.end_turn_break_cleanup()

        alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
        round_offset = (self._current_turn - 1) * SUBSEQUENT_AV
        for char in alive:
            if char.is_alive():
                spd = char.stat.total_spd()
                char.action_value = round_offset + ACTION_COST / spd if spd > 0 else round_offset + ACTION_COST

        self._current_turn += 1
        self._create_round_marker()

        return self.events[-1] if self.events else None

    def _log_action_event(self, actor: Character, skill: Skill, results: list):
        action_name = skill.type.name
        
        hp_before = actor.current_hp
        energy_before = actor.energy
        bp_before = self.state.shared_battle_points
        
        if len(results) > 1:
            total_dmg = sum(r.final_damage for _, r in results)
            target_names = ", ".join(t.name for t, _ in results)
            _, first_result = results[0]
            detail = f"{actor.name} 使用 {skill.name} 攻击 {target_names}，造成共计 {total_dmg} 伤害"
            if first_result.is_crit:
                detail += " CRIT!"
            event = BattleEvent(
                turn=self._current_turn,
                actor=actor,
                action=action_name,
                detail=detail,
                damage_result=first_result,
                hp_before=hp_before,
                energy_before=energy_before,
                bp_before=bp_before,
            )
            self._log(event)
        else:
            target, result = results[0]
            detail_parts = [
                f"{actor.name} 使用 {skill.name} 攻击 {target.name}，造成 {result.final_damage} 伤害"
            ]
            if result.is_crit:
                detail_parts.append("CRIT!")
            event = BattleEvent(
                turn=self._current_turn,
                actor=actor,
                action=action_name,
                detail=" ".join(detail_parts),
                damage_result=result,
                hp_before=hp_before,
                energy_before=energy_before,
                bp_before=bp_before,
            )
            self._log(event)

    def _try_break(self, target: Character, caster: Character, skill: Skill) -> Optional[str]:
        if target.toughness > 0:
            target.toughness -= getattr(skill, 'break_power', 10)
        
        if target.toughness <= 0 and skill.damage_type in target.weakness_elements:
            target.toughness = 0
            break_type = self._get_break_effect_type(skill.damage_type)
            result = self.state.apply_break(target, caster, break_type, skill.damage_type)
            return f"触发 {break_type.name}"
        return None

    def _get_break_effect_type(self, element) -> BreakEffectType:
        from .models import ELEMENT_BREAK_MAP
        return ELEMENT_BREAK_MAP.get(element, BreakEffectType.NONE)

    def _try_follow_up(self, caster: Character, skill: Skill, results: list, turn: int):
        if not caster.follow_up_rules:
            return
        
        for rule in caster.follow_up_rules:
            if rule.trigger_skill_type == skill.type:
                if rule.check_trigger(caster):
                    follow_up_targets = [t for t, _ in results]
                    follow_up_skill = Skill(
                        name=rule.follow_up_skill_name,
                        type=SkillType.FOLLOW_UP,
                        multiplier=rule.multiplier,
                        damage_type=rule.damage_type,
                    )
                    for target in follow_up_targets:
                        result = calculate_damage(
                            caster, target,
                            skill_multiplier=follow_up_skill.multiplier,
                            damage_type=follow_up_skill.damage_type,
                            damage_source=DamageSource.FOLLOW_UP,
                            attacker_is_player=not caster.is_enemy,
                        )
                        apply_damage(caster, target, result)
                    
                    self._log(BattleEvent(
                        turn=turn,
                        actor=caster,
                        action="FOLLOW_UP",
                        detail=f"{caster.name} 触发追击！",
                        damage_result=result,
                    ))

    def step_back(self) -> bool:
        """
        回退到上一个行动状态
        Returns:
            bool: 是否成功回退
        """
        if not self.events:
            return False
        
        if len(self.events) < 2:
            return False
        
        last_event = self.events[-1]
        
        if last_event.turn != self._current_turn:
            return False
        
        if last_event.action in ["END", "START", "ROUND_MARKER"]:
            return False
        
        if not hasattr(last_event, 'hp_before') or last_event.hp_before is None:
            return False
        
        actor = last_event.actor
        if actor and hasattr(actor, 'current_hp'):
            actor.current_hp = last_event.hp_before
        
        if actor and hasattr(actor, 'energy'):
            actor.energy = last_event.energy_before if last_event.energy_before is not None else actor.energy
        
        if last_event.bp_before is not None:
            self.state.shared_battle_points = last_event.bp_before
        
        if hasattr(actor, 'action_value') and actor.action_value is not None:
            spd = actor.stat.total_spd() if hasattr(actor, 'stat') and actor.stat else 100
            actor.action_value -= ACTION_COST / spd if spd > 0 else ACTION_COST
        
        self.events.pop()
        
        return True

    def start(self) -> str:
        self._init_action_values()
        self._current_turn = 1
        
        self._log(BattleEvent(
            turn=1,
            actor=Character("N/A"),
            action="START",
            detail="战斗开始",
        ))
        
        turn_counter = 0
        
        while True:
            turn_counter += 1
            
            over, winner = self.state.is_battle_over()
            if over:
                result_str = "Victory!" if winner == "player" else "Defeat..."
                self._log(BattleEvent(
                    turn=self._current_turn,
                    actor=Character("N/A"),
                    action="END",
                    detail=f"战斗结束：{result_str}",
                ))
                return result_str
            
            alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
            if not alive:
                break
            
            while True:
                alive = [c for c in self.state.player_team + self.state.enemy_team if c.is_alive()]
                if not alive:
                    break
                
                current_time = self._get_current_time()
                next_time = self._get_next_action_time(current_time)
                round_end_time = self._get_round_end_time(self._current_turn)
                
                if next_time > round_end_time:
                    break
                
                actor = min(alive, key=lambda c: c.action_value)  # 行动值最小的先行动
                self._process_action(actor, alive, turn_counter)
                actor.action_value += ACTION_COST / actor.stat.total_spd()
            
            for char in alive:
                for effect in char.effects:
                    effect.turns_remaining -= 1
                    if effect.turns_remaining <= 0:
                        effect.remove_from(char)
                char.remove_expired_effects()
                char.end_turn_cleanup()
            
            dot_results = self.state.tick_break_dots()
            for char, dmg, name in dot_results:
                self._log(BattleEvent(
                    turn=turn_counter,
                    actor=char,
                    action="DOT",
                    detail=f"{char.name} 受到 {name} 伤害 {dmg}",
                ))
            
            self.state.end_turn_break_cleanup()
            self._current_turn += 1
        
        return "平局..."

    def _process_action(self, actor: Character, alive: list, turn_counter: int):
        if not actor.can_act():
            if actor.frozen_turns > 0:
                actor.frozen_turns -= 1
                if actor.frozen_turns <= 0:
                    self.state._break_status(actor).freeze_turns = 0
                    actor.reset_action_value_after_freeze()
                    self._log(BattleEvent(
                        turn=turn_counter,
                        actor=actor,
                        action="UNFROZEN",
                        detail=f"{actor.name} 解除冻结，行动值重置",
                    ))
            return
        
        for effect in actor.effects:
            if effect.turns_remaining <= 0:
                effect.remove_from(actor)
        actor.remove_expired_effects()
        
        if actor.action_delay > 0:
            delay_pct = actor.action_delay
            actor.action_delay = 0.0
            actor.apply_delay(delay_pct)
            self._log(BattleEvent(
                turn=turn_counter,
                actor=actor,
                action="DELAYED",
                detail=f"{actor.name} 行动延后 {int(delay_pct * 100)}%",
            ))
        
        if not actor.can_act():
            return
        
        if actor in self.state.player_team:
            opponents = [c for c in alive if c in self.state.enemy_team]
        else:
            opponents = [c for c in alive if c in self.state.player_team]
        
        if not opponents:
            return
        
        if actor.is_enemy:
            from .skill import select_enemy_skill, select_enemy_targets
            skill = select_enemy_skill(actor, opponents)
            sorted_targets = select_enemy_targets(actor, opponents)
            targets = sorted_targets if (skill and skill.is_aoe()) else sorted_targets[:1]
        else:
            skill = self._skill_executor.select_best_skill(actor, self.state)
            targets = skill.get_targets(opponents) if skill else []
        
        if skill is None or not targets:
            return
        
        results = self._skill_executor.execute(skill, actor, targets, self.state)
        
        if not results:
            return
        
        self._log_action_event(actor, skill, results)
        
        for target, result in results:
            break_msg = self._try_break(target, actor, skill)
            if break_msg:
                self._log(BattleEvent(
                    turn=turn_counter,
                    actor=actor,
                    action="BREAK",
                    detail=f"{target.name}: {break_msg}",
                ))
            
            if not target.is_alive():
                if actor in self.state.player_team:
                    kill_gain = getattr(actor, 'kill_energy_gain', 10)
                    actor.add_energy(kill_gain, affected_by_recovery_rate=True)
                    self._log(BattleEvent(
                        turn=turn_counter,
                        actor=actor,
                        action="KILL",
                        detail=f"{actor.name} 击杀目标，回复能量",
                    ))
            
            target_status = self.state._break_status(target)
            if target_status.break_type == BreakEffectType.ENTANGLE:
                target_status.entangle_hit_stacks = min(5, target_status.entangle_hit_stacks + 1)
                target.entangle_hit_stacks = target_status.entangle_hit_stacks
        
        self._try_follow_up(actor, skill, results, turn_counter)


def create_default_character(name: str, element=None) -> Character:
    from .models import Element, Stat
    if element is None:
        element = Element.PHYSICAL
    stat = Stat(
        base_max_hp=1200,
        base_atk=120,
        base_def=80,
        base_spd=105,
    )
    char = Character(
        name=name,
        level=80,
        element=element,
        stat=stat,
        current_hp=stat.total_max_hp(),
        energy=60,
        energy_limit=120,
        battle_points=3,
        battle_points_limit=5,
        base_spd=stat.base_spd,
    )
    return char


def create_enemy(
    name: str,
    level: int = 90,
    hp_units: float = 10.0,
    atk: int = 663,
    defense: int = 1100,
    spd: int = 132,
    weakness_elements: list = None,
    toughness: float = 40.0,
) -> Character:
    from .models import Element, Stat, Character
    
    if weakness_elements is None:
        weakness_elements = []
    
    stat = Stat(
        base_max_hp=1,
        base_atk=atk,
        base_def=defense,
        base_spd=spd,
        effect_hit=0.32,
        effect_res=0.30,
    )
    
    char = Character(
        name=name,
        level=level,
        element=Element.PHYSICAL,
        stat=stat,
        current_hp=1,
        is_enemy=True,
        weakness_elements=weakness_elements,
        toughness=toughness,
        base_spd=stat.base_spd,
        action_value=0.0,
        hp_units=hp_units,
    )
    
    final_hp = char.calculate_hp()
    char.current_hp = final_hp
    stat.base_max_hp = final_hp
    
    return char
