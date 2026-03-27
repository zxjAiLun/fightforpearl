"""
银狼 (Silverwolf) 角色技能设计

基于 https://starrailstation.com/cn/character/silverwolf#skills 数据

角色定位：量子+虚无 - 弱点植入+缺陷植入

==============================
技能
==============================

【普攻】|系统警告|
- Break 30
- 对指定敌方单体造成等同于银狼50%攻击力的量子属性伤害

【战技】是否允许更改？
- 使目标添加1个我方持有属性的弱点
- 该弱点对应属性抗性降低20%
- 使目标全属性抗性降低7.5%
- 造成98%攻击力量子属性伤害

【终结技】|账号已封禁|
- 使目标防御力降低36%
- 造成228%攻击力量子属性伤害

【天赋】等待程序响应…
- 植入【缺陷】：攻击力降低5%、防御力降低4%、速度降低3%
- 每次攻击后有60%概率植入1个随机缺陷

==============================
机制
==============================

【缺陷】：降低攻击/防御/速度的debuff
【弱点植入】：为敌方添加我方属性弱点
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_silverwolf_basic_skill() -> Skill:
    """普攻：|系统警告| - 50% ATK"""
    return Skill(
        name="|系统警告|",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成50%攻击力的量子属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_silverwolf_special_skill() -> Skill:
    """战技：是否允许更改？ - 弱点植入+减抗"""
    return Skill(
        name="是否允许更改？",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.98,
        damage_type=Element.QUANTUM,
        description="添加弱点+抗性降低20%+7.5%，造成98%伤害",
        energy_gain=30.0,
        break_power=60,
    )


def create_silverwolf_ult_skill() -> Skill:
    """终结技：|账号已封禁| - 减防+伤害"""
    return Skill(
        name="|账号已封禁|",
        type=SkillType.ULT,
        multiplier=2.28,
        damage_type=Element.QUANTUM,
        description="使目标防御力-36%，造成228%量子伤害",
        energy_gain=5.0,
        break_power=90,
    )


def create_silverwolf_talent_skill() -> Skill:
    """天赋：等待程序响应… - 缺陷植入"""
    return Skill(
        name="等待程序响应…",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="攻击后60%概率植入【缺陷】：攻击-5%/防御-4%/速度-3%",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
    )


def create_silverwolf_passives() -> list[Passive]:
    """银狼的被动技能"""
    return [
        Passive(
            name="生成",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="defect_duration_extend",
            value=1.0,
            description="【缺陷】持续时间+1回合，弱点被击破时65%概率植入缺陷",
        ),
        Passive(
            name="注入",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="weakness_duration_extend",
            value=1.0,
            description="战技添加的弱点持续时间+1回合",
        ),
        Passive(
            name="旁注",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="res_reduction_boost",
            value=3.0,
            description="目标有3+负面效果时，战技全属性抗性降低效果额外+3%",
        ),
        Passive(
            name="重叠网络",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_per_debuff",
            value=0.20,
            description="敌方每有1个负面效果，银狼对其伤害+20%，最多+100%",
        ),
    ]


def create_all_silverwolf_skills() -> list[Skill]:
    return [
        create_silverwolf_basic_skill(),
        create_silverwolf_special_skill(),
        create_silverwolf_ult_skill(),
        create_silverwolf_talent_skill(),
    ]
