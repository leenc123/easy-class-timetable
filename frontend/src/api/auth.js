import api from './index'

export const authApi = {
  // 登录
  login(data) {
    return api.post('/auth/login', data)
  },

  // 获取当前用户信息
  getMe() {
    return api.get('/auth/me')
  },

  // 修改密码
  changePassword(data) {
    return api.post('/auth/change-password', data)
  },

  // 创建用户
  createUser(data) {
    return api.post('/auth/users', data)
  },

  // 更新用户
  updateUser(id, data) {
    return api.put(`/auth/users/${id}`, data)
  },

  // 删除用户
  deleteUser(id) {
    return api.delete(`/auth/users/${id}`)
  }
}