"""角色相关功能"""
from __future__ import annotations
from typing import Optional
import json
import os

from .models import Character, Element, Stat, Skill, SkillType, Passive
from .skill import assign_default_passives


def _load_character_data() -> dict:
    """从 JSON 文件加载角色完整数据"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(base_dir, "data", "characters.json")
    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
            return {c["name"]: c for c in data}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


_CHARACTER_DATA = _load_character_data()


def get_character_data(name: str) -> Optional[dict]:
    """获取角色完整数据"""
    return _CHARACTER_DATA.get(name)


def list_characters() -> list[str]:
    """返回所有角色名"""
    return list(_CHARACTER_DATA.keys())


def _parse_stat(stat_dict: dict) -> Stat:
    """从字典解析Stat对象"""
    return Stat(
        base_max_hp=stat_dict.get("base_max_hp", 100),
        base_atk=stat_dict.get("base_atk", 50),
        base_def=stat_dict.get("base_def", 30),
        base_spd=stat_dict.get("base_spd", 100),
        hp_pct=stat_dict.get("hp_pct", 0.0),
        atk_pct=stat_dict.get("atk_pct", 0.0),
        def_pct=stat_dict.get("def_pct", 0.0),
        spd_pct=stat_dict.get("spd_pct", 0.0),
        hp_flat=stat_dict.get("hp_flat", 0),
        atk_flat=stat_dict.get("atk_flat", 0),
        def_flat=stat_dict.get("def_flat", 0),
        crit_rate=stat_dict.get("crit_rate", 0.05),
        crit_dmg=stat_dict.get("crit_dmg", 1.5),
        effect_hit=stat_dict.get("effect_hit", 0.0),
        effect_res=stat_dict.get("effect_res", 0.0),
        dmg_pct=stat_dict.get("dmg_pct", 0.0),
        break_efficiency=stat_dict.get("break_efficiency", 1.0),
        energy_recovery_rate=stat_dict.get("energy_recovery_rate", 1.0),
        physical_dmg_pct=stat_dict.get("physical_dmg_pct", 0.0),
        wind_dmg_pct=stat_dict.get("wind_dmg_pct", 0.0),
        thunder_dmg_pct=stat_dict.get("thunder_dmg_pct", 0.0),
        fire_dmg_pct=stat_dict.get("fire_dmg_pct", 0.0),
        ice_dmg_pct=stat_dict.get("ice_dmg_pct", 0.0),
        quantum_dmg_pct=stat_dict.get("quantum_dmg_pct", 0.0),
        imaginary_dmg_pct=stat_dict.get("imaginary_dmg_pct", 0.0),
        physical_res_pct=stat_dict.get("physical_res_pct", 0.0),
        wind_res_pct=stat_dict.get("wind_res_pct", 0.0),
        thunder_res_pct=stat_dict.get("thunder_res_pct", 0.0),
        fire_res_pct=stat_dict.get("fire_res_pct", 0.0),
        ice_res_pct=stat_dict.get("ice_res_pct", 0.0),
        quantum_res_pct=stat_dict.get("quantum_res_pct", 0.0),
        imaginary_res_pct=stat_dict.get("imaginary_res_pct", 0.0),
    )


def create_character_from_preset(name: str) -> Character:
    """从JSON数据创建角色"""
    char_data = get_character_data(name)
    if not char_data:
        raise ValueError(f"未找到角色: {name}")
    
    stat = _parse_stat(char_data.get("stat", {}))
    element = Element[char_data.get("element", "PHYSICAL")]
    energy_limit = char_data.get("energy_limit", 120)
    initial_energy = energy_limit / 2
    
    char = Character(
        name=name,
        level=80,
        element=element,
        stat=stat,
        current_hp=stat.total_max_hp(),
        energy=initial_energy,
        energy_limit=energy_limit,
        battle_points=3,
        battle_points_limit=5,
        base_spd=stat.base_spd,
    )
    assign_default_passives(char)
    return char


def create_default_character(name: str, element: Element = Element.PHYSICAL) -> Character:
    """创建默认角色（用于测试）"""
    stat = Stat(
        base_max_hp=1200,
        base_atk=120,
        base_def=80,
        base_spd=105,
    )
    char = Character(
        name=name,
        level=80,
        element=element,
        stat=stat,
        current_hp=stat.total_max_hp(),
        energy=60,
        energy_limit=120,
        battle_points=3,
        battle_points_limit=5,
        base_spd=stat.base_spd,
    )
    return char
