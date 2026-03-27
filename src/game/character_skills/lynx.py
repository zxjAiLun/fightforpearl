"""
玲可 (Lynx) - 崩坏：星穹铁道

角色定位：丰饶·量子 - 治疗 + 护盾

关键机制：
1. 普攻：单体量子伤害（基于生命值上限）
2. 战技：单体治疗 + 【求生反应】提高生命上限
3. 终结技：全体治疗 + 驱散
4. 天赋：战技/终结技附加持续治疗
5. 秘技：开场全队附加持续治疗

量子属性关联：量子属性伤害、效果命中
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_lynx_basic_skill() -> Skill:
    """普攻：冰攀前齿技术 - 25% HP上限"""
    return Skill(
        name="冰攀前齿技术",
        type=SkillType.BASIC,
        multiplier=0.25,
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成等同于玲可25%生命上限的量子属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_lynx_special_skill() -> Skill:
    """战技：盐渍野营罐头 - 治疗+护盾"""
    return Skill(
        name="盐渍野营罐头",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="为指定我方单体附加【求生反应】，提高5%生命上限+50的的生命上限，回避大幅提高，持续2回合，回复8%生命上限+80的生命值",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="盐渍野营罐头-求生反应",
    )


def create_lynx_ult_skill() -> Skill:
    """终结技：雪原急救方案 - 全体治疗+驱散"""
    return Skill(
        name="雪原急救方案",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="解除我方全体1个负面效果，立即回复9%生命上限+90的生命值",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="雪原急救方案",
        target_count=-1,
    )


def create_lynx_talent_skill() -> Skill:
    """天赋：户外生存经验 - 持续治疗"""
    return Skill(
        name="户外生存经验",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="施放战技或终结技时，我方目标获得2回合持续治疗，每回合回复2.4%生命上限+24，持有【求生反应】时额外回复3%生命上限+30",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="户外生存经验-持续治疗",
    )


def create_lynx_technique_skill() -> Skill:
    """秘技：巧克力能量棒 - 开场持续治疗"""
    return Skill(
        name="巧克力能量棒",
        type=SkillType.FESTIVITY,
        cost=0,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="战斗开始时为我方全体附加天赋的持续治疗效果，持续2回合",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="巧克力能量棒-开场治疗",
    )


def create_lynx_passives() -> list[Passive]:
    """创建玲可的行迹被动"""
    return [
        # A2: 提前勘测 - 求生反应目标受攻击时恢复2能量
        Passive(
            name="提前勘测",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_restore_on_hit",
            value=2.0,
            duration=0,
            description="持有【求生反应】的目标受到攻击后，玲可立即恢复2点能量",
        ),
        # A2: 防御力+5%，生命值+4%
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.05,
            duration=0,
            description="防御力+5%",
        ),
        Passive(
            name="生命值强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_pct_increase",
            value=0.04,
            duration=0,
            description="生命值+4%",
        ),
        # A3: 探险技术 - 效果抵抗+35%
        Passive(
            name="探险技术",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.35,
            duration=0,
            description="抵抗控制类负面状态的概率提高35%",
        ),
        # A4: 生命值+6%，防御力+7.5%
        Passive(
            name="生命值强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_pct_increase",
            value=0.06,
            duration=0,
            description="生命值+6%",
        ),
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.075,
            duration=0,
            description="防御力+7.5%",
        ),
        # A5: 极境求生 - 持续治疗延长1回合
        Passive(
            name="极境求生",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="heal_duration_extend",
            value=1.0,
            duration=0,
            description="天赋产生的持续回复效果延长1回合",
        ),
        # A6: 效果抵抗+6%，防御力+10%
        Passive(
            name="效果抵抗强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.06,
            duration=0,
            description="效果抵抗+6%",
        ),
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.10,
            duration=0,
            description="防御力+10%",
        ),
    ]


def create_all_lynx_skills() -> list[Skill]:
    """创建玲可所有技能"""
    return [
        create_lynx_basic_skill(),
        create_lynx_special_skill(),
        create_lynx_ult_skill(),
        create_lynx_talent_skill(),
        create_lynx_technique_skill(),
    ]
