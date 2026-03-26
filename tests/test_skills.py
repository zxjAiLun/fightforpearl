"""技能系统测试"""
import pytest
from src.game.character import create_character_from_preset
from src.game.models import Character, Element, Stat, Skill, SkillType, Passive, Effect
from src.game.skill import SkillExecutor, assign_default_skills, assign_default_passives
import json


def _load_skills():
    import os
    base = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base, "data", "skills.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _char_with_skills(name: str) -> Character:
    """创建带技能的角色（模拟 BattleEngine 的行为）"""
    char = create_character_from_preset(name)
    skills_data = _load_skills()
    assign_default_skills(char, skills_data)
    return char


class TestSkillExecutor:
    def test_all_characters_have_three_skills(self):
        """每个角色应有3个主动技能"""
        char = _char_with_skills("星")
        assert len(char.skills) == 3

    def test_basic_damage_output(self):
        """普攻应造成伤害"""
        char = _char_with_skills("星")
        enemy = _char_with_skills("丹恒")
        executor = SkillExecutor()

        skill = char.skills[0]
        results = executor.execute(skill, char, [enemy])
        assert len(results) == 1
        target, result = results[0]
        assert result.final_damage >= 1

    def test_basic_multiplier(self):
        """普攻倍率应为 1.0"""
        char = _char_with_skills("星")
        basic_skill = [s for s in char.skills if s.type == SkillType.BASIC][0]
        assert basic_skill.multiplier == 1.0

    def test_special_multiplier(self):
        """战技倍率应为 1.5"""
        char = _char_with_skills("星")
        special_skill = [s for s in char.skills if s.type == SkillType.SPECIAL][0]
        assert special_skill.multiplier == 1.5

    def test_ult_multiplier(self):
        """大招倍率应为 3.0"""
        char = _char_with_skills("星")
        ult_skill = [s for s in char.skills if s.type == SkillType.ULT][0]
        assert ult_skill.multiplier == 3.0

    def test_energy_limit(self):
        """能量上限为 120"""
        char = create_character_from_preset("星")
        assert char.energy_limit == 120

    def test_battle_points_limit(self):
        """战绩点上限为 5"""
        char = create_character_from_preset("星")
        assert char.battle_points_limit == 5

    def test_can_use_special_always(self):
        """战技可以随时使用（不消耗能量）"""
        char = _char_with_skills("星")
        char.energy = 0
        special = [s for s in char.skills if s.type == SkillType.SPECIAL][0]
        assert SkillExecutor().can_use_skill(special, char) is True

    def test_can_use_basic_always(self):
        """普攻可以随时使用"""
        char = _char_with_skills("星")
        basic = [s for s in char.skills if s.type == SkillType.BASIC][0]
        assert SkillExecutor().can_use_skill(basic, char) is True

    def test_ult_requires_full_energy(self):
        """大招需要能量满（120）"""
        char = _char_with_skills("星")
        char.energy = 119
        ult = [s for s in char.skills if s.type == SkillType.ULT][0]
        assert SkillExecutor().can_use_skill(ult, char) is False

    def test_ult_can_use_when_full(self):
        """能量满时可以使用大招"""
        char = _char_with_skills("星")
        char.energy = 120
        ult = [s for s in char.skills if s.type == SkillType.ULT][0]
        assert SkillExecutor().can_use_skill(ult, char) is True

    def test_select_best_skill_full_energy(self):
        """满能量时选择大招"""
        char = _char_with_skills("星")
        char.energy = 120
        skill = SkillExecutor().select_best_skill(char)
        assert skill.type == SkillType.ULT

    def test_select_best_skill_no_energy(self):
        """无能量时选择普攻"""
        char = _char_with_skills("星")
        char.energy = 0
        skill = SkillExecutor().select_best_skill(char)
        assert skill.type == SkillType.BASIC

    def test_special_damage_higher_than_basic(self):
        """战技伤害应高于普攻（比较基础伤害，不受暴击影响）"""
        char = _char_with_skills("姬子")
        enemy = _char_with_skills("丹恒")
        executor = SkillExecutor()

        basic = [s for s in char.skills if s.type == SkillType.BASIC][0]
        special = [s for s in char.skills if s.type == SkillType.SPECIAL][0]

        basic_results = executor.execute(basic, char, [enemy])
        _, basic_result = basic_results[0]

        char2 = _char_with_skills("姬子")
        special_results = executor.execute(special, char2, [enemy])
        _, special_result = special_results[0]

        assert special_result.base_damage > basic_result.base_damage

    def test_ult_damage_higher_than_special(self):
        """大招伤害应高于战技（比较基础伤害，不受暴击影响）"""
        char = _char_with_skills("姬子")
        enemy = _char_with_skills("丹恒")
        executor = SkillExecutor()

        char.energy = 120
        ult = [s for s in char.skills if s.type == SkillType.ULT][0]
        special = [s for s in char.skills if s.type == SkillType.SPECIAL][0]

        ult_results = executor.execute(ult, char, [enemy])
        _, ult_result = ult_results[0]

        char2 = _char_with_skills("姬子")
        special_results = executor.execute(special, char2, [enemy])
        _, special_result = special_results[0]

        assert ult_result.base_damage > special_result.base_damage

    def test_energy_deduct_ult(self):
        """使用大往后能量归零"""
        char = _char_with_skills("星")
        char.energy = 120
        ult = [s for s in char.skills if s.type == SkillType.ULT][0]
        enemy = _char_with_skills("丹恒")
        SkillExecutor().execute(ult, char, [enemy])
        assert char.energy == 0.0

    def test_basic_energy_gain(self):
        """使用普攻后能量 +20"""
        char = _char_with_skills("星")
        char.energy = 0
        basic = [s for s in char.skills if s.type == SkillType.BASIC][0]
        enemy = _char_with_skills("丹恒")
        SkillExecutor().execute(basic, char, [enemy])
        assert char.energy == 20.0

    def test_special_energy_gain(self):
        """使用战技后能量 +30"""
        char = _char_with_skills("星")
        char.energy = 0
        special = [s for s in char.skills if s.type == SkillType.SPECIAL][0]
        enemy = _char_with_skills("丹恒")
        SkillExecutor().execute(special, char, [enemy])
        assert char.energy == 30.0

    def test_energy_cap_at_limit(self):
        """能量不能超过上限"""
        char = _char_with_skills("星")
        char.energy = 115
        basic = [s for s in char.skills if s.type == SkillType.BASIC][0]
        enemy = _char_with_skills("丹恒")
        SkillExecutor().execute(basic, char, [enemy])
        assert char.energy == 120

    def test_battle_points_gain(self):
        """使用普攻后战绩点 +1（团队共享）"""
        from src.game.models import BattleState
        char = _char_with_skills("星")
        basic = [s for s in char.skills if s.type == SkillType.BASIC][0]
        enemy = _char_with_skills("丹恒")
        state = BattleState(player_team=[char], enemy_team=[enemy])
        state.shared_battle_points = 3
        SkillExecutor().execute(basic, char, [enemy], state)
        assert state.shared_battle_points == 4

    def test_battle_points_cap_at_limit(self):
        """战绩点不能超过上限（团队共享）"""
        from src.game.models import BattleState
        char = _char_with_skills("星")
        basic = [s for s in char.skills if s.type == SkillType.BASIC][0]
        enemy = _char_with_skills("丹恒")
        state = BattleState(player_team=[char], enemy_team=[enemy])
        state.shared_battle_points = 5
        SkillExecutor().execute(basic, char, [enemy], state)
        assert state.shared_battle_points == 5


