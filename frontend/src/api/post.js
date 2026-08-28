import request from './request'

// 发帖
export function createPost(data) {
  return request.post('/post', data)
}

// 帖子列表（支持板块/分页）
export function listPosts(params) {
  return request.get('/post/list', { params })
}

// 帖子详情
export function getPost(id) {
  return request.get(`/post/${id}`)
}

// 板块列表
export function listCategories() {
  return request.get('/post/categories')
}
