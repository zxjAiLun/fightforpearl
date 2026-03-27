"""
姬子 (Himeko) - 崩坏：星穹铁道

角色定位：智识·火 - AOE火伤 + 追击

关键机制：
1. 普攻：单体火伤
2. 战技：扩散伤害（主目标+相邻目标）
3. 终结技：全体火伤 + 击杀回复能量
4. 天赋：弱点击破后获得充能（上限3），充能满时普攻后触发AOE追击
5. 秘技：战斗开始使敌人受到火伤+10%

火属性伤害加成
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 姬子技能 ==============

def create_himeko_basic_skill() -> Skill:
    """姬子普攻：武装调律"""
    return Skill(
        name="武装调律",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成等同于姬子50%攻击力的火属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_himeko_special_skill() -> Skill:
    """姬子战技：熔核爆裂"""
    return Skill(
        name="熔核爆裂",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=1.00,
        damage_type=Element.FIRE,
        description="对指定敌方单体造成100%攻击力火属性伤害，同时对其相邻目标造成40%攻击力火属性伤害",
        energy_gain=30.0,
        break_power=60,
        spread_count=1,
        spread_multiplier=0.4,
    )


def create_himeko_ult_skill() -> Skill:
    """姬子终结技：天坠之火"""
    return Skill(
        name="天坠之火",
        type=SkillType.ULT,
        multiplier=1.38,
        damage_type=Element.FIRE,
        description="对敌方全体造成138%攻击力的火属性伤害，每消灭1个敌方目标额外恢复姬子5点能量",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,
        aoe_multiplier=1.0,
    )


def create_himeko_talent_skill() -> Skill:
    """姬子天赋：乘胜追击"""
    return Skill(
        name="乘胜追击",
        type=SkillType.TALENT,
        multiplier=0.70,
        damage_type=Element.FIRE,
        description="弱点击破后姬子获得1点充能（上限3点）。充能满时，我方目标施放攻击后姬子发动追加攻击，对敌方全体造成70%攻击力火属性伤害",
        energy_gain=10.0,
        break_power=30,
        target_count=-1,
    )


def create_himeko_technique_skill() -> Skill:
    """姬子秘技：不完全燃烧"""
    return Skill(
        name="不完全燃烧",
        type=SkillType.FESTIVITY,
        cost=0,
        multiplier=0.0,
        damage_type=Element.FIRE,
        description="进入战斗后，有100%基础概率使敌方目标受到的火属性伤害提高10%，持续2回合",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="不完全燃烧-易伤",
    )


def create_himeko_passives() -> list[Passive]:
    """创建姬子的行迹被动"""
    return [
        # A2: 星火 - 攻击后50%概率使目标灼烧
        Passive(
            name="星火",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="burn_chance",
            value=0.50,
            duration=2,
            description="攻击后有50%基础概率使目标陷入灼烧状态，持续2回合",
        ),
        # A2: 攻击力+4%, 火属性伤害+3.2%
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.04,
            duration=0,
            description="攻击力+4%",
        ),
        Passive(
            name="火属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="fire_dmg_increase",
            value=0.032,
            duration=0,
            description="火属性伤害+3.2%",
        ),
        # A3: 灼热 - 战技对灼烧目标伤害+20%
        Passive(
            name="灼热",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="burn_dmg_bonus",
            value=0.20,
            duration=0,
            description="战技对灼烧状态下的敌方目标造成的伤害提高20%",
        ),
        # A4: 火属性伤害+4.8%, 攻击力+6%
        Passive(
            name="火属性伤害强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="fire_dmg_increase",
            value=0.048,
            duration=0,
            description="火属性伤害+4.8%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.06,
            duration=0,
            description="攻击力+6%",
        ),
        # A5: 道标 - HP>=80%时暴击率+15%
        Passive(
            name="道标",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="crit_rate_high_hp",
            value=0.15,
            duration=0,
            description="若当前生命值百分比大于等于80%，则暴击率提高15%",
        ),
        # A6: 效果抵抗+6%, 攻击力+8%
        Passive(
            name="效果抵抗强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="effect_res_increase",
            value=0.06,
            duration=0,
            description="效果抵抗+6%",
        ),
        Passive(
            name="攻击力强化",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.08,
            duration=0,
            description="攻击力+8%",
        ),
    ]


def create_all_himeko_skills() -> list[Skill]:
    """创建姬子所有技能"""
    return [
        create_himeko_basic_skill(),
        create_himeko_special_skill(),
        create_himeko_ult_skill(),
        create_himeko_talent_skill(),
        create_himeko_technique_skill(),
    ]


# ============== 效果应用辅助函数 ==============

def apply_himeko_charge(caster: Character) -> int:
    """
    为姬子增加1点充能
    返回当前充能数
    """
    if not hasattr(caster, '_himeko_charges'):
        caster._himeko_charges = 1  # 战斗开始获得1点充能
    else:
        caster._himeko_charges = min(3, caster._himeko_charges + 1)
    return caster._himeko_charges


def get_himeko_charges(caster: Character) -> int:
    """获取姬子当前充能数"""
    return getattr(caster, '_himeko_charges', 0)


def consume_himeko_charge(caster: Character) -> int:
    """
    消耗姬子全部充能
    返回消耗的充能数
    """
    charges = get_himeko_charges(caster)
    caster._himeko_charges = 0
    return charges


def apply_himeko_technique_fire_vuln(caster: Character, targets: list[Character]) -> list[Modifier]:
    """
    应用姬子秘技的火属性易伤效果
    使目标受到的火属性伤害+10%，持续2回合
    """
    modifiers = []
    for target in targets:
        mod = Modifier(
            name="不完全燃烧-易伤",
            source_skill="不完全燃烧",
            duration=2,
            modifier_type=ModifierType.DEBUFF,
            fire_dmg_pct=0.10,  # 受到的火属性伤害+10% (通过易伤机制实现)
        )
        target.add_modifier(mod)
        modifiers.append(mod)
    return modifiers


def apply_himeko_burn(caster: Character, target: Character) -> Modifier | None:
    """
    应用姬子A2被动【星火】的灼烧效果
    50%概率使目标陷入灼烧状态，持续2回合
    """
    import random
    
    if random.random() > 0.50:
        return None
    
    from src.game.models import BreakEffectType
    mod = Modifier(
        name="星火-灼烧",
        source_skill="星火",
        duration=2,
        modifier_type=ModifierType.DEBUFF,
        break_type=BreakEffectType.BURN,
    )
    target.add_modifier(mod)
    return mod
