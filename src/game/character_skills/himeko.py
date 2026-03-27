"""
姬子 (Himeko) 角色技能设计

基于 https://starrailstation.com/cn/character/himeko#skills 数据

角色定位：火属性智识 - AOE+追击

==============================
技能
==============================

【普攻】武装调律
- Break 30
- 对指定敌方单体造成等同于姬子50%攻击力的火属性伤害

【战技】熔核爆裂
- Break 60 + 30/相邻
- 对指定敌方单体造成100%攻击力火属性伤害
- 对相邻目标造成40%攻击力火属性伤害

【终结技】天坠之火
- Break 60/hit
- 对敌方全体造成138%火属性伤害
- 每消灭1个敌方目标额外恢复5点能量

【天赋】乘胜追击
- 敌方弱点被击破时获得充能，上限3点
- 充能达到上限时，立即发动追加攻击，对敌方全体造成70%火属性伤害
- 战斗开始时获得1点充能

==============================
机制
==============================

【充能】：弱点被击破时获得，最多3点
【追击】：充能满时触发全体攻击
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_himeko_basic_skill() -> Skill:
    """普攻：武装调律 - 50% ATK"""
    return Skill(
        name="武装调律",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成50%攻击力的火属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_himeko_special_skill() -> Skill:
    """战技：熔核爆裂 - 100%+40%扩散"""
    return Skill(
        name="熔核爆裂",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.0,
        secondary_multiplier=0.40,
        damage_type=Element.FIRE,
        description="对目标100%伤害，对相邻目标40%伤害",
        energy_gain=30.0,
        break_power=60,
    )


def create_himeko_ult_skill() -> Skill:
    """终结技：天坠之火 - 138% AOE"""
    return Skill(
        name="天坠之火",
        type=SkillType.ULT,
        multiplier=1.38,
        damage_type=Element.FIRE,
        description="对敌方全体造成138%火属性伤害，击杀回复能量",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
    )


def create_himeko_talent_skill() -> Skill:
    """天赋：乘胜追击 - 充能追击系统"""
    return Skill(
        name="乘胜追击",
        type=SkillType.TALENT,
        multiplier=0.70,
        damage_type=Element.FIRE,
        description="弱点击破获得充能，上限3点；充能满时追加攻击全体70%伤害",
        energy_gain=10.0,
        break_power=30,
        target_count=-1,
    )


def create_himeko_passives() -> list[Passive]:
    """姬子的被动技能"""
    return [
        Passive(
            name="星火",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="burn_application",
            value=0.50,
            description="攻击后50%概率使敌人陷入灼烧状态2回合",
        ),
        Passive(
            name="灼热",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="burn_dmg_bonus",
            value=0.20,
            description="战技对灼烧状态目标伤害+20%",
        ),
        Passive(
            name="道标",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_rate_hp_threshold",
            value=0.15,
            description="HP>=80%时暴击率+15%",
        ),
    ]


def create_all_himeko_skills() -> list[Skill]:
    return [
        create_himeko_basic_skill(),
        create_himeko_special_skill(),
        create_himeko_ult_skill(),
        create_himeko_talent_skill(),
    ]
