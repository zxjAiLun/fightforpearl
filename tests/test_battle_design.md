# 战斗系统测试设计

> 本文档描述 battle.py 战斗引擎需要新增的关键测试用例。
> 覆盖方向：4角色队伍、怪物队列（≤5）、回合制行动顺序、伤害计算。

---

## 现有测试覆盖情况

| 文件 | 覆盖范围 |
|------|---------|
| `test_battle.py` | 速度排序、战斗结束条件、死亡处理、战斗引擎核心、属性系统 |
| `test_break.py` | 弱点击破触发、DOT效果、击破类型判定 |
| `test_aoe.py` | AOE技能伤害 |
| `test_damage_numbers.py` | 伤害数值计算 |
| `test_followup.py` | 追击触发与执行 |
| `test_skills.py` | 技能执行 |
| `test_celydra.py` | 角色专属测试 |
| `test_hysilens.py` | 海瑟音天赋/结界 |
| `test_player_input.py` | 玩家输入控制 |
| `test_gui.py` | GUI组件 |

**覆盖缺口：**
- 4角色完整队伍战斗流程
- 怪物队列（2-5个敌人）战斗
- 精确的回合制行动顺序验证（多角色混战）
- 伤害计算各环节（防御减伤、暴击、易伤）组合场景
- 共享战斗点消耗与回复
- 行动值（AV）系统
- 能量/大招机制
- 冻结/延后等控制效果
- 玩家控制与AI控制切换
- 回退（step_back）机制
- 战斗日志导出（export_to_json）
- 多人同时死亡边界条件

---

## 新增测试用例（12个）

---

### TC-001：4角色玩家队伍 vs 单个敌人，战斗正常进行并分出胜负

**目的**：验证完整的4人队伍能够正常开始战斗、每个角色都有行动机会、战斗最终结束。

**前置条件**：
- 4个不同预设角色组成玩家队伍
- 1个普通敌人

**测试步骤**：
1. 创建4人玩家队伍（使用 `create_character_from_preset`）
2. 创建1个 `create_enemy`
3. 构造 `BattleState`，调用 `engine.start()`
4. 收集所有 `engine.events`

**预期结果**：
- `engine.events[0].action == "START"`
- 事件中包含至少4个不同角色名（每人至少行动一次）
- 最终存在 `action == "END"` 的事件
- `is_battle_over()` 返回 `(True, winner)`

---

### TC-002：4角色队伍 vs 5个敌人（最大队列），战斗正常进行

**目的**：验证怪物队列最多5个时的战斗处理。

**前置条件**：
- 4个玩家角色
- 5个不同敌人（不同速度和血量配置）

**测试步骤**：
1. 创建5个敌人：`create_enemy(..., hp_units=X)` 各不相同
2. 设置不同速度 `spd` 值
3. `BattleState` + `engine.start()`

**预期结果**：
- 5个敌人都在事件中出现
- 没有索引越界或队列错误
- 战斗正确结束

---

### TC-003：3个敌人队列战斗，正常分出胜负

**目的**：验证中等规模敌人队列（3个）的战斗流程。

**前置条件**：
- 1个玩家角色
- 3个敌人

**测试步骤**：
1. 创建3个敌人（不同属性）
2. 战斗启动
3. 检查事件中有3种不同敌人名称

**预期结果**：
- 所有敌人至少被攻击一次或自身行动一次
- 战斗结束且有明确胜负方

---

### TC-004：回合制行动顺序——高速角色优先于低速角色

**目的**：验证行动值（AV）系统按速度排序，行动值小的先行动。

**前置条件**：
- 2个玩家角色：A（spd=130）、B（spd=80）
- 1个敌人（spd=100）

**测试步骤**：
1. 设置 A 速度=130，B 速度=80，敌人速度=100
2. `engine.start()`
3. 收集前若个 `BASIC`/`SPECIAL`/`ULT` 事件中的 `actor.name`

**预期结果**：
- 第一个行动的角色是 A（速度最快）
- 第二个行动者（排除A后）在 B 和敌人之间按速度排序

