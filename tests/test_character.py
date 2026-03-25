"""角色系统测试"""
import pytest
from src.game.character import (
    StatAllocator, get_preset, list_presets,
    create_character_from_preset, create_custom_character,
)
from src.game.models import Character, Element, Stat


class TestPresets:
    def test_get_preset(self):
        p = get_preset("星")
        assert p is not None
        assert p["element"] == Element.PHYSICAL

    def test_get_preset_not_found(self):
        assert get_preset("不存在") is None

    def test_list_presets(self):
        presets = list_presets()
        assert "星" in presets
        assert "丹恒" in presets
        assert "银狼" in presets

    def test_create_character_from_preset(self):
        char = create_character_from_preset("星")
        assert char.name == "星"
        assert char.element == Element.PHYSICAL
        assert char.is_alive()
        assert char.current_energy == 0.0

    def test_preset_has_passives(self):
        """预设角色应有2个默认被动"""
        char = create_character_from_preset("三月萤")
        assert len(char.passives) == 2
        passive_names = [p.name for p in char.passives]
        assert "战技·增伤" in passive_names
        assert "大招·加攻" in passive_names


class TestStatAllocator:
    def test_allocator_init(self):
        alloc = StatAllocator()
        assert alloc.remaining == 100

    def test_add_points(self):
        alloc = StatAllocator()
        assert alloc.add("atk", 20) is True
        assert alloc.points["atk"] == 20
        assert alloc.remaining == 80

    def test_add_exceed_remaining(self):
        alloc = StatAllocator()
        assert alloc.add("atk", 150) is False

    def test_reset(self):
        alloc = StatAllocator()
        alloc.add("atk", 50)
        alloc.reset()
        assert alloc.points["atk"] == 0
        assert alloc.remaining == 100

    def test_get_final_stat(self):
        alloc = StatAllocator()
        alloc.add("atk", 30)
        alloc.add("def", 20)
        base = {"max_hp": 100, "atk": 50, "def": 30, "spd": 100}
        stat = alloc.get_final_stat(base)
        assert stat.base_atk == 80
        assert stat.base_def == 50
        assert stat.base_max_hp == 100

    def test_total_points(self):
        alloc = StatAllocator()
        alloc.add("atk", 25)
        alloc.add("def", 25)
        alloc.add("max_hp", 25)
        alloc.add("spd", 25)
        assert alloc.remaining == 0

    def test_stat_limits(self):
        alloc = StatAllocator()
        assert alloc.add("atk", -1) is False


class TestCharacter:
    def test_create_character(self):
        stat = Stat(base_max_hp=500, base_atk=80, base_def=40, base_spd=90)
        char = create_custom_character("测试角色", Element.FIRE, stat)
        assert char.name == "测试角色"
        assert char.element == Element.FIRE
        assert char.current_hp == 500

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

    def test_total_atk_calculation(self):
        """ATK = (base_atk + flat) × (1 + pct)"""
        stat = Stat(base_atk=100, atk_pct=0.5, atk_flat=0)
        assert stat.total_atk() == 150

        stat2 = Stat(base_atk=100, atk_pct=0.3, atk_flat=20)
        assert stat2.total_atk() == 156  # (100+20) * 1.3

    def test_total_max_hp_calculation(self):
        stat = Stat(base_max_hp=1000, hp_pct=0.2)
        assert stat.total_max_hp() == 1200
