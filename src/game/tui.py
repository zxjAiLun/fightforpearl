"""游戏 TUI 界面"""
from __future__ import annotations
import sys

from .battle import BattleEngine, BattleState, BattleEvent, create_default_character
from .models import Element


def print_battle_event(event: BattleEvent):
    print(f"  [{event.turn}] {event.detail}")


def print_character_status(char):
    hp_bar = "█" * int(char.current_hp / char.stat.max_hp * 10)
    hp_bar += "░" * (10 - len(hp_bar))
    elem = char.element.name
    print(f"  {char.name} [{elem}] HP:{char.current_hp}/{char.stat.max_hp} SPD:{char.stat.spd} |{hp_bar}|")


def battle_demo():
    """演示战斗"""
    # 创建角色
    player = create_default_character("星穹", Element.THUNDER)
    enemy1 = create_default_character("可可利亚", Element.ICE)
    enemy2 = create_default_character("史瓦罗", Element.ICE)

    print("=" * 50)
    print("⚔️  Fight for Pearl — 战斗演示")
    print("=" * 50)

    state = BattleState(
        player_team=[player],
        enemy_team=[enemy1, enemy2],
        turn=1,
    )

    engine = BattleEngine(state)
    engine.set_logger(print_battle_event)

    print("\n【战斗开始】")
    print(f"我方：{player.name} (HP:{player.current_hp} SPD:{player.stat.spd})")
    print(f"敌方：{enemy1.name} (HP:{enemy1.current_hp} SPD:{enemy1.stat.spd})")
    print(f"敌方：{enemy2.name} (HP:{enemy2.current_hp} SPD:{enemy2.stat.spd})")
    print()

    result = engine.start()

    print("\n【战斗结果】")
    for char in state.player_team + state.enemy_team:
        print_character_status(char)
    print(f"\n{result}")


def main():
    battle_demo()


if __name__ == "__main__":
    main()
