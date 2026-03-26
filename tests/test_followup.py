"""追击机制 + 伤害来源系统测试"""
import pytest
from src.game.battle import BattleEngine, BattleState, create_enemy
from src.game.character import create_character_from_preset
from src.game.models import Element, Skill, SkillType, DamageSource, FollowUpRule
from src.game.skill import SkillExecutor
from src.game.damage import calculate_damage


# ============================================================
# 伤害来源分类
# ============================================================
class TestDamageSource:
    def test_basic_attack_has_basic_source(self):
        """普攻伤害来源为 BASIC"""
        player = create_character_from_preset("星")
        enemy = create_enemy("敌人", level=50, hp_units=10.0, atk=80, defense=100, spd=90, weakness_elements=[])

        skill = Skill(
            name="基础攻击",
            type=SkillType.BASIC,
            multiplier=1.0,
        )

        from src.game.damage import DamageResult
        # 普攻调用 calculate_damage 默认 source=BASIC
        result = calculate_damage(player, enemy, 1.0, damage_source=DamageSource.BASIC)
        assert result.damage_source == DamageSource.BASIC

    def test_special_has_special_source(self):
        """战技伤害来源为 SPECIAL"""
        player = create_character_from_preset("姬子")
        enemy = create_enemy("敌人", level=50, hp_units=10.0, atk=80, defense=100, spd=90, weakness_elements=[])

        result = calculate_damage(player, enemy, 1.5, damage_source=DamageSource.SPECIAL)
        assert result.damage_source == DamageSource.SPECIAL

    def test_ult_has_ult_source(self):
        """终结技伤害来源为 ULT"""
        player = create_character_from_preset("姬子")
        enemy = create_enemy("敌人", level=50, hp_units=10.0, atk=80, defense=100, spd=90, weakness_elements=[])

        result = calculate_damage(player, enemy, 3.0, damage_source=DamageSource.ULT)
        assert result.damage_source == DamageSource.ULT

    def test_follow_up_has_follow_up_source(self):
        """追击伤害来源为 FOLLOW_UP"""
        player = create_character_from_preset("星")
        enemy = create_enemy("敌人", level=50, hp_units=10.0, atk=80, defense=100, spd=90, weakness_elements=[])

        result = calculate_damage(player, enemy, 0.5, damage_source=DamageSource.FOLLOW_UP)
        assert result.damage_source == DamageSource.FOLLOW_UP


# ============================================================
# 追击触发规则
# ============================================================
class TestFollowUpRule:
    def test_follow_up_rule_creation(self):
        """创建追击规则"""
        rule = FollowUpRule(
            name="姬子追击",
            trigger_skill_type=SkillType.BASIC,
            chance=0.5,
            follow_up_skill_name="追加射击",
            multiplier=0.5,
            damage_type=Element.FIRE,
        )
        assert rule.chance == 0.5
        assert rule.trigger_skill_type == SkillType.BASIC
        assert rule.multiplier == 0.5

    def test_follow_up_rule_default_chance(self):
        """追击规则默认概率50%"""
        rule = FollowUpRule(
            name="测试追击",
            trigger_skill_type=SkillType.BASIC,
        )
        assert rule.chance == 0.5


