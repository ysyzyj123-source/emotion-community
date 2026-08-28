import { useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'
import { getSentimentTrend, getTopicDistribution, getPostStats } from '../api/dashboard'

export default function Dashboard() {
  const trendRef = useRef(null)
  const topicRef = useRef(null)
  const [stats, setStats] = useState({})

  useEffect(() => {
    getPostStats().then((res) => setStats(res.data)).catch(() => {})

    getSentimentTrend(7).then((res) => {
      const d = res.data
      const chart = echarts.init(trendRef.current)
      chart.setOption({
        title: { text: '情感趋势（近7天）' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['正向', '负向', '中性'] },
        xAxis: { type: 'category', data: d.labels },
        yAxis: { type: 'value' },
        series: [
          { name: '正向', type: 'line', data: d['正向'], smooth: true },
          { name: '负向', type: 'line', data: d['负向'], smooth: true },
          { name: '中性', type: 'line', data: d['中性'], smooth: true },
        ],
      })
      window.addEventListener('resize', () => chart.resize())
    }).catch(() => {})

    getTopicDistribution().then((res) => {
      const d = res.data
      const chart = echarts.init(topicRef.current)
      chart.setOption({
        title: { text: '话题分布' },
        tooltip: { trigger: 'item' },
        legend: { bottom: 0 },
        series: [{
          type: 'pie',
          radius: ['40%', '65%'],
          data: d.labels.map((name, i) => ({ name, value: d.values[i] })),
        }],
      })
      window.addEventListener('resize', () => chart.resize())
    }).catch(() => {})
  }, [])

  return (
    <div>
      <h2>数据看板</h2>
      <div style={{ display: 'flex', gap: 20, marginBottom: 16 }}>
        <span>帖子：<b>{stats.posts || 0}</b></span>
        <span>回复：<b>{stats.replies || 0}</b></span>
        <span>用户：<b>{stats.users || 0}</b></span>
      </div>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <div ref={trendRef} style={{ width: 520, height: 320, border: '1px solid #eee', borderRadius: 6 }} />
        <div ref={topicRef} style={{ width: 400, height: 320, border: '1px solid #eee', borderRadius: 6 }} />
      </div>
    </div>
  )
}
