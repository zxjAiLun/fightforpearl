"""
那刻夏 (Anaxa) - 崩坏：星穹铁道角色技能设计

基于 https://starrailstation.com/cn/character/anaxa#skills 数据

角色定位：智识型 - 风属性，多属性弱点添加 + 弹射输出

==============================
关键机制
==============================

【升华】状态
- 那刻夏终结技使敌方全体陷入升华状态
- 目标同时被添加物理、火、冰、雷、风、量子、虚数属性弱点
- 若目标不具有控制抵抗，则【升华】状态下无法行动

【质性揭露】状态
- 拥有至少5个不同属性弱点的敌方目标陷入该状态
- 那刻夏对其伤害提高18%
- 施放普攻或战技后，额外施放1次战技（不消耗战技点）

【属性弱点添加】
- 天赋：每次击中敌方目标后添加1个随机属性弱点（优先添加目标尚未拥有的弱点）
- 终结技：使目标同时拥有7种属性弱点

【弹射战技】
- 对指定目标造成伤害，并额外弹射4次
- 场上可攻击敌方目标越多，本次战技伤害越高（每目标+20%）
"""

from __future__ import annotations

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 那刻夏技能 ==============

def create_anaxa_basic_skill() -> Skill:
    """普攻：楚痛，酿造实识 - 50% ATK 单体风伤"""
    return Skill(
        name="楚痛，酿造实识",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.WIND,
        description="对指定敌方单体造成50%攻击力的风属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_anaxa_special_skill() -> Skill:
    """战技：分形，驱逐虚知 - 弹射伤害"""
    return Skill(
        name="分形，驱逐虚知",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.35,  # 主目标35% ATK
        damage_type=Element.WIND,
        description="对指定敌方单体造成35%攻击力伤害，并额外弹射4次，每次对随机敌方造成35% ATK伤害，场上每有1个可攻击目标伤害+20%",
        energy_gain=6.0,  # per hit
        break_power=30,
        ricochet_count=4,
        ricochet_decay=1.0,  # no decay
    )


def create_anaxa_ult_skill() -> Skill:
    """终结技：生息破土，世界塑造 - 升华状态 + 全属性弱点"""
    return Skill(
        name="生息破土，世界塑造",
        type=SkillType.ULT,
        multiplier=0.80,  # 80% ATK AOE
        damage_type=Element.WIND,
        description="使敌方全体陷入【升华】状态（无法行动+全属性弱点），对敌方全体造成80% ATK风属性伤害",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,  # AOE
        is_support_skill=True,
        support_modifier_name="升华",
    )


def create_anaxa_talent_skill() -> Skill:
    """天赋：四分明哲，三重至高 - 属性弱点添加"""
    return Skill(
        name="四分明哲，三重至高",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="每次击中敌方目标后添加1个随机属性弱点（持续3回合），拥有5个以上属性弱点的目标陷入【质性揭露】状态",
        energy_gain=5.0,
        break_power=0,
    )


def create_anaxa_passives() -> list[Passive]:
    """那刻夏的被动技能"""
    return [
        # A2: 流浪的能指 - 普攻额外回能+回合开始回能
        Passive(
            name="流浪的能指",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_on_basic",
            value=10.0,
            duration=0,
            description="施放普攻时额外恢复10点能量，回合开始时若不存在【质性揭露】状态目标则恢复30点能量",
        ),
        # A2: 暴击率+2.7%
        Passive(
            name="暴击率强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_rate_increase",
            value=0.027,
            duration=0,
            description="暴击率+2.7%",
        ),
        # A3: 风属性伤害+3.2%
        Passive(
            name="风属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="wind_dmg_increase",
            value=0.032,
            duration=0,
            description="风属性伤害提高3.2%",
        ),
        # A3: 生命值+4%
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_increase",
            value=0.04,
            duration=0,
            description="生命值+4%",
        ),
        # A4: 必要的留白 - 智识角色数量触发效果
        Passive(
            name="必要的留白",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="erudition_bonus",
            value=0.0,
            duration=0,
            description="根据我方智识命途角色数量触发：1名时暴击伤害+140%，至少2名时我方全体伤害+50%",
        ),
        # A4: 风属性伤害+4.8%
        Passive(
            name="风属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="wind_dmg_increase",
            value=0.048,
            duration=0,
            description="风属性伤害提高4.8%",
        ),
        # A4: 暴击率+4%
        Passive(
            name="暴击率强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_rate_increase",
            value=0.04,
            duration=0,
            description="暴击率+4%",
        ),
        # A5: 风属性伤害+4.8%
        Passive(
            name="风属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="wind_dmg_increase",
            value=0.048,
            duration=0,
            description="风属性伤害提高4.8%",
        ),
        # A5: 质性的嬗变 - 属性弱点增加无视防御
        Passive(
            name="质性的嬗变",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="weakness_def_ignore",
            value=0.04,  # 每弱点4%防御无视，最多7个
            duration=0,
            description="敌方每拥有1个不同属性弱点，那刻夏对其伤害无视4%防御力",
        ),
        # A6: 生命值+6%
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_increase",
            value=0.06,
            duration=0,
            description="生命值+6%",
        ),
        # A6: 暴击率+5.3%
        Passive(
            name="暴击率强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_rate_increase",
            value=0.053,
            duration=0,
            description="暴击率+5.3%",
        ),
        # Lv75: 风属性伤害+3.2%
        Passive(
            name="风属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="wind_dmg_increase",
            value=0.032,
            duration=0,
            description="风属性伤害提高3.2%",
        ),
        # Lv1/Lv80: 风属性伤害+6.4% (combined as Lv80)
        Passive(
            name="风属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="wind_dmg_increase",
            value=0.064,
            duration=0,
            description="风属性伤害提高6.4%",
        ),
    ]


