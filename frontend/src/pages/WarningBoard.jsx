import { useEffect, useState } from 'react'
import { listWarnings, warningStats, getWarning, handleWarning } from '../api/warning'

const STATUS = { 0: '待处理', 1: '已处理', 2: '已下架' }
const STD_COLOR = { 0: '#e6a23c', 1: '#2e8b57', 2: '#999' }

export default function WarningBoard() {
  const [filter, setFilter] = useState('') // '' 全部, 0/1/2 状态筛选
  const [items, setItems] = useState([])
  const [stats, setStats] = useState({})
  const [selected, setSelected] = useState(null) // 当前详情
  const [note, setNote] = useState('')
  const [msg, setMsg] = useState('')

  const load = (status = filter) => {
    const params = status !== '' ? { status } : {}
    listWarnings(params).then((res) => setItems(res.data.items || [])).catch(() => {})
    warningStats().then((res) => setStats(res.data)).catch(() => {})
  }

  useEffect(() => { load() }, [filter])

  const openDetail = (id) => {
    getWarning(id).then((res) => { setSelected(res.data); setNote(''); setMsg('') }).catch(() => {})
  }

  const submit = async (status) => {
    if (!note.trim()) { setMsg('请填写处理记录'); return }
    try {
      await handleWarning(selected.warning_id, { note, status })
      setMsg('处理成功')
      setSelected(null)
      load()
    } catch (err) {
      setMsg(err?.response?.data?.msg || '处理失败')
    }
  }

  return (
    <div>
      <h2>预警工作台</h2>
      <div style={{ display: 'flex', gap: 20, marginBottom: 16 }}>
        <span>待处理：<b style={{ color: '#e6a23c' }}>{stats.pending || 0}</b></span>
        <span>已处理：<b style={{ color: '#2e8b57' }}>{stats.handled || 0}</b></span>
        <span>已下架：<b style={{ color: '#999' }}>{stats.taken_down || 0}</b></span>
        <span>总数：<b>{stats.total || 0}</b></span>
      </div>

      <div style={{ marginBottom: 12, display: 'flex', gap: 8 }}>
        {[['', '全部'], ['0', '待处理'], ['1', '已处理'], ['2', '已下架']].map(([v, label]) => (
          <button key={v} onClick={() => setFilter(v)} style={{ fontWeight: filter === v ? 700 : 400 }}>
            {label}
          </button>
        ))}
      </div>

      {items.length === 0 && <p>暂无预警记录</p>}
      {items.map((it) => (
        <div key={it.warning_id} style={{ border: '1px solid #eee', padding: 12, marginBottom: 8, borderRadius: 4, cursor: 'pointer' }}
             onClick={() => openDetail(it.warning_id)}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <b>{it.title}</b>
            <span style={{ color: STD_COLOR[it.status] }}>[{STATUS[it.status]}]</span>
          </div>
          <p style={{ color: '#666', margin: '4px 0' }}>{it.content}</p>
          <span style={{ fontSize: 12, color: '#999' }}>
            紧急程度：{it.emergency}　{it.create_time}
          </span>
        </div>
      ))}

      {selected && (
        <div style={{ marginTop: 20, padding: 16, border: '1px solid #4a90d9', borderRadius: 6 }}>
          <h3>处理预警 #{selected.warning_id}</h3>
          <p><b>{selected.post?.title}</b></p>
          <p style={{ whiteSpace: 'pre-wrap' }}>{selected.post?.content}</p>
          <p style={{ color: '#888' }}>情感：{selected.post?.sentiment}　紧急：{selected.emergency}</p>
          <textarea placeholder="填写处理记录..." rows={3} value={note}
                    onChange={(e) => setNote(e.target.value)} style={{ width: '100%', padding: 8 }} />
          {msg && <p style={{ color: '#e74c3c' }}>{msg}</p>}
          <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
            <button onClick={() => submit(1)}>标记已处理</button>
            <button onClick={() => submit(2)} style={{ background: '#d33', color: '#fff' }}>下架内容</button>
            <button onClick={() => setSelected(null)}>取消</button>
          </div>
        </div>
      )}
    </div>
  )
}
