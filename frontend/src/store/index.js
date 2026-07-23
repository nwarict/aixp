import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

axios.defaults.baseURL = API_URL

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin' || state.user?.role === 'superadmin'
  },

  actions: {
    async login(email, password) {
      const response = await axios.post('/v1/auth/login', { email, password })
      const { access_token, refresh_token } = response.data

      this.token = access_token
      this.refreshToken = refresh_token

      localStorage.setItem('token', access_token)
      localStorage.setItem('refreshToken', refresh_token)

      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      await this.fetchUser()
      return response.data
    },

    async fetchUser() {
      const response = await axios.get('/v1/auth/me')
      this.user = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      return response.data
    },

    logout() {
      this.token = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      delete axios.defaults.headers.common['Authorization']
    },

    initAuth() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
    }
  }
})

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarOpen: true,
    currentTenant: null,
    notifications: [],
    language: 'ar'
  }),

  actions: {
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen
    },
    setLanguage(lang) {
      this.language = lang
    },
    addNotification(notification) {
      this.notifications.push({
        id: Date.now(),
        ...notification
      })
      setTimeout(() => {
        this.notifications = this.notifications.filter(n => n.id !== notification.id)
      }, 5000)
    }
  }
})
