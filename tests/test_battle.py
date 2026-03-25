"""测试套件"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from game import (
    Character, Element, Stat,
    calculate_damage, apply_damage,
    BattleState, BattleEngine,
    ELEMENT_COUNTER,
)
from game.battle import create_default_character


def test_damage_formula():
    """测试伤害公式"""
    attacker = Character(name="Test", stat=Stat(atk=100, def_=30, spd=100, max_hp=1000))
    defender = Character(name="Enemy", stat=Stat(atk=50, def_=30, spd=90, max_hp=1000))

    result = calculate_damage(attacker, defender, skill_multiplier=1.0)

    assert result.final_damage >= 1, f"伤害应该 >= 1，实际 {result.final_damage}"
    assert result.def_reduction > 0, "防御应该减免伤害"
    assert result.def_reduction < 1, "防御减免应该 < 100%"
    print(f"✅ 伤害公式测试通过：{result.final_damage} 伤害 (暴击={result.is_crit})")


def test_crit_calculation():
    """测试暴击"""
    attacker = Character(name="Critter", stat=Stat(atk=200, crit_rate=1.0, crit_dmg=1.5))
    defender = Character(name="Tank", stat=Stat(def_=30, max_hp=5000))

    result = calculate_damage(attacker, defender, skill_multiplier=1.0)
    assert result.is_crit, "100% 暴击率应该触发暴击"
    assert result.crit_multiplier == 1.5, "暴击倍率应为 1.5"
    print(f"✅ 暴击测试通过：{result.final_damage} 伤害")


def test_element_counter():
    """测试元素克制"""
    thunder = Character(name="雷", element=Element.THUNDER, stat=Stat(atk=100))
    wind = Character(name="风", element=Element.WIND, stat=Stat(def_=30, max_hp=1000))

    result = calculate_damage(thunder, wind, skill_multiplier=1.0)
    assert result.element_multiplier == 1.2, f"雷克风，应为 1.2，实际 {result.element_multiplier}"
    print(f"✅ 元素克制测试通过：雷→风 = {result.element_multiplier}x")


def test_battle_engine():
    """测试战斗流程"""
    p1 = create_default_character("我方1")
    p2 = create_default_character("我方2")
    e1 = create_default_character("敌方1")

    state = BattleState(player_team=[p1, p2], enemy_team=[e1])
    engine = BattleEngine(state)
    result = engine.start()

    assert result in ["🎉 胜利！", "💀 失败..."], f"战斗结果应为 胜利/失败，实际 {result}"
    print(f"✅ 战斗流程测试通过：{result}")


if __name__ == "__main__":
    print("运行测试...")
    test_damage_formula()
    test_crit_calculation()
    test_element_counter()
    test_battle_engine()
    print("\n🎉 所有测试通过！")
