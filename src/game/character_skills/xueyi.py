"""
雪衣 (Xueyi) 角色技能设计

基于 https://starrailstation.com/cn/character/xueyi#skills 数据

角色定位：毁灭+量子 - 弹射追加攻击

==============================
技能
==============================

【普攻】破魔锥
- Break 30
- 对指定敌方单体造成等同于雪衣50%攻击力的量子属性伤害

【战技】摄伏诸恶
- Break 60 + 30/adjacent
- 对指定敌方单体造成70%攻击力量子属性伤害
- 对相邻目标造成35%攻击力量子属性伤害

【终结技】天罚贯身
- 消耗能量 120
- Break 120
- 对指定敌方单体造成150%攻击力量子属性伤害
- 本次攻击无视弱点属性削减敌方单体的韧性
- 击破弱点时触发量子属性弱点击破效果
- 削韧越多伤害越高，最多提高36%

【天赋】十王圣断，业报恒常
- 雪衣施放攻击削减敌方韧性时，叠加【恶报】层数
- 队友削减韧性时，雪衣叠加1层【恶报】
- 【恶报】叠至上限时，立即发动追加攻击
- 追加攻击：对敌方随机单体造成3次45%攻击力量子属性伤害

【秘技】斩立决
- Break 60
- 进入战斗后对敌方全体造成80%攻击力量子属性伤害

==============================
机制
==============================

【恶报】：雪衣的核心机制，削韧叠层，满层触发追加攻击
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_xueyi_basic_skill() -> Skill:
    """普攻：破魔锥 - 50% ATK"""
    return Skill(
        name="破魔锥",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成50%攻击力的量子属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_xueyi_special_skill() -> Skill:
    """战技：摄伏诸恶 - 扩散伤害"""
    return Skill(
        name="摄伏诸恶",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.70,
        damage_type=Element.QUANTUM,
        description="对主目标70%ATK+相邻目标35%ATK量子属性伤害",
        energy_gain=30.0,
        break_power=60,
        target_count=2,
        aoe_multiplier=0.5,
    )


def create_xueyi_ult_skill() -> Skill:
    """终结技：天罚贯身 - 高伤害无视弱点"""
    return Skill(
        name="天罚贯身",
        type=SkillType.ULT,
        multiplier=1.50,  # 150% ATK
        damage_type=Element.QUANTUM,
        description="造成150%ATK量子伤害，无视弱点削韧，削韧越多伤害越高（最多+36%）",
        energy_gain=5.0,
        break_power=120,
    )


def create_xueyi_talent_skill() -> Skill:
    """天赋：十王圣断，业报恒常 - 恶报追加攻击"""
    return Skill(
        name="十王圣断，业报恒常",
        type=SkillType.TALENT,
        multiplier=0.45,  # 3 hits × 45%
        damage_type=Element.QUANTUM,
        description="【恶报】叠满时触发追加攻击：对随机单体3次45%ATK量子伤害",
        energy_gain=2.0,
        break_power=15,
    )


def create_xueyi_passives() -> list[Passive]:
    """雪衣的被动技能"""
    return [
        Passive(
            name="预兆机杼",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_to_dmg",
            value=2.40,
            description="造成的伤害提高，提高数值等同于击破特攻的100%，最多+240%",
        ),
        Passive(
            name="摧锋轴承",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_against_full_toughness",
            value=0.10,
            description="若敌方当前韧性≥50%，终结技伤害提高10%",
        ),
        Passive(
            name="伺观中枢",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="overflow_stack",
            value=6.0,
            description="累计溢出的【恶报】层数（最多6层），触发天赋后获得溢出层数",
        ),
        Passive(
            name="缚心魔",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="follow_up_dmg_boost",
            value=0.40,
            description="天赋的追加攻击造成的伤害提高40%",
        ),
        Passive(
            name="破五尘",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="follow_up_ignore_weakness",
            value=1.0,
            description="追加攻击无视弱点属性削韧，并恢复5%HP，击破弱点触发量子弱点击破",
        ),
    ]


def create_all_xueyi_skills() -> list[Skill]:
    return [
        create_xueyi_basic_skill(),
        create_xueyi_special_skill(),
        create_xueyi_ult_skill(),
        create_xueyi_talent_skill(),
    ]
