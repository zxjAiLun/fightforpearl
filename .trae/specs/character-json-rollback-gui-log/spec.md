# 角色数据JSON化 + GUI修复 Spec

## Why

1. 当前角色数据分离（preset在Python代码，json只有配置），需要统一到json
2. GUI日志超出范围无法查看，需要添加滚动功能
3. 删除属性分配功能（不需要手动分配）
4. 修复自动战斗只放普攻的问题

## What Changes

### 1. characters.json 包含完整角色属性

```json
{
  "name": "星",
  "element": "PHYSICAL",
  "stat": {
    "base_max_hp": 1200,
    "base_atk": 120,
    "base_def": 80,
    "base_spd": 105,
    "crit_rate": 0.05,
    "crit_dmg": 1.5
  },
  "energy_limit": 120,
  "skills": [...]
}
```

### 2. GUI日志滚动功能

- 添加鼠标滚轮支持
- 或上下箭头键滚动
- 添加滚动条指示器

### 3. 修复自动战斗技能选择

- 检查战绩点是否足够释放战技
- 优先释放战技（消耗战绩点）
- 普攻仅在战绩点不足时使用

## Impact

- Affected code:
  - `data/characters.json` - 包含完整角色数据
  - `src/game/character.py` - 从json读取所有属性
  - `src/game/gui.py` - 日志滚动功能
  - `src/game/skill.py` - 修复技能选择逻辑

## ADDED Requirements

### Requirement: 完整角色数据JSON

系统 SHALL 从 characters.json 加载角色的所有属性。

### Requirement: GUI日志滚动

系统 SHALL 支持日志面板滚动查看历史记录。

### Requirement: 智能技能选择

系统 SHALL 在战绩点足够时优先释放战技。
