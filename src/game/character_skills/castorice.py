"""
遐蝶 (Castorice) 完整技能设计

基于 https://starrailstation.com/cn/character/castorice 数据

==============================
行迹/被动技能
==============================

【A2】收容的暗潮
除死龙以外的我方目标接受治疗后会将100%的治疗数值转化为【新蕊】，死龙在场时则转化为死龙生命值。
我方每个目标累计转化值不超过【新蕊】上限的12%。
任意单位行动后重置所有单位累计的转化值。

【A4】倒置的火炬
遐蝶当前生命值大于等于自身生命上限的50%时，遐蝶速度提高40%。
死龙施放【燎尽黯泽的焰息】对场上所有敌方造成致命伤害或敌方无法被继续削减生命值时，死龙速度提高100%，持续1回合。

【A4】伤害强化•量子
量子属性伤害提高 +4.8%

【A5】西风的驻足
死龙每次施放【燎尽黯泽的焰息】时，造成的伤害提高30%，该效果最多叠加6层，持续至本回合结束。

【A6】伤害强化•量子
量子属性伤害提高 +6.4%

==============================
死龙行迹
==============================

【A2】暴击伤害+5.3%

【A3】暴击率+4%

【A4】收容的暗潮
除死龙以外的我方目标接受治疗后会将100%的治疗数值转化为【新蕊】，死龙在场时则转化为死龙生命值。
我方每个目标累计转化值不超过【新蕊】上限的12%。
任意单位行动后重置所有单位累计的转化值。

【A5】暴击率+4%

【A5】西风的驻足
死龙每次施放【燎尽黯泽的焰息】时，造成的伤害提高30%，该效果最多叠加6层，持续至本回合结束。

【A6】暴击伤害+8%

【A6】伤害强化•量子
量子属性伤害提高 +6.4%
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.summon import Summon, SummonState
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 死龙 (Netherwing) ==============

def create_castorice_netherwing(owner: Character, newbud_hp: int = 0) -> Summon:
    """
    创建死龙(Netherwing)
    """
    base_hp = int(owner.stat.total_max_hp() * 0.5)
    netherwing_hp = max(base_hp, newbud_hp)
    
    netherwing = Summon(
        name="死龙·玻吕刻斯",
        owner=owner,
        level=owner.level,
        max_hp=netherwing_hp,
        current_hp=netherwing_hp,
        atk=int(owner.stat.total_max_hp() * 0.2),
        def_value=int(owner.stat.total_def() * 0.3),
        spd=165,
        basic_skill_name="擘裂冥茫的爪痕",
        skill_multiplier=0.2,
        follow_up_on_basic=False,
        flame_stack=0,
        max_flame_damage=0.17,
    )
    return netherwing


# ============== 遐蝶被动技能（行迹）==============

def create_castorice_passives() -> list[Passive]:
    """创建遐蝶的所有行迹/被动"""
    return [
        # A2: 收容的暗潮 - 治疗转化新蕊
        Passive(
            name="收容的暗潮",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="heal_to_newbud",
            value=1.0,  # 100%转化
            duration=0,
            description="治疗转化为新蕊，死龙在场时转死龙HP",
        ),
        # A4: 倒置的火炬 - 速度提高
        Passive(
            name="倒置的火炬",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase_when_hp_high",
            value=0.4,  # 40%速度
            duration=0,
            description="HP>=50%时速度+40%",
        ),
        # A4: 伤害强化•量子
        Passive(
            name="伤害强化•量子",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="quantum_dmg_increase",
            value=0.048,  # 4.8%
            duration=0,
            description="量子属性伤害+4.8%",
        ),
        # A5: 西风的驻足
        Passive(
            name="西风的驻足",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="flame_damage_increase",
            value=0.30,  # 30%
            duration=0,
            description="焰息伤害+30%，最多6层",
        ),
        # A6: 伤害强化•量子
        Passive(
            name="伤害强化•量子",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="quantum_dmg_increase",
            value=0.064,  # 6.4%
            duration=0,
            description="量子属性伤害+6.4%",
        ),
        # A6: 暴击伤害
        Passive(
            name="暴击伤害+8%",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.08,
            duration=0,
            description="暴击伤害+8%",
        ),
    ]


def create_netherwing_passives() -> list[Passive]:
    """创建死龙的行迹/被动"""
    return [
        Passive(
            name="暴击伤害+5.3%",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.053,
            duration=0,
            description="暴击伤害+5.3%",
        ),
        Passive(
            name="暴击率+4%",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_rate_increase",
            value=0.04,
            duration=0,
            description="暴击率+4%",
        ),
        Passive(
            name="收容的暗潮",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="heal_to_newbud",
            value=1.0,
            duration=0,
            description="治疗转化为新蕊",
        ),
        Passive(
            name="西风的驻足",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="flame_damage_increase",
            value=0.30,
            duration=0,
            description="焰息伤害+30%，最多6层",
        ),
        Passive(
            name="伤害强化•量子",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="quantum_dmg_increase",
            value=0.064,
            duration=0,
            description="量子属性伤害+6.4%",
        ),
    ]


# ============== 遐蝶技能 ==============

def create_castorice_basic_skill() -> Skill:
    """遐蝶普攻：哀悼，死海之涟漪 - 25% Max HP"""
    return Skill(
        name="哀悼，死海之涟漪",
        type=SkillType.BASIC,
        multiplier=0.25,
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成等同于遐蝶25%生命上限的量子属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_castorice_special_skill() -> Skill:
    """遐蝶战技"""
    return Skill(
        name="缄默，幽蝶之轻抚",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.25,
        damage_type=Element.QUANTUM,
        description="消耗30%全队HP，对目标造成25% Max HP，相邻目标15% Max HP",
        energy_gain=25.0,
        break_power=60,
        spread_count=1,
        spread_multiplier=0.6,
    )


def create_castorice_enhanced_special_skill() -> Skill:
    """遐蝶强化战技：骸爪，冥龙之环拥"""
    return Skill(
        name="骸爪，冥龙之环拥",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.25,
        damage_type=Element.QUANTUM,
        description="消耗40%全队HP(除死龙)，遐蝶与死龙连携攻击，对敌方全体造成15%和25% Max HP伤害",
        energy_gain=25.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=0.6,
    )


def create_castorice_ult_skill() -> Skill:
    """遐蝶大招：亡喉怒哮，苏生之颂铃"""
    return Skill(
        name="亡喉怒哮，苏生之颂铃",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="召唤死龙使其行动提前100%，展开遗世冥域降敌方抗性10%",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="召唤死龙",
        target_count=-1,
    )


def create_all_castorice_skills() -> list[Skill]:
    """创建遐蝶所有技能"""
    return [
        create_castorice_basic_skill(),
        create_castorice_special_skill(),
        create_castorice_enhanced_special_skill(),
        create_castorice_ult_skill(),
    ]


# ============== 死龙技能 ==============

def execute_netherwing_skill(netherwing: Summon, targets: list) -> list:
    """执行死龙的忆灵技"""
    from src.game.damage import calculate_damage, apply_damage, DamageSource
    
    results = []
    owner = netherwing.owner
    
    for target in targets:
        result = calculate_damage(
            attacker=owner,
            defender=target,
            skill_multiplier=0.20,
            damage_type=Element.QUANTUM,
            damage_source=DamageSource.FOLLOW_UP,
            attacker_is_player=not owner.is_enemy,
        )
        apply_damage(owner, target, result)
        results.append((target, result))
    
    return results


def execute_flame_burn(netherwing: Summon, targets: list) -> tuple:
    """焰息：燎尽黯泽的焰息"""
    from src.game.damage import calculate_damage, apply_damage, DamageSource
    
    hp_cost = int(netherwing.max_hp * 0.25)
    netherwing.current_hp = max(1, netherwing.current_hp - hp_cost)
    
    netherwing.flame_stack = min(netherwing.flame_stack + 1, 3)
    multipliers = [0.12, 0.14, 0.17]
    current_mult = multipliers[netherwing.flame_stack - 1]
    
    results = []
    owner = netherwing.owner
    
    for target in targets:
        result = calculate_damage(
            attacker=owner,
            defender=target,
            skill_multiplier=current_mult,
            damage_type=Element.QUANTUM,
            damage_source=DamageSource.FOLLOW_UP,
            attacker_is_player=not owner.is_enemy,
        )
        apply_damage(owner, target, result)
        results.append((target, result))
    
    if netherwing.current_hp <= netherwing.max_hp * 0.25:
        return results, True
    return results, False


def execute_ricochet_attack(netherwing: Summon, targets: list) -> tuple:
    """弹射：灼掠幽墟的晦翼"""
    from src.game.damage import calculate_damage, apply_damage, DamageSource
    
    netherwing.current_hp = 0
    results = []
    owner = netherwing.owner
    
    import random
    for _ in range(6):
        if not targets:
            break
        target = random.choice(targets)
        
        result = calculate_damage(
            attacker=owner,
            defender=target,
            skill_multiplier=0.20,
            damage_type=Element.QUANTUM,
            damage_source=DamageSource.FOLLOW_UP,
            attacker_is_player=not owner.is_enemy,
        )
        apply_damage(owner, target, result)
        results.append((target, result))
    
    heal_amount = int(owner.stat.total_max_hp() * 0.03) + 400
    return results, heal_amount
