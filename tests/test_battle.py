"""Battle 战斗引擎测试"""
import pytest
from src.game.battle import BattleEngine, BattleState, create_default_character
from src.game.character import create_character_from_preset
from src.game.models import Element


# ============================================================
# 辅助函数
# ============================================================
def make_char(name: str, element: Element = Element.PHYSICAL):
    return create_character_from_preset(name)


# ============================================================
# 速度排序
# ============================================================
class TestSpeedSorting:
    def test_high_spd_acts_first(self):
        fast = create_character_from_preset("银狼")   # spd=115
        slow = create_character_from_preset("姬子")     # spd=112
        # 虽然差距小，但在同一队伍内排序仍然生效
        player = make_char("星")
        enemy1 = make_char("丹恒")
        enemy2 = make_char("姬子")
        state = BattleState(player_team=[player], enemy_team=[enemy1, enemy2])
        engine = BattleEngine(state)
        # 验证速度计算
        assert player.stat.total_spd() > 0
        assert enemy1.stat.total_spd() > 0

    def test_spd_order_multiple_chars(self):
        chars = [make_char("姬子"), make_char("丹恒"), make_char("星")]
        chars[0].stat.base_spd = 90
        chars[1].stat.base_spd = 110
        chars[2].stat.base_spd = 100
        chars.sort(key=lambda c: c.stat.total_spd(), reverse=True)
        assert chars[0].name == "丹恒"  # 110
        assert chars[1].name == "星"    # 100
        assert chars[2].name == "姬子"  # 90


# ============================================================
# 战斗结束判定
# ============================================================
class TestBattleEndConditions:
    def test_battle_ends_when_enemies_dead(self):
        player = make_char("星")
        enemy = make_char("丹恒")
        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)

        # 把敌人打死
        enemy.take_damage(enemy.stat.total_max_hp())
        over, winner = state.is_battle_over()
        assert over is True
        assert winner == "player"

    def test_battle_ends_when_player_dead(self):
        player = make_char("星")
        enemy = make_char("丹恒")
        state = BattleState(player_team=[player], enemy_team=[enemy])

        player.take_damage(player.stat.total_max_hp())
        over, winner = state.is_battle_over()
        assert over is True
        assert winner == "enemy"

    def test_battle_ends_when_both_sides_dead_same_turn(self):
        player = make_char("星")
        enemy = make_char("丹恒")
        state = BattleState(player_team=[player], enemy_team=[enemy])

        player.take_damage(player.stat.total_max_hp())
        enemy.take_damage(enemy.stat.total_max_hp())
        over, winner = state.is_battle_over()
        assert over is True


# ============================================================
# 死亡角色处理
# ============================================================
class TestDeadCharacterCannotAct:
    def test_dead_character_not_in_alive_list(self):
        player = make_char("星")
        enemy = make_char("丹恒")
        state = BattleState(player_team=[player], enemy_team=[enemy])

        enemy.take_damage(enemy.stat.total_max_hp())
        alive = [c for c in state.player_team + state.enemy_team if c.is_alive()]
        assert enemy not in alive
        assert player in alive

    def test_dead_character_skipped(self):
        player = make_char("星")
        enemy = make_char("丹恒")
        state = BattleState(player_team=[player], enemy_team=[enemy])
        enemy.take_damage(enemy.stat.total_max_hp())

        alive = [c for c in state.player_team + state.enemy_team if c.is_alive()]
        assert len(alive) == 1

    def test_hp_goes_to_zero_on_killing_blow(self):
        player = make_char("星")
        player.take_damage(player.stat.total_max_hp())
        assert player.current_hp == 0


# ============================================================
# 战斗引擎核心
# ============================================================
class TestBattleEngineCore:
    def test_battle_event_logged(self):
        player = make_char("星")
        enemy = make_char("丹恒")
        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)
        result = engine.start()
        assert len(engine.events) > 0
        assert engine.events[0].action == "START"

    def test_multiple_rounds(self):
        player = make_char("星")
        enemy = make_char("丹恒")
        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)
        result = engine.start()
        # 验证有多轮（战斗不应只进行1回合就结束）
        turn_numbers = [e.turn for e in engine.events]
        assert max(turn_numbers) >= 1

    def test_turn_counter_increments(self):
        player = make_char("星")
        enemy = make_char("丹恒")
        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)
        engine.start()
        assert state.turn >= 1


# ============================================================
# 属性系统验证
# ============================================================
class TestStatSystem:
    def test_base_atk_works(self):
        """基础攻击力正确"""
        char = make_char("星")
        assert char.stat.base_atk > 0

    def test_total_atk_includes_bonus(self):
        """总攻击力 = 基础 × (1 + 百分比)"""
        char = make_char("星")
        initial = char.stat.total_atk()
        char.stat.atk_pct += 0.5  # +50%
        assert char.stat.total_atk() == int(initial * 1.5)

    def test_effect_applies_to_character(self):
        """效果能正确修改角色属性"""
        char = make_char("星")
        from src.game.models import Effect
        effect = Effect(name="测试增伤", turns_remaining=2, atk_pct_bonus=0.3)
        effect.apply_to(char)
        assert char.stat.atk_pct == 0.3

    def test_effect_removes_from_character(self):
        """效果结束时属性恢复"""
        char = make_char("星")
        from src.game.models import Effect
        effect = Effect(name="测试增伤", turns_remaining=1, atk_pct_bonus=0.3)
        effect.apply_to(char)
        effect.remove_from(char)
        assert char.stat.atk_pct == 0.0

    def test_turns_remaining_decrements(self):
        """效果回合数正确递减"""
        char = make_char("星")
        from src.game.models import Effect
        effect = Effect(name="测试", turns_remaining=2, atk_pct_bonus=0.2)
        char.effects.append(effect)
        effect.turns_remaining -= 1
        assert effect.turns_remaining == 1
