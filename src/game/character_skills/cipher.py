"""
赛飞儿 (Cipher) - 崩坏：星穹铁道角色技能设计

基于 https://starrailstation.com/cn/character/cipher#skills 数据

角色定位：虚无型 - 量子属性，老主顾追踪 + 记录伤害追加攻击

==============================
关键机制
==============================

【老主顾】
- 场上不存在老主顾时，赛飞儿立即使当前生命上限最高的敌方成为老主顾
- 老主顾受到我方其他目标攻击后，赛飞儿立即对其发动追加攻击（75% ATK量子伤害）
- 每回合最多触发1次，赛飞儿回合开始时重置
- 施放战技和终结技时使主目标成为老主顾
- 仅对最新被施加的目标生效

【记录值】
- 赛飞儿记录我方对老主顾造成的非真实伤害的12%
- 终结技消耗全部记录值，造成额外真实伤害
- 秘技效果：进入战斗时因该次伤害获得的记录值+200%

==============================
技能
==============================

【普攻】呀，漏网之鱼 - 50% ATK 单体量子伤
【战技】嘿，空手套白银 - AOE虚弱+攻击力提高
【终结技】猫咪怪盗，敬上！ - 主目标伤害+记录值消耗
【天赋】热情好客的多洛斯人 - 老主顾追踪+追加攻击
"""

from __future__ import annotations

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 赛飞儿技能 ==============

def create_cipher_basic_skill() -> Skill:
    """普攻：呀，漏网之鱼 - 50% ATK 单体量子伤"""
    return Skill(
        name="呀，漏网之鱼",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成50%攻击力的量子属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_cipher_special_skill() -> Skill:
    """战技：嘿，空手套白银 - AOE虚弱+攻击力提高"""
    return Skill(
        name="嘿，空手套白银",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.00,  # 主目标100% ATK
        damage_type=Element.QUANTUM,
        description="120%基础概率使指定敌方单体及其相邻目标陷入虚弱状态（伤害-10%），赛飞儿攻击力+30%持续2回合，对主目标造成100% ATK量子伤害，对相邻目标造成50% ATK量子伤害",
        energy_gain=30.0,
        battle_points_gain=0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=0.50,
    )


def create_cipher_ult_skill() -> Skill:
    """终结技：猫咪怪盗，敬上！ - 主目标伤害+记录值消耗"""
    return Skill(
        name="猫咪怪盗，敬上！",
        type=SkillType.ULT,
        multiplier=0.60,  # 主目标60% ATK
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成60% ATK伤害，之后造成等同于记录值25%的真实伤害，并对目标及其相邻造成记录值75%真实伤害（均分）",
        energy_gain=5.0,
        break_power=90,
        target_count=-1,
        aoe_multiplier=0.20,
    )


def create_cipher_talent_skill() -> Skill:
    """天赋：热情好客的多洛斯人 - 老主顾追踪+追加攻击"""
    return Skill(
        name="热情好客的多洛斯人",
        type=SkillType.TALENT,
        multiplier=0.75,  # 追加攻击75% ATK
        damage_type=Element.QUANTUM,
        description="场上不存在老主顾时使生命上限最高的敌方成为老主顾，老主顾受到我方攻击后赛飞儿追加攻击（75% ATK），每回合最多1次，记录对老主顾伤害的12%",
        energy_gain=5.0,
        break_power=60,
    )


def create_cipher_passives() -> list[Passive]:
    """赛飞儿的被动技能"""
    return [
        # A2: 神行宝鞋 - 高速暴击/记录值加成
        Passive(
            name="神行宝鞋",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_crit_record_bonus",
            value=0.0,
            duration=0,
            description="速度>=140/170时暴击率+25%/+50%，记录值+50%/+100%",
        ),
        # A2: 量子属性伤害+3.2%
        Passive(
            name="量子属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="quantum_dmg_increase",
            value=0.032,
            duration=0,
            description="量子属性伤害提高3.2%",
        ),
        # A3: 速度+2
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=2,
            duration=0,
            description="速度+2",
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
        # A3: 三百侠盗 - 记录非老主顾目标伤害
        Passive(
            name="三百侠盗",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="record_all_targets",
            value=0.08,  # 记录8%
            duration=0,
            description="赛飞儿记录我方对【老主顾】以外目标造成的非真实伤害的8%",
        ),
        # A4: 速度+3
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=3,
            duration=0,
            description="速度+3",
        ),
        # A4: 量子属性伤害+4.8%
        Passive(
            name="量子属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="quantum_dmg_increase",
            value=0.048,
            duration=0,
            description="量子属性伤害提高4.8%",
        ),
        # A5: 速度+3
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=3,
            duration=0,
            description="速度+3",
        ),
        # A5: 偷天换日 - 天赋追加攻击暴击伤害+100%，在场时敌方全体受伤害+40%
        Passive(
            name="偷天换日",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="talent_crit_dmg_bonus",
            value=1.0,  # +100%
            duration=0,
            description="天赋追加攻击暴击伤害+100%，赛飞儿在场时敌方全体受到伤害+40%",
        ),
        # A6: 效果命中+6%
        Passive(
            name="效果命中强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_hit_increase",
            value=0.06,
            duration=0,
            description="效果命中+6%",
        ),
        # A6: 量子属性伤害+6.4%
        Passive(
            name="量子属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="quantum_dmg_increase",
            value=0.064,
            duration=0,
            description="量子属性伤害提高6.4%",
        ),
        # Lv75: 速度+2
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=2,
            duration=0,
            description="速度+2",
        ),
        # Lv1: 速度+4
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=4,
            duration=0,
            description="速度+4",
        ),
    ]


