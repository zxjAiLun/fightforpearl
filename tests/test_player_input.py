"""玩家输入模块测试"""

import pytest
from src.game.player_input import PlayerInputHandler, SkillChoice, get_player_input_handler


class TestPlayerInputHandler:
    """测试PlayerInputHandler"""
    
    def test_singleton(self):
        """测试全局单例"""
        handler1 = get_player_input_handler()
        handler2 = get_player_input_handler()
        assert handler1 is handler2
    
    def test_callback_registration(self):
        """测试回调函数注册"""
        handler = PlayerInputHandler()
        
        called = []
        
        def tui_cb(actor, skills, opponents):
            called.append(True)
            return skills[0], opponents[:1]
        
        def gui_cb(actor, skills, opponents):
            called.append(False)
            return skills[0], opponents[:1]
        
        handler.set_tui_callback(tui_cb)
        handler.set_gui_callback(gui_cb)
        
        assert handler._tui_callback is not None
        assert handler._gui_callback is not None
    
    def test_auto_mode(self):
        """测试自动模式"""
        handler = PlayerInputHandler()
        
        class MockSkill:
            def __init__(self, name):
                self.name = name
                self.is_aoe = lambda: False
                self.get_targets = lambda x: x[:1]
        
        class MockActor:
            name = "TestActor"
            skills = []
        
        skills = [MockSkill("skill1"), MockSkill("skill2")]
        opponents = ["target1", "target2"]
        
        result = handler.request_player_input(MockActor(), skills, opponents, mode='auto')
        
        # 自动模式下没有技能会返回None
        assert result.skill is None


class TestSkillChoice:
    """测试SkillChoice数据类"""
    
    def test_skill_choice_creation(self):
        """测试SkillChoice创建"""
        class MockSkill:
            name = "test"
        
        choice = SkillChoice(skill=MockSkill(), targets=["target1", "target2"])
        
        assert choice.skill.name == "test"
        assert len(choice.targets) == 2
