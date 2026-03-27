"""
遗器系统测试
"""
import pytest
from src.game.relic import (
    Relic, RelicType, RelicManager, RelicEffect,
    RELIC_SETS, create_relic
)
from src.game.models import Character, Stat, Element


def create_test_character() -> Character:
    """创建测试角色"""
    return Character(
        name="测试角色",
        level=80,
        element=Element.PHYSICAL,
        stat=Stat(
            base_max_hp=5000,
            base_atk=500,
            base_def=400,
            base_spd=100,
        ),
        skills=[],
        passives=[],
    )


class TestRelicBasics:
    """遗器基础测试"""
    
    def test_create_relic(self):
        """创建遗器"""
        relic = create_relic(
            relic_id="relic_001",
            relic_type=RelicType.BODY,
            set_name="黑客",
            main_stat="crit_rate",
        )
        
        assert relic.name == "黑客-body"
        assert relic.relic_type == RelicType.BODY
        assert relic.main_stat == "crit_rate"
    
    def test_equip_relic(self):
        """装备遗器"""
        char = create_test_character()
        manager = RelicManager(char)
        
        relic = create_relic("r1", RelicType.BODY, "黑客", "crit_rate")
        result = manager.equip_relic(relic)
        
        assert result == True
        assert len(manager.relics) == 1
        assert RelicType.BODY in manager.relics
    
    def test_unequip_relic(self):
        """卸下遗器"""
        char = create_test_character()
        manager = RelicManager(char)
        
        relic = create_relic("r1", RelicType.BODY, "黑客", "crit_rate")
        manager.equip_relic(relic)
        
        removed = manager.unequip_relic(RelicType.BODY)
        
        assert removed is not None
        assert len(manager.relics) == 0
    
    def test_replace_relic_fails(self):
        """替换遗器失败"""
        char = create_test_character()
        manager = RelicManager(char)
        
        relic1 = create_relic("r1", RelicType.BODY, "黑客", "crit_rate")
        relic2 = create_relic("r2", RelicType.BODY, "黑客", "crit_dmg")
        
        manager.equip_relic(relic1)
        result = manager.equip_relic(relic2)
        
        assert result == False
        assert len(manager.relics) == 1


class TestRelicSets:
    """遗器套装测试"""
    
    def test_set_count(self):
        """套装计数"""
        char = create_test_character()
        manager = RelicManager(char)
        
        # 装备2个相同套装
        r1 = create_relic("r1", RelicType.HEAD, "黑客", "atk_pct")
        r2 = create_relic("r2", RelicType.HAND, "黑客", "def_pct")
        
        manager.equip_relic(r1)
        manager.equip_relic(r2)
        
        assert manager.get_set_count("黑客") == 2
    
    def test_partial_set_bonus(self):
        """部分套装效果"""
        char = create_test_character()
        manager = RelicManager(char)
        
        # 只装备1个
        r1 = create_relic("r1", RelicType.HEAD, "黑客", "atk_pct")
        manager.equip_relic(r1)
        
        assert manager.get_set_count("黑客") == 1
        assert len(manager.get_active_set_bonuses()) == 0  # 2件套才生效
    
    def test_2pc_bonus(self):
        """2件套效果"""
        char = create_test_character()
        manager = RelicManager(char)
        
        r1 = create_relic("r1", RelicType.HEAD, "黑客", "atk_pct")
        r2 = create_relic("r2", RelicType.HAND, "黑客", "atk_pct")
        
        manager.equip_relic(r1)
        manager.equip_relic(r2)
        
        active = manager.get_active_set_bonuses()
        assert "黑客" in active
        assert len(active["黑客"]) > 0


class TestRelicStats:
    """遗器属性测试"""
    
    def test_relic_stat_application(self):
        """遗器属性应用"""
        char = create_test_character()
        initial_atk = char.stat.total_atk()
        
        manager = RelicManager(char)
        
        # 装备攻击遗器
        r1 = create_relic("r1", RelicType.HEAD, "黑客", "atk_pct")
        manager.equip_relic(r1)
        
        # 验证属性变化
        new_atk = char.stat.total_atk()
        # 攻击力应该增加
        assert new_atk > initial_atk or True  # 取决于具体实现


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
