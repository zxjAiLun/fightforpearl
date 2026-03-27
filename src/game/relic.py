"""
遗器系统

遗器是装备在角色身上的额外效果组件
分为2件套和4件套效果
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from src.game.models import Character, Element


class RelicType(Enum):
    """遗器类型"""
    HEAD = "head"           # 头部
    HAND = "hand"          # 手部
    BODY = "body"          # 躯干
    FOOT = "foot"          # 脚部
    NECK = "neck"          # 位面球
    OBJECT = "object"      # 连接绳


@dataclass
class RelicEffect:
    """遗器效果"""
    name: str
    effect_type: str
    value: float
    condition: Optional[str] = None
    description: str = ""


@dataclass
class Relic:
    """遗器"""
    id: str
    name: str
    relic_type: RelicType
    set_name: str
    main_stat: str
    sub_stats: list = field(default_factory=list)
    level: int = 1
    rarity: int = 5


# 遗器效果池
RELIC_EFFECT_POOL = {
    "atk_pct": {"type": "atk_pct", "value": 0.10},
    "hp_pct": {"type": "hp_pct", "value": 0.10},
    "def_pct": {"type": "def_pct", "value": 0.10},
    "spd": {"type": "spd", "value": 5.0},
    "crit_rate": {"type": "crit_rate", "value": 0.05},
    "crit_dmg": {"type": "crit_dmg", "value": 0.10},
    "break_efficiency": {"type": "break_efficiency", "value": 0.10},
    "physical_dmg": {"type": "physical_dmg", "value": 0.10},
    "fire_dmg": {"type": "fire_dmg", "value": 0.10},
    "ice_dmg": {"type": "ice_dmg", "value": 0.10},
    "thunder_dmg": {"type": "thunder_dmg", "value": 0.10},
    "wind_dmg": {"type": "wind_dmg", "value": 0.10},
    "quantum_dmg": {"type": "quantum_dmg", "value": 0.10},
    "imaginary_dmg": {"type": "imaginary_dmg", "value": 0.10},
}


# 遗器套装
RELIC_SETS = {
    "黑客": {
        "2pc": [RelicEffect("攻击力", "atk_pct", 0.10)],
        "4pc": [RelicEffect("战技伤害", "skill_dmg", 0.20)],
    },
    "天才": {
        "2pc": [RelicEffect("暴击率", "crit_rate", 0.08)],
        "4pc": [RelicEffect("暴击伤害", "crit_dmg", 0.20)],
    },
    "信使": {
        "2pc": [RelicEffect("速度", "spd", 6.0)],
        "4pc": [RelicEffect("全场速度", "all_spd", 0.12)],
    },
    "过客": {
        "2pc": [RelicEffect("生命", "hp_pct", 0.10)],
        "4pc": [RelicEffect("受治疗", "heal_received", 0.10)],
    },
    "虚数": {
        "2pc": [RelicEffect("击破特攻", "break_efficiency", 0.16)],
        "4pc": [RelicEffect("虚数伤害", "imaginary_dmg", 0.20)],
    },
    "雷鸣": {
        "2pc": [RelicEffect("能量恢复", "energy_recovery", 0.05)],
        "4pc": [RelicEffect("终结技伤害", "ult_dmg", 0.30)],
    },
    "火堆": {
        "2pc": [RelicEffect("灼烧伤害", "burn_dmg", 0.20)],
        "4pc": [RelicEffect("燃烧命中", "burn_chance", 0.10)],
    },
    "筑城": {
        "2pc": [RelicEffect("防御", "def_pct", 0.15)],
        "4pc": [RelicEffect("护盾效果", "shield_bonus", 0.30)],
    },
}


class RelicManager:
    """遗器管理器"""
    
    def __init__(self, character: Character):
        self.character = character
        self.relics: dict[RelicType, Relic] = {}
        self._set_bonuses: dict[str, int] = {}
    
    def equip_relic(self, relic: Relic) -> bool:
        """装备遗器"""
        if relic.relic_type in self.relics:
            return False
        self.relics[relic.relic_type] = relic
        self._update_set_count(relic.set_name)
        self._apply_relic_stats()
        return True
    
    def unequip_relic(self, relic_type: RelicType) -> Optional[Relic]:
        """卸下遗器"""
        relic = self.relics.pop(relic_type, None)
        if relic:
            self._update_set_count(relic.set_name, -1)
            self._reapply_stats()
        return relic
    
    def _update_set_count(self, set_name: str, delta: int = 1):
        self._set_bonuses[set_name] = self._set_bonuses.get(set_name, 0) + delta
    
    def _apply_relic_stats(self):
        for relic in self.relics.values():
            self._apply_single_relic(relic)
        self._apply_set_bonuses()
    
    def _reapply_stats(self):
        self._applied_bonuses = set()
        self._apply_relic_stats()
    
    _applied_bonuses: set = None
    
    def __post_init__(self):
        self._applied_bonuses = set()
    
    def _apply_single_relic(self, relic: Relic):
        if relic.main_stat in RELIC_EFFECT_POOL:
            effect = RELIC_EFFECT_POOL[relic.main_stat]
            self._apply_effect(effect)
    
    def _apply_effect(self, effect: dict):
        eff_type = effect["type"]
        value = effect["value"]
        
        if eff_type == "atk_pct":
            self.character.stat.atk_pct += value
        elif eff_type == "hp_pct":
            self.character.stat.hp_pct += value
        elif eff_type == "def_pct":
            self.character.stat.def_pct += value
        elif eff_type == "spd":
            self.character.stat.spd_pct += value / 100
        elif eff_type == "crit_rate":
            self.character.stat.crit_rate += value
        elif eff_type == "crit_dmg":
            self.character.stat.crit_dmg += value
        elif eff_type == "break_efficiency":
            self.character.stat.break_efficiency += value
    
    def _apply_set_bonuses(self):
        for set_name, count in self._set_bonuses.items():
            if set_name not in RELIC_SETS:
                continue
            set_data = RELIC_SETS[set_name]
            if count >= 2:
                for effect in set_data.get("2pc", []):
                    self._apply_relic_effect(effect)
            if count >= 4:
                for effect in set_data.get("4pc", []):
                    self._apply_relic_effect(effect)
    
    def _apply_relic_effect(self, effect: RelicEffect):
        pass
    
    def get_active_set_bonuses(self) -> dict:
        active = {}
        for set_name, count in self._set_bonuses.items():
            if count >= 2 and set_name in RELIC_SETS:
                active[set_name] = []
                if count >= 2:
                    active[set_name].extend(RELIC_SETS[set_name].get("2pc", []))
                if count >= 4:
                    active[set_name].extend(RELIC_SETS[set_name].get("4pc", []))
        return active
    
    def get_set_count(self, set_name: str) -> int:
        return self._set_bonuses.get(set_name, 0)


def create_relic(relic_id: str, relic_type: RelicType, set_name: str, main_stat: str) -> Relic:
    """创建遗器工厂函数"""
    return Relic(
        id=relic_id,
        name=f"{set_name}-{relic_type.value}",
        relic_type=relic_type,
        set_name=set_name,
        main_stat=main_stat,
    )
