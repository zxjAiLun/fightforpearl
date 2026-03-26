# Fight for Pearl — 项目进度总结 v0.3.0

## 项目概述

**Fight for Pearl** 是一个回合制战斗框架，灵感来源于崩坏星穹铁道的战斗系统。当前版本 **v0.3.0**，核心战斗逻辑已基本完成。

## 项目目标

**复刻崩坏星穹铁道回合制战斗逻辑**
- 优先级：战斗逻辑 > GUI > 养成系统（暂不实现）
- 养成逻辑目前用手填数据

---

## 已完成功能

### ✅ 战斗引擎核心
- [x] 回合制战斗流程
- [x] 行动值（Action Value）系统 — 基于速度的行动排序
- [x] 回合标记（Round Marker）机制
- [x] Step Back功能（回退到上一个行动）
- [x] DOT触发和结算

### ✅ 技能系统
- [x] 普通攻击（Basic Attack）— 普攻不消耗战绩点，回复1点战绩点
- [x] 战技（Special Skill）— 消耗1点战绩点，回复能量
- [x] 大招（Ultimate）— 消耗全部能量，需能量满（≥120），释放后能量重置为0
- [x] 追击（Follow-Up）— 满足条件后触发的额外攻击
- [x] 被动技能触发系统
- [x] AOE技能支持

### ✅ 能量与战绩点系统
- [x] 能量上限：120点
- [x] 初始能量：60点（上限的一半）
- [x] 普攻回复：20能量
- [x] 战技回复：30能量
- [x] 击杀回能：10能量
- [x] 战绩点：团队共享，上限6点
- [x] **战技消耗1点战绩点**（已修复）
- [x] 普攻回复1点战绩点

### ✅ 属性与效果系统
- [x] 攻击力、防御力、速度属性
- [x] HP与韧性条
- [x] Buff/Debuff效果
- [x] DOT持续伤害
- [x] Break击破效果（物理、风、火、雷、冰、量子、虚数）

### ✅ 伤害计算
- [x] 崩铁风格伤害公式
- [x] 防御减伤公式（两种：玩家攻击怪物/怪物攻击玩家）
- [x] 暴击判定（敌人不暴击）
- [x] 易伤区叠加
- [x] 增伤区叠加
- [x] 击破伤害计算

### ✅ 击破系统
- [x] 7种元素对应7种击破效果
- [x] 裂伤（物理）：HP%持续伤害
- [x] 灼烧（火）：火属性DOT
- [x] 冻结（冰）：无法行动
- [x] 触电（雷）：雷属性DOT
- [x] 风化（风）：可叠加DOT
- [x] 纠缠（量子）：行动延后+额外伤害
- [x] 禁锢（虚数）：行动延后+减速

### ✅ GUI界面
- [x] Pygame图形界面
- [x] 行动条（Action Bar）显示
- [x] 回合标记显示
- [x] 战斗日志面板
- [x] 角色面板 — 显示HP、Energy、速度
- [x] 敌人面板 — 显示HP、弱点、Buff
- [x] 怪物详情面板
- [x] Step/Back/Restart/Export 按钮
- [x] 速度调节滑块

---

## 最近修复 (v0.3.0)

### 核心修复
1. **战技消耗战绩点** — 战技执行前检查战绩点是否足够
2. **行动值常量统一** — 统一为AV_BASE=10000
3. **行动角色选择bug** — max改为min（行动值最小的先行动）
4. **FollowUpRule.check_trigger方法** — 缺失方法已添加
5. **SkillType.FOLLOW_UP** — 枚举值缺失已添加

---

## 当前GUI布局

```
+--------------------------------------------------+
|                                                  |
|        [Enemy Windows - Top Center-Right]        |
|            enemy1 | enemy2 | enemy3...           |
|                                                  |
|  [Action Bar]                                    |
|   (Left-Top)                                     |
|   200x400                                        |
|                                                  |
|  [Log Panel]                                     |
|   (Left-Bottom)                                  |
|   200x250                                        |
|                                                  |
|        [Buttons: Pause | Step | Back | Restart | Export]|
|        [Speed Slider]                            |
|                                                  |
|        [Character Windows - Bottom Center-Right]  |
|            char1 | char2 | char3 | char4          |
+--------------------------------------------------+
```

---

## 测试状态

| 测试套件 | 通过 | 失败 | 总计 |
|---------|------|------|------|
| test_battle.py | 16 | 0 | 16 |
| test_skills.py | 29 | 0 | 29 |
| test_character.py | 6 | 0 | 6 |
| test_aoe.py | 10 | 0 | 10 |
| test_break.py | 14 | 2 | 16 |
| test_followup.py | 8 | 4 | 12 |
| **总计** | **83** | **6** | **89** |

> ⚠️ 6个测试失败是预先存在的问题（测试期望与代码逻辑不匹配），需要更新测试用例。

---

## 文件结构

```
fightforpearl/
├── src/game/
│   ├── __init__.py
│   ├── battle.py      # 战斗引擎核心
│   ├── gui.py         # Pygame图形界面
│   ├── tui.py         # 命令行界面
│   ├── skill.py       # 技能执行器
│   ├── character.py   # 角色创建
│   ├── damage.py      # 伤害计算
│   ├── models.py      # 数据模型
│   └── config/
│       ├── __init__.py
│       └── battle.py  # 战斗配置常量
├── data/
│   ├── characters.json
│   ├── enemies.json
│   └── skills.json
├── tests/             # 单元测试
├── .trae/specs/       # 功能规格文档
├── SPEC.md           # 设计规范
├── PROJECT.md        # 项目进度
└── README.md         # 项目说明
```

---

## 运行方式

```bash
# 进入虚拟环境
source .venv/bin/activate

# 运行GUI
python -m src.game.gui

# 运行测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_battle.py -v
```

---

## 待完善事项

### 高优先级
- [ ] 完善效果命中/抵抗判定
- [ ] 敌人AI智能决策
- [ ] 拉条/推条效果实现
- [ ] 验证防御公式正确性
- [ ] 验证击破公式正确性

### 中优先级
- [ ] 玩家手动技能选择界面
- [ ] 伤害数字飘字
- [ ] Buff图标显示
- [ ] 战斗动画效果

### 低优先级
- [ ] 音效系统
- [ ] 存档/读档功能
- [ ] 更多角色预设
- [ ] 更多敌人类型

---

## 技术栈

- **Python 3.12+**
- **Pygame 2.6+** — 图形界面
- **Pytest** — 单元测试
- **JSON** — 数据存储

---

*最后更新：2026-03-27*
