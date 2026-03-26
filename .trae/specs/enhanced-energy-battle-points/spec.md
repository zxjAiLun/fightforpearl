# 增强能量系统 + 团队战绩点 + 属性抗性 Spec

## Why

1. 需要调整能量回复数值（普攻20、战技30、大招后5）
2. 需要增加击杀/受击回能机制
3. 需要增加能量恢复效率属性影响所有能量回复
4. 战绩点需要改为团队共享
5. 需要增加元素伤害提高和抵抗属性

## What Changes

### 1. 能量回复数值调整

**技能数据调整**：

* 普攻：`energy_gain = 20`

* 战技：`energy_gain = 30`

* 大招：`energy_gain = 5`（大招释放后能量清零，并回复5点）

### 2. 击杀/受击回能

**怪物数据扩展**：

* `kill_energy_gain: int` - 击杀该怪物后回复的能量（默认10）

* `hit_energy_gain: int` - 受到该怪物攻击后回复的能量（默认10）

### 3. 能量恢复效率

**Character 模型扩展**：

* `energy_recovery_rate: float` - 能量恢复效率（默认1.0 = 100%）

**计算公式**：

```
实际回复能量 = 基础能量 × energy_recovery_rate × (1 - 无视恢复效率)
```

**不受能量恢复效率影响的回复**：

* 需要添加 `affected_by_recovery_rate: bool` 标志

* 默认所有回复都受能量恢复效率影响

### 4. 团队战绩点

**BattleState 模型修改**：

* `battle_points: int` - 团队共享战绩点数

* `battle_points_limit: int` - 团队战绩点上限

**修改点**：

* Character.battle\_points 原逻辑不再使用

* 所有能量回复/消耗改为使用 BattleState 的共享战绩点

### 5. 元素伤害提高和抵抗

**Stat 模型扩展**：

```
# 元素伤害提高
physical_dmg_pct: float = 0.0
wind_dmg_pct: float = 0.0
thunder_dmg_pct: float = 0.0
fire_dmg_pct: float = 0.0
ice_dmg_pct: float = 0.0
quantum_dmg_pct: float = 0.0
imaginary_dmg_pct: float = 0.0

# 元素伤害抵抗
physical_res_pct: float = 0.0
wind_res_pct: float = 0.0
thunder_res_pct: float = 0.0
fire_res_pct: float = 0.0
ice_res_pct: float = 0.0
quantum_res_pct: float = 0.0
imaginary_res_pct: float = 0.0
```

### 6. Battle Demo 修改

在 tui.py 的 battle\_demo 中使用 create\_enemy 创建敌人。

## Impact

* Affected code:

  * `src/game/models.py` - Stat, Character, BattleState 模型

  * `src/game/skill.py` - 技能执行器

  * `src/game/battle.py` - 战斗引擎、create\_enemy

  * `src/game/damage.py` - 伤害计算

  * `data/enemies.json` - 敌人数据（新建）

  * `data/skills.json` - 技能数据更新

## ADDED Requirements

### Requirement: 击杀回能

系统 SHALL 在角色击杀怪物后，根据怪物配置的 kill\_energy\_gain 回复能量。

### Requirement: 受击回能

系统 SHALL 在角色受到怪物攻击后，根据怪物技能的 hit\_energy\_gain 回复能量。

### Requirement: 能量恢复效率

系统 SHALL 在所有能量回复计算中应用能量恢复效率属性。

### Requirement: 团队战绩点

系统 SHALL 实现团队共享的战绩点系统，所有我方角色共享相同的战绩点数。

### Requirement: 元素伤害提高

系统 SHALL 支持根据元素类型增加对应伤害。

### Requirement: 元素伤害抵抗

系统 SHALL 支持根据元素类型减少受到的对应元素伤害。

## MODIFIED Requirements

### Requirement: 能量回复

修改所有能量回复逻辑：

* 普攻回复20点能量

* 战技回复30点能量

* 大招释放后回复5点能量

* 所有回复受能量恢复效率影响

### Requirement: 伤害计算

修改伤害计算，应用于元素伤害提高和抵抗。

## REMOVED Requirements

### Requirement: 个人战绩点

**Reason**: 战绩点改为团队共享
**Migration**: 移除 Character.battle\_points，改为 BattleState.shared\_battle\_points
