# Fight For Pearl - 星铁战斗模拟器

## 项目简介

基于崩坏：星穹铁道的回合制战斗游戏，包含完整的模拟宇宙玩法。

## 技术架构

- **游戏核心**: Python
- **API 层**: FastAPI
- **前端**: Vue 3 + Vite + Pinia

## 快速开始

### 安装依赖

```bash
cd fightforpearl
uv sync
```

### 启动后端 API

```bash
uv run uvicorn src.api.main:app --reload --port 8000
```

### 启动前端（另开终端）

```bash
cd src/web
npm install
npm run dev
```

访问 http://localhost:5173

### 仅运行 TUI 版本

```bash
uv run python -m src.game.simulated_universe.tui
```

### 运行测试

```bash
uv run pytest tests/ -v
```

## 项目结构

- `src/game/` - 游戏核心逻辑
- `src/api/` - FastAPI REST API
- `src/web/` - Vue 3 前端
- `data/` - 敌人/技能配置数据
- `tests/` - pytest 测试用例

## 核心功能

- AV 回合制战斗系统
- 追击/终结技优先级系统
- 模拟宇宙抽卡探索
- 祝福/奇物/方程增益系统
