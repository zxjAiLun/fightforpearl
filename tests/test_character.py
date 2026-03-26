"""角色系统测试"""
import pytest
from src.game.character import (
    get_character_data,
    list_characters,
    create_character_from_preset,
)
from src.game.models import Character, Element, Stat


class TestCharacterData:
    def test_get_character_data(self):
        data = get_character_data("星")
        assert data is not None
        assert data["element"] == "PHYSICAL"

    def test_get_character_data_not_found(self):
        assert get_character_data("不存在") is None

    def test_list_characters(self):
        chars = list_characters()
        assert "星" in chars
        assert "丹恒" in chars
        assert "银狼" in chars


class TestCreateCharacter:
    def test_create_character_from_preset(self):
        char = create_character_from_preset("星")
        assert char.name == "星"
        assert char.element == Element.PHYSICAL
        assert char.is_alive()
        assert char.energy == char.energy_limit / 2

    def test_preset_has_passives(self):
        """预设角色应有2个默认被动"""
        char = create_character_from_preset("三月萤")
        assert len(char.passives) == 2
        passive_names = [p.name for p in char.passives]
        assert "战技·增伤" in passive_names
        assert "大招·加攻" in passive_names

    def test_character_current_hp_equals_max_hp(self):
        """新建角色 current_hp 应等于 max_hp"""
        char = create_character_from_preset("丹恒")
        assert char.current_hp == char.stat.total_max_hp()

    def test_take_damage(self):
        char = create_character_from_preset("星")
        char.take_damage(300)
        assert char.current_hp == char.stat.total_max_hp() - 300

    def test_heal(self):
        char = create_character_from_preset("星")
        char.take_damage(500)
        char.heal(200)
        assert char.current_hp == char.stat.total_max_hp() - 300

    def test_is_alive(self):
        char = create_character_from_preset("姬子")
        assert char.is_alive() is True
        char.take_damage(char.stat.total_max_hp())
        assert char.is_alive() is False


class TestStat:
    def test_total_atk_calculation(self):
        """ATK = (base_atk + flat) × (1 + pct)"""
        stat = Stat(base_atk=100, atk_pct=0.5, atk_flat=0)
        assert stat.total_atk() == 150

        stat2 = Stat(base_atk=100, atk_pct=0.3, atk_flat=20)
        assert stat2.total_atk() == 156

    def test_total_max_hp_calculation(self):
        stat = Stat(base_max_hp=1000, hp_pct=0.2)
        assert stat.total_max_hp() == 1200
