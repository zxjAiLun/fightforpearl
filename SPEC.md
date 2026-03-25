# Fight for Pearl — 游戏设计规范

## 1. 项目概述

类崩坏星穹铁道回合制战斗框架，支持角色创建、属性分配、技能设计、装备系统。

**当前阶段**：阶段 1 — 基础框架搭建

---

## 2. 核心概念

### 2.1 属性系统

| 属性 | 英文 | 说明 |
|------|------|------|
| 生命值 | HP | 角色生命，归零则倒下 |
| 攻击力 | ATK | 影响伤害数值 |
| 防御力 | DEF | 降低受到伤害 |
| 速度 | SPD | 决定行动顺序 |
| 暴击率 | CRIT Rate | 触发暴击的概率（上限 100%） |
| 暴击伤害 | CRIT DMG | 暴击时伤害倍率 |
| 效果命中 | Effect Hit | 影响技能附加效果命中率 |
| 效果抵抗 | Effect RES | 抵抗敌方附加效果 |

### 2.2 伤害公式（参考崩铁）

```
伤害 = ATK × 技能倍率 × (1 - DEF_reduction) × (1 + 增伤) × (1 + 易伤) × 属性克制 × (暴击?: CRIT_DMG : 1) × (1 + 伤害加成)
```

**防御减伤公式**：
```
DEF_reduction = DEF / (DEF + 200 + 10 × 敌人等级)
```

**暴击判定**：
- 随机数 rand ∈ [0, 100]，若 rand < CRIT Rate，则暴击
- 暴击时伤害 = 基础伤害 × CRIT DMG

**属性克制**：
- 物理 → 风 → 雷 → 火 → 冰 → 量子 → 虚数 → 物理（各造成 1.2 倍伤害）
- 无克制关系 = 1.0 倍

---

## 3. 角色系统

### 3.1 角色定义

```
Character:
  name: str
  level: int (1-80)
  element: Element
  max_hp: int
  atk: int
  def: int
  spd: int
  crit_rate: float (0-1)
  crit_dmg: float (0-3)
  effect_hit: float (0-1)
  effect_res: float (0-1)
  skills: list[Skill]
  passives: list[Passive]
```

### 3.2 元素类型

```
物理 / 风 / 雷 / 火 / 冰 / 量子 / 虚数
```

---

## 4. 技能系统

### 4.1 技能分类

| 类型 | 说明 |
|------|------|
| 普攻 | 普通攻击，消耗 0 能量 |
| 战技 | 消耗 1 点能量 |
| 大招 | 消耗能量 ≥ 3，自动回复 |
| 被动 | 被动效果，分战斗被动和队长被动 |

### 4.2 技能定义

```
Skill:
  name: str
  type: SkillType (BASIC/SPECIAL/ULT/FAILING_PASSIVE/ABILITY)
  cost: int (能量消耗)
 倍率: float (ATK 倍率)
  damage_type: Element or "Physical"
  effects: list[Effect] (附加效果)
```

---

## 5. 战斗流程

1. **回合开始** → 速度排序（SPD 高的先行动）
2. **行动阶段** → 按顺序执行角色动作（攻击/技能/道具）
3. **伤害计算** → 应用伤害公式
4. **状态结算** → BUFF/DEBUFF 持续时间 -1
5. **回合结束** → 检查角色存活，清除持续时间已到的状态
6. **战斗结束** → 敌人全灭 = 胜利，己方全灭 = 失败

---

## 6. 阶段计划

### 阶段 1：基础框架（进行中）
- [ ] 数据模型（Character, Skill, Effect）
- [ ] 伤害公式实现
- [ ] 基础战斗流程
- [ ] CLI/TUI 界面

### 阶段 2：角色系统
- [ ] 角色创建与属性点分配
- [ ] 等级与成长
- [ ] 角色池

### 阶段 3：技能系统
- [ ] 技能定义与效果
- [ ] BUFF/DEBUFF 系统
- [ ] 能量管理

### 阶段 4：装备系统（规划中）
- [ ] 遗器
- [ ] 光锥

### 阶段 5：GUI（规划中）
- [ ] Pygame / Godot / Web GUI
