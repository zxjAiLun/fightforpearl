# Checklist

## Skills Data (data/skills.json)
- [x] Skill.energy_gain 字段存在且有默认值
- [x] Skill.battle_points_gain 字段存在且有默认值
- [x] skills.json 中每个技能都有 energy_gain 和 battle_points_gain 配置

## Character Data (data/characters.json)
- [x] characters.json 文件存在
- [x] 每个角色有 energy_limit 配置
- [x] 每个角色有 initial_energy 配置
- [x] 每个角色有 battle_points_limit 配置
- [x] 每个角色有 initial_battle_points 配置

## Models (models.py)
- [x] Skill.energy_gain 字段存在
- [x] Skill.battle_points_gain 字段存在
- [x] Character.action_value 字段存在
- [x] Character.base_spd 字段存在
- [x] calculate_action_value() 方法正确实现
- [x] advance_action() 方法正确实现
- [x] apply_pull_forward() 方法正确实现
- [x] apply_delay() 方法正确实现
- [x] reset_action_value_after_freeze() 方法正确实现

## Skill Executor (skill.py)
- [x] _execute_basic() 从 skill.energy_gain 读取能量回复值
- [x] _execute_basic() 从 skill.battle_points_gain 读取战绩点回复值
- [x] _execute_special() 从 skill.energy_gain 读取能量回复值
- [x] _execute_ult() 释放后能量归零

## Battle Engine (battle.py)
- [x] 战斗开始时正确初始化行动值 (_init_action_values)
- [x] 速度排序按 action_value 升序
- [x] 角色行动后正确重置行动值（+10000）
- [x] 拉条效果正确减少行动值
- [x] 推条效果正确增加行动值
- [x] 冻结解除时行动值设为5000

## TUI (tui.py)
- [x] 显示角色行动值
- [x] 行动条可视化正确

## SPEC.md
- [x] 伤害公式部分已更新
- [x] 角色系统部分已更新
- [x] 技能系统部分已更新
- [x] 行动条系统说明已添加
- [x] 能量系统说明已添加
- [x] 战绩点系统说明已添加
- [x] 数据文件说明已添加

## Tests
- [x] 所有现有测试通过 (97 passed)
- [x] 新功能有基本测试覆盖