---

### TC-005：多个角色行动顺序按 AV 值严格递增

**目的**：在一个完整的 round 内，验证所有角色按 AV 从低到高依次行动。

**前置条件**：
- 4人玩家队伍（速度各异）
- 3个敌人（速度各异）

**测试步骤**：
1. 记录所有 `BASIC`/`SPECIAL`/`ULT` 事件
2. 检查同一轮（`turn` 相同）内，事件的 `action_value` 字段严格递增

**预期结果**：
- 同一轮内，所有角色的行动值单调递增
- 不存在"高AV角色先于低AV角色行动"的情况

---

### TC-006：伤害计算——防御减伤正确应用

**目的**：验证 `calculate_damage` 中防御减伤公式。

**前置条件**：
- 攻击方 ATK=500，level=80
- 防守方 DEF=1000（高防御场景）

**测试步骤**：
1. 用 `calculate_damage` 计算伤害
2. 手动按公式计算预期值：
   - `def_reduction = 100 / (100 + 80*20) = 100/1700`
   - `after_def = ATK * multiplier * (1 - def_reduction)`

**预期结果**：
- `result.def_reduction` 与预期值误差 < 0.0001
- `final_damage` 为正整数

---

### TC-007：伤害计算——暴击与非暴击

**目的**：验证暴击率判定和暴击伤害倍率。

**前置条件**：
- 攻击方 crit_rate=1.0（必定暴击），crit_dmg=1.5
- 非敌人角色（敌人不暴击）

**测试步骤**：
1. 创建 crit_rate=1.0 的角色
2. 执行技能造成伤害
3. 检查 `result.is_crit == True` 和 `crit_multiplier == 1.5`

**预期结果**：
- `is_crit == True`
- `final_damage` 包含了暴击倍率

---

### TC-008：伤害计算——易伤（Vulnerability）增伤

**目的**：验证目标身上的易伤效果能正确增加受到的伤害。

**前置条件**：
- 目标身上有 `Effect(vuln_pct=0.2)`（+20% 易伤）

**测试步骤**：
1. 无易伤状态计算一次伤害
2. 添加 `Effect(vuln_pct=0.2)` 后再计算一次
3. 比较 `final_damage`

**预期结果**：
- 有易伤时的伤害 = 无易伤时伤害 × 1.2（误差 ±1）

---

### TC-009：完整伤害公式组合——ATK×倍率×防御×增伤×暴击×易伤

**目的**：端到端验证完整伤害链路的各个乘区。

**前置条件**：
- ATK=600, multiplier=1.5, crit_rate=1.0, crit_dmg=2.0, vuln=0.3
- 敌人 DEF=800, level=80

**测试步骤**：
1. 执行完整伤害计算
2. 按公式手动推导：
   - `def_reduction = 100/(100+1600) = 100/1700`
   - `base_damage = 600 * 1.5 = 900`
   - `after_def = 900 * (1 - 100/1700)`
   - `final = after_def * (1+0) * 2.0 * (1+0.3)`

**预期结果**：
- `final_damage` 与理论值误差 ≤ 1

---

### TC-010：共享战斗点（Battle Points）消耗与回复

**目的**：验证共享战斗点的消耗和回复机制。

**前置条件**：
- 玩家队伍携带共享 BP，初始值=3，上限=5

**测试步骤**：
1. 检查初始 `state.shared_battle_points`
2. 消耗1点（如果有消耗机制）
3. 检查值正确扣减
4. 检查上限不能超

**预期结果**：
- 消耗后 BP 减少
- 回复后 BP 增加
- BP 不能超过 `shared_battle_points_limit`

---

### TC-011：玩家控制与AI控制模式切换

**目的**：验证 `enable_player_control` / `disable_player_control` 切换正常。

**前置条件**：
- 正常 AI 模式开始
- 注册一个 player_input_callback

