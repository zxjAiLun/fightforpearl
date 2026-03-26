# Tasks

- [x] Task 1: 修改 Character 模型，添加敌人血量计算相关字段
  - [x] SubTask 1.1: 添加血量系数相关字段（变体系数、精英组系数、阶段系数）
  - [x] SubTask 1.2: 添加难度索引（difficulty_index）字段
  - [x] SubTask 1.3: 添加 calculate_hp() 方法计算最终血量

- [x] Task 2: 实现元素抗性计算
  - [x] SubTask 2.1: 在 Character 模型添加 get_elemental_res() 方法
  - [x] SubTask 2.2: 根据弱点元素计算抗性（弱点0%，非弱点20%）

- [x] Task 3: 修改 create_enemy 函数
  - [x] SubTask 3.1: 使用新的默认属性值（90级）
  - [x] SubTask 3.2: 支持血量系数参数
  - [x] SubTask 3.3: 默认血量改为 10 × heart

- [x] Task 4: 更新敌人数据模板
  - [x] SubTask 4.1: 更新 data/enemies.json 使用新格式
  - [x] SubTask 4.2: 添加血量系数配置

- [x] Task 5: 更新 SPEC.md 文档
  - [x] SubTask 5.1: 更新敌人系统说明
  - [x] SubTask 5.2: 添加血量公式说明

- [x] Task 6: 运行测试验证修改
  - [x] SubTask 6.1: 运行 pytest 确保所有测试通过
  - [x] SubTask 6.2: 运行游戏验证功能正常

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 1, Task 2
- Task 4 依赖 Task 3
- Task 5 依赖 Task 1-4
- Task 6 依赖 Task 1-5
