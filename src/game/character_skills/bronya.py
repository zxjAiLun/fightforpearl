"""
布洛妮娅 (Bronya) 角色技能设计

基于 https://starrailstation.com/cn/character/bronya#skills 数据

角色定位：风属性同谐 - 拉条+增伤辅助

==============================
技能
==============================

【普攻】驭风的子弹
- Break 30
- 对指定敌方单体造成等同于布洛妮娅50%攻击力的风属性伤害

【战技】作战再部署
- 解除指定我方单体的1个负面效果
- 使该目标立即行动
- 造成的伤害提高33%，持续1回合
- 当对自身施放时，无法触发立即行动效果

【终结技】贝洛伯格进行曲
- 使我方全体攻击力提高33%
- 使我方全体暴击伤害提高12%+12%
- 持续2回合

【天赋】先人一步
- 施放普攻后，布洛妮娅的下一次行动提前15%

==============================
行迹
==============================

A1: 50%概率恢复1战技点
A2: 普攻暴击率100%
A4: 队友攻击风弱敌人时，布洛妮娅立即进行1次追加攻击(80%普攻伤害)
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_bronya_basic_skill() -> Skill:
    """普攻：驭风的子弹 - 50% ATK"""
    return Skill(
        name="驭风的子弹",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.WIND,
        description="对指定敌方单体造成50%攻击力的风属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_bronya_special_skill() -> Skill:
    """战技：作战再部署 - 拉条+驱散+增伤"""
    return Skill(
        name="作战再部署",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="解除我方1个负面效果，使目标立即行动，伤害+33%持续1回合",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="作战再部署",
    )


def create_bronya_ult_skill() -> Skill:
    """终结技：贝洛伯格进行曲 - 全队增伤+爆伤"""
    return Skill(
        name="贝洛伯格进行曲",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="我方全体攻击力+33%，暴击伤害+12%+12%持续2回合",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="贝洛伯格进行曲",
        target_count=-1,
    )


def create_bronya_talent_skill() -> Skill:
    """天赋：先人一步 - 普攻后下次行动提前"""
    return Skill(
        name="先人一步",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="施放普攻后，布洛妮娅的下一次行动提前15%",
        energy_gain=5.0,
        break_power=30,
    )


def create_bronya_passives() -> list[Passive]:
    """布洛妮娅的被动技能"""
    return [
        Passive(
            name="号令",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="basic_crit_100",
            value=1.0,
            description="普攻的暴击率提高至100%",
        ),
        Passive(
            name="阵地",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_bonus_on_battle_start",
            value=0.20,
            description="战斗开始时，我方全体防御力+20%持续2回合",
        ),
        Passive(
            name="军势",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_bonus_party",
            value=0.10,
            description="布洛妮娅在场时，我方全体造成的伤害+10%",
        ),
    ]


def create_all_bronya_skills() -> list[Skill]:
    return [
        create_bronya_basic_skill(),
        create_bronya_special_skill(),
        create_bronya_ult_skill(),
        create_bronya_talent_skill(),
    ]
