"""弱点击破系统测试"""
import pytest
from src.game.battle import BattleEngine, BattleState, create_enemy
from src.game.character import create_character_from_preset
from src.game.models import Element, BreakEffectType


# ============================================================
# 辅助函数
# ============================================================
def make_player(name: str = "星"):
    return create_character_from_preset(name)


def make_enemy(
    name: str = "敌人",
    weakness: list[Element] = None,
):
    if weakness is None:
        weakness = [Element.PHYSICAL]
    return create_enemy(
        name=name,
        level=50,
        hp_units=10.0,
        atk=100,
        defense=100,
        spd=90,
        weakness_elements=weakness,
    )


# ============================================================
# 击破触发
# ============================================================
class TestBreakTrigger:
    def test_break_triggers_on_weakness_hit(self):
        """攻击敌人弱点元素时触发击破"""
        player = make_player("三月萤")  # 风
        enemy = make_enemy("机械兵", [Element.WIND])

        # enemy韧性和弱点
        enemy.toughness = 0.0  # 削到0触发击破

        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)
        result = engine.start()

        # 验证击破事件被记录
        break_events = [e for e in engine.events if "击破" in e.detail or "裂伤" in e.detail or "灼烧" in e.detail or "风化" in e.detail]
        assert len(break_events) > 0

    def test_no_break_without_weakness(self):
        """攻击非弱点元素不触发击破"""
        player = make_player("星")  # 物理
        enemy = make_enemy("机械兵", [Element.ICE])  # 弱点是ICE，不是物理

        enemy.toughness = 0.0
        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)
        result = engine.start()

        break_events = [e for e in engine.events if "击破" in e.detail]
        assert len(break_events) == 0


# ============================================================
# 各元素击破效果
# ============================================================
class TestPhysicalBreak:
    def test_slash_deals_hp_percent_damage(self):
        """裂伤：按目标HP%造成DOT"""
        enemy = make_enemy("机械兵", [Element.PHYSICAL])
        enemy.toughness = 0.0
        enemy.current_hp = 1000

        player = make_player("星")
        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)

        # 手动触发击破
        br = state.apply_break(enemy, player, BreakEffectType.SLASH, Element.PHYSICAL)

        assert br.break_type == BreakEffectType.SLASH
        assert br.break_damage > 0
        assert br.dot_damage > 0  # HP%的DOT
        assert "裂伤" in br.detail

    def test_slash_dot_tick(self):
        """裂伤DOT触发"""
        enemy = make_enemy()
        enemy.current_hp = 1000
        player = make_player()

        state = BattleState(player_team=[player], enemy_team=[enemy])
        br = state.apply_break(enemy, player, BreakEffectType.SLASH, Element.PHYSICAL)

        # DOT每次触发造成HP%伤害
        status = state._break_status(enemy)
        initial_hp = enemy.current_hp
        dot_dmg = status.dot_tick()

        assert dot_dmg > 0


class TestFireBreak:
    def test_burn_creates_dot(self):
        """灼烧：火属性DOT"""
        enemy = make_enemy("机械兵", [Element.FIRE])
        player = make_player("姬子")  # 火
        enemy.toughness = 0.0

        state = BattleState(player_team=[player], enemy_team=[enemy])
        br = state.apply_break(enemy, player, BreakEffectType.BURN, Element.FIRE)

        assert br.break_type == BreakEffectType.BURN
        assert br.dot_damage > 0
        assert "灼烧" in br.detail


class TestIceBreak:
    def test_freeze_prevents_action(self):
        """冻结：角色无法行动"""
        player = make_player("三月萤")
        enemy = make_enemy("敌人", [Element.ICE])
        enemy.toughness = 0.0

        state = BattleState(player_team=[player], enemy_team=[enemy])
        br = state.apply_break(enemy, player, BreakEffectType.FREEZE, Element.ICE)

        assert br.break_type == BreakEffectType.FREEZE
        assert enemy.frozen_turns > 0
        assert enemy.can_act() is False
        assert "冻结" in br.detail


class TestThunderBreak:
    def test_shock_creates_dot(self):
        """触电：雷属性DOT"""
        player = make_player("丹恒")  # 雷
        enemy = make_enemy("机械兵", [Element.THUNDER])
        enemy.toughness = 0.0

        state = BattleState(player_team=[player], enemy_team=[enemy])
        br = state.apply_break(enemy, player, BreakEffectType.SHOCK, Element.THUNDER)

        assert br.break_type == BreakEffectType.SHOCK
        assert br.dot_damage > 0
        assert "触电" in br.detail


