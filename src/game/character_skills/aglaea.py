"""
阿格莱雅 (Aglaea) - 崩坏：星穹铁道角色技能设计

基于 https://starrailstation.com/cn/character/aglaea#skills 数据

角色定位：记忆型 - 忆灵衣匠召唤 + 雷属性输出

==============================
关键机制
==============================

【忆灵·衣匠】
- 衣匠是阿格莱雅的忆灵伙伴
- 初始速度为阿格莱雅的35%
- 初始生命上限为阿格莱雅的44% Max HP + 180
- 攻击处于【间隙织线】状态的目标后，自身速度+44（最多6层）
- 衣匠存在时阿格莱雅攻击会给目标附加【间隙织线】

【至高之姿】
- 阿格莱雅终结技进入该状态
- 普通攻击变为【孤锋千吻】（连携攻击）
- 无法施放战技
- 衣匠获得速度提高层数（每层+10%速度）
- 衣匠免疫控制类负面状态
- 倒计时存在期间再次施放终结技重置倒计时
- 衣匠自毁后阿格莱雅退出该状态

【间隙织线】
- 阿格莱雅攻击时给目标附加
- 攻击处于该状态的敌人后，额外造成12%攻击力雷属性附加伤害
- 仅对最新被施加的目标生效
"""

from __future__ import annotations

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.summon import Summon, SummonState
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 忆灵·衣匠 (Memory Spirit Tailor) ==============

def create_tailor(owner: Character, is_first_summon: bool = True) -> Summon:
    """
    创建忆灵·衣匠

    衣匠属性：
    - 速度: 阿格莱雅速度的35%
    - HP上限: 阿格莱雅HP上限的44% + 180
    - 攻击倍率: 100% ATK (忆灵技)
    - 协同攻击倍率: 55% (刺纹之陷)
    """
    aglaea_spd = owner.stat.total_spd()
    aglaea_hp_max = owner.stat.total_max_hp()

    tailor = Summon(
        name="忆灵·衣匠",
        owner=owner,
        level=owner.level,
        max_hp=int(aglaea_hp_max * 0.44) + 180,
        current_hp=int(aglaea_hp_max * 0.44) + 180,
        atk=int(owner.stat.total_atk() * 0.5),
        def_value=int(owner.stat.total_def() * 0.3),
        spd=int(aglaea_spd * 0.35),
        basic_skill_name="刺纹之陷",
        skill_multiplier=0.55,  # 忆灵技倍率
        follow_up_on_basic=True,
    )
    tailor.skill_multiplier_main = 1.0   # 衣匠普攻倍率（对主目标）
    tailor.skill_multiplier_adj = 0.33   # 衣匠普攻倍率（对相邻目标）
    tailor.spd_stack = 0  # 速度提高层数（天赋）
    tailor.max_spd_stacks = 6
    tailor.spd_stack_value = 44  # 每层+44速度
    tailor.is_immune_to_control = True  # 免疫控制类负面状态
    return tailor


def execute_tailor_skill(tailor: Summon, targets: list[Character], has_gap_state: bool = False) -> list:
    """
    执行衣匠的忆灵技：刺纹之陷
    - 对主目标造成55% ATK雷伤，对相邻目标造成33% ATK雷伤
    - 攻击处于【间隙织线】的目标后，速度+44（最多6层）
    """
    from src.game.damage import calculate_damage, apply_damage, DamageSource

    results = []
    aglaea = tailor.owner

    # Find main target (prioritize target with 间隙织线)
    main_target = None
    for t in targets:
        if _has_gap_state(t):
            main_target = t
            break
    if main_target is None and targets:
        main_target = targets[0]

    # Adjacent targets
    adjacent = [t for t in targets if t != main_target]

    # Main target damage (55% of Tailor's ATK, but we use aglaea's ATK as reference)
    if main_target:
        atk_ref = tailor.atk
        result = calculate_damage(
            attacker=aglaea,
            defender=main_target,
            skill_multiplier=tailor.skill_multiplier,
            damage_type=Element.THUNDER,
            damage_source=DamageSource.FOLLOW_UP,
            attacker_is_player=True,
        )
        apply_damage(aglaea, main_target, result)
        results.append((main_target, result))

        # 天赋：攻击间隙织线目标后速度+44
        if has_gap_state:
            tailor.spd_stack = min(tailor.spd_stack + 1, tailor.max_spd_stacks)

    # Adjacent target damage (33% of Tailor's ATK)
    for adj in adjacent:
        result = calculate_damage(
            attacker=aglaea,
            defender=adj,
            skill_multiplier=tailor.skill_multiplier_adj,
            damage_type=Element.THUNDER,
            damage_source=DamageSource.FOLLOW_UP,
            attacker_is_player=True,
        )
        apply_damage(aglaea, adj, result)
        results.append((adj, result))

    return results


def get_tailor_effective_spd(tailor: Summon) -> int:
    """计算衣匠实际速度（包含速度提高层数）"""
    base_spd = tailor.spd
    spd_bonus = tailor.spd_stack * tailor.spd_stack_value
    return base_spd + spd_bonus


# ============== 阿格莱雅技能 ==============

