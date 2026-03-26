# 行动条时间轴 + 回合标记修复 Spec

## Why

修复GUI中的关键问题：
1. enemy1行动时卡住，无法继续step
2. 行动条时间戳机制未正确实现
3. 回合结束标记格式不正确且位置错误

## 核心设计决策

### 1. 中立Dummy角色方案

**方案**：为每回合结束的时间点/行动值建立一个中立`RoundMarker`角色：
- 不属于`player_team`或`enemy_team`
- 专门用作时间结束的指示
- 在行动条中显示为特殊的"回合结束"标记
- 行动值 = 当前回合的行动值上限（第一回合150，之后100）

**优势**：
- 简化时间戳逻辑，不需要维护额外的全局变量
- 行动条统一处理所有角色的排序和显示
- 回合结束自然成为时间轴上的一个"行动点"

### 2. 角色/敌人函数分离

**方案**：角色和敌人调用不同的函数规则：

```python
# 玩家角色使用智能技能选择
def select_player_skill(caster, battle_state):
    """玩家角色技能选择逻辑"""
    # 检查战绩点、能量等因素
    ...

# 敌人使用简单的技能选择
def select_enemy_skill(caster, battle_state):
    """敌人技能选择逻辑"""
    # 敌人固定使用普攻或随机技能
    ...
```

## What Changes

### 1. 修复Step卡住问题

**问题分析**：
- `_process_single_action()` 在某些情况下返回 `None`
- 当actor是敌人时，`select_best_skill` 可能返回None
- 需要为敌人实现独立的技能选择逻辑

**修复方案**：
- 创建 `select_enemy_skill()` 函数专门处理敌人技能选择
- 敌人固定使用普攻（无战绩点消耗）
- 确保敌人总是能执行行动

### 2. 实现时间轴机制（基于Dummy）

**实现方案**：
```python
class RoundMarker:
    """回合结束标记角色（不显示头像）"""
    def __init__(self, round_num: int, action_value: float):
        self.name = f"round{round_num}end"
        self.action_value = action_value
        self.is_round_marker = True
        self.is_enemy = False
        # 其他属性...

# 初始化时创建当前回合的标记
current_round_marker = RoundMarker(
    round_num=engine._current_turn,
    action_value=FIRST_ROUND_AV if engine._current_turn == 1 else SUBSEQUENT_AV
)
```

**行动条显示逻辑**：
```python
def update_entries(self, player_team, enemy_team, round_marker=None):
    all_entries = []
    
    # 添加所有存活角色
    for char in player_team + enemy_team:
        if char.is_alive():
            all_entries.append(...)
    
    # 添加回合结束标记
    if round_marker:
        all_entries.append({
            'name': round_marker.name,
            'action_value': round_marker.action_value,
            'is_round_marker': True,
            ...
        })
    
    # 按行动值排序
    all_entries.sort(key=lambda e: e['action_value'])
```

### 3. 回合结束标记位置

**实现方案**：
- 回合开始时创建`RoundMarker`
- `RoundMarker`作为特殊角色加入行动排序
- 当轮到`RoundMarker`行动时，触发回合结束逻辑
- 格式：`round{N}end`（如`round1end`）

## Impact

- Affected code:
  - `src/game/battle.py` - 新增RoundMarker类、敌人技能选择函数
  - `src/game/gui.py` - 行动条处理RoundMarker
  - `src/game/skill.py` - 新增select_enemy_skill

## ADDED Requirements

### Requirement: RoundMarker角色

系统 SHALL 创建`RoundMarker`角色来表示回合结束点。

### Requirement: 独立敌人技能选择

系统 SHALL 为敌人实现独立的技能选择函数，确保敌人始终能执行行动。

### Requirement: 行动条显示RoundMarker

系统 SHALL 在行动条中显示回合结束标记，使用格式`round{N}end`。

## MODIFIED Requirements

### Requirement: 技能选择分离

系统 SHALL 分离玩家角色和敌人的技能选择逻辑：
- 玩家角色：使用`select_player_skill()`考虑战绩点、能量等因素
- 敌人：使用`select_enemy_skill()`简单选择普攻

### Requirement: 回合结束逻辑

回合结束标记 SHALL 作为时间轴上的一个"行动点"，当轮到该点行动时触发回合结束处理。
