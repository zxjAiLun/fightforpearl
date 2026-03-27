"""
布洛妮娅技能设计

角色定位：
- 战技：使单个队友拉条100%（行动提前）
- 大招：全队增加爆伤

技能效果通过Modifier实现
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking, ModifierManager
from src.game.models import Character, Element, Skill, SkillType


def create_bronya_basic_skill() -> Skill:
    """布洛妮娅普攻"""
    return Skill(
        name="射击",
        type=SkillType.BASIC,
        multiplier=1.0,
        damage_type=Element.ICE,
        description="普通射击攻击",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=10,
    )


def create_bronya_special_skill() -> Skill:
    """布洛妮娅战技：使一名我方角色行动提前100%"""
    return Skill(
        name="指令",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,  # 不造成伤害
        damage_type=Element.ICE,
        description="使我方指定角色行动提前100%，快速获得额外回合",
        energy_gain=30.0,
        break_power=0,
        # 战技不造成伤害，而是应用拉条Modifier
    )


def create_bronya_ult_skill() -> Skill:
    """布洛妮娅终结技：为我方全体增加爆伤"""
    return Skill(
        name="轮契",
        type=SkillType.ULT,
        multiplier=0.0,  # 不造成伤害
        damage_type=Element.ICE,
        description="为我方全体增加爆伤，持续2回合",
        energy_gain=5.0,
        break_power=0,
        target_count=-1,  # 全体
    )


def apply_bronya_special_effect(caster: Character, target: Character) -> Modifier:
    """
    应用布洛妮娅战技效果：目标拉条100%
    
    拉条100%意味着目标行动值减少10000，即立即行动
    """
    mod = Modifier(
        name="指令-拉条",
        source_skill="指令",
        duration=1,  # 持续1回合
        modifier_type=ModifierType.BUFF,
        pull_forward_pct=1.0,  # 100%拉条
    )
    return mod


def apply_bronya_ult_effect(caster: Character, targets: list[Character]) -> list[Modifier]:
    """
    应用布洛妮娅大招效果：全队增加爆伤
    
    崩铁中布洛妮娅大招提供约60%爆伤加成
    """
    modifiers = []
    for target in targets:
        mod = Modifier(
            name="轮契-爆伤",
            source_skill="轮契",
            duration=2,  # 持续2回合
            modifier_type=ModifierType.BUFF,
            crit_dmg_pct=0.6,  # +60%爆伤
        )
        modifiers.append(mod)
    return modifiers


def create_all_bronya_skills() -> list[Skill]:
    """创建布洛妮娅所有技能"""
    return [
        create_bronya_basic_skill(),
        create_bronya_special_skill(),
        create_bronya_ult_skill(),
    ]
