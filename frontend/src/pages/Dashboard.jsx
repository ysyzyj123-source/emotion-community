import { useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'
import { getSentimentTrend, getTopicDistribution, getPostStats } from '../api/dashboard'

export default function Dashboard() {
  const trendRef = useRef(null)
  const topicRef = useRef(null)
  const [stats, setStats] = useState({})

  useEffect(() => {
    getPostStats().then((res) => setStats(res.data)).catch(() => {})

    getSentimentTrend().then((res) => {
      const d = res.data
      const chart = echarts.init(trendRef.current)
      const labels = d.points.map((p) => `#${p.index}`)
      const values = d.points.map((p) => p.valence)
      chart.setOption({
        title: { text: '情感趋势（每帖情感分值，-10~+10，0中性）' },
        tooltip: { trigger: 'axis', formatter: (params) => {
          const i = params[0].dataIndex
          const p = d.points[i]
          return `第${p.index}帖<br/>时间：${p.time}<br/>情感分值：${p.valence}`
        } },
        xAxis: { type: 'category', data: labels },
        yAxis: { type: 'value', min: d.min, max: d.max },
        series: [{
          name: '情感分值',
          type: 'line',
          data: values,
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          markLine: {
            silent: true,
            symbol: 'none',
            data: [
              { yAxis: 0, lineStyle: { color: '#999', type: 'dashed' }, label: { formatter: '中性线', position: 'insideEndTop' } },
              { yAxis: d.avg, lineStyle: { color: '#e6a23c', type: 'solid' }, label: { formatter: `平均 ${d.avg}`, position: 'insideEndBottom' } },
            ],
          },
        }],
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
      <div style={{ display: 'flex', gap: 16, flexDirection: 'column' }}>
        <div ref={trendRef} style={{ width: '100%', height: 360, border: '1px solid #eee', borderRadius: 6 }} />
        <div ref={topicRef} style={{ width: 520, height: 300, border: '1px solid #eee', borderRadius: 6 }} />
      </div>
    </div>
  )
}
