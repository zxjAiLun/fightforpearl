"""
瓦尔特 (Welt) - 崩坏：星穹铁道

角色定位：虚无·虚数 - AOE + 禁锢 + 减速

关键机制：
1. 普攻：单体虚数伤害
2. 战技：弹射攻击（主目标+2次随机目标），65%基础概率使目标减速
3. 终结技：全体虚数伤害 + 100%禁锢（行动延后32%）
4. 天赋：对减速目标额外造成附加伤害
5. 秘技：战斗开始使敌人陷入禁锢

虚数属性关联：虚数属性伤害、效果命中
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 瓦尔特技能 ==============

def create_welt_basic_skill() -> Skill:
    """瓦尔特普攻：重力压制"""
    return Skill(
        name="重力压制",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.IMAGINARY,
        description="对指定敌方单体造成等同于瓦尔特50%攻击力的虚数属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_welt_special_skill() -> Skill:
    """瓦尔特战技：虚空断界"""
    return Skill(
        name="虚空断界",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.36,
        damage_type=Element.IMAGINARY,
        description="对指定敌方单体造成36%攻击力虚数伤害，并额外造成2次伤害（每次对随机目标造成36%攻击力虚数伤害）。命中时有65%基础概率使目标速度降低10%，持续2回合",
        energy_gain=30.0,
        break_power=30,
        ricochet_count=2,
        ricochet_decay=1.0,  # 弹射倍率不变
    )


def create_welt_ult_skill() -> Skill:
    """瓦尔特终结技：拟似黑洞"""
    return Skill(
        name="拟似黑洞",
        type=SkillType.ULT,
        multiplier=0.90,
        damage_type=Element.IMAGINARY,
        description="对敌方全体造成90%攻击力的虚数伤害，有100%基础概率使目标陷入禁锢状态（行动延后32%，速度降低10%），持续1回合",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )


def create_welt_talent_skill() -> Skill:
    """瓦尔特天赋：时空扭曲"""
    return Skill(
        name="时空扭曲",
        type=SkillType.TALENT,
        multiplier=0.30,
        damage_type=Element.IMAGINARY,
        description="击中处于减速状态的敌方目标时，额外造成1次30%攻击力的虚数属性附加伤害",
        energy_gain=0.0,
        break_power=0,
    )


def create_welt_technique_skill() -> Skill:
    """瓦尔特秘技：画地为牢"""
    return Skill(
        name="画地为牢",
        type=SkillType.FESTIVITY,
        cost=0,
        multiplier=0.0,
        damage_type=Element.IMAGINARY,
        description="进入战斗后，有100%基础概率使敌方目标陷入禁锢状态（行动延后20%，速度降低10%），持续1回合",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="画地为牢-禁锢",
    )


def create_welt_passives() -> list[Passive]:
    """创建瓦尔特的行迹被动"""
    return [
        # A2: 惩戒 - 终结技使目标受伤+12%
        Passive(
            name="惩戒",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="ult_vuln",
            value=0.12,
            duration=2,
            description="施放终结技时，有100%基础概率使目标受到的伤害提高12%，持续2回合",
        ),
        # A2: 虚数伤害+3.2%, 攻击力+4%
        Passive(
            name="虚数属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="imaginary_dmg_increase",
            value=0.032,
            duration=0,
            description="虚数属性伤害+3.2%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            duration=0,
            description="攻击力+4%",
        ),
        # A3: 审判 - 终结技额外恢复10能量
        Passive(
            name="审判",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="ult_energy_restore",
            value=10.0,
            duration=0,
            description="施放终结技时，额外恢复10点能量",
        ),
        # A4: 攻击力+6%, 虚数伤害+4.8%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            duration=0,
            description="攻击力+6%",
        ),
        Passive(
            name="虚数属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="imaginary_dmg_increase",
            value=0.048,
            duration=0,
            description="虚数属性伤害+4.8%",
        ),
        # A5: 裁决 - 对弱点击破目标伤害+20%
        Passive(
            name="裁决",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_target_dmg_bonus",
            value=0.20,
            duration=0,
            description="对被弱点击破的敌方目标造成的伤害提高20%",
        ),
        # A6: 效果抵抗+6%, 虚数伤害+6.4%
        Passive(
            name="效果抵抗强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.06,
            duration=0,
            description="效果抵抗+6%",
        ),
        Passive(
            name="虚数属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="imaginary_dmg_increase",
            value=0.064,
            duration=0,
            description="虚数属性伤害+6.4%",
        ),
    ]


def create_all_welt_skills() -> list[Skill]:
    """创建瓦尔特所有技能"""
    return [
        create_welt_basic_skill(),
        create_welt_special_skill(),
        create_welt_ult_skill(),
        create_welt_talent_skill(),
        create_welt_technique_skill(),
    ]


# ============== 效果应用辅助函数 ==============

def apply_welt_imprison(caster: Character, target: Character, delay_pct: float = 0.32, spd_penalty: float = 0.10) -> Modifier:
    """
    应用禁锢效果
    - 行动延后 delay_pct（默认32%）
    - 速度降低 spd_penalty（默认10%）
    - 持续1回合
    """
    mod = Modifier(
        name="拟似黑洞-禁锢",
        source_skill="拟似黑洞",
        duration=1,
        modifier_type=ModifierType.DEBUFF,
        delay_pct=delay_pct,
        spd_pct=-spd_penalty,
    )
    target.add_modifier(mod)
    return mod


def apply_welt_technique_imprison(caster: Character, targets: list[Character]) -> list[Modifier]:
    """
    应用瓦尔特秘技的禁锢效果（画地为牢）
    - 行动延后20%，速度降低10%，持续1回合
    """
    modifiers = []
    for target in targets:
        mod = Modifier(
            name="画地为牢-禁锢",
            source_skill="画地为牢",
            duration=1,
            modifier_type=ModifierType.DEBUFF,
            delay_pct=0.20,
            spd_pct=-0.10,
        )
        target.add_modifier(mod)
        modifiers.append(mod)
    return modifiers


def apply_welt_slow(caster: Character, target: Character) -> Modifier | None:
    """
    应用减速效果
    65%基础概率使目标速度降低10%，持续2回合
    """
    import random
    
    if random.random() > 0.65:
        return None
    
    mod = Modifier(
        name="虚空断界-减速",
        source_skill="虚空断界",
        duration=2,
        modifier_type=ModifierType.DEBUFF,
        spd_pct=-0.10,
    )
    target.add_modifier(mod)
    return mod


def apply_welt_talent_extra_damage(caster: Character, target: Character) -> Modifier | None:
    """
    应用瓦尔特天赋【时空扭曲】的附加伤害
    仅当目标处于减速状态时触发
    """
    # 检查目标是否有减速效果
    has_slow = any(
        m.name == "虚空断界-减速" or (hasattr(m, 'spd_pct') and m.spd_pct < 0)
        for m in target.modifier_manager._modifiers if hasattr(target, 'modifier_manager') and target.modifier_manager
    )
    
    if not has_slow:
        return None
    
    mod = Modifier(
        name="时空扭曲-附加伤害",
        source_skill="时空扭曲",
        duration=0,
        modifier_type=ModifierType.BUFF,
    )
    # 附加伤害通过追击系统实现，这里返回标记modifier
    return mod
