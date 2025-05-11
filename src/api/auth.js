import request from './config'

export const login = async (password) => {
  const formData = new FormData()
  formData.append('password', password)
  const response = await request.post('/login/', formData)
  
  if (response.message === '登录成功') {
    return { success: true }
  } else {
    return { 
      success: false, 
      error: response.error || '未知错误' 
    }
  }
}

export const logout = () => {
  return request.post('/logout/')
}

export const checkAuth = () => {
  return request.get('/config/')
} 