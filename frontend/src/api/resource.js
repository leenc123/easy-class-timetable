import api from './index'

export const classroomApi = {
  getList(params) {
    return api.get('/classrooms', { params })
  },

  getDetail(id) {
    return api.get(`/classrooms/${id}`)
  },

  create(data) {
    return api.post('/classrooms', data)
  },

  update(id, data) {
    return api.put(`/classrooms/${id}`, data)
  },

  delete(id) {
    return api.delete(`/classrooms/${id}`)
  }
}

export const teacherApi = {
  getList(params) {
    return api.get('/teachers', { params })
  },

  getDetail(id) {
    return api.get(`/teachers/${id}`)
  },

  create(data) {
    return api.post('/teachers', data)
  },

  update(id, data) {
    return api.put(`/teachers/${id}`, data)
  },

  delete(id) {
    return api.delete(`/teachers/${id}`)
  },

  getAvailability(id) {
    return api.get(`/teachers/${id}/availability`)
  },

  setAvailability(id, data) {
    return api.put(`/teachers/${id}/availability`, data)
  }
}

export const studentApi = {
  getList(params) {
    return api.get('/students', { params })
  },

  getDetail(id) {
    return api.get(`/students/${id}`)
  },

  create(data) {
    return api.post('/students', data)
  },

  update(id, data) {
    return api.put(`/students/${id}`, data)
  },

  delete(id) {
    return api.delete(`/students/${id}`)
  }
}

export const courseApi = {
  getList(params) {
    return api.get('/courses', { params })
  },

  getDetail(id) {
    return api.get(`/courses/${id}`)
  },

  create(data) {
    return api.post('/courses', data)
  },

  update(id, data) {
    return api.put(`/courses/${id}`, data)
  },

  delete(id) {
    return api.delete(`/courses/${id}`)
  },

  assignTeachers(id, data) {
    return api.post(`/courses/${id}/teachers`, data)
  },

  assignStudents(id, data) {
    return api.post(`/courses/${id}/students`, data)
  }
}