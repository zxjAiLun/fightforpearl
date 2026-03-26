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
| 能量恢复效率 | Energy Recovery Rate | 影响能量回复量（默认100%） |
| 元素伤害提高 | Elemental DMG% | 各元素伤害加成 |
| 元素伤害抵抗 | Elemental RES% | 各元素伤害减免 |

### 2.2 伤害公式（参考崩铁）

```
伤害 = 基础值 × (1 - DEF_reduction) × (1 + 增伤) × (1 + 易伤) × (1 - 减伤) × (暴击?: CRIT_DMG : 1) × (1 + 独立伤害乘区)
```

**角色攻击怪物时，防御减伤公式**：
```
防御系数 = 100 / (100 + (敌人等级 × 20) × (1 - 减防 - 无视防御))
```

**怪物攻击角色时，防御减伤公式**：
```
防御系数 = (10 × 敌人等级 + 200) / (100 × 敌人等级 + 200 + 角色防御)
```

**暴击判定**：
- 玩家角色：随机数 rand ∈ [0, 100]，若 rand < CRIT Rate，则暴击
- **敌人（is_enemy=True）不进行暴击判定，暴击率强制为0**

---

## 3. 角色系统

### 3.1 角色定义

```
Character:
  name: str
  level: int (1-80)
  element: Element
  stat: Stat (基础属性)
  current_hp: int
  energy: float (当前能量)
  energy_limit: int (能量上限，默认120)
  initial_energy: float (初始能量，默认=能量上限/2)
  action_value: float (行动值)
  base_spd: int (基础速度)
  kill_energy_gain: int (击杀回能，默认10)
  skills: list[Skill]
  passives: list[Passive]
```

### 3.2 Stat 属性

```
Stat:
  # 基础属性
  base_max_hp, base_atk, base_def, base_spd
  
  # 百分比加成
  hp_pct, atk_pct, def_pct, spd_pct
  
  # 固定值加成
  hp_flat, atk_flat, def_flat
  
  # 暴击/抵抗
  crit_rate, crit_dmg, effect_hit, effect_res
  
  # 伤害加成
  dmg_pct, break_efficiency
  
  # 能量恢复效率
  energy_recovery_rate: float (默认1.0 = 100%)
  
  # 元素伤害提高
  physical_dmg_pct, wind_dmg_pct, thunder_dmg_pct
  fire_dmg_pct, ice_dmg_pct, quantum_dmg_pct, imaginary_dmg_pct
  
  # 元素伤害抵抗
  physical_res_pct, wind_res_pct, thunder_res_pct
  fire_res_pct, ice_res_pct, quantum_res_pct, imaginary_res_pct
```

### 3.3 元素类型

```
物理 / 风 / 雷 / 火 / 冰 / 量子 / 虚数
```

### 3.4 能量系统

- 能量上限：默认 120 点（可配置）
- **初始能量：能量上限 / 2（默认60）**
- 普攻回复：根据技能配置（默认20点）
- 战技回复：根据技能配置（默认30点）
- 大招释放后回复：根据技能配置（默认5点）
- 击杀回能：根据角色配置（默认10点）
- **受击回能：根据技能配置（默认10点）**
- 能量恢复效率：百分比加成，影响所有能量回复
- 能量溢出：到达上限后溢出部分直接丢弃，不累计
- **大招释放：需要能量满（≥能量上限）才能释放**

### 3.5 战绩点系统

- **团队共享**：战绩点是团队共享属性，存储在 BattleState 中
- 战绩点上限：默认 5 点
- 普攻回复：根据技能配置（默认1点）
- **只有玩家角色增加战绩点，怪物不增加**

---

## 4. 技能系统

### 4.1 技能分类

| 类型 | 说明 |
|------|------|
| 普攻 | 普通攻击，回复能量和战绩点 |
| 战技 | 回复能量 |
| 大招 | 消耗全部能量，需能量满，释放后回复少量能量 |
| 追击 | 满足条件后触发的额外攻击 |
| 被动 | 被动效果，分战斗被动和队长被动 |