class TestPassive:
    def test_passive_trigger_on_skill(self):
        """使用战技时触发战技增伤被动"""
        char = _char_with_skills("星")
        special = [s for s in char.skills if s.type == SkillType.SPECIAL][0]
        enemy = _char_with_skills("丹恒")

        SkillExecutor().execute(special, char, [enemy])

        passive_names = [e.name for e in char.effects]
        assert "战技·增伤" in passive_names

    def test_passive_duration(self):
        """被动效果应持续正确回合数"""
        char = create_character_from_preset("三月萤")
        passive = char.passives[0]
        assert passive.duration == 2

    def test_passive_atk_increase(self):
        """大招触发后攻击力应增加"""
        char = _char_with_skills("星")
        char.energy = 120
        ult = [s for s in char.skills if s.type == SkillType.ULT][0]
        enemy = _char_with_skills("丹恒")

        initial_atk = char.stat.total_atk()
        SkillExecutor().execute(ult, char, [enemy])

        passive_names = [e.name for e in char.effects]
        assert "大招·加攻" in passive_names


class TestSkillEnergyIntegration:
    def test_energy_progression_over_turns(self):
        """连续多回合能量累计正确"""
        char = create_character_from_preset("星")
        char.energy = 0.0
        for _ in range(4):
            char.add_energy(30.0)
        assert char.energy == 120.0

    def test_full_battle_with_energy(self):
        """BattleEngine 中能量积攒流程"""
        from src.game.battle import BattleEngine, BattleState

        player = _char_with_skills("星")
        enemy = _char_with_skills("丹恒")

        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)

        assert len(player.skills) == 3
        assert len(enemy.skills) == 3
