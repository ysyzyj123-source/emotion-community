import axios from 'axios'

// 统一 axios 实例：后端通过 Vite 代理转发
const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截：附上 JWT
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截：统一解包 code/msg
request.interceptors.response.use(
  (resp) => resp.data,
  (err) => Promise.reject(err),
)

export default request
