"""
爻光 (Yaoguang) 角色技能设计

基于 https://starrailstation.com/cn/character/yaoguang#skills 数据

角色定位：欢愉型 - 物理属性，笑点机制

==============================
技能
==============================

【普攻】雀翎鸣镝，过招有喜
- Break 30/hit
- 对指定敌方单体造成45% ATK物理伤害
- 对相邻目标造成15% ATK物理伤害

【战技】十方光映，万法皆明
- 展开结界，持续3回合
- 结界持续期间，我方全体欢愉度提高(爻光欢愉度的10%)
- 爻光施放普攻、战技后获得3个笑点

【终结技】霓裳铁羽，六爻皆吉
- 消耗能量 180
- 获得5个笑点
- 使阿哈立即获得1个固定计入20笑点的额外回合
- 使我方全体全属性抗性穿透提高10%，持续3回合

【天赋】屏开千光，遍观自在
- 爻光持有【好活当赏】时：
- 使我方目标施放攻击后触发【大吉大利】效果
- 对随机1个击中的目标额外造成10%的对应属性欢愉伤害
- 本次攻击若消耗战技点，额外触发1次【大吉大利】效果

【欢愉技】赠君一卦，火树银花
- Break 60/hit
- 使敌方全体陷入【凶星低语】状态，持续3回合
- 受到的伤害提高16%
- 对敌方全体造成50%物理欢愉伤害
- 对敌方随机单体造成5次10%物理欢愉伤害

==============================
欢愉机制
==============================

【笑点】：欢愉角色的资源点数，用于触发各种效果
- 爻光普攻回复30点能量（高于一般20点）
- 终结技消耗大量能量但获得笑点

【欢愉度】：影响欢愉角色技能效果的属性

【好活当赏】：触发天赋效果的条件状态

【阿哈时刻】：阿哈的额外回合机制

【大吉大利】：触发追加欢愉伤害的效果
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_yaoguang_basic_skill() -> Skill:
    """普攻：雀翎鸣镝，过招有喜 - 45% ATK + 扩散15%"""
    return Skill(
        name="雀翎鸣镝，过招有喜",
        type=SkillType.BASIC,
        multiplier=0.45,
        damage_type=Element.PHYSICAL,
        description="对目标造成45% ATK伤害，对相邻目标造成15% ATK伤害",
        energy_gain=30.0,  # 比一般多
        battle_points_gain=1,
        break_power=30,
    )


def create_yaoguang_special_skill() -> Skill:
    """战技：十方光映，万法皆明 - 结界3回合"""
    return Skill(
        name="十方光映，万法皆明",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.PHYSICAL,
        description="展开结界持续3回合，我方欢愉度提高，攻击后获得3笑点",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="十方光映结界",
    )


def create_yaoguang_ult_skill() -> Skill:
    """终结技：霓裳铁羽，六爻皆吉 - 笑点+阿哈时刻"""
    return Skill(
        name="霓裳铁羽，六爻皆吉",
        type=SkillType.ULT,
        multiplier=0.0,  # 主要效果是辅助
        damage_type=Element.PHYSICAL,
        description="获得5笑点，使阿哈获得额外回合，我方全属性抗性穿透+10%",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="霓裳铁羽",
        target_count=-1,
    )


def create_yaoguang_talent_skill() -> Skill:
    """天赋：屏开千光，遍观自在"""
    return Skill(
        name="屏开千光，遍观自在",
        type=SkillType.TALENT,
        multiplier=0.10,  # 10%追加伤害
        damage_type=Element.PHYSICAL,
        description="持有【好活当赏】时，攻击后触发【大吉大利】追加伤害",
        energy_gain=0.0,
        break_power=0,
        is_follow_up=True,
    )


def create_yaoguang_festivity_skill() -> Skill:
    """欢愉技：赠君一卦，火树银花"""
    return Skill(
        name="赠君一卦，火树银花",
        type=SkillType.FESTIVITY,
        multiplier=0.50,  # 50% + 5次10%
        damage_type=Element.PHYSICAL,
        description="敌方全体50%伤害，5次10%随机目标，敌人增伤16%持续3回合",
        energy_gain=5.0,
        battle_points_gain=0,
        break_power=60,
        target_count=-1,
    )


def create_yaoguang_passives() -> list[Passive]:
    """爻光的被动技能"""
    return [
        Passive(
            name="开屏有礼",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="joyfulness_bonus",
            value=0.30,  # 速度>=120时欢愉度+30%
            description="速度>=120时欢愉度+30%，每超1点+1%，最多计入200",
        ),
        Passive(
            name="神闲意满",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_boost",
            value=0.60,  # 暴击伤害+60%
            description="自身暴击伤害+60%，施放欢愉技后恢复1战技点",
        ),
        Passive(
            name="鸿运鳞集",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="haozan_duration",
            value=1.0,  # 【好活当赏】持续+1回合
            description="获得【好活当赏】时持续时间+1回合",
        ),
    ]


def create_all_yaoguang_skills() -> list[Skill]:
    return [
        create_yaoguang_basic_skill(),
        create_yaoguang_special_skill(),
        create_yaoguang_ult_skill(),
        create_yaoguang_talent_skill(),
        create_yaoguang_festivity_skill(),
    ]
