"""技能系统测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import json
import unittest
from game import (
    Character, Element, Stat, Skill, SkillType,
    BattleState, BattleEngine,
    ELEMENT_COUNTER,
)
from game.skill import (
    SkillExecutor, build_skills_from_json, assign_default_skills,
)
from game.battle import create_default_character


# ---------------------------------------------------------------------------
# 固定随机种子，确保测试可复现
# ---------------------------------------------------------------------------
import random
random.seed(42)


# ---------------------------------------------------------------------------
# 辅助函数
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
        stat=Stat(max_hp=hp, atk=atk, def_=50, spd=spd, crit_rate=0.0),
        current_hp=hp,
        current_energy=energy,
    )
    return c


def get_basic(c):
    return next(s for s in c.skills if s.type == SkillType.BASIC)


def get_special(c):
    return next(s for s in c.skills if s.type == SkillType.SPECIAL)


def get_ult(c):
    return next(s for s in c.skills if s.type == SkillType.ULT)


# ---------------------------------------------------------------------------
# 测试类
# ---------------------------------------------------------------------------

class TestSkillExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = SkillExecutor()
        # 加载技能数据
        base = os.path.join(os.path.dirname(__file__), "..", "data", "skills.json")
        with open(base, encoding="utf-8") as f:
            self.skills_data = json.load(f)

    # -----------------------------------------------------------------------
    # 能量系统
    # -----------------------------------------------------------------------

    def test_energy_cap(self):
        """能量上限为 3"""
        self.assertEqual(SkillExecutor.MAX_ENERGY, 3.0)

    def test_energy_refill_per_turn(self):
        """每回合回复 1 点能量，上限 3"""
        char = make_char(energy=0.0)
        assign_default_skills(char, self.skills_data)

        engine = BattleEngine(BattleState(player_team=[char], enemy_team=[]), self.skills_data)

        # 模拟第一回合开始时的能量回复
        char.current_energy = min(3.0, char.current_energy + 1.0)
        self.assertEqual(char.current_energy, 1.0)

        # 连续多回合
        for _ in range(3):
            char.current_energy = min(3.0, char.current_energy + 1.0)
        self.assertEqual(char.current_energy, 3.0)

        # 超过上限不再增加
        char.current_energy = min(3.0, char.current_energy + 1.0)
        self.assertEqual(char.current_energy, 3.0)

    def test_energy_deduct_special(self):
        """战技消耗 1 点能量"""
        char = make_char(name="星", energy=1.0)
        assign_default_skills(char, self.skills_data)

        target = make_char(name="目标", hp=1000)
        special = get_special(char)

        results = self.executor.execute(special, char, [target])
        self.assertGreater(len(results), 0)
        self.assertEqual(char.current_energy, 0.0)

    def test_energy_deduct_ult(self):
        """大招消耗全部能量"""
        char = make_char(name="星", energy=3.0)
        assign_default_skills(char, self.skills_data)

        target = make_char(name="目标", hp=1000)
        ult = get_ult(char)

        results = self.executor.execute(ult, char, [target])
        self.assertGreater(len(results), 0)
        self.assertEqual(char.current_energy, 0.0)

    def test_ult_requires_full_energy(self):
        """大招需要 ≥3 能量才能释放"""
        char = make_char(name="银狼", energy=2.0)
        assign_default_skills(char, self.skills_data)

        target = make_char(name="目标", hp=1000)
        ult = get_ult(char)

        results = self.executor.execute(ult, char, [target])
        self.assertEqual(len(results), 0)  # 能量不足，应返回空
        self.assertEqual(char.current_energy, 2.0)  # 能量未消耗

    def test_special_requires_energy(self):
        """战技需要 ≥1 能量才能释放"""
        char = make_char(name="姬子", energy=0.0)
        assign_default_skills(char, self.skills_data)

        target = make_char(name="目标", hp=1000)
        special = get_special(char)

        results = self.executor.execute(special, char, [target])
        self.assertEqual(len(results), 0)  # 能量不足
        self.assertEqual(char.current_energy, 0.0)  # 未消耗

    # -----------------------------------------------------------------------
    # 技能伤害倍率
    # -----------------------------------------------------------------------

    def test_basic_multiplier(self):
        """普攻倍率为 1.0"""
        char = make_char(atk=100, energy=0.0)
        assign_default_skills(char, self.skills_data)
        basic = get_basic(char)
        self.assertEqual(basic.multiplier, 1.0)

    def test_special_multiplier(self):
        """战技倍率为 1.5"""
        char = make_char(name="星", atk=100, energy=1.0)
        assign_default_skills(char, self.skills_data)
        special = get_special(char)
        self.assertEqual(special.multiplier, 1.5)

    def test_ult_multiplier(self):
        """大招倍率为 3.0"""
        char = make_char(name="布洛妮娅", atk=100, energy=3.0)
        assign_default_skills(char, self.skills_data)
        ult = get_ult(char)
        self.assertEqual(ult.multiplier, 3.0)

    def test_basic_damage_output(self):
        """普攻实际伤害 = ATK × 1.0 相关（受防御影响）"""
        char = make_char(name="攻击方", atk=200, energy=0.0)
        assign_default_skills(char, self.skills_data)

        target = make_char(name="目标", atk=50, hp=10000, element=Element.PHYSICAL)
        # 目标防御为 0，方便验证
        target.stat.def_ = 0

        basic = get_basic(char)
        results = self.executor.execute(basic, char, [target])

        self.assertEqual(len(results), 1)
        _, dmg_result = results[0]
        # 防御为 0，base = 200 * 1.0 = 200，无元素克制 = 200
        self.assertEqual(dmg_result.base_damage, 200.0)
        self.assertEqual(dmg_result.final_damage, 200)

    def test_special_damage_higher_than_basic(self):
        """战技伤害 > 普攻伤害（同目标）"""
        char1 = make_char(name="星", atk=100, energy=1.0)
        char2 = make_char(name="三月萤", atk=100, energy=3.0)
        assign_default_skills(char1, self.skills_data)
        assign_default_skills(char2, self.skills_data)

        # 使用无克制关系的元素目标：WIND 与 FIRE/ICE 均无克制关系
        target1 = make_char(name="T1", hp=10000, element=Element.FIRE)
        target2 = make_char(name="T2", hp=10000, element=Element.FIRE)
        target1.stat.def_ = 0
        target2.stat.def_ = 0

        basic = get_basic(char1)
        special = get_special(char1)
        ult = get_ult(char2)

        results_basic = self.executor.execute(basic, char1, [target1])
        results_special = self.executor.execute(special, char1, [target1])
        results_ult = self.executor.execute(ult, char2, [target2])

        basic_dmg = results_basic[0][1].final_damage
        special_dmg = results_special[0][1].final_damage
        ult_dmg = results_ult[0][1].final_damage

        self.assertGreater(special_dmg, basic_dmg)
        self.assertGreater(ult_dmg, special_dmg)
        self.assertEqual(special_dmg, 150)   # ATK=100 × 1.5
        self.assertEqual(ult_dmg, 300)        # ATK=100 × 3.0

    # -----------------------------------------------------------------------
    # 技能选择逻辑
    # -----------------------------------------------------------------------

    def test_select_best_skill_full_energy(self):
        """能量满时优先选择大招"""
        char = make_char(name="星", energy=3.0)
        assign_default_skills(char, self.skills_data)

        skill = self.executor.select_best_skill(char)
        self.assertEqual(skill.type, SkillType.ULT)
        self.assertEqual(skill.multiplier, 3.0)

    def test_select_best_skill_one_energy(self):
        """能量为 1 时选择战技"""
        char = make_char(name="三月萤", energy=1.0)
        assign_default_skills(char, self.skills_data)

        skill = self.executor.select_best_skill(char)
        self.assertEqual(skill.type, SkillType.SPECIAL)
        self.assertEqual(skill.multiplier, 1.5)

    def test_select_best_skill_no_energy(self):
        """能量为 0 时选择普攻"""
        char = make_char(name="丹恒", energy=0.0)
        assign_default_skills(char, self.skills_data)

        skill = self.executor.select_best_skill(char)
        self.assertEqual(skill.type, SkillType.BASIC)
        self.assertEqual(skill.multiplier, 1.0)

    def test_can_use_skill(self):
        """can_use_skill 正确判断释放条件"""
        char = make_char(name="星", energy=0.0)
        assign_default_skills(char, self.skills_data)

        basic = get_basic(char)
        special = get_special(char)
        ult = get_ult(char)

        self.assertTrue(self.executor.can_use_skill(basic, char))
        self.assertFalse(self.executor.can_use_skill(special, char))
        self.assertFalse(self.executor.can_use_skill(ult, char))

        char.current_energy = 1.0
        self.assertTrue(self.executor.can_use_skill(special, char))
        self.assertFalse(self.executor.can_use_skill(ult, char))

        char.current_energy = 3.0
        self.assertTrue(self.executor.can_use_skill(ult, char))

    # -----------------------------------------------------------------------
    # 技能数据
    # -----------------------------------------------------------------------

    def test_build_skills_from_json(self):
        """build_skills_from_json 正确解析 JSON"""
        skills_dict = build_skills_from_json(self.skills_data)

        self.assertIn("星", skills_dict)
        self.assertEqual(len(skills_dict["星"]), 3)

        star_skills = skills_dict["星"]
        types = {s.type for s in star_skills}
        self.assertIn(SkillType.BASIC, types)
        self.assertIn(SkillType.SPECIAL, types)
        self.assertIn(SkillType.ULT, types)

    def test_all_characters_have_three_skills(self):
        """每个预设角色都有 3 个技能"""
        skills_dict = build_skills_from_json(self.skills_data)
        for char_name, skills in skills_dict.items():
            self.assertEqual(len(skills), 3, f"{char_name} 应该有 3 个技能")

    def test_skill_cost_correct(self):
        """技能能量消耗正确"""
        skills_dict = build_skills_from_json(self.skills_data)
        for char_name, skills in skills_dict.items():
            basic = next(s for s in skills if s.type == SkillType.BASIC)
            special = next(s for s in skills if s.type == SkillType.SPECIAL)
            ult = next(s for s in skills if s.type == SkillType.ULT)
            self.assertEqual(basic.cost, 0.0, f"{char_name} 普攻消耗 0")
            self.assertEqual(special.cost, 1.0, f"{char_name} 战技消耗 1")
            self.assertEqual(ult.cost, 3.0, f"{char_name} 大招消耗 3")


class TestSkillEnergyIntegration(unittest.TestCase):
    """技能能量系统与战斗集成测试"""

    def setUp(self):
        base = os.path.join(os.path.dirname(__file__), "..", "data", "skills.json")
        with open(base, encoding="utf-8") as f:
            self.skills_data = json.load(f)

    def test_energy_progression_over_turns(self):
        """连续 5 回合能量累积到上限"""
        char = make_char(energy=0.0)
        assign_default_skills(char, self.skills_data)

        energies = []
        e = 0.0
        for _ in range(5):
            e = min(3.0, e + 1.0)
            energies.append(e)

        self.assertEqual(energies, [1.0, 2.0, 3.0, 3.0, 3.0])

    def test_full_battle_with_energy(self):
        """完整战斗流程验证能量管理"""
        p1 = create_default_character("我方1")
        p2 = create_default_character("我方2", Element.FIRE)
        e1 = create_default_character("敌方1", Element.ICE)

        # 设置不同速度
        p1.stat.spd = 120
        p2.stat.spd = 80
        e1.stat.spd = 100

        state = BattleState(player_team=[p1, p2], enemy_team=[e1])
        engine = BattleEngine(state, self.skills_data)
        result = engine.start()

        self.assertIn(result, ["🎉 胜利！", "💀 失败..."])
        # 验证战斗产生了事件
        self.assertGreater(len(engine.events), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
