"""刻律德菈角色测试"""
import pytest
from src.game.character import create_character_from_preset
from src.game.models import Character, Element, BattleState, Stat
from src.game.character_skills.celydra import (
    _get_celydra_state,
    apply_military_merit,
    apply_charge,
    upgrade_to_noble_title,
    remove_noble_title,
    MOD_MILITARY_MERIT,
    MOD_NOBLE_TITLE,
    create_celydra_special_skill,
    create_celydra_basic_skill,
    trigger_follow_up_damage,
)


class TestCelydraBasic:
    """测试刻律德菈基本属性"""

    def test_celydra_element_is_wind(self):
        char = create_character_from_preset("刻律德菈")
        assert char.element == Element.WIND

    def test_celydra_energy_limit(self):
        char = create_character_from_preset("刻律德菈")
        assert char.energy_limit == 130

    def test_celydra_has_three_skills(self):
        char = create_character_from_preset("刻律德菈")
        assert len(char.skills) == 3

    def test_celydra_basic_skill_is_wind(self):
        char = create_character_from_preset("刻律德菈")
        basic = char.skills[0]
        assert basic.damage_type == Element.WIND
        assert basic.type.value == 1  # BASIC


class TestMilitaryMeritState:
    """测试军功/爵位状态机"""

    def test_charge_starts_at_zero(self):
        caster = create_character_from_preset("刻律德菈")
        ally = create_character_from_preset("星")
        state = _get_celydra_state(caster)
        assert state.charge == 0

    def test_apply_charge_increases_charge(self):
        caster = create_character_from_preset("刻律德菈")
        ally = create_character_from_preset("星")
        state = _get_celydra_state(caster)
        gained = apply_charge(caster, 1)
        assert gained == 1
        assert state.charge == 1

    def test_charge_max_8(self):
        caster = create_character_from_preset("刻律德菈")
        ally = create_character_from_preset("星")
        apply_military_merit(caster, ally)
        # Fill to max
        apply_charge(caster, 8)
        state = _get_celydra_state(caster)
        assert state.charge == 8

    def test_charge_at_6_upgrades_to_noble_title(self):
        caster = create_character_from_preset("刻律德菈")
        ally = create_character_from_preset("星")
        
        # Create battle state
        battle_state = BattleState(
            player_team=[caster, ally],
            enemy_team=[],
        )
        caster._battle_state = battle_state
        ally._battle_state = battle_state
        
        apply_military_merit(caster, ally)
        apply_charge(caster, 6)
        
        state = _get_celydra_state(caster)
        assert state.is_noble_title is True
        assert state.charge == 6

    def test_military_merit_attack_bonus(self):
        caster = create_character_from_preset("刻律德菈")
        ally = create_character_from_preset("星")
        
        apply_military_merit(caster, ally)
        
        # Check ally has the military merit modifier
        has_merit = ally.modifier_manager.has_modifier(f"{MOD_MILITARY_MERIT}-{ally.name}")
        assert has_merit is True

    def test_noble_title_removal_consumes_charge(self):
        caster = create_character_from_preset("刻律德菈")
        ally = create_character_from_preset("星")
        
        battle_state = BattleState(
            player_team=[caster, ally],
            enemy_team=[],
        )
        caster._battle_state = battle_state
        ally._battle_state = battle_state
        
        apply_military_merit(caster, ally)
        apply_charge(caster, 6)  # upgrade to noble title
        
        state = _get_celydra_state(caster)
        assert state.is_noble_title is True
        
        # Remove noble title (should consume 6 charge)
        remove_noble_title(caster, ally)
        assert state.is_noble_title is False
        assert state.charge == 0


class TestCelydraSkills:
    """测试刻律德菈技能"""

    def test_basic_skill_multiplier(self):
        basic = create_celydra_basic_skill()
        assert basic.multiplier == 1.0
        assert basic.damage_type == Element.WIND

    def test_special_skill_is_support(self):
        special = create_celydra_special_skill()
        assert special.is_support_skill is True
        assert special.cost == 1

    def test_special_skill_no_damage(self):
        special = create_celydra_special_skill()
        assert special.multiplier == 0.0


class TestFollowUpDamage:
    """测试军功附加伤害"""

    def test_follow_up_consumes_hits(self):
        caster = create_character_from_preset("刻律德菈")
        ally = create_character_from_preset("星")
        enemy = create_character_from_preset("姬子")
        enemy.is_enemy = True
        enemy.stat.base_atk = 500
        enemy.stat.base_def = 200
        
        battle_state = BattleState(
            player_team=[caster, ally],
            enemy_team=[enemy],
        )
        caster._battle_state = battle_state
        ally._battle_state = battle_state
        enemy._battle_state = battle_state
        
        state = _get_celydra_state(caster)
        assert state.follow_up_hits_remaining == 20
        
        results = trigger_follow_up_damage(caster, ally, battle_state)
        assert len(results) > 0
        assert state.follow_up_hits_remaining == 19

    def test_follow_up_exhausted_returns_empty(self):
        caster = create_character_from_preset("刻律德菈")
        ally = create_character_from_preset("星")
        enemy = create_character_from_preset("姬子")
        enemy.is_enemy = True
        
        battle_state = BattleState(
            player_team=[caster, ally],
            enemy_team=[enemy],
        )
        caster._battle_state = battle_state
        ally._battle_state = battle_state
        enemy._battle_state = battle_state
        
        state = _get_celydra_state(caster)
        state.follow_up_hits_remaining = 0
        
        results = trigger_follow_up_damage(caster, ally, battle_state)
        assert len(results) == 0


class TestCelydraSurpriseAttack:
    """测试奇袭机制"""

    def test_noble_special_triggers_once(self):
        caster = create_character_from_preset("刻律德菈")
        ally = create_character_from_preset("星")
        
        battle_state = BattleState(
            player_team=[caster, ally],
            enemy_team=[],
        )
        caster._battle_state = battle_state
        ally._battle_state = battle_state
        
        state = _get_celydra_state(caster)
        
        # Simulate noble title
        state.charge = 6
        state.is_noble_title = True
        state.noble_special_surprise_triggered = False
        
        assert state.noble_special_surprise_triggered is False
