"""
青雀 (Qingque) 角色技能设计

基于 https://starrailstation.com/cn/character/qingque#skills 数据

角色定位：智识型 - 量子麻将随机输出

==============================
关键机制
==============================

【琼玉牌系统】
- 青雀每回合开始随机抽取1张琼玉牌（共3种花色）
- 最多持有4张牌
- 4张相同花色时进入【暗杠】状态

【暗杠状态】
- 攻击力+36%
- 普攻变为强化普攻【杠上开花！】
- 不可施放战技

【战技：海底捞月】
- 立即抽取2张牌
- 伤害提高14%，持续至本回合结束
- 可叠加4层

==============================
技能
==============================

【普攻】门前清
- 50% ATK 单体量子伤害

【强化普攻】杠上开花！
- 120% ATK 单体+50% ATK AOE
- 不可恢复战技点

【战技】海底捞月
- 抽取2张琼玉牌
- 伤害+14%，持续至本回合结束（可叠加4层）

【终结技】四幺暗刻？和！
- 120% ATK AOE量子伤害
- 获得4张相同花色琼玉牌

【天赋】帝垣琼玉
- 回合开始时随机抽取1张牌
- 4张相同花色时进入【暗杠】

【秘技】独弈之乐
- 战斗开始时抽取2张琼玉牌
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_qingque_basic_skill() -> Skill:
    """普攻：门前清 - 50% ATK 单体量子"""
    return Skill(
        name="门前清",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.QUANTUM,
        description="使用1张当前花色最少的琼玉牌，对指定敌方单体造成50%攻击力的量子属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_qingque_enhanced_basic_skill() -> Skill:
    """强化普攻：杠上开花！- 120% ATK AOE"""
    return Skill(
        name="杠上开花！",
        type=SkillType.BASIC,
        multiplier=1.20,
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成120%攻击力量子伤害，对相邻目标造成50%攻击力伤害",
        energy_gain=20.0,
        battle_points_gain=0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=0.50,
    )


def create_qingque_special_skill() -> Skill:
    """战技：海底捞月 - 抽牌+增伤"""
    return Skill(
        name="海底捞月",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="立即抽取2张琼玉牌，使自身造成的伤害提高14%，持续至本回合结束，可叠加4层",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="海底捞月增益",
    )


def create_qingque_ult_skill() -> Skill:
    """终结技：四幺暗刻？和！- 120% ATK AOE+4张同花色牌"""
    return Skill(
        name="四幺暗刻？和！",
        type=SkillType.ULT,
        multiplier=1.20,
        damage_type=Element.QUANTUM,
        description="对敌方全体造成120%攻击力的量子属性伤害，并获得4张相同花色的琼玉牌",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
    )


def create_qingque_talent_skill() -> Skill:
    """天赋：帝垣琼玉 - 抽牌机制"""
    return Skill(
        name="帝垣琼玉",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="回合开始时随机抽取1张琼玉牌，4张相同花色进入暗杠状态，攻击力+36%",
        energy_gain=5.0,
        break_power=0,
    )


def create_qingque_passives() -> list[Passive]:
    """青雀的被动技能（行迹）"""
    return [
        # A2: 争番 - 战技恢复1点战技点（单场1次）
        Passive(
            name="争番",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="skill_point_on_special",
            value=1,
            description="施放战技时，恢复1个战技点，该效果单场战斗中只能触发1次",
        ),
        # A2: 量子伤害+3.2%，攻击力+4%
        Passive(
            name="量子伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="quantum_dmg_increase",
            value=0.032,
            description="量子属性伤害提高3.2%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            description="攻击力提高4%",
        ),
        # A3: 听牌 - 战技增伤效果额外+10%
        Passive(
            name="听牌",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="special_dmg_bonus",
            value=0.10,
            description="战技使自身造成的伤害提高效果额外提高10%",
        ),
        # A4: 攻击力+6%，量子伤害+4.8%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
        Passive(
            name="量子伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="quantum_dmg_increase",
            value=0.048,
            description="量子属性伤害提高4.8%",
        ),
        # A5: 抢杠 - 强化普攻后速度+10%持续1回合
        Passive(
            name="抢杠",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="speed_after_enhanced_basic",
            value=0.10,
            description="施放强化普攻后，青雀的速度提高10%，持续1回合",
        ),
        # A6: 防御力+7.5%，量子伤害+6.4%
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.075,
            description="防御力提高7.5%",
        ),
        Passive(
            name="量子伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="quantum_dmg_increase",
            value=0.064,
            description="量子属性伤害提高6.4%",
        ),
        # Lv75: 攻击力+4%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            description="攻击力提高4%",
        ),
        # Lv1: 攻击力+8%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.08,
            description="攻击力提高8%",
        ),
    ]


def create_all_qingque_skills() -> list[Skill]:
    return [
        create_qingque_basic_skill(),
        create_qingque_special_skill(),
        create_qingque_ult_skill(),
        create_qingque_talent_skill(),
    ]
