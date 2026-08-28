import request from './request'

// 学生注册
export function registerStudent(data) {
  return request.post('/auth/register', data)
}

// 登录（三类角色），data: { account, password, role }
export function login(data) {
  return request.post('/auth/login', data)
}
