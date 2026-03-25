"""战斗系统测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import json
import unittest
import random

from game import (
    Character, Element, Stat, Skill, SkillType,
    BattleState, BattleEngine, BattleEvent,
    ELEMENT_COUNTER,
    calculate_damage, apply_damage,
)
from game.battle import create_default_character
from game.skill import assign_default_skills


# ---------------------------------------------------------------------------
# 固定随机种子
# ---------------------------------------------------------------------------
random.seed(12345)


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------

def make_char(
    name="测试",
    element=Element.PHYSICAL,
    atk=100,
    hp=1000,
    spd=100,
    energy=0.0,
):
    c = Character(
        name=name,
        element=element,
        stat=Stat(max_hp=hp, atk=atk, def_=50, spd=spd, crit_rate=0.0, crit_dmg=1.5),
        current_hp=hp,
        current_energy=energy,
    )
    return c


def load_skills():
    base = os.path.join(os.path.dirname(__file__), "..", "data", "skills.json")
    with open(base, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 测试类
# ---------------------------------------------------------------------------

class TestSpeedSorting(unittest.TestCase):
    """速度排序测试"""

    def setUp(self):
        self.skills_data = load_skills()

    def test_high_spd_acts_first(self):
        """SPD 高的角色先行动"""
        fast = make_char(name="快", spd=200)
        slow = make_char(name="慢", spd=50)

        assign_default_skills(fast, self.skills_data)
        assign_default_skills(slow, self.skills_data)

        state = BattleState(player_team=[fast], enemy_team=[slow])
        engine = BattleEngine(state, self.skills_data)

        events = []
        engine.set_logger(lambda e: events.append(e))
        engine.start()

        # 找到第一个实际攻击事件（跳过 START 事件）
        attack_events = [e for e in events if e.action in ("BASIC", "SPECIAL", "ULT")]
        self.assertGreater(len(attack_events), 0)
        first_attacker = attack_events[0].actor.name
        self.assertEqual(first_attacker, "快", "SPD 高的角色应该先行动")

    def test_spd_order_multiple_chars(self):
        """多角色速度排序正确"""
        c1 = make_char(name="最慢", spd=30)
        c2 = make_char(name="中速", spd=100)
        c3 = make_char(name="最快", spd=200)

        for c in [c1, c2, c3]:
            assign_default_skills(c, self.skills_data)

        state = BattleState(player_team=[c1, c2], enemy_team=[c3])
        engine = BattleEngine(state, self.skills_data)

        events = []
        engine.set_logger(lambda e: events.append(e))
        engine.start()

        attack_events = [e for e in events if e.action in ("BASIC", "SPECIAL", "ULT")]
        self.assertGreater(len(attack_events), 0)

        names = [e.actor.name for e in attack_events]
        # 验证：最快不会出现在最慢之后
        fastest_i = names.index("最快") if "最快" in names else -1
        slowest_i = names.index("最慢") if "最慢" in names else -1
        if fastest_i >= 0 and slowest_i >= 0:
            self.assertLess(
                fastest_i, slowest_i,
                f"最快应该在最慢之前行动，实际顺序: {names}",
            )


class TestBattleEndConditions(unittest.TestCase):
    """战斗结束条件测试"""

    def setUp(self):
        self.skills_data = load_skills()

    def test_battle_ends_when_enemies_dead(self):
        """敌方全灭时战斗结束，胜利方为 player"""
        attacker = make_char(name="我方", atk=10000, hp=1000, spd=100)
        defender = make_char(name="敌方", hp=1, spd=50)  # 1 HP，一击必杀

        defender.stat.def_ = 0  # 无防御，确保被击杀
        assign_default_skills(attacker, self.skills_data)
        assign_default_skills(defender, self.skills_data)

        state = BattleState(player_team=[attacker], enemy_team=[defender])
        engine = BattleEngine(state, self.skills_data)

        result = engine.start()
        self.assertEqual(result, "🎉 胜利！")

    def test_battle_ends_when_player_dead(self):
        """己方全灭时战斗结束，胜利方为 enemy"""
        attacker = make_char(name="敌方", atk=50000, hp=1000, spd=100)
        defender = make_char(name="我方", hp=1, spd=50)

        defender.stat.def_ = 0
        assign_default_skills(attacker, self.skills_data)
        assign_default_skills(defender, self.skills_data)

        state = BattleState(player_team=[defender], enemy_team=[attacker])
        engine = BattleEngine(state, self.skills_data)

        result = engine.start()
        self.assertEqual(result, "💀 失败...")

    def test_battle_ends_when_both_sides_dead_same_turn(self):
        """双方同时全灭，先判定输赢"""
        # 这种边界情况，is_battle_over 的胜负判定与队伍顺序有关
        # 核心是确保不会无限循环
        p1 = make_char(name="我方1", atk=5000, hp=1, spd=200)
        e1 = make_char(name="敌方1", atk=5000, hp=1, spd=100)

        p1.stat.def_ = 0
        e1.stat.def_ = 0
        for c in [p1, e1]:
            assign_default_skills(c, self.skills_data)

        state = BattleState(player_team=[p1], enemy_team=[e1])
        engine = BattleEngine(state, self.skills_data)

        result = engine.start()
        self.assertIn(result, ["🎉 胜利！", "💀 失败..."])


class TestDeadCharacterCannotAct(unittest.TestCase):
    """HP 归零角色不能行动测试"""

    def setUp(self):
        self.skills_data = load_skills()

    def test_dead_character_skipped(self):
        """死亡的角色的 HP=0，不会出现在行动序列中参与行动"""
        alive = make_char(name="存活", hp=1000, spd=50)
        dead = make_char(name="已死亡", hp=0, spd=200)  # 速度高但已死亡

        assign_default_skills(alive, self.skills_data)
        assign_default_skills(dead, self.skills_data)

        state = BattleState(player_team=[dead], enemy_team=[alive])
        engine = BattleEngine(state, self.skills_data)

        events = []
        engine.set_logger(lambda e: events.append(e))
        engine.start()

        # 死亡角色不应该有攻击事件
        dead_attacks = [e for e in events if e.actor.name == "已死亡"
                        and e.action in ("BASIC", "SPECIAL", "ULT")]
        self.assertEqual(
            len(dead_attacks), 0,
            "死亡角色不应发动攻击",
        )

    def test_dead_character_not_in_alive_list(self):
        """is_alive() 正确区分存活/死亡"""
        alive = make_char(name="存活", hp=100)
        dead = make_char(name="死亡", hp=0)

        self.assertTrue(alive.is_alive())
        self.assertFalse(dead.is_alive())

    def test_hp_goes_to_zero_on_killing_blow(self):
        """受到致命伤害时 HP 归零（不能为负）"""
        target = make_char(name="目标", hp=50)
        target.stat.def_ = 0
        attacker = make_char(name="攻击方", atk=1000)

        from game.damage import calculate_damage, apply_damage
        result = calculate_damage(attacker, target, skill_multiplier=1.0)
        apply_damage(attacker, target, result)

        self.assertEqual(target.current_hp, 0)
        self.assertFalse(target.is_alive())


class TestBattleEngineCore(unittest.TestCase):
    """战斗引擎核心功能测试"""

    def setUp(self):
        self.skills_data = load_skills()

    def test_battle_event_logged(self):
        """战斗事件被正确记录"""
        p1 = make_char(name="我方1", hp=1000, spd=100)
        e1 = make_char(name="敌方1", hp=1000, spd=90)

        for c in [p1, e1]:
            assign_default_skills(c, self.skills_data)

        state = BattleState(player_team=[p1], enemy_team=[e1])
        engine = BattleEngine(state, self.skills_data)
        engine.start()

        self.assertGreater(len(engine.events), 0)
        event_types = {e.action for e in engine.events}
        self.assertIn("START", event_types)

    def test_multiple_rounds(self):
        """多回合战斗正常进行"""
        p1 = make_char(name="我方1", atk=50, hp=5000, spd=100)
        e1 = make_char(name="敌方1", atk=50, hp=5000, spd=90)

        for c in [p1, e1]:
            assign_default_skills(c, self.skills_data)

        state = BattleState(player_team=[p1], enemy_team=[e1])
        engine = BattleEngine(state, self.skills_data)
        engine.start()

        # 验证回合数 > 1（有多轮行动）
        max_turn = max(e.turn for e in engine.events)
        self.assertGreater(max_turn, 1, "战斗应该持续多个回合")

    def test_turn_counter_increments(self):
        """回合计数器正确递增"""
        p1 = make_char(name="我方", hp=5000, spd=100)
        e1 = make_char(name="敌方", hp=5000, spd=90)

        for c in [p1, e1]:
            assign_default_skills(c, self.skills_data)

        state = BattleState(player_team=[p1], enemy_team=[e1])
        engine = BattleEngine(state, self.skills_data)
        engine.start()

        turns = sorted({e.turn for e in engine.events})
        # START 事件 turn=0，之后战斗事件从 turn=1 开始
        non_zero_turns = [t for t in turns if t > 0]
        self.assertGreater(len(non_zero_turns), 0, "应该有 turn>0 的事件")
        self.assertEqual(non_zero_turns[0], 1, "第一个战斗回合应为 1")
        for i in range(1, len(non_zero_turns)):
            self.assertEqual(non_zero_turns[i], non_zero_turns[i - 1] + 1)


class TestElementCounter(unittest.TestCase):
    """元素克制测试"""

    def test_thunder_counters_wind(self):
        """雷攻击火：雷克制火（1.2x）。ELEMENT_COUNTER[THUNDER] = {FIRE}"""
        thunder = make_char(name="雷", element=Element.THUNDER, atk=100)
        fire = make_char(name="火", element=Element.FIRE, hp=1000)
        fire.stat.def_ = 0
        result = calculate_damage(thunder, fire, skill_multiplier=1.0)
        self.assertEqual(result.element_multiplier, 1.2, "雷攻击火应造成1.2x（雷克制火）")

    def test_fire_counters_ice(self):
        """火攻击冰：火克制冰（1.2x）。ELEMENT_COUNTER[FIRE] = {ICE}"""
        fire = make_char(name="火", element=Element.FIRE, atk=100)
        ice = make_char(name="冰", element=Element.ICE, hp=1000)
        ice.stat.def_ = 0
        result = calculate_damage(fire, ice, skill_multiplier=1.0)
        self.assertEqual(result.element_multiplier, 1.2, "火攻击冰应造成1.2x（火克制冰）")

    def test_counter_circle(self):
        """元素克制循环：ELEMENT_COUNTER[attacker] = {attacker 克制的元素}"""
        # 修正后的关系：key 克制 value，key 攻击 value 时获得 1.2x
        # 循环：物理 → 风 → 雷 → 火 → 冰 → 量子 → 虚数 → 物理
        # 即：物理克风，风克雷，雷克火，火克冰，冰克量子，量子克虚数，虚数克物理
        pairs = [
            (Element.PHYSICAL, Element.WIND),       # 物理克风
            (Element.WIND, Element.THUNDER),         # 风克雷
            (Element.THUNDER, Element.FIRE),         # 雷克火
            (Element.FIRE, Element.ICE),             # 火克冰
            (Element.ICE, Element.QUANTUM),          # 冰克量子
            (Element.QUANTUM, Element.IMAGINARY),   # 量子克虚数
            (Element.IMAGINARY, Element.PHYSICAL),  # 虚数克物理
        ]
        for attacker, defender in pairs:
            self.assertIn(
                defender,
                ELEMENT_COUNTER.get(attacker, set()),
                f"{attacker} 应该克制 {defender}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