def create_all_cipher_skills() -> list[Skill]:
    return [
        create_cipher_basic_skill(),
        create_cipher_special_skill(),
        create_cipher_ult_skill(),
        create_cipher_talent_skill(),
    ]


# ============== 辅助函数 ==============

def get_record_value(caster: Character) -> int:
    """获取赛飞儿当前记录值"""
    for mod in caster.modifiers:
        if mod.name == "记录值":
            return int(getattr(mod, 'value', 0))
    return 0


def add_record_value(caster: Character, damage_dealt: int) -> int:
    """
    为赛飞儿添加记录值
    Returns: 新增的记录值
    """
    record_rate = 0.12  # 基础12%
    # A3 三百侠盗：额外记录非老主顾目标的8%
    # A2 神行宝鞋：速度加成
    spd = caster.stat.total_spd()
    if spd >= 170:
        record_rate += 1.0  # +100%
    elif spd >= 140:
        record_rate += 0.5  # +50%

    added = int(damage_dealt * record_rate)
    _add_or_update_record_modifier(caster, added)
    return added


def _add_or_update_record_modifier(caster: Character, added: int) -> None:
    """添加或更新记录值modifier"""
    existing = None
    for mod in caster.modifiers:
        if mod.name == "记录值":
            existing = mod
            break

    if existing:
        existing.value = getattr(existing, 'value', 0) + added
    else:
        mod = Modifier(
            name="记录值",
            source_skill="热情好客的多洛斯人",
            duration=999,
            modifier_type=ModifierType.BUFF,
            value=added,
        )
        caster.add_modifier(mod)


def clear_record_value(caster: Character) -> int:
    """清空记录值，返回清空前的值"""
    record = get_record_value(caster)
    caster.remove_modifier_by_name("记录值")
    return record


def get_old_client_target(caster: Character) -> Character:
    """获取当前老主顾目标"""
    for mod in caster.modifiers:
        if mod.name == "老主顾":
            return getattr(mod, 'target', None)
    return None


def apply_old_client_state(target: Character, caster: Character, duration: int = 99) -> Modifier:
    """为目标应用【老主顾】状态"""
    mod = Modifier(
        name="老主顾",
        source_skill="热情好客的多洛斯人",
        duration=duration,
        modifier_type=ModifierType.DEBUFF,
        target=target,
    )
    target.add_modifier(mod)
    # 在caster上也记录引用
    caster_mod = Modifier(
        name="老主顾",
        source_skill="热情好客的多洛斯人",
        duration=duration,
        modifier_type=ModifierType.BUFF,
        target=target,
    )
    caster.add_modifier(caster_mod)
    return mod


def remove_old_client_state(target: Character, caster: Character) -> None:
    """移除老主顾状态"""
    target.remove_modifier_by_name("老主顾")
    caster.remove_modifier_by_name("老主顾")


def get_follow_up_trigger_count(caster: Character) -> int:
    """获取赛飞儿当前回合剩余追加攻击次数"""
    for mod in caster.modifiers:
        if mod.name == "追加攻击次数":
            return getattr(mod, 'value', 1)
    return 1


def reset_follow_up_trigger(caster: Character) -> None:
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
            source_skill="热情好客的多洛斯人",
            duration=1,
            modifier_type=ModifierType.BUFF,
            value=1,
        )
        caster.add_modifier(mod)


def use_follow_up_trigger(caster: Character) -> bool:
    """使用1次追加攻击机会，返回是否还有剩余"""
    count = get_follow_up_trigger_count(caster)
    if count > 0:
        for mod in caster.modifiers:
            if mod.name == "追加攻击次数":
                mod.value = count - 1
                return count - 1 > 0
    return False


def apply_weakness_debuff(target: Character, caster: Character, duration: int = 2) -> Modifier:
    """应用虚弱状态（伤害降低10%）"""
    mod = Modifier(
        name="虚弱",
        source_skill="嘿，空手套白银",
        duration=duration,
        modifier_type=ModifierType.DEBUFF,
        dmg_pct=-0.10,
    )
    target.add_modifier(mod)
    return mod


def apply_atk_boost(caster: Character, duration: int = 2, value: float = 0.30) -> Modifier:
    """应用攻击力提高状态"""
    mod = Modifier(
        name="攻击力提高",
        source_skill="嘿，空手套白银",
        duration=duration,
        modifier_type=ModifierType.BUFF,
        atk_pct=value,
    )
    caster.add_modifier(mod)
    return mod
