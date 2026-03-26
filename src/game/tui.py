"""游戏 TUI 界面"""
from __future__ import annotations
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from .battle import BattleEngine, BattleState, BattleEvent, create_default_character, create_enemy
from .character import create_character_from_preset
from .models import Element


def print_battle_event_damage_only(event: BattleEvent):
    """仅显示伤害相关事件"""
    print(f"  [{event.turn}] {event.detail}")


def print_battle_event_full(event: BattleEvent):
    """显示完整战斗信息"""
    av_bar = _make_action_value_bar(event.action_value)
    print(f"  [{event.turn}] AV:{event.action_value:.1f}{av_bar} BP:{event.shared_battle_points}/{event.shared_battle_points_limit} | {event.detail}")


def _make_action_value_bar(total_av: float) -> str:
    """生成累计行动值条"""
    if total_av < 0:
        return ""
    filled = min(int(total_av / 50), 20)
    return f" [累计:{filled}/20]"


def _make_energy_bar(energy: float, limit: int) -> str:
    """生成能量条"""
    filled = int(energy / limit * 5)
    return "⚡" * filled + "○" * (5 - filled)


def print_character_status(char, shared_battle_points: int = None, shared_battle_points_limit: int = None):
    """显示角色状态"""
    hp_bar = "█" * int(char.current_hp / char.stat.total_max_hp() * 10)
    hp_bar += "░" * (10 - len(hp_bar))
    elem = char.element.name
    
    if shared_battle_points is not None:
        print(f"  {char.name} [{elem}] HP:{char.current_hp}/{char.stat.total_max_hp()} |{hp_bar}| 能量:{int(char.energy)}/{char.energy_limit} BP:{shared_battle_points}/{shared_battle_points_limit} SPD:{char.stat.total_spd()} AV:{char.action_value:.1f}")
    else:
        print(f"  {char.name} [{elem}] HP:{char.current_hp}/{char.stat.total_max_hp()} |{hp_bar}| 能量:{int(char.energy)}/{char.energy_limit} BP:{char.battle_points}/{char.battle_points_limit} SPD:{char.stat.total_spd()} AV:{char.action_value:.1f}")


def _make_action_bar(char) -> str:
    """生成行动条可视化"""
    av = getattr(char, 'action_value', 0.0)
    spd = char.stat.total_spd()
    if spd <= 0:
        return "░" * 10
    progress = max(0, 1 - av / 100.0) if av >= 0 else 1.0
    filled = int(progress * 10)
    return "█" * filled + "░" * (10 - filled)


def create_player_team() -> list:
    """创建默认玩家队伍：星、银狼、姬子、布洛妮娅"""
    return [
        create_character_from_preset("星"),
        create_character_from_preset("银狼"),
        create_character_from_preset("姬子"),
        create_character_from_preset("布洛妮娅"),
    ]


def battle_demo(log_level: str = BattleEngine.DAMAGE_ONLY):
    """演示战斗
    
    Args:
        log_level: 日志级别，BattleEngine.DAMAGE_ONLY 或 BattleEngine.FULL_DETAIL
    """
    player_team = create_player_team()
    
    enemy1 = create_enemy(
        name="可可利亚",
        weakness_elements=[Element.THUNDER, Element.FIRE],
        hp_units=10,
    )
    
    enemy2 = create_enemy(
        name="史瓦罗",
        weakness_elements=[Element.THUNDER, Element.FIRE],
        hp_units=10,
    )

    print("=" * 70)
    print("⚔️  Fight for Pearl — 战斗演示")
    print(f"日志级别: {'全部事件' if log_level == BattleEngine.FULL_DETAIL else '仅伤害'}")
    print("=" * 70)

    state = BattleState(
        player_team=player_team,
        enemy_team=[enemy1, enemy2],
        turn=1,
        shared_battle_points=3,
        shared_battle_points_limit=5,
    )

    engine = BattleEngine(state, log_level=log_level)
    
    if log_level == BattleEngine.FULL_DETAIL:
        engine.set_logger(print_battle_event_full)
    else:
        engine.set_logger(print_battle_event_damage_only)

    print("\n【战斗开始】")
    for i, player in enumerate(player_team):
        print(f"我方{i+1}：{player.name} (HP:{player.current_hp} SPD:{player.stat.total_spd()})")
    print(f"敌方：{enemy1.name} (HP:{enemy1.current_hp} SPD:{enemy1.stat.total_spd()})")
    print(f"敌方：{enemy2.name} (HP:{enemy2.current_hp} SPD:{enemy2.stat.total_spd()})")
    print()

    result = engine.start()

    print("\n【战斗结果】")
    for char in state.player_team + state.enemy_team:
        if char in state.player_team:
            print_character_status(char, state.shared_battle_points, state.shared_battle_points_limit)
        else:
            print_character_status(char)
    print(f"\n{result}")

    return engine


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fight for Pearl 战斗演示")
    parser.add_argument("--full", action="store_true", help="显示完整战斗日志")
    parser.add_argument("--export", type=str, default=None, help="导出战斗日志到指定文件")
    args = parser.parse_args()
    
    log_level = BattleEngine.FULL_DETAIL if args.full else BattleEngine.DAMAGE_ONLY
    engine = battle_demo(log_level)
    
    if args.export:
        engine.export_to_json(args.export)
        print(f"\n战斗日志已导出到: {args.export}")


if __name__ == "__main__":
    main()
