import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getPost } from '../api/post'

export default function PostDetail() {
  const { id } = useParams()
  const [post, setPost] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getPost(id)
      .then((res) => setPost(res.data))
      .catch((err) => setError(err?.response?.data?.msg || '加载失败'))
  }, [id])

  if (error) return <p style={{ color: '#e74c3c' }}>{error}</p>
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
    </div>
  )
}
