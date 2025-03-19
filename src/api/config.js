import axios from 'axios'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 5000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 可以在这里添加token等认证信息
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
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