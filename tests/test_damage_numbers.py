"""伤害飘字系统测试"""

import pytest
from src.game.gui import FloatingDamageNumber, FloatingDamageManager


class TestFloatingDamageNumber:
    """测试飘字类"""
    
    def test_creation(self):
        """测试飘字创建"""
        num = FloatingDamageNumber(
            text="100",
            x=100,
            y=200,
            color=(255, 255, 255),
        )
        assert num.text == "100"
        assert num.x == 100
        assert num.y == 200
        assert num.alpha == 255
        assert num.lifetime == 60
    
    def test_update_decreases_lifetime(self):
        """测试更新减少持续时间"""
        num = FloatingDamageNumber("50", 100, 200, (255, 255, 255))
        initial_lifetime = num.lifetime
        num.update()
        assert num.lifetime < initial_lifetime
    
    def test_update_returns_false_when_expired(self):
        """测试过期返回False"""
        num = FloatingDamageNumber("50", 100, 200, (255, 255, 255))
        num.lifetime = 1
        result = num.update()
        assert result == False
    
    def test_crit_font_size(self):
        """测试暴击时字体更大"""
        normal = FloatingDamageNumber("100", 100, 200, (255, 255, 255))
        crit = FloatingDamageNumber("100", 100, 200, (255, 255, 255), is_crit=True)
        
        assert normal.font_size == 18
        assert crit.font_size == 24


class TestFloatingDamageManager:
    """测试飘字管理器"""
    
    def test_add_damage(self):
        """测试添加伤害"""
        manager = FloatingDamageManager()
        manager.add_damage(100, 100, 200)
        
        assert len(manager.numbers) == 1
        assert manager.numbers[0].text == "100"
    
    def test_add_crit_damage(self):
        """测试添加暴击伤害"""
        manager = FloatingDamageManager()
        manager.add_damage(500, 100, 200, is_crit=True)
        
        assert len(manager.numbers) == 1
        assert "💥" in manager.numbers[0].text
        assert manager.numbers[0].is_crit == True
    
    def test_add_heal(self):
        """测试添加治疗"""
        manager = FloatingDamageManager()
        manager.add_damage(50, 100, 200, is_heal=True)
        
        assert len(manager.numbers) == 1
        assert manager.numbers[0].is_heal == True
    
    def test_update_removes_expired(self):
        """测试更新移除过期的飘字"""
        manager = FloatingDamageManager()
        manager.add_damage(100, 100, 200)
        manager.numbers[0].lifetime = 1
        
        manager.update()
        assert len(manager.numbers) == 0