class TestWindBreak:
    def test_shear_stacks(self):
        """风化：可叠加"""
        player = make_player("三月萤")  # 风
        enemy = make_enemy("机械兵", [Element.WIND])
        enemy.toughness = 0.0

        state = BattleState(player_team=[player], enemy_team=[enemy])

        # 第一次击破
        br1 = state.apply_break(enemy, player, BreakEffectType.SHEAR, Element.WIND)
        status = state._break_status(enemy)
        assert status.dot.stacks == 1

        # 再次击破（叠加）
        br2 = state.apply_break(enemy, player, BreakEffectType.SHEAR, Element.WIND)
        status = state._break_status(enemy)
        assert status.dot.stacks == 2

        # 不超过3层
        br3 = state.apply_break(enemy, player, BreakEffectType.SHEAR, Element.WIND)
        br4 = state.apply_break(enemy, player, BreakEffectType.SHEAR, Element.WIND)
        assert status.dot.stacks == 3


class TestQuantumBreak:
    def test_entangle_delays_action(self):
        """纠缠：行动延后 + 下回合额外伤害"""
        player = make_player("银狼")  # 量子
        enemy = make_enemy("机械兵", [Element.QUANTUM])
        enemy.toughness = 0.0

        state = BattleState(player_team=[player], enemy_team=[enemy])
        br = state.apply_break(enemy, player, BreakEffectType.ENTANGLE, Element.QUANTUM)

        assert br.break_type == BreakEffectType.ENTANGLE
        assert enemy.action_delay > 0
        assert "纠缠" in br.detail

    def test_entangle_extra_damage_on_tick(self):
        """纠缠DOT：下回合触发额外量子伤害"""
        player = make_player("银狼")
        enemy = make_enemy()
        enemy.toughness = 0.0

        state = BattleState(player_team=[player], enemy_team=[enemy])
        br = state.apply_break(enemy, player, BreakEffectType.ENTANGLE, Element.QUANTUM)

        # tick触发额外伤害
        dot_results = state.tick_break_dots()
        assert len(dot_results) > 0


class TestImaginaryBreak:
    def test_imprision_delays_and_slows(self):
        """禁锢：行动延后 + 减速"""
        player = make_player("瓦尔特")  # 虚数
        enemy = make_enemy("机械兵", [Element.IMAGINARY])
        enemy.toughness = 0.0
        initial_spd_pct = enemy.stat.spd_pct

        state = BattleState(player_team=[player], enemy_team=[enemy])
        br = state.apply_break(enemy, player, BreakEffectType.IMPRISON, Element.IMAGINARY)

        assert br.break_type == BreakEffectType.IMPRISON
        assert enemy.action_delay > 0
        assert enemy.stat.spd_pct < initial_spd_pct  # 速度被降低


# ============================================================
# DOT生命周期
# ============================================================
class TestDotLifecycle:
    def test_dot_expires_after_duration(self):
        """DOT在持续回合结束后消失"""
        enemy = make_enemy()
        player = make_player()
        enemy.current_hp = 1000

        state = BattleState(player_team=[player], enemy_team=[enemy])
        br = state.apply_break(enemy, player, BreakEffectType.BURN, Element.FIRE)

        status = state._break_status(enemy)
        assert status.has_dot() is True

        # 触发2次
        status.dot.tick()
        assert status.has_dot() is True
        status.dot.tick()  # 持续2回合后消失
        assert status.has_dot() is False

    def test_tick_break_dots_returns_damage(self):
        """tick_break_dots 返回所有DOT伤害"""
        enemy1 = make_enemy("敌人1", [Element.FIRE])
        enemy2 = make_enemy("敌人2", [Element.THUNDER])
        player = make_player("姬子")

        for e in [enemy1, enemy2]:
            e.toughness = 0.0
            e.current_hp = 1000

        state = BattleState(player_team=[player], enemy_team=[enemy1, enemy2])
        state.apply_break(enemy1, player, BreakEffectType.BURN, Element.FIRE)
        state.apply_break(enemy2, player, BreakEffectType.SHOCK, Element.THUNDER)

        results = state.tick_break_dots()
        assert len(results) >= 1


# ============================================================
# 冻结状态
# ============================================================
class TestFreezeState:
    def test_frozen_character_skips_turn(self):
        """被冻结的角色跳过行动"""
        player = make_player()
        enemy = make_enemy()
        enemy.toughness = 0.0

        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)

        # 手动冻结
        state.apply_break(enemy, player, BreakEffectType.FREEZE, Element.ICE)

        # enemy被冻结，无法行动
        assert enemy.can_act() is False

    def test_freeze_expires_after_2_turns(self):
        """冻结2回合后自动解除"""
        enemy = make_enemy()
        player = make_player()

        state = BattleState(player_team=[player], enemy_team=[enemy])
        state.apply_break(enemy, player, BreakEffectType.FREEZE, Element.ICE)

        assert enemy.frozen_turns == 2
        enemy.end_turn_cleanup()  # 模拟回合结束
        assert enemy.frozen_turns == 1
        enemy.end_turn_cleanup()
        assert enemy.frozen_turns == 0
        assert enemy.can_act() is True
