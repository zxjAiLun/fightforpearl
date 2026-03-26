# Tasks

- [x] Task 1: 修复日志滚动功能
  - [x] SubTask 1.1: 检查BattleLogPanel滚动逻辑
  - [x] SubTask 1.2: 修复鼠标滚轮滚动
  - [x] SubTask 1.3: 修复键盘方向键滚动
  - [x] SubTask 1.4: 添加自动滚动到最新消息功能

- [x] Task 2: 重构GUI布局
  - [x] SubTask 2.1: 移动角色窗口到下部偏右居中
  - [x] SubTask 2.2: 移动敌人窗口到顶部偏右居中
  - [x] SubTask 2.3: 调整Action Bar位置到左上
  - [x] SubTask 2.4: 调整日志面板位置到左下，宽度与action bar对齐

- [x] Task 3: 简化日志显示格式
  - [x] SubTask 3.1: 修改GUI日志格式为 `{actor} 对 {target} 造成 {damage} 伤害`
  - [x] SubTask 3.2: 减少日志显示数量从25条到8条
  - [x] SubTask 3.3: 保持导出日志使用详细格式

- [x] Task 4: 添加Step Back功能
  - [x] SubTask 4.1: 在BattleEngine中添加回退方法
  - [x] SubTask 4.2: 在GUI中添加Step Back按钮
  - [x] SubTask 4.3: 实现回退逻辑（恢复行动值、HP、能量）
  - [x] SubTask 4.4: 添加回退限制（只能回退到当前回合）

- [ ] Task 5: 测试验证
  - [ ] SubTask 5.1: 运行测试验证
  - [ ] SubTask 5.2: 手动测试滚动功能
  - [ ] SubTask 5.3: 手动测试布局显示
  - [ ] SubTask 5.4: 手动测试Step Back功能
