"""
刻律德菈 (Celydra) 角色技能设计

角色定位：同谐风属性 - 军功机制核心角色
- 军功/爵位状态机：充能达到6点时军功升级为爵位，爵位期间战技触发奇袭
- 奇袭机制：爵位激活时战技触发奇袭（复制技能提前施放），消耗6点充能后变回军功
- 战技免费释放：秘技效果使下次战斗开始时自动施放战技，不消耗战技点
- 同谐风属性：提供攻击力加成、暴击率、速度等辅助
"""

from src.game.modifier import Modifier, ModifierType, ModifierStacking
from src.game.models import Character, Element, Skill, SkillType, Passive


# ============================================================================
# 角色状态标记常量
# ============================================================================

# 军功 Modifier 名称
MOD_MILITARY_MERIT = "军功"
MOD_NOBLE_TITLE = "爵位"
MOD_CELYDRA_MERIT = "刻律德菈-军功"   # 标记在军功持有者身上的modifier名

# Celydra 自身状态标记
class CelydraState:
    """刻律德菈自身状态追踪（不存储在Character对象上，而是通过函数参数传递或全局状态）"""
    def __init__(self):
        # 充能点数 (上限8，达到6时升级爵位)
        self.charge: int = 0
        # 当前军功目标（角色名）
        self.merit_target_name: str = ""
        # 军功是否已升级为爵位
        self.is_noble_title: bool = False
        # 奇袭期间不能充能
        self.surprise_attack_active: bool = False
        # 附加伤害触发次数上限 (20次)
        self.follow_up_hits_remaining: int = 20
        # 爵位激活的战技是否已触发过奇袭（防止递归）
        self.noble_special_surprise_triggered: bool = False
        # 见者：军功角色施放终结技充能效果（单场1次）
        self.merit_ult_charge_used: bool = False
        # 秘技：下次战斗开始时自动战技的目标
        self.technique_auto_target_name: str = ""
        # 秘技：是否已激活（下次战斗开始时触发）
        self.technique_ready: bool = False

    def reset_per_battle(self):
        """每场战斗重置"""
        self.charge = 0
        self.merit_target_name = ""
        self.is_noble_title = False
        self.surprise_attack_active = False
        self.follow_up_hits_remaining = 20
        self.noble_special_surprise_triggered = False
        self.merit_ult_charge_used = False
        self.technique_auto_target_name = ""
        self.technique_ready = False


# 全局状态存储（每个Celydra角色实例独享）
_celydra_states: dict[int, CelydraState] = {}


def _get_celydra_state(caster: Character) -> CelydraState:
    """获取或创建角色的Celydra状态"""
    cid = id(caster)
    if cid not in _celydra_states:
        _celydra_states[cid] = CelydraState()
    return _celydra_states[cid]


def _clear_celydra_state(caster: Character):
    """清理角色状态"""
    cid = id(caster)
    if cid in _celydra_states:
        del _celydra_states[cid]


# ============================================================================
# 技能定义
# ============================================================================

def create_celydra_basic_skill() -> Skill:
    """普攻：易位，兵贵神速 - 对敌方单体造成风属性伤害"""
    return Skill(
        name="易位，兵贵神速",
        type=SkillType.BASIC,
        multiplier=1.0,
        damage_type=Element.WIND,
        description="对指定敌方单体造成50%/100%攻击力的风属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=10,
    )


def create_celydra_special_skill() -> Skill:
    """战技：升变，士皆可帅 - 给予军功/爵位效果"""
    return Skill(
        name="升变，士皆可帅",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="使指定我方单体角色获得【军功】，充能达到6时升级为【爵位】",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name=MOD_MILITARY_MERIT,
    )


