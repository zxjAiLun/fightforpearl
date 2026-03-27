"""
桂乃芬 (Guinaifen) 角色技能设计

基于 https://starrailstation.com/cn/character/guinaifen#skills 数据

角色定位：虚无+火 - 灼烧DOT+易伤叠加

==============================
技能
==============================

【普攻】劈头满堂彩
- Break 30
- 对指定敌方单体造成等同于桂乃芬50%攻击力的火属性伤害

【战技】迎面开门红
- Break 60 + 30/adjacent
- 对指定敌方单体造成60%攻击力火属性伤害
- 对相邻目标造成20%攻击力火属性伤害
- 100%基础概率使目标陷入灼烧状态

【终结技】给您来段看家戏
- 消耗能量 120
- 对敌方全体造成72%攻击力火属性伤害
- 若目标处于灼烧状态，立即触发一次灼烧伤害（72%）

【天赋】古来君子养艺人
- 敌方灼烧触发后，100%概率陷入【吞火】状态
- 【吞火】：受到的伤害提高4%，持续3回合，最多叠加3层

【秘技】耍耍把式卖卖艺
- Break 60
- 进入战斗后造成4次伤害，每次对随机单体造成50%攻击力火属性伤害
- 100%基础概率使目标陷入【吞火】状态

==============================
机制
==============================

【灼烧】：每回合开始受到83.9%攻击力火属性持续伤害，持续2回合
【吞火】：增伤易伤debuff，最多3层
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_guinaifen_basic_skill() -> Skill:
    """普攻：劈头满堂彩 - 50% ATK"""
    return Skill(
        name="劈头满堂彩",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成50%攻击力的火属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_guinaifen_special_skill() -> Skill:
    """战技：迎面开门红 - 扩散灼烧"""
    return Skill(
        name="迎面开门红",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.60,
        damage_type=Element.FIRE,
        description="对主目标60%ATK+相邻目标20%ATK火伤害，100%施加灼烧状态",
        energy_gain=30.0,
        break_power=60,
        target_count=2,
        aoe_multiplier=0.33,
    )


def create_guinaifen_ult_skill() -> Skill:
    """终结技：给您来段看家戏 - AOE+灼烧引爆"""
    return Skill(
        name="给您来段看家戏",
        type=SkillType.ULT,
        multiplier=0.72,
        damage_type=Element.FIRE,
        description="对敌方全体造成72%ATK火属性伤害，灼烧目标额外触发72%伤害",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )


def create_guinaifen_talent_skill() -> Skill:
    """天赋：古来君子养艺人 - 吞火易伤"""
    return Skill(
        name="古来君子养艺人",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.FIRE,
        description="灼烧触发后敌方100%陷入【吞火】：受伤+4%/层，持续3回合，最多3层",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
    )


def create_guinaifen_passives() -> list[Passive]:
    """桂乃芬的被动技能"""
    return [
        Passive(
            name="缘竿",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="burn_on_basic",
            value=0.80,
            description="普攻有80%基础概率施加灼烧状态",
        ),
        Passive(
            name="投狭",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="action_advance",
            value=0.25,
            description="战斗开始时，桂乃芬的行动提前25%",
        ),
        Passive(
            name="逾锋",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_against_burning",
            value=0.20,
            description="对陷入灼烧状态的敌方目标造成的伤害提高20%",
        ),
        Passive(
            name="吞剑通脊背",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="stack_extension",
            value=1.0,
            description="使【吞火】的可叠加层数增加1层（最多4层）",
        ),
        Passive(
            name="胸口碎大石",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_on_dot",
            value=2.0,
            description="灼烧状态每触发一次伤害，使自身恢复2点能量",
        ),
    ]


def create_all_guinaifen_skills() -> list[Skill]:
    return [
        create_guinaifen_basic_skill(),
        create_guinaifen_special_skill(),
        create_guinaifen_ult_skill(),
        create_guinaifen_talent_skill(),
    ]
