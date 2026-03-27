"""角色相关功能"""
from __future__ import annotations
from typing import Optional
import json
import os

from .models import Character, Element, Stat, Skill, SkillType, Passive, FollowUpTrigger, TriggerCondition
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
    
    # 特殊角色有特定的被动技能
    if name == "遐蝶":
        from .character_skills.castorice import create_castorice_passives
        char.passives.extend(create_castorice_passives())
    if name == "丹恒·腾荒":
        from .character_skills.danheng_percival import create_danheng_percival_passives, create_souldragon
        char.passives.extend(create_danheng_percival_passives())
        # 初始化龙灵为None（战技后召唤）
        char.souldragon = None
        # 初始化挚友状态
        from .character_skills.danheng_percival import BondmateState
        char.bondmate_state = BondmateState()
        # 初始化护盾管理器
        from .character_skills.danheng_percival import ShieldManager
        char.shield_manager = ShieldManager(char)
    if name == "海瑟音":
        from .character_skills.hysilens import create_hysilens_passives
        char.passives.extend(create_hysilens_passives())
    if name == "罗刹":
        from .character_skills.luocha import create_luocha_passives
        char.passives.extend(create_luocha_passives())
    if name == "玲可":
        from .character_skills.lynx import create_lynx_passives
        char.passives.extend(create_lynx_passives())
    if name == "佩拉":
        from .character_skills.pela import create_pela_passives
        char.passives.extend(create_pela_passives())
    if name == "黑天鹅":
        from .character_skills.blackswan import create_blackswan_passives
        char.passives.extend(create_blackswan_passives())
    
    # 从skills.json加载技能数据并分配
    try:
        import json
        from pathlib import Path
        # Path(__file__) = src/game/character.py
        # parent = src/game
        # parent.parent = src
        # parent.parent.parent = 项目根目录
        path = Path(__file__).parent.parent.parent / "data" / "skills.json"
        with open(path, encoding="utf-8") as f:
            skills_data = json.load(f)
        from .skill import assign_default_skills
        assign_default_skills(char, skills_data)
    except Exception as e:
        print(f"Warning: Failed to load skills for {name}: {e}")
    
    # 加载追加攻击触发器
    char_data = get_character_data(name)
    if char_data and "follow_up_triggers" in char_data:
        for trigger_data in char_data["follow_up_triggers"]:
            trigger = FollowUpTrigger(
                name=trigger_data["name"],
                condition=TriggerCondition[trigger_data.get("condition", "NONE")],
                condition_value=float(trigger_data.get("condition_value", 0.0)),
                trigger_skill_type=SkillType[trigger_data.get("trigger_skill_type", "BASIC")],
                chance=float(trigger_data.get("chance", 1.0)),
                follow_up_skill_name=trigger_data.get("follow_up_skill_name", ""),
                multiplier=float(trigger_data.get("multiplier", 0.6)),
                damage_type=Element[trigger_data.get("damage_type", "PHYSICAL")],
                target_scope=trigger_data.get("target_scope", "single"),
                description=trigger_data.get("description", ""),
            )
            char.follow_up_triggers.append(trigger)
    
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
