"""
藿藿 (Huohuo) 角色技能设计

基于 https://starrailstation.com/cn/character/huohuo#skills 数据

角色定位：丰饶+风 - 治疗+能量回复+驱散

==============================
技能
==============================

【普攻】令旗·征风召雨
- Break 30
- 对指定敌方单体造成等同于藿藿25%生命上限的风属性伤害

【战技】灵符·保命护身
- 解除指定我方单体的1个负面效果
- 为目标回复等同于藿藿14%生命上限+140的生命值
- 为相邻目标回复等同于藿藿11.2%生命上限+112的生命值

【终结技】尾巴·遣神役鬼
- 消耗能量 140
- 为队友恢复各自15%能量上限的能量
- 使其攻击力提高24%，持续2回合

【天赋】凭附·气通天真
- 施放战技后获得【禳命】持续2回合
- 【禳命】：回合开始或施放终结技时为队友回复等同于藿藿3%生命上限+30的生命
- 治疗时解除目标1个负面效果（最多触发6次）

【秘技】凶煞·劾压鬼物
- 恐吓周围敌人陷入【魄散】状态
- 【魄散】：敌人逃跑，进入战斗时敌方全体攻击力降低25%，持续2回合

==============================
机制
==============================

【禳命】：藿藿的核心治疗状态，每回合为队友提供治疗和驱散
【魄散】：秘技控制效果
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_huohuo_basic_skill() -> Skill:
    """普攻：令旗·征风召雨 - 25% HP作为伤害"""
    return Skill(
        name="令旗·征风召雨",
        type=SkillType.BASIC,
        multiplier=0.25,  # 25% HP-based
        damage_type=Element.WIND,
        description="对指定敌方单体造成等同于藿藿25%生命上限的风属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_huohuo_special_skill() -> Skill:
    """战技：灵符·保命护身 - 治疗+驱散"""
    return Skill(
        name="灵符·保命护身",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="解除1个负面效果，为己方单体回复14%HP+140，相邻目标回复11.2%HP+112",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="禳命",
    )


def create_huohuo_ult_skill() -> Skill:
    """终结技：尾巴·遣神役鬼 - 能量回复+攻击加成"""
    return Skill(
        name="尾巴·遣神役鬼",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="为队友恢复各自15%能量上限能量，攻击力+24%持续2回合",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="尾巴增伤",
        target_count=-1,
    )


def create_huohuo_talent_skill() -> Skill:
    """天赋：凭附·气通天真 - 禳命治疗机制"""
    return Skill(
        name="凭附·气通天真",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="【禳命】每回合/终结技时为队友治疗3%HP+30，治疗时驱散1个负面效果",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
    )


def create_huohuo_passives() -> list[Passive]:
    """藿藿的被动技能"""
    return [
        Passive(
            name="不敢自专",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="initial_buff",
            value=1.0,
            description="战斗开始时获得【禳命】持续1回合；效果抵抗+4%，生命值+4%",
        ),
        Passive(
            name="贞凶之命",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_resist",
            value=0.35,
            description="抵抗控制类负面状态的概率提高35%",
        ),
        Passive(
            name="怯惧应激",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_on_heal",
            value=1.0,
            description="触发天赋为我方目标提供治疗时，藿藿恢复1点能量",
        ),
        Passive(
            name="魂魄灾厄",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_by_hp_ratio",
            value=0.80,
            description="战技治疗时，目标当前HP越低治疗量越高，最多使治疗量提高80%",
        ),
    ]


def create_all_huohuo_skills() -> list[Skill]:
    return [
        create_huohuo_basic_skill(),
        create_huohuo_special_skill(),
        create_huohuo_ult_skill(),
        create_huohuo_talent_skill(),
    ]
