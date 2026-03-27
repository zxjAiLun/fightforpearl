"""
黑天鹅 (Black Swan) - 崩坏：星穹铁道角色技能设计

基于 https://starrailstation.com/cn/character/blackswan#skills 数据

角色定位：虚无·风 - 持续伤害 + 奥迹叠层

==============================
关键机制
==============================

【奥迹】(Arcane Stack)
- 黑天鹅的核心机制，可叠加的持续伤害状态
- 最多叠加50层
- 每层使持续伤害倍率提高4.8%
- 持续伤害触发后重置为1层（揭露状态下除外）
- 施加：普攻50%基础概率、战技100%基础概率、天赋50%基础概率

【揭露】(Revelation)
- 终结技施加的群体debuff，持续2回合
- 敌方受到伤害提高15%
- 奥迹层数不会在造成伤害后重置
- 揭露状态下，奥迹被视为风化、裂伤、灼烧、触电状态

【奥迹叠层策略】
- 普攻：单体，50%基础概率
- 战技：扩散(主目标+相邻)，100%基础概率，DEF降低14.8%
- 天赋：每受到1次DoT，50%基础概率触发1层
- 秘技：战斗开始150%基础概率施加

==============================
技能
==============================

【普攻】洞见，缄默的黎明
- 30% ATK，风属性伤害
- 50%基础概率使目标陷入1层奥迹
- 攻击陷入风化/裂伤/灼烧/触电状态的目标后，分别50%额外概率叠加1层

【战技】失坠，伪神的黄昏
- 45% ATK扩散（主目标+相邻目标）
- 100%基础概率使目标与相邻目标陷入1层奥迹
- 100%基础概率使目标防御力降低14.8%，持续3回合

【终结技】沉醉于彼界的臂湾
- 120能量，72% ATK AOE
- 使敌方全体陷入揭露状态，持续2回合
- 揭露：受伤+15%，奥迹不重置层数

【天赋】无端命运的机杼
- 每回合开始，每受到1次持续伤害，50%基础概率陷入1层奥迹
- 奥迹：每回合开始受到96% ATK风属性持续伤害，每层+4.8%，最多50层
- >=3层：对相邻目标造成72% ATK持续伤害，50%基础概率使相邻目标陷入1层奥迹
- >=7层：无视目标及相邻目标20%防御力

【秘技】取此真相，弃舍表征
- 战斗开始150%基础概率使每个敌方单体陷入1层奥迹
- 反复施加直到失败，每次概率为上次成功时的50%
"""

from __future__ import annotations

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 黑天鹅技能 ==============

