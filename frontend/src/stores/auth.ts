import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const TOKEN_KEY = 'lab-pilot-token'
const USER_KEY = 'lab-pilot-user'

export interface AuthUser {
  user_id: number
  username: string
  email: string | null
  role: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<AuthUser | null>(JSON.parse(localStorage.getItem(USER_KEY) ?? 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function setAuth(newToken: string, newUser: AuthUser) {
    token.value = newToken
    user.value = newUser
    localStorage.setItem(TOKEN_KEY, newToken)
    localStorage.setItem(USER_KEY, JSON.stringify(newUser))
  }

  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return { token, user, isAuthenticated, isAdmin, setAuth, clearAuth }
})
