import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const res = await authApi.login({ username, password })
    token.value = res.access_token
    user.value = res.user_info
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user_info))
    return res
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  async function fetchCurrentUser() {
    const res = await authApi.getMe()
    user.value = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
    return res.data
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    logout,
    fetchCurrentUser
  }
})