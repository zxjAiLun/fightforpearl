"""模拟宇宙奖励系统"""
from dataclasses import dataclass
from typing import List

from .blessings import Blessing, BLESSING_POOL, PathType
from .curios import Curio, CURIO_POOL


@dataclass
class RunReward:
    """运行奖励"""
    credits: int = 0
    blessings: List[Blessing] = field(default_factory=list)
    curios: List[Curio] = field(default_factory=list)
    completed_floors: int = 0
    defeated_enemies: int = 0
    equations_activated: int = 0


def calculate_run_rewards(run) -> RunReward:
    """根据运行结果计算奖励"""
    reward = RunReward()
    reward.credits = run.credits
    reward.blessings = list(run.blessings)
    reward.curios = list(run.curios)
    reward.completed_floors = run.current_floor - 1
    reward.equations_activated = len(run.active_equations)
    return reward


def get_completion_bonus(completed_floors: int, difficulty: int = 1) -> int:
    """通关奖励：额外信用点"""
    base = completed_floors * 50
    return base * difficulty
