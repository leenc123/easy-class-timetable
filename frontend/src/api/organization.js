import api from './index'

export const organizationApi = {
  // 获取机构列表
  getList(params) {
    return api.get('/organizations', { params })
  },

  // 获取机构详情
  getDetail(id) {
    return api.get(`/organizations/${id}`)
  },

  // 创建机构
  create(data) {
    return api.post('/organizations', data)
  },

  // 更新机构
  update(id, data) {
    return api.put(`/organizations/${id}`, data)
  }
}