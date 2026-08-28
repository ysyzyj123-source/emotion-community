import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getPost } from '../api/post'
import { listReplies, createReply } from '../api/reply'

export default function PostDetail() {
  const { id } = useParams()
  const [post, setPost] = useState(null)
  const [replies, setReplies] = useState([])
  const [replyContent, setReplyContent] = useState('')
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    getPost(id).then((res) => setPost(res.data)).catch((err) => setError(err?.response?.data?.msg || '加载失败'))
    listReplies(id).then((res) => setReplies(res.data.items || [])).catch(() => {})
  }

  useEffect(load, [id])

  const handleReply = async (e) => {
    e.preventDefault()
    setMsg('')
    if (!replyContent.trim()) return
    setSubmitting(true)
    try {
      await createReply(id, replyContent)
      setReplyContent('')
      setMsg('回复成功')
      load()
    } catch (err) {
      setError(err?.response?.data?.msg || '回复失败')
    } finally {
      setSubmitting(false)
    }
  }

  if (error && !post) return <p style={{ color: '#e74c3c' }}>{error}</p>
  if (!post) return <p>加载中...</p>

  return (
    <div>
      <p><Link to="/">← 返回列表</Link></p>
      <h2>{post.title}</h2>
      <p style={{ color: '#888', fontSize: 13 }}>
        作者：{post.author_nickname}　{post.create_time}　板块：{post.category}
      </p>
      <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>{post.content}</p>

      <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
        <span style={{ color: post.sentiment === '负向' ? '#e74c3c' : '#2e8b57' }}>情感：{post.sentiment}</span>
        <span style={{ color: post.emergency === '紧急' ? '#d33' : '#999' }}>紧急程度：{post.emergency}</span>
        {post.topic_label && <span>话题：{post.topic_label}</span>}
      </div>

      {post.is_warning && (
        <p style={{ color: '#d33', marginTop: 12, padding: 10, border: '1px solid #f2c1c1', borderRadius: 4 }}>
          ⚠️ 该内容已获得关注，请友好回应
        </p>
      )}

      <hr style={{ margin: '24px 0' }} />

      <h3>回复（{replies.length}）</h3>
      {replies.map((r) => (
        <div key={r.reply_id} style={{ border: '1px solid #eee', padding: 10, marginBottom: 8, borderRadius: 4 }}>
          <p style={{ margin: '0 0 4px' }}>{r.content}</p>
          <span style={{ fontSize: 12, color: '#999' }}>
            {r.author_nickname}　{r.create_time}
            {r.result && `　[${r.result}]`}
          </span>
        </div>
      ))}

      <form onSubmit={handleReply} style={{ marginTop: 16 }}>
        <textarea
          placeholder="写下你的回应..."
          value={replyContent}
          rows={3}
          onChange={(e) => setReplyContent(e.target.value)}
          style={{ width: '100%', padding: '8px 12px' }}
        />
        {msg && <p style={{ color: '#2e8b57' }}>{msg}</p>}
        {error && <p style={{ color: '#e74c3c' }}>{error}</p>}
        <button type="submit" disabled={submitting} style={{ marginTop: 8, padding: '8px 20px' }}>
          {submitting ? '提交中...' : '回复'}
        </button>
      </form>
    </div>
  )
}
