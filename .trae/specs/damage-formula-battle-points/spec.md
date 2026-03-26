# 伤害公式修改 + 战绩点系统 + 能量系统 Spec

## Why

1. 当前伤害公式未区分角色攻击怪物与怪物攻击角色的不同减伤机制
2. 需要复刻崩坏星穹铁道的战绩点（Battle Points）机制
3. 当前能量系统需要完善能量回复和上限机制

## What Changes

### 1. 伤害公式修改

**角色攻击怪物时，防御减伤公式**：

```
防御系数 = 100 / (100 + (敌人等级 × 20) × (1 - 减防 - 无视防御))
```

**怪物攻击角色时，防御减伤公式**：

```
防御系数 = (10 × 敌人等级 + 200) / (100 × 敌人等级 + 200 + 角色防御)
```

### 2. 战绩点系统（Battle Points）

* 战绩点上限：5 点

* 释放战绩：消耗 1 点战绩点

* 释放普攻：回复 1 点战绩点

* 无战绩点：无法释放战绩

### 3. 能量系统

* 能量上限：默认 120 点

* 普攻回复：10 点能量

* 战技回复：30 点能量

* 能量溢出：到达上限后溢出部分直接丢弃，不累计

* 大招释放：需要能量 ≥ 上限（满能量）才能释放

## Impact

* Affected specs: 伤害公式、战斗流程、技能系统

* Affected code:

  * `src/game/damage.py` - 伤害计算

  * `src/game/models.py` - 数据模型修改

  * `src/game/battle.py` - 战斗引擎修改

  * `src/game/skill.py` - 技能执行修改

## ADDED Requirements

### Requirement: 差异化防御公式

系统 SHALL 支持角色攻击怪物和怪物攻击角色使用不同的防御减伤计算公式。

#### Scenario: 角色攻击怪物

* **WHEN** 角色对怪物造成伤害

* **THEN** 使用角色攻击怪物的防御减伤公式

#### Scenario: 怪物攻击角色

* **WHEN** 怪物对角色造成伤害

* **THEN** 使用怪物攻击角色的防御减伤公式

### Requirement: 战绩点系统

系统 SHALL 实现战绩点机制，限制战绩的使用频率。

#### Scenario: 释放战绩

* **WHEN** 角色战绩点 > 0 时释放战绩

* **THEN** 战绩点 -1（默认）

#### Scenario: 普攻回复战绩点

* **WHEN** 角色释放普通攻击

* **THEN** 战绩点 +1，默认上限为 5

#### Scenario: 无战绩点释放战绩

* **WHEN** 角色战绩点 = 0 时尝试释放战绩

* **THEN** 战绩释放失败，系统提示"战绩点不足"

### Requirement: 能量系统

系统 SHALL 实现完整的能量管理和上限机制。

#### Scenario: 普攻回复能量

* **WHEN** 角色释放普通攻击

* **THEN** 能量 +10，上限为 120

#### Scenario: 战技回复能量

* **WHEN** 角色释放战技

* **THEN** 能量 +30，上限为 120

#### Scenario: 能量溢出

* **WHEN** 当前能量为 115/120，释放普攻 +10

* **THEN** 能量变为 120/120（而非 125）

#### Scenario: 释放大招

* **WHEN** 角色能量 < 120

* **THEN** 大招无法释放

## MODIFIED Requirements

### Requirement: 伤害计算函数

修改 `calculate_damage` 函数，添加 `attacker_is_player` 参数以区分攻击者类型。

### Requirement: Character 模型

在 Character 模型中添加：

* `battle_points: int` - 战绩点，默认 3

* `energy: float` - 当前能量，默认 0

* `energy_limit: int` - 能量上限，默认 120

* `battle_points_limit: int` - 战绩点上限，默认 5

## REMOVED Requirements

### Requirement: 旧版防御公式

**Reason**: 需要实现崩铁风格的差异化防御公式
**Migration**: 无需迁移，旧公式完全废弃
