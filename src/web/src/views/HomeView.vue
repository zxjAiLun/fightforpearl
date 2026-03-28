<template>
  <div class="home">
    <div class="container">
      <h1 class="title">🌌 Fight For Pearl</h1>
      <p class="subtitle">模拟宇宙 · 差分宇宙</p>
      
      <div class="features">
        <div class="feature">
          <h3>🎴 抽卡式探索</h3>
          <p>像杀戮尖塔一样从手牌中选择</p>
        </div>
        <div class="feature">
          <h3>⚔️ 策略战斗</h3>
          <p>运用祝福、奇物、方程搭配</p>
        </div>
        <div class="feature">
          <h3>🌟 方程系统</h3>
          <p>多命途组合激活强力效果</p>
        </div>
      </div>
      
      <button class="start-btn" @click="startGame" :disabled="loading">
        {{ loading ? '启动中...' : '开始冒险' }}
      </button>
      
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'

const router = useRouter()
const store = useGameStore()

async function startGame() {
  const gameId = await store.startGame()
  if (gameId) {
    router.push(`/game/${gameId}`)
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.container {
  text-align: center;
  padding: 2rem;
}
.title {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(90deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.subtitle {
  font-size: 1.2rem;
  color: #888;
  margin-bottom: 3rem;
}
.features {
  display: flex;
  gap: 2rem;
  justify-content: center;
  margin-bottom: 3rem;
}
.feature {
  background: rgba(255,255,255,0.05);
  padding: 1.5rem;
  border-radius: 12px;
  width: 180px;
}
.feature h3 {
  margin-bottom: 0.5rem;
}
.feature p {
  font-size: 0.9rem;
  color: #aaa;
}
.start-btn {
  padding: 1rem 3rem;
  font-size: 1.2rem;
  background: linear-gradient(90deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: transform 0.2s;
}
.start-btn:hover:not(:disabled) {
  transform: scale(1.05);
}
.start-btn:disabled {
  opacity: 0.6;
}
.error {
  color: #ff6b6b;
  margin-top: 1rem;
}
</style>