"""
忘归人 (Fugue) 角色技能设计

基于 https://starrailstation.com/cn/character/fugue#skills 数据

角色定位：虚无+火 - 超击破伤害

==============================
技能
==============================

【普攻】焕焕辰尾
- Break 30
- 对指定敌方单体造成等同于忘归人50%攻击力的火属性伤害

【战技】有道祥见，衔书摇风
- 使指定我方单体获得【狐祈】
- 使自身进入【炽灼】状态，持续3回合
- 持有【狐祈】的目标击破特攻提高15%
- 【狐祈】目标攻击时，忘归人有100%概率使目标防御力降低8%

【终结技】阳极照世，离火满缀
- Break 60/hit
- 对敌方全体造成100%火属性伤害
- 本次攻击无视弱点属性削减敌方全体韧性

【天赋】善盈后福，德气流布
- 敌方目标被额外附上【云火昭】（韧性上限40%）
- 我方攻击弱点击破状态敌人时，将削韧值转化为超击破伤害

==============================
机制
==============================

【狐祈】：使目标获得击破特攻提升和无视弱点削韧
【炽灼】：忘归人强化状态
【云火昭】：额外韧性，可被超击破
【超击破】：削韧值转化为伤害
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_fugue_basic_skill() -> Skill:
    """普攻：焕焕辰尾 - 50% ATK"""
    return Skill(
        name="焕焕辰尾",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成50%攻击力的火属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_fugue_special_skill() -> Skill:
    """战技：有道祥见，衔书摇风 - 【狐祈】+击破特攻"""
    return Skill(
        name="有道祥见，衔书摇风",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.FIRE,
        description="使目标获得【狐祈】：击破特攻+15%，可无视弱点削韧",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="狐祈",
    )


def create_fugue_ult_skill() -> Skill:
    """终结技：阳极照世，离火满缀 - 无视弱点削韧"""
    return Skill(
        name="阳极照世，离火满缀",
        type=SkillType.ULT,
        multiplier=1.0,
        damage_type=Element.FIRE,
        description="对敌方全体造成100%火属性伤害，无视弱点削韧",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
    )


def create_fugue_talent_skill() -> Skill:
    """天赋：善盈后福，德气流布 - 超击破"""
    return Skill(
        name="善盈后福，德气流布",
        type=SkillType.TALENT,
        multiplier=0.50,  # 超击破伤害倍率
        damage_type=Element.FIRE,
        description="攻击弱点击破目标时，削韧值转化为50%超击破伤害",
        energy_gain=0.0,
        break_power=0,
    )


def create_fugue_passives() -> list[Passive]:
    """忘归人的被动技能"""
    return [
        Passive(
            name="青丘重光",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_action_delay",
            value=0.15,
            description="弱点击破后额外使敌人行动延后15%",
        ),
        Passive(
            name="涂山玄设",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_dmg_bonus",
            value=0.30,
            description="使自身击破特攻提高30%",
        ),
        Passive(
            name="玑星太素",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="party_break_bonus",
            value=0.06,
            description="队友击破特攻+6%，最多2层",
        ),
    ]


def create_all_fugue_skills() -> list[Skill]:
    return [
        create_fugue_basic_skill(),
        create_fugue_special_skill(),
        create_fugue_ult_skill(),
        create_fugue_talent_skill(),
    ]
