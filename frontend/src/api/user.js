import request from './request'

// 当前用户信息（积分/等级）
export function getProfile() {
  return request.get('/user/profile')
}

// 积分明细
export function getPointRecords() {
  return request.get('/user/points/records')
}