def create_celydra_ult_skill() -> Skill:
    """终结技：世事如棋，四步堪杀 - 全体风伤害 + 充能 + 附加军功"""
    return Skill(
        name="世事如棋，四步堪杀",
        type=SkillType.ULT,
        multiplier=2.40,
        damage_type=Element.WIND,
        description="对敌方全体造成144%/240%攻击力的风属性伤害，获得2点充能",
        energy_gain=5.0,
        break_power=20,
        target_count=-1,   # 全体
    )


def create_celydra_technique_skill() -> Skill:
    """秘技：先手优势 - 军功准备 + 战斗开始自动战技"""
    return Skill(
        name="先手优势",
        type=SkillType.TALENT,  # 使用TALENT类型代表秘技
        cost=0,
        multiplier=0.0,
        damage_type=Element.WIND,
        description="使自身获得【军功】，切换角色时军功转移，下次战斗开始时自动施放战技（不消耗战技点）",
        energy_gain=0.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="先手优势",
    )


# ============================================================================
# 被动技能（行迹/额外能力）
# ============================================================================

def create_celydra_passives() -> list[Passive]:
    """刻律德菈的被动技能（天赋+额外能力）"""
    return [
        # 天赋：荣光属于凯撒
        Passive(
            name="荣光属于凯撒-攻击加成",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="atk_increase",
            value=0.24,
            duration=999,  # 持续到军功目标改变
            description="持有【军功】的角色攻击力提高等同于刻律德菈攻击力的24%",
        ),
        # 额外能力1：来者
        Passive(
            name="来者",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="来者",
            value=0.0,
            duration=0,
            description="攻击力大于2000时，每超过100点使暴击伤害提高18%，最多360%",
        ),
        # 额外能力2：见者
        Passive(
            name="见者",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="见者",
            value=0.0,
            duration=0,
            description="暴击率提高100%，军功角色施放终结技时使刻律德菈获得1点充能（单场1次）",
        ),
        # 额外能力3：征服者
        Passive(
            name="征服者",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="征服者",
            value=0.0,
            duration=0,
            description="施放战技时使自身和军功角色速度提高20点，持续3回合；军功角色施放普攻/战技时为刻律德菈恢复5点能量",
        ),
    ]


def create_all_celydra_skills() -> list[Skill]:
    return [
        create_celydra_basic_skill(),
        create_celydra_special_skill(),
        create_celydra_ult_skill(),
    ]


# ============================================================================
# 核心机制：军功/爵位状态机
# ============================================================================

def apply_military_merit(caster: Character, target: Character) -> list[Modifier]:
    """
    对目标应用【军功】效果
    
    军功效果：
    1. 目标攻击力提高：+24% of Caster's ATK
    2. 目标施放普攻/战技时，Caster 获得1点充能（奇袭期间除外）
    3. 目标施放攻击后，Caster 额外造成1次 60% ATK 的风属性附加伤害
    4. 场上只能存在一个军功目标（目标改变时 Caster 充能重置为0）
    """
    state = _get_celydra_state(caster)
    
    # 如果新目标和当前目标不同，重置充能
    if state.merit_target_name and state.merit_target_name != target.name:
        state.charge = 0
    
    state.merit_target_name = target.name
    state.is_noble_title = False
    
    modifiers = []
    
    # 1. 军功 ATK 加成
    atk_bonus_pct = 0.24
    merit_mod = Modifier(
        name=f"{MOD_MILITARY_MERIT}-{target.name}",
        source_skill="升变，士皆可帅",
        duration=999,  # 持续到主动移除
        modifier_type=ModifierType.BUFF,
        atk_pct=atk_bonus_pct,
    )
    target.add_modifier(merit_mod)
    modifiers.append(merit_mod)
    
    # 2. 标记目标身上的军功状态（用于触发附加伤害）
    # 这个modifier用于标识军功存在
    marker = Modifier(
        name=MOD_CELYDRA_MERIT,
        source_skill="荣光属于凯撒",
        duration=999,
        modifier_type=ModifierType.BUFF,
        # 附加伤害通过事件系统触发，这里只做标记
    )
    target.add_modifier(marker)
    modifiers.append(marker)
    
    return modifiers


