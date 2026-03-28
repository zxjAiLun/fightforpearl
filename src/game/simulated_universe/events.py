"""模拟宇宙事件定义"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EventType(Enum):
    BATTLE = "battle"           # 普通战斗
    ELITE = "elite"             # 精英战斗
    BOSS = "boss"               # Boss战
    BLESSING = "blessing"       # 祝福选择
    CURIO = "curio"             # 奇物事件
    SHOP = "shop"               # 商店
    REWARD = "reward"           # 直接奖励（信用点）
    MYSTERY = "mystery"         # 随机事件
    REST = "rest"               # 休息（回血）
    EQUATION = "equation"       # 方程激活


@dataclass
class UniverseEvent:
    """宇宙事件"""
    name: str
    type: EventType
    description: str
    # 战斗配置
    enemies: list[str] = None   # 敌人ID列表
    # 奖励配置
    credit_reward: int = 0
    blessing_pool: list[str] = None  # 可选祝福列表
    curios_pool: list[str] = None   # 可选奇物列表
    equation_unlock: str = None     # 可解锁的方程ID
    # 难度
    difficulty: int = 1

    def __post_init__(self):
        if self.enemies is None:
            self.enemies = []
