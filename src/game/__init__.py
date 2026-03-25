"""Fight for Pearl — 类崩铁回合制战斗框架"""
from .models import Character, Element, Skill, SkillType, Effect, Stat, BattleState, ELEMENT_COUNTER
from .damage import calculate_damage, apply_damage, DamageResult
from .battle import BattleEngine, BattleState, BattleEvent
from .skill import SkillExecutor
from .character import (
    create_character,
    create_character_from_preset,
    get_preset,
    list_presets,
    StatAllocator,
    TOTAL_POINTS,
    STAT_LIMITS,
    STAT_NAMES,
    STAT_DISPLAY,
)
from .character_creator import run_character_creator

__all__ = [
    # models
    "Character",
    "Element",
    "Skill",
    "SkillType",
    "Effect",
    "Stat",
    "BattleState",
    "BattleEngine",
    "BattleEvent",
    "DamageResult",
    # damage
    "calculate_damage",
    "apply_damage",
    # character
    "create_character",
    "create_character_from_preset",
    "get_preset",
    "list_presets",
    "StatAllocator",
    "TOTAL_POINTS",
    "STAT_LIMITS",
    "STAT_NAMES",
    "STAT_DISPLAY",
    # tui
    "run_character_creator",
]
