"""
彦卿 (Yanqing) 角色技能设计

基于 https://starrailstation.com/cn/character/yanqing#skills 数据

角色定位：巡猎型 - 冰属性暴击输出

==============================
关键机制
==============================

【智剑连心】
- 战技后获得【智剑连心】
- 暴击率+15%，暴击伤害+15%
- 受到攻击时消失
- 触发天赋追加攻击（50% ATK冰伤，65%冻结1回合）

【终结技：快雨燕相逐】
- 暴击率+60%
- 智剑连心时暴击伤害额外+30%
- 造成210% ATK冰伤

==============================
技能
==============================

【普攻】霜锋点寒芒
- 50% ATK 单体冰伤

【战技】遥击三尺水
- 110% ATK 单体冰伤
- 附加【智剑连心】1回合

【终结技】快雨燕相逐
- 暴击率+60%
- 智剑连心时暴击伤害+30%
- 210% ATK 单体冰伤

【天赋】呼剑如影
- 智剑连心：暴击率+15%，暴击伤害+15%
- 攻击后50%概率追加攻击（25% ATK冰伤，65%冻结1回合）
- 受击后智剑连心消失

【秘技】御剑真诀
- 对HP≥50%敌人伤害+30%，持续2回合
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_yanqing_basic_skill() -> Skill:
    """普攻：霜锋点寒芒 - 50% ATK 单体冰伤"""
    return Skill(
        name="霜锋点寒芒",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.ICE,
        description="对指定敌方单体造成50%攻击力的冰属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_yanqing_special_skill() -> Skill:
    """战技：遥击三尺水 - 110% ATK+智剑连心"""
    return Skill(
        name="遥击三尺水",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.10,
        damage_type=Element.ICE,
        description="对指定敌方单体造成110%攻击力的冰属性伤害，并附加【智剑连心】持续1回合",
        energy_gain=30.0,
        break_power=60,
    )


def create_yanqing_ult_skill() -> Skill:
    """终结技：快雨燕相逐 - 210% ATK+暴击率/暴击伤害"""
    return Skill(
        name="快雨燕相逐",
        type=SkillType.ULT,
        multiplier=2.10,
        damage_type=Element.ICE,
        description="暴击率+60%，智剑连心时暴击伤害额外+30%，对指定敌方单体造成210%攻击力冰伤",
        energy_gain=5.0,
        break_power=90,
    )


def create_yanqing_talent_skill() -> Skill:
    """天赋：呼剑如影 - 智剑连心追加攻击"""
    return Skill(
        name="呼剑如影",
        type=SkillType.TALENT,
        multiplier=0.25,
        damage_type=Element.ICE,
        description="智剑连心状态下，攻击后50%概率追加攻击造成25%攻击力冰伤，65%概率冻结1回合",
        energy_gain=10.0,
        break_power=30,
    )


def create_yanqing_passives() -> list[Passive]:
    """彦卿的被动技能（行迹）"""
    return [
        # A2: 颁冰 - 攻击冰弱敌人附加30% ATK冰伤
        Passive(
            name="颁冰",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="ice_weak_bonus",
            value=0.30,
            description="施放攻击后，对携带冰属性弱点的敌方目标造成30%攻击力的冰属性附加伤害",
        ),
        # A2: 冰属性伤害+3.2%，攻击力+4%
        Passive(
            name="冰属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="ice_dmg_increase",
            value=0.032,
            description="冰属性伤害提高3.2%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            description="攻击力提高4%",
        ),
        # A3: 凌霜 - 智剑连心状态抵抗+20%
        Passive(
            name="凌霜",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="sword_heart_res",
            value=0.20,
            description="处于【智剑连心】效果时，效果抵抗提高20%",
        ),
        # A3: 攻击力+6%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
        # A4: 攻击力+6%，冰属性伤害+4.8%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
        Passive(
            name="冰属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="ice_dmg_increase",
            value=0.048,
            description="冰属性伤害提高4.8%",
        ),
        # A5: 轻吕 - 暴击后速度+10%持续2回合
        Passive(
            name="轻吕",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="speed_after_crit",
            value=0.10,
            description="触发暴击时，速度提高10%，持续2回合",
        ),
        # A6: 生命值+6%，冰属性伤害+6.4%
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="max_hp_increase",
            value=0.06,
            description="生命值提高6%",
        ),
        Passive(
            name="冰属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="ice_dmg_increase",
            value=0.064,
            description="冰属性伤害提高6.4%",
        ),
        # Lv75: 攻击力+8%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.08,
            description="攻击力提高8%",
        ),
        # Lv80: 攻击力+4%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            description="攻击力提高4%",
        ),
        # Lv1: 生命值+4%，攻击力+6%
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="max_hp_increase",
            value=0.04,
            description="生命值提高4%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
    ]


def create_all_yanqing_skills() -> list[Skill]:
    return [
        create_yanqing_basic_skill(),
        create_yanqing_special_skill(),
        create_yanqing_ult_skill(),
        create_yanqing_talent_skill(),
    ]
