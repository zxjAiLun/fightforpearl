"""
万敌 (Mydei) - 崩坏：星穹铁道角色技能设计

基于 https://starrailstation.com/cn/character/mydei#skills 数据

角色定位：毁灭型 - 虚数属性，以血还血/血仇形态 + HP消耗输出

==============================
关键机制
==============================

【充能系统】
- 每损失1%生命值积攒1点充能，最多200点
- 充能达到100时消耗100点进入【血仇】状态

【血仇状态】
- 生命上限提高50%（防御力保持为0）
- 自身回合开始时自动施放【弑王成王】
- 充能达到150时立即获得额外回合并自动施放【弑神登神】
- 受到致命攻击时不陷入无法战斗，清空充能退出状态并回复50% Max HP

【弑王成王】- 强化战技
- 消耗当前生命值35%，对单体造成55% Max HP伤害，对相邻造成33% Max HP伤害

【弑神登神】- 终极强化战技
- 消耗150点充能，对单体造成140% Max HP伤害，对相邻造成84% Max HP伤害

==============================
技能
==============================

【普攻】踏破征途的誓言 - 25% Max HP 单体虚数伤
【战技】万死无悔 - 50%当前HP消耗，45% Max HP AOE
【强化战技1】弑王成王 - 35%当前HP消耗，55% Max HP单体+33%相邻
【强化战技2】弑神登神 - 150充能消耗，140% Max HP单体+84%相邻
【终结技】诛天焚骨的王座 - 回复15%Max HP+20充能，96% Max HP AOE+嘲讽
"""

from __future__ import annotations

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 万敌技能 ==============

