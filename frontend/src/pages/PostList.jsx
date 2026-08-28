import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listPosts, listCategories } from '../api/post'

const CAT_LABEL = { 正向: '#2e8b57', 负向: '#e74c3c', 中性: '#888' }
const EMERGENCY_LABEL = { 紧急: '#d33', 关注: '#e6a23c', 正常: '#999' }

export default function PostList() {
  const [cats, setCats] = useState([])
  const [activeCat, setActiveCat] = useState(0) // 0=全部
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    listCategories().then((res) => setCats(res.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = { per_page: 20 }
    if (activeCat) params.category_id = activeCat
    listPosts(params)
      .then((res) => setPosts(res.data.items || []))
      .catch(() => setPosts([]))
      .finally(() => setLoading(false))
  }, [activeCat])

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
        <button
          onClick={() => setActiveCat(0)}
          style={{ padding: '6px 14px', fontWeight: activeCat === 0 ? 700 : 400 }}
        >全部</button>
        {cats.map((c) => (
          <button
            key={c.id}
            onClick={() => setActiveCat(c.id)}
            style={{ padding: '6px 14px', fontWeight: activeCat === c.id ? 700 : 400 }}
          >{c.name}</button>
        ))}
        <Link to="/post/new" style={{ marginLeft: 'auto', padding: '6px 14px', background: '#4a90d9', color: '#fff', textDecoration: 'none', borderRadius: 4 }}>发帖</Link>
      </div>

      {loading && <p>加载中...</p>}
      {!loading && posts.length === 0 && <p>暂无帖子，点击"发帖"发布第一条吧</p>}

      {posts.map((p) => (
        <div key={p.post_id} style={{ border: '1px solid #eee', padding: 14, marginBottom: 12, borderRadius: 6 }}>
          <Link to={`/post/${p.post_id}`} style={{ textDecoration: 'none', color: '#333' }}>
            <h3 style={{ margin: '0 0 8px' }}>{p.title}</h3>
          </Link>
          <p style={{ color: '#666', margin: '0 0 8px' }}>{p.content}</p>
          <div style={{ display: 'flex', gap: 12, fontSize: 13, color: '#888' }}>
            <span style={{ color: CAT_LABEL[p.sentiment] || '#888' }}>情感：{p.sentiment}</span>
            <span style={{ color: EMERGENCY_LABEL[p.emergency] || '#888' }}>紧急：{p.emergency}</span>
            <span>{p.create_time}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
