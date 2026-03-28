"""优先级行动队列 - 支持插队的行动调度系统"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from .models import Character, Skill


@dataclass
class QueuedAction:
    """一个待执行的行动"""
    actor: Character
    skill: Skill
    targets: list[Character]
    priority: int  # 优先级
    is_preemptive: bool = False  # 是否插队
    timestamp: float = 0.0  # 时间戳（用于同优先级排序）


class PriorityActionQueue:
    """
    优先级行动队列
    
    特性：
    - 按优先级排序，高优先级在前
    - 支持插队（preemptive）
    - 同优先级按时间戳排序
    """
    
    def __init__(self):
        self._queue: list[QueuedAction] = []
        self._current_action: Optional[QueuedAction] = None
        self._counter: float = 0.0  # 用于生成时间戳
    
    def _get_next_timestamp(self) -> float:
        """获取下一个时间戳（单调递增）"""
        self._counter += 1.0
        return self._counter
    
    def enqueue(self, action: QueuedAction) -> None:
        """添加行动到队列"""
        if action.timestamp == 0.0:
            action.timestamp = self._get_next_timestamp()
        self._queue.append(action)
        self._queue.sort(key=lambda a: (-a.priority, a.timestamp))
    
    def enqueue_preemptive(self, action: QueuedAction) -> None:
        """插队 - 将行动插入到当前执行的行动之后、最高优先级之前"""
        action.is_preemptive = True
        if action.timestamp == 0.0:
            action.timestamp = self._get_next_timestamp()
        
        if self._current_action:
            # 找到当前行动的位置
            current_idx = self._find_action_index(self._current_action)
            if current_idx >= 0:
                # 插入到当前行动之后、同优先级行动之前
                insert_idx = current_idx + 1
                while insert_idx < len(self._queue) and self._queue[insert_idx].priority == self._current_action.priority:
                    insert_idx += 1
                self._queue.insert(insert_idx, action)
            else:
                # 当前行动不在队列中（已完成），插入到队列头部
                self._queue.insert(0, action)
        else:
            # 没有当前行动，直接插入到队列头部
            self._queue.insert(0, action)
    
    def _find_action_index(self, action: QueuedAction) -> int:
        for i, a in enumerate(self._queue):
            if a is action:
                return i
        return -1
    
    def dequeue(self) -> Optional[QueuedAction]:
        """取出下一个要执行的行动"""
        if not self._queue:
            return None
        action = self._queue.pop(0)
        self._current_action = action
        return action
    
    def peek(self) -> Optional[QueuedAction]:
        """查看下一个行动（不取出）"""
        return self._queue[0] if self._queue else None
    
    def cancel(self, actor: Character) -> bool:
        """取消某个角色的待执行行动"""
        for i, a in enumerate(self._queue):
            if a.actor is actor:
                del self._queue[i]
                return True
        return False
    
    def is_empty(self) -> bool:
        return len(self._queue) == 0
    
    def clear(self) -> None:
        self._queue.clear()
        self._current_action = None
    
    @property
    def current_action(self) -> Optional[QueuedAction]:
        """获取当前正在执行的行动"""
        return self._current_action
    
    def __len__(self) -> int:
        return len(self._queue)
    
    def __repr__(self) -> str:
        return f"PriorityActionQueue(queue={self._queue}, current={self._current_action})"
