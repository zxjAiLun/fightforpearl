"""
寒鸦 (Hanya) 角色技能设计

基于 https://starrailstation.com/cn/character/hanya#skills 数据

角色定位：同谐+物理 - 战技点回复+承负易伤

==============================
技能
==============================

【普攻】冥谶天笔
- Break 30
- 对指定敌方单体造成等同于寒鸦50%攻击力的物理属性伤害

【战技】生灭系缚
- Break 60
- 对指定敌方单体造成120%攻击力物理属性伤害
- 使目标陷入【承负】状态
- 每当我方目标对【承负】目标施放2次普攻/战技/终结技后
- 立即为我方恢复1个战技点

【终结技】十王敕令，遍土遵行
- 消耗能量 140
- 使指定我方单体速度提高（等同寒鸦速度的15%）
- 使该目标攻击力提高36%，持续2回合

【天赋】罚恶
- 我方目标对【承负】状态下敌方施放普攻/战技/终结技时
- 造成的伤害提高15%，持续2回合

【秘技】判冥
- Break 60
- 进入战斗后对敌方随机单体附上战技效果的【承负】

==============================
机制
==============================

【承负】：核心状态，每2次攻击触发战技点回复+增伤
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_hanya_basic_skill() -> Skill:
    """普攻：冥谶天笔 - 50% ATK"""
    return Skill(
        name="冥谶天笔",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.PHYSICAL,
        description="对指定敌方单体造成50%攻击力的物理属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_hanya_special_skill() -> Skill:
    """战技：生灭系缚 - 承负状态"""
    return Skill(
        name="生灭系缚",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.20,
        damage_type=Element.PHYSICAL,
        description="造成120%ATK物理伤害，使目标陷入【承负】：每2次攻击回复1战技点",
        energy_gain=30.0,
        break_power=60,
    )


def create_hanya_ult_skill() -> Skill:
    """终结技：十王敕令，遍土遵行 - 加速+增伤"""
    return Skill(
        name="十王敕令，遍土遵行",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.PHYSICAL,
        description="指定队友速度+寒鸦速度的15%，攻击力+36%，持续2回合",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="十王敕令",
        target_count=1,
    )


def create_hanya_talent_skill() -> Skill:
    """天赋：罚恶 - 承负增伤"""
    return Skill(
        name="罚恶",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.PHYSICAL,
        description="对【承负】目标施放普攻/战技/终结技时，造成的伤害+15%，持续2回合",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
    )


def create_hanya_passives() -> list[Passive]:
    """寒鸦的被动技能"""
    return [
        Passive(
            name="录事",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_buff_on_sp_trigger",
            value=0.10,
            description="触发【承负】战技点回复的我方单位攻击力+10%，持续1回合；速度+2，攻击力+4%",
        ),
        Passive(
            name="幽府",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="sp_bonus_on_kill",
            value=1.0,
            description="持有【承负】的敌方被消灭时，若触发次数≤1，额外回复1点战技点",
        ),
        Passive(
            name="还阳",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_on_sp_trigger",
            value=2.0,
            description="当【承负】战技点恢复效果被触发时，自身恢复2点能量",
        ),
        Passive(
            name="一心",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="action_advance_on_kill",
            value=0.15,
            description="持有终结技效果的队友消灭敌方时，寒鸦行动提前15%（每回合1次）",
        ),
        Passive(
            name="二观",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_buff_on_special",
            value=0.20,
            description="施放战技后，速度提高20%，持续1回合",
        ),
        Passive(
            name="六正",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_boost_talent",
            value=0.10,
            description="天赋的伤害提高效果额外提高10%（共+25%）",
        ),
    ]


def create_all_hanya_skills() -> list[Skill]:
    return [
        create_hanya_basic_skill(),
        create_hanya_special_skill(),
        create_hanya_ult_skill(),
        create_hanya_talent_skill(),
    ]
