"""
火花 (Sparxie) 角色技能设计

基于 https://starrailstation.com/cn/character/sparxie#skills 数据

角色定位：火属性输出 - 多段攻击和追加攻击

==============================
技能
==============================

【普攻】魔女的小黑魔法
- Break 20
- 对指定敌方单体造成等同于角色50%攻击力的火属性伤害

【战技】魔女的四重罪
- Break 30
- 对随机敌方目标造成4次等同于角色40%攻击力的火属性伤害
- 每次伤害递减15%

【终结技】魔女的终夜狂舞
- Break 60
- 对敌方全体造成3次等同于角色80%攻击力的火属性伤害

【被动1】魔女的永燃论
- 火属性伤害提高12%

【被动2】魔女的燃命说
- 每次攻击造成伤害时，额外造成1次等同于角色10%攻击力的火属性伤害
- 视为追加攻击
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_sparxie_basic_skill() -> Skill:
    """普攻：魔女的小黑魔法 - 50% ATK"""
    return Skill(
        name="魔女的小黑魔法",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成等同于角色50%攻击力的火属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=20,
    )


def create_sparxie_special_skill() -> Skill:
    """战技：魔女的四重罪 - 4次攻击"""
    return Skill(
        name="魔女的四重罪",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.40,
        damage_type=Element.FIRE,
        description="对随机目标造成4次40%ATK伤害，每次递减15%",
        energy_gain=0.0,
        break_power=30,
        ricochet_count=3,  # 4次攻击 = 1次主目标 + 3次弹射
        ricochet_decay=0.85,
    )


def create_sparxie_ult_skill() -> Skill:
    """终结技：魔女的终夜狂舞 - 3次AOE"""
    return Skill(
        name="魔女的终夜狂舞",
        type=SkillType.ULT,
        multiplier=0.80,
        damage_type=Element.FIRE,
        description="对敌方全体造成3次80%ATK伤害",
        energy_gain=0.0,
        break_power=60,
        target_count=-1,
    )


def create_sparxie_passives() -> list[Passive]:
    """火花的被动技能"""
    return [
        Passive(
            name="被动：魔女的永燃论",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="fire_dmg_increase",
            value=0.12,
            description="火属性伤害提高12%",
        ),
        Passive(
            name="被动：魔女的燃命说",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="extra_attack",
            value=0.10,
            description="每次攻击额外造成1次10%ATK伤害，视为追加攻击",
        ),
    ]


def create_all_sparxie_skills() -> list[Skill]:
    return [
        create_sparxie_basic_skill(),
        create_sparxie_special_skill(),
        create_sparxie_ult_skill(),
    ]
