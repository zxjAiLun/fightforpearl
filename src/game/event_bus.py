"""战斗事件系统 - ROS2风格发布-订阅架构"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional
from collections import defaultdict


class EventType(Enum):
    """战斗事件类型"""
    # 技能相关
    SKILL_EXECUTED = auto()      # 技能执行（任意技能）
    BASIC_EXECUTED = auto()      # 普攻执行
    SPECIAL_EXECUTED = auto()    # 战技执行
    ULT_EXECUTED = auto()       # 大招执行
    
    # 伤害相关
    DAMAGE_DEALT = auto()        # 造成伤害
    CRIT_OCCURRED = auto()      # 暴击发生
    KILL_OCCURRED = auto()      # 击杀发生
    
    # HP相关
    TARGET_HP_BELOW = auto()     # 目标HP低于阈值
    TARGET_HP_ABOVE = auto()     # 目标HP高于阈值
    TARGET_HP_BELOW_50 = auto()  # 目标HP低于50%
    TARGET_HP_BELOW_80 = auto()  # 目标HP低于80%
    TARGET_WEAKENED = auto()      # 目标处于弱化状态
    
    # 自身状态相关
    CASTER_HP_BELOW = auto()     # 自身HP低于阈值
    CASTER_HP_BELOW_50 = auto()  # 自身HP低于50%
    
    # 战斗流程相关
    TURN_START = auto()         # 回合开始
    TURN_END = auto()           # 回合结束
    ACTION_START = auto()       # 行动开始
    ACTION_END = auto()         # 行动结束
    
    # 击破相关
    BREAK_TRIGGERED = auto()    # 击破触发
    DOT_TICK = auto()           # DOT伤害结算
    
    # 特殊
    AFTER_BASIC = auto()        # 普攻之后（无条件）
    AFTER_SPECIAL = auto()       # 战技之后（无条件）
    AFTER_ULT = auto()          # 大招之后（无条件）
    RANDOM_CHECK = auto()       # 随机检查（用于纯概率触发）


@dataclass
class BattleEvent:
    """
    战斗事件
    
    代表战斗过程中发生的任何事件，用于事件池的发布-订阅。
    """
    event_type: EventType
    caster: 'Character'
    target: 'Character'
    turn: int = 0
    
    # 额外数据
    skill_name: str = ""
    skill_type: 'SkillType' = None
    damage: int = 0
    is_crit: bool = False
    hp_threshold: float = 0.0  # 用于HP相关事件
    extra_data: dict = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"BattleEvent({self.event_type.name}, {self.caster.name} -> {self.target.name})"


@dataclass
class EventSubscription:
    """事件订阅器"""
    trigger: 'FollowUpTrigger'
    event_types: list[EventType]
    condition_checker: Optional[Callable] = None  # 额外的条件检查函数


class EventBus:
    """
    事件总线 - 发布-订阅模式
    
    所有战斗事件都通过这个事件总线进行分发。
    触发器订阅特定事件，当事件发生时自动通知。
    
    使用方式：
    1. 创建EventBus
    2. 触发器通过subscribe()订阅事件
    3. 战斗引擎通过publish()发布事件
    4. EventBus自动分发事件给订阅者
    """
    
    def __init__(self):
        self.events: list[BattleEvent] = []  # 事件历史
        self._subscriptions: dict[EventType, list[EventSubscription]] = defaultdict(list)
        self._triggered_this_turn: set = set()  # 本回合已触发过的触发器ID
    
    def subscribe(
        self,
        trigger: 'FollowUpTrigger',
        event_types: list[EventType],
        condition_checker: Optional[Callable] = None,
    ) -> None:
        """
        订阅事件
        
        Args:
            trigger: 触发器对象
            event_types: 订阅的事件类型列表
            condition_checker: 可选的额外条件检查函数
        """
        subscription = EventSubscription(
            trigger=trigger,
            event_types=event_types,
            condition_checker=condition_checker,
        )
        for event_type in event_types:
            self._subscriptions[event_type].append(subscription)
    
    def unsubscribe(self, trigger: 'FollowUpTrigger') -> None:
        """取消订阅"""
        for event_type, subs in self._subscriptions.items():
            self._subscriptions[event_type] = [
                s for s in subs if s.trigger != trigger
            ]
    
    def publish(self, event: BattleEvent) -> list[tuple]:
        """
        发布事件
        
        Args:
            event: 战斗事件
            
        Returns:
            触发成功的触发器及其目标列表 [(trigger, targets), ...]
        """
        self.events.append(event)
        triggered = []
        
        # 获取订阅了这个事件类型的所有订阅器
        subscriptions = self._subscriptions.get(event.event_type, [])
        
        for sub in subscriptions:
            # 检查触发器是否已在本回合触发过
            trigger_id = id(sub.trigger)
            if trigger_id in self._triggered_this_turn:
                continue
            
            # 检查额外条件
            if sub.condition_checker and not sub.condition_checker(event):
                continue
            
            # 检查触发器自身的条件
            triggered_targets = sub.trigger.check_condition(
                caster=event.caster,
                trigger_target=event.target,
                all_opponents=self._get_opponents(event),
            )
            
            if triggered_targets[0]:  # 第一个元素是bool，第二个是目标列表
                self._triggered_this_turn.add(trigger_id)
                triggered.append((sub.trigger, triggered_targets[1]))
        
        return triggered
    
    def _get_opponents(self, event: BattleEvent) -> list['Character']:
        """获取对手列表"""
        if event.caster.is_enemy:
            return event.caster._battle_state.player_team if hasattr(event.caster, '_battle_state') else []
        else:
            return event.caster._battle_state.enemy_team if hasattr(event.caster, '_battle_state') else []
    
    def new_turn(self) -> None:
        """新回合开始，重置触发状态"""
        self._triggered_this_turn.clear()
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        caster_name: Optional[str] = None,
    ) -> list[BattleEvent]:
        """获取事件历史"""
        events = self.events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if caster_name:
            events = [e for e in events if e.caster.name == caster_name]
        return events
    
    def clear(self) -> None:
        """清空事件历史"""
        self.events.clear()
        self._triggered_this_turn.clear()
