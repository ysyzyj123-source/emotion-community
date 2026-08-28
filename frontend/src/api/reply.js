import request from './request'

// 回复帖子
export function createReply(postId, content) {
  return request.post(`/reply/${postId}`, { content })
}

// 帖子回复列表
export function listReplies(postId) {
  return request.get(`/reply/post/${postId}`)
}
