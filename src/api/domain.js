import request from './config'

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