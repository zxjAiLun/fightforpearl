"""
不死途 (Ashveil) 角色技能设计

基于 https://starrailstation.com/cn/character/ashveil#skills 数据

角色定位：生存型 - 消耗生命值换取护盾和伤害

==============================
技能
==============================

【普攻】银枪，冲刺攻击
- Break 20
- 对指定敌方单体造成等同于角色50%生命上限+25%攻击力的量子属性伤害

【战技】残谱，血牛
- Break 30
- 消耗等同于生命上限40%的生命值
- 生命值降至1点时获得100%生命上限的护盾
- 护盾存在期间，使指定敌方单体速度降低50%，持续3回合
- 施放后获得100%生命上限50%的生命恢复

【终结技】绝息，锁命缚
- Break 60
- 消耗100%当前生命值
- 每损失1%生命值获得3点防御力
- 对指定敌方单体造成等同于损失生命值30%的量子属性伤害
- 若击败目标则回复100%生命值

【天赋】冥息，万物终焉
- 我方全体每损失1点生命值，角色获得1点护盾
- 每损失1点生命值，角色防御力提高2点
- 最多通过生命值损失获得500点护盾和1000点防御力

【被动】收息，永劫归烬
- 生命值归零时不会倒下，而是在生命值归零的基础上获得等同于100%生命上限的护盾
- 该护盾存在期间，角色受到致命伤害时免疫该伤害并恢复等同于100%生命上限的生命值
- 该护盾存在2回合后破碎

==============================
死途机制
==============================

【烬化】
- 生命值消耗转化为伤害提升
- 每消耗1%生命值，伤害提升1%，最多100%
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 不死途技能 ==============

def create_ashveil_basic_skill() -> Skill:
    """普攻：银枪，冲刺攻击 - 50% Max HP + 25% ATK"""
    return Skill(
        name="银枪，冲刺攻击",
        type=SkillType.BASIC,
        multiplier=0.50,  # 50% Max HP
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成等同于角色50%生命上限+25%攻击力的量子属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=20,
    )


def create_ashveil_special_skill() -> Skill:
    """战技：残谱，血牛 - 消耗40% HP换护盾+降速"""
    return Skill(
        name="残谱，血牛",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,  # 不造成伤害
        damage_type=Element.QUANTUM,
        description="消耗40%HP获得护盾，护盾期间降低敌人50%速度",
        energy_gain=0.0,
        break_power=30,
        is_support_skill=True,
        support_modifier_name="血牛护盾",
    )


def create_ashveil_ult_skill() -> Skill:
    """大招：绝息，锁命缚 - 消耗100% HP换伤害"""
    return Skill(
        name="绝息，锁命缚",
        type=SkillType.ULT,
        multiplier=0.30,  # 30% * 损失生命值%
        damage_type=Element.QUANTUM,
        description="消耗100%当前HP，每损失1%获得3防御，对目标造成损失值30%的伤害",
        energy_gain=0.0,
        break_power=60,
    )


def create_ashveil_passives() -> list[Passive]:
    """不死途的被动技能"""
    return [
        Passive(
            name="天赋：冥息，万物终焉",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="shield_from_hp_loss",
            value=1.0,  # 每损失1HP获得1护盾
            description="损失HP获得护盾和防御力",
        ),
        Passive(
            name="被动：收息，永劫归烬",
            trigger=SkillType.FALLING_PASSIVE,
            effect_type="immortal_shield",
            value=1.0,  # 100% Max HP护盾
            description="生命归零时不倒下，获得100%MaxHP护盾",
        ),
    ]


def create_all_ashveil_skills() -> list[Skill]:
    """创建不死途所有技能"""
    return [
        create_ashveil_basic_skill(),
        create_ashveil_special_skill(),
        create_ashveil_ult_skill(),
    ]