def upgrade_to_noble_title(caster: Character, target: Character) -> list[Modifier]:
    """
    将【军功】升级为【爵位】
    
    爵位效果：
    1. 视为同时持有【军功】
    2. 战技伤害的暴伤提高72%，全属性抗性穿透提高10%
    3. 对敌方目标施放战技时触发奇袭
    4. 奇袭结束后消耗6点充能变回【军功】
    """
    state = _get_celydra_state(caster)
    state.is_noble_title = True
    state.noble_special_surprise_triggered = False
    
    modifiers = []
    
    # 爵位：暴伤+72%
    noble_crit_mod = Modifier(
        name=f"{MOD_NOBLE_TITLE}-暴伤",
        source_skill="升变，士皆可帅",
        duration=999,
        modifier_type=ModifierType.BUFF,
        crit_dmg_pct=0.72,
    )
    target.add_modifier(noble_crit_mod)
    modifiers.append(noble_crit_mod)
    
    # 爵位：全属性抗性穿透+10%（简化处理，用quantum_dmg_pct表示穿透）
    # 注意：游戏中通常有专门的穿透字段，这里用dmg_pct作为载体
    # 实际穿透在damage.py中需要特殊处理，这里预留接口
    noble_pen_mod = Modifier(
        name=f"{MOD_NOBLE_TITLE}-抗穿",
        source_skill="升变，士皆可帅",
        duration=999,
        modifier_type=ModifierType.BUFF,
        # 抗穿透字段（游戏中需支持）
    )
    target.add_modifier(noble_pen_mod)
    modifiers.append(noble_pen_mod)
    
    return modifiers


def remove_noble_title(caster: Character, target: Character) -> None:
    """移除爵位效果，变回军功"""
    state = _get_celydra_state(caster)
    state.is_noble_title = False
    state.charge = max(0, state.charge - 6)
    
    # 移除爵位modifier
    target.modifier_manager.remove_modifier(f"{MOD_NOBLE_TITLE}-暴伤")
    target.modifier_manager.remove_modifier(f"{MOD_NOBLE_TITLE}-抗穿")


def apply_charge(caster: Character, amount: int) -> int:
    """
    增加充能，返回实际增加的量
    奇袭期间无法获得充能
    充能达到6时自动升级为爵位
    """
    state = _get_celydra_state(caster)
    
    # 奇袭期间不能获得充能
    if state.surprise_attack_active:
        return 0
    
    old_charge = state.charge
    state.charge = min(8, state.charge + amount)
    
    gained = state.charge - old_charge
    
    # 达到6点时自动升级为爵位
    if old_charge < 6 and state.charge >= 6 and state.merit_target_name:
        # 找到军功目标并升级
        from src.game.battle import BattleState
        battle_state = getattr(caster, '_battle_state', None)
        if battle_state:
            for char in battle_state.player_team:
                if char.name == state.merit_target_name:
                    upgrade_to_noble_title(caster, char)
                    break
    
    return gained


