import api from './axios'

export const authAPI = {
  login(email, password) {
    return api.post('/auth/login', { email, password })
  },

  register(email, password, nickname) {
    return api.post('/auth/register', { email, password, nickname })
  },

  getMe() {
    return api.get('/auth/me')
  }
}

export const detectionAPI = {
  uploadAndDetect(file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/detection/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  getHistory(skip = 0, limit = 20) {
    return api.get('/detection/history', { params: { skip, limit } })
  },

  getRecent(limit = 5) {
    return api.get('/detection/recent', { params: { limit } })
  },

  getDetection(id) {
    return api.get(`/detection/${id}`)
  },

  getTraceRecords(id) {
    return api.get(`/detection/${id}/trace`)
  },

  verifyCertification(id) {
    return api.post(`/detection/${id}/verify`)
  },

  getImageUrl(path) {
    return `http://localhost:8000/${path}`
  }
}

export const userAPI = {
  getProfile() {
    return api.get('/user/me')
  },

  updateProfile(data) {
    return api.put('/user/me', data)
  }
}

export const adminAPI = {
  getDashboardStats() {
    return api.get('/admin/dashboard/stats')
  },

  getUsers(skip = 0, limit = 50) {
    return api.get('/admin/users', { params: { skip, limit } })
  },

  toggleUserActive(userId) {
    return api.put(`/admin/users/${userId}/toggle-active`)
  },

  getAuditLogs(params = {}) {
    return api.get('/admin/audit-logs', { params })
  },

  getAuditLogDetail(logId) {
    return api.get(`/admin/audit-logs/${logId}`)
  }
}
