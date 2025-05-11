import { reactive } from 'vue'
import { checkAuth as checkAuthApi, logout as logoutApi } from '../api/auth'

const state = reactive({
  isAuthenticated: false,
  loading: false
})

export const useAuth = () => {
  const checkAuth = async () => {
    try {
      await checkAuthApi()
      state.isAuthenticated = true
      return true
    } catch (error) {
      if (error.response?.status === 401) {
        state.isAuthenticated = false
        return false
      }
      // 其他错误可能是网络问题等，保持当前认证状态
      return state.isAuthenticated
    }
  }

  const logout = async () => {
    try {
      await logoutApi()
      state.isAuthenticated = false
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return {
    state,
    checkAuth,
    logout
  }
} 