def create_all_anaxa_skills() -> list[Skill]:
    return [
        create_anaxa_basic_skill(),
        create_anaxa_special_skill(),
        create_anaxa_ult_skill(),
        create_anaxa_talent_skill(),
    ]


# ============== 辅助函数 ==============

# 所有属性类型列表（用于弱点添加）
ALL_ELEMENTS = [
    Element.PHYSICAL,
    Element.FIRE,
    Element.ICE,
    Element.THUNDER,
    Element.WIND,
    Element.QUANTUM,
    Element.IMAGINARY,
]


def get_target_weakness_count(target: Character) -> int:
    """获取目标当前拥有的属性弱点数量"""
    count = 0
    for mod in target.modifiers:
        if mod.name and "弱点" in mod.name:
            count += 1
    return count


def apply_random_weakness(target: Character, duration: int = 3) -> str:
    """
    为目标添加1个随机属性弱点（优先添加目标尚未拥有的弱点）
    Returns: 添加的弱点名称
    """
    existing = set()
    for mod in target.modifiers:
        if mod.name and "弱点" in mod.name:
            existing.add(mod.name.replace("弱点", ""))

    available = [e for e in ALL_ELEMENTS if e.name not in existing]
    if not available:
        available = ALL_ELEMENTS  # 全部满时随机选一个

    import random
    element = random.choice(available)
    mod = Modifier(
        name=f"{element.name}弱点",
        source_skill="四分明哲，三重至高",
        duration=duration,
        modifier_type=ModifierType.DEBUFF,
    )
    target.add_modifier(mod)
    return f"{element.name}弱点"


def apply_sublimation_state(target: Character, duration: int = 99) -> Modifier:
    """
    为目标应用【升华】状态
    - 同时添加7种属性弱点
    - 若目标不具有控制抵抗则无法行动
    """
    mod = Modifier(
        name="升华",
        source_skill="生息破土，世界塑造",
        duration=duration,
        modifier_type=ModifierType.DEBUFF,
        cannot_act=True,
    )
    target.add_modifier(mod)

    # 添加所有7种属性弱点
    for element in ALL_ELEMENTS:
        weakness_mod = Modifier(
            name=f"{element.name}弱点",
            source_skill="生息破土，世界塑造",
            duration=duration,
            modifier_type=ModifierType.DEBUFF,
        )
        target.add_modifier(weakness_mod)

    return mod


def apply_revelation_state(target: Character, duration: int = 99) -> Modifier:
    """
    为目标应用【质性揭露】状态
    - 那刻夏对其伤害+18%
    """
    mod = Modifier(
        name="质性揭露",
        source_skill="四分明哲，三重至高",
        duration=duration,
        modifier_type=ModifierType.DEBUFF,
        dmg_taken_pct=0.18,  # 受到伤害+18%
    )
    target.add_modifier(mod)
    return mod


def check_and_apply_revelation(target: Character) -> bool:
    """
    检查目标是否有至少5个不同属性弱点，如有则施加质性揭露
    Returns: 是否成功施加
    """
    weakness_count = get_target_weakness_count(target)
    if weakness_count >= 5:
        # 避免重复添加
        if not any(m.name == "质性揭露" for m in target.modifiers):
            apply_revelation_state(target)
            return True
    return False
