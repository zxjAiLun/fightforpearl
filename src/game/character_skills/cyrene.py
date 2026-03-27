"""
昔涟 (Cyrene) 角色技能设计

基于 https://starrailstation.com/cn/character/cyrene#skills 数据

角色定位：共生型 - 护盾与治疗转换

==============================
技能
==============================

【普攻】共鸣之触
- Break 30
- 对1个我方目标和1个敌方目标各造成1次等同于角色80%攻击力的虚数属性伤害

【战技】虚影，浊身
- Break 60
- 消耗生命上限30%的生命值
- 转化为【浊身形态】
- 获得等同于消耗量150%的护盾
- 每次受到攻击时，消耗护盾的100%来抵挡伤害

【终结技】虚影，双身
- Break 90
- 消耗生命上限50%的生命值
- 转化为【双身形态】
- 获得等同于消耗量100%的护盾
- 获得100%行动提前
- 使敌方全体防御力降低40%，持续3回合

【行迹1】共生
- 我方全体受到治疗时，将100%的治疗数值转化为护盾
- 每个目标累计转化量不超过自身生命上限的30%
- 任意单位行动后，重置所有单位累计的转化量

【行迹2】共生•共鸣
- 护盾溢出时，额外为我方生命最低的目标恢复等同于溢出量的生命值
- 我方目标生命值最低的20%部分，每1%溢出会额外恢复1点生命值

【行迹3】伤害强化•虚数
- 虚数属性伤害提高12.8%

【行迹4】伤害强化•虚数
- 虚数属性伤害提高12.8%
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_cyrene_basic_skill() -> Skill:
    """普攻：共鸣之触 - 对1个我方+1个敌方造成伤害"""
    return Skill(
        name="共鸣之触",
        type=SkillType.BASIC,
        multiplier=0.80,
        damage_type=Element.IMAGINARY,
        description="对1个我方目标和1个敌方目标各造成1次80%ATK伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_cyrene_special_skill() -> Skill:
    """战技：虚影，浊身 - 转化为浊身形态"""
    return Skill(
        name="虚影，浊身",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.IMAGINARY,
        description="消耗30%HP获得150%护盾，转化为浊身形态",
        energy_gain=0.0,
        break_power=60,
        is_support_skill=True,
        support_modifier_name="浊身形态",
    )


def create_cyrene_ult_skill() -> Skill:
    """终结技：虚影，双身 - 转化为双身形态"""
    return Skill(
        name="虚影，双身",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.IMAGINARY,
        description="消耗50%HP获得100%护盾+行动提前100%，敌方防御-40%",
        energy_gain=0.0,
        break_power=90,
        is_support_skill=True,
        support_modifier_name="双身形态",
        target_count=-1,
    )


def create_cyrene_passives() -> list[Passive]:
    """昔涟的被动技能"""
    return [
        Passive(
            name="行迹：共生",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="heal_to_shield",
            value=1.0,  # 100%转化
            description="治疗转化为护盾，每目标上限30%生命",
        ),
        Passive(
            name="行迹：共生•共鸣",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="shield_overflow_heal",
            value=1.0,
            description="护盾溢出时额外治疗我方",
        ),
        Passive(
            name="行迹：伤害强化•虚数",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="imaginary_dmg_increase",
            value=0.128,
            description="虚数属性伤害提高12.8%",
        ),
        Passive(
            name="行迹：伤害强化•虚数",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="imaginary_dmg_increase",
            value=0.128,
            description="虚数属性伤害提高12.8%",
        ),
    ]


def create_all_cyrene_skills() -> list[Skill]:
    return [
        create_cyrene_basic_skill(),
        create_cyrene_special_skill(),
        create_cyrene_ult_skill(),
    ]
