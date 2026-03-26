# Tasks

- [x] Task 1: 模块化战斗初始化
  - [x] SubTask 1.1: 修改 tui.py 创建四个角色（星、银狼、姬子、布洛妮娅）
  - [x] SubTask 1.2: 创建 create_player_team() 函数

- [x] Task 2: 清理 characters.json
  - [x] SubTask 2.1: 删除 battle_points_limit 配置
  - [x] SubTask 2.2: 删除 initial_battle_points 配置
  - [x] SubTask 2.3: 删除 initial_energy 配置

- [x] Task 3: 修改玩家角色初始能量
  - [x] SubTask 3.1: 修改 create_character_from_preset() 初始能量 = 能量上限 / 2

- [x] Task 4: 简化敌人数据结构
  - [x] SubTask 4.1: 删除 enemies.json 中的 element、kill_energy_gain、hit_energy_gain
  - [x] SubTask 4.2: 删除 create_enemy() 中的相关参数

- [x] Task 5: 添加韧性削弱系统
  - [x] SubTask 5.1: 在 Skill 模型添加 break_power 字段
  - [x] SubTask 5.2: 修改 data/skills.json 添加 break_power 配置
  - [x] SubTask 5.3: 修改 battle.py 在伤害计算时显示韧性削弱

- [x] Task 6: TUI 显示行动值
  - [x] SubTask 6.1: 在行动日志中显示韧性削弱值

- [x] Task 7: 更新测试
  - [x] SubTask 7.1: 更新相关测试以适应新的数据结构

- [x] Task 8: 更新 SPEC.md 文档

- [x] Task 9: 运行测试验证
  - [x] SubTask 9.1: 运行 pytest 确保所有测试通过
  - [x] SubTask 9.2: 运行游戏验证功能正常

# Task Dependencies
- Task 2, 3, 4 依赖 Task 1
- Task 6 依赖 Task 1
- Task 7 依赖 Task 1-6
- Task 8 依赖 Task 1-7
- Task 9 依赖 Task 1-8
