# Checklist

## Models (models.py)
- [x] Character.battle_points 字段存在且默认为 3
- [x] Character.battle_points_limit 字段存在且默认为 5
- [x] Character.energy 字段存在且默认为 0
- [x] Character.energy_limit 字段存在且默认为 120
- [x] add_battle_points() 方法正确实现（增加战绩点，上限为 limit）
- [x] add_energy() 方法正确实现（增加能量，上限为 limit）
- [x] use_battle_points() 方法正确实现（消耗战绩点，返回是否成功）
- [x] is_energy_full() 方法正确实现（检查 energy >= energy_limit）

## Damage (damage.py)
- [x] calculate_def_reduction_for_player() 函数存在并使用正确公式
- [x] calculate_def_reduction_for_enemy() 函数存在并使用正确公式
- [x] calculate_damage() 函数接受 attacker_is_player 参数
- [x] 根据 attacker_is_player 选择正确的防御公式
- [x] 旧版 calculate_def_reduction() 函数保留但不再使用

## Battle Engine (battle.py)
- [x] 普攻执行后能量 +10
- [x] 战技执行后能量 +30
- [x] 普攻执行后战绩点 +1
- [x] 大招释放前检查能量是否满
- [x] 战绩释放前检查战绩点是否 > 0
- [x] 战绩释放后战绩点 -1
- [x] 大招释放后能量重置为 0

## Skill Executor (skill.py)
- [x] 大招释放需要能量满
- [x] 大招释放后能量消耗（重置为0）
- [x] 战技随时可用（不消耗能量）
- [x] 普攻随时可用

## TUI (tui.py)
- [x] 角色状态显示包含能量信息
- [x] 角色状态显示包含战绩点信息

## Tests
- [x] 所有现有测试通过 (97 passed)
- [x] 新功能有基本测试覆盖
