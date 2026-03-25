"""角色相关功能"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .models import Character, Element, Stat, Skill, SkillType, Passive
from .skill import assign_default_passives


# ============================================================
# 预设角色数据（基础属性，百分比加成均为0）
# ============================================================
PRESET_CHARACTERS = {
    "星": {
        "element": Element.PHYSICAL,
        "stat": Stat(base_max_hp=1200, base_atk=120, base_def=80, base_spd=105),
    },
    "三月萤": {
        "element": Element.WIND,
        "stat": Stat(base_max_hp=1000, base_atk=110, base_def=70, base_spd=110),
    },
    "丹恒": {
        "element": Element.THUNDER,
        "stat": Stat(base_max_hp=1050, base_atk=125, base_def=65, base_spd=108),
    },
    "姬子": {
        "element": Element.FIRE,
        "stat": Stat(base_max_hp=950, base_atk=130, base_def=60, base_spd=112),
    },
    "银狼": {
        "element": Element.QUANTUM,
        "stat": Stat(base_max_hp=1000, base_atk=118, base_def=68, base_spd=115),
    },
    "布洛妮娅": {
        "element": Element.ICE,
        "stat": Stat(base_max_hp=1020, base_atk=115, base_def=72, base_spd=108),
    },
    "瓦尔特": {
        "element": Element.IMAGINARY,
        "stat": Stat(base_max_hp=980, base_atk=128, base_def=62, base_spd=110),
    },
}


def get_preset(name: str) -> Optional[dict]:
    """获取预设角色数据"""
    return PRESET_CHARACTERS.get(name)


def list_presets() -> list[str]:
    """返回所有预设角色名"""
    return list(PRESET_CHARACTERS.keys())


def create_character_from_preset(name: str) -> Character:
    """从预设创建角色（含默认被动）"""
    preset = get_preset(name)
    if not preset:
        raise ValueError(f"未找到预设角色: {name}")
    stat = preset["stat"].clone()
    char = Character(
        name=name,
        level=1,
        element=preset["element"],
        stat=stat,
        current_hp=stat.total_max_hp(),
        current_energy=0.0,
    )
    assign_default_passives(char)
    return char


def create_custom_character(
    name: str,
    element: Element,
    stat: Stat,
) -> Character:
    """创建自定义角色（属性自由分配）"""
    char = Character(
        name=name,
        level=1,
        element=element,
        stat=stat,
        current_hp=stat.total_max_hp(),
        current_energy=0.0,
    )
    assign_default_passives(char)
    return char


# ============================================================
# 属性分配器（100点自由分配）
# ============================================================
@dataclass
class StatAllocator:
    """
    属性点分配器
    提供 100 点供自由分配到 4 项基础属性
    """
    TOTAL_POINTS: int = 100

    def __init__(self):
        self.points = {
            "max_hp": 0,
            "atk": 0,
            "def": 0,
            "spd": 0,
        }
        self.remaining = self.TOTAL_POINTS

    def allocate(self, stat_name: str, value: int) -> bool:
        """分配属性点，返回是否成功"""
        if stat_name not in self.points:
            return False
        delta = value - self.points[stat_name]
        if delta > self.remaining:
            return False
        if value < 0:
            return False
        self.points[stat_name] = value
        self.remaining = self.TOTAL_POINTS - sum(self.points.values())
        return True

    def add(self, stat_name: str, delta: int) -> bool:
        """增加某项属性点，返回是否成功"""
        if stat_name not in self.points:
            return False
        if delta <= 0:
            return False
        if delta > self.remaining:
            return False
        self.points[stat_name] += delta
        self.remaining -= delta
        return True

    def reset(self) -> None:
        """重置所有属性点"""
        for k in self.points:
            self.points[k] = 0
        self.remaining = self.TOTAL_POINTS

    def get_final_stat(self, base: dict) -> Stat:
        """
        将分配结果应用到基础属性上
        base = {"max_hp": 100, "atk": 50, "def": 30, "spd": 100}
        返回包含基础值 + 分配值的 Stat
        """
        return Stat(
            base_max_hp=base["max_hp"] + self.points["max_hp"],
            base_atk=base["atk"] + self.points["atk"],
            base_def=base["def"] + self.points["def"],
            base_spd=base["spd"] + self.points["spd"],
        )

    @property
    def summary(self) -> dict:
        return {
            **self.points,
            "remaining": self.remaining,
        }
