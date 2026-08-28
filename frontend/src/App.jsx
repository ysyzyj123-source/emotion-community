import { Outlet, useNavigate } from 'react-router-dom'
import { getAuth, clearAuth } from './store/auth'

export default function App() {
  const navigate = useNavigate()
  const auth = getAuth()

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  return (
    <div className="app">
      <header className="app-header">
        <span className="app-title">大学生情感互助系统</span>
        {auth && (
          <span className="app-user">
            {auth.name}（{auth.role === 'student' ? '学生' : auth.role === 'teacher' ? '老师' : '管理员'}）
            <button onClick={handleLogout}>退出</button>
          </span>
        )}
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}
