"""
遐蝶 (Castorice) 完整技能设计

基于 https://starrailstation.com/cn/character/castorice 数据

角色定位：召唤师 - 召唤死龙(Netherwing)协同战斗

==============================
遐蝶本体技能
==============================

【普攻】哀悼，死海之涟漪
- 单攻
- Break 30
- 对指定敌方单体造成等同于遐蝶25%生命上限的量子属性伤害

【战技】缄默，幽蝶之轻抚
- 扩散
- Break 60/hit
- 消耗我方全体当前30%的生命值
- 对指定敌方单体造成等同于遐蝶25%生命上限的量子属性伤害
- 对其相邻目标造成等同于遐蝶15%生命上限的量子属性伤害
- 若当前生命值不足，最多使当前生命值降至1点
- 若死龙在场，战技替换为【骸爪，冥龙之环拥】

【骸爪，冥龙之环拥】（强化战技）
- 群攻
- Break 60/hit
- 消耗除死龙以外的我方全体当前40%的生命值
- 遐蝶与死龙向目标发起连携攻击
- 对敌方全体造成等同于遐蝶15%和25%生命上限的量子属性伤害

【终结技】亡喉怒哮，苏生之颂铃
- 召唤
- 召唤忆灵死龙使其行动提前100%
- 展开境界【遗世冥域】，使敌方全体全属性抗性降低10%
- 死龙初始拥有165点速度以及等同于【新蕊】上限100%的固定生命上限
- 死龙3个回合后或生命值为0时消失，同时解除境界【遗世冥域】

【天赋】掌心淌过的荒芜
- 强化
- 【新蕊】上限与场上全体角色等级有关
- 我方全体每损失1点生命值遐蝶获得1点【新蕊】
- 当【新蕊】达到上限时可激活终结技
- 我方损失生命值时，遐蝶与死龙造成的伤害提高10%，该效果最多叠加3层，持续3回合
- 死龙在场时无法通过天赋获得【新蕊】
- 除死龙以外我方全体每损失1点生命值会转化为死龙同等的生命值

==============================
死龙•玻吕刻斯 (Netherwing)
==============================

【忆灵技】擘裂冥茫的爪痕
- 群攻
- 对敌方全体造成等同于遐蝶20%生命上限的量子属性伤害

【焰息】燎尽黯泽的焰息
- 发动会消耗等同于死龙生命上限25%的生命值
- 对敌方全体造成等同于遐蝶12%生命上限的量子属性伤害
- 一次攻击中可重复发动，重复发动时伤害倍率依次提高至14%/17%
- 达到17%后不再提高，伤害倍率提高效果在死龙消失前不会降低
- 死龙当前生命值小于等于自身生命上限25%时，发动该技能会主动将生命值降至1点后触发等同于天赋【灼掠幽墟的晦翼】的技能效果

【弹射】灼掠幽墟的晦翼
- 消耗全部生命
- 造成6次伤害，每次伤害对敌方随机单体造成等同于遐蝶20%生命上限的量子属性伤害
- 同时为我方全体回复等同于遐蝶3%生命上限+400点的生命值

【弹射】灼掠幽墟的晦翼（死龙消失时触发）
- 死龙消失时触发
- 造成6次伤害，每次伤害对敌方随机单体造成等同于遐蝶20%生命上限的量子属性伤害
- 同时为我方全体回复等同于遐蝶3%生命上限+400点的生命值

【辅助】震彻寂壤的怒啸
- 死龙被召唤时，我方全体造成的伤害提高10%，持续3回合

【忆灵天赋】月茧荫蔽的身躯
- 死龙在场时为我方后援
- 我方受到伤害或消耗生命值时，当前生命值最多降至1点
- 此后由死龙承担，但死龙会消耗等同于原数值500%的生命值
- 持续至死龙消失
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.summon import Summon, SummonState
from src.game.models import Character, Element, Skill, SkillType


# ============== 死龙 (Netherwing) ==============

def create_castorice_netherwing(owner: Character, newbud_hp: int = 0) -> Summon:
    """
    创建死龙(Netherwing)
    
    属性：
    - HP: min(新蕊上限100, max(50% Max HP, 新蕊转化的HP))
    - SPD: 165
    - ATK: 20% Max HP (用于计算伤害)
    """
    # 死龙HP = min(100, max(50% Max HP, newbud转化HP))
    base_hp = int(owner.stat.total_max_hp() * 0.5)
    netherwing_hp = max(base_hp, newbud_hp)
    
    netherwing = Summon(
        name="死龙·玻吕刻斯",
        owner=owner,
        level=owner.level,
        max_hp=netherwing_hp,
        current_hp=netherwing_hp,
        atk=int(owner.stat.total_max_hp() * 0.2),  # 20% Max HP
        def_value=int(owner.stat.total_def() * 0.3),
        spd=165,
        basic_skill_name="擘裂冥茫的爪痕",  # 忆灵技
        skill_multiplier=0.2,  # 20% Max HP
        follow_up_on_basic=False,  # 不是协同攻击，是独立回合
        # 死龙特殊属性
        flame_stack=0,  # 焰息叠加层数
        max_flame_damage=0.17,  # 最大焰息伤害倍率17%
    )
    return netherwing


# ============== 遐蝶技能 ==============

def create_castorice_basic_skill() -> Skill:
    """遐蝶普攻：哀悼，死海之涟漪 - 25% Max HP"""
    return Skill(
        name="哀悼，死海之涟漪",
        type=SkillType.BASIC,
        multiplier=0.25,  # 25% Max HP
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成等同于遐蝶25%生命上限的量子属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_castorice_special_skill() -> Skill:
    """遐蝶战技：缄默，幽蝶之轻抚 - 扩散伤害"""
    return Skill(
        name="缄默，幽蝶之轻抚",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.25,  # 目标25% Max HP
        damage_type=Element.QUANTUM,
        description="消耗30%全队HP，对目标造成25% Max HP，相邻目标15% Max HP",
        energy_gain=25.0,
        break_power=60,
        # 扩散效果：相邻目标15%
        spread_count=1,
        spread_multiplier=0.6,  # 15%/25% = 0.6
    )


def create_castorice_enhanced_special_skill() -> Skill:
    """遐蝶强化战技：骸爪，冥龙之环拥 - 死龙在场时"""
    return Skill(
        name="骸爪，冥龙之环拥",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.25,  # 25% Max HP (主目标)
        damage_type=Element.QUANTUM,
        description="遐蝶与死龙连携攻击，对敌方全体造成15%和25% Max HP伤害",
        energy_gain=25.0,
        break_power=60,
        target_count=-1,  # AOE
        aoe_multiplier=0.6,  # 15%/25% = 0.6
    )


def create_castorice_ult_skill() -> Skill:
    """遐蝶大招：亡喉怒哮，苏生之颂铃 - 召唤死龙"""
    return Skill(
        name="亡喉怒哮，苏生之颂铃",
        type=SkillType.ULT,
        multiplier=0.0,  # 不造成直接伤害
        damage_type=Element.QUANTUM,
        description="召唤死龙使其行动提前100%，展开遗世冥域降敌方抗性10%",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="召唤死龙",
        target_count=-1,  # AOE效果
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

def execute_netherwing_skill(netherwing: Summon, targets: list[Character]) -> list:
    """
    执行死龙的忆灵技：擘裂冥茫的爪痕
    全体20% Max HP伤害
    """
    from src.game.damage import calculate_damage, apply_damage, DamageSource
    
    results = []
    owner = netherwing.owner
    
    for target in targets:
        result = calculate_damage(
            attacker=owner,
            defender=target,
            skill_multiplier=0.20,  # 20% Max HP
            damage_type=Element.QUANTUM,
            damage_source=DamageSource.FOLLOW_UP,
            attacker_is_player=not owner.is_enemy,
        )
        apply_damage(owner, target, result)
        results.append((target, result))
    
    return results


def execute_flame_burn(netherwing: Summon, targets: list[Character]) -> tuple:
    """
    执行焰息：燎尽黯泽的焰息
    - 消耗25% Max HP
    - 全体12% Max HP伤害
    - 可叠加到14%/17%
    """
    from src.game.damage import calculate_damage, apply_damage, DamageSource
    
    # 消耗25% HP
    hp_cost = int(netherwing.max_hp * 0.25)
    netherwing.current_hp = max(1, netherwing.current_hp - hp_cost)
    
    # 叠加伤害倍率
    netherwing.flame_stack = min(netherwing.flame_stack + 1, 3)
    multipliers = [0.12, 0.14, 0.17]  # 12% -> 14% -> 17%
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
    
    # 检查是否HP<=25%，触发弹射
    if netherwing.current_hp <= netherwing.max_hp * 0.25:
        return results, True  # 触发弹射
    return results, False


def execute_ricochet_attack(netherwing: Summon, targets: list[Character]) -> tuple:
    """
    执行弹射：灼掠幽墟的晦翼
    - 消耗全部HP
    - 6次20% Max HP伤害
    - 回血3% Max HP + 400
    """
    from src.game.damage import calculate_damage, apply_damage, DamageSource
    
    # 消耗全部HP
    netherwing.current_hp = 0
    
    results = []
    owner = netherwing.owner
    
    # 6次随机目标伤害
    for _ in range(6):
        if not targets:
            break
        import random
        target = random.choice(targets)
        
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
    
    # 回血：3% Max HP + 400
    heal_amount = int(owner.stat.total_max_hp() * 0.03) + 400
    
    return results, heal_amount


def apply_netherwing_summon_bonus(owner: Character) -> Modifier:
    """
    应用死龙召唤buff：震彻寂壤的怒啸
    - 全队+10%伤害，持续3回合
    """
    mod = Modifier(
        name="死龙之啸",
        source_skill="死龙召唤",
        duration=3,
        modifier_type=ModifierType.BUFF,
        dmg_pct=0.10,  # +10%伤害
    )
    return mod


def apply_moon茧_protection(target: Character) -> Modifier:
    """
    应用月茧效果
    - 延后倒下，可行动一次
    """
    mod = Modifier(
        name="月茧",
        source_skill="天赋-月茧",
        duration=999,  # 持续到下次行动
        modifier_type=ModifierType.BUFF,
    )
    return mod
