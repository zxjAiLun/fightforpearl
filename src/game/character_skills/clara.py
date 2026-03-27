"""
克拉拉 (Clara) 角色技能设计

基于 https://starrailstation.com/cn/character/clara#skills 数据

角色定位：毁灭型 - 物理反击守护

==============================
关键机制
==============================

【史瓦罗反击系统】
- 克拉拉受击时，史瓦罗自动反击标记的敌人（天赋触发）
- 战技对全体造成伤害，并额外攻击被标记的敌人
- 终结技强化反击：伤害倍率+96%，可攻击相邻目标

【反击标记】
- 攻击克拉拉的敌人被史瓦罗标记
- 被标记的敌人受到史瓦罗反击
- 战技后标记消失（除非有星魂1）

==============================
技能
==============================

【普攻】我也想帮上忙
- 50% ATK 单体物理伤害

【战技】史瓦罗在看着你
- 60% ATK AOE伤害
- 对反击标记目标额外造成60% ATK物理伤害
- 战技后反击标记失效

【终结技】是约定不是命令
- 受到伤害-15%，嘲讽大幅提高，持续2回合
- 史瓦罗反击伤害倍率+96%
- 反击攻击相邻目标（50%主目标伤害）
- 强化反击生效2次

【天赋】因为我们是家人
- 受击伤害-10%
- 攻击克拉拉的敌人被史瓦罗反击（80% ATK物理）
- 反击标记敌人

【秘技】胜利的小小代价
- 战斗开始嘲讽提高，持续2回合
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_clara_basic_skill() -> Skill:
    """普攻：我也想帮上忙 - 50% ATK 单体物理"""
    return Skill(
        name="我也想帮上忙",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.PHYSICAL,
        description="对指定敌方单体造成50%攻击力的物理属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_clara_special_skill() -> Skill:
    """战技：史瓦罗在看着你 - 60% ATK AOE + 反击标记额外伤害"""
    return Skill(
        name="史瓦罗在看着你",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.60,
        damage_type=Element.PHYSICAL,
        description="对敌方全体造成60%攻击力物理伤害，并对反击标记目标额外造成60%攻击力伤害",
        energy_gain=30.0,
        break_power=30,
        target_count=-1,
        aoe_multiplier=0.0,
    )


def create_clara_ult_skill() -> Skill:
    """终结技：是约定不是命令 - 强化史瓦罗反击"""
    return Skill(
        name="是约定不是命令",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.PHYSICAL,
        description="受到伤害-15%，嘲讽提高，史瓦罗反击伤害+96%并攻击相邻目标，持续2回合，强化2次",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="史瓦罗强化反击",
        target_count=-1,
    )


def create_clara_talent_skill() -> Skill:
    """天赋：因为我们是家人 - 史瓦罗反击"""
    return Skill(
        name="因为我们是家人",
        type=SkillType.TALENT,
        multiplier=0.80,
        damage_type=Element.PHYSICAL,
        description="攻击克拉拉的敌人被史瓦罗反击，造成80%攻击力物理伤害并附加反击标记",
        energy_gain=5.0,
        break_power=30,
    )


def create_clara_passives() -> list[Passive]:
    """克拉拉的被动技能（行迹）"""
    return [
        # A2: 家人 - 35%概率解除1个负面效果
        Passive(
            name="家人",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dispel_self_debuff",
            value=0.35,
            description="受到攻击时35%概率解除自身1个负面效果",
        ),
        # A2: 物理属性伤害+3.2%，攻击力+4%
        Passive(
            name="物理强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="physical_dmg_increase",
            value=0.032,
            description="物理属性伤害提高3.2%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            description="攻击力提高4%",
        ),
        # A3: 守护 - 抵抗控制类负面状态+35%
        Passive(
            name="守护",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="control_res",
            value=0.35,
            description="抵抗控制类负面状态的概率提高35%",
        ),
        # A4: 攻击力+6%，物理属性伤害+4.8%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
        Passive(
            name="物理强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="physical_dmg_increase",
            value=0.048,
            description="物理属性伤害提高4.8%",
        ),
        # A5: 复仇 - 史瓦罗反击伤害+30%
        Passive(
            name="复仇",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="svarog_counter_dmg",
            value=0.30,
            description="史瓦罗的反击造成的伤害提高30%",
        ),
        # A6: 生命值+6%，物理属性伤害+6.4%
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="max_hp_increase",
            value=0.06,
            description="生命值提高6%",
        ),
        Passive(
            name="物理强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="physical_dmg_increase",
            value=0.064,
            description="物理属性伤害提高6.4%",
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
    ]


def create_all_clara_skills() -> list[Skill]:
    return [
        create_clara_basic_skill(),
        create_clara_special_skill(),
        create_clara_ult_skill(),
        create_clara_talent_skill(),
    ]
