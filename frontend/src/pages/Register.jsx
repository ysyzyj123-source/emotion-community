import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { registerStudent } from '../api/auth'

// 昵称显示宽度：中日韩宽字符按 2 计，其余按 1 计
function nicknameWidth(name) {
  let w = 0
  for (const ch of name) {
    const cp = ch.codePointAt(0)
    if ((cp >= 0x4e00 && cp <= 0x9fff) || (cp >= 0x3000 && cp <= 0x303f) ||
        (cp >= 0xff00 && cp <= 0xffef) || (cp >= 0x3040 && cp <= 0x30ff)) w += 2
    else w += 1
  }
  return w
}

export default function Register() {
  const navigate = useNavigate()
  const [nickname, setNickname] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!nickname || !password) {
      setError('请填写昵称和密码')
      return
    }
    if (nicknameWidth(nickname) > 12) {
      setError('昵称最长 12 个字符（最多 6 个汉字）')
      return
    }
    if (password.length < 6) {
      setError('密码长度至少 6 位')
      return
    }
    if (password !== confirm) {
      setError('两次输入的密码不一致')
      return
    }
    setLoading(true)
    try {
      await registerStudent({ nickname, password })
      navigate('/login', { state: { registered: true } })
    } catch (err) {
      setError(err?.response?.data?.msg || '注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>学生注册</h2>
        <form onSubmit={handleSubmit}>
          <input
            placeholder="昵称（最多 6 个汉字 / 12 个字符）"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
          />
          <input
            type="password"
            placeholder="密码（至少 6 位）"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <input
            type="password"
            placeholder="确认密码"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
          />
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? '注册中...' : '注册'}
          </button>
        </form>
        <p className="switch">
          已有账号？<Link to="/login">返回登录</Link>
        </p>
      </div>
    </div>
  )
}
