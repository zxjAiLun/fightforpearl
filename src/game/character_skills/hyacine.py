"""
风堇 (Hyacine) 角色技能设计

基于 https://starrailstation.com/cn/character/hyacine 数据

角色定位：风属性辅助 - 忆灵召唤 + 治疗

==============================
关键机制
==============================

【忆灵·小伊卡】
- 风堇的忆灵伙伴，速度为0，不出现在行动序列上
- 免疫负面效果
- 初始生命上限为风堇的50%
- 被召唤时为风堇恢复15能量（首次额外+30）
- 消失时使风堇行动提前30%

【治疗机制】
- 风堇治疗: 百分比生命上限+固定值
- 小伊卡被动治疗: 当我方目标HP降低时触发，消耗自身4%HP上限
- 【雨过天晴】状态: 我方全体生命上限+15%+150

【累计治疗值系统】
- 风堇和小伊卡的治疗会累积到累计治疗数值
- 小伊卡的忆灵技将累计治疗值的10%转化为风属性伤害
- 每次忆灵技施放清空50%累计治疗值

==============================
技能
==============================

【普攻】当微风轻吻云沫
- 对指定敌方单体造成等同于风堇25%生命上限的风属性伤害
- Energy Gen: 20 | Break: 30

【战技】爱在虹光洒落时
- 召唤忆灵小伊卡
- 为除小伊卡以外的我方全体回复风堇4%HP上限+40
- 为小伊卡回复风堇5%HP上限+50

【终结技】飞入晨昏的我们
- 召唤忆灵小伊卡
- 为除小伊卡以外的我方全体回复风堇5%HP上限+50
- 为小伊卡回复风堇6%HP上限+60
- 风堇进入【雨过天晴】状态，持续3回合
- Energy: 140 / Gen: 5

【天赋】疗愈世间的晨曦
- 小伊卡初始拥有风堇50%HP上限的生命上限
- 风堇或小伊卡提供治疗时，小伊卡造成的伤害提高40%，持续2回合，最多叠加3层

【秘技】天气正好，万物可爱！
- 下一次战斗开始时，为我方全体回复风堇30%HP上限+600，HP上限提高20%，持续2回合
"""

from __future__ import annotations

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.summon import Summon, SummonState
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 忆灵·小伊卡 (Memory Spirit Xiaoyika) ==============

def create_xiaoyika(owner: Character, is_first_summon: bool = True) -> Summon:
    """
    创建忆灵·小伊卡

    小伊卡特点：
    - 速度为0，不出现在行动序列上
    - 免疫负面效果
    - 初始HP为风堇的50%
    - 被召唤时为风堇恢复能量
    - 消失时使风堇行动提前30%
    """
    max_hp = int(owner.stat.total_max_hp() * 0.50)
    heal_pct = 0.04  # 4% of owner max HP per passive heal
    heal_flat = 10    # +10 flat heal per passive trigger
    heal_from_hy = 0.01  # 1% of Hyacine max HP per passive heal to all
    heal_from_hy_flat = 10  # +10 flat heal to all from Hyacine passive

    xiaoyika = Summon(
        name="忆灵·小伊卡",
        owner=owner,
        level=owner.level,
        max_hp=max_hp,
        current_hp=max_hp,
        atk=int(owner.stat.total_max_hp() * 0.15),
        def_value=int(owner.stat.total_def() * 0.3),
        spd=0,  # 速度为0，不出现在行动序列上
        basic_skill_name="乌云乌云快走开！",
        skill_multiplier=0.0,  # 忆灵技倍率由累计治疗值决定
        follow_up_on_basic=False,
    )
    # 小伊卡特有字段（作为实例属性）
    xiaoyika.is_immune_to_debuffs = True
    xiaoyika.heal_pct_per_trigger = heal_pct
    xiaoyika.heal_flat_per_trigger = heal_flat
    xiaoyika.heal_from_hy_pct = heal_from_hy
    xiaoyika.heal_from_hy_flat = heal_from_hy
    xiaoyika.accumulated_heal = 0  # 累计治疗值
    xiaoyika.damage_stack = 0  # 小伊卡伤害加成层数
    xiaoyika.max_damage_stacks = 3
    xiaoyika.is_first_summon = is_first_summon
    return xiaoyika


