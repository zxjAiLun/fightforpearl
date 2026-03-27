"""
流萤 (Firefly/SAM) 角色技能设计

基于 https://starrailstation.com/cn/character/sam#skills 数据

角色定位：毁灭+火 - 超击破伤害

==============================
技能
==============================

【普攻】指令-闪燃推进
- Break 30
- 对指定敌方单体造成50% ATK火属性伤害

【强化普攻】火萤Ⅳ型-底火斩击
- 回复20% HP
- 造成100% ATK火属性伤害

【战技】指令-天火轰击
- 消耗40% HP恢复50%能量
- 造成100% ATK伤害
- HP不足时降至1点，下次行动提前25%

【强化战技】火萤Ⅳ型-死星过载
- 回复25% HP
- 添加火属性弱点2回合
- 造成(0.2*击破特攻+100%) ATK伤害
- 相邻目标(0.1*击破特攻+50%)

【大招】火萤Ⅳ型-完全燃烧
- 行动提前100%
- 进入【完全燃烧】状态
- 强化普攻和强化战技
- 速度+30
- 无法再施放终结技

【天赋】茧式源火中枢
- HP越低受伤越低，<=20%时最大20%减伤
- 【完全燃烧】维持最大减伤，效果抵抗+10%
- 能量<50%时恢复至50%

==============================
机制
==============================

【完全燃烧】：强化状态，速度+30，强化普攻/战技
【超击破】：削韧值转化为伤害
【击破特攻】：流萤核心属性
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_firefly_basic_skill() -> Skill:
    """普攻：指令-闪燃推进 - 50% ATK"""
    return Skill(
        name="指令-闪燃推进",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成50%攻击力的火属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_firefly_enhanced_basic_skill() -> Skill:
    """强化普攻：火萤Ⅳ型-底火斩击"""
    return Skill(
        name="火萤Ⅳ型-底火斩击",
        type=SkillType.BASIC,
        multiplier=1.0,
        damage_type=Element.FIRE,
        description="回复20% HP，造成100% ATK伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=45,
    )


def create_firefly_special_skill() -> Skill:
    """战技：指令-天火轰击"""
    return Skill(
        name="指令-天火轰击",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.0,
        damage_type=Element.FIRE,
        description="消耗40%HP恢复50%能量，造成100% ATK伤害",
        energy_gain=0.0,
        break_power=60,
    )


def create_firefly_enhanced_special_skill() -> Skill:
    """强化战技：火萤Ⅳ型-死星过载"""
    return Skill(
        name="火萤Ⅳ型-死星过载",
        type=SkillType.SPECIAL,
        cost=0,  # 强化战技不消耗战技点
        multiplier=1.0,  # 基础100%，实际为(0.2*击破特攻+100%)
        damage_type=Element.FIRE,
        description="回复25%HP，添加火弱点，造成(0.2*击破特攻+100%)伤害",
        energy_gain=0.0,
        break_power=90,
        target_count=1,
    )


def create_firefly_ult_skill() -> Skill:
    """终结技：火萤Ⅳ型-完全燃烧"""
    return Skill(
        name="火萤Ⅳ型-完全燃烧",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.FIRE,
        description="进入【完全燃烧】状态，行动提前100%，强化普攻/战技",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="完全燃烧",
    )


def create_firefly_talent_skill() -> Skill:
    """天赋：茧式源火中枢"""
    return Skill(
        name="茧式源火中枢",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.FIRE,
        description="HP越低受伤越低，能量<50%时恢复至50%",
        energy_gain=0.0,
        break_power=0,
    )


def create_firefly_passives() -> list[Passive]:
    """流萤的被动技能"""
    return [
        Passive(
            name="α模组-偏时迸发",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_ignore_weakness",
            value=0.55,
            description="【完全燃烧】状态下可无视弱点削韧55%",
        ),
        Passive(
            name="β模组-自限装甲",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="super_break_conversion",
            value=0.35,
            description="击破特攻>=200%/360%时，削韧值转化为35%/50%超击破伤害",
        ),
        Passive(
            name="γ模组-过载核心",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_from_atk",
            value=0.008,
            description="ATK>1800时，每超10点ATK使击破特攻+0.8%",
        ),
    ]


def create_all_firefly_skills() -> list[Skill]:
    return [
        create_firefly_basic_skill(),
        create_firefly_enhanced_basic_skill(),
        create_firefly_special_skill(),
        create_firefly_enhanced_special_skill(),
        create_firefly_ult_skill(),
        create_firefly_talent_skill(),
    ]
