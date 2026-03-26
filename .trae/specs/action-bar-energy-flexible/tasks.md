# Tasks

- [x] Task 1: 扩展技能数据结构，支持能量/战绩点回复配置
  - [x] SubTask 1.1: 在 Skill 模型中添加 energy_gain 字段（默认10）
  - [x] SubTask 1.2: 在 Skill 模型中添加 battle_points_gain 字段（默认0）
  - [x] SubTask 1.3: 修改 build_skills_from_json() 解析新字段
  - [x] SubTask 1.4: 更新 skills.json 添加 energy_gain 和 battle_points_gain

- [x] Task 2: 创建角色数据配置文件
  - [x] SubTask 2.1: 创建 data/characters.json 包含角色能量/战绩点配置
  - [x] SubTask 2.2: 添加 energy_limit、initial_energy、battle_points_limit、initial_battle_points

- [x] Task 3: 修改 Character 模型
  - [x] SubTask 3.1: 添加 action_value 字段（当前行动值）
  - [x] SubTask 3.2: 添加 base_spd 字段（基础速度）
  - [x] SubTask 3.3: 添加 calculate_action_value() 方法
  - [x] SubTask 3.4: 添加 advance_action() 方法（行动后加10000距离）
  - [x] SubTask 3.5: 添加 apply_pull_forward() 方法
  - [x] SubTask 3.6: 添加 apply_delay() 方法
  - [x] SubTask 3.7: 添加 reset_action_value_after_freeze() 方法

- [x] Task 4: 修改 SkillExecutor
  - [x] SubTask 4.1: 修改 _execute_basic() 从 skill.energy_gain 读取能量回复值
  - [x] SubTask 4.2: 修改 _execute_basic() 从 skill.battle_points_gain 读取战绩点回复值
  - [x] SubTask 4.3: 修改 _execute_special() 从 skill.energy_gain 读取能量回复值
  - [x] SubTask 4.4: 修改 _execute_ult() 设置能量为0

- [x] Task 5: 实现行动条系统
  - [x] SubTask 5.1: 修改 BattleEngine.start() 初始化行动值
  - [x] SubTask 5.2: 添加 _calculate_init_action_value() 计算初始行动值
  - [x] SubTask 5.3: 修改速度排序逻辑，按 action_value 排序
  - [x] SubTask 5.4: 角色行动后调用 advance_action()
  - [x] SubTask 5.5: 实现 apply_action_delay() 处理拉条/推条
  - [x] SubTask 5.6: 冻结解除时设置行动值为5000

- [x] Task 6: 更新 TUI 显示
  - [x] SubTask 6.1: 显示角色行动值
  - [x] SubTask 6.2: 显示行动条可视化

- [x] Task 7: 更新 SPEC.md 文档
  - [x] SubTask 7.1: 更新伤害公式部分
  - [x] SubTask 7.2: 更新角色系统部分
  - [x] SubTask 7.3: 更新技能系统部分
  - [x] SubTask 7.4: 添加行动条系统说明
  - [x] SubTask 7.5: 添加能量系统说明
  - [x] SubTask 7.6: 添加战绩点系统说明
  - [x] SubTask 7.7: 添加数据文件说明

- [x] Task 8: 运行测试验证修改
  - [x] SubTask 8.1: 运行 pytest 确保所有测试通过
  - [x] SubTask 8.2: 运行游戏验证功能正常

# Task Dependencies
- Task 3 依赖 Task 1
- Task 4 依赖 Task 1
- Task 5 依赖 Task 3
- Task 6 依赖 Task 5
- Task 7 依赖 Task 1-6
- Task 8 依赖 Task 1-6