### 4.2 技能定义

```
Skill:
  name: str
  type: SkillType (BASIC/SPECIAL/ULT/FALLING_PASSIVE/ABILITY)
  cost: float (能量消耗)
  multiplier: float (ATK 倍率)
  damage_type: Element
  energy_gain: float (释放后回复的能量)
  battle_points_gain: int (释放后回复的战绩点)
  hit_energy_gain: int (受到攻击时回复的能量)
  break_power: float (韧性削弱值)
  target_count: int (攻击目标数量)
  aoe_multiplier: float (AOE倍率折扣)
```

### 4.3 技能能量回复配置

技能数据中可配置能量回复：
- 每个技能的回复值可在 `data/skills.json` 中独立设置
- 普攻默认：energy_gain=20, battle_points_gain=1, break_power=10
- 战技默认：energy_gain=30, battle_points_gain=0, break_power=20
- 大招默认：energy_gain=5, battle_points_gain=0, break_power=40
- 追击默认：break_power=5

### 4.4 韧性削弱

| 技能类型 | 韧性削弱 |
|---------|---------|
| 普攻 | 10 |
| 战技 | 20 |
| 终结技 | 40 |
| 追击 | 5 |

---

## 5. 敌人系统

### 5.1 敌人基本设定

- 怪物默认不带有 element（无元素属性）
- 怪物默认 level = 90
- **怪物不暴击，暴击率强制为0**
- **怪物不增加战绩点**

### 5.2 敌人血量计算公式

**公式**：
```
敌人最终生命值 = 标度系数 × 线性值 × 变体系数 × 精英组系数 × 阶段系数
```

**血量标准（heart）**：
- 标度系数 1.0 时，怪物等级 90 级，血量 = 21997.729
- 定义为 1 heart

**线性值**（通过 difficulty_index 区分难度）：
- 默认（index=0）：21997.729（1 heart）
- 混沌（index=1）：26954.786

**变体系数**：
- 包括：生命、攻击、速度、韧性、防御系数
- 默认均为 1.0

**生成怪物时的用法**：
- 直接以 n × heart 定义血量
- 例如：10 × heart = 219977.29 血量

### 5.3 敌人默认属性（90级普通怪物）

| 属性 | 值 |
|------|-----|
| level | 90 |
| HP | 10 × heart = 219977.29 |
| ATK | 663 |
| DEF | 1100 |
| SPD | 132.00 |
| 效果命中 | 32.0% |
| 效果抵抗 | 30.0% |
| 韧性（toughness） | 40 |

### 5.4 元素抗性规则

- 弱点元素：抗性为 0%
- 非弱点元素：抗性为 20%

**示例**：
- 弱点：物理、虚数、火
- 则：物理、虚数、火 抗性 = 0%
- 其他（雷、冰、风、量子）：抗性 = 20%

---

## 6. 行动条系统（Action Bar）

### 6.1 基础概念

- **行动值（Action Value）**：距离下次行动的剩余时间
- **第一轮行动值**：150（简化计算）
- **后续行动值**：100
- **角色速度**：每秒前进的距离

### 6.2 行动值计算

```
第一轮：行动值 = 150 / 速度
后续：行动值 = 100 / 速度

示例：
150 / 100速 = 1.5
150 / 120速 ≈ 1.25
150 / 132速 ≈ 1.14
```

### 6.3 行动条排序

- 按行动值升序排列（小的先行动）
- 行动后重置行动值（+100）

### 6.4 影响行动值的因素

1. **加速/减速效果**
   - 变化后行动值 = 当前距离 / 变化后速度

2. **拉条/推条效果**
   - 每1%提前/延后 = 100距离
   - 提前最多到0，延后可以无限

3. **冻结效果**
   - 冻结角色解除后，行动值设为 5000（半回合）

### 6.5 行动值配置

行动值常量存储在配置文件中，可通过 BattleState 修改：

```python
BattleState:
  first_round_av: float = 150.0
  subsequent_av: float = 100.0
```

---

## 7. 战斗流程

### 7.1 回合制行动顺序（基于行动条）

