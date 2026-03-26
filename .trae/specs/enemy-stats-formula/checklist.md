# Checklist

## Character Model (models.py)
- [x] 血量系数相关字段存在
- [x] difficulty_index 字段存在
- [x] calculate_hp() 方法正确实现
- [x] get_elemental_res() 方法正确实现（弱点0%，非弱点20%）

## create_enemy (battle.py)
- [x] 使用新的默认属性值（90级）
- [x] ATK = 663
- [x] DEF = 1100
- [x] SPD = 132
- [x] 效果命中 = 32.0%
- [x] 效果抵抗 = 30.0%
- [x] toughness = 40
- [x] 默认血量 = 10 × heart

## Enemy Data (data/enemies.json)
- [x] 使用新格式
- [x] 包含血量系数配置

## SPEC.md
- [x] 敌人系统说明已更新
- [x] 血量公式说明已添加

## Tests
- [x] 所有现有测试通过 (97 passed)
- [x] 新功能有基本测试覆盖
