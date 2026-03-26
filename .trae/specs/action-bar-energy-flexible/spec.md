# 灵活能量系统 + 行动条系统 Spec

## Why

1. 当前能量/战绩点回复值硬编码在 SkillExecutor 中，无法为不同角色定制
2. 需要实现崩铁风格的行动条（Action Bar）系统，基于速度计算行动顺序
3. 每次修改后需要更新 SPEC.md 文档

## What Changes

### 1. 灵活能量/战绩点系统

**技能数据结构扩展**：

* 每个技能可定义 `energy_gain`：释放该技能后回复的能量值

* 每个技能可定义 `battle_points_gain`：释放该技能后回复的战绩点数

**角色数据扩展**：

* 每个角色可定义 `energy_limit`：能量上限（默认120）

* 每个角色可定义 `initial_energy`：初始能量值

* 每个角色可定义 `battle_points_limit`：战绩点上限（默认5）

* 每个角色可定义 `initial_battle_points`：初始战绩点数

### 2. 行动条系统（Action Bar）

**基础概念**：

* 行动值（Action Value）= 距离下次行动的剩余距离

* 行动所需距离 = 10000（固定）

* 角色速度 = 每秒前进距离

**行动值计算**：

```
初始行动值 = 10000 / 角色速度
例：100速角色行动值=100，120速=83.3，200速=50
```

**行动条排序**：

* 行动值最小的角色先行动

* 行动后重新计算该角色的行动值（加回10000）

* 后续按照行动值最小的角色依次行动

* 可以理解为有一个跑道，速度快的角色先跑，所以他的行动值（轮到他动需要的时间）少，所以他先行动，他行动之后，再轮到后续行动值的角色行动。

**影响行动值的因素**：

1. **加速/减速效果**

   * 变化后行动值 = 当前距离 + 变化后速度

   * 例：120速角色行动值为30时，获得+50速增益

   * 新行动值 = 120\*30/(120+50) = 21.2

2. **拉条/推条效果**

   * 每1%提前/延后 = 100距离

   * 提前最多到0，延后可以无限

   * 例：160速角色行动值为20时，被拉条20%

   * 新行动值 (20 *\* 160 - 10000 \* *20%) / 160 = 7.5

3. **冻结效果**

   * 冻结角色下一回合行动值 = 5000

## Impact

* Affected specs: 技能系统、战斗流程、数据模型

* Affected code:

  * `data/skills.json` - 技能数据扩展

  * `data/characters.json` - 角色数据扩展（新建）

  * `src/game/models.py` - 数据模型修改

  * `src/game/skill.py` - 技能执行器修改

  * `src/game/battle.py` - 战斗引擎重写行动排序逻辑

## ADDED Requirements

### Requirement: 技能能量/战绩点回复配置

系统 SHALL 支持在技能数据中配置能量和战绩点回复值。

#### Scenario: 普攻回复能量

* **WHEN** 角色释放普攻技能

* **THEN** 根据技能配置的 energy\_gain 回复能量

#### Scenario: 战技回复能量

* **WHEN** 角色释放战技技能

* **THEN** 根据技能配置的 energy\_gain 回复能量

### Requirement: 行动条系统

系统 SHALL 实现基于速度的行动条排序机制。

#### Scenario: 速度排序

* **WHEN** 战斗开始或角色行动后

* **THEN** 按行动值升序排列（小的先行动）

#### Scenario: 行动后重置

* **WHEN** 角色完成行动

* **THEN** 该角色行动值 += 10000

#### Scenario: 拉条效果

* **WHEN** 角色受到拉条效果（如加速XX%）

* **THEN** 行动值 -= 10000 × 拉条比例

#### Scenario: 推条效果

* **WHEN** 角色受到推条效果（如行动延后XX%）

* **THEN** 行动值 += 10000 × 推条比例

#### Scenario: 冻结后重置

* **WHEN** 角色解除冻结状态

* **THEN** 该角色行动值 = 5000

## MODIFIED Requirements

### Requirement: Character 模型

修改 Character 模型：

* 添加 `action_value: float` - 当前行动值

* 添加 `base_spd: int` - 基础速度（用于百分比加速计算）

### Requirement: SkillExecutor

修改技能执行器：

* 能量回复值从技能数据读取，而非硬编码

* 战绩点回复值从技能数据读取，而非硬编码

### Requirement: SPEC.md 更新

每次完成代码修改后，更新 `SPEC.md` 文档以反映最新实现。

## REMOVED Requirements

### Requirement: 硬编码能量回复

**Reason**: 需要支持不同角色有不同的能量回复机制
**Migration**: 从 skills.json 读取配置
