"""
爻光 (Yaoguang) 角色技能设计

基于 https://starrailstation.com/cn/character/yaoguang#skills 数据

角色定位：速度型 - 消耗生命换取伤害和速度

==============================
技能
==============================

【普攻】落头鬼，暴攻
- Break 20
- 对指定敌方单体造成等同于角色80%攻击力的虚数属性伤害

【战技】身藐，身攻
- Break 30
- 消耗等同于当前生命上限30%的生命值
- 每损失1%生命值，造成的伤害提高1%
- 最高提高30%
- 对指定敌方单体造成等同于损失生命值30%的虚数属性伤害

【终结技】全体藐，魂攻
- Break 60
- 消耗100%当前生命值
- 每损失1%生命值获得3点攻击力
- 对指定敌方单体造成等同于损失生命值40%的虚数属性伤害
- 若击杀则回复100%生命上限的生命值

【天赋】互藐•速战
- 每次攻击后使自身速度提高10%
- 最多叠加5层，持续3回合

【被动】互攻•疾战
- 速度提高20%
- 每次攻击后使自身速度额外提高5%，最多叠加5层
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_yaoguang_basic_skill() -> Skill:
    """普攻：落头鬼，暴攻 - 80% ATK"""
    return Skill(
        name="落头鬼，暴攻",
        type=SkillType.BASIC,
        multiplier=0.80,
        damage_type=Element.IMAGINARY,
        description="对指定敌方单体造成等同于角色80%攻击力的虚数属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=20,
    )


def create_yaoguang_special_skill() -> Skill:
    """战技：身藐，身攻"""
    return Skill(
        name="身藐，身攻",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.30,
        damage_type=Element.IMAGINARY,
        description="消耗30%HP，每损失1%HP伤害+1%，最高30%",
        energy_gain=0.0,
        break_power=30,
    )


def create_yaoguang_ult_skill() -> Skill:
    """终结技：全体藐，魂攻"""
    return Skill(
        name="全体藐，魂攻",
        type=SkillType.ULT,
        multiplier=0.40,
        damage_type=Element.IMAGINARY,
        description="消耗100%HP，每损失1%HP获得3攻击力，造成损失值40%伤害",
        energy_gain=0.0,
        break_power=60,
    )


def create_yaoguang_passives() -> list[Passive]:
    """爻光的被动技能"""
    return [
        Passive(
            name="天赋：互藐•速战",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="speed_stack",
            value=0.10,  # 每次攻击+10%速度
            description="每次攻击后使自身速度提高10%，最多5层",
        ),
        Passive(
            name="被动：互攻•疾战",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="speed_increase",
            value=0.20,  # 20%速度
            description="速度提高20%，每次攻击额外+5%",
        ),
    ]


def create_all_yaoguang_skills() -> list[Skill]:
    return [
        create_yaoguang_basic_skill(),
        create_yaoguang_special_skill(),
        create_yaoguang_ult_skill(),
    ]
