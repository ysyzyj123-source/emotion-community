import { Outlet, useNavigate, Link } from 'react-router-dom'
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
        <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }} className="app-title">Empathia · 大学生情感互助系统</Link>
        {auth && (
          <span className="app-user">
            <Link to="/profile" style={{ color: 'inherit' }}>{auth.name}（{auth.role === 'student' ? '学生' : auth.role === 'teacher' ? '老师' : '管理员'}）</Link>
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