def create_blackswan_basic_skill() -> Skill:
    """普攻：洞见，缄默的黎明"""
    return Skill(
        name="洞见，缄默的黎明",
        type=SkillType.BASIC,
        multiplier=0.30,
        damage_type=Element.WIND,
        description="对指定敌方单体造成30%攻击力的风属性伤害，有50%的基础概率使目标陷入1层奥迹",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_blackswan_special_skill() -> Skill:
    """战技：失坠，伪神的黄昏"""
    return Skill(
        name="失坠，伪神的黄昏",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.45,
        damage_type=Element.WIND,
        description="对指定敌方单体及其相邻目标造成45%攻击力的风属性伤害，100%基础概率使目标与相邻目标陷入1层奥迹，防御力降低14.8%，持续3回合",
        energy_gain=30.0,
        break_power=60,
        spread_count=1,
        spread_multiplier=1.0,
    )


def create_blackswan_ult_skill() -> Skill:
    """终结技：沉醉于彼界的臂湾"""
    return Skill(
        name="沉醉于彼界的臂湾",
        type=SkillType.ULT,
        multiplier=0.72,
        damage_type=Element.WIND,
        description="使敌方全体陷入揭露状态，持续2回合。揭露状态下敌方受到伤害提高15%，奥迹每回合开始造成伤害后不会重置层数。对敌方全体造成72%攻击力的风属性伤害",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )


def create_blackswan_talent_skill() -> Skill:
    """天赋：无端命运的机杼"""
    return Skill(
        name="无端命运的机杼",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="敌方目标每回合开始时每受到1次持续伤害，有50%的基础概率陷入1层奥迹。奥迹状态下每回合开始受到96%攻击力风属性持续伤害，每层使伤害倍率提高4.8%，最多叠加50层",
        energy_gain=0.0,
        break_power=0,
    )


def create_blackswan_technique_skill() -> Skill:
    """秘技：取此真相，弃舍表征"""
    return Skill(
        name="取此真相，弃舍表征",
        type=SkillType.FESTIVITY,
        cost=0,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="下一次战斗开始时，有150%的基础概率使敌方每个单体目标陷入1层奥迹。每次施加失败后，下次对该目标施加的基础概率为上次成功时的50%",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="取此真相-奥迹",
    )


def create_blackswan_passives() -> list[Passive]:
    """黑天鹅的被动技能（行迹）"""
    return [
        # A2: 脏中躁动 - 战技攻击风化/裂伤/灼烧/触电状态目标时，65%额外概率使目标陷入1层奥迹
        Passive(
            name="脏中躁动",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="arcane_stack_from_dot_targets",
            value=0.65,
            duration=0,
            description="施放战技攻击陷入风化、裂伤、灼烧、触电状态的指定敌方单体后，分别各有65%的基础概率额外使目标陷入1层奥迹",
        ),
        # A2: 风属性伤害+3.2%，攻击力+4%
        Passive(
            name="风属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="wind_dmg_increase",
            value=0.032,
            duration=0,
            description="风属性伤害+3.2%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            duration=0,
            description="攻击力+4%",
        ),
        # A3: 效果命中+4%
        Passive(
            name="效果命中强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_hit_increase",
            value=0.04,
            duration=0,
            description="效果命中+4%",
        ),
        # A3: 杯底端倪 - 敌人进入战斗时65%概率陷入1层奥迹，每次受击65%概率最多3层
        Passive(
            name="杯底端倪",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="arcane_stack_on_battle_start",
            value=0.65,
            duration=0,
            description="在敌方目标进入战斗时，有65%的基础概率陷入1层奥迹。敌方目标在我方单次攻击内每受到1次持续伤害，有65%的基础概率陷入1层奥迹，单次攻击内最多陷入3层",
        ),
        # A4: 攻击力+6%，风属性伤害+4.8%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            duration=0,
            description="攻击力+6%",
        ),
        Passive(
            name="风属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="wind_dmg_increase",
            value=0.048,
            duration=0,
            description="风属性伤害+4.8%",
        ),
        # A5: 攻击力+6%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            duration=0,
            description="攻击力+6%",
        ),
        # A5: 烛影朕兆 - 造成的伤害提高，提高值等同于效果命中的60%，最多72%
        Passive(
            name="烛影朕兆",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_bonus_from_effect_hit",
            value=0.60,
            duration=0,
            description="使自身造成的伤害提高，提高数值等同于效果命中的60%，最多使造成的伤害提高72%",
        ),
        # A6: 效果命中+6%，风属性伤害+6.4%
        Passive(
            name="效果命中强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_hit_increase",
            value=0.06,
            duration=0,
            description="效果命中+6%",
        ),
        Passive(
            name="风属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="wind_dmg_increase",
            value=0.064,
            duration=0,
            description="风属性伤害+6.4%",
        ),
        # Lv75: 攻击力+4%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            duration=0,
            description="攻击力+4%",
        ),
        # Lv80: 攻击力+8%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.08,
            duration=0,
            description="攻击力+8%",
        ),
    ]


def create_all_blackswan_skills() -> list[Skill]:
    """创建黑天鹅所有技能"""
    return [
        create_blackswan_basic_skill(),
        create_blackswan_special_skill(),
        create_blackswan_ult_skill(),
        create_blackswan_talent_skill(),
        create_blackswan_technique_skill(),
    ]


# ============== 效果应用辅助函数 ==============

def apply_arcane_stack(target: Character, stacks: int = 1) -> Modifier:
    """
    为目标施加奥迹状态
    - 持续伤害倍率 = 96% * (1 + 4.8% * (层数-1))
    - 最多50层
    """
    import math
    actual_stacks = min(stacks, 50)  # 最多50层
    dot_multiplier = 0.96 * (1 + 0.048 * (actual_stacks - 1))
    
    mod = Modifier(
        name="奥迹",
        source_skill="无端命运的机杼",
        duration=99,  # 持续到被清除
        modifier_type=ModifierType.DEBUFF,
        dot_multiplier=dot_multiplier,
        arcane_stack_count=actual_stacks,
    )
    target.add_modifier(mod)
    return mod


