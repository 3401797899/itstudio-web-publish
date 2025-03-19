import request from './config'

// 获取配置文件预览
export function previewConfig() {
  return request({
    url: '/domains/preview/',
    method: 'get'
  })
}

// 写入配置文件
export function writeConfig() {
  return request({
    url: '/domains/write/',
    method: 'post'
  })
}

// 重启Cloudflared服务
export function restartCloudflared() {
  return request({
    url: '/domains/restart/',
    method: 'post'
  })
}

// 获取域名列表
export function getDomainList() {
  return request({
    url: '/domains/',
    method: 'get'
  })
}

// 添加域名
export function addDomain(data) {
  return request({
    url: '/domains/',
    method: 'post',
    data
  })
}

// 更新域名
export function updateDomain(id, data) {
  return request({
    url: `/domains/${id}/`,
    method: 'put',
    data
  })
}

// 删除域名
export function deleteDomain(id) {
  return request({
    url: `/domains/${id}/`,
    method: 'delete'
  })
}