"""Fight for Pearl — 类崩铁回合制战斗框架"""
from .models import (
    Character, Element, Skill, SkillType, Effect, Stat, BattleState,
    Passive, BreakDot, BreakStatus, BreakResult,
    BreakEffectType, ELEMENT_BREAK_MAP,
)
from .damage import calculate_damage, apply_damage, DamageResult
from .battle import BattleEngine, BattleEvent, create_default_character, create_enemy
from .skill import SkillExecutor, assign_default_passives
from .character import (
    create_character_from_preset,
    create_custom_character,
    get_preset,
    list_presets,
    StatAllocator,
)

__all__ = [
    # models
    "Character", "Element", "Skill", "SkillType", "Effect", "Stat",
    "BattleState", "Passive", "BreakDot", "BreakStatus", "BreakResult",
    "BreakEffectType", "ELEMENT_BREAK_MAP",
    # damage
    "calculate_damage", "apply_damage", "DamageResult",
    # battle
    "BattleEngine", "BattleEvent", "create_default_character", "create_enemy",
    # skill
    "SkillExecutor", "assign_default_passives",
    # character
    "create_character_from_preset", "create_custom_character",
    "get_preset", "list_presets", "StatAllocator",
]
