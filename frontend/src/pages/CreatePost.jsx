import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createPost } from '../api/post'

export default function CreatePost() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!title || !content) {
      setError('请填写标题和正文')
      return
    }
    setLoading(true)
    try {
      const res = await createPost({ title, content })
      setResult(res.data)
      setTimeout(() => navigate('/'), 1500)
    } catch (err) {
      setError(err?.response?.data?.msg || '发布失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>发布帖子</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 12 }}>
          <input
            placeholder="标题（最长50字）"
            value={title}
            maxLength={50}
            onChange={(e) => setTitle(e.target.value)}
            style={{ width: '100%', padding: '8px 12px' }}
          />
        </div>
        <div style={{ marginBottom: 12 }}>
          <textarea
            placeholder="写下你的倾诉或分享..."
            value={content}
            rows={6}
            onChange={(e) => setContent(e.target.value)}
            style={{ width: '100%', padding: '8px 12px' }}
          />
        </div>
        {error && <p style={{ color: '#e74c3c' }}>{error}</p>}
        <button type="submit" disabled={loading} style={{ padding: '8px 20px' }}>
          {loading ? '发布中...' : '发布'}
        </button>
      </form>

      {result && (
        <div style={{ marginTop: 16, padding: 12, border: '1px solid #eee', borderRadius: 6 }}>
          <p>✅ 发布成功！智能分析结果：</p>
          <p>情感：{result.sentiment}　紧急程度：{result.emergency}</p>
          <p>话题：{result.topic_label}　板块：{result.category}</p>
          {result.warning && <p style={{ color: '#d33' }}>⚠️ 已识别为高风险内容，将推送老师跟进</p>}
        </div>
      )}
    </div>
  )
}
