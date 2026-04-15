"""模拟宇宙难度定义"""
from enum import Enum


class DifficultyLevel(Enum):
    """难度档位"""
    EASY = 1       # 简单
    NORMAL = 2     # 普通
    HARD = 3       # 困难
    ENDLESS = 4    # 无尽

    @property
    def enemy_scale(self) -> float:
        """敌人属性缩放比例"""
        return 1.0 + (self.value - 1) * 0.20  # 每档+20%

    @property
    def blessing_count(self) -> int:
        """祝福/诅咒选择数量"""
        return self.value + 1  # 简单2，普通3，困难4，无尽5

    @property
    def total_floors(self) -> int:
        """总层数"""
        if self == DifficultyLevel.ENDLESS:
            return 999  # 无尽模式
        return 8

    @property
    def label(self) -> str:
        labels = {1: "简单", 2: "普通", 3: "困难", 4: "无尽"}
        return labels[self.value]
