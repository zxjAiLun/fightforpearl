"""
佩拉 (Pela) - 崩坏：星穹铁道

角色定位：虚无·冰 - 驱散 + 防御减益

关键机制：
1. 普攻：单体冰伤害
2. 战技：单体冰伤害 + 驱散1个增益
3. 终结技：全体冰伤害 + 【通解】状态（防御降低30%）
4. 天赋：攻击负面状态敌人后额外恢复5能量
5. 秘技：全体防御降低

冰属性关联：冰属性伤害、效果命中
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_pela_basic_skill() -> Skill:
    """普攻：冰点射击 - 50% ATK"""
    return Skill(
        name="冰点射击",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.ICE,
        description="对指定敌方单体造成50%攻击力的冰属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_pela_special_skill() -> Skill:
    """战技：低温妨害 - 单体伤害+驱散"""
    return Skill(
        name="低温妨害",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.05,
        damage_type=Element.ICE,
        description="解除指定敌方单体的1个增益效果，造成105%攻击力冰属性伤害",
        energy_gain=30.0,
        break_power=60,
    )


def create_pela_ult_skill() -> Skill:
    """终结技：领域压制 - 全体伤害+防御降低"""
    return Skill(
        name="领域压制",
        type=SkillType.ULT,
        multiplier=0.60,
        damage_type=Element.ICE,
        description="敌方全体陷入【通解】状态，防御力降低30%持续2回合，造成60%攻击力冰属性伤害",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )


def create_pela_talent_skill() -> Skill:
    """天赋：数据采集 - 能量恢复"""
    return Skill(
        name="数据采集",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.ICE,
        description="攻击后若敌方目标处于负面效果状态，额外恢复5点能量",
        energy_gain=5.0,
        break_power=0,
    )


def create_pela_technique_skill() -> Skill:
    """秘技：先发制人 - 开场防御降低"""
    return Skill(
        name="先发制人",
        type=SkillType.FESTIVITY,
        cost=0,
        multiplier=0.80,
        damage_type=Element.ICE,
        description="进入战斗后对敌方随机单体造成80%攻击力冰属性伤害，使敌方全体防御力降低20%持续2回合",
        energy_gain=0.0,
        break_power=60,
        target_count=-1,
    )


def create_pela_passives() -> list[Passive]:
    """创建佩拉的行迹被动"""
    return [
        # A2: 痛击 - 对负面目标伤害+20%
        Passive(
            name="痛击",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="debuff_target_dmg_bonus",
            value=0.20,
            duration=0,
            description="对处于负面效果的敌方目标造成的伤害提高20%",
        ),
        # A2: 攻击力+4%，冰属性伤害+3.2%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            duration=0,
            description="攻击力+4%",
        ),
        Passive(
            name="冰属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="ice_dmg_increase",
            value=0.032,
            duration=0,
            description="冰属性伤害+3.2%",
        ),
        # A3: 秘策 - 我方全体效果命中+10%
        Passive(
            name="秘策",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="party_effect_hit",
            value=0.10,
            duration=0,
            description="佩拉在场时，我方全体的效果命中提高10%",
        ),
        # A4: 冰属性伤害+4.8%，攻击力+6%
        Passive(
            name="冰属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="ice_dmg_increase",
            value=0.048,
            duration=0,
            description="冰属性伤害+4.8%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            duration=0,
            description="攻击力+6%",
        ),
        # A5: 追歼 - 战技驱散后下一次攻击+20%
        Passive(
            name="追歼",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="post_dispel_dmg_bonus",
            value=0.20,
            duration=1,
            description="施放战技解除增益效果时，下一次攻击造成的伤害提高20%",
        ),
        # A6: 效果命中+6%，攻击力+8%
        Passive(
            name="效果命中强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_hit_increase",
            value=0.06,
            duration=0,
            description="效果命中+6%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.08,
            duration=0,
            description="攻击力+8%",
        ),
    ]


def create_all_pela_skills() -> list[Skill]:
    """创建佩拉所有技能"""
    return [
        create_pela_basic_skill(),
        create_pela_special_skill(),
        create_pela_ult_skill(),
        create_pela_talent_skill(),
        create_pela_technique_skill(),
    ]
