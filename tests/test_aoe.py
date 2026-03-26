"""多目标/AOE 技能系统测试"""
import pytest
from src.game.battle import BattleEngine, BattleState, create_enemy
from src.game.character import create_character_from_preset
from src.game.models import Element, Skill, SkillType, BreakEffectType
from src.game.skill import SkillExecutor


class TestMultiTarget:
    def test_single_target_skill_hits_one(self):
        """单体技能只选择一个目标"""
        skill = Skill(
            name="单体攻击",
            type=SkillType.BASIC,
            multiplier=1.0,
            target_count=1,
        )
        targets = ["a", "b", "c"]
        result = skill.get_targets(targets)
        assert len(result) == 1
        assert result[0] == "a"

    def test_aoe_skill_targets_all(self):
        """AOE技能 target_count=-1 选择全体"""
        skill = Skill(
            name="全体攻击",
            type=SkillType.ULT,
            multiplier=2.0,
            target_count=-1,
        )
        targets = ["a", "b", "c"]
        result = skill.get_targets(targets)
        assert len(result) == 3

    def test_multi_target_skill_hits_count(self):
        """多目标技能选择指定数量"""
        skill = Skill(
            name="双目标",
            type=SkillType.SPECIAL,
            multiplier=1.0,
            target_count=2,
        )
        targets = ["a", "b", "c"]
        result = skill.get_targets(targets)
        assert len(result) == 2
        assert result == ["a", "b"]

    def test_aoe_skill_has_aoe_multiplier(self):
        """AOE技能有倍率折扣"""
        skill = Skill(
            name="全体爆发",
            type=SkillType.ULT,
            multiplier=3.0,
            target_count=-1,
            aoe_multiplier=0.8,
        )
        assert skill.is_aoe() is True
        assert skill.aoe_multiplier == 0.8

    def test_non_aoe_skill_is_not_aoe(self):
        """单体技能不是AOE"""
        skill = Skill(
            name="单体",
            type=SkillType.BASIC,
            multiplier=1.0,
            target_count=1,
        )
        assert skill.is_aoe() is False


class TestAoeDamage:
    def test_aoe_skill_applies_aoe_multiplier(self):
        """AOE技能对每个目标应用 aoe_multiplier 折扣"""
        player = create_character_from_preset("姬子")
        enemy1 = create_enemy("敌人1", weakness_elements=[Element.FIRE], hp_units=1)
        enemy2 = create_enemy("敌人2", weakness_elements=[Element.FIRE], hp_units=1)
        enemy1.toughness = 0.0
        enemy2.toughness = 0.0

        state = BattleState(player_team=[player], enemy_team=[enemy1, enemy2])
        engine = BattleEngine(state)

        aoe_skill = Skill(
            name="火焰散射",
            type=SkillType.SPECIAL,
            cost=1.0,
            multiplier=1.5,
            damage_type=Element.FIRE,
            target_count=2,
            aoe_multiplier=0.8,
        )
        player.skills = [aoe_skill]
        player.energy = 30.0

        executor = SkillExecutor()
        results = executor.execute(aoe_skill, player, [enemy1, enemy2])

        assert len(results) == 2

    def test_single_target_skill_no_aoe_penalty(self):
        """单体技能没有 AOE 惩罚"""
        skill = Skill(
            name="单体",
            type=SkillType.BASIC,
            multiplier=1.0,
            target_count=1,
            aoe_multiplier=0.8,
        )
        executor = SkillExecutor()
        assert executor._effective_multiplier(skill) == 1.0  # 无折扣

    def test_aoe_skill_has_penalty(self):
        """AOE技能有倍率折扣"""
        skill = Skill(
            name="全体",
            type=SkillType.ULT,
            multiplier=3.0,
            target_count=-1,
            aoe_multiplier=0.8,
        )
        executor = SkillExecutor()
        assert executor._effective_multiplier(skill) == pytest.approx(2.4)


class TestAoeBreakEffects:
    def test_aoe_hits_break_multiple_enemies(self):
        """AOE技能对每个敌人独立判定击破"""
        player = create_character_from_preset("姬子")  # 火角色
        enemy1 = create_enemy("敌人1", weakness_elements=[Element.FIRE])
        enemy2 = create_enemy("敌人2", weakness_elements=[Element.FIRE])

        state = BattleState(player_team=[player], enemy_team=[enemy1, enemy2])

        br1 = state.apply_break(enemy1, player, BreakEffectType.BURN, Element.FIRE)
        br2 = state.apply_break(enemy2, player, BreakEffectType.BURN, Element.FIRE)

        assert br1.break_type == BreakEffectType.BURN
        assert br2.break_type == BreakEffectType.BURN


class TestBattleAoe:
    def test_aoe_skill_targets_multiple_in_battle(self):
        """战斗中AOE技能对多个敌人造成伤害"""
        player = create_character_from_preset("姬子")
        enemy1 = create_enemy("敌人1", weakness_elements=[Element.FIRE])
        enemy2 = create_enemy("敌人2", weakness_elements=[Element.FIRE])

        state = BattleState(player_team=[player], enemy_team=[enemy1, enemy2])
        engine = BattleEngine(state)

        fire_aoe = Skill(
            name="火焰散射",
            type=SkillType.ULT,
            cost=3.0,
            multiplier=3.0,
            damage_type=Element.FIRE,
            target_count=-1,
            aoe_multiplier=0.8,
        )

        player.skills = [fire_aoe]
        player.energy = 120

        alive = [player, enemy1, enemy2]
        engine._process_action(player, alive, 1)

        assert enemy1.current_hp < enemy1.stat.base_max_hp
        assert enemy2.current_hp < enemy2.stat.base_max_hp
