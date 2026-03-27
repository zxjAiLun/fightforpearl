"""
驭空 (Yukong) 角色技能设计

基于 https://starrailstation.com/cn/character/yukong#skills 数据

角色定位：同谐+虚数 - 鸣弦号令增益+暴击爆伤

==============================
技能
==============================

【普攻】流镝
- Break 30
- 对指定敌方单体造成等同于驭空50%攻击力的虚数属性伤害

【战技】天阙鸣弦
- 获得2层【鸣弦号令】
- 持有【鸣弦号令】时，我方全体攻击力提高40%
- 每次我方目标回合结束时移除1层（驭空放战技的回合不移除）

【终结技】贯云饮羽
- 消耗能量 130
- 若持有【鸣弦号令】，额外使我方全体暴击率提高21%
- 暴击伤害提高39%
- 对指定敌方单体造成228%攻击力虚数属性伤害

【天赋】箭彻七札
- 施放普攻可额外造成40%攻击力虚数属性伤害
- 本次攻击削韧值提高100%
- 该效果在1回合后可再次触发

【秘技】云鸢逐风
- 冲刺状态持续20秒，自身移动速度+35%
- 主动攻击进入战斗时，驭空获得2层【鸣弦号令】

==============================
机制
==============================

【鸣弦号令】：核心增益，每层提供攻击力+40%，回合结束减层
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_yukong_basic_skill() -> Skill:
    """普攻：流镝 - 50% ATK"""
    return Skill(
        name="流镝",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.IMAGINARY,
        description="对指定敌方单体造成50%攻击力的虚数属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_yukong_special_skill() -> Skill:
    """战技：天阙鸣弦 - 鸣弦号令增益"""
    return Skill(
        name="天阙鸣弦",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.IMAGINARY,
        description="获得2层【鸣弦号令】：我方全体攻击力+40%，每队友回合结束减1层",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="鸣弦号令",
        target_count=-1,
    )


def create_yukong_ult_skill() -> Skill:
    """终结技：贯云饮羽 - 暴击爆伤加成+伤害"""
    return Skill(
        name="贯云饮羽",
        type=SkillType.ULT,
        multiplier=2.28,
        damage_type=Element.IMAGINARY,
        description="持有鸣弦时：全队暴击率+21%，暴击伤害+39%，对单体造成228%虚数伤害",
        energy_gain=5.0,
        break_power=90,
    )


def create_yukong_talent_skill() -> Skill:
    """天赋：箭彻七札 - 额外伤害+削韧"""
    return Skill(
        name="箭彻七札",
        type=SkillType.TALENT,
        multiplier=0.40,
        damage_type=Element.IMAGINARY,
        description="普攻额外造成40%ATK伤害，削韧值+100%，1回合后可再次触发",
        energy_gain=0.0,
        break_power=0,
    )


def create_yukong_passives() -> list[Passive]:
    """驭空的被动技能"""
    return [
        Passive(
            name="襄尺",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="debuff_resist_once",
            value=1.0,
            description="被施加负面效果时可抵抗1次，该效果在2回合后可再次触发；生命+4%，虚数伤害+3.2%",
        ),
        Passive(
            name="迟彝",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="imaginary_dmg_party",
            value=0.12,
            description="驭空在场时，我方全体造成的虚数属性伤害提高12%",
        ),
        Passive(
            name="气壮",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_per_ally_action",
            value=2.0,
            description="持有【鸣弦号令】时，每我方目标行动后，驭空恢复2点能量",
        ),
        Passive(
            name="百里闻风",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_buff_start",
            value=0.10,
            description="进入战斗时，我方全体速度提高10%，持续2回合",
        ),
        Passive(
            name="百里闻风·九曲响镝",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_with_string",
            value=0.30,
            description="持有【鸣弦号令】时，驭空造成的伤害提高30%",
        ),
        Passive(
            name="弦栝如雷",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="string_on_ult",
            value=1.0,
            description="驭空施放终结技时，立即先获得1层【鸣弦号令】",
        ),
    ]


def create_all_yukong_skills() -> list[Skill]:
    return [
        create_yukong_basic_skill(),
        create_yukong_special_skill(),
        create_yukong_ult_skill(),
        create_yukong_talent_skill(),
    ]
