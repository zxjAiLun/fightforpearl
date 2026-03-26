"""
遐蝶 (Castorice) 角色技能设计

角色定位：召唤师 - 召唤忆灵(Netherwing)协同战斗

技能设计（基于实际数据）：
1. 普攻：单体25% Max HP量子伤害
2. 战技：消耗30%全队HP，25%/15% Max HP伤害，忆灵在场时变联合攻击
3. 大招：召唤忆灵，提前100%行动，部署领域降抗性
4. 被动：Newbud系统，队友掉血转给忆灵

关键机制：
- 伤害基于Max HP百分比计算
- Newbud：队友损失HP转化为忆灵HP
- 月茧：延迟倒下次
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.summon import Summon, SummonState
from src.game.models import Character, Element, Skill, SkillType


# ============== 遐蝶的忆灵（Netherwing）==============

def create_castorice_netherwing(owner: Character, newbud: int = 0) -> Summon:
    """
    创建遐蝶的忆灵Netherwing
    
    忆灵属性：
    - HP: Newbud值（队友损失HP转化）
    - ATK: 基于遐蝶Max HP的百分比
    - SPD: 165
    - 持续3回合或HP为0时消失
    """
    # 忆灵的HP等于最大Newbud值
    max_hp = max(newbud, int(owner.stat.total_max_hp() * 0.5))  # 至少50% Max HP
    
    netherwing = Summon(
        name="忆灵·Netherwing",
        owner=owner,
        level=owner.level,
        max_hp=max_hp,
        current_hp=max_hp,
        atk=int(owner.stat.total_max_hp() * 0.2),  # 20% Max HP作为ATK
        def_value=int(owner.stat.total_def() * 0.3),
        spd=165,  # 固定165速
        basic_skill_name="裂隙",
        skill_multiplier=0.2,  # AoE 20% Max HP
        follow_up_on_basic=False,  # 不是协同攻击，是独立回合
    )
    return netherwing


# ============== 遐蝶技能 ==============

def create_castorice_basic_skill() -> Skill:
    """遐蝶普攻：单体25% Max HP量子伤害"""
    return Skill(
        name="叹息·内海涟漪",
        type=SkillType.BASIC,
        multiplier=0.25,  # 25% Max HP（基础倍率，实际伤害=MaxHP*multiplier*ATK系数/DEF）
        damage_type=Element.QUANTUM,
        description="对单目标造成25% Max HP的量子伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_castorice_special_skill() -> Skill:
    """遐蝶战技：消耗30%全队HP，对目标/相邻目标造成伤害"""
    return Skill(
        name="缄默·游掠者之触",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.25,  # 目标25% Max HP
        damage_type=Element.QUANTUM,
        description="消耗30%全队当前HP，对目标造成25% Max HP，相邻目标15% Max HP",
        energy_gain=25.0,
        break_power=60,
        # 扩散效果：相邻目标15%
        spread_count=1,
        spread_multiplier=0.6,  # 15%/25% = 0.6
    )


def create_castorice_ult_skill() -> Skill:
    """遐蝶大招：召唤忆灵+领域"""
    return Skill(
        name="哀鸣·破晓钟声",
        type=SkillType.ULT,
        multiplier=0.0,  # 不造成直接伤害，召唤忆灵
        damage_type=Element.QUANTUM,
        description="召唤忆灵Netherwing，行动提前100%，部署领域降低敌人全属性抗性10%",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="召唤忆灵",
        target_count=-1,  # AOE效果
    )


def create_all_castorice_skills() -> list[Skill]:
    """创建遐蝶所有技能"""
    return [
        create_castorice_basic_skill(),
        create_castorice_special_skill(),
        create_castorice_ult_skill(),
    ]


# ============== 忆灵技能 ==============

def execute_netherwing_attack(netherwing: Summon, targets: list[Character]) -> list:
    """
    执行忆灵AoE攻击
    20% Max HP AoE伤害
    """
    from src.game.damage import calculate_damage, apply_damage, DamageSource
    
    results = []
    owner = netherwing.owner
    
    for target in targets:
        # 忆灵伤害 = 20% Max HP（基础伤害比例）
        # 实际伤害需要计算
        result = calculate_damage(
            attacker=owner,
            defender=target,
            skill_multiplier=0.20,  # 20%
            damage_type=Element.QUANTUM,
            damage_source=DamageSource.FOLLOW_UP,
            attacker_is_player=not owner.is_enemy,
        )
        apply_damage(owner, target, result)
        results.append((target, result))
    
    return results


# ============== 辅助效果 ==============

def apply_mooncocoon_effect(target: Character) -> Modifier:
    """
    应用月茧效果
    队友受致命伤害时，延迟倒下一次
    """
    mod = Modifier(
        name="月茧",
        source_skill="支援-月茧",
        duration=999,  # 持续到下个回合
        modifier_type=ModifierType.BUFF,
        description="受致命伤害时延迟倒下，可正常行动一次",
    )
    return mod


def create_newbud_system(owner: Character) -> dict:
    """
    创建Newbud系统状态
    """
    return {
        "current": 0,
        "max": 100,  # 与队友HP挂钩
    }
