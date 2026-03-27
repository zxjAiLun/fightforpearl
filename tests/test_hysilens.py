"""海瑟音 (Hysilens) 角色测试"""
import pytest
from src.game.battle import BattleEngine, BattleState
from src.game.character import create_character_from_preset
from src.game.character_skills.hysilens import (
    HysilensBarrierModifier,
    HysilensTalentSystem,
    HysilensDotType,
    create_all_hysilens_skills,
)
from src.game.models import Element, BreakEffectType, BreakDot


def make_hysilens():
    return create_character_from_preset("海瑟音")


def make_enemy(name="敌人", weakness=None):
    if weakness is None:
        weakness = [Element.PHYSICAL]
    from src.game.battle import create_enemy
    return create_enemy(name=name, level=50, hp_units=10.0, atk=100, defense=100, spd=90, weakness_elements=weakness)


# ============================================================
# 角色加载测试
# ============================================================
class TestHysilensLoad:
    def test_hysilens_character_loads(self):
        """海瑟音角色可以正确加载"""
        h = make_hysilens()
        assert h.name == "海瑟音"
        assert h.element == Element.PHYSICAL
        assert h.stat.total_atk() > 2000
        assert h.stat.total_max_hp() >= 4000

    def test_hysilens_has_all_skills(self):
        """海瑟音拥有所有技能"""
        h = make_hysilens()
        skill_names = [s.name for s in h.skills]
        assert "小调，止水中回响" in skill_names  # 普攻
        assert "泛音，暗流后齐鸣" in skill_names  # 战技
        assert "绝海回涛，噬魂舞曲" in skill_names  # 终结技
        assert "海妖在欢唱" in skill_names  # 天赋
        assert "于海的栖息地" in skill_names  # 秘技

    def test_hysilens_has_passives(self):
        """海瑟音拥有行迹被动"""
        h = make_hysilens()
        passive_names = [p.name for p in h.passives]
        assert "征服的剑旗" in passive_names  # A2
        assert "盛会的泡沫" in passive_names  # A4
        assert "珍珠的琴弦" in passive_names  # A6


# ============================================================
# 结界机制测试
# ============================================================
class TestBarrierMechanics:
    def test_barrier_creation(self):
        """结界可以正确创建"""
        h = make_hysilens()
        enemy = make_enemy()
        barrier = HysilensBarrierModifier(owner=h, max_triggers=8, dot_damage_mult=0.32, duration=3)
        barrier.add_enemy(enemy)
        
        assert barrier.duration == 3
        assert barrier.is_active is True
        assert len(barrier._enemies_in_barrier) == 1

    def test_barrier_trigger(self):
        """结界可以触发追加DOT"""
        h = make_hysilens()
        enemy = make_enemy()
        barrier = HysilensBarrierModifier(owner=h, max_triggers=8, dot_damage_mult=0.32, duration=3)
        barrier.add_enemy(enemy)
        
        triggered, dmg = barrier.trigger_dot(enemy, "灼烧")
        assert triggered is True
        assert dmg == int(h.stat.total_atk() * 0.32)
        assert barrier._trigger_counts[id(enemy)] == 1

    def test_barrier_max_triggers(self):
        """结界有最大触发次数限制"""
        h = make_hysilens()
        enemy = make_enemy()
        barrier = HysilensBarrierModifier(owner=h, max_triggers=8, dot_damage_mult=0.32, duration=3)
        barrier.add_enemy(enemy)
        
        for _ in range(10):
            barrier.trigger_dot(enemy, "灼烧")
        
        assert barrier._trigger_counts[id(enemy)] == 8

    def test_barrier_enemy_not_in_barrier(self):
        """不在结界内的敌人不会触发追加DOT"""
        h = make_hysilens()
        enemy1 = make_enemy("敌人1")
        enemy2 = make_enemy("敌人2")
        barrier = HysilensBarrierModifier(owner=h, max_triggers=8, dot_damage_mult=0.32, duration=3)
        barrier.add_enemy(enemy1)
        
        triggered, _ = barrier.trigger_dot(enemy2, "灼烧")
        assert triggered is False

    def test_barrier_duration_decrements(self):
        """结界持续时间每回合递减"""
        h = make_hysilens()
        enemy = make_enemy()
        barrier = HysilensBarrierModifier(owner=h, max_triggers=8, dot_damage_mult=0.32, duration=3)
        barrier.add_enemy(enemy)
        
        assert barrier.duration == 3
        barrier.on_tick()
        assert barrier.duration == 2
        barrier.on_tick()
        assert barrier.duration == 1
        barrier.on_tick()
        assert barrier.is_active is False


