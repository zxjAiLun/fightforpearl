"""
托帕&账账 (Topaz & Numby) 角色技能设计

基于 https://starrailstation.com/cn/character/topaz#skills 数据

角色定位：巡猎+火 - 追加攻击召唤物+负债证明

==============================
技能
==============================

【普攻】赤字…
- Break 30
- 对指定敌方单体造成等同于托帕50%攻击力的火属性伤害

【战技】支付困难？
- Break 60
- 使指定敌方单体陷入【负债证明】状态
- 使其受到的追加攻击伤害提高25%
- 使账账对该目标造成75%攻击力火属性伤害
- 施放此战技造成伤害时被视为追加攻击

【终结技】扭亏为盈！
- 消耗能量 130
- 使账账进入【涨幅惊人！】状态
- 伤害倍率提高75%，暴击伤害提高12.5%
- 当【负债证明】目标受到攻击时，账账行动提前50%
- 账账施放2次攻击后退出【涨幅惊人！】状态

【天赋】猪市？！
- 战斗开始时召唤账账
- 账账初始拥有80点速度
- 行动时发动追加攻击，对【负债证明】目标造成75%攻击力火属性伤害
- 【负债证明】目标受到追加攻击时，账账行动提前50%

【秘技】明补
- 托帕入场时召唤账账
- 账账自动搜寻范围内的普通战利品与扑满
- 主动施放秘技使下一场战斗中账账首次攻击后，托帕恢复60点能量

==============================
机制
==============================

【账账】：召唤物，追加攻击触发器
【负债证明】：核心易伤，使目标受到追加攻击伤害提高
【涨幅惊人！】：账账强化状态
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_topaz_basic_skill() -> Skill:
    """普攻：赤字… - 50% ATK"""
    return Skill(
        name="赤字…",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成50%攻击力的火属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_topaz_special_skill() -> Skill:
    """战技：支付困难？ - 负债证明+账账追加攻击"""
    return Skill(
        name="支付困难？",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.75,
        damage_type=Element.FIRE,
        description="使目标陷入【负债证明】：追加攻击伤害+25%，账账造成75%ATK火伤害（追加攻击）",
        energy_gain=30.0,
        break_power=60,
    )


def create_topaz_ult_skill() -> Skill:
    """终结技：扭亏为盈！ - 账账强化"""
    return Skill(
        name="扭亏为盈！",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.FIRE,
        description="账账进入【涨幅惊人！】：伤害倍率+75%，暴击伤害+12.5%，攻击后行动提前50%",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="涨幅惊人",
        target_count=-1,
    )


def create_topaz_talent_skill() -> Skill:
    """天赋：猪市？！ - 账账追加攻击"""
    return Skill(
        name="猪市？！",
        type=SkillType.TALENT,
        multiplier=0.75,
        damage_type=Element.FIRE,
        description="账账对【负债证明】目标发动追加攻击，造成75%ATK火伤害，行动提前50%",
        energy_gain=0.0,
        break_power=60,
    )


def create_topaz_passives() -> list[Passive]:
    """托帕的被动技能"""
    return [
        Passive(
            name="透支",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="basic_as_follow_up",
            value=1.0,
            description="托帕施放普攻造成伤害时，被视为发动了追加攻击",
        ),
        Passive(
            name="金融动荡",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_against_weakness",
            value=0.15,
            description="托帕和账账对拥有火属性弱点的敌方目标造成的伤害提高15%",
        ),
        Passive(
            name="技术性调整",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_after_follow_up",
            value=10.0,
            description="账账处于【涨幅惊人！】状态施放攻击后，额外使托帕恢复10点能量",
        ),
        Passive(
            name="善意收购",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_after_numby_action",
            value=5.0,
            description="账账自身行动并发动攻击后，托帕恢复5点能量",
        ),
        Passive(
            name="敏捷处理",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="topaz_advance_on_numby_start",
            value=0.20,
            description="账账自身回合开始时，托帕的行动提前20%",
        ),
        Passive(
            name="激励机制",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="extra_attack_and_res_pen",
            value=1.0,
            description="账账【涨幅惊人！】攻击次数+1次，火属性抗性穿透+10%",
        ),
    ]


def create_all_topaz_skills() -> list[Skill]:
    return [
        create_topaz_basic_skill(),
        create_topaz_special_skill(),
        create_topaz_ult_skill(),
        create_topaz_talent_skill(),
    ]