def create_aglaea_basic_skill() -> Skill:
    """普攻：刺纹之蜜 - 50% ATK 单体雷伤"""
    return Skill(
        name="刺纹之蜜",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.THUNDER,
        description="对指定敌方单体造成50%攻击力的雷属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_aglaea_enhanced_basic_skill() -> Skill:
    """强化普攻：孤锋千吻 - 连携攻击（阿格莱雅+衣匠）"""
    return Skill(
        name="孤锋千吻",
        type=SkillType.BASIC,
        multiplier=1.00,  # 阿格莱雅100% ATK
        damage_type=Element.THUNDER,
        description="阿格莱雅与衣匠向目标发起连携攻击，对目标造成100%ATK雷伤，对相邻目标造成45%ATK雷伤",
        energy_gain=20.0,
        battle_points_gain=0,  # 不恢复战技点
        break_power=60,
        target_count=-1,  # AOE
        aoe_multiplier=0.45,  # 相邻目标45%
    )


def create_aglaea_special_skill() -> Skill:
    """战技：高举吧，升华的名讳 - 召唤/治疗衣匠"""
    return Skill(
        name="高举吧，升华的名讳",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.THUNDER,
        description="为衣匠回复25%生命上限的生命值，若衣匠不在场则召唤衣匠并使阿格莱雅立即行动",
        energy_gain=20.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="召唤衣匠",
    )


def create_aglaea_ult_skill() -> Skill:
    """终结技：共舞吧，命定的衣匠 - 召唤/满血衣匠 + 至高之姿"""
    return Skill(
        name="共舞吧，命定的衣匠",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.THUNDER,
        description="召唤忆灵衣匠（已在场则回复至满血），阿格莱雅进入【至高之姿】状态，普通攻击变为【孤锋千吻】，衣匠获得速度提高层数",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="至高之姿",
        target_count=-1,
    )


def create_aglaea_talent_skill() -> Skill:
    """天赋：金玫之指 - 衣匠属性与间隙织线机制"""
    return Skill(
        name="金玫之指",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.THUNDER,
        description="衣匠初始拥有阿格莱雅35%速度的速度和44%HP上限+180的生命上限，攻击间隙织线目标后速度+44（最多6层）",
        energy_gain=10.0,
        break_power=0,
    )


def create_aglaea_passives() -> list[Passive]:
    """阿格莱雅的被动技能"""
    return [
        # A2: 短视之惩 - 至高之姿状态下攻击力提高
        Passive(
            name="短视之惩",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="至高之姿_atk_bonus",
            value=0.0,
            description="处于【至高之姿】状态时，阿格莱雅与衣匠的攻击力提高",
        ),
        # A2: 防御力+5%
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.05,
            description="防御力+5%",
        ),
        # A3: 雷属性伤害+4.8%
        Passive(
            name="雷属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="thunder_dmg_increase",
            value=0.048,
            description="雷属性伤害提高4.8%",
        ),
        # A4: 织运之竭 - 衣匠消失时保留1层速度层数
        Passive(
            name="织运之竭",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="tailor_spd_stack_preserve",
            value=1,
            description="衣匠消失时，忆灵天赋的速度提高层数最多保留1层",
        ),
        # A4: 暴击率+4%
        Passive(
            name="暴击率强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_rate_increase",
            value=0.04,
            description="暴击率+4%",
        ),
        # A5: 雷属性伤害+4.8%
        Passive(
            name="雷属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="thunder_dmg_increase",
            value=0.048,
            description="雷属性伤害提高4.8%",
        ),
        # A5: 飞驰之阳 - 能量不足50%时恢复至50%
        Passive(
            name="飞驰之阳",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_fill_to_50",
            value=0.0,
            description="战斗开始时，若自身能量不足50%，恢复自身能量至50%",
        ),
        # A6: 防御力+7.5%
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.075,
            description="防御力+7.5%",
        ),
        # A6: 暴击率+5.3%
        Passive(
            name="暴击率强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_rate_increase",
            value=0.053,
            description="暴击率+5.3%",
        ),
        # Lv75: 雷属性伤害+6.4%
        Passive(
            name="雷属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="thunder_dmg_increase",
            value=0.064,
            description="雷属性伤害提高6.4%",
        ),
        # Lv80: 雷属性伤害+3.2%
        Passive(
            name="雷属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="thunder_dmg_increase",
            value=0.032,
            description="雷属性伤害提高3.2%",
        ),
    ]


def create_all_aglaea_skills() -> list[Skill]:
    return [
        create_aglaea_basic_skill(),
        create_aglaea_special_skill(),
        create_aglaea_ult_skill(),
        create_aglaea_talent_skill(),
    ]


# ============== 辅助函数 ==============

def _has_gap_state(target: Character) -> bool:
    """检查目标是否处于间隙织线状态"""
    for mod in target.modifiers:
        if mod.name == "间隙织线":
            return True
    return False


def apply_gap_state(target: Character, duration: int = 99) -> Modifier:
    """为目标附加间隙织线状态"""
    mod = Modifier(
        name="间隙织线",
        source_skill="金玫之指",
        duration=duration,
        modifier_type=ModifierType.DEBUFF,
        dmg_pct=0.12,  # 12%攻击力雷属性附加伤害
    )
    target.add_modifier(mod)
    return mod


def remove_gap_state(target: Character) -> None:
    """移除间隙织线状态"""
    target.remove_modifier_by_name("间隙织线")


def apply_supreme_stance(caster: Character, duration: int = 99) -> Modifier:
    """应用【至高之姿】状态"""
    mod = Modifier(
        name="至高之姿",
        source_skill="共舞吧，命定的衣匠",
        duration=duration,
        modifier_type=ModifierType.BUFF,
        basic_skill_override="孤锋千吻",  # 普攻变为强化普攻
        control_immune=True,
    )
    caster.add_modifier(mod)
    return mod


def remove_supreme_stance(caster: Character) -> None:
    """移除至高之姿状态"""
    caster.remove_modifier_by_name("至高之姿")
