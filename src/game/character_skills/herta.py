"""
遐蝶 (Herta) 角色技能设计

角色定位：召唤师 - 召唤忆灵协同战斗

技能设计：
1. 普攻：单体冰伤
2. 战技：召唤/强化忆灵
3. 大招：群体冰伤 + 忆灵追加攻击
4. 被动：忆灵协同攻击

忆灵机制：
- 遐蝶的战技召唤忆灵傀儡
- 忆灵在遐蝶普攻后协同攻击
- 大招后忆灵追击
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.summon import Summon, SummonState
from src.game.models import Character, Element, Skill, SkillType


# ============== 遐蝶的忆灵（召唤物）==============

def create_herta_puppet(owner: Character) -> Summon:
    """
    创建遐蝶的忆灵傀儡
    
    忆灵属性：
    - HP: 遐蝶HP的50%
    - ATK: 遐蝶ATK的40%
    - SPD: 100
    - 协同攻击倍率: 50% ATK
    """
    puppet = Summon(
        name="忆灵·傀儡",
        owner=owner,
        level=owner.level,
        max_hp=int(owner.stat.total_max_hp() * 0.5),
        current_hp=int(owner.stat.total_max_hp() * 0.5),
        atk=int(owner.stat.total_atk() * 0.4),
        def_value=int(owner.stat.total_def() * 0.3),
        spd=100,
        basic_skill_name="协同攻击",
        skill_multiplier=0.5,
        follow_up_on_basic=True,
    )
    return puppet


# ============== 遐蝶技能 ==============

def create_herta_basic_skill() -> Skill:
    """遐蝶普攻"""
    return Skill(
        name="霜棘",
        type=SkillType.BASIC,
        multiplier=1.0,
        damage_type=Element.ICE,
        description="单体冰伤攻击",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=10,
    )


def create_herta_special_skill() -> Skill:
    """遐蝶战技：召唤/强化忆灵"""
    return Skill(
        name="织梦",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,  # 不造成伤害
        damage_type=Element.ICE,
        description="召唤忆灵傀儡，忆灵会在普攻后协同攻击",
        energy_gain=25.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="召唤忆灵",
    )


def create_herta_ult_skill() -> Skill:
    """遐蝶大招：群体伤害 + 忆灵追击"""
    return Skill(
        name="凝寒",
        type=SkillType.ULT,
        multiplier=1.5,
        damage_type=Element.ICE,
        description="对所有敌人造成1.5倍冰伤，忆灵追击所有敌人",
        energy_gain=5.0,
        break_power=30,
        target_count=-1,  # AOE
        aoe_multiplier=0.8,
    )


def create_all_herta_skills() -> list[Skill]:
    """创建遐蝶所有技能"""
    return [
        create_herta_basic_skill(),
        create_herta_special_skill(),
        create_herta_ult_skill(),
    ]


# ============== 召唤物执行逻辑 ==============

def execute_summon_attack(summon: Summon, targets: list[Character]) -> list:
    """
    执行召唤物攻击
    
    Returns:
        list of (target, damage_result) tuples
    """
    from src.game.damage import calculate_damage, apply_damage, DamageSource
    
    results = []
    
    # 协同攻击：50% ATK倍率
    base_damage = summon.atk * summon.skill_multiplier
    
    for target in targets:
        # 简化伤害计算
        result = calculate_damage(
            attacker=summon.owner,  # 归属为召唤者
            defender=target,
            skill_multiplier=summon.skill_multiplier,
            damage_type=Element.ICE,
            damage_source=DamageSource.FOLLOW_UP,  # 视为追击伤害
            attacker_is_player=not summon.owner.is_enemy,
        )
        apply_damage(summon.owner, target, result)
        results.append((target, result))
    
    return results


def apply_herta_summon_effect(caster: Character, target: Character = None) -> Summon:
    """
    应用遐蝶召唤忆灵效果
    
    Returns:
        创建的召唤物
    """
    summon = create_herta_puppet(caster)
    return summon