def execute_xiaoyika_skill(xiaoyika: Summon, owner: Character, all_targets: list[Character]) -> tuple:
    """
    执行小伊卡的忆灵技：乌云乌云快走开！
    - 对敌方全体造成等同于累计治疗值10%的风属性伤害
    - 清空50%累计治疗值
    - 雨过天晴状态下额外行动
    """
    from src.game.damage import calculate_damage, apply_damage, DamageSource

    accumulated = getattr(xiaoyika, 'accumulated_heal', 0)
    damage_pct = 0.10  # 10% of accumulated heal as damage
    clear_pct = 0.50  # clear 50% of accumulated heal

    damage = int(accumulated * damage_pct)
    cleared = int(accumulated * clear_pct)

    results = []
    for target in all_targets:
        if damage > 0:
            result = calculate_damage(
                attacker=owner,
                defender=target,
                skill_multiplier=0.0,  # direct damage, no multiplier
                damage_type=Element.WIND,
                damage_source=DamageSource.FOLLOW_UP,
                attacker_is_player=not owner.is_enemy,
            )
            # Override final damage with accumulated heal based damage
            result.final_damage = damage
            apply_damage(owner, target, result)
            results.append((target, result))

    # Clear accumulated heal
    xiaoyika.accumulated_heal = accumulated - cleared
    if xiaoyika.accumulated_heal < 0:
        xiaoyika.accumulated_heal = 0

    return results, cleared


def xiaoyika_passive_heal(xiaoyika: Summon, owner: Character, allies: list[Character]) -> list[tuple]:
    """
    小伊卡被动治疗：当除小伊卡外的我方目标HP降低时触发
    - 消耗自身4%HP上限的生命值
    - 为生命值降低的目标回复风堇1%HP上限+10
    - 雨过天晴状态下额外为全体回复
    """
    results = []

    # Find allies with HP below max
    damaged_allies = [a for a in allies if a.current_hp < a.stat.total_max_hp()]

    if not damaged_allies:
        return results

    # Cost: 4% of Xiaoyika's max HP
    hp_cost = int(xiaoyika.max_hp * 0.04)
    xiaoyika.current_hp = max(1, xiaoyika.current_hp - hp_cost)

    # Heal each damaged ally: 1% of Hyacine's max HP + 10
    heal_per_target = int(owner.stat.total_max_hp() * 0.01) + 10

    for ally in damaged_allies:
        ally.heal(heal_per_target)
        # Record heal for accumulated heal tracking
        _record_heal(xiaoyika, heal_per_target)
        results.append((ally, heal_per_target))

    # If 雨过天晴 active, also heal all allies
    rain_status = _get_rain_status(owner)
    if rain_status is not None:
        extra_heal = int(owner.stat.total_max_hp() * 0.01) + 10
        for ally in allies:
            if ally != xiaoyika and ally not in damaged_allies:
                ally.heal(extra_heal)
                _record_heal(xiaoyika, extra_heal)
                results.append((ally, extra_heal))

    return results


def _record_heal(xiaoyika: Summon, heal_amount: int) -> None:
    """记录治疗到累计治疗值"""
    if hasattr(xiaoyika, 'accumulated_heal'):
        xiaoyika.accumulated_heal += heal_amount


def _get_rain_status(owner: Character) -> Modifier | None:
    """获取雨过天晴状态"""
    for mod in owner.modifiers:
        if mod.name == "雨过天晴":
            return mod
    return None


def _has_rain_status(owner: Character) -> bool:
    """检查是否处于雨过天晴状态"""
    return _get_rain_status(owner) is not None


# ============== 风堇被动技能（行迹）==============

