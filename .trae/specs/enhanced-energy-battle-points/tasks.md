# Tasks

- [x] Task 1: 修改能量回复数值
  - [x] SubTask 1.1: 修改 data/skills.json 普攻 energy_gain=20
  - [x] SubTask 1.2: 修改 data/skills.json 战技 energy_gain=30
  - [x] SubTask 1.3: 修改 data/skills.json 大招 energy_gain=5
  - [x] SubTask 1.4: 修改 Skill 模型默认值

- [x] Task 2: 添加能量恢复效率属性
  - [x] SubTask 2.1: 在 Stat 模型添加 energy_recovery_rate 字段
  - [x] SubTask 2.2: 修改 Character.add_energy() 方法应用恢复效率

- [x] Task 3: 添加击杀/受击回能
  - [x] SubTask 3.1: 创建 data/enemies.json 怪物数据
  - [x] SubTask 3.2: 在 Skill 模型添加 hit_energy_gain 字段
  - [x] SubTask 3.3: 修改 Character 添加 kill_energy_gain 字段
  - [x] SubTask 3.4: 修改 battle.py 在击杀后回复能量
  - [x] SubTask 3.5: 修改 battle.py 在受击后回复能量

- [x] Task 4: 实现团队战绩点
  - [x] SubTask 4.1: 在 BattleState 模型添加 shared_battle_points
  - [x] SubTask 4.2: 在 BattleState 模型添加 shared_battle_points_limit
  - [x] SubTask 4.3: 修改 SkillExecutor 使用团队战绩点
  - [x] SubTask 4.4: 修改 TUI 显示团队战绩点

- [x] Task 5: 添加元素伤害提高和抵抗
  - [x] SubTask 5.1: 在 Stat 模型添加7种元素伤害提高字段
  - [x] SubTask 5.2: 在 Stat 模型添加7种元素伤害抵抗字段
  - [x] SubTask 5.3: 在 Stat 模型添加 get_elemental_dmg_pct() 方法
  - [x] SubTask 5.4: 在 Stat 模型添加 get_elemental_res_pct() 方法

- [x] Task 6: 修改 battle_demo 使用 create_enemy
  - [x] SubTask 6.1: 修改 tui.py battle_demo 使用 create_enemy
  - [x] SubTask 6.2: 为敌人配置弱点元素

- [x] Task 7: 更新 SPEC.md 文档
  - [x] SubTask 7.1: 更新能量系统说明
  - [x] SubTask 7.2: 更新战绩点系统说明
  - [x] SubTask 7.3: 添加元素属性说明
  - [x] SubTask 7.4: 添加敌人系统说明

- [x] Task 8: 运行测试验证修改
  - [x] SubTask 8.1: 运行 pytest 确保所有测试通过
  - [x] SubTask 8.2: 运行游戏验证功能正常

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 1, Task 2
- Task 4 依赖 Task 1
- Task 5 可独立进行
- Task 6 依赖 Task 3
- Task 7 依赖 Task 1-5
- Task 8 依赖 Task 1-6
