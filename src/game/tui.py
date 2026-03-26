"""游戏 TUI 界面"""
from __future__ import annotations
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from .battle import BattleEngine, BattleState, BattleEvent, create_default_character, create_enemy
from .character import create_character_from_preset
from .models import Element, SkillType


def prompt_skill_selection(actor, available_skills, opponents) -> tuple:
    """
    TUI模式下提示玩家选择技能和目标
    
    Args:
        actor: 当前行动的角色
        available_skills: 可用的技能列表
        opponents: 可选择的敌人目标
    
    Returns:
        (skill, targets): 选中的技能和目标列表
    """
    from .skill import select_player_skill
    
    # 获取可用的技能
    available = []
    for skill in available_skills:
        if skill.type == SkillType.ULT and not actor.is_energy_full():
            continue  # 大招能量不足
        if skill.type == SkillType.SPECIAL:
            # 战技需要战绩点，但在TUI中我们不检查这个
            available.append(skill)
        else:
            available.append(skill)
    
    # 显示技能选择菜单
    print(f"\n{'='*50}")
    print(f"【{actor.name}】选择技能：")
    print(f"能量: {int(actor.energy)}/{actor.energy_limit}")
    print(f"战绩点: (团队共享)")
    print(f"{'='*50}")
    
    for i, skill in enumerate(available, 1):
        skill_type = skill.type.name
        if skill.type == SkillType.ULT:
            skill_type = "大招"
        elif skill.type == SkillType.SPECIAL:
            skill_type = "战技"
        elif skill.type == SkillType.BASIC:
            skill_type = "普攻"
        
        print(f"  {i}. {skill.name} [{skill_type}] - 倍率:{skill.multiplier}")
    
    # 显示目标选择
    print(f"\n可用目标：")
    for i, opp in enumerate(opponents, 1):
        print(f"  {i}. {opp.name} (HP:{int(opp.current_hp)}/{opp.stat.total_max_hp()})")
    
    # 读取玩家输入
    while True:
        try:
            skill_choice = input("\n选择技能(数字): ").strip()
            skill_idx = int(skill_choice) - 1
            if 0 <= skill_idx < len(available):
                selected_skill = available[skill_idx]
                break
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入数字")
    
    # 选择目标
    if selected_skill.is_aoe() or selected_skill.target_count == -1:
        # AOE技能选择所有目标
        targets = opponents
    else:
        while True:
            try:
                target_choice = input("\n选择目标(数字，逗号分隔多个): ").strip()
                if not target_choice:
                    # 默认选择第一个目标
                    targets = [opponents[0]]
                    break
                
                indices = [int(x.strip()) - 1 for x in target_choice.split(",")]
                targets = [opponents[i] for i in indices if 0 <= i < len(opponents)]
                if targets:
                    break
                else:
                    print("无效的选择，请重新输入")
            except ValueError:
                print("请输入有效的数字")
    
    print(f"选择了 {selected_skill.name}，目标: {[t.name for t in targets]}")
    
    return selected_skill, targets


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
    parser.add_argument("--team", type=str, default=None, help="指定队伍角色（逗号分隔，如'星,银狼,姬子,布洛妮娅'）")
    parser.add_argument("--enemy", type=int, default=2, help="敌人数量（默认2）")
    parser.add_argument("--player", action="store_true", help="启用玩家手动技能选择")
    args = parser.parse_args()
    
    # 自定义队伍
    if args.team:
        team_names = args.team.split(",")
        player_team = [create_character_from_preset(name.strip()) for name in team_names]
    else:
        player_team = create_player_team()
    
    # 创建敌人
    enemies = []
    enemy_names = ["可可利亚", "史瓦罗", "杰维斯", "可可利亚Ⅲ"]
    for i in range(min(args.enemy, len(enemy_names))):
        enemy = create_enemy(
            name=enemy_names[i],
            weakness_elements=[Element.THUNDER, Element.FIRE],
            hp_units=10,
        )
        enemies.append(enemy)
    
    log_level = BattleEngine.FULL_DETAIL if args.full else BattleEngine.DAMAGE_ONLY
    engine = battle_demo_with_custom_team(player_team, enemies, log_level, player_control=args.player)
    
    if args.export:
        engine.export_to_json(args.export)
        print(f"\n战斗日志已导出到: {args.export}")


def battle_demo_with_custom_team(player_team, enemies, log_level=BattleEngine.DAMAGE_ONLY, player_control=False):
    """使用自定义队伍的演示战斗
    
    Args:
        player_team: 玩家队伍
        enemies: 敌人队伍
        log_level: 日志级别
        player_control: 是否启用玩家手动控制
    """
    
    print("=" * 70)
    print("⚔️  Fight for Pearl — 战斗演示")
    print(f"日志级别: {'全部事件' if log_level == BattleEngine.FULL_DETAIL else '仅伤害'}")
    print(f"玩家控制: {'启用' if player_control else '关闭(AI自动)'}")
    print("=" * 70)

    state = BattleState(
        player_team=player_team,
        enemy_team=enemies,
        turn=1,
        shared_battle_points=3,
        shared_battle_points_limit=5,
    )

    engine = BattleEngine(state, log_level=log_level)
    
    # 启用玩家手动控制
    if player_control:
        engine.enable_player_control(callback=prompt_skill_selection)
    
    if log_level == BattleEngine.FULL_DETAIL:
        engine.set_logger(print_battle_event_full)
    else:
        engine.set_logger(print_battle_event_damage_only)

    print("\n【战斗开始】")
    for i, player in enumerate(player_team):
        # 显示角色技能信息
        skills_info = ", ".join([f"{s.name}({s.multiplier}x)" for s in player.skills[:3]])
        print(f"我方{i+1}：{player.name} (HP:{player.current_hp} SPD:{player.stat.total_spd()}) 技能:{skills_info}")
    for i, enemy in enumerate(enemies):
        print(f"敌方{i+1}：{enemy.name} (HP:{enemy.current_hp} SPD:{enemy.stat.total_spd()})")
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


if __name__ == "__main__":
    main()
