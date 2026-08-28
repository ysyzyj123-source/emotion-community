import request from './request'

export function listWarnings(params) {
  return request.get('/warning/list', { params })
}

export function warningStats() {
  return request.get('/warning/stats')
}

export function getWarning(id) {
  return request.get(`/warning/${id}`)
}

export function handleWarning(id, data) {
  return request.post(`/warning/${id}/handle`, data)
}