# ============================================================
# 天赋DOT系统测试
# ============================================================
class TestTalentDOTSystem:
    def test_dot_manager_apply(self):
        """DOT管理器可以施加DOT"""
        h = make_hysilens()
        enemy = make_enemy()
        state = BattleState(player_team=[h], enemy_team=[enemy])
        talent_sys = HysilensTalentSystem(h, state)
        
        talent_sys.dot_manager.apply_dot(enemy, h, HysilensDotType.WOUND, 100, 2)
        assert talent_sys.dot_manager.has_dot_type(enemy, HysilensDotType.WOUND) is True

    def test_dot_stacking(self):
        """同类型DOT可以叠加（最多2层）"""
        h = make_hysilens()
        enemy = make_enemy()
        state = BattleState(player_team=[h], enemy_team=[enemy])
        talent_sys = HysilensTalentSystem(h, state)
        
        talent_sys.dot_manager.apply_dot(enemy, h, HysilensDotType.WOUND, 100, 2)
        talent_sys.dot_manager.apply_dot(enemy, h, HysilensDotType.WOUND, 100, 2)
        
        dot = talent_sys.dot_manager._dots[id(enemy)][HysilensDotType.WOUND]
        assert dot.stacks == 2

    def test_laceration_dot_tag(self):
        """裂伤DOT有正确的tag"""
        h = make_hysilens()
        enemy = make_enemy()
        state = BattleState(player_team=[h], enemy_team=[enemy])
        talent_sys = HysilensTalentSystem(h, state)
        
        talent_sys.dot_manager.apply_dot(enemy, h, HysilensDotType.WOUND, 100, 2)
        
        dot = talent_sys.dot_manager._dots[id(enemy)][HysilensDotType.WOUND]
        assert dot.dot_tag == "laceration"
        assert dot.laceration_cap == int(h.stat.total_atk() * 0.10)

    def test_different_dot_types_coexist(self):
        """不同类型DOT可以共存"""
        h = make_hysilens()
        enemy = make_enemy()
        state = BattleState(player_team=[h], enemy_team=[enemy])
        talent_sys = HysilensTalentSystem(h, state)
        
        talent_sys.dot_manager.apply_dot(enemy, h, HysilensDotType.WOUND, 100, 2)
        talent_sys.dot_manager.apply_dot(enemy, h, HysilensDotType.FIRE, 50, 2)
        
        assert talent_sys.dot_manager.get_dot_count(enemy) == 2


# ============================================================
# 战斗流程测试
# ============================================================
class TestBattleIntegration:
    def test_battle_with_hysilens(self):
        """海瑟音可以参与战斗"""
        h = make_hysilens()
        enemy = make_enemy()
        state = BattleState(player_team=[h], enemy_team=[enemy])
        engine = BattleEngine(state)
        
        result = engine.start()
        assert result in ["Victory!", "Defeat..."]
        assert len(engine.events) > 0

    def test_a2_barrier_on_battle_start(self):
        """海瑟音A2被动：战斗开始时展开结界"""
        h = make_hysilens()
        enemy1 = make_enemy("敌人1")
        enemy2 = make_enemy("敌人2")
        state = BattleState(player_team=[h], enemy_team=[enemy1, enemy2])
        engine = BattleEngine(state)
        
        # 触发天赋系统初始化和A2结界
        engine._ensure_hysilens_talent_system()
        engine._apply_hysilens_a2_barrier()
        
        assert len(state.hysilens_barriers) == 1
        barrier = state.hysilens_barriers[0]
        assert barrier.duration == 3
        assert len(barrier._enemies_in_barrier) == 2

    def test_talent_triggers_on_ally_attack(self):
        """海瑟音天赋：盟友攻击时触发DOT"""
        h = make_hysilens()
        enemy = make_enemy()
        state = BattleState(player_team=[h], enemy_team=[enemy])
        
        talent_sys = HysilensTalentSystem(h, state)
        applied = talent_sys.on_ally_attack(h, enemy)
        
        assert len(applied) == 1
        assert applied[0] in [
            HysilensDotType.WOUND,
            HysilensDotType.WIND,
            HysilensDotType.FIRE,
            HysilensDotType.THUNDER,
        ]