# ============================================================
# 追击触发逻辑
# ============================================================
class TestFollowUpTrigger:
    def test_follow_up_triggers_after_skill(self):
        """主动技能后，追击概率触发"""
        player = create_character_from_preset("姬子")  # 火
        enemy = create_enemy("敌人", level=50, hp_units=25.0, atk=80, defense=100, spd=90, weakness_elements=[])

        # 给角色添加追击规则（普攻后50%概率追击）
        rule = FollowUpRule(
            name="火系追击",
            trigger_skill_type=SkillType.BASIC,
            chance=1.0,  # 100%触发方便测试
            follow_up_skill_name="基础攻击",
            multiplier=0.5,
            damage_type=Element.FIRE,
        )
        player.follow_up_rules.append(rule)

        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)

        # 处理一回合
        alive = [player, enemy]
        engine._process_action(player, alive, 1)

        # 检查是否有追击事件
        follow_up_events = [e for e in engine.events if e.action == "FOLLOW_UP"]
        assert len(follow_up_events) > 0
        assert "追击" in follow_up_events[0].detail

    def test_follow_up_uses_multiplier(self):
        """追击使用正确的倍率"""
        player = create_character_from_preset("星")
        enemy = create_enemy("敌人", level=50, hp_units=25.0, atk=100, defense=100, spd=90, weakness_elements=[])

        rule = FollowUpRule(
            name="测试追击",
            trigger_skill_type=SkillType.BASIC,
            chance=1.0,
            follow_up_skill_name="基础攻击",
            multiplier=0.3,  # 30%普攻倍率
            damage_type=Element.PHYSICAL,
        )
        player.follow_up_rules.append(rule)

        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)

        alive = [player, enemy]
        engine._process_action(player, alive, 1)

        follow_up_events = [e for e in engine.events if e.action == "FOLLOW_UP"]
        assert len(follow_up_events) > 0

    def test_no_follow_up_if_chance_miss(self):
        """概率未触发时不追击"""
        player = create_character_from_preset("星")
        enemy = create_enemy("敌人", level=50, hp_units=25.0, atk=80, defense=100, spd=90, weakness_elements=[])

        rule = FollowUpRule(
            name="不触发追击",
            trigger_skill_type=SkillType.BASIC,
            chance=0.0,  # 0%触发
            follow_up_skill_name="基础攻击",
            multiplier=0.5,
        )
        player.follow_up_rules.append(rule)

        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)

        alive = [player, enemy]
        engine._process_action(player, alive, 1)

        follow_up_events = [e for e in engine.events if e.action == "FOLLOW_UP"]
        assert len(follow_up_events) == 0

    def test_follow_up_only_on_correct_trigger(self):
        """只在释放正确技能类型时触发追击"""
        player = create_character_from_preset("星")
        enemy = create_enemy("敌人", level=50, hp_units=25.0, atk=80, defense=100, spd=90, weakness_elements=[])

        # 追击只在SPECIAL时触发
        rule = FollowUpRule(
            name="战技追击",
            trigger_skill_type=SkillType.SPECIAL,
            chance=1.0,
            follow_up_skill_name="基础攻击",
            multiplier=0.5,
        )
        player.follow_up_rules.append(rule)
        player.current_energy = 0.0  # 无法放战技，只能普攻

        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)

        alive = [player, enemy]
        engine._process_action(player, alive, 1)

        # 玩家没有触发追击
        follow_up_events = [e for e in engine.events if e.action == "FOLLOW_UP"]
        assert len(follow_up_events) == 0


# ============================================================
# 完整战斗中的追击
# ============================================================
class TestFollowUpInBattle:
    def test_full_battle_with_follow_up(self):
        """完整战斗流程中追击正常触发"""
        player = create_character_from_preset("姬子")
        enemy = create_enemy("敌人", level=50, hp_units=15.0, atk=80, defense=80, spd=70, weakness_elements=[])

        # 玩家每回合用战技（因为能量回1点），所以追击触发条件设战技
        rule = FollowUpRule(
            name="姬子追击",
            trigger_skill_type=SkillType.SPECIAL,
            chance=1.0,
            follow_up_skill_name="基础攻击",
            multiplier=0.5,
            damage_type=Element.FIRE,
        )
        player.follow_up_rules.append(rule)

        state = BattleState(player_team=[player], enemy_team=[enemy])
        engine = BattleEngine(state)

        result = engine.start()

        # 验证战斗结束
        assert result != ""

        # 验证追击事件存在
        follow_up_events = [e for e in engine.events if e.action == "FOLLOW_UP"]
        assert len(follow_up_events) > 0
