import { Navigate } from 'react-router-dom'
import { isLoggedIn } from '../store/auth'

// 未登录则重定向到登录页
export default function RequireAuth({ children }) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />
  }
  return children
}