def trigger_surprise_attack(
    caster: Character,
    target_char: Character,
    original_skill: Skill,
    battle_state,
) -> list:
    """
    触发奇袭机制
    
    奇袭：爵位激活时，施放战技会触发奇袭
    复制一次即将施放的技能并提前施放，随后施放原技能
    奇袭不会再次触发奇袭
    
    Returns:
        奇袭执行结果列表 [(target, damage_result), ...]
    """
    from src.game.damage import calculate_damage, apply_damage, DamageResult
    from src.game.skill import SkillExecutor
    from src.game.models import DamageSource
    
    state = _get_celydra_state(caster)
    state.surprise_attack_active = True
    state.noble_special_surprise_triggered = True  # 防止递归
    
    executor = SkillExecutor()
    results = []
    
    # 构建奇袭技能（复制原技能，但标记为奇袭触发）
    surprise_skill = Skill(
        name=f"奇袭·{original_skill.name}",
        type=original_skill.type,
        multiplier=original_skill.multiplier,
        damage_type=original_skill.damage_type,
        description=f"奇袭复制技能：{original_skill.description}",
        energy_gain=0.0,  # 奇袭不回复能量
        break_power=original_skill.break_power,
        target_count=original_skill.target_count,
        aoe_multiplier=original_skill.aoe_multiplier,
        ricochet_count=original_skill.ricochet_count,
        ricochet_decay=original_skill.ricochet_decay,
        spread_count=original_skill.spread_count,
        spread_multiplier=original_skill.spread_multiplier,
        is_support_skill=original_skill.is_support_skill,
        support_modifier_name=original_skill.support_modifier_name,
    )
    
    # 奇袭提前施放：找出敌方目标
    opponents = []
    if battle_state:
        opponents = [e for e in battle_state.enemy_team if e.is_alive()]
    
    if opponents:
        # 对敌方施放奇袭
        for opp in opponents[:surprise_skill.target_count if surprise_skill.target_count > 0 else len(opponents)]:
            result = calculate_damage(
                caster, opp,
                skill_multiplier=surprise_skill.multiplier,
                damage_type=surprise_skill.damage_type,
                damage_source=DamageSource.FOLLOW_UP,
                attacker_is_player=not caster.is_enemy,
            )
            apply_damage(caster, opp, result)
            results.append((opp, result))
    
    state.surprise_attack_active = False
    
    return results


def trigger_follow_up_damage(
    caster: Character,
    merit_holder: Character,
    battle_state,
) -> list:
    """
    触发军功附加伤害
    军功角色施放攻击后，刻律德菈额外造成1次 60% ATK 的风属性附加伤害
    该伤害使受击者额外受到1次伤害（本次伤害不视为造成了1次攻击）
    """
    from src.game.damage import calculate_damage, apply_damage, DamageResult
    from src.game.models import DamageSource
    
    state = _get_celydra_state(caster)
    
    if state.follow_up_hits_remaining <= 0:
        return []
    
    # 找到攻击目标（简化：随机选一个敌方）
    opponents = []
    if battle_state:
        opponents = [e for e in battle_state.enemy_team if e.is_alive()]
    
    if not opponents:
        return []
    
    target = opponents[0]
    
    # 计算附加伤害：60% ATK
    atk = caster.stat.total_atk()
    follow_up_mult = 0.60
    result = calculate_damage(
        caster, target,
        skill_multiplier=follow_up_mult,
        damage_type=Element.WIND,
        damage_source=DamageSource.附加,
        attacker_is_player=not caster.is_enemy,
    )
    apply_damage(caster, target, result)
    
    state.follow_up_hits_remaining -= 1
    
    return [(target, result)]


def on_merit_holder_attacks(
    caster: Character,
    merit_holder: Character,
    battle_state,
    skill_type: SkillType,
) -> None:
    """
    当军功持有者施放普攻或战技时调用
    
    效果：
    1. Caster 获得1点充能（奇袭期间除外）
    2. 军功角色施放攻击后，Caster 额外造成1次附加伤害
    3. 征服者：军功角色施放普攻/战技时为 Caster 恢复5点能量
    """
    state = _get_celydra_state(caster)
    
    # 1. 获得充能（奇袭期间不能获得）
    if not state.surprise_attack_active:
        apply_charge(caster, 1)
    
    # 2. 触发附加伤害
    if state.merit_target_name == merit_holder.name:
        trigger_follow_up_damage(caster, merit_holder, battle_state)
    
    # 3. 征服者：恢复能量
    caster.add_energy(5.0, affected_by_recovery_rate=True)


