import request from './request'

export function getSentimentTrend(days = 7) {
  return request.get('/dashboard/sentiment-trend', { params: { days } })
}

export function getTopicDistribution() {
  return request.get('/dashboard/topic-distribution')
}

export function getPostStats() {
  return request.get('/dashboard/post-stats')
}
