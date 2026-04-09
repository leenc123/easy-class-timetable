import api from './index'

export const cycleApi = {
  getList(params) {
    return api.get('/cycles', { params })
  },

  create(data) {
    return api.post('/cycles', data)
  },

  update(id, data) {
    return api.put(`/cycles/${id}`, data)
  },

  generateDates(id, endDate) {
    return api.post(`/cycles/${id}/generate-dates`, null, { params: { end_date: endDate } })
  },

  getDates(id, params) {
    return api.get(`/cycles/${id}/dates`, { params })
  },

  getTimeSlots(orgId) {
    return api.get('/cycles/time-slots', { params: { org_id: orgId } })
  },

  createTimeSlot(data) {
    return api.post('/cycles/time-slots', data)
  },

  updateTimeSlot(id, data) {
    return api.put(`/cycles/time-slots/${id}`, data)
  }
}

export const scheduleApi = {
  getList(params) {
    return api.get('/schedule', { params })
  },

  create(data) {
    return api.post('/schedule', data)
  },

  update(id, data) {
    return api.put(`/schedule/${id}`, data)
  },

  delete(id) {
    return api.delete(`/schedule/${id}`)
  },

  checkConflict(data) {
    return api.post('/schedule/check-conflict', data)
  },

  batchCreate(data) {
    return api.post('/schedule/batch-create', data)
  }
}

export const checkinApi = {
  create(data) {
    return api.post('/checkins', data)
  },

  getBySession(sessionId) {
    return api.get(`/checkins/session/${sessionId}`)
  }
}

export const exportApi = {
  exportPdf(params) {
    return api.get('/exports/pdf', { params, responseType: 'blob' })
  },

  exportExcel(params) {
    return api.get('/exports/excel', { params, responseType: 'blob' })
  }
}

export const viewApi = {
  getCalendar(params) {
    return api.get('/views/calendar', { params })
  },

  getTeacherSchedule(teacherId, params) {
    return api.get(`/views/teacher/${teacherId}`, { params })
  },

  getStudentSchedule(studentId, params) {
    return api.get(`/views/student/${studentId}`, { params })
  },

  getClassroomSchedule(classroomId, params) {
    return api.get(`/views/classroom/${classroomId}`, { params })
  }
}