def create_mydei_basic_skill() -> Skill:
    """普攻：踏破征途的誓言 - 25% Max HP 单体虚数伤"""
    return Skill(
        name="踏破征途的誓言",
        type=SkillType.BASIC,
        multiplier=0.25,
        damage_type=Element.IMAGINARY,
        description="对指定敌方单体造成等同于万敌25%生命上限的虚数属性伤害（生命上限百分比）",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_mydei_special_skill() -> Skill:
    """战技：万死无悔 - HP消耗 + 45% Max HP AOE"""
    return Skill(
        name="万死无悔",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.45,  # 对主目标45% Max HP
        damage_type=Element.IMAGINARY,
        description="消耗50%当前生命值，对指定敌方单体造成45% Max HP虚数伤害，对相邻目标造成25% Max HP虚数伤害（生命上限百分比）",
        energy_gain=30.0,
        battle_points_gain=0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=0.25,
    )


def create_mydei_enhanced_skill_1() -> Skill:
    """强化战技1：弑王成王（自动施放）"""
    return Skill(
        name="弑王成王",
        type=SkillType.SPECIAL,
        cost=0,  # 自动施放，不消耗战技点
        multiplier=0.55,
        damage_type=Element.IMAGINARY,
        description="消耗35%当前生命值，对敌方单体造成55% Max HP虚数伤害，对相邻目标造成33% Max HP虚数伤害（生命上限百分比，血仇状态下自动施放）",
        energy_gain=30.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=0.33,
    )


def create_mydei_enhanced_skill_2() -> Skill:
    """强化战技2：弑神登神（自动施放，消耗150充能）"""
    return Skill(
        name="弑神登神",
        type=SkillType.SPECIAL,
        cost=0,  # 自动施放
        multiplier=1.40,
        damage_type=Element.IMAGINARY,
        description="消耗150点充能，对敌方单体造成140% Max HP虚数伤害，对相邻目标造成84% Max HP虚数伤害（生命上限百分比）",
        energy_gain=10.0,
        break_power=90,
        target_count=-1,
        aoe_multiplier=0.84,
    )


def create_mydei_ult_skill() -> Skill:
    """终结技：诛天焚骨的王座"""
    return Skill(
        name="诛天焚骨的王座",
        type=SkillType.ULT,
        multiplier=0.96,
        damage_type=Element.IMAGINARY,
        description="回复15% Max HP并积攒20点充能，对指定敌方单体造成96% Max HP虚数伤害，对相邻造成60% Max HP虚数伤害，使目标与相邻目标嘲讽2回合",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=0.60,
    )


def create_mydei_talent_skill() -> Skill:
    """天赋：以血还血 - 充能系统"""
    return Skill(
        name="以血还血",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.IMAGINARY,
        description="每损失1%生命值积攒1点充能，100点充能进入【血仇】状态（HP上限+50%），受到致命攻击不倒下并清空充能退出",
        energy_gain=0.0,
        break_power=0,
    )


def create_mydei_passives() -> list[Passive]:
    """万敌的被动技能"""
    return [
        # A2: 水与泥土 - 血仇状态下致命攻击不退出（3次）
        Passive(
            name="水与泥土",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="blood_fury_no_exit",
            value=3,
            duration=0,
            description="【血仇】状态下受到致命攻击时不会退出该状态，该效果单场战斗可触发3次",
        ),
        # A2: 生命值+4%
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_increase",
            value=0.04,
            duration=0,
            description="生命值+4%",
        ),
        # A2: 暴击伤害+5.3%
        Passive(
            name="暴击伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.053,
            duration=0,
            description="暴击伤害+5.3%",
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
        # A3: 三十僭主 - 血仇状态下免疫控制
        Passive(
            name="三十僭主",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="blood_fury_cc_immune",
            value=0.0,
            duration=0,
            description="【血仇】状态下万敌免疫控制类负面状态",
        ),
        # A4: 暴击伤害+8%
        Passive(
            name="暴击伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.08,
            duration=0,
            description="暴击伤害+8%",
        ),
        # A4: 生命值+6%
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_increase",
            value=0.06,
            duration=0,
            description="生命值+6%",
        ),
        # A5: 暴击伤害+8%
        Passive(
            name="暴击伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.08,
            duration=0,
            description="暴击伤害+8%",
        ),
        # A5: 血祥罩衫 - HP上限超4000部分暴击率+受治疗加成
        Passive(
            name="血祥罩衫",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_excess_crit_heal",
            value=0.0,
            duration=0,
            description="战斗开始时若HP上限>4000，每超100点暴击率+1.2%，受伤害充能+2.5%，受治疗+0.75%",
        ),
        # A6: 速度+3
        Passive(
            name="速度强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=3,
            duration=0,
            description="速度+3",
        ),
        # A6: 生命值+8%
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="hp_increase",
            value=0.08,
            duration=0,
            description="生命值+8%",
        ),
        # Lv75: 暴击伤害+10.7%
        Passive(
            name="暴击伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.107,
            duration=0,
            description="暴击伤害+10.7%",
        ),
        # Lv80: 暴击伤害+5.3%
        Passive(
            name="暴击伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_dmg_increase",
            value=0.053,
            duration=0,
            description="暴击伤害+5.3%",
        ),
    ]


def create_all_mydei_skills() -> list[Skill]:
    return [
        create_mydei_basic_skill(),
        create_mydei_special_skill(),
        create_mydei_ult_skill(),
        create_mydei_talent_skill(),
    ]


# ============== 辅助函数 ==============

def get_charge_value(character: Character) -> int:
    """获取万敌当前充能值"""
    for mod in character.modifiers:
        if mod.name == "充能":
            return int(getattr(mod, 'value', 0))
    return 0


def add_charge(character: Character, amount: int) -> int:
    """增加充能值，返回实际增加量"""
    current = get_charge_value(character)
    new_charge = min(current + amount, 200)  # 最多200点
    added = new_charge - current

    existing = None
    for mod in character.modifiers:
        if mod.name == "充能":
            existing = mod
            break

    if existing:
        existing.value = new_charge
    else:
        mod = Modifier(
            name="充能",
            source_skill="以血还血",
            duration=999,
            modifier_type=ModifierType.BUFF,
            value=new_charge,
        )
        character.add_modifier(mod)

    return added


def clear_charge(character: Character) -> None:
    """清空充能值"""
    character.remove_modifier_by_name("充能")


def consume_charge(character: Character, amount: int) -> bool:
    """消耗充能，返回是否成功"""
    current = get_charge_value(character)
    if current >= amount:
        for mod in character.modifiers:
            if mod.name == "充能":
                mod.value = current - amount
                return True
    return False


