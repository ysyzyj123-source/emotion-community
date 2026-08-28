import { Outlet, useNavigate, Link } from 'react-router-dom'
import { getAuth, clearAuth } from './store/auth'

const ROLE_NAME = { student: '学生', teacher: '老师', admin: '管理员' }

export default function App() {
  const navigate = useNavigate()
  const auth = getAuth()
  const role = auth?.role

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  // 根据角色显示的导航项
  const navItems = role === 'teacher'
    ? [{ to: '/warning', label: '预警工作台' }, { to: '/dashboard', label: '数据看板' }]
    : role === 'admin'
      ? [{ to: '/dashboard', label: '数据看板' }] // 管理后台后续补
      : [{ to: '/', label: '社区' }, { to: '/profile', label: '我的' }]

  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }} className="app-title">Empathia · 大学生情感互助系统</Link>
        <nav style={{ display: 'flex', gap: 16 }}>
          {navItems.map((n) => (
            <Link key={n.to} to={n.to} style={{ color: 'inherit', textDecoration: 'none' }}>{n.label}</Link>
          ))}
        </nav>
        {auth && (
          <span className="app-user">
            <Link to="/profile" style={{ color: 'inherit' }}>{auth.name}（{ROLE_NAME[role]}）</Link>
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
