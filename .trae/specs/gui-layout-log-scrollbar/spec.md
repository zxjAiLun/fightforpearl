# GUI布局重构与日志滚动修复 Spec

## Why

当前GUI存在以下问题：

1. 日志窗口滚动功能不工作，多余的日志无法及时查看
2. 角色和敌人窗口位置不合理
3. 日志显示内容过于详细
4. 缺少回退功能

## What Changes

### 1. 修复日志滚动问题

* 修复BattleLogPanel的滚动逻辑

* 确保鼠标滚轮和键盘方向键能正确滚动

* 日志满时自动滚动到最新消息

### 2. 重新设计GUI布局

**布局设计**：

```
+--------------------------------------------------+
|  [Buttons]  [Step Back] [Step] [Restart]         |      
|            [Enemy Windows - Top Center]          |
|            enemy1 | enemy2 |enemy3               |
|                                                  |
|  [Action Bar]                                    |
|   (Left)                                         |
|                                                  |
| [Log Panel - Simplified]                         |
| [Last 5 actions]                                 |
|                                                  |
|                                                  |
|                                                  |
|         [Character Windows - Bottom Center]      |
|           char1 | char2 | char3 | char4          |
+--------------------------------------------------+
```

**角色窗口位置**：

* 位置：屏幕底部居中

* 布局：横向排列，最多4个角色，在上方预留第二排的空间

* 大小：280x160像素

**敌人窗口位置**：

* 位置：屏幕顶部居中

* 布局：横向排列，最多5个敌人

* 大小：280x160像素

  Action Bar 和Log Panel在屏幕左边，修改log panel的长度与action bar保持对齐，Action Bar在上log panel在下，战斗窗口占据剩余位置，在做居中

### 3. 简化日志显示格式

**GUI日志显示**（实时显示）：

* 格式：`{actor} 对 {target} 造成 {damage} 伤害`

* 示例：`March7th 对 敌人 造成 1256 伤害`

* 只显示最后一个行动结果

* 最多显示最近8条日志

**导出日志保持原格式**：

* 保持详细的JSON格式

* 包含所有事件信息

### 4. 添加Step Back功能

* 新增"Step Back"按钮

* 回退到上一个行动状态

* 包括：行动值恢复、HP/能量恢复、移除最后一个事件

* 限制：只能回退到当前回合内的行动

## Impact

* Affected code:

  * `src/game/gui.py` - 重构布局和日志显示

  * `src/game/battle.py` - 添加回退逻辑

## ADDED Requirements

### Requirement: 日志滚动修复

系统 SHALL 支持鼠标滚轮和键盘方向键滚动日志
系统 SHALL 在日志满时自动显示最新消息

### Requirement: 布局重构

系统 SHALL 在屏幕顶部居中显示敌人窗口
系统 SHALL 在屏幕底部居中显示角色窗口
系统 SHALL 在屏幕中央显示当前行动值信息

### Requirement: 简化日志显示

系统 SHALL 在GUI日志面板中只显示简化格式：`{actor} 对 {target} 造成 {damage} 伤害`
系统 SHALL 导出日志保持详细格式

### Requirement: Step Back功能

系统 SHALL 提供回退到上一个行动的功能
系统 SHALL 回退包括：恢复行动值、恢复HP/能量、移除事件记录

## MODIFIED Requirements

### Requirement: BattleLogPanel

修改日志显示数量从25条减少到8条
修改日志格式为简化版本
保持导出功能使用详细格式
