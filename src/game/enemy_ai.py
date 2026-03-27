"""
敌人AI系统

设计目标：
1. 多种AI策略（激进/保守/均衡/智能）
2. 目标选择逻辑（最低HP/最高威胁/随机）
3. 技能选择逻辑（能量/血量/增益状态）
4. 元素弱点瞄准
5. 增益效果管理
6. 协同攻击（多敌人配合）
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum
from abc import ABC, abstractmethod
import random

from src.game.models import Character, Element, Skill, SkillType
from src.game.damage import calculate_damage


class AIPersonality(Enum):
    """AI性格/策略"""
    AGGRESSIVE = "aggressive"      # 激进：优先攻击血量最低目标
    CONSERVATIVE = "conservative"  # 保守：优先攻击威胁最大目标
    BALANCED = "balanced"          # 均衡：综合考虑多种因素
    INTELLIGENT = "intelligent"    # 智能：学习玩家行为模式


class TargetSelection(Enum):
    """目标选择策略"""
    LOWEST_HP = "lowest_hp"        # 血量最低
    HIGHEST_THREAT = "highest_threat"  # 威胁最高（高伤害/高速度）
    WEAKEST = "weakest"            # 最弱点（属性被克）
    RANDOM = "random"             # 随机
    ALL = "all"                   # 全体（用于AOE）


@dataclass
class AIConsideration:
    """AI决策考量"""
    name: str
    weight: float  # 权重 0-1
    evaluate: Callable[[Character, list[Character], Character], float]  # 评估函数


@dataclass
class EnemyAIConfig:
    """敌人AI配置"""
    personality: AIPersonality = AIPersonality.BALANCED
    target_strategy: TargetSelection = TargetSelection.LOWEST_HP
    ult_threshold: float = 0.8  # 能量达到80%就考虑放ULT
    aoe_threshold: int = 2  # 敌人数量>=2时考虑AOE
    dot_preference: float = 0.3  # DOT技能偏好概率
    heal_threshold: float = 0.5  # 血量低于50%时考虑治疗
    buff_preference: float = 0.4  # 增益技能偏好概率


class EnemyAI:
    """
    敌人AI基类
    
    负责：
    1. 目标选择
    2. 技能选择
    3. 时机判断
    """
    
    def __init__(self, config: EnemyAIConfig = None):
        self.config = config or EnemyAIConfig()
        self.considerations: list[AIConsideration] = []
        self._setup_considerations()
    
    def _setup_considerations(self):
        """设置决策考量"""
        # 血量考量
        self.considerations.append(AIConsideration(
            name="hp_ratio",
            weight=0.3,
            evaluate=lambda self, actor, targets, current: 
                1.0 - (current.stat.total_max_hp() / max(1, current.current_hp))
        ))
        
        # 威胁度考量
        self.considerations.append(AIConsideration(
            name="threat_level",
            weight=0.25,
            evaluate=lambda self, actor, targets, current:
                (current.stat.total_atk() / 1000) + (current.stat.base_spd / 100)
        ))
        
        # 元素弱点考量
        self.considerations.append(AIConsideration(
            name="element_advantage",
            weight=0.2,
            evaluate=lambda self, actor, targets, current:
                1.0 if actor.element.does_superimpose(current.element) else 0.5
        ))
        
        # 增益状态考量
        self.considerations.append(AIConsideration(
            name="buff_status",
            weight=0.15,
            evaluate=lambda self, actor, targets, current:
                len(current.effects) / 5.0  # 有buff的目标优先
        ))
        
        # 速度考量
        self.considerations.append(AIConsideration(
            name="speed",
            weight=0.1,
            evaluate=lambda self, actor, targets, current:
                current.stat.base_spd / 150.0
        ))
    
    def select_target(self, actor: Character, opponents: list[Character]) -> Optional[Character]:
        """
        选择目标
        
        Args:
            actor: 行动的角色（敌人）
            opponents: 可选择的敌方目标列表
        
        Returns:
            选择的目标，如果无法选择则返回None
        """
        if not opponents:
            return None
        
        # 过滤存活目标
        alive = [t for t in opponents if t.is_alive()]
        if not alive:
            return None
        
        # 根据策略选择
        if self.config.target_strategy == TargetSelection.LOWEST_HP:
            return min(alive, key=lambda t: t.current_hp)
        
        elif self.config.target_strategy == TargetSelection.HIGHEST_THREAT:
            return max(alive, key=lambda t: self._calculate_threat(t))
        
        elif self.config.target_strategy == TargetSelection.WEAKEST:
            return min(alive, key=lambda t: self._calculate_weakness(actor, t))
        
        elif self.config.target_strategy == TargetSelection.RANDOM:
            return random.choice(alive)
        
        else:  # INTELLIGENT
            return self._intelligent_select(actor, alive)
    
    def _intelligent_select(self, actor: Character, targets: list[Character]) -> Character:
        """智能选择：综合评分"""
        scores = []
        for t in targets:
            score = sum(
                c.weight * c.evaluate(self, actor, targets, t)
                for c in self.considerations
            )
            scores.append((t, score))
        
        return max(scores, key=lambda x: x[1])[0]
    
    def _calculate_threat(self, target: Character) -> float:
        """计算目标威胁度"""
        return (
            target.stat.total_atk() * 0.3 +
            target.stat.base_spd * 0.2 +
            len([e for e in target.effects if e.is_buff]) * 10
        )
    
    def _calculate_weakness(self, actor: Character, target: Character) -> float:
        """计算目标弱点程度"""
        base_score = target.current_hp
        
        # 属性被克
        if actor.element.does_superimpose(target.element):
            base_score *= 1.5
        
        # 有debuff的目标更容易被攻击
        if len([e for e in target.effects if e.is_debuff]) > 0:
            base_score *= 1.2
        
        return base_score
    
    def select_skill(
        self, 
        actor: Character, 
        available_skills: list[Skill],
        opponents: list[Character]
    ) -> tuple[Optional[Skill], list[Character]]:
        """
        选择技能和目标
        
        Args:
            actor: 行动的角色
            available_skills: 可用技能列表
            opponents: 敌方目标列表
        
        Returns:
            (选择的技能, 目标列表)
        """
        if not available_skills or not opponents:
            return None, []
        
        # 过滤可用技能（能量足够）
        usable = [s for s in available_skills if self._can_use_skill(actor, s)]
        if not usable:
            # 使用普攻
            basic = next((s for s in available_skills if s.type == SkillType.BASIC), None)
            return basic, [self.select_target(actor, opponents)]
        
        # 分类技能
        aoe_skills = [s for s in usable if self._is_aoe_skill(s)]
        single_skills = [s for s in usable if not self._is_aoe_skill(s)]
        ult_skills = [s for s in usable if s.type == SkillType.ULT]
        
        # 决策逻辑
        alive_opponents = [t for t in opponents if t.is_alive()]
        aoe_count = len(alive_opponents)
        
        # 1. ULT优先（能量足够时）
        for ult in ult_skills:
            if actor.energy >= actor.energy_limit * self.config.ult_threshold:
                if self.config.personality == AIPersonality.AGGRESSIVE:
                    # 激进：直接放ULT
                    return ult, alive_opponents if self._is_aoe_skill(ult) else [self.select_target(actor, alive_opponents)]
        
        # 2. AOE优先（敌人数量足够时）
        if aoe_count >= self.config.aoe_threshold:
            for aoe in aoe_skills:
                if random.random() < 0.7:  # 70%概率使用AOE
                    return aoe, alive_opponents
        
        # 3. 智能选择
        if self.config.personality == AIPersonality.AGGRESSIVE:
            # 激进：优先高伤害技能
            best = max(single_skills or usable, key=lambda s: s.multiplier)
            return best, [self.select_target(actor, alive_opponents)]
        
        elif self.config.personality == AIPersonality.CONSERVATIVE:
            # 保守：优先控制/增益技能
            control = next((s for s in usable if self._is_control_skill(s)), None)
            if control:
                return control, [self.select_target(actor, alive_opponents)]
            # 使用低消耗技能
            best = min(single_skills or usable, key=lambda s: getattr(s, 'cost', 0))
            return best, [self.select_target(actor, alive_opponents)]
        
        elif self.config.personality == AIPersonality.BALANCED:
            # 均衡：随机选择但偏向AOE
            if random.random() < 0.4 and single_skills:
                skill = random.choice(single_skills)
            else:
                skill = random.choice(usable)
            return skill, [self.select_target(actor, alive_opponents)]
        
        else:  # INTELLIGENT
            # 智能：根据状态选择
            return self._intelligent_skill_select(actor, usable, alive_opponents)
    
    def _intelligent_skill_select(
        self, 
        actor: Character, 
        skills: list[Skill],
        opponents: list[Character]
    ) -> tuple[Skill, list[Character]]:
        """智能技能选择"""
        # 根据自身状态选择
        hp_ratio = actor.current_hp / actor.stat.total_max_hp()
        
        # 低血量时优先治疗/护盾
        if hp_ratio < self.config.heal_threshold:
            heal_skill = next((s for s in skills if self._is_heal_skill(s)), None)
            if heal_skill:
                return heal_skill, [actor]
        
        # 增益状态不足时使用增益技能
        if len(actor.effects) < 2:
            buff_skill = next((s for s in skills if self._is_buff_skill(s)), None)
            if buff_skill and random.random() < self.config.buff_preference:
                return buff_skill, [actor]
        
        # DOT偏好
        if random.random() < self.config.dot_preference:
            dot_skill = next((s for s in skills if self._is_dot_skill(s)), None)
            if dot_skill:
                target = self.select_target(actor, opponents)
                return dot_skill, [target]
        
        # 默认选择高伤害技能
        best = max(skills, key=lambda s: s.multiplier)
        return best, [self.select_target(actor, opponents)]
    
    def _can_use_skill(self, actor: Character, skill: Skill) -> bool:
        """检查技能是否可用"""
        if skill.type == SkillType.ULT:
            return actor.energy >= actor.energy_limit
        elif skill.type == SkillType.SPECIAL:
            return actor.battle_points >= skill.cost
        return True
    
    def _is_aoe_skill(self, skill: Skill) -> bool:
        """是否AOE技能"""
        return (
            getattr(skill, 'target_count', 0) == -1 or
            getattr(skill, 'is_aoe', False) or
            '全体' in getattr(skill, 'description', '')
        )
    
    def _is_control_skill(self, skill: Skill) -> bool:
        """是否控制技能"""
        desc = getattr(skill, 'description', '').lower()
        return any(kw in desc for kw in ['冻结', '禁锢', '减速', '眩晕', '石化'])
    
    def _is_heal_skill(self, skill: Skill) -> bool:
        """是否治疗技能"""
        desc = getattr(skill, 'description', '').lower()
        return '治疗' in desc or '恢复' in desc or '回复' in desc
    
    def _is_buff_skill(self, skill: Skill) -> bool:
        """是否增益技能"""
        desc = getattr(skill, 'description', '').lower()
        return any(kw in desc for kw in ['攻击力', '防御力', '速度', '暴击', '伤害提高'])
    
    def _is_dot_skill(self, skill: Skill) -> bool:
        """是否DOT技能"""
        desc = getattr(skill, 'description', '').lower()
        return any(kw in desc for kw in ['灼烧', '触电', '风化', '裂伤', '持续伤害'])


class TeamAI(EnemyAI):
    """
    团队AI - 多敌人协同
    
    特点：
    1. 敌人之间可以协同
    2. 分配不同角色定位（坦克/输出/辅助）
    3. 集火目标
    """
    
    def __init__(self, config: EnemyAIConfig = None):
        super().__init__(config)
        self.team_focus_target: Optional[Character] = None
        self.role_assignments: dict[int, str] = {}  # {character_id: role}
    
    def set_focus_target(self, target: Character):
        """设置集火目标"""
        self.team_focus_target = target
    
    def clear_focus_target(self):
        """清除集火目标"""
        self.team_focus_target = None
    
    def assign_roles(self, team: list[Character]):
        """为队伍分配角色"""
        # 按速度排序
        sorted_team = sorted(team, key=lambda c: c.stat.base_spd, reverse=True)
        
        # 第一个是辅助（拉条/治疗）
        # 最后一个是输出（高伤害）
        # 中间是控制
        
        for i, char in enumerate(sorted_team):
            if i == 0:
                self.role_assignments[id(char)] = "support"
            elif i == len(sorted_team) - 1:
                self.role_assignments[id(char)] = "dps"
            else:
                self.role_assignments[id(char)] = "control"
    
    def select_target_for_role(
        self, 
        actor: Character, 
        opponents: list[Character]
    ) -> list[Character]:
        """根据角色定位选择目标"""
        role = self.role_assignments.get(id(actor), "dps")
        
        if role == "support":
            # 辅助：治疗/增益自己或攻击
            return [actor]
        
        elif role == "dps":
            # 输出：集火目标或血量最低
            if self.team_focus_target and self.team_focus_target.is_alive():
                return [self.team_focus_target]
            return [self.select_target(actor, opponents)]
        
        else:  # control
            # 控制：攻击有增益的目标
            targets_with_buffs = [t for t in opponents if len(t.effects) > 0]
            if targets_with_buffs:
                return [random.choice(targets_with_buffs)]
            return [self.select_target(actor, opponents)]


class BossAI(EnemyAI):
    """
    BOSS AI - 更复杂的决策
    
    特点：
    1. 多阶段战斗
    2. 特殊机制
    3. 召唤小怪
    4. 狂暴状态
    """
    
    def __init__(self, config: EnemyAIConfig = None):
        super().__init__(config)
        self.phase = 1
        self.max_phase = 3
        self.enrage_threshold = 0.2  # 血量低于20%进入狂暴
        self.special_cooldown = 0
        self.uses_special = False
    
    def update_phase(self, current_hp: float, max_hp: float):
        """更新战斗阶段"""
        hp_ratio = current_hp / max_hp
        
        if hp_ratio <= self.enrage_threshold:
            self.phase = self.max_phase  # 狂暴
        elif hp_ratio <= 0.5:
            self.phase = 2
        else:
            self.phase = 1
    
    def select_skill_for_phase(
        self,
        actor: Character,
        skills: list[Skill],
        opponents: list[Character]
    ) -> tuple[Optional[Skill], list[Character]]:
        """根据阶段选择技能"""
        # 第一阶段：普通攻击为主
        if self.phase == 1:
            basic = next((s for s in skills if s.type == SkillType.BASIC), None)
            return basic, [self.select_target(actor, opponents)]
        
        # 第二阶段：开始使用技能
        elif self.phase == 2:
            # 使用一些特殊技能
            special_skills = [s for s in skills if s.type in [SkillType.SPECIAL, SkillType.ULT]]
            if special_skills and random.random() < 0.5:
                skill = random.choice(special_skills)
                targets = opponents if self._is_aoe_skill(skill) else [self.select_target(actor, opponents)]
                return skill, targets
            
            basic = next((s for s in skills if s.type == SkillType.BASIC), None)
            return basic, [self.select_target(actor, opponents)]
        
        # 第三阶段：狂暴 - 全力攻击
        else:
            # 优先ULT
            ult = next((s for s in skills if s.type == SkillType.ULT), None)
            if ult:
                return ult, opponents  # 全体攻击
            
            special = next((s for s in skills if s.type == SkillType.SPECIAL), None)
            if special:
                return special, [self.select_target(actor, opponents)]
            
            basic = next((s for s in skills if s.type == SkillType.BASIC), None)
            return basic, [self.select_target(actor, opponents)]


class EliteAI(EnemyAI):
    """
    精英怪AI - 中等复杂度的敌人
    
    特点：
    1. 有护盾/治疗机制
    2. 会使用控制技能
    3. 有增益状态管理
    """
    
    def __init__(self, config: EnemyAIConfig = None):
        super().__init__(config)
        self.shield_threshold = 0.3  # 护盾阈值
        self.buff_duration_threshold = 2  # buff持续时间阈值
    
    def should_use_defensive_skill(self, actor: Character) -> bool:
        """是否使用防御技能"""
        hp_ratio = actor.current_hp / actor.stat.total_max_hp()
        
        # 血量低时使用
        if hp_ratio < self.shield_threshold:
            return True
        
        # 没有护盾时使用
        has_shield = any('护盾' in str(e) for e in actor.effects)
        if not has_shield and hp_ratio < 0.5:
            return True
        
        return False
    
    def should_remove_debuff(self, actor: Character) -> bool:
        """是否驱散debuff"""
        debuffs = [e for e in actor.effects if e.is_debuff]
        return len(debuffs) >= 2


def create_enemy_ai(personality: str = "balanced") -> EnemyAI:
    """工厂函数：创建敌人AI"""
    config = EnemyAIConfig(
        personality=AIPersonality(personality),
        target_strategy=TargetSelection.LOWEST_HP,
    )
    return EnemyAI(config)


def create_team_ai(personality: str = "balanced") -> TeamAI:
    """工厂函数：创建团队AI"""
    config = EnemyAIConfig(
        personality=AIPersonality(personality),
    )
    return TeamAI(config)


def create_boss_ai(max_phase: int = 3) -> BossAI:
    """工厂函数：创建BOSS AI"""
    config = EnemyAIConfig(
        personality=AIPersonality.AGGRESSIVE,
        ult_threshold=0.5,  # BOSS更早放ULT
    )
    ai = BossAI(config)
    ai.max_phase = max_phase
    return ai
