"""
大丽花 (Dahlia) - 崩坏：星穹铁道角色技能设计

基于 https://starrailstation.com/cn/character/dahlia#skills 数据

角色定位：虚无型 - 火属性，结界+共舞者超击破

==============================
关键机制
==============================

【结界】
- 大丽花战技开启结界，持续3回合
- 结界持续期间，我方全体弱点击破效率+50%
- 敌方目标未处于弱点击破状态时削韧值也能转化为超击破伤害

【共舞者】
- 大丽花和另一位队友共同成为【共舞者】
- 每当场上不存在另一位共舞者时，大丽花和击破特攻最高的队友重新成为共舞者
- 共舞者攻击处于弱点击破状态的敌人时，将削韧值转化为超击破伤害
- 敌方目标受到另一位共舞者攻击后，大丽花发动追加攻击（5次×15% ATK火伤）

【败谢】状态
- 终结技使敌方全体陷入败谢状态，持续4回合
- 防御力-8%，会被添加所有共舞者属性的弱点

==============================
技能
==============================

【普攻】拨弄…记忆绽开裂隙 - 50% ATK 单体火伤
【战技】舔舐…背叛伸出火舌 - 结界+80% ATK AOE火伤
【终结技】沉溺…飞灰邀入墓床 - 败谢+AOE火伤
【天赋】谁在害怕康士坦丝？ - 共舞者+追加攻击+超击破转化
"""

from __future__ import annotations

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 大丽花技能 ==============

def create_dahlia_basic_skill() -> Skill:
    """普攻：拨弄…记忆绽开裂隙 - 50% ATK 单体火伤"""
    return Skill(
        name="拨弄…记忆绽开裂隙",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成50%攻击力的火属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_dahlia_special_skill() -> Skill:
    """战技：舔舐…背叛伸出火舌 - 结界+80% ATK AOE火伤"""
    return Skill(
        name="舔舐…背叛伸出火舌",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.80,
        damage_type=Element.FIRE,
        description="开启结界持续3回合，回合开始时持续回合-1，我方全体弱点击破效率+50%，对主目标及相邻造成80% ATK火属性伤害，结界期间削韧值转化为超击破伤害",
        energy_gain=30.0,
        battle_points_gain=0,
        break_power=30,
        target_count=-1,
        aoe_multiplier=0.80,
        is_support_skill=True,
        support_modifier_name="结界",
    )


def create_dahlia_ult_skill() -> Skill:
    """终结技：沉溺…飞灰邀入墓床 - 败谢+AOE火伤"""
    return Skill(
        name="沉溺…飞灰邀入墓床",
        type=SkillType.ULT,
        multiplier=1.80,  # 180% ATK AOE（均分）
        damage_type=Element.FIRE,
        description="使敌方全体陷入【败谢】状态（防御-8%+全火属性弱点），持续4回合，对敌方全体造成180% ATK火属性伤害（均分）",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
        is_support_skill=True,
        support_modifier_name="败谢",
    )


def create_dahlia_talent_skill() -> Skill:
    """天赋：谁在害怕康士坦丝？ - 共舞者+追加攻击"""
    return Skill(
        name="谁在害怕康士坦丝？",
        type=SkillType.TALENT,
        multiplier=0.15,  # 追加攻击15% ATK × 5次
        damage_type=Element.FIRE,
        description="进入战斗大丽花和1名队友成为【共舞者】，共舞者攻击弱点击破目标时将削韧转化为超击破伤害，受到另一位共舞者攻击后大丽花追加攻击5次×15% ATK火伤，每回合最多1次",
        energy_gain=2.0,  # per hit
        break_power=9,
        bounce_count=5,
    )


def create_dahlia_passives() -> list[Passive]:
    """大丽花的被动技能"""
    return [
        # A2: 又一场葬礼 - 开局击破特攻加成+受治疗/护盾时刷新
        Passive(
            name="又一场葬礼",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_atk_party_buff",
            value=0.0,
            description="进入战斗时使其他角色击破特攻提高（大丽花击破特攻×24%+50%），持续1回合，受治疗或护盾时再次触发持续3回合",
        ),
        # A2: 效果抵抗+4%
        Passive(
            name="效果抵抗强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.04,
            description="效果抵抗+4%",
        ),
        # A2: 击破特攻+5.3%
        Passive(
            name="击破特攻强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_efficiency_increase",
            value=0.053,
            description="击破特攻+5.3%",
        ),
        # A3: 速度+2
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=2,
            description="速度+2",
        ),
        # A3: 致哀，故人 - 追加攻击回战技点
        Passive(
            name="致哀，故人",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="follow_up_skill_point",
            value=1.0,
            description="施放天赋追加攻击时为我方恢复1个战技点，每施放2次追加攻击可触发1次",
        ),
        # A4: 击破特攻+8%
        Passive(
            name="击破特攻强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_efficiency_increase",
            value=0.08,
            description="击破特攻+8%",
        ),
        # A4: 效果抵抗+6%
        Passive(
            name="效果抵抗强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.06,
            description="效果抵抗+6%",
        ),
        # A5: 击破特攻+8%
        Passive(
            name="击破特攻强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_efficiency_increase",
            value=0.08,
            description="击破特攻+8%",
        ),
        # A5: 弃旧，恋新 - 添加弱点时速度提高+额外削韧
        Passive(
            name="弃旧，恋新",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="weakness_add_spd",
            value=30,
            description="我方为目标添加弱点时速度+30%持续2回合，火属性角色添加弱点后额外造成20点火属性固定削韧并恢复10%能量上限能量",
        ),
        # A6: 速度+3
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=3,
            description="速度+3",
        ),
        # A6: 效果抵抗+8%
        Passive(
            name="效果抵抗强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.08,
            description="效果抵抗+8%",
        ),
        # Lv75: 击破特攻+5.3%
        Passive(
            name="击破特攻强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_efficiency_increase",
            value=0.053,
            description="击破特攻+5.3%",
        ),
        # Lv1: 击破特攻+10.7%
        Passive(
            name="击破特攻强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_efficiency_increase",
            value=0.107,
            description="击破特攻+10.7%",
        ),
    ]


