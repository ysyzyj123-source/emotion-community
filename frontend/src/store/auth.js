// 简单认证状态管理（基于 localStorage）
export function saveAuth(data) {
  localStorage.setItem('token', data.token)
  localStorage.setItem('role', data.role)
  localStorage.setItem('name', data.name)
  localStorage.setItem('userId', data.user_id)
}

export function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('name')
  localStorage.removeItem('userId')
}

export function getAuth() {
  const token = localStorage.getItem('token')
  if (!token) return null
  return {
    token,
    role: localStorage.getItem('role'),
    name: localStorage.getItem('name'),
    userId: localStorage.getItem('userId'),
  }
}

export function isLoggedIn() {
  return !!localStorage.getItem('token')
}
