# 终结技机制修改 + GUI修复 + 架构重构 Spec

## Why

1. 终结技应该在能量满时即可释放，不占用行动值（崩铁机制）
2. GUI restart 按钮报错需要修复
3. 行动值常量应该从战斗配置读取而非硬编码
4. 项目结构需要梳理和重构，方便调试

## What Changes

### 1. 终结技机制修改

终结技能量满时释放，不消耗行动值：
- 当角色行动值到达0时，检查是否有终结技可以释放
- 如果有满能量终结技，立即释放，不消耗行动值
- 释放后继续检查，直到没有满能量终结技为止
- 然后才消耗行动值

### 2. GUI修复

修复 restart 按钮回调问题：
- `on_restart` 函数需要接受一个参数
- 或者改为可选参数

### 3. 行动值配置化

将行动值常量从 Character 类移到 BattleState：
```python
@dataclass
class BattleState:
    first_round_av: float = 150.0
    subsequent_av: float = 100.0
```

### 4. 项目架构梳理

```
src/game/
├── __init__.py          # 导出核心类
├── models.py            # 数据模型（Character, Stat, Skill等）
├── damage.py            # 伤害计算
├── battle.py           # 战斗引擎
├── skill.py            # 技能执行器
├── character.py         # 角色创建
├── effect.py           # 效果系统
├── break_system.py     # 击破系统
├── config/
│   ├── __init__.py
│   ├── skills.py       # 技能数据
│   ├── characters.py   # 角色数据
│   ├── enemies.py      # 敌人数据
│   └── battle.py       # 战斗配置（行动值等）
├── ui/
│   ├── __init__.py
│   ├── tui.py         # 文本界面
│   └── gui.py          # 图形界面
└── main.py             # 入口
```

## Impact

- Affected code:
  - `src/game/battle.py` - 终结技不消耗行动值
  - `src/game/models.py` - 移除行动值常量
  - `src/game/gui.py` - 修复restart回调
  - `src/game/config/battle.py` - 战斗配置

## ADDED Requirements

### Requirement: 终结技不消耗行动值

系统 SHALL 在角色行动时检查终结技是否可释放，释放后不消耗行动值。

#### Scenario: 能量满的终结技
- **WHEN** 角色行动值到达0且能量满
- **THEN** 立即释放终结技，不消耗行动值

#### Scenario: 连续终结技
- **WHEN** 多个角色都有满能量终结技
- **THEN** 依次释放，直到没有满能量终结技

## MODIFIED Requirements

### Requirement: BattleState 配置

将行动值常量移到 BattleState 类中。

### Requirement: GUI restart

修复回调函数参数问题。
