# Fight For Pearl - 星铁战斗模拟器

基于崩坏：星穹铁道的回合制战斗游戏，包含完整的模拟宇宙 roguelike 玩法。

---

## 快速开始

### 安装依赖

```bash
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

---

## 核心玩法

### AV 回合制战斗

游戏采用虚构变量（AV，Action Value）回合制系统：
- 速度决定行动顺序，速度越高越快行动
- 每次行动后 AV 重置，进入下一轮排序
- 击杀敌人触发**追击**，积累能量释放**终结技**

### 模拟宇宙 roguelike

探索随机生成的地图，收集祝福、奇物和方程，构建独特Build：

- **祝福**：提供属性加成和战斗效果
- **奇物**：被动效果，如伤害反弹、回合加成等
- **方程**：组合祝福触发额外协同效果

### 角色养成

- 命途设计：毁灭、巡猎、智识、同谐、虚无、存护、丰饶
- 光锥系统：装备提升角色属性和技能效果
- 遗器系统：提供额外词条和套装效果

---

## 游戏模式

| 模式 | 描述 |
|------|------|
| 模拟宇宙 | roguelike 探索，支持多难度 |
| 战斗演练 | 练习特定敌人机制 |
| 角色图鉴 | 查看所有角色/光锥/遗器数据 |

---

## 更新日志

见 [CHANGELOG.md](./CHANGELOG.md)
