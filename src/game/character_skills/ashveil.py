"""
不死途 (Ashveil) 角色技能设计

基于 https://starrailstation.com/cn/character/ashveil#skills 数据

角色定位：巡猎型 - 雷属性追踪猎手

==============================
技能
==============================

【普攻】利爪，授以礼仪
- Break 30
- 对指定敌方单体造成等同于不死途50%攻击力的雷属性伤害

【战技】鞭哨，逐尽恶兽
- Break 60
- 使指定敌方单体成为【饲饵】，造成100% ATK伤害
- 若目标为【饲饵】，额外造成50% ATK伤害并恢复1点战技点
- 场上存在【饲饵】时，敌方全体防御力降低20%

【终结技】飨宴，自始无终
- Break 90
- 使目标成为【饲饵】，造成200% ATK伤害
- 随后发动1次获得强化的天赋追加攻击
- 获得3点充能

【天赋】宿怨，切齿奉还
- 不死途初始拥有2点充能，最多3点
- 【饲饵】受到攻击后，不死途消耗1点充能发动追加攻击
- 造成100% ATK雷属性伤害，随后获得2层【婪酣】(最多12层)
- 每消耗4层【婪酣】可额外造成1次100% ATK伤害

==============================
机制
==============================

【饲饵】：被标记的目标，受到不死途的追踪攻击

【充能】：初始2点，最多3点，用于发动追加攻击

【婪酣】：叠加层数，提高追加攻击伤害
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_ashveil_basic_skill() -> Skill:
    """普攻：利爪，授以礼仪 - 50% ATK"""
    return Skill(
        name="利爪，授以礼仪",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.THUNDER,
        description="对指定敌方单体造成50%攻击力的雷属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_ashveil_special_skill() -> Skill:
    """战技：鞭哨，逐尽恶兽 - 使目标成为【饲饵】"""
    return Skill(
        name="鞭哨，逐尽恶兽",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.0,  # 100% ATK
        damage_type=Element.THUNDER,
        description="使目标成为【饲饵】，造成100% ATK伤害，若已是【饲饵】额外50% ATK+回1战技点",
        energy_gain=30.0,
        break_power=60,
    )


def create_ashveil_ult_skill() -> Skill:
    """终结技：飨宴，自始无终 - 200% ATK + 强化追加"""
    return Skill(
        name="飨宴，自始无终",
        type=SkillType.ULT,
        multiplier=2.0,  # 200% ATK
        damage_type=Element.THUNDER,
        description="对目标造成200% ATK伤害，发动强化天赋追加攻击，获得3点充能",
        energy_gain=5.0,
        break_power=90,
    )


def create_ashveil_talent_skill() -> Skill:
    """天赋：宿怨，切齿奉还 - 追加攻击"""
    return Skill(
        name="宿怨，切齿奉还",
        type=SkillType.TALENT,
        multiplier=1.0,  # 100% ATK追加攻击
        damage_type=Element.THUNDER,
        description="消耗1充能对【饲饵】发动追加攻击，造成100% ATK伤害，获得2层【婪酣】",
        energy_gain=5.0,
        break_power=15,
    )


def create_ashveil_passives() -> list[Passive]:
    """不死途的被动技能"""
    return [
        Passive(
            name="罪途",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="lanhan_stack",
            value=1.0,  # 战技/终结技获得【婪酣】
            description="施放战技/终结技时获得【婪酣】层数",
        ),
        Passive(
            name="影肢",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="follow_up_dmg_bonus",
            value=0.80,  # +80%追加攻击伤害
            description="追加攻击伤害提高80%，每层【婪酣】额外+10%",
        ),
        Passive(
            name="头狼",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_bonus",
            value=0.40,  # +40%暴击伤害
            description="我方全体暴击伤害+40%，追加攻击暴击伤害+80%",
        ),
    ]


def create_all_ashveil_skills() -> list[Skill]:
    return [
        create_ashveil_basic_skill(),
        create_ashveil_special_skill(),
        create_ashveil_ult_skill(),
        create_ashveil_talent_skill(),
    ]
