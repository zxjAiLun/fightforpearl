# Fight for Pearl

类崩坏星穹铁道回合制战斗游戏框架。

## 项目状态

进行中 — 阶段 1：基础框架搭建

## 架构

```
fightforpearl/
├── src/game/           # 游戏核心逻辑
│   ├── models.py       # 数据模型（角色、属性、技能）
│   ├── damage.py       # 伤害公式
│   ├── skill.py        # 技能系统
│   ├── battle.py       # 回合制战斗
│   └── tui.py          # 文字界面
├── tests/              # 测试
├── data/               # 角色/技能数据
└── docs/              # 设计文档
```

## 开发

```bash
uv sync                          # 安装依赖
uv run python -m src.game.tui    # 启动游戏
uv run pytest                   # 运行测试
```