def on_merit_holder_uses_ult(
    caster: Character,
    merit_holder: Character,
) -> None:
    """
    当军功持有者施放终结技时调用
    
    效果：
    1. 若 Caster 充能未满，军功角色施放终结技时使 Caster 获得1点充能（单场1次）
    2. 附加伤害触发
    """
    state = _get_celydra_state(caster)
    
    # 见者效果：单场1次，充能未满时+1充能
    if not state.merit_ult_charge_used and state.charge < 8:
        state.merit_ult_charge_used = True
        apply_charge(caster, 1)
    
    # 触发附加伤害
    if state.merit_target_name == merit_holder.name:
        from src.game.battle import BattleState
        battle_state = getattr(caster, '_battle_state', None)
        if battle_state:
            trigger_follow_up_damage(caster, merit_holder, battle_state)


def on_celydra_uses_ult(
    caster: Character,
    battle_state,
) -> None:
    """
    当刻律德菈施放终结技时调用
    
    效果：
    1. 获得2点充能
    2. 重置附加伤害可触发次数（20次）
    3. 对敌方全体造成伤害
    4. 若场上不存在军功角色，优先使队伍第一位获得军功
    """
    state = _get_celydra_state(caster)
    
    # 1. 获得2点充能
    apply_charge(caster, 2)
    
    # 2. 重置附加伤害次数
    state.follow_up_hits_remaining = 20
    
    # 3. 检查是否需要施加军功
    if not state.merit_target_name and battle_state:
        team = battle_state.player_team
        for char in team:
            if char.is_alive() and char.name != caster.name:
                apply_military_merit(caster, char)
                break


def on_celydra_uses_special(
    caster: Character,
    target_char: Character,
    battle_state,
) -> None:
    """
    当刻律德菈施放战技时调用
    
    效果：
    1. 使目标获得军功，Caster 获得1点充能
    2. 若爵位激活，触发奇袭
    3. 奇袭结束后消耗6点充能变回军功
    """
    state = _get_celydra_state(caster)
    
    # 1. 应用军功
    apply_military_merit(caster, target_char)
    
    # 2. 获得1点充能
    apply_charge(caster, 1)
    
    # 3. 检查是否触发奇袭
    if state.is_noble_title and not state.noble_special_surprise_triggered:
        # 找到目标角色身上的技能（简化：使用目标的战技）
        # 实际上奇袭是复制Celydra当前要施放的技能
        # 触发奇袭
        surprise_results = trigger_surprise_attack(
            caster, target_char,
            create_celydra_basic_skill(),  # 简化：复制普攻
            battle_state,
        )
        
        # 奇袭结束后消耗6点变回军功
        if state.is_noble_title:
            # 找到军功目标
            if battle_state:
                for char in battle_state.player_team:
                    if char.name == state.merit_target_name:
                        remove_noble_title(caster, char)
                        break


# ============================================================================
# 秘技效果
# ============================================================================

def activate_celydra_technique(caster: Character) -> None:
    """
    激活秘技效果
    1. 使自身获得军功
    2. 标记下次战斗开始时自动施放战技
    """
    state = _get_celydra_state(caster)
    
    # 标记秘技准备状态
    state.technique_ready = True
    state.merit_target_name = caster.name
    state.technique_auto_target_name = caster.name
    
    # 给予军功标记
    caster.add_modifier(Modifier(
        name="先手优势-军功",
        source_skill="先手优势",
        duration=999,
        modifier_type=ModifierType.BUFF,
    ))


def on_battle_start_auto_special(caster: Character, battle_state) -> None:
    """
    战斗开始时自动施放战技（秘技效果）
    不消耗战技点
    """
    state = _get_celydra_state(caster)
    
    if not state.technique_ready:
        return
    
    state.technique_ready = False
    
    # 找到军功目标
    target_name = state.technique_auto_target_name
    if not target_name:
        return
    
    # 找到目标角色
    target = None
    for char in battle_state.player_team:
        if char.name == target_name:
            target = char
            break
    
    if target:
        # 应用军功
        apply_military_merit(caster, target)
        # 获得1点充能
        apply_charge(caster, 1)
