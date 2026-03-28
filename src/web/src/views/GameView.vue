<template>
  <div class="game" v-if="state">
    <!-- 顶部状态栏 -->
    <div class="top-bar">
      <div class="stat">
        <span class="label">层数</span>
        <span class="value">{{ state.floor }} / {{ state.total_floors }}</span>
      </div>
      <div class="stat">
        <span class="label">信用点</span>
        <span class="value">💰 {{ state.credits }}</span>
      </div>
      <div class="stat">
        <span class="label">祝福</span>
        <span class="value">{{ state.blessings.length }}</span>
      </div>
      <div class="stat">
        <span class="label">方程</span>
        <span class="value">{{ state.equations.length }}</span>
      </div>
      <div class="stat">
        <span class="label">血量</span>
        <span class="value">❤️ {{ state.player_hp }}/{{ state.player_max_hp }}</span>
      </div>
    </div>
    
    <!-- 卡组信息 -->
    <div class="deck-info">
      <span>抽牌堆: {{ state.deck_count }}</span>
      <span>弃牌堆: {{ state.discard_count }}</span>
    </div>
    
    <!-- 手牌区 -->
    <div class="hand-section">
      <h2>选择要打出的卡牌</h2>
      <div class="hand">
        <div
          v-for="(card, index) in state.hand"
          :key="card.id"
          class="card"
          :class="`rarity-${card.rarity}`"
          @click="selectCard(index)"
        >
          <div class="card-name">{{ card.name }}</div>
          <div class="card-type">{{ card.card_type }}</div>
          <div class="card-desc">{{ card.description }}</div>
        </div>
      </div>
    </div>
    
    <!-- 事件结果区 -->
    <div v-if="lastEvent" class="event-result">
      <h3>{{ lastEvent.event_name }}</h3>
      <p>{{ lastEvent.description }}</p>
      
      <!-- 祝福选择 -->
      <div v-if="pendingChoice && pendingChoice.length > 0" class="choice-panel">
        <p>选择一项：</p>
        <div class="choice-options">
          <button
            v-for="(opt, idx) in pendingChoice"
            :key="idx"
            @click="makeChoice(idx)"
          >
            {{ opt.name || opt }}
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <div v-else class="loading">
    <p>加载中...</p>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useGameStore } from '../stores/game'

const route = useRoute()
const store = useGameStore()

const state = computed(() => store.state)
const lastEvent = computed(() => store.lastEvent)
const pendingChoice = computed(() => store.pendingChoice)

onMounted(async () => {
  const gameId = route.params.id
  if (gameId) {
    store.gameId = gameId
    await store.fetchState()
  }
})

async function selectCard(index) {
  await store.playCard(index)
}

async function makeChoice(index) {
  if (store.lastEvent?.event_type === 'blessing') {
    await store.chooseBlessing(index)
  } else if (store.lastEvent?.event_type === 'curio') {
    await store.chooseCurio(index)
  }
}
</script>

<style scoped>
.game {
  min-height: 100vh;
  padding: 1rem;
}
.top-bar {
  display: flex;
  justify-content: space-around;
  background: rgba(255,255,255,0.05);
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
}
.stat {
  text-align: center;
}
.stat .label {
  display: block;
  font-size: 0.8rem;
  color: #888;
}
.stat .value {
  font-size: 1.2rem;
  font-weight: bold;
}
.deck-info {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1rem;
  color: #888;
}
.hand-section {
  text-align: center;
  margin-bottom: 2rem;
}
.hand-section h2 {
  margin-bottom: 1rem;
}
.hand {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.card {
  width: 180px;
  padding: 1rem;
  border-radius: 12px;
  background: rgba(255,255,255,0.08);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: left;
}
.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}
.card.rarity-1 { border: 2px solid #888; }
.card.rarity-2 { border: 2px solid #4fc3f7; }
.card.rarity-3 { border: 2px solid #ffb74d; }
.card-name {
  font-weight: bold;
  margin-bottom: 0.3rem;
}
.card-type {
  font-size: 0.8rem;
  color: #aaa;
  margin-bottom: 0.5rem;
}
.card-desc {
  font-size: 0.85rem;
  color: #ccc;
}
.event-result {
  background: rgba(255,255,255,0.05);
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
}
.choice-panel {
  margin-top: 1rem;
}
.choice-options {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 0.5rem;
}
.choice-options button {
  padding: 0.5rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.choice-options button:hover {
  background: #764ba2;
}
.loading {
  text-align: center;
  padding: 3rem;
}
</style>