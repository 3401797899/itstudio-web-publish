import axios from 'axios'
import router from '../router'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  withCredentials: true, // 允许跨域请求携带 cookie
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 检查响应头中是否包含 Set-Cookie
    const setCookie = response.headers['set-cookie']
    if (setCookie) {
      // 如果是登录响应，确保 cookie 被正确设置
      if (response.config.url === '/api/login/') {
        document.cookie = setCookie
      }
    }
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未认证，跳转到登录页
          router.push('/login')
          break
        case 403:
          // 权限不足
          console.error('权限不足')
          break
        default:
          console.error('请求错误:', error.response.data)
      }
    }
    return Promise.reject(error)
  }
)

export default request

// 获取全局配置
export function getGlobalConfig() {
  return request({
    url: '/config/',
    method: 'get'
  })
}

// 更新全局配置
export function updateGlobalConfig(data) {
  return request({
    url: '/config/',
    method: 'post',
    data
  })
}