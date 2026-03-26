"""
召唤物/忆灵系统

召唤物是独立于角色的实体，拥有自己的属性和行动。
它们从属于召唤者，在战斗中可以协同攻击。

与Modifier的区别：
- Modifier: 修改角色属性的效果，有持续时间
- Summon: 独立实体，有HP，可以被攻击，可以主动行动
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum, auto


class SummonState(Enum):
    """召唤物状态"""
    IDLE = auto()      # 待机
    ACTIVE = auto()    # 激活
    COOLDOWN = auto()  # 冷却中


@dataclass
class Summon:
    """
    召唤物/忆灵
    
    召唤物是从属于角色的独立实体：
    - 有自己的HP和属性
    - 可以被敌方攻击
    - 可以对敌方行动
    - 回合开始时重置为IDLE状态
    """
    name: str
    owner: 'Character'  # 召唤者
    level: int = 1
    
    # 属性
    max_hp: int = 1000
    current_hp: int = 1000
    atk: int = 500
    def_value: int = 200
    spd: int = 100
    
    # 状态
    state: SummonState = SummonState.IDLE
    action_value: float = 0.0
    is_alive: bool = True
    
    # 技能
    basic_skill_name: str = "协同攻击"
    skill_multiplier: float = 0.5  # 协同攻击倍率
    
    # 特殊效果
    follow_up_on_basic: bool = True  # 召唤者普攻后协同攻击
    
    def is_alive_func(self) -> bool:
        """检查召唤物是否存活"""
        return self.current_hp > 0 and self.is_alive
    
    def take_damage(self, damage: int) -> None:
        """承受伤害"""
        self.current_hp = max(0, self.current_hp - damage)
        if self.current_hp <= 0:
            self.is_alive = False
    
    def heal(self, amount: int) -> None:
        """回复HP"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def calculate_action_value(self, is_first_round: bool = True) -> float:
        """计算行动值"""
        if self.spd <= 0:
            return 150.0 if is_first_round else 100.0
        base = 150.0 if is_first_round else 100.0
        return base / self.spd
    
    def reset_for_turn(self) -> None:
        """回合开始时重置"""
        self.state = SummonState.IDLE
        self.action_value = self.calculate_action_value()
    
    def advance_action(self, subsequent_av: float = 100.0) -> None:
        """行动后重置行动值"""
        self.action_value += subsequent_av


class SummonManager:
    """
    召唤物管理器 - 管理角色身上的所有召唤物
    """
    
    def __init__(self, owner: Character):
        self.owner = owner
        self.summons: list[Summon] = []
        self.max_summons: int = 1  # 默认最多1个召唤物
    
    def add_summon(self, summon: Summon) -> bool:
        """添加召唤物"""
        if len(self.summons) >= self.max_summons:
            # 替换最旧的召唤物
            self.remove_oldest()
        
        summon.owner = self.owner
        self.summons.append(summon)
        return True
    
    def remove_summon(self, summon: Summon) -> bool:
        """移除召唤物"""
        if summon in self.summons:
            self.summons.remove(summon)
            return True
        return False
    
    def remove_oldest(self) -> None:
        """移除最旧的召唤物"""
        if self.summons:
            self.summons.pop(0)
    
    def get_active_summons(self) -> list[Summon]:
        """获取活跃的召唤物"""
        return [s for s in self.summons if s.is_alive_func()]
    
    def tick_turn_start(self) -> None:
        """回合开始时重置所有召唤物"""
        for summon in self.summons:
            if summon.is_alive_func():
                summon.reset_for_turn()
    
    def __len__(self) -> int:
        return len(self.summons)
    
    def __iter__(self):
        return iter(self.summons)
