"""
Modifier系统 - 参考DOTA 2的日志系统

Modifier是附着在角色身上的效果，可以修改角色的属性或行为。
所有技能效果最终都通过Modifier来实现。

示例：
- 攻击力加成 Modifier: +100 ATK for 3 turns
- 拉条 Modifier: Advance 100% AV
- 速度加成 Modifier: +30% SPD for 2 turns
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum, auto


class ModifierStacking(Enum):
    """Modifier叠加行为"""
    REFRESH = auto()      # 刷新持续时间（默认）
    ACCUMULATE = auto()  # 叠加效果（如风化）
    IGNORE = auto()       # 忽略新modifier


class ModifierType(Enum):
    """Modifier类型"""
    BUFF = auto()        # 增益
    DEBUFF = auto()      # 减益
    NEUTRAL = auto()     # 中性


@dataclass
class Modifier:
    """
    Modifier - 角色身上的效果
    
    每个modifier描述了对角色的一个效果，可以是：
    - 属性修改（ATK, DEF, SPD等）
    - 状态效果（拉条、推条、冻结等）
    - 特殊效果（伤害反射、吸血等）
    
    特性：
    - 有持续时间（turns_remaining）
    - 可以叠加（stacking behavior）
    - 可以影响战斗结算
    """
    name: str
    source_skill: str = ""
    duration: int = 0  # 持续回合数，0表示无限
    modifier_type: ModifierType = ModifierType.BUFF
    
    # 属性修改
    atk_flat: int = 0
    def_flat: int = 0
    spd_flat: float = 0.0
    atk_pct: float = 0.0      # ATK百分比加成
    def_pct: float = 0.0
    spd_pct: float = 0.0      # SPD百分比加成
    hp_pct: float = 0.0
    
    # 战斗属性
    crit_rate_pct: float = 0.0
    crit_dmg_pct: float = 0.0
    dmg_pct: float = 0.0
    break_eff_pct: float = 0.0  # 击破效率
    
    # 元素属性加成
    physical_dmg_pct: float = 0.0
    fire_dmg_pct: float = 0.0
    ice_dmg_pct: float = 0.0
    thunder_dmg_pct: float = 0.0
    wind_dmg_pct: float = 0.0
    quantum_dmg_pct: float = 0.0
    imaginary_dmg_pct: float = 0.0
    
    # 状态效果
    action_value_change: float = 0.0  # 行动值变化（拉条/退条）
    pull_forward_pct: float = 0.0      # 拉条百分比
    delay_pct: float = 0.0            # 退条百分比
    freeze: bool = False              # 冻结
    silence: bool = False             # 沉默（无法使用技能）
    stun: bool = False               # 眩晕
    taunt: bool = False              # 嘲讽
    
    # 特殊效果
    heal_on_hit_pct: float = 0.0   # 受到攻击时回复HP百分比
    damage_reflect_pct: float = 0.0  # 伤害反射
    vuln_pct: float = 0.0           # 易伤百分比
    
    # 叠加行为
    stacking: ModifierStacking = ModifierStacking.REFRESH
    
    def on_tick(self) -> dict:
        """
        每回合触发时返回效果字典
        用于DOT伤害等周期性效果
        """
        return {}
    
    def on_apply(self, target: Character) -> None:
        """
        Modifier应用时触发
        """
        pass
    
    def on_remove(self, target: Character) -> None:
        """
        Modifier移除时触发
        """
        pass
    
    def is_expired(self) -> bool:
        """是否已过期"""
        return self.duration <= 0
    
    def tick(self) -> bool:
        """
        每回合减少持续时间
        返回True表示modifier应该被移除
        """
        if self.duration > 0:
            self.duration -= 1
        return self.duration <= 0
    
    def refresh(self) -> None:
        """刷新持续时间"""
        self.duration = max(self.duration, 0)  # 保持当前最大值
    
    def accumulate(self, other: Modifier) -> None:
        """
        叠加到当前modifier
        用于ACCUMULATE类型的modifier
        """
        self.atk_flat += other.atk_flat
        self.def_flat += other.def_flat
        self.atk_pct += other.atk_pct
        # 其他属性类似...
    
    def get_icon_color(self) -> tuple:
        """获取图标颜色"""
        if self.modifier_type == ModifierType.BUFF:
            return (100, 200, 100)  # 绿色
        elif self.modifier_type == ModifierType.DEBUFF:
            return (200, 100, 100)  # 红色
        else:
            return (150, 150, 150)  # 灰色
    
    def __repr__(self) -> str:
        return f"Modifier({self.name}, dur={self.duration})"


class ModifierManager:
    """
    Modifier管理器 - 管理角色身上的所有Modifier
    
    职责：
    - 添加/移除modifier
    - 处理叠加行为
    - 计算最终属性加成
    - 触发modifier事件
    """
    
    def __init__(self, owner: Character):
        self.owner = owner
        self.modifiers: list[Modifier] = []
    
    def add_modifier(self, modifier: Modifier) -> None:
        """
        添加modifier到角色
        
        处理叠加行为：
        - REFRESH: 如果已存在同名modifier，刷新持续时间
        - ACCUMULATE: 叠加效果（如风化层数）
        - IGNORE: 如果已存在，忽略新的
        """
        # 检查是否已存在同名modifier
        existing = self._find_modifier(modifier.name)
        
        if existing:
            if modifier.stacking == ModifierStacking.REFRESH:
                existing.refresh()
            elif modifier.stacking == ModifierStacking.ACCUMULATE:
                existing.accumulate(modifier)
            # IGNORE: 不做任何处理
        else:
            modifier.on_apply(self.owner)
            self.modifiers.append(modifier)
    
    def remove_modifier(self, name: str) -> bool:
        """移除指定名称的modifier"""
        for mod in self.modifiers:
            if mod.name == name:
                mod.on_remove(self.owner)
                self.modifiers.remove(mod)
                return True
        return False
    
    def _find_modifier(self, name: str) -> Optional[Modifier]:
        """查找同名modifier"""
        for mod in self.modifiers:
            if mod.name == name:
                return mod
        return None
    
    def tick_modifiers(self) -> list:
        """
        每回合触发所有modifier
        返回过期被移除的modifier列表
        """
        removed = []
        for mod in self.modifiers[:]:  # 复制列表避免迭代时修改
            if mod.tick():
                mod.on_remove(self.owner)
                removed.append(mod)
                self.modifiers.remove(mod)
        return removed
    
    def get_total_stats(self) -> dict:
        """
        计算所有modifier带来的总属性加成
        """
        stats = {
            'atk_flat': 0,
            'def_flat': 0,
            'spd_flat': 0.0,
            'atk_pct': 0.0,
            'def_pct': 0.0,
            'spd_pct': 0.0,
            'hp_pct': 0.0,
            'crit_rate_pct': 0.0,
            'crit_dmg_pct': 0.0,
            'dmg_pct': 0.0,
            'break_eff_pct': 0.0,
            'physical_dmg_pct': 0.0,
            'fire_dmg_pct': 0.0,
            'ice_dmg_pct': 0.0,
            'thunder_dmg_pct': 0.0,
            'wind_dmg_pct': 0.0,
            'quantum_dmg_pct': 0.0,
            'imaginary_dmg_pct': 0.0,
        }
        
        for mod in self.modifiers:
            stats['atk_flat'] += mod.atk_flat
            stats['def_flat'] += mod.def_flat
            stats['spd_flat'] += mod.spd_flat
            stats['atk_pct'] += mod.atk_pct
            stats['def_pct'] += mod.def_pct
            stats['spd_pct'] += mod.spd_pct
            stats['hp_pct'] += mod.hp_pct
            stats['crit_rate_pct'] += mod.crit_rate_pct
            stats['crit_dmg_pct'] += mod.crit_dmg_pct
            stats['dmg_pct'] += mod.dmg_pct
            stats['break_eff_pct'] += mod.break_eff_pct
            stats['physical_dmg_pct'] += mod.physical_dmg_pct
            stats['fire_dmg_pct'] += mod.fire_dmg_pct
            stats['ice_dmg_pct'] += mod.ice_dmg_pct
            stats['thunder_dmg_pct'] += mod.thunder_dmg_pct
            stats['wind_dmg_pct'] += mod.wind_dmg_pct
            stats['quantum_dmg_pct'] += mod.quantum_dmg_pct
            stats['imaginary_dmg_pct'] += mod.imaginary_dmg_pct
        
        return stats
    
    def get_action_value_change(self) -> float:
        """获取行动值变化（拉条/退条）"""
        total = 0.0
        for mod in self.modifiers:
            total += mod.pull_forward_pct * 100  # 拉条百分比转AV
            total -= mod.delay_pct * 100       # 退条百分比转AV
        return total
    
    def get_status_effects(self) -> dict:
        """获取状态效果（冻结、沉默等）"""
        effects = {
            'freeze': False,
            'silence': False,
            'stun': False,
            'taunt': False,
        }
        for mod in self.modifiers:
            if mod.freeze:
                effects['freeze'] = True
            if mod.silence:
                effects['silence'] = True
            if mod.stun:
                effects['stun'] = True
            if mod.taunt:
                effects['taunt'] = True
        return effects
    
    def has_modifier(self, name: str) -> bool:
        """检查是否有指定名称的modifier"""
        return self._find_modifier(name) is not None
    
    def get_modifiers_by_type(self, mtype: ModifierType) -> list[Modifier]:
        """获取指定类型的所有modifier"""
        return [m for m in self.modifiers if m.modifier_type == mtype]
    
    def clear_all(self) -> None:
        """清除所有modifier"""
        for mod in self.modifiers:
            mod.on_remove(self.owner)
        self.modifiers.clear()
    
    def __len__(self) -> int:
        return len(self.modifiers)
    
    def __iter__(self):
        return iter(self.modifiers)