**测试步骤**：
1. 确认初始 `is_player_controlled() == False`
2. `enable_player_control(callback)`
3. `is_player_controlled() == True`
4. `disable_player_control()`
5. `is_player_controlled() == False`

**预期结果**：
- 模式切换状态正确反映
- 切换期间战斗不崩溃

---

### TC-012：战斗回退（step_back）恢复到上一次行动状态

**目的**：验证 `step_back()` 正确恢复 HP、能量、BP 和行动值。

**前置条件**：
- 战斗开始后至少执行了一个完整行动

**测试步骤**：
1. 记录行动前 actor 的 `hp_before`、`energy_before`、`bp_before`
2. 执行行动
3. 调用 `step_back()`
4. 检查 actor HP/能量/BP 恢复到记录值

**预期结果**：
- `hp_before` 恢复
- `energy_before` 恢复
- `shared_battle_points` 恢复
- `events` 列表长度减少1

---

### TC-013：多角色同时死亡——战斗正确判定胜负

**目的**：验证多个角色在同一行动/回合内死亡时，胜负判定仍然正确。

**前置条件**：
- 玩家角色只剩1点HP
- 敌人只剩1点HP
- 下一击会导致双方同时死亡

**测试步骤**：
1. 设置上述状态
2. 执行最后一击
3. 检查 `is_battle_over()` 的 winner

**预期结果**：
- 不会抛出异常
- 返回正确的 winner（攻击方优先还是防守方优先，按当前逻辑）

---

### TC-014：行动值冻结效果——被冻结角色跳过行动

**目的**：验证带有 `frozen_turns > 0` 的角色正确跳过行动。

**前置条件**：
- 玩家角色 A 被施加冻结效果（`frozen_turns=2`）
- 敌人 B 速度低于 A

**测试步骤**：
1. 设置 A 的 `frozen_turns = 2`
2. 启动战斗
3. 检查在冻结期间 A 的 `action` 不出现 `BASIC`/`SPECIAL`/`ULT`

**预期结果**：
- 冻结期间 A 不执行任何主动技能
- 冻结结束后 A 恢复正常行动（`UNFROZEN` 事件）
- A 的行动值正确重置

---

### TC-015：行动延后（action_delay）——延迟效果正确扣减行动值

**目的**：验证 `action_delay` 效果使角色行动顺序延后。

**前置条件**：
- 角色 A 的 `action_delay = 0.3`（延后30%）
- 角色 B 速度略高于 A

**测试步骤**：
1. 设置 A.action_delay = 0.3
2. 战斗启动
3. 检查 B 在 A 之前行动

**预期结果**：
- B 的 `action_value` 低于 A（或 A 被 `DELAYED` 事件记录）
- A 的行动被正确推迟

---

## 总结

| 编号 | 覆盖方向 | 测试类 |
|------|---------|--------|
| TC-001 | 4角色队伍战斗流程 | `TestFourPlayerTeamBattle` |
| TC-002 | 5敌人最大队列 | `TestEnemyQueue` |
| TC-003 | 3敌人中等队列 | `TestEnemyQueue` |
| TC-004 | 行动顺序-速度排序 | `TestTurnOrder` |
| TC-005 | 行动顺序-AV严格递增 | `TestTurnOrder` |
| TC-006 | 伤害计算-防御减伤 | `TestDamageCalculation` |
| TC-007 | 伤害计算-暴击 | `TestDamageCalculation` |
| TC-008 | 伤害计算-易伤增伤 | `TestDamageCalculation` |
| TC-009 | 伤害计算-完整链路 | `TestDamageCalculation` |
| TC-010 | 共享战斗点机制 | `TestBattlePoints` |
| TC-011 | 玩家/AI控制切换 | `TestPlayerControl` |
| TC-012 | step_back 回退 | `TestStepBack` |
| TC-013 | 同时死亡胜负判定 | `TestBattleEndConditions` |
| TC-014 | 冻结跳过行动 | `TestControlEffects` |
| TC-015 | 行动延后效果 | `TestControlEffects` |

**新增测试数量：15个**，分布在5个测试类中。
