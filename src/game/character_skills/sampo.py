"""
桑博 (Sampo) 角色技能设计

基于 https://starrailstation.com/cn/character/sampo#skills 数据

角色定位：虚无型 - 风属性风化DOT

==============================
关键机制
==============================

【风化DOT】
- 天赋击中敌人65%概率附加风化状态
- 风化：每回合20% ATK风属性持续伤害，持续3回合
- 最多叠加5层
- 叠加层数影响战技4的即时伤害

【战技：反复横跳的爱】
- 弹射5次，每次28% ATK风伤
- 每次对随机敌方单体

【终结技：惊喜礼盒】
- 96% ATK AOE风伤
- 100%基础概率使敌方全体受到持续伤害+20%，持续2回合

==============================
技能
==============================

【普攻】酷炫的刀花
- 50% ATK 单体风伤

【战技】反复横跳的爱
- 28% ATK 弹射5次（随机单体）

【终结技】惊喜礼盒
- 96% ATK AOE风伤
- 使敌方受到的持续伤害+20%，持续2回合

【天赋】撕风的匕首
- 击中敌人65%概率附加风化（20% ATK/层，持续3回合，最多5层）

【秘技】你最闪亮
- 使区域内敌人目盲（无法发现我方）
- 主动攻击目盲敌人100%行动延后25%
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_sampo_basic_skill() -> Skill:
    """普攻：酷炫的刀花 - 50% ATK 单体风伤"""
    return Skill(
        name="酷炫的刀花",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.WIND,
        description="对指定敌方单体造成50%攻击力的风属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_sampo_special_skill() -> Skill:
    """战技：反复横跳的爱 - 弹射5次28% ATK"""
    return Skill(
        name="反复横跳的爱",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.28,
        damage_type=Element.WIND,
        description="对敌方单体造成28%攻击力风属性伤害，共弹射5次（随机目标）",
        energy_gain=6.0,
        break_power=30,
        target_count=5,
    )


def create_sampo_ult_skill() -> Skill:
    """终结技：惊喜礼盒 - 96% ATK AOE+持续伤害提升"""
    return Skill(
        name="惊喜礼盒",
        type=SkillType.ULT,
        multiplier=0.96,
        damage_type=Element.WIND,
        description="对敌方全体造成96%攻击力风属性伤害，使敌方受到的持续伤害提高20%，持续2回合",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        is_support_skill=True,
        support_modifier_name="持续伤害提升",
    )


def create_sampo_talent_skill() -> Skill:
    """天赋：撕风的匕首 - 风化状态"""
    return Skill(
        name="撕风的匕首",
        type=SkillType.TALENT,
        multiplier=0.20,
        damage_type=Element.WIND,
        description="击中敌人65%概率附加风化状态，每回合20%攻击力风属性持续伤害，最多5层",
        energy_gain=5.0,
        break_power=0,
    )


def create_sampo_passives() -> list[Passive]:
    """桑博的被动技能（行迹）"""
    return [
        # A2: 圈套 - 天赋风化持续时间+1回合
        Passive(
            name="圈套",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="winded_duration_extend",
            value=1,
            description="天赋使敌方陷入风化状态的持续时间延长1回合",
        ),
        # A2: 效果命中+4%，攻击力+4%
        Passive(
            name="效果命中强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_hit_increase",
            value=0.04,
            description="效果命中提高4%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            description="攻击力提高4%",
        ),
        # A3: 后手 - 终结技额外恢复10能量
        Passive(
            name="后手",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="ult_energy_bonus",
            value=10.0,
            description="施放终结技时，额外恢复10点能量",
        ),
        # A4: 攻击力+6%，效果命中+6%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
        Passive(
            name="效果命中强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_hit_increase",
            value=0.06,
            description="效果命中提高6%",
        ),
        # A5: 加料 - 风化目标对桑博伤害-15%
        Passive(
            name="加料",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="winded_dmg_res",
            value=0.15,
            description="风化状态下的敌方目标对桑博造成的伤害降低15%",
        ),
        # A6: 效果抵抗+6%，效果命中+8%
        Passive(
            name="效果抵抗强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.06,
            description="效果抵抗提高6%",
        ),
        Passive(
            name="效果命中强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_hit_increase",
            value=0.08,
            description="效果命中提高8%",
        ),
        # Lv75: 攻击力+4%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            description="攻击力提高4%",
        ),
        # Lv80: (未完整显示)
        # Lv1: 攻击力+8%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.08,
            description="攻击力提高8%",
        ),
    ]


def create_all_sampo_skills() -> list[Skill]:
    return [
        create_sampo_basic_skill(),
        create_sampo_special_skill(),
        create_sampo_ult_skill(),
        create_sampo_talent_skill(),
    ]
