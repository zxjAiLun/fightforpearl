"""
火花 (Sparxie) 角色技能设计

基于 https://starrailstation.com/cn/character/sparxie#skills 数据

角色定位：欢愉型 - 火属性，多段攻击

==============================
技能
==============================

【普攻】哑火了吗
- Break 30
- 对指定敌方单体造成50% ATK火属性伤害

【强化普攻】百花齐放，胜者独享！
- 扩散攻击
- 对指定敌方单体造成50% ATK火属性伤害
- 对相邻目标造成25% ATK火属性伤害

【战技】尖叫！火花花连线中
- 开启直播连线，使普攻变为【百花齐放，胜者独享！】
- 发动【互动陷阱】：使强化普攻伤害倍率提高10%/5%
- 随机获得礼物：【红红火火】2笑点+2战技点 或 【恍恍惚惚】1笑点
- 可发动最多20次【互动陷阱】

【终结技】万我狂欢，镜头不要停
- Break 60
- 获得2个笑点
- 对敌方全体造成(0.6*欢愉度+30%) ATK的火属性伤害

【天赋】幕后花手
- 火花持有【好活当赏】时：
- 强化普攻对指定目标造成20%火属性欢愉伤害
- 对相邻目标造成10%火属性欢愉伤害
- 每发动1次【互动陷阱】，额外对随机1个目标造成1次10%火属性欢愉伤害
- 终结技对敌方全体造成24%火属性欢愉伤害

【欢愉技】信号溢出：好戏返场！
- Break 20/hit
- 对敌方全体造成25%火属性欢愉伤害
- 额外造成20次12.5%火属性欢愉伤害（随机单体）
- 使火花获得2个【爆点】（可抵扣战技点消耗）

==============================
欢愉机制
==============================

【笑点】：欢愉角色的资源点
【好活当赏】：触发天赋强化的条件状态
【爆点】：可抵扣战技点消耗的点数
【互动陷阱】：火花战技的核心机制
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_sparxie_basic_skill() -> Skill:
    """普攻：哑火了吗 - 50% ATK"""
    return Skill(
        name="哑火了吗",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成50% ATK火属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_sparxie_enhanced_basic_skill() -> Skill:
    """强化普攻：百花齐放，胜者独享！- 扩散"""
    return Skill(
        name="百花齐放，胜者独享！",
        type=SkillType.BASIC,
        multiplier=0.50,
        secondary_multiplier=0.25,
        damage_type=Element.FIRE,
        description="对目标50% ATK，对相邻目标25% ATK",
        energy_gain=40.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_sparxie_special_skill() -> Skill:
    """战技：尖叫！火花花连线中 - 直播连线"""
    return Skill(
        name="尖叫！火花花连线中",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.FIRE,
        description="开启直播连线，使普攻变为强化普攻，发动【互动陷阱】最多20次",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="直播连线",
    )


def create_sparxie_ult_skill() -> Skill:
    """终结技：万我狂欢，镜头不要停"""
    return Skill(
        name="万我狂欢，镜头不要停",
        type=SkillType.ULT,
        multiplier=0.30,  # 基础30% + 欢愉度加成
        damage_type=Element.FIRE,
        description="获得2笑点，对敌方全体造成(30%+0.6*欢愉度)% ATK火属性伤害",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
    )


def create_sparxie_talent_skill() -> Skill:
    """天赋：幕后花手 - 强化普攻追加"""
    return Skill(
        name="幕后花手",
        type=SkillType.TALENT,
        multiplier=0.20,  # 20% + 10%
        secondary_multiplier=0.10,
        damage_type=Element.FIRE,
        description="持有【好活当赏】时，强化普攻追加伤害，每【互动陷阱】+1次追加",
        energy_gain=0.0,
        break_power=15,
        is_follow_up=True,
    )


def create_sparxie_festivity_skill() -> Skill:
    """欢愉技：信号溢出：好戏返场！"""
    return Skill(
        name="信号溢出：好戏返场！",
        type=SkillType.FESTIVITY,
        multiplier=0.25,  # 25% + 20次12.5%
        damage_type=Element.FIRE,
        description="全体25%伤害，额外20次12.5%随机伤害，获得2【爆点】",
        energy_gain=5.0,
        break_power=20,
        target_count=-1,
        ricochet_count=20,
        ricochet_decay=0.0,  # 固定12.5%
    )


def create_sparxie_passives() -> list[Passive]:
    """火花的被动技能"""
    return [
        Passive(
            name="甜蜜！笑点签售会",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="joyfulness_atk_bonus",
            value=0.05,  # ATK>2000时每超100点欢愉度+5%
            description="攻击力>2000时，每超100点使欢愉度+5%，最多80%",
        ),
        Passive(
            name="炫目！人设万花筒",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="festivity_bonus",
            value=2.0,  # 额外获得笑点和爆点
            description="队伍中欢愉角色数量1/2/3时，终结技额外获得2/4/8笑点和1/1/4爆点",
        ),
        Passive(
            name="沸腾！真伪调色盘",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_per_laugh",
            value=0.08,  # 每笑点+8%暴击伤害
            description="每拥有1笑点，我方全体暴击伤害+8%，最多80%",
        ),
    ]


def create_all_sparxie_skills() -> list[Skill]:
    return [
        create_sparxie_basic_skill(),
        create_sparxie_enhanced_basic_skill(),
        create_sparxie_special_skill(),
        create_sparxie_ult_skill(),
        create_sparxie_talent_skill(),
        create_sparxie_festivity_skill(),
    ]
