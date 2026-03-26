# Checklist

## Energy Values (data/skills.json)
- [x] 普攻 energy_gain = 20
- [x] 战技 energy_gain = 30
- [x] 大招 energy_gain = 5
- [x] Skill 模型默认值正确

## Energy Recovery Rate (models.py)
- [x] Stat.energy_recovery_rate 字段存在（默认1.0）
- [x] Character.apply_energy_gain() 方法正确应用恢复效率

## Kill/Hit Energy Gain
- [x] data/enemies.json 存在怪物数据
- [x] Skill.hit_energy_gain 字段存在（默认10）
- [x] Character.kill_energy_gain 字段存在（默认10）
- [x] create_enemy() 支持 kill_energy_gain
- [x] 击杀后正确回复能量
- [x] 受击后正确回复能量（通过skill.hit_energy_gain）

## Team Battle Points (BattleState)
- [x] BattleState.shared_battle_points 字段存在
- [x] BattleState.shared_battle_points_limit 字段存在
- [x] BattleState.add_shared_battle_points() 方法正确
- [x] BattleState.use_shared_battle_points() 方法正确
- [x] SkillExecutor 使用团队战绩点
- [x] TUI 正确显示团队战绩点

## Elemental Damage (models.py, damage.py)
- [x] 7种元素伤害提高字段存在
- [x] 7种元素伤害抵抗字段存在
- [x] Stat.get_elemental_dmg_pct() 方法正确
- [x] Stat.get_elemental_res_pct() 方法正确

## Battle Demo (tui.py)
- [x] battle_demo 使用 create_enemy 创建敌人
- [x] 敌人配置弱点元素

## SPEC.md
- [x] 能量系统说明已更新
- [x] 战绩点系统说明已更新
- [x] 元素属性说明已添加
- [x] 敌人系统说明已添加

## Tests
- [x] 所有现有测试通过 (97 passed)
- [x] 新功能有基本测试覆盖
