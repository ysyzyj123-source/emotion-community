import { useEffect, useState } from 'react'
import { getProfile, getPointRecords } from '../api/user'

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [records, setRecords] = useState([])

  useEffect(() => {
    getProfile().then((res) => setProfile(res.data)).catch(() => {})
    getPointRecords().then((res) => setRecords(res.data.items || [])).catch(() => {})
  }, [])

  if (!profile) return <p>加载中...</p>

  return (
    <div>
      <h2>我的中心</h2>
      <p>昵称：<b>{profile.name}</b>　<span>等级：Lv.{profile.level}</span></p>
      <p style={{ fontSize: 16 }}>
        当前积分：<b style={{ color: '#4a90d9', fontSize: 22 }}>{profile.points}</b>
      </p>

      <h3 style={{ marginTop: 24 }}>积分明细</h3>
      {records.length === 0 && <p>暂无记录</p>}
      {records.map((r, i) => (
        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
          <span>{r.remark || r.action}</span>
          <span style={{ color: r.change > 0 ? '#2e8b57' : '#e74c3c', fontWeight: 700 }}>
            {r.change > 0 ? `+${r.change}` : r.change}
          </span>
        </div>
      ))}
    </div>
  )
}
