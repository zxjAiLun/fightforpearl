"""
素裳 (Sushang) 角色技能设计

基于 https://starrailstation.com/cn/character/sushang#skills 数据

角色定位：巡猎型 - 物理弱点击破输出

==============================
关键机制
==============================

【剑势】
- 战技最后一击33%概率发动【剑势】
- 剑势：50% ATK物理附加伤害
- 弱点击破时剑势必定发动

【终结技：太虚形蕴•烛夜】
- 192% ATK 单体物理伤害
- 立即行动
- 攻击力+18%，持续2回合
- 战技额外增加2次剑势判定（额外剑势伤害为原伤害50%）

【天赋：游刃若水】
- 场上有敌人弱点被击破时，速度+15%，持续2回合

==============================
技能
==============================

【普攻】云骑剑经•素霓
- 50% ATK 单体物理伤害

【战技】云骑剑经•山倾
- 105% ATK 单体物理伤害
- 最后一击33%概率发动【剑势】（50% ATK）
- 弱点击破时剑势必定发动

【终结技】太虚形蕴•烛夜
- 192% ATK 单体物理伤害
- 立即行动
- 攻击力+18%，持续2回合
- 战技额外增加2次剑势判定

【天赋】游刃若水
- 敌人弱点击破时速度+15%，持续2回合

【秘技】云骑剑经•叩阵
- 战斗开始对敌方全体造成80% ATK物理伤害
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_sushang_basic_skill() -> Skill:
    """普攻：云骑剑经•素霓 - 50% ATK 单体物理"""
    return Skill(
        name="云骑剑经•素霓",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.PHYSICAL,
        description="对指定敌方单体造成50%攻击力的物理属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_sushang_special_skill() -> Skill:
    """战技：云骑剑经•山倾 - 105% ATK+剑势"""
    return Skill(
        name="云骑剑经•山倾",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.05,
        damage_type=Element.PHYSICAL,
        description="对指定敌方单体造成105%攻击力的物理属性伤害，最后一击33%概率发动【剑势】，弱点击破时必定发动",
        energy_gain=30.0,
        break_power=60,
    )


def create_sushang_ult_skill() -> Skill:
    """终结技：太虚形蕴•烛夜 - 192% ATK+立即行动+攻击力+剑势强化"""
    return Skill(
        name="太虚形蕴•烛夜",
        type=SkillType.ULT,
        multiplier=1.92,
        damage_type=Element.PHYSICAL,
        description="对指定敌方单体造成192%攻击力的物理属性伤害，立即行动，攻击力+18%持续2回合，战技额外增加2次剑势判定",
        energy_gain=5.0,
        break_power=90,
        is_support_skill=True,
        support_modifier_name="太虚形蕴",
    )


def create_sushang_talent_skill() -> Skill:
    """天赋：游刃若水 - 击破弱点头脑+速度"""
    return Skill(
        name="游刃若水",
        type=SkillType.TALENT,
        multiplier=0.50,
        damage_type=Element.PHYSICAL,
        description="场上有敌方目标的弱点被击破时，素裳的速度提高15%，持续2回合",
        energy_gain=0.0,
        break_power=0,
    )


def create_sushang_passives() -> list[Passive]:
    """素裳的被动技能（行迹）"""
    return [
        # A2: 赤子 - HP≤50%时降低被攻击概率
        Passive(
            name="赤子",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="taunt_reduction_low_hp",
            value=0.0,
            description="若当前生命值百分比小于等于50%，则被敌方目标攻击的概率降低",
        ),
        # A2: 生命值+4%，攻击力+4%
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="max_hp_increase",
            value=0.04,
            description="生命值提高4%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            description="攻击力提高4%",
        ),
        # A3: 逐寇 - 剑势伤害+2.5%（最多10层）
        Passive(
            name="逐寇",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="jian_shi_dmg_stack",
            value=0.025,
            description="每发动1次【剑势】，【剑势】造成的伤害提高2.5%，该效果最多叠加10层",
        ),
        # A3: 攻击力+6%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
        # A4: 攻击力+6%，生命值+6%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            description="攻击力提高6%",
        ),
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="max_hp_increase",
            value=0.06,
            description="生命值提高6%",
        ),
        # A5: 破敌 - 击破弱点后行动提前15%
        Passive(
            name="破敌",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="advance_on_break",
            value=0.15,
            description="施放普攻或战技后，若场上有敌方目标处于弱点击破状态，则素裳的行动提前15%",
        ),
        # A6: 防御力+7.5%，生命值+8%
        Passive(
            name="防御力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.075,
            description="防御力提高7.5%",
        ),
        Passive(
            name="生命强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="max_hp_increase",
            value=0.08,
            description="生命值提高8%",
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
        # Lv1: 防御力+5%，攻击力+6%
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
            value=0.06,
            description="攻击力提高6%",
        ),
    ]


def create_all_sushang_skills() -> list[Skill]:
    return [
        create_sushang_basic_skill(),
        create_sushang_special_skill(),
        create_sushang_ult_skill(),
        create_sushang_talent_skill(),
    ]
