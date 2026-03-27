"""
停云 (Tingyun) 角色技能设计

基于 https://starrailstation.com/cn/character/tingyun#skills 数据

角色定位：同谐型 - 雷属性增伤辅助

==============================
关键机制
==============================

【赐福】
- 战技为目标提供【赐福】
- 攻击力+25%（上限停云ATK的15%）
- 目标攻击后附加20% ATK雷伤
- 持续3回合
- 仅对最新目标生效

【天赋：紫电扶摇】
- 赐福目标攻击后额外造成30% ATK雷属性附加伤害

【终结技】
- 为指定我方单体恢复50能量
- 伤害+20%，持续2回合

==============================
技能
==============================

【普攻】逐客令
- 50% ATK 单体雷伤

【战技】祥音和韵
- 为指定我方提供【赐福】
- 攻击力+25%（上限停云ATK的15%）
- 赐福目标攻击后附加20% ATK雷伤
- 持续3回合

【终结技】庆云光覆仪祷
- 为指定我方恢复50能量
- 伤害+20%，持续2回合

【天赋】紫电扶摇
- 赐福目标攻击后额外造成30% ATK雷属性附加伤害

【秘技】惠风和畅
- 立即恢复50点能量
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_tingyun_basic_skill() -> Skill:
    """普攻：逐客令 - 50% ATK 单体雷伤"""
    return Skill(
        name="逐客令",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.THUNDER,
        description="对指定敌方单体造成50%攻击力的雷属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_tingyun_special_skill() -> Skill:
    """战技：祥音和韵 - 【赐福】增伤辅助"""
    return Skill(
        name="祥音和韵",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.THUNDER,
        description="为指定我方单体提供【赐福】，攻击力+25%（上限停云ATK的15%），攻击后附加20%雷伤，持续3回合",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="赐福",
    )


def create_tingyun_ult_skill() -> Skill:
    """终结技：庆云光覆仪祷 - 能量恢复+增伤"""
    return Skill(
        name="庆云光覆仪祷",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.THUNDER,
        description="为指定我方单体恢复50点能量，同时使目标造成的伤害提高20%，持续2回合",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="庆云光覆",
        target_count=1,
    )


def create_tingyun_talent_skill() -> Skill:
    """天赋：紫电扶摇 - 赐福附加雷伤"""
    return Skill(
        name="紫电扶摇",
        type=SkillType.TALENT,
        multiplier=0.30,
        damage_type=Element.THUNDER,
        description="获得【赐福】的我方目标攻击后，额外造成30%攻击力雷属性附加伤害",
        energy_gain=5.0,
        break_power=0,
    )


def create_tingyun_passives() -> list[Passive]:
    """停云的被动技能（行迹）"""
    return [
        # A2: 驻晴 - 战技后自身速度+20%持续1回合
        Passive(
            name="驻晴",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="speed_after_special",
            value=0.20,
            description="施放战技时，停云自身速度提高20%，持续1回合",
        ),
        # A2: 防御力+5%，攻击力+4%
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.05,
            description="防御力提高5%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            description="攻击力提高4%",
        ),
        # A3: 止厄 - 普攻伤害+40%
        Passive(
            name="止厄",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="basic_dmg_increase",
            value=0.40,
            description="普攻造成的伤害提高40%",
        ),
        # A3: 攻击力+6%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
        # A4: 攻击力+6%，防御力+7.5%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.075,
            description="防御力提高7.5%",
        ),
        # A5: 亨通 - 回合开始恢复5能量
        Passive(
            name="亨通",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_on_turn_start",
            value=5.0,
            description="停云的回合开始时，自身立即恢复5点能量",
        ),
        # A6: 雷属性伤害+4.8%，防御力+10%
        Passive(
            name="雷属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="thunder_dmg_increase",
            value=0.048,
            description="雷属性伤害提高4.8%",
        ),
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.10,
            description="防御力提高10%",
        ),
        # Lv75: 攻击力+8%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.08,
            description="攻击力提高8%",
        ),
        # Lv80: 攻击力+4%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            description="攻击力提高4%",
        ),
        # Lv1: 雷属性伤害+3.2%，攻击力+6%
        Passive(
            name="雷属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="thunder_dmg_increase",
            value=0.032,
            description="雷属性伤害提高3.2%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
    ]


def create_all_tingyun_skills() -> list[Skill]:
    return [
        create_tingyun_basic_skill(),
        create_tingyun_special_skill(),
        create_tingyun_ult_skill(),
        create_tingyun_talent_skill(),
    ]
