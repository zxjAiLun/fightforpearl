"""角色创建与属性分配测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from game import Character, Element, Stat
from game.character import (
    create_character,
    create_character_from_preset,
    StatAllocator,
    TOTAL_POINTS,
    STAT_LIMITS,
    get_preset,
    list_presets,
)
from game.character_creator import _elem_name


def test_create_character():
    """测试 create_character 函数"""
    stat = Stat(
        max_hp=1000,
        atk=120,
        def_=80,
        spd=105,
        crit_rate=0.05,
        crit_dmg=1.5,
        effect_hit=0.0,
        effect_res=0.0,
    )
    char = create_character("穹", Element.PHYSICAL, stat)

    assert char.name == "穹"
    assert char.element == Element.PHYSICAL
    assert char.stat.max_hp == 1000
    assert char.stat.atk == 120
    assert char.stat.def_ == 80
    assert char.stat.spd == 105
    assert char.stat.crit_rate == 0.05
    assert char.stat.crit_dmg == 1.5
    assert char.current_hp == 1000  # current_hp 应等于 max_hp
    assert char.current_energy == 0.0
    print("✅ create_character 测试通过")


def test_create_character_from_preset():
    """测试从预设创建角色"""
    char = create_character_from_preset("三月七")
    assert char is not None
    assert char.name == "三月七"
    assert char.element == Element.ICE
    assert char.stat.max_hp == 1100
    print("✅ create_character_from_preset 测试通过")


def test_create_character_from_preset_not_found():
    """测试预设不存在时返回 None"""
    char = create_character_from_preset("不存在的角色")
    assert char is None
    print("✅ create_character_from_preset (不存在) 测试通过")


def test_preset_list():
    """测试预设列表"""
    presets = list_presets()
    assert len(presets) >= 3
    names = [p["name"] for p in presets]
    assert "穹" in names
    assert "三月七" in names
    print(f"✅ list_presets 测试通过 (共 {len(presets)} 个预设)")


def test_get_preset():
    """测试获取单个预设"""
    preset = get_preset("丹恒")
    assert preset is not None
    assert preset["element"] == "WIND"
    assert preset["stat"]["atk"] == 140
    print("✅ get_preset 测试通过")


def test_stat_allocator_basic():
    """测试属性分配器基本功能"""
    allocator = StatAllocator(total_points=TOTAL_POINTS)
    base = Stat(max_hp=100, atk=50, def_=30, spd=100)
    allocator.set_base_stat(base)

    assert allocator.remaining_points() == TOTAL_POINTS

    # 分配 HP +10
    ok = allocator.allocate("max_hp", 10)
    assert ok
    assert allocator.remaining_points() == TOTAL_POINTS - 10

    # 分配 ATK +5
    ok = allocator.allocate("atk", 5)
    assert ok
    assert allocator.remaining_points() == TOTAL_POINTS - 15

    # 减少 HP 5 点
    ok = allocator.allocate("max_hp", -5)
    assert ok
    assert allocator.remaining_points() == TOTAL_POINTS - 10

    print("✅ StatAllocator 基本分配 测试通过")


def test_stat_allocator_percentage():
    """测试百分比属性分配"""
    allocator = StatAllocator(total_points=TOTAL_POINTS)
    base = Stat(crit_rate=0.05, crit_dmg=1.5, effect_hit=0.0, effect_res=0.0)
    allocator.set_base_stat(base)

    # 分配 5% 暴击率（消耗 5 点）
    ok = allocator.allocate("crit_rate", 0.05)
    assert ok
    assert allocator.remaining_points() == TOTAL_POINTS - 5

    # 分配 10% 暴击伤害（消耗 10 点）
    ok = allocator.allocate("crit_dmg", 0.10)
    assert ok
    assert allocator.remaining_points() == TOTAL_POINTS - 15

    # 分配 5% 暴击率（再消耗 5 点）
    ok = allocator.allocate("crit_rate", 0.05)
    assert ok
    assert allocator.remaining_points() == TOTAL_POINTS - 20

    print("✅ StatAllocator 百分比属性 测试通过")


def test_stat_allocator_limit():
    """测试属性上限"""
    allocator = StatAllocator(total_points=200)
    base = Stat(crit_rate=0.99, crit_dmg=2.8, effect_hit=0.9, effect_res=0.9)
    allocator.set_base_stat(base)

    # crit_rate 上限 1.0，当前 0.99，再加 0.02 应该失败
    ok = allocator.allocate("crit_rate", 0.02)
    assert not ok

    # 刚好到上限
    ok = allocator.allocate("crit_rate", 0.01)
    assert ok
    assert allocator.remaining_points() == 200 - 1  # 1%

    print("✅ StatAllocator 属性上限 测试通过")


def test_stat_allocator_exhaust_points():
    """测试点数耗尽"""
    allocator = StatAllocator(total_points=100)
    base = Stat(max_hp=0, atk=0, def_=0, spd=0)
    allocator.set_base_stat(base)

    # 消耗完所有 100 点
    for _ in range(100):
        ok = allocator.allocate("max_hp", 1)
        assert ok

    assert allocator.remaining_points() == 0
    # 再分配应该失败
    ok = allocator.allocate("max_hp", 1)
    assert not ok
    print("✅ StatAllocator 点数耗尽 测试通过")


def test_stat_allocator_mixed():
    """测试整数属性 + 百分比属性混合分配"""
    allocator = StatAllocator(total_points=100)
    base = Stat(max_hp=100, atk=50, def_=30, spd=100, crit_rate=0.05)
    allocator.set_base_stat(base)

    # 整数: HP +10 (消耗 10 点)
    allocator.allocate("max_hp", 10)
    # 百分比: 暴击率 +10% (消耗 10 点)
    allocator.allocate("crit_rate", 0.10)
    # 整数: ATK +5 (消耗 5 点)
    allocator.allocate("atk", 5)

    assert allocator.remaining_points() == 100 - 10 - 10 - 5

    print("✅ StatAllocator 混合分配 测试通过")


def test_stat_allocator_get_final_stat():
    """测试生成最终属性"""
    allocator = StatAllocator(total_points=100)
    base = Stat(max_hp=100, atk=50, def_=30, spd=100, crit_rate=0.05, crit_dmg=1.5)
    allocator.set_base_stat(base)

    allocator.allocate("max_hp", 20)
    allocator.allocate("atk", 10)
    allocator.allocate("crit_rate", 0.20)

    stat = allocator.get_final_stat()
    assert stat.max_hp == 120
    assert stat.atk == 60
    assert stat.crit_rate == 0.25
    assert stat.crit_dmg == 1.5  # 未分配，不变
    print("✅ StatAllocator.get_final_stat 测试通过")


def test_stat_allocator_reset():
    """测试重置分配"""
    allocator = StatAllocator(total_points=100)
    base = Stat(max_hp=100, atk=50)
    allocator.set_base_stat(base)

    allocator.allocate("max_hp", 30)
    allocator.allocate("atk", 20)
    assert allocator.remaining_points() == 50

    for k in allocator.allocated:
        allocator.allocated[k] = 0
    assert allocator.remaining_points() == 100
    print("✅ StatAllocator 重置 测试通过")


def test_character_current_hp_equals_max_hp():
    """验证创建角色时 current_hp == max_hp"""
    stat = Stat(max_hp=2000, atk=150, def_=100, spd=90)
    char = create_character("测试角色", Element.FIRE, stat)
    assert char.current_hp == char.stat.max_hp == 2000
    print("✅ 角色 current_hp == max_hp 测试通过")


def test_stat_limits():
    """验证 STAT_LIMITS 定义正确"""
    assert STAT_LIMITS["crit_rate"] == 1.0
    assert STAT_LIMITS["crit_dmg"] == 3.0
    assert STAT_LIMITS["effect_hit"] == 1.0
    assert STAT_LIMITS["effect_res"] == 1.0
    print("✅ STAT_LIMITS 定义测试通过")


def test_total_points():
    """验证总点数常量"""
    assert TOTAL_POINTS == 100
    print("✅ TOTAL_POINTS == 100 测试通过")


if __name__ == "__main__":
    print("运行角色创建与属性分配测试...\n")
    test_create_character()
    test_create_character_from_preset()
    test_create_character_from_preset_not_found()
    test_preset_list()
    test_get_preset()
    test_stat_allocator_basic()
    test_stat_allocator_percentage()
    test_stat_allocator_limit()
    test_stat_allocator_exhaust_points()
    test_stat_allocator_mixed()
    test_stat_allocator_get_final_stat()
    test_stat_allocator_reset()
    test_character_current_hp_equals_max_hp()
    test_stat_limits()
    test_total_points()
    print("\n🎉 所有角色创建与属性分配测试通过！")
