# Fight for Pearl — 项目管理文档

## 当前阶段
**阶段 5：多目标/AOE技能系统** — 已完成

## 已完成功能

### 阶段 1：基础框架 ✅
- [x] 数据模型（Character, Skill, Effect, Stat）
- [x] 伤害公式（崩铁风格）
- [x] 回合制战斗引擎
- [x] TUI 界面
- [x] 测试套件

### 阶段 2：角色系统 + 技能系统 ✅
- [x] StatAllocator 属性点分配器（100点）
- [x] 预设角色（星/三月萤/丹恒/姬子/银狼/布洛妮娅/瓦尔特）
- [x] SkillExecutor（普攻×1.0 / 战技×1.5 / 大招×3.0）
- [x] 能量系统（上限3，每回合+1，大招需≥3）
- [x] 智能技能选择

### 阶段 3：属性系统重构 + 被动技能 ✅
- [x] 移除元素克制（崩铁无此机制）
- [x] 分离基础属性 vs 百分比加成 vs 固定值
- [x] 伤害公式分区（增伤区/易伤区/暴击区/击破区）
- [x] 被动1：战技增伤30% 2T
- [x] 被动2：大招加攻30% 2T

### 阶段 4：弱点击破系统 ✅
- [x] 敌人韧性值模型（toughness，削韧 → 击破）
- [x] 弱点元素系统（enemy.weakness_elements）
- [x] 物理/裂伤：按HP%持续伤害
- [x] 火/灼烧：火属性DOT
- [x] 冰/冻结：无法行动2回合
- [x] 雷/触电：雷属性DOT
- [x] 风/风化：可叠加DOT，最高3层
- [x] 量子/纠缠：行动延后30% + 下回合额外伤害
- [x] 虚数/禁锢：行动延后30% + 减速10%
- [x] BreakStatus 统一管理
- [x] 冻结跳过机制（can_act()）

### 阶段 5：多目标/AOE技能系统 ✅
- [x] Skill.target_count（1=单体，-1=全体，>1=指定数量）
- [x] Skill.aoe_multiplier（AOE倍率折扣）
- [x] SkillExecutor._effective_multiplier()（AOE时 base × 0.8）
- [x] Skill.is_aoe() / Skill.get_targets()
- [x] BattleEngine 多目标击破独立判定

## 测试总览
| 测试文件 | 数量 | 状态 |
|---------|------|------|
| test_battle.py | 16 | ✅ |
| test_character.py | 17 | ✅ |
| test_skills.py | 24 | ✅ |
| test_break.py | 15 | ✅ |
| test_aoe.py | 10 | ✅ |
| **总计** | **82** | **✅** |

## 待完成
- [ ] GUI 界面
- [ ] BUFF/DEBUFF 效果扩展
- [ ] 追击/反击机制
- [ ] 护盾系统
