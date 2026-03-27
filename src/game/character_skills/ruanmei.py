"""
阮梅 (Ruan Mei) 角色技能设计

基于 https://starrailstation.com/cn/character/ruanmei#skills 数据

角色定位：同谐+冰 - 击破特攻+结界延长

==============================
技能
==============================

【普攻】一针幽兰
- Break 30
- 对指定敌方单体造成等同于阮梅50%攻击力的冰属性伤害

【战技】慢捻抹复挑
- 阮梅获得【弦外音】，持续3回合
- 我方全体伤害提高16%
- 弱点击破效率提高50%

【终结技】摇花缎水，沾衣不摘
- 展开结界，持续2回合
- 结界中我方全属性抗性穿透提高15%
- 攻击后对敌方施加【残梅绽】

【天赋】分型的螺旋
- 队友速度提高8%
- 队友击破弱点时，阮梅造成额外击破伤害

==============================
机制
==============================

【弦外音】：增伤+击破效率
【结界】：延长弱点击破状态
【残梅绽】：敌人试图恢复时触发，延长击破+造成击破伤害
【击破特攻】：阮梅核心属性
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


def create_ruanmei_basic_skill() -> Skill:
    """普攻：一针幽兰 - 50% ATK"""
    return Skill(
        name="一针幽兰",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.ICE,
        description="对指定敌方单体造成50%攻击力的冰属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_ruanmei_special_skill() -> Skill:
    """战技：慢捻抹复挑 - 【弦外音】增伤"""
    return Skill(
        name="慢捻抹复挑",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.ICE,
        description="获得【弦外音】3回合，我方伤害+16%，击破效率+50%",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="弦外音",
    )


def create_ruanmei_ult_skill() -> Skill:
    """终结技：摇花缎水，沾衣不摘 - 结界"""
    return Skill(
        name="摇花缎水，沾衣不摘",
        type=SkillType.ULT,
        multiplier=0.0,
        damage_type=Element.ICE,
        description="展开结界2回合，全队抗性穿透+15%，攻击后施加【残梅绽】",
        energy_gain=5.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="阮梅结界",
        target_count=-1,
    )


def create_ruanmei_talent_skill() -> Skill:
    """天赋：分型的螺旋 - 击破追击"""
    return Skill(
        name="分型的螺旋",
        type=SkillType.TALENT,
        multiplier=0.60,  # 60%击破伤害
        damage_type=Element.ICE,
        description="队友击破弱点时，阮梅造成60%冰属性击破伤害",
        energy_gain=0.0,
        break_power=0,
    )


def create_ruanmei_passives() -> list[Passive]:
    """阮梅的被动技能"""
    return [
        Passive(
            name="物体呼吸中",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="break_dmg_bonus_party",
            value=0.20,
            description="我方全体击破特攻+20%",
        ),
        Passive(
            name="日消遐思长",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="energy_per_turn",
            value=5.0,
            description="回合开始时自身恢复5点能量",
        ),
        Passive(
            name="落烛照水燃",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="dmg_bonus_break_ratio",
            value=0.06,
            description="击破特攻>120%时，每超10%战技增伤效果+6%",
        ),
    ]


def create_all_ruanmei_skills() -> list[Skill]:
    return [
        create_ruanmei_basic_skill(),
        create_ruanmei_special_skill(),
        create_ruanmei_ult_skill(),
        create_ruanmei_talent_skill(),
    ]
