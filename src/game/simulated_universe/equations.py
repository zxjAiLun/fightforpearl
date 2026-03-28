"""模拟宇宙方程系统（差分宇宙核心）"""
from dataclasses import dataclass
from typing import List

from .blessings import PathType


@dataclass
class Equation:
    """方程"""
    id: str
    name: str
    description: str
    # 激活条件：需要的祝福数量
    required_blessings: dict  # {PathType.WARRIOR: 3} 表示需要3个战士祝福
    # 激活后的效果加成
    atk_pct: float = 0.0
    def_pct: float = 0.0
    hp_pct: float = 0.0
    crit_rate: float = 0.0
    crit_dmg: float = 0.0
    spd_pct: float = 0.0
    dmg_pct: float = 0.0
    elemental_dmg_pct: float = 0.0
    break_efficiency: float = 0.0
    energy_recovery_rate: float = 0.0

    def can_activate(self, blessing_counts: dict) -> bool:
        """检查是否满足激活条件"""
        for path, required in self.required_blessings.items():
            if blessing_counts.get(path, 0) < required:
                return False
        return True

    def apply_to(self, character):
        """应用方程效果"""
        character.stat.atk_pct += self.atk_pct
        character.stat.def_pct += self.def_pct
        character.stat.hp_pct += self.hp_pct
        character.stat.crit_rate += self.crit_rate
        character.stat.crit_dmg += self.crit_dmg
        character.stat.spd_pct += self.spd_pct
        character.stat.dmg_pct += self.dmg_pct
        character.stat.break_efficiency += self.break_efficiency
        character.stat.energy_recovery_rate += self.energy_recovery_rate


EQUATION_POOL = {
    "eq_explosion": Equation(
        id="eq_explosion",
        name="繁育方程·爆发",
        description="繁育≥8：攻击力+20%",
        required_blessings={PathType.QUANTUM: 8},
        atk_pct=0.20,
    ),
    "eq_void": Equation(
        id="eq_void",
        name="虚无方程·侵蚀",
        description="虚无≥5：全体伤害+15%",
        required_blessings={PathType.QUANTUM: 5},
        dmg_pct=0.15,
    ),
    "eq_warrior": Equation(
        id="eq_warrior",
        name="战士方程·铁壁",
        description="战士≥3：防御+15%，HP+10%",
        required_blessings={PathType.WARRIOR: 3},
        def_pct=0.15,
        hp_pct=0.10,
    ),
    "eq_mage": Equation(
        id="eq_mage",
        name="智识方程·奥术",
        description="智识≥3：暴击率+10%，暴击伤害+20%",
        required_blessings={PathType.MAGE: 3},
        crit_rate=0.10,
        crit_dmg=0.20,
    ),
    "eq_thunder": Equation(
        id="eq_thunder",
        name="雷鸣方程·疾电",
        description="雷鸣≥5：速度+15%，能量恢复+20%",
        required_blessings={PathType.THUNDER: 5},
        spd_pct=0.15,
        energy_recovery_rate=0.20,
    ),
}


def get_available_equations(blessing_counts: dict) -> list[Equation]:
    """获取当前可激活的方程"""
    available = []
    for eq in EQUATION_POOL.values():
        if eq.can_activate(blessing_counts):
            available.append(eq)
    return available
