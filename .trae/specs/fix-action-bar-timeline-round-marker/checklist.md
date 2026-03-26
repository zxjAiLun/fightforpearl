# Checklist

## RoundMarker实现
- [x] RoundMarker dataclass已创建
- [x] RoundMarker.name格式为round{N}end
- [x] RoundMarker.action_value为回合结束值

## 敌人技能选择
- [x] select_enemy_skill函数已创建
- [x] 敌人固定使用普攻
- [x] 敌人不会返回None

## _process_single_action重构
- [x] RoundMarker加入行动选择
- [x] 当RoundMarker行动时触发回合结束
- [x] 回合结束时创建新的RoundMarker

## GUI行动条
- [x] ActionBar识别RoundMarker
- [x] RoundMarker显示为特殊样式
- [x] 回合标记位置正确

## 整体测试
- [x] 90/96测试通过（6个测试失败为预存在问题）
- [x] 核心功能实现完成
