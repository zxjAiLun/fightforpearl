"""
银狼 (Silverwolf) - 崩坏：星穹铁道

角色定位：虚无·量子 - 弱点植入 + 负面效果

关键机制：
1. 战技：为敌方添加我方属性的弱点（植入弱点），同时降低全属性抗性
2. 终结技：降低敌方防御力
3. 天赋：攻击后60%概率植入【缺陷】（攻击力↓/防御力↓/速度↓）
4. 秘技：战斗开始对敌方全体造成伤害并削韧

量子属性关联：量子属性伤害、效果命中
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============== 银狼技能 ==============

def create_silverwolf_basic_skill() -> Skill:
    """银狼普攻：系统警告"""
    return Skill(
        name="系统警告",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.QUANTUM,
        description="对指定敌方单体造成等同于银狼50%攻击力的量子属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_silverwolf_special_skill() -> Skill:
    """银狼战技：是否允许更改？"""
    return Skill(
        name="是否允许更改？",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.98,
        damage_type=Element.QUANTUM,
        description="有75%基础概率为敌方添加1个我方属性弱点（持续2回合），同时降低全属性抗性7.5%（持续2回合）。战技造成98%攻击力量子伤害",
        energy_gain=30.0,
        break_power=60,
        # 植入弱点效果通过天赋/被动系统处理
        is_support_skill=False,
    )


def create_silverwolf_ult_skill() -> Skill:
    """银狼终结技：账号已封禁"""
    return Skill(
        name="账号已封禁",
        type=SkillType.ULT,
        multiplier=2.28,
        damage_type=Element.QUANTUM,
        description="有85%基础概率使敌方防御力降低36%（持续3回合），同时造成228%攻击力量子伤害",
        energy_gain=5.0,
        break_power=90,
        # 降低防御力效果通过support_modifier处理
        is_support_skill=False,
    )


def create_silverwolf_talent_skill() -> Skill:
    """银狼天赋：等待程序响应…"""
    return Skill(
        name="等待程序响应…",
        type=SkillType.TALENT,
        multiplier=0.0,
        damage_type=Element.QUANTUM,
        description="银狼能够制造攻击力降低5%、防御力降低4%、速度降低3%3种【缺陷】。攻击后有60%基础概率给目标植入1个随机【缺陷】（持续3回合）",
        energy_gain=0.0,
        break_power=0,
    )


def create_silverwolf_technique_skill() -> Skill:
    """银狼秘技：强制结束进程"""
    return Skill(
        name="强制结束进程",
        type=SkillType.FESTIVITY,
        cost=0,
        multiplier=0.80,
        damage_type=Element.QUANTUM,
        description="进入战斗后对敌方全体造成80%攻击力量子伤害，无视弱点削韧",
        energy_gain=0.0,
        break_power=60,
        target_count=-1,
    )


def create_all_silverwolf_skills() -> list[Skill]:
    """创建银狼所有技能"""
    return [
        create_silverwolf_basic_skill(),
        create_silverwolf_special_skill(),
        create_silverwolf_ult_skill(),
        create_silverwolf_talent_skill(),
        create_silverwolf_technique_skill(),
    ]


# ============== 效果应用辅助函数 ==============

def apply_silverwolf_talent_defect(caster: Character, target: Character) -> list[Modifier]:
    """
    应用银狼天赋【缺陷】效果
    有60%概率植入1个随机缺陷
    
    缺陷类型：
    - 攻击力降低5%（持续3回合）
    - 防御力降低4%（持续3回合）
    - 速度降低3%（持续3回合）
    """
    import random
    
    if random.random() > 0.60:
        return []  # 60%基础概率不触发
    
    defect_roll = random.random()
    if defect_roll < 0.333:
        # 攻击力降低5%
        mod = Modifier(
            name="缺陷-攻击力降低",
            source_skill="等待程序响应…",
            duration=3,
            modifier_type=ModifierType.DEBUFF,
            atk_pct=-0.05,
        )
    elif defect_roll < 0.666:
        # 防御力降低4%
        mod = Modifier(
            name="缺陷-防御力降低",
            source_skill="等待程序响应…",
            duration=3,
            modifier_type=ModifierType.DEBUFF,
            def_pct=-0.04,
        )
    else:
        # 速度降低3%
        mod = Modifier(
            name="缺陷-速度降低",
            source_skill="等待程序响应…",
            duration=3,
            modifier_type=ModifierType.DEBUFF,
            spd_pct=-0.03,
        )
    
    target.add_modifier(mod)
    return [mod]


def apply_silverwolf_ult_def_down(caster: Character, target: Character) -> Modifier:
    """
    应用银狼大招的防御力降低效果
    85%基础概率使目标防御力降低36%，持续3回合
    """
    import random
    
    if random.random() > 0.85:
        return None
    
    mod = Modifier(
        name="账号已封禁-防御降低",
        source_skill="账号已封禁",
        duration=3,
        modifier_type=ModifierType.DEBUFF,
        def_pct=-0.36,
    )
    target.add_modifier(mod)
    return mod


def apply_silverwolf_technique_weakness(
    caster: Character,
    target: Character,
    caster_elements: list[Element]
) -> Modifier | None:
    """
    应用银狼战技的弱点植入效果
    75%基础概率为敌方添加1个银狼属性的弱点
    """
    import random
    
    if random.random() > 0.75:
        return None
    
    # 使用银狼的主属性（量子）
    mod = Modifier(
        name="是否允许更改？-弱点植入",
        source_skill="是否允许更改？",
        duration=2,
        modifier_type=ModifierType.DEBUFF,
        vuln_pct=0.0,  # 弱点植入通过特殊字段处理
    )
    target.add_modifier(mod)
    return mod
