# Tasks

- [ ] Task 1: 修改 Character 模型，添加战绩点和能量相关字段
  - [ ] SubTask 1.1: 在 models.py 的 Character 类中添加 battle_points 字段（默认3）
  - [ ] SubTask 1.2: 在 models.py 的 Character 类中添加 battle_points_limit 字段（默认5）
  - [ ] SubTask 1.3: 在 models.py 的 Character 类中添加 energy 字段（替换 current_energy，默认0）
  - [ ] SubTask 1.4: 在 models.py 的 Character 类中添加 energy_limit 字段（默认120）
  - [ ] SubTask 1.5: 添加 add_battle_points() 方法
  - [ ] SubTask 1.6: 添加 add_energy() 方法（处理上限溢出）
  - [ ] SubTask 1.7: 添加 use_battle_points() 方法
  - [ ] SubTask 1.8: 添加 is_energy_full() 方法（检查能量是否满）

- [ ] Task 2: 修改伤害公式，实现差异化防御计算
  - [ ] SubTask 2.1: 在 damage.py 中添加 calculate_def_reduction_for_player() 函数（角色攻击怪物）
  - [ ] SubTask 2.2: 在 damage.py 中添加 calculate_def_reduction_for_enemy() 函数（怪物攻击角色）
  - [ ] SubTask 2.3: 修改 calculate_damage() 函数，添加 attacker_is_player 参数
  - [ ] SubTask 2.4: 根据 attacker_is_player 选择正确的防御公式

- [ ] Task 3: 修改 battle.py 中的战斗引擎
  - [ ] SubTask 3.1: 修改技能执行后添加能量回复逻辑（普攻+10，战技+30）
  - [ ] SubTask 3.2: 修改技能执行后添加战绩点回复逻辑（普攻+1）
  - [ ] SubTask 3.3: 修改大招释放条件检查（能量必须满）
  - [ ] SubTask 3.4: 修改战绩释放条件检查（战绩点必须>0）
  - [ ] SubTask 3.5: 战绩释放后战绩点-1

- [ ] Task 4: 修改 skill.py 中的技能执行器
  - [ ] SubTask 4.1: 在 SkillExecutor 中添加能量消耗检查
  - [ ] SubTask 4.2: 在 SkillExecutor 中添加战绩点消耗检查
  - [ ] SubTask 4.3: 大招消耗能量后重置为0

- [ ] Task 5: 更新 TUI 显示
  - [ ] SubTask 5.1: 在 tui.py 中显示战绩点和能量信息

- [ ] Task 6: 运行测试验证修改
  - [ ] SubTask 6.1: 运行 pytest 确保所有测试通过
  - [ ] SubTask 6.2: 运行游戏验证功能正常

# Task Dependencies

- Task 2 依赖 Task 1（需要 attacker_is_player 参数来自 Character）
- Task 3 依赖 Task 1 和 Task 4
- Task 4 依赖 Task 1
- Task 5 依赖 Task 1
- Task 6 依赖所有其他任务
