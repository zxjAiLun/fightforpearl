"""角色创建与属性分配模块"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from typing import Optional

from .models import Character, Element, Stat


# 属性上限定义
STAT_LIMITS = {
    "max_hp": 99999,
    "atk": 9999,
    "def": 9999,
    "spd": 999,
    "crit_rate": 1.0,      # 100%
    "crit_dmg": 3.0,       # 300%
    "effect_hit": 1.0,     # 100%
    "effect_res": 1.0,     # 100%
}

# 可分配点数
TOTAL_POINTS = 100

# 属性中文名映射
STAT_NAMES = {
    "max_hp": "HP",
    "atk": "ATK",
    "def": "DEF",
    "spd": "SPD",
    "crit_rate": "暴击率",
    "crit_dmg": "暴击伤害",
    "effect_hit": "效果命中",
    "effect_res": "效果抵抗",
}

# 属性展示名（与 dataclass 字段对应）
STAT_DISPLAY = [
    ("max_hp",    "HP"),
    ("atk",       "ATK"),
    ("def",       "DEF"),
    ("spd",       "SPD"),
    ("crit_rate", "暴击率"),
    ("crit_dmg",  "暴击伤害"),
    ("effect_hit","效果命中"),
    ("effect_res","效果抵抗"),
]


def _load_presets() -> list[dict]:
    """从 data/characters.json 加载预设角色数据"""
    # __file__ = src/game/character.py → 3 levels up = project root
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base, "data", "characters.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("presets", [])


def list_presets() -> list[dict]:
    """返回所有预设角色数据（不含详细属性）"""
    presets = _load_presets()
    return [
        {"name": p["name"], "element": p["element"]}
        for p in presets
    ]


def get_preset(name: str) -> Optional[dict]:
    """根据名字查找预设角色"""
    presets = _load_presets()
    for p in presets:
        if p["name"] == name:
            return p
    return None


def create_character(name: str, element: Element, stat: Stat) -> Character:
    """
    创建角色

    Args:
        name: 角色名
        element: 元素类型
        stat: 角色属性

    Returns:
        Character 实例
    """
    return Character(
        name=name,
        element=element,
        stat=stat,
        current_hp=stat.max_hp,
        current_energy=0.0,
    )


def create_character_from_preset(name: str) -> Optional[Character]:
    """
    从预设创建角色

    Args:
        name: 预设角色名

    Returns:
        Character 实例，或 None（未找到）
    """
    preset = get_preset(name)
    if preset is None:
        return None

    element = Element[preset["element"]]
    s = preset["stat"]
    stat = Stat(
        max_hp=s["max_hp"],
        atk=s["atk"],
        def_=s["def"],
        spd=s["spd"],
        crit_rate=s["crit_rate"],
        crit_dmg=s["crit_dmg"],
        effect_hit=s["effect_hit"],
        effect_res=s["effect_res"],
    )
    return create_character(preset["name"], element, stat)


@dataclass
class StatAllocator:
    """
    属性点分配器（用于 TUI 交互）

    每次从剩余点数中分配到某个属性，支持增加/减少/重置
    """
    total_points: int = TOTAL_POINTS

    def __post_init__(self):
        # 当前各属性分配值
        self.allocated: dict[str, float] = {
            "max_hp": 0,
            "atk": 0,
            "def": 0,
            "spd": 0,
            "crit_rate": 0.0,
            "crit_dmg": 0.0,
            "effect_hit": 0.0,
            "effect_res": 0.0,
        }
        # 原始基础值（来自角色模板）
        self.base_stat: dict[str, float] = {}

    def set_base_stat(self, stat: Stat) -> None:
        """设置角色的基础属性（分配前）"""
        self.base_stat = {
            "max_hp": stat.max_hp,
            "atk": stat.atk,
            "def": stat.def_,
            "spd": stat.spd,
            "crit_rate": stat.crit_rate,
            "crit_dmg": stat.crit_dmg,
            "effect_hit": stat.effect_hit,
            "effect_res": stat.effect_res,
        }
        # 重置分配
        for k in self.allocated:
            self.allocated[k] = 0

    def remaining_points(self) -> int:
        """剩余可分配点数

        百分比属性（crit_rate/crit_dmg/effect_hit/effect_res）:
          存储值为小数（0.05 = 5%），换算为点数 = value * 100
        整数属性（HP/ATK/DEF/SPD）:
          存储值即点数
        """
        # 百分比属性：0.01 = 1 点
        pct_used = int(sum(
            v * 100 for k, v in self.allocated.items()
            if k in ("crit_rate", "crit_dmg", "effect_hit", "effect_res")
        ))
        # 整数属性：1:1
        int_used = int(sum(
            v for k, v in self.allocated.items()
            if k not in ("crit_rate", "crit_dmg", "effect_hit", "effect_res")
        ))
        return self.total_points - int_used - pct_used

    def can_allocate(self, stat_key: str, delta: float) -> bool:
        """检查是否能分配指定量"""
        if stat_key in STAT_LIMITS:
            current = self.base_stat.get(stat_key, 0) + self.allocated[stat_key]
            if current + delta > STAT_LIMITS[stat_key]:
                return False
            if current + delta < 0:
                return False
        # 点数检查
        if stat_key in ("crit_rate", "crit_dmg", "effect_hit", "effect_res"):
            # 百分比属性：delta 以 0.01 (1%) 为单位
            return self.remaining_points() >= int(delta * 100)
        else:
            return self.remaining_points() >= int(delta)

    def allocate(self, stat_key: str, delta: float) -> bool:
        """
        分配属性点
        - delta > 0: 增加
        - delta < 0: 减少
        返回是否成功
        """
        if not self.can_allocate(stat_key, delta):
            return False

        self.allocated[stat_key] += delta
        return True

    def get_final_stat(self) -> Stat:
        """生成最终属性"""
        return Stat(
            max_hp=int(self.base_stat["max_hp"] + self.allocated["max_hp"]),
            atk=int(self.base_stat["atk"] + self.allocated["atk"]),
            def_=int(self.base_stat["def"] + self.allocated["def"]),
            spd=int(self.base_stat["spd"] + self.allocated["spd"]),
            crit_rate=round(self.base_stat["crit_rate"] + self.allocated["crit_rate"], 4),
            crit_dmg=round(self.base_stat["crit_dmg"] + self.allocated["crit_dmg"], 4),
            effect_hit=round(self.base_stat["effect_hit"] + self.allocated["effect_hit"], 4),
            effect_res=round(self.base_stat["effect_res"] + self.allocated["effect_res"], 4),
        )

    def summary(self) -> str:
        """生成当前分配摘要"""
        lines = []
        for key, display_name in STAT_DISPLAY:
            base = self.base_stat.get(key, 0)
            allocated = self.allocated[key]
            current = base + allocated
            limit = STAT_LIMITS.get(key, None)
            if key in ("crit_rate", "effect_hit", "effect_res"):
                line = f"  {display_name:<10}: {base:.0%} + {allocated:+.0%} = {current:.0%}"
            elif key == "crit_dmg":
                line = f"  {display_name:<10}: {base:.0%} + {allocated:+.0%} = {current:.0%}"
            else:
                line = f"  {display_name:<10}: {int(base):>6} + {int(allocated):>+6} = {int(current):>6}"
            if limit is not None and limit < 9999:
                if key in ("crit_rate", "effect_hit", "effect_res"):
                    line += f"  (上限 {limit:.0%})"
                elif key == "crit_dmg":
                    line += f"  (上限 {limit:.0%})"
            lines.append(line)
        lines.append(f"\n  剩余点数: {self.remaining_points()}")
        return "\n".join(lines)