def create_hyacine_passives() -> list[Passive]:
    """创建风堇的所有行迹/被动"""
    return [
        # A1: 阴云莞尔 - 治疗量提升
        Passive(
            name="阴云莞尔",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="heal_boost_on_low_hp",
            value=0.25,  # 25% heal boost
            duration=0,
            description="为HP<=50%目标治疗时，治疗量提高25%",
        ),
        # A2: 生命强化
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_increase",
            value=0.04,
            duration=0,
            description="生命值+4%",
        ),
        # A3: 速度强化
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=3,
            duration=0,
            description="速度+3",
        ),
        # A4: 雷雨轻柔 - 效果抵抗+解除负面
        Passive(
            name="雷雨轻柔",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.50,  # 50% effect res
            duration=0,
            description="效果抵抗+50%，施放战技和终结技时解除我方全体1个负面",
        ),
        # A4: 效果抵抗强化
        Passive(
            name="效果抵抗强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.06,
            duration=0,
            description="效果抵抗+6%",
        ),
        # A5: 速度强化
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=3,
            duration=0,
            description="速度+3",
        ),
        # A5: 暴风停歇 - 高速治疗加成
        Passive(
            name="暴风停歇",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_heal_bonus",
            value=0.01,  # 1% per speed over 200
            duration=0,
            description="速度>200时，生命上限+20%，每超1点速度治疗量+1%",
        ),
        # A6: 生命强化
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_increase",
            value=0.06,
            duration=0,
            description="生命值+6%",
        ),
        # A6: 效果抵抗强化
        Passive(
            name="效果抵抗强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.08,
            duration=0,
            description="效果抵抗+8%",
        ),
        # A6: 小伊卡伤害加成层数上限提升（天赋效果的一部分）
        Passive(
            name="疗愈世间的晨曦",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="xiaoyika_dmg_stack",
            value=0.40,  # 40% damage boost per stack
            duration=0,
            description="治疗提供时，小伊卡伤害+40%/层，持续2回合，最多3层",
        ),
        # Lv75: 速度强化
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=4,
            duration=0,
            description="速度+4",
        ),
        # Lv80: 速度强化
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=2,
            duration=0,
            description="速度+2",
        ),
    ]


# ============== 风堇技能 ==============