def get_hp_loss_for_charge(character: Character) -> int:
    """
    根据已损失HP计算应获得的充能
    每损失1%生命值积攒1点充能
    """
    max_hp = character.stat.total_max_hp()
    current_hp = character.current_hp
    hp_lost_pct = (max_hp - current_hp) / max_hp  # 损失百分比
    return int(hp_lost_pct * 100)  # 每1%损失=1点充能


def apply_blood_fury_state(character: Character, duration: int = 99) -> Modifier:
    """
    应用【血仇】状态
    - 生命上限提高50%
    - 防御力保持为0
    """
    max_hp = character.stat.total_max_hp()
    extra_hp = int(max_hp * 0.50)

    mod = Modifier(
        name="血仇",
        source_skill="以血还血",
        duration=duration,
        modifier_type=ModifierType.BUFF,
        hp_pct=0.50,  # 生命上限+50%
        def_pct=-1.0,  # 防御力保持为0
    )
    character.add_modifier(mod)
    # 增加生命上限
    character.stat.base_max_hp += extra_hp
    return mod


def remove_blood_fury_state(character: Character) -> None:
    """移除血仇状态"""
    max_hp = character.stat.total_max_hp()
    extra_hp = int(max_hp * 0.50 / 1.50)  # 还原
    character.stat.base_max_hp -= extra_hp
    character.remove_modifier_by_name("血仇")


def check_blood_fury_entry(character: Character) -> bool:
    """
    检查是否达到血仇状态进入条件（100充能）
    Returns: 是否成功进入血仇
    """
    charge = get_charge_value(character)
    if charge >= 100:
        # 消耗100充能
        consume_charge(character, 100)
        # 回复15% Max HP
        heal_amount = int(character.stat.total_max_hp() * 0.15)
        character.heal(heal_amount)
        # 进入血仇状态
        apply_blood_fury_state(character)
        # 行动提前100%
        advance_mod = Modifier(
            name="血仇-行动提前",
            source_skill="以血还血",
            duration=1,
            modifier_type=ModifierType.BUFF,
            pull_forward_pct=1.0,
        )
        character.add_modifier(advance_mod)
        return True
    return False


def check_blood_fury_ultimate_entry(character: Character) -> bool:
    """
    检查血仇状态下是否触发弑神登神（150充能）
    Returns: 是否触发
    """
    if not any(m.name == "血仇" for m in character.modifiers):
        return False
    charge = get_charge_value(character)
    if charge >= 150:
        consume_charge(character, 150)
        return True
    return False


def get_blood_fury_no_exit_uses(character: Character) -> int:
    """获取血仇状态下致命攻击不退出效果的剩余次数"""
    for mod in character.modifiers:
        if mod.name == "血仇不退出次数":
            return getattr(mod, 'value', 3)
    return 3


def use_blood_fury_no_exit(character: Character) -> bool:
    """使用一次血仇不退出效果，返回是否还有剩余"""
    uses = get_blood_fury_no_exit_uses(character)
    if uses > 0:
        for mod in character.modifiers:
            if mod.name == "血仇不退出次数":
                mod.value = uses - 1
                return uses - 1 > 0
        # 首次使用
        mod = Modifier(
            name="血仇不退出次数",
            source_skill="水与泥土",
            duration=999,
            modifier_type=ModifierType.BUFF,
            value=uses - 1,
        )
        character.add_modifier(mod)
        return uses - 1 > 0
    return False


def apply_taunt(target: Character, duration: int = 2) -> Modifier:
    """为目标应用嘲讽状态"""
    mod = Modifier(
        name="嘲讽",
        source_skill="诛天焚骨的王座",
        duration=duration,
        modifier_type=ModifierType.DEBUFF,
        taunt=True,
    )
    target.add_modifier(mod)
    return mod


def apply_lethal_survival(character: Character) -> None:
    """
    受到致命攻击时的处理
    - 不陷入无法战斗
    - 清空充能退出血仇状态
    - 回复50% Max HP
    """
    # 回复50% Max HP
    heal_amount = int(character.stat.total_max_hp() * 0.50)
    character.heal(heal_amount)
    # 清空充能
    clear_charge(character)
    # 退出血仇状态
    if any(m.name == "血仇" for m in character.modifiers):
        remove_blood_fury_state(character)
