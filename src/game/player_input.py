"""玩家技能选择模块"""

from __future__ import annotations
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class SkillChoice:
    """玩家技能选择结果"""
    skill: 'Skill'
    targets: list['Character']


class PlayerInputHandler:
    """
    玩家输入处理器
    
    处理玩家手动选择技能和目标的逻辑。
    支持TUI和GUI两种输入模式。
    """
    
    def __init__(self):
        self._tui_callback: Optional[Callable] = None
        self._gui_callback: Optional[Callable] = None
    
    def set_tui_callback(self, callback: Callable):
        """设置TUI模式下的回调函数"""
        self._tui_callback = callback
    
    def set_gui_callback(self, callback: Callable):
        """设置GUI模式下的回调函数"""
        self._gui_callback = callback
    
    def request_player_input(self, actor, available_skills, opponents, mode='auto') -> SkillChoice:
        """
        请求玩家输入
        
        Args:
            actor: 当前行动的角色
            available_skills: 可用的技能列表
            opponents: 可选择的敌人目标
            mode: 输入模式 ('auto', 'tui', 'gui')
        
        Returns:
            SkillChoice: 包含选中的技能和目标
        """
        if mode == 'auto':
            # 自动模式：使用AI选择
            return self._auto_select(actor, available_skills, opponents)
        elif mode == 'tui' and self._tui_callback:
            return self._tui_callback(actor, available_skills, opponents)
        elif mode == 'gui' and self._gui_callback:
            return self._gui_callback(actor, available_skills, opponents)
        else:
            # 默认自动模式
            return self._auto_select(actor, available_skills, opponents)
    
    def _auto_select(self, actor, available_skills, opponents):
        """自动选择技能（AI逻辑）"""
        from .skill import select_player_skill
        
        skill = select_player_skill(actor, None)
        targets = skill.get_targets(opponents) if skill else []
        
        return SkillChoice(skill=skill, targets=targets)


# 全局实例
_player_input_handler = PlayerInputHandler()


def get_player_input_handler() -> PlayerInputHandler:
    """获取全局玩家输入处理器"""
    return _player_input_handler


def set_tui_input_mode():
    """设置TUI输入模式"""
    pass  # TUI使用自己的回调


def set_gui_input_mode():
    """设置GUI输入模式"""
    pass  # GUI使用自己的回调
