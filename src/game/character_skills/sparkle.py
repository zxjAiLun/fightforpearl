"""
花火 (Sparkle) 角色技能设计

基于 https://starrailstation.com/cn/character/sparkle#skills 数据

角色定位：同谐型 - 量子属性，爆伤辅助+战技点驱动

==============================
技能
==============================

【普攻】独角戏
- Break 30
- 对指定敌方单体造成等同于花火50%攻击力的量子属性伤害

【战技】梦游鱼
- 使指定我方单体的暴击伤害提高
- 提高数值等同于花火12%暴击伤害+27%
- 持续1回合
- 使该目标行动提前50%
- 当花火对自身施放时，无法触发行动提前效果

【终结技】一人千役
- 消耗能量 110
- 为我方恢复4个战技点
- 使我方全体获得【谜诡】
- 持有【谜诡】的目标触发花火天赋伤害提高效果时，每层额外提高6%

【天赋】叙述性诡计
- 花火在场时，战技点上限额外增加2点
- 当我方目标每消耗1点战技点
- 使我方全体造成的伤害提高3%
- 该效果持续2回合，最多可叠加3层

【秘技】不可靠叙事者
- 使用秘技后，我方全体进入持续20秒的【迷误】状态
- 【迷误】状态下不会被敌人发现
- 【迷误】状态期间进入战斗时为我方恢复3个战技点

==============================
机制
==============================

【谜诡】：花火终结技给予的增益状态

【迷误】：秘技给予的隐身状态

【战技点驱动】：消耗战技点触发伤害提高效果
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_sparkle_basic_skill() -> Skill:
    """普攻：独角戏 - 50% ATK"""
    return Skill(
        name="独角戏",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成50%攻击力的量子属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_sparkle_special_skill() -> Skill:
    """战技：梦游鱼 - 爆伤提高+拉条"""
    return Skill(
        name="梦游鱼",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="使指定我方单体暴击伤害提高(花火12%暴击伤害+27%)，行动提前50%",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="梦游鱼",
    )


def create_sparkle_ult_skill() -> Skill:
    """终结技：一人千役 - 回战技点+【谜诡】"""
    return Skill(
        name="一人千役",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="为我方恢复4个战技点，使我方全体获得【谜诡】",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="谜诡",
        target_count=-1,
    )


def create_sparkle_talent_skill() -> Skill:
    """天赋：叙述性诡计 - 战技点消耗增伤"""
    return Skill(
        name="叙述性诡计",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="每消耗1点战技点使我方全体伤害+3%，最多3层持续2回合",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
    )


def create_sparkle_passives() -> list[Passive]:
    """花火的被动技能"""
    return [
        Passive(
            name="岁时记",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_on_basic",
            value=10.0,  # 普攻额外恢复10能量
            description="施放普攻时额外恢复10点能量",
        ),
        Passive(
            name="人造花",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_duration_extend",
            value=1.0,  # 延长战技爆伤效果
            description="战技提供的暴击伤害提高效果会延长到目标下一个回合开始",
        ),
        Passive(
            name="夜想曲",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_bonus",
            value=0.15,  # 我方全体攻击力+15%
            description="我方全体攻击力+15%，量子角色额外+5%/15%/30%",
        ),
    ]


def create_all_sparkle_skills() -> list[Skill]:
    return [
        create_sparkle_basic_skill(),
        create_sparkle_special_skill(),
        create_sparkle_ult_skill(),
        create_sparkle_talent_skill(),
    ]
