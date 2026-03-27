"""
银枝 (Argenti) 角色技能设计

基于 https://starrailstation.com/cn/character/argenti#skills 数据

角色定位：智识+物理 - 能量积累型AOE输出

==============================
技能
==============================

【普攻】芬芳一现
- Break 30
- 对指定敌方单体造成等同于银枝50%攻击力的物理属性伤害

【战技】公正，此处盛放
- Break 30/hit
- 对敌方全体造成60%攻击力物理属性伤害

【终结技】驻于花庭，赐与尽美
- 消耗能量 90
- Break 60/hit
- 对敌方全体造成96%攻击力物理属性伤害

【强化终结技】「驻「我」华庭，授予至勋」
- 消耗能量 180
- Break 60/hit
- 对敌方全体造成168%攻击力物理属性伤害
- 额外造成6次伤害，每次对随机单体造成57%攻击力物理属性伤害

【天赋】崇高的客体
- 施放普攻、战技、终结技时，每击中1个敌方目标
- 为银枝恢复3点能量并获得1层【升格】
- 【升格】：暴击率+1%，最多叠加10层

【秘技】纯粹高洁宣言
- 使区域内敌人陷入10秒晕眩
- 进入战斗时对敌方全体造成80%攻击力物理伤害
- 银枝恢复15点能量

==============================
机制
==============================

【升格】：暴击率提升，最多10层
【强化终结技】：180能量高消耗版，额外6次随机单体伤害
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_argenti_basic_skill() -> Skill:
    """普攻：芬芳一现 - 50% ATK"""
    return Skill(
        name="芬芳一现",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.PHYSICAL,
        description="对指定敌方单体造成50%攻击力的物理属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_argenti_special_skill() -> Skill:
    """战技：公正，此处盛放 - AOE"""
    return Skill(
        name="公正，此处盛放",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.60,
        damage_type=Element.PHYSICAL,
        description="对敌方全体造成60%攻击力的物理属性伤害",
        energy_gain=30.0,
        break_power=30,
        target_count=-1,
        aoe_multiplier=0.8,
    )


def create_argenti_ult_skill() -> Skill:
    """终结技：驻于花庭，赐与尽美 - AOE"""
    return Skill(
        name="驻于花庭，赐与尽美",
        type=SkillType.ULT,
        multiplier=0.96,
        damage_type=Element.PHYSICAL,
        description="消耗90能量，对敌方全体造成96%攻击力物理伤害",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )


def create_argenti_enhanced_ult_skill() -> Skill:
    """强化终结技：「驻「我」华庭，授予至勋」"""
    return Skill(
        name="「驻「我」华庭，授予至勋」",
        type=SkillType.ULT,
        multiplier=1.68,  # 基础168%
        damage_type=Element.PHYSICAL,
        description="消耗180能量，对敌方全体造成168%伤害+6次57%随机单体伤害",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )


def create_argenti_talent_skill() -> Skill:
    """天赋：崇高的客体 - 升格叠层"""
    return Skill(
        name="崇高的客体",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.PHYSICAL,
        description="每击中1个敌方目标恢复3能量并获得1层【升格】：暴击率+1%，最多10层",
        energy_gain=3.0,
        break_power=0,
    )


def create_argenti_passives() -> list[Passive]:
    """银枝的被动技能"""
    return [
        Passive(
            name="虔诚",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="start_of_fight_stack",
            value=1.0,
            description="回合开始时，立即获得1层【升格】；物理伤害+3.2%，攻击力+4%",
        ),
        Passive(
            name="慷慨",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_on_battle_start",
            value=2.0,
            description="在敌方目标进入战斗时，自身立即恢复2点能量",
        ),
        Passive(
            name="勇气",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_against_low_hp",
            value=0.15,
            description="对当前HP%≤50%的敌方目标造成的伤害提高15%",
        ),
        Passive(
            name="审美王国的缺口",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_per_stack",
            value=0.04,
            description="每层【升格】额外使暴击伤害提高4%",
        ),
        Passive(
            name="玛瑙石的谦卑",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dot_dmg_boost",
            value=0.40,
            description="施放终结技时，若敌方≥3个，攻击力提高40%，持续1回合",
        ),
    ]


def create_all_argenti_skills() -> list[Skill]:
    return [
        create_argenti_basic_skill(),
        create_argenti_special_skill(),
        create_argenti_ult_skill(),
        create_argenti_enhanced_ult_skill(),
        create_argenti_talent_skill(),
    ]
