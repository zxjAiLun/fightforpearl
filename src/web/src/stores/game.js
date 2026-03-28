import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

const API_BASE = '/api/game'

export const useGameStore = defineStore('game', {
  state: () => ({
    gameId: null,
    state: null,
    lastEvent: null,     // 最近的事件结果
    pendingChoice: null, // 等待玩家选择（祝福/奇物列表）
    loading: false,
    error: null,
  }),
  
  actions: {
    async startGame() {
      this.loading = true
      try {
        const res = await axios.post(`${API_BASE}/start`)
        this.gameId = res.data.game_id
        this.state = res.data.state
        return res.data.game_id
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
    
    async fetchState() {
      if (!this.gameId) return
      try {
        const res = await axios.get(`${API_BASE}/${this.gameId}`)
        this.state = res.data
      } catch (e) {
        this.error = e.message
      }
    },
    
    async playCard(index) {
      this.loading = true
      try {
        const res = await axios.post(`${API_BASE}/${this.gameId}/play`, {
          card_index: index
        })
        this.lastEvent = res.data
        // 检查是否需要选择祝福/奇物
        if (res.data.options) {
          this.pendingChoice = res.data.options
        } else {
          this.pendingChoice = null
        }
        await this.fetchState()
        return res.data
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
    
    async chooseBlessing(index) {
      try {
        const res = await axios.post(`${API_BASE}/${this.gameId}/choose-blessing`, null, {
          params: { index }
        })
        this.pendingChoice = null
        await this.fetchState()
        return res.data
      } catch (e) {
        this.error = e.message
      }
    },
    
    async chooseCurio(index) {
      try {
        const res = await axios.post(`${API_BASE}/${this.gameId}/choose-curio`, null, {
          params: { index }
        })
        this.pendingChoice = null
        await this.fetchState()
        return res.data
      } catch (e) {
        this.error = e.message
      }
    },
  },
})