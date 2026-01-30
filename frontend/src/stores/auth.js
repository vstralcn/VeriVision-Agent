import { defineStore } from 'pinia'
import { authAPI } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
  },

  actions: {
    async login(email, password) {
      const data = await authAPI.login(email, password)
      this.token = data.access_token
      localStorage.setItem('token', data.access_token)

      // Fetch user info
      const user = await authAPI.getMe()
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))

      return user
    },

    async register(email, password, nickname) {
      await authAPI.register(email, password, nickname)
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    async fetchUser() {
      if (this.token) {
        try {
          const user = await authAPI.getMe()
          this.user = user
          localStorage.setItem('user', JSON.stringify(user))
        } catch (error) {
          this.logout()
        }
      }
    }
  }
})
