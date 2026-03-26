# Tasks

- [ ] Task 1: 修复战绩点逻辑
  - [ ] SubTask 1.1: 修改 SkillExecutor._execute_basic() 仅对玩家角色增加战绩点
  - [ ] SubTask 1.2: 确保怪物技能执行不会增加战绩点

- [ ] Task 2: 修复暴击判定
  - [ ] SubTask 2.1: 修改 damage.py 中敌人不进行暴击判定
  - [ ] SubTask 2.2: 将敌人暴击率强制设为0

- [ ] Task 3: 修复能量显示
  - [ ] SubTask 3.1: 修改 tui.py 移除能量条
  - [ ] SubTask 3.2: 直接显示能量数值如 `能量:30/120`

- [ ] Task 4: 修复行动值计算
  - [ ] SubTask 4.1: 修改 Character 模型添加 TURN_ACTION_VALUE 常量
  - [ ] SubTask 4.2: 第一轮行动值 = 150 / 速度
  - [ ] SubTask 4.3: 后续回合行动值 = 100 / 速度
  - [ ] SubTask 4.4: 修改 battle.py 追踪回合数

- [ ] Task 5: 修复测试数据
  - [ ] SubTask 5.1: 测试中涉及多个enemy时使用 hp_units=1

- [ ] Task 6: 运行测试验证

# Task Dependencies
- Task 2, 3, 4 依赖 Task 1
- Task 5 依赖 Task 1-4
- Task 6 依赖 Task 1-5