def create_all_dahlia_skills() -> list[Skill]:
    return [
        create_dahlia_basic_skill(),
        create_dahlia_special_skill(),
        create_dahlia_ult_skill(),
        create_dahlia_talent_skill(),
    ]


# ============== 辅助函数 ==============

def get_field_turns(character: Character) -> int:
    """获取结界剩余回合数"""
    for mod in character.modifiers:
        if mod.name == "结界":
            return mod.duration
    return 0


def apply_field_state(caster: Character, duration: int = 3) -> Modifier:
    """应用结界状态"""
    mod = Modifier(
        name="结界",
        source_skill="舔舐…背叛伸出火舌",
        duration=duration,
        modifier_type=ModifierType.BUFF,
        break_efficiency_pct=0.50,  # 弱点击破效率+50%
        super_break=True,  # 削韧值转化为超击破伤害
    )
    caster.add_modifier(mod)
    return mod


def remove_field_state(caster: Character) -> None:
    """移除结界状态"""
    caster.remove_modifier_by_name("结界")


def apply_wilt_state(target: Character, caster: Character, duration: int = 4) -> Modifier:
    """
    为目标应用【败谢】状态
    - 防御力-8%
    - 添加火属性弱点
    """
    mod = Modifier(
        name="败谢",
        source_skill="沉溺…飞灰邀入墓床",
        duration=duration,
        modifier_type=ModifierType.DEBUFF,
        def_pct=-0.08,  # 防御力-8%
    )
    target.add_modifier(mod)

    # 添加火属性弱点
    fire_weakness = Modifier(
        name="FIRE弱点",
        source_skill="沉溺…飞灰邀入墓床",
        duration=duration,
        modifier_type=ModifierType.DEBUFF,
    )
    target.add_modifier(fire_weakness)

    return mod


