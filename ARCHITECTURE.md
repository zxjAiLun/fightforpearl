# 技术架构

## 技术栈

| 层级 | 技术 |
|------|------|
| 游戏核心 | Python |
| API 层 | FastAPI |
| 前端 | Vue 3 + Vite + Pinia |
| 测试 | pytest |
| 依赖管理 | uv |

## 目录结构

```
src/
├── game/                          # 游戏核心（Python）
│   ├── battle.py                  # 战斗主循环
│   ├── action_queue.py            # AV 行动队列
│   ├── character.py               # 角色实体
│   ├── character_skills.py         # 角色技能
│   ├── character_creator.py        # 角色创建器
│   ├── skill.py                   # 技能基础类
│   ├── damage.py                  # 伤害计算
│   ├── enemy_ai.py                # 敌人 AI
│   ├── enemy_skills.py            # 敌人技能
│   ├── modifier.py                # 战斗修饰符
│   ├── summon.py                  # 召唤物
│   ├── relic.py                   # 遗器系统
│   ├── lightcone_skills.py        # 光锥效果
│   ├── models.py                  # Pydantic 数据模型
│   ├── codex.py                   # 图鉴数据
│   ├── event_bus.py               # 事件总线
│   ├── config/                    # 游戏配置
│   ├── character_skills/           # 各角色技能实现
│   ├── simulated_universe/         # 模拟宇宙 roguelike
│   │   ├── universe.py            # 宇宙主循环
│   │   ├── map.py                # 地图生成
│   │   ├── events.py             # 随机事件
│   │   ├── blessings.py          # 祝福系统
│   │   ├── curios.py             # 奇物系统
│   │   ├── equations.py          # 方程系统
│   │   ├── rewards.py            # 奖励结算
│   │   ├── difficulty.py         # 难度配置
│   │   ├── run.py               # 单次探索流程
│   │   └── tui.py               # TUI 终端界面
│   ├── gui.py                    # GUI 主菜单
│   └── tui.py                    # 终端界面
├── api/                           # FastAPI 后端
│   ├── main.py                   # 应用入口
│   ├── models.py                 # API 数据模型
│   ├── game_manager.py           # 游戏状态管理
│   └── routers/
│       └── codex.py             # 图鉴路由
├── web/                          # Vue 3 前端
│   ├── index.html
│   ├── src/
│   └── ...                       # 前端源码
data/
├── characters.json               # 角色数据
├── enemies.json                 # 敌人数据
├── skills.json                  # 技能数据
├── lightcones/                  # 光锥数据
└── lightcone_effects.json       # 光锥特效
tests/
├── test_simulated_universe.py
└── ...
web_demo/
├── index.html                   # 战斗演示页面
└── ...
```

## 核心模块

### 战斗循环（battle.py）

采用 AV 轮询驱动：
1. 所有单位按 AV 排序
2. 最低 AV 者行动
3. 更新 AV 队列
4. 触发追击、buff 等后续结算
5. 重复直到战斗结束

### 事件总线（event_bus.py）

解耦战斗中各系统通信：
- 伤害结算后发布 `damage_dealt` 事件
- 击杀后发布 `enemy_killed` 事件
- 祝福/奇物订阅并响应事件

### 模拟宇宙（simulated_universe/）

roguelike 引擎：
- `map.py`：生成随机节点网络
- `blessings.py`：祝福效果与触发
- `equations.py`：祝福组合协同
- `run.py`：单次探索的状态机

## API 设计

### REST 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/codex/characters` | GET | 获取角色列表 |
| `/codex/lightcones` | GET | 获取光锥列表 |
| `/codex/enemies` | GET | 获取敌人列表 |
| `/game/start` | POST | 开始新游戏 |
| `/game/battle` | POST | 提交战斗操作 |

### WebSocket

支持实时战斗状态推送（规划中）。

## 测试

- `tests/test_simulated_universe.py`：模拟宇宙核心逻辑测试
- 使用 pytest 框架
- 218+ 测试用例覆盖