def create_hyacine_basic_skill() -> Skill:
    """风堇普攻：当微风轻吻云沫 - 25% Max HP"""
    return Skill(
        name="当微风轻吻云沫",
        type=SkillType.BASIC,
        multiplier=0.25,
        damage_type=Element.WIND,
        description="对指定敌方单体造成等同于风堇25%生命上限的风属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_hyacine_special_skill() -> Skill:
    """风堇战技：爱在虹光洒落时"""
    return Skill(
        name="爱在虹光洒落时",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="召唤忆灵小伊卡，为我方全体回复风堇4%HP上限+40，为小伊卡回复5%HP上限+50",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="召唤小伊卡",
    )


def create_hyacine_ult_skill() -> Skill:
    """风堇终结技：飞入晨昏的我们"""
    return Skill(
        name="飞入晨昏的我们",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="召唤忆灵小伊卡，为我方全体回复风堇5%HP上限+50，为小伊卡回复6%HP上限+60，风堇进入【雨过天晴】状态",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="雨过天晴",
        target_count=-1,
    )


def create_hyacine_talent_skill() -> Skill:
    """风堇天赋：疗愈世间的晨曦（被动标记技能，用于追踪）"""
    return Skill(
        name="疗愈世间的晨曦",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="小伊卡初始拥有风堇50%HP上限，治疗提供时小伊卡伤害+40%/层",
        energy_gain=0.0,
        break_power=0,
    )


def create_hyacine_technique_skill() -> Skill:
    """风堇秘技：天气正好，万物可爱！"""
    return Skill(
        name="天气正好，万物可爱！",
        type=SkillType.FESTIVITY,
        cost=0,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="下一次战斗开始时，为我方全体回复风堇30%HP上限+600，HP上限+20%持续2回合",
        energy_gain=0.0,
        break_power=0,
    )


def create_all_hyacine_skills() -> list[Skill]:
    """创建风堇所有技能"""
    return [
        create_hyacine_basic_skill(),
        create_hyacine_special_skill(),
        create_hyacine_ult_skill(),
        create_hyacine_talent_skill(),
    ]


# ============== 治疗与状态辅助函数 ==============

def calculate_hyacine_heal(owner: Character, base_pct: float, base_flat: int) -> int:
    """计算风堇的治疗量"""
    return int(owner.stat.total_max_hp() * base_pct) + base_flat


def apply_hyacine_heal(
    owner: Character,
    targets: list[Character],
    base_pct: float,
    base_flat: int,
    xiaoyika: Summon = None,
) -> list[tuple[Character, int]]:
    """
    应用风堇的治疗效果

    Returns:
        list of (target, actual_heal_amount)
    """
    results = []
    heal_amount = calculate_hyacine_heal(owner, base_pct, base_flat)

    for target in targets:
        actual_heal = min(
            heal_amount,
            target.stat.total_max_hp() - target.current_hp,
        )
        if actual_heal > 0:
            target.heal(actual_heal)
            results.append((target, actual_heal))

            # Record to accumulated heal (for Xiaoyika)
            if xiaoyika is not None and hasattr(xiaoyika, 'accumulated_heal'):
                xiaoyika.accumulated_heal += actual_heal

            # A1: heal boost when target HP <= 50%
            if target.current_hp <= target.stat.total_max_hp() * 0.5:
                boosted = int(actual_heal * 1.25)
                extra = boosted - actual_heal
                if extra > 0:
                    target.heal(extra)
                    results[-1] = (target, boosted)
                    if xiaoyika and hasattr(xiaoyika, 'accumulated_heal'):
                        xiaoyika.accumulated_heal += extra

            # A5 暴风停歇: speed-based heal bonus
            total_spd = owner.stat.total_spd()
            if total_spd > 200:
                over_spd = min(total_spd - 200, 200)
                bonus_pct = over_spd * 0.01  # 1% per over-speed point, max 200%
                extra = int(actual_heal * bonus_pct)
                if extra > 0:
                    target.heal(extra)
                    results[-1] = (target, actual_heal + extra)
                    if xiaoyika and hasattr(xiaoyika, 'accumulated_heal'):
                        xiaoyika.accumulated_heal += extra

    return results


def apply_rain_status(caster: Character, duration: int = 3) -> Modifier:
    """
    应用【雨过天晴】状态
    - 我方全体生命上限+15%+150

    Note: The +150 flat HP is tracked as a separate component on the modifier.
    When calculating max HP with rain status, use get_rain_hp_bonus() to get the total bonus.
    """
    mod = Modifier(
        name="雨过天晴",
        source_skill="飞入晨昏的我们",
        duration=duration,
        modifier_type=ModifierType.BUFF,
        hp_pct=0.15,
        hp_flat=150,
    )
    caster.add_modifier(mod)
    return mod


def get_rain_hp_bonus(modifier: Modifier, owner_hp_max: int) -> int:
    """
    获取雨过天晴的HP加成
    Returns: int = int(hp_max * hp_pct) + hp_flat
    """
    if modifier is None:
        return 0
    pct_bonus = int(owner_hp_max * modifier.hp_pct)
    return pct_bonus + modifier.hp_flat


def remove_rain_status(caster: Character) -> None:
    """移除雨过天晴状态"""
    caster.remove_modifier_by_name("雨过天晴")


def summon_xiaoyika(
    owner: Character,
    is_first: bool = False,
) -> Summon:
    """
    召唤小伊卡
    - 创建小伊卡
    - 为风堇恢复能量（15基础，首次+30）
    - 添加到owner的summon_manager
    """
    from src.game.summon import SummonManager

    xiaoyika = create_xiaoyika(owner, is_first_summon=is_first)

    # Energy restore: 15 base, +30 for first summon
    energy_gain = 15
    if is_first:
        energy_gain += 30
    owner.add_energy(energy_gain)

    # Add to summon manager
    if not hasattr(owner, 'summon_manager'):
        owner.summon_manager = SummonManager(owner)
    owner.summon_manager.add_summon(xiaoyika)

    return xiaoyika


def dismiss_xiaoyika(xiaoyika: Summon) -> None:
    """
    消散小伊卡
    - 从owner的summon_manager移除
    - 使风堇行动提前30%
    """
    owner = xiaoyika.owner
    if hasattr(owner, 'summon_manager'):
        owner.summon_manager.remove_summon(xiaoyika)

    # Advance owner's action by 30%
    # pull_forward_pct = 0.30 means 30% of current action value
    advance_mod = Modifier(
        name="小伊卡消散-行动提前",
        source_skill="忆灵消散",
        duration=1,
        modifier_type=ModifierType.BUFF,
        pull_forward_pct=0.30,
    )
    owner.add_modifier(advance_mod)
