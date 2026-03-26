# Tasks

- [ ] Task 1: 修复GUI restart按钮报错
  - [ ] SubTask 1.1: 修复on_restart函数参数问题

- [ ] Task 2: 行动值配置化
  - [ ] SubTask 2.1: 创建config模块目录结构
  - [ ] SubTask 2.2: 创建battle_config.py存储行动值常量
  - [ ] SubTask 2.3: 从BattleState读取行动值配置
  - [ ] SubTask 2.4: 移除Character类的行动值常量

- [ ] Task 3: 实现终结技不消耗行动值
  - [ ] SubTask 3.1: 修改_process_single_action检查终结技
  - [ ] SubTask 3.2: 满能量终结技立即释放
  - [ ] SubTask 3.3: 循环检查直到没有满能量终结技

- [ ] Task 4: 项目结构梳理
  - [ ] SubTask 4.1: 创建config模块
  - [ ] SubTask 4.2: 创建ui模块
  - [ ] SubTask 4.3: 更新__init__.py导出
  - [ ] SubTask 4.4: 简化main入口

- [ ] Task 5: 运行测试验证