def apply_revelation(caster: Character, targets: list[Character], duration: int = 2) -> list[Modifier]:
    """
    应用揭露状态
    - 目标受到伤害提高15%
    - 奥迹不会在造成伤害后重置层数
    """
    modifiers = []
    for target in targets:
        mod = Modifier(
            name="揭露",
            source_skill="沉醉于彼界的臂湾",
            duration=duration,
            modifier_type=ModifierType.DEBUFF,
            vuln_pct=0.15,  # 受到伤害+15%
            arcane_no_reset=True,  # 奥迹不重置层数
        )
        target.add_modifier(mod)
        modifiers.append(mod)
    return modifiers


def apply_arcane_stack_from_dot(caster: Character, target: Character, dot_count: int) -> Modifier | None:
    """
    天赋触发：目标每受到1次持续伤害，有50%基础概率陷入1层奥迹
    """
    import random
    
    for _ in range(dot_count):
        if random.random() > 0.50:
            # 50% base chance failed
            return None
        # Success - apply 1 arcane stack
        apply_arcane_stack(target, 1)
    
    return None


def get_arcane_stack_count(target: Character) -> int:
    """获取目标的奥迹层数"""
    for mod in target.modifiers:
        if mod.name == "奥迹" and hasattr(mod, 'arcane_stack_count'):
            return mod.arcane_stack_count
    return 0


def has_revelation(target: Character) -> bool:
    """检查目标是否处于揭露状态"""
    for mod in target.modifiers:
        if mod.name == "揭露":
            return True
    return False


def blackswan_a3_extra_stacks(attacker: Character, target: Character, dot_hits: int) -> int:
    """
    A3行迹「杯底端倪」：单次攻击内每次持续伤害有65%基础概率使目标额外陷入1层奥迹，单次攻击最多3层
    """
    import random
    extra_stacks = 0
    for _ in range(dot_hits):
        if extra_stacks >= 3:
            break
        if random.random() <= 0.65:
            extra_stacks += 1
    return extra_stacks


def blackswan_talent_splash_damage(caster: Character, main_target: Character, adjacent_targets: list[Character], stack_count: int) -> list:
    """
    天赋触发：奥迹>=3层时对相邻目标造成72% ATK持续伤害，50%概率使相邻目标陷入1层奥迹
    奥迹>=7层时无视20%防御力
    """
    results = []
    
    if stack_count < 3:
        return results
    
    # Splash damage to adjacent targets
    for adj in adjacent_targets:
        # 72% ATK wind DoT (this is added as a modifier, actual damage handled by battle system)
        mod = Modifier(
            name="奥迹-溅射",
            source_skill="无端命运的机杼",
            duration=0,
            modifier_type=ModifierType.DEBUFF,
            dot_multiplier=0.72,
            ignores_def=stack_count >= 7,
            def_ignore_pct=0.20 if stack_count >= 7 else 0.0,
        )
        adj.add_modifier(mod)
        results.append((adj, mod))
        
        # 50% chance for adjacent to also get 1 arcane stack
        import random
        if random.random() <= 0.50:
            apply_arcane_stack(adj, 1)
    
    return results


def blackswan_s6_teamwork_trigger(caster: Character, target: Character) -> Modifier | None:
    """
    S6星魂：当敌方目标受到黑天鹅队友的攻击时，黑天鹅有65%基础概率使目标陷入1层奥迹
    每当黑天鹅使目标陷入奥迹时，有50%固定概率额外提高1层
    """
    import random
    
    if random.random() > 0.65:
        return None
    
    # 50% fixed chance to add 1 extra stack
    extra = 1 if random.random() <= 0.50 else 0
    total_stacks = 1 + extra
    
    mod = apply_arcane_stack(target, total_stacks)
    return mod


def blackswan_s2_chain_stack(caster: Character, killed_target: Character, adjacent_targets: list[Character]) -> list[Modifier]:
    """
    S2星魂：奥迹状态下的敌方目标被消灭时，有100%基础概率使相邻目标陷入6层奥迹
    """
    modifiers = []
    for adj in adjacent_targets:
        mod = apply_arcane_stack(adj, 6)
        modifiers.append(mod)
    return modifiers