def get_dancer_partner(caster: Character) -> Character:
    """获取当前共舞者搭档"""
    for mod in caster.modifiers:
        if mod.name == "共舞者":
            return getattr(mod, 'partner', None)
    return None


def apply_dancer_state(caster: Character, partner: Character, duration: int = 999) -> tuple[Modifier, Modifier]:
    """
    为大丽花和搭档应用【共舞者】状态
    Returns: (caster_mod, partner_mod)
    """
    caster_mod = Modifier(
        name="共舞者",
        source_skill="谁在害怕康士坦丝？",
        duration=duration,
        modifier_type=ModifierType.BUFF,
        partner=partner,
    )
    caster.add_modifier(caster_mod)

    partner_mod = Modifier(
        name="共舞者",
        source_skill="谁在害怕康士坦丝？",
        duration=duration,
        modifier_type=ModifierType.BUFF,
        partner=caster,
    )
    partner.add_modifier(partner_mod)

    return caster_mod, partner_mod


def remove_dancer_state(caster: Character, partner: Character) -> None:
    """移除共舞者状态"""
    caster.remove_modifier_by_name("共舞者")
    partner.remove_modifier_by_name("共舞者")


def get_follow_up_attack_count(caster: Character) -> int:
    """获取追加攻击剩余次数"""
    for mod in caster.modifiers:
        if mod.name == "追加攻击次数":
            return getattr(mod, 'value', 1)
    return 1


def reset_follow_up_attack(caster: Character) -> None:
    """重置追加攻击次数（回合开始时）"""
    existing = None
    for mod in caster.modifiers:
        if mod.name == "追加攻击次数":
            existing = mod
            break

    if existing:
        existing.value = 1
    else:
        mod = Modifier(
            name="追加攻击次数",
            source_skill="谁在害怕康士坦丝？",
            duration=1,
            modifier_type=ModifierType.BUFF,
            value=1,
        )
        caster.add_modifier(mod)


def use_follow_up_attack(caster: Character) -> bool:
    """使用1次追加攻击机会，返回是否还有剩余"""
    count = get_follow_up_attack_count(caster)
    if count > 0:
        for mod in caster.modifiers:
            if mod.name == "追加攻击次数":
                mod.value = count - 1
                return count - 1 > 0
    return False


def calculate_super_break_damage(break_damage: int, break_efficiency: float, target: Character) -> int:
    """
    计算超击破伤害
    - 基础：削韧值 × 击破特攻
    - 结界效果：即使未弱点击破也能触发超击破
    """
    base_damage = int(break_damage * break_efficiency)
    return base_damage


def convert_break_to_super_break(
    character: Character,
    break_damage: int,
    target: Character,
    is_weakness_break: bool
) -> int:
    """
    将削韧值转化为超击破伤害
    - 结界状态下：即使未弱点击破也能转化
    - 普通状态：需要处于弱点击破状态
    Returns: 超击破伤害值
    """
    # 检查是否有结界
    has_field = any(m.name == "结界" for m in character.modifiers)

    if not is_weakness_break and not has_field:
        return 0  # 非弱点击破且无结界，无法触发超击破

    # 获取击破特攻
    break_eff = getattr(character.stat, 'break_efficiency', 1.0)
    # 结界状态额外加成
    if has_field:
        break_eff *= 1.50  # 弱点击破效率+50%

    return calculate_super_break_damage(break_damage, break_eff, target)


def find_highest_break_efficiency_ally(allies: list[Character], exclude: Character) -> Character:
    """找到击破特攻最高的队友"""
    best = None
    best_value = -1
    for ally in allies:
        if ally == exclude:
            continue
        value = getattr(ally.stat, 'break_efficiency', 1.0)
        if value > best_value:
            best_value = value
            best = ally
    return best
