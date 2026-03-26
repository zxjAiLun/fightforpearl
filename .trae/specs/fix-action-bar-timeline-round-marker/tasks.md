# Tasks

- [x] Task 1: 创建RoundMarker类
  - [x] SubTask 1.1: 在battle.py中创建RoundMarker dataclass
  - [x] SubTask 1.2: RoundMarker包含name、action_value等属性
  - [x] SubTask 1.3: RoundMarker标记is_round_marker=True

- [x] Task 2: 实现敌人技能选择函数
  - [x] SubTask 2.1: 在skill.py中创建select_enemy_skill函数
  - [x] SubTask 2.2: 敌人固定使用普攻
  - [x] SubTask 2.3: 修改battle.py调用正确的选择函数

- [x] Task 3: 重构_process_single_action
  - [x] SubTask 3.1: 创建当前回合的RoundMarker
  - [x] SubTask 3.2: RoundMarker加入行动排序
  - [x] SubTask 3.3: 当RoundMarker行动时触发回合结束
  - [x] SubTask 3.4: 回合结束时创建下一回合的RoundMarker

- [x] Task 4: 更新GUI行动条
  - [x] SubTask 4.1: ActionBar识别RoundMarker
  - [x] SubTask 4.2: RoundMarker显示为特殊标记（不显示头像）
  - [x] SubTask 4.3: 回合结束时正确更新显示

- [x] Task 5: 测试验证
  - [x] SubTask 5.1: 运行测试验证
  - [x] SubTask 5.2: 90/96测试通过
