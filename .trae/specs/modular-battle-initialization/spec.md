# 模块化战斗初始化 + 韧性削弱系统 Spec

## Why

1. 需要模块化战斗初始化，支持创建多个角色
2. 清理多余的配置文件
3. 统一玩家角色初始能量
4. 简化敌人数据结构
5. 添加韧性削弱机制

## What Changes

### 1. 模块化战斗初始化

战斗时默认创建四个角色：

* 星（物理）

* 银狼（量子）

* 姬子（火）

* 布洛妮娅（冰）

### 2. 清理 characters.json

删除多余的配置：

* 删除 `battle_points_limit`

* 删除 `initial_battle_points`

* 仅保留 `energy_limit` 和 `initial_energy`

### 3. 玩家角色初始能量

所有玩家角色初始能量 = 能量上限的一半

### 4. 简化敌人数据结构

敌人仅保留必要字段：

* `level`

* `hp_units`

* `atk`

* `def`

* `spd`

* `weakness_elements`

* `toughness`

删除：

* `element`

* `kill_energy_gain`

* `hit_energy_gain`

### 5. 韧性削弱系统

所有造成伤害的技能都添加韧性削弱数值：

| 技能类型 | 韧性削弱 |
| ---- | ---- |
| 普攻   | 10   |
| 战技   | 20   |
| 终结技  | 40   |
| 追击   | 5    |

### 6. TUI 显示行动值

每次角色/怪物行动时显示行动值消耗

## Impact

* Affected code:

  * `src/game/tui.py` - 战斗初始化

  * `src/game/models.py` - Skill 模型

  * `data/characters.json` - 简化配置

  * `data/enemies.json` - 简化配置

  * `tests/` - 测试更新

## ADDED Requirements

### Requirement: 韧性削弱

系统 SHALL 在每次造成伤害时，根据技能类型削弱目标韧性。

### Requirement: 行动值显示

系统 SHALL 在 TUI 中显示每次行动消耗的行动值。

## MODIFIED Requirements

### Requirement: Skill 模型

添加 `break_power` 字段（韧性削弱值）。

### Requirement: characters.json

删除 battle\_points 相关配置。

### Requirement: enemies.json

简化敌人数据结构。

### Requirement: 初始能量

默认玩家角色初始能量 = 能量上限 / 2。
