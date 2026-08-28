import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login } from '../api/auth'
import { saveAuth } from '../store/auth'

const ROLES = [
  { value: 'student', label: '学生' },
  { value: 'teacher', label: '心理辅导老师' },
  { value: 'admin', label: '系统管理员' },
]

export default function Login() {
  const navigate = useNavigate()
  const [role, setRole] = useState('student')
  const [account, setAccount] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!account || !password) {
      setError('请输入账号和密码')
      return
    }
    setLoading(true)
    try {
      const res = await login({ account, password, role })
      saveAuth(res.data)
      // 按角色跳转
      if (role === 'student') navigate('/')
      else if (role === 'teacher') navigate('/warning')
      else navigate('/admin')
    } catch (err) {
      setError(err?.response?.data?.msg || '登录失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>大学生情感互助系统</h2>
        <div className="role-tabs">
          {ROLES.map((r) => (
            <button
              key={r.value}
              type="button"
              className={role === r.value ? 'active' : ''}
              onClick={() => setRole(r.value)}
            >
              {r.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit}>
          <input
            placeholder={role === 'student' ? '昵称' : role === 'teacher' ? '工号' : '用户名'}
            value={account}
            onChange={(e) => setAccount(e.target.value)}
          />
          <input
            type="password"
            placeholder="密码"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? '登录中...' : '登录'}
          </button>
        </form>

        {role === 'student' && (
          <p className="switch">
            还没有账号？<Link to="/register">立即注册</Link>
          </p>
        )}
      </div>
    </div>
  )
}
