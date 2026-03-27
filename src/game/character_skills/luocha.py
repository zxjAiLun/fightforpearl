"""
罗刹 (Luocha) - 崩坏：星穹铁道

角色定位：丰饶·虚数 - 治疗 + 结界

关键机制：
1. 普攻：单体虚数伤害
2. 战技：单体治疗 + 被动触发（队友HP<=50%时自动治疗）
3. 终结技：群体虚数伤害 + 驱散 + 获得【白花之刻】
4. 天赋：2层【白花之刻】展开结界，我方攻击回血
5. 秘技：战斗开始立即触发天赋展开结界

虚数属性关联：虚数属性伤害、效果命中
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_luocha_basic_skill() -> Skill:
    """普攻：黑渊的棘刺 - 50% ATK"""
    return Skill(
        name="黑渊的棘刺",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.IMAGINARY,
        description="对指定敌方单体造成50%攻击力的虚数属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_luocha_special_skill() -> Skill:
    """战技：白花的祈望 - 单体治疗"""
    return Skill(
        name="白花的祈望",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.IMAGINARY,
        description="为指定我方单体回复40%攻击力+200的生命值，获得1层【白花之刻】；队友HP<=50%时自动触发",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="白花的祈望-治疗",
    )


def create_luocha_ult_skill() -> Skill:
    """终结技：归葬的遂愿 - 群体伤害+驱散"""
    return Skill(
        name="归葬的遂愿",
        type=SkillType.ULT,
        multiplier=1.20,
        damage_type=Element.IMAGINARY,
        description="解除敌方全体1个增益，对敌方全体造成120%攻击力虚数伤害，获得1层【白花之刻】",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )


def create_luocha_talent_skill() -> Skill:
    """天赋：生息的轮转 - 结界展开"""
    return Skill(
        name="生息的轮转",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.IMAGINARY,
        description="【白花之刻】达2层时消耗全部展开结界，我方攻击后回血12%攻击力+60，持续2回合",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="生息的轮转-结界",
    )


def create_luocha_technique_skill() -> Skill:
    """秘技：愚者的悲悯 - 开场结界"""
    return Skill(
        name="愚者的悲悯",
        type=SkillType.FESTIVITY,
        cost=0,
        multiplier=0.0,
        damage_type=Element.IMAGINARY,
        description="进入战斗后立即触发天赋【生息的轮转】展开结界",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="愚者的悲悯-结界",
    )


def create_luocha_passives() -> list[Passive]:
    """创建罗刹的行迹被动"""
    return [
        # A2: 浸池苏生 - 战技治疗时解除目标1个负面效果
        Passive(
            name="浸池苏生",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="cure_debuff_on_heal",
            value=1.0,
            duration=0,
            description="触发战技效果时，解除指定我方单体的1个负面效果",
        ),
        # A2: 生命值+4%，攻击力+4%
        Passive(
            name="生命值强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_pct_increase",
            value=0.04,
            duration=0,
            description="生命值+4%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            duration=0,
            description="攻击力+4%",
        ),
        # A3: 浇灌尘身 - 结界中队友攻击后其他人也回血
        Passive(
            name="浇灌尘身",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="party_heal_on_attack",
            value=0.07,
            duration=0,
            description="处于结界中，敌方受攻击后除攻击者外的我方目标也回复7%攻击力+93的生命",
        ),
        # A4: 攻击力+6%，生命值+6%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            duration=0,
            description="攻击力+6%",
        ),
        Passive(
            name="生命值强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_pct_increase",
            value=0.06,
            duration=0,
            description="生命值+6%",
        ),
        # A5: 行过幽谷 - 效果抵抗+70%
        Passive(
            name="行过幽谷",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.70,
            duration=0,
            description="抵抗控制类负面状态的概率提高70%",
        ),
        # A6: 防御力+7.5%，生命值+8%
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.075,
            duration=0,
            description="防御力+7.5%",
        ),
        Passive(
            name="生命值强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_pct_increase",
            value=0.08,
            duration=0,
            description="生命值+8%",
        ),
    ]


def create_all_luocha_skills() -> list[Skill]:
    """创建罗刹所有技能"""
    return [
        create_luocha_basic_skill(),
        create_luocha_special_skill(),
        create_luocha_ult_skill(),
        create_luocha_talent_skill(),
        create_luocha_technique_skill(),
    ]