1. **战斗开始** → 初始化所有角色行动值（第一轮）
2. **行动值排序** → 按行动值升序排列
3. **角色行动** → 行动值最小的角色行动
4. **行动后重置** → 该角色行动值 +100
5. **循环判断** → 回到步骤2
6. **回合结束** → 所有角色行动值 ≥ 100 时触发
7. **状态结算** → BUFF/DEBUFF 持续时间 -1
8. **击破DOT触发** → 结算击破持续伤害
9. **战斗结束** → 敌人全灭 = 胜利，己方全灭 = 失败

### 7.2 状态效果

- **冻结**：无法行动，冻结解除后行动值重置为5000
- **行动延后**：量子/虚数击破效果，延后30%
- **弱点击破**：裂伤、灼烧、冻结、触电、风化、纠缠、禁锢

---

## 8. 数据文件

### 8.1 src/game/config/battle.py

战斗配置常量：

```python
FIRST_ROUND_AV = 150.0
SUBSEQUENT_AV = 100.0
HEART_HP_BASE = 21997.729
HP_LINEAR_VALUES = {0: HEART_HP_BASE, 1: 26954.786}
ENERGY_CONFIG = {...}
```

### 8.2 data/characters.json

角色完整数据配置：

```json
{
  "name": "星",
  "element": "PHYSICAL",
  "energy_limit": 120,
  "stat": {
    "base_max_hp": 1200,
    "base_atk": 120,
    "base_def": 80,
    "base_spd": 105,
    "crit_rate": 0.05,
    "crit_dmg": 1.5,
    "energy_recovery_rate": 1.0,
    ...
  }
}
```

角色从JSON加载完整属性，包括所有Stat字段

### 8.3 data/skills.json

技能能量/战绩点/韧性削弱配置

### 8.4 data/enemies.json

敌人数据配置

---

## 9. 用户界面

### 9.1 TUI（文本界面）

命令行界面，支持两种日志级别：
- DAMAGE_ONLY：仅显示伤害相关事件
- FULL_DETAIL：显示所有事件，包含行动值和战绩点

### 9.2 GUI（图形界面）

Pygame 实现的图形界面，功能：
- 角色/敌人状态面板
- 战斗日志面板
- 控制按钮：Play/Pause、Step、Restart
- 速度滑块：0.5x - 5x

**快捷键**：
- 空格：暂停/继续
- S：单步执行
- R：重新开始
- ESC：退出

---

## 10. 项目结构

```
src/game/
├── __init__.py          # 导出核心类
├── models.py            # 数据模型（Character, Stat, Skill, BattleState等）
├── damage.py             # 伤害计算
├── battle.py            # 战斗引擎
├── skill.py             # 技能执行器
├── character.py         # 角色创建
├── effect.py            # 效果系统
├── break_system.py      # 击破系统
├── config/
│   ├── __init__.py
│   └── battle.py       # 战斗配置常量
├── gui.py               # Pygame 图形界面
└── tui.py               # 文本界面
```

---

## 11. 阶段计划

### 阶段 1：基础框架 ✅ 已完成
- [x] 数据模型（Character, Skill, Effect, Stat）
- [x] 伤害公式实现
- [x] 差异化防御公式
- [x] 基础战斗流程
- [x] 行动条系统
- [x] 能量/战绩点系统
- [x] 团队战绩点
- [x] 击杀/受击回能
- [x] 能量恢复效率
- [x] 元素伤害提高/抵抗
- [x] 韧性削弱系统
- [x] TUI 界面
- [x] GUI 界面

### 阶段 2：角色系统
- [ ] 角色创建与属性点分配
- [ ] 等级与成长
- [ ] 角色池

### 阶段 3：技能系统
- [ ] 技能定义与效果
- [ ] BUFF/DEBUFF 系统
- [ ] 追击系统完善

### 阶段 4：装备系统（规划中）
- [ ] 遗器
- [ ] 光锥

### 阶段 5：GUI完善（进行中）
- [ ] 玩家手动选择技能
- [ ] 动画效果
- [ ] 音效
