# Checklist

## Battle Initialization (tui.py)
- [x] create_player_team() 函数存在
- [x] 默认创建四个角色（星、银狼、姬子、布洛妮娅）

## characters.json
- [x] 已删除 battle_points_limit
- [x] 已删除 initial_battle_points
- [x] 已删除 initial_energy
- [x] 仅保留 energy_limit

## Initial Energy
- [x] 玩家角色初始能量 = 能量上限 / 2（60）

## enemies.json
- [x] 已删除 element
- [x] 已删除 kill_energy_gain
- [x] 已删除 hit_energy_gain

## Skill Model (models.py)
- [x] break_power 字段存在
- [x] 普攻 break_power = 10
- [x] 战技 break_power = 20
- [x] 终结技 break_power = 40
- [x] 追击 break_power = 5

## TUI Display
- [x] 韧性削弱显示正常

## Tests
- [x] 所有测试通过 (97 passed)

## SPEC.md
- [x] 文档已更新
