"""
虎克 (Hook) 角色技能设计

基于 https://starrailstation.com/cn/character/hook#skills 数据

角色定位：毁灭型 - 火属性灼烧输出

==============================
关键机制
==============================

【灼烧DOT】
- 战技/强化战技附加灼烧状态，持续2回合
- 灼烧：每回合受到25% ATK火属性持续伤害
- 秘技灼烧持续3回合，每回合50% ATK火属性持续伤害

【强化战技】
- 终结技后下一次战技变为强化战技
- 强化战技：AOE，对相邻目标造成40% ATK伤害

【天赋：火上浇油】
- 攻击灼烧目标时追加50% ATK附加伤害
- 额外恢复5点能量

==============================
技能
==============================

【普攻】喂！小心火烛
- 50% ATK 单体火伤

【战技】嘿！记得虎克吗
- 120% ATK 单体火伤
- 100%基础概率灼烧2回合

【强化战技】嘿！记得虎克吗（扩散）
- 140% ATK 单体火伤
- 100%基础概率灼烧2回合
- 对相邻目标造成40% ATK火伤

【终结技】轰！飞来焰火
- 240% ATK 单体火伤
- 下一次战技变为强化战技

【天赋】哈！火上浇油
- 攻击灼烧目标时追加50% ATK火属性附加伤害
- 额外恢复5点能量

【秘技】哎！瞧这一团糟
- 战斗开始：单体50% ATK火伤
- 敌方全体100%灼烧3回合
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_hook_basic_skill() -> Skill:
    """普攻：喂！小心火烛 - 50% ATK 单体火伤"""
    return Skill(
        name="喂！小心火烛",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成50%攻击力的火属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_hook_special_skill() -> Skill:
    """战技：嘿！记得虎克吗 - 120% ATK 单体+灼烧"""
    return Skill(
        name="嘿！记得虎克吗",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.20,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成120%攻击力的火属性伤害，100%基础概率灼烧2回合",
        energy_gain=30.0,
        break_power=60,
    )


def create_hook_enhanced_special_skill() -> Skill:
    """强化战技：嘿！记得虎克吗（扩散）- 140% ATK AOE+灼烧"""
    return Skill(
        name="嘿！记得虎克吗（扩散）",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.40,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成140%攻击力火属性伤害，对相邻目标造成40%攻击力火属性伤害，100%灼烧2回合",
        energy_gain=30.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=0.40,
    )


def create_hook_ult_skill() -> Skill:
    """终结技：轰！飞来焰火 - 240% ATK 单体火伤+强化战技"""
    return Skill(
        name="轰！飞来焰火",
        type=SkillType.ULT,
        multiplier=2.40,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成240%攻击力的火属性伤害，下一次战技得到强化",
        energy_gain=5.0,
        break_power=90,
        is_support_skill=True,
        support_modifier_name="战技强化",
    )


def create_hook_talent_skill() -> Skill:
    """天赋：哈！火上浇油 - 灼烧追加伤害"""
    return Skill(
        name="哈！火上浇油",
        type=SkillType.TALENT,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="攻击灼烧状态的敌方目标时，追加50%攻击力火属性附加伤害，额外恢复5点能量",
        energy_gain=5.0,
        break_power=30,
    )


def create_hook_passives() -> list[Passive]:
    """虎克的被动技能（行迹）"""
    return [
        # A2: 童真 - 触发天赋时回复5% HP
        Passive(
            name="童真",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="talent_hp_heal",
            value=0.05,
            description="触发天赋时，回复5%生命上限的生命值",
        ),
        # A2: 生命值+4%，暴击伤害+5.3%
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="max_hp_increase",
            value=0.04,
            description="生命值提高4%",
        ),
        Passive(
            name="暴击伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.053,
            description="暴击伤害提高5.3%",
        ),
        # A3: 无邪 - 控制抵抗+35%
        Passive(
            name="无邪",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="control_res",
            value=0.35,
            description="抵抗控制类负面状态的概率提高35%",
        ),
        # A4: 暴击伤害+8%，生命值+6%
        Passive(
            name="暴击伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.08,
            description="暴击伤害提高8%",
        ),
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="max_hp_increase",
            value=0.06,
            description="生命值提高6%",
        ),
        # A5: 玩火 - 终结技后行动提前20%+额外恢复5能
        Passive(
            name="玩火",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="ult_advance_and_energy",
            value=0.20,
            description="施放终结技后，行动提前20%并额外恢复5点能量",
        ),
        # A6: 暴击伤害+8%，生命值+8%
        Passive(
            name="暴击伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.08,
            description="暴击伤害提高8%",
        ),
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="max_hp_increase",
            value=0.08,
            description="生命值提高8%",
        ),
        # Lv75: 暴击伤害+10.7%
        Passive(
            name="暴击伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.107,
            description="暴击伤害提高10.7%",
        ),
        # Lv80: 暴击伤害+5.3%
        Passive(
            name="暴击伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.053,
            description="暴击伤害提高5.3%",
        ),
    ]


def create_all_hook_skills() -> list[Skill]:
    return [
        create_hook_basic_skill(),
        create_hook_special_skill(),
        create_hook_ult_skill(),
        create_hook_talent_skill(),
    ]
