"""
丹恒·腾荒 (Danheng • Permansor Terrae) 完整技能设计

基于 https://starrailstation.com/en/character/danhengpt 数据

==============================
角色定位
==============================
- 命途：存护 (Preservation)
- 属性：物理 (Physical)
- 核心机制：护盾系统、龙灵(Souldragon)召唤、挚友(Bondmate)机制

==============================
护盾系统
==============================
- 基础护盾：14% ATK + 100（战技/大招）
- 龙灵护盾：7% ATK + 50（龙灵行动时）
- 护盾可叠加，上限300%当前护盾值
- 护盾吸收伤害时优先消耗护盾值

==============================
龙灵 (Souldragon)
==============================
- 速度：165 SPD
- 行动时：驱散1个debuff + 提供护盾
- 追击：40% ATK物理伤害 + 40%挚友ATK（挚友属性伤害）
- 强化后：额外2次追击，挚友伤害200%

==============================
挚友 (Bondmate)
==============================
- 指定一名队友，龙灵跟随协助
- 终结技后龙灵强化
- 挚友阵亡时龙灵消失
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from src.game.modifier import Modifier, ModifierType, ModifierStacking, ModifierManager
from src.game.summon import Summon, SummonState, SummonManager
from src.game.models import Character, Element, Skill, SkillType, Passive, Effect, DamageSource

if TYPE_CHECKING:
    from src.game.damage import DamageResult


# ============== 护盾系统 ==============

@dataclass
class Shield:
    """
    护盾数据
    
    护盾有以下特点：
    - 可叠加，堆叠式吸收伤害
    - 上限为初始护盾值的300%
    - 有持续时间
    """
    name: str
    source_name: str  # 来源技能名
    owner: Character   # 护盾所属角色
    shield_hp: int     # 护盾当前HP
    max_shield_hp: int  # 护盾上限（初始值的300%）
    duration: int = 3  # 持续回合
    
    def absorb_damage(self, damage: int) -> int:
        """
        吸收伤害，返回实际吸收的伤害量
        护盾优先吸收伤害
        """
        if damage <= 0:
            return 0
        absorbed = min(self.shield_hp, damage)
        self.shield_hp -= absorbed
        return absorbed
    
    def is_expired(self) -> bool:
        return self.duration <= 0
    
    def tick(self) -> None:
        if self.duration > 0:
            self.duration -= 1
    
    def refresh(self, new_hp: int) -> None:
        """刷新护盾：叠加HP，但不超过上限"""
        self.shield_hp = min(self.shield_hp + new_hp, self.max_shield_hp)


class ShieldManager:
    """
    护盾管理器 - 管理角色身上的所有护盾
    
    护盾叠加规则：
    - 同一来源护盾：刷新持续时间，叠加HP（不超过上限）
    - 不同来源护盾：分别计算，最终吸收伤害时合并计算
    """
    
    def __init__(self, owner: Character):
        self.owner = owner
        self.shields: list[Shield] = []
    
    def add_shield(self, shield: Shield) -> None:
        """添加护盾"""
        self.shields.append(shield)
    
    def remove_shield(self, shield: Shield) -> bool:
        """移除护盾"""
        if shield in self.shields:
            self.shields.remove(shield)
            return True
        return False
    
    def get_total_shield_hp(self) -> int:
        """获取总护盾HP"""
        return sum(s.shield_hp for s in self.shields if s.shield_hp > 0)
    
    def absorb_damage(self, damage: int) -> tuple[int, int]:
        """
        吸收伤害，返回(实际吸收的伤害, 穿透到HP的伤害)
        按护盾添加顺序消耗护盾
        """
        total_absorbed = 0
        remaining_damage = damage
        
        for shield in self.shields[:]:
            if remaining_damage <= 0:
                break
            if shield.shield_hp > 0:
                absorbed = shield.absorb_damage(remaining_damage)
                total_absorbed += absorbed
                remaining_damage -= absorbed
                if shield.is_expired() or shield.shield_hp <= 0:
                    self.remove_shield(shield)
        
        return total_absorbed, remaining_damage
    
    def tick(self) -> None:
        """回合结束，护盾持续时间递减"""
        for shield in self.shields[:]:
            shield.tick()
            if shield.is_expired():
                self.shields.remove(shield)
    
    def __len__(self) -> int:
        return len(self.shields)


def apply_shield(
    target: Character,
    shield_hp: int,
    source_skill: str,
    cap_multiplier: float = 3.0,
    duration: int = 3,
) -> Shield:
    """
    对目标应用护盾
    
    Args:
        target: 目标角色
        shield_hp: 护盾HP
        source_skill: 来源技能名
        cap_multiplier: 上限倍率（默认300%）
        duration: 持续回合
    
    Returns:
        创建的Shield对象
    """
    if not hasattr(target, 'shield_manager') or target.shield_manager is None:
        target.shield_manager = ShieldManager(target)
    
    # 检查是否已有同名护盾
    existing = None
    for s in target.shield_manager.shields:
        if s.source_name == source_skill:
            existing = s
            break
    
    max_hp = int(shield_hp * cap_multiplier)
    
    if existing:
        # 刷新并叠加
        existing.refresh(shield_hp)
        existing.duration = duration
        return existing
    else:
        shield = Shield(
            name=f"{source_skill}-护盾",
            source_name=source_skill,
            owner=target,
            shield_hp=shield_hp,
            max_shield_hp=max_hp,
            duration=duration,
        )
        target.shield_manager.add_shield(shield)
        return shield


def calculate_skill_shield_hp(caster: Character) -> int:
    """
    计算战技/大招护盾值：14% ATK + 100
    """
    atk = caster.stat.total_atk()
    return int(atk * 0.14) + 100


def calculate_souldragon_shield_hp(caster: Character) -> int:
    """
    计算龙灵护盾值：7% ATK + 50
    """
    atk = caster.stat.total_atk()
    return int(atk * 0.07) + 50


# ============== 挚友(Bondmate)系统 ==============

@dataclass
class BondmateState:
    """挚友状态"""
    target: Optional[Character] = None
    enhanced_actions: int = 0  # 强化追击次数
    is_enhanced: bool = False


# ============== 龙灵(Souldragon) ==============

def create_souldragon(owner: Character) -> 'Souldragon':
    """创建龙灵"""
    souldragon = Souldragon(
        name="龙灵",
        owner=owner,
        level=owner.level,
        max_hp=1,  # 龙灵不吃伤害
        current_hp=1,
        atk=int(owner.stat.total_atk() * 0.4),  # 40% ATK
        def_value=owner.stat.total_def(),
        spd=165,  # 固定165 SPD
        basic_skill_name="龙灵反击",
        skill_multiplier=0.4,  # 40% ATK
        bondmate_atk_multiplier=0.4,  # 40% Bondmate ATK
        enhanced_actions=0,
    )
    return souldragon


class Souldragon(Summon):
    """
    龙灵 (Souldragon)
    
    继承自Summon，额外属性：
    - bondmate_atk_multiplier: 挚友ATK倍率
    - enhanced_actions: 强化追击剩余次数
    """
    
    def __init__(
        self,
        name: str,
        owner: 'Character',
        level: int,
        max_hp: int,
        current_hp: int,
        atk: int,
        def_value: int,
        spd: int,
        basic_skill_name: str,
        skill_multiplier: float,
        bondmate_atk_multiplier: float = 0.4,
        enhanced_actions: int = 0,
        **kwargs,
    ):
        super().__init__(
            name=name,
            owner=owner,
            level=level,
            max_hp=max_hp,
            current_hp=current_hp,
            atk=atk,
            def_value=def_value,
            spd=spd,
            basic_skill_name=basic_skill_name,
            skill_multiplier=skill_multiplier,
            **kwargs,
        )
        self.bondmate_atk_multiplier = bondmate_atk_multiplier
        self.enhanced_actions = enhanced_actions
        self.dispel_count = 1  # 驱散1个debuff
    
    def is_enhanced(self) -> bool:
        return self.enhanced_actions > 0
    
    def execute_action(self, battle_state) -> list:
        """
        龙灵行动：驱散debuff + 护盾 + 追击
        """
        from src.game.damage import calculate_damage, apply_damage
        
        results = []
        
        # 1. 驱散我方1个debuff
        for ally in battle_state.player_team + battle_state.enemy_team:
            if not ally.is_alive():
                continue
            # 只驱散debuff（负面效果）
            if hasattr(ally, 'effects'):
                debuffs = [e for e in ally.effects if not e.is_buff()]
                if debuffs and self.dispel_count > 0:
                    debuffs[0].turns_remaining = 0
                    self.dispel_count -= 1
                    results.append(f"{ally.name}被驱散1个debuff")
        
        # 2. 提供护盾（7% ATK + 50）
        for ally in battle_state.player_team:
            if not ally.is_alive():
                continue
            shield_hp = calculate_souldragon_shield_hp(self.owner)
            apply_shield(
                target=ally,
                shield_hp=shield_hp,
                source_skill="龙灵",
                cap_multiplier=3.0,
                duration=3,
            )
        
        # 3. 追击伤害
        enemies = [c for c in battle_state.enemy_team if c.is_alive()]
        if not enemies:
            return results
        
        # 获取挚友
        bondmate = None
        if hasattr(self.owner, 'bondmate_state') and self.owner.bondmate_state:
            bondmate = self.owner.bondmate_state.target
        
        # 计算追击次数：强化时额外2次（基础1次 + 额外2次）
        follow_up_count = 1 + self.enhanced_actions
        
        for _ in range(follow_up_count):
            for enemy in enemies:
                # 物理伤害：40% ATK（或强化时200%）
                phys_mult = self.skill_multiplier * (2.0 if self.is_enhanced() else 1.0)
                result = calculate_damage(
                    attacker=self.owner,
                    defender=enemy,
                    skill_multiplier=phys_mult,
                    damage_type=Element.PHYSICAL,
                    damage_source=DamageSource.FOLLOW_UP,
                    attacker_is_player=not self.owner.is_enemy,
                )
                apply_damage(self.owner, enemy, result)
                results.append((enemy, result, "龙灵物理追击"))
                
                # 挚友属性伤害（如果有挚友）
                if bondmate and bondmate.is_alive():
                    bondmate_mult = self.bondmate_atk_multiplier * (2.0 if self.is_enhanced() else 1.0)
                    bondmate_atk = bondmate.stat.total_atk()
                    extra_dmg = calculate_damage(
                        attacker=bondmate,
                        defender=enemy,
                        skill_multiplier=bondmate_mult,
                        damage_type=bondmate.element,
                        damage_source=DamageSource.FOLLOW_UP,
                        attacker_is_player=not bondmate.is_enemy,
                    )
                    apply_damage(bondmate, enemy, extra_dmg)
                    results.append((enemy, extra_dmg, "龙灵挚友追击"))
        
        # 消耗强化次数
        if self.enhanced_actions > 0:
            self.enhanced_actions -= 1
        
        return results


# ============== 丹恒·腾荒被动技能 ==============

def create_danheng_percival_passives() -> list[Passive]:
    """创建丹恒·腾荒的行迹/被动"""
    return [
        # A2: Watch Trails to Blaze - 额外强化次数
        Passive(
            name="威化飞龙印",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="souldragon_enhanced_actions",
            value=2,  # +2次强化追击
            duration=0,
            description="终结技后龙灵额外2次强化追击",
        ),
        # A4: By Oath, This Vessel Is I - 挚友减伤
        Passive(
            name="誓约之誓",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="bondmate_dmg_reduction",
            value=0.20,  # 20%减伤
            duration=0,
            description="挚友受到伤害降低20%",
        ),
        # A6: One Dream to Enfold All Wilds - 挚友增伤
        Passive(
            name="宏愿唯心",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="bondmate_dmg_increase",
            value=0.20,  # 敌人增伤20%
            duration=0,
            description="挚友在场时，敌人受到伤害增加20%",
        ),
        # A6: 速度
        Passive(
            name="速度+3",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="spd_increase",
            value=3,
            duration=0,
            description="速度+3",
        ),
        # A6: 防御
        Passive(
            name="防御+10%",
            trigger=SkillType.ABILITY_PASSIVE,
            effect_type="def_increase",
            value=0.10,
            duration=0,
            description="防御+10%",
        ),
    ]


# ============== 丹恒·腾荒技能 ==============

def create_danheng_basic_skill() -> Skill:
    """丹恒·腾荒普攻：Aegis Vitae - 50% ATK物理伤害"""
    return Skill(
        name="Aegis Vitae",
        type=SkillType.BASIC,
        multiplier=0.50,
        damage_type=Element.PHYSICAL,
        description="对指定敌方单体造成50%攻击力的物理属性伤害",
        energy_gain=20.0,
        battle_points_gain=1,
        break_power=30,
    )


def create_danheng_special_skill() -> Skill:
    """丹恒·腾荒战技：Terra Omnibus
    - 指定挚友，全队护盾
    - 护盾值：14% ATK + 100，持续3回合
    - 可叠加，上限300%
    """
    return Skill(
        name="Terra Omnibus",
        type=SkillType.SPECIAL,
        cost=1,
        multiplier=0.0,
        damage_type=Element.PHYSICAL,
        description="指定一名我方角色为【挚友】，为全体提供护盾（14% ATK+100）持续3回合，护盾可叠加上限300%",
        energy_gain=30.0,
        break_power=0,
        is_support_skill=True,
        support_modifier_name="Terra Omnibus-护盾",
    )


def create_danheng_ult_skill() -> Skill:
    """丹恒·腾荒终结技：A Dragon's Zenith Knows No Rue
    - 对所有敌人造成150% ATK物理伤害
    - 全队护盾
    - 龙灵强化：额外2次追击
    """
    return Skill(
        name="A Dragon's Zenith Knows No Rue",
        type=SkillType.ULT,
        multiplier=1.50,
        damage_type=Element.PHYSICAL,
        description="对所有敌人造成150% ATK物理伤害，为全体提供护盾，龙灵进入强化状态额外2次追击",
        energy_gain=5.0,
        break_power=60,
        target_count=-1,  # 全体
        aoe_multiplier=1.0,
        is_support_skill=True,
        support_modifier_name="龙灵强化",
    )


def create_all_danheng_percival_skills() -> list[Skill]:
    """创建丹恒·腾荒所有技能"""
    return [
        create_danheng_basic_skill(),
        create_danheng_special_skill(),
        create_danheng_ult_skill(),
    ]


# ============== 技能执行效果 ==============

def execute_danheng_special_skill(
    caster: Character,
    targets: list[Character],
    bondmate: Character,
    battle_state=None,
) -> list:
    """
    执行丹恒·腾荒战技效果
    
    1. 指定挚友
    2. 为全队提供护盾
    """
    results = []
    
    # 1. 设置挚友
    if not hasattr(caster, 'bondmate_state'):
        caster.bondmate_state = BondmateState()
    caster.bondmate_state.target = bondmate
    
    # 2. 为全队提供护盾
    shield_hp = calculate_skill_shield_hp(caster)
    for target in battle_state.player_team if battle_state else targets:
        if not target.is_alive():
            continue
        shield = apply_shield(
            target=target,
            shield_hp=shield_hp,
            source_skill="Terra Omnibus",
            cap_multiplier=3.0,
            duration=3,
        )
        results.append(f"{target.name}获得护盾 {shield.shield_hp}")
    
    # 3. 召唤龙灵（如果还没有）
    if not hasattr(caster, 'souldragon') or caster.souldragon is None:
        caster.souldragon = create_souldragon(caster)
        results.append(f"龙灵被召唤")
    
    return results


def execute_danheng_ult_skill(
    caster: Character,
    targets: list[Character],
    battle_state=None,
) -> list:
    """
    执行丹恒·腾荒终结技效果
    
    1. 对所有敌人造成150% ATK物理伤害
    2. 全队护盾
    3. 龙灵强化（额外2次追击）
    """
    from src.game.damage import calculate_damage, apply_damage
    
    results = []
    
    # 1. 对所有敌人造成AOE伤害
    for target in targets:
        if not target.is_alive():
            continue
        result = calculate_damage(
            attacker=caster,
            defender=target,
            skill_multiplier=1.50,
            damage_type=Element.PHYSICAL,
            damage_source=DamageSource.ULT,
            attacker_is_player=not caster.is_enemy,
        )
        apply_damage(caster, target, result)
        results.append((target, result, "终结技"))
    
    # 2. 全队护盾
    shield_hp = calculate_skill_shield_hp(caster)
    for target in battle_state.player_team if battle_state else []:
        if not target.is_alive():
            continue
        shield = apply_shield(
            target=target,
            shield_hp=shield_hp,
            source_skill="A Dragon's Zenith Knows No Rue",
            cap_multiplier=3.0,
            duration=3,
        )
        results.append(f"{target.name}获得护盾 {shield.shield_hp}")
    
    # 3. 龙灵强化
    if hasattr(caster, 'souldragon') and caster.souldragon is not None:
        # 基础2次强化 + A2额外2次 = 4次
        caster.souldragon.enhanced_actions += 2
        # A2: 龙灵行动提前100%
        caster.souldragon.action_value -= 10000  # 提前行动
        results.append(f"龙灵进入强化状态，额外追击2次")
    else:
        # 如果龙灵不存在，召唤它
        caster.souldragon = create_souldragon(caster)
        caster.souldragon.enhanced_actions = 2
        results.append(f"龙灵被召唤并进入强化状态")
    
    return results


def execute_souldragon_action(souldragon: Souldragon, battle_state) -> list:
    """执行龙灵行动"""
    return souldragon.execute_action(battle_state)


# ============== Sublimity (Trace) 效果 ==============

def apply_souldragon_sublimity_shield(caster: Character, battle_state=None) -> None:
    """
    Sublimity效果：龙灵行动时，为护盾最低的我方目标额外提供护盾
    护盾值：5% ATK + 100
    """
    if battle_state is None:
        return
    
    # 找到护盾最低的我方角色
    min_shield_char = None
    min_shield_hp = float('inf')
    
    for ally in battle_state.player_team:
        if not ally.is_alive():
            continue
        shield_hp = 0
        if hasattr(ally, 'shield_manager') and ally.shield_manager:
            shield_hp = ally.shield_manager.get_total_shield_hp()
        if shield_hp < min_shield_hp:
            min_shield_hp = shield_hp
            min_shield_char = ally
    
    if min_shield_char:
        shield_hp = int(caster.stat.total_atk() * 0.05) + 100
        apply_shield(
            target=min_shield_char,
            shield_hp=shield_hp,
            source_skill="Sublimity-龙灵",
            cap_multiplier=3.0,
            duration=3,
        )
