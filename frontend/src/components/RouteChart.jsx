/**
 * RouteChart — Top routes by average fare (grouped bar or bar chart).
 */
import Plot from 'react-plotly.js'

const PLOTLY_CONFIG = { displayModeBar: false, responsive: true }

export default function RouteChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="chart-card">
        <div className="chart-title">🗺 Route Fare Comparison</div>
        <div className="empty-state">No route data available</div>
      </div>
    )
  }

  const sorted = [...data].sort((a, b) => b.avg_fare - a.avg_fare).slice(0, 10)
  const routes = sorted.map((d) => d.route || `${d.origin}→${d.destination}`)
  const fares = sorted.map((d) => d.avg_fare)

  // Gradient colors from blue→purple based on rank
  const colors = routes.map((_, i) => {
    const t = i / Math.max(routes.length - 1, 1)
    const r = Math.round(59 + t * (139 - 59))
    const g = Math.round(130 + t * (92 - 130))
    const b = Math.round(246 + t * (246 - 246))
    return `rgba(${r},${g},${b},0.8)`
  })

  return (
    <div className="chart-card">
      <div className="chart-title">
        🗺 Route Fare Comparison
        <span className="chart-subtitle">top 10 routes by avg fare</span>
      </div>
      <Plot
        data={[
          {
            x: routes,
            y: fares,
            type: 'bar',
            marker: {
              color: fares,
              colorscale: [
                [0, 'rgba(16,185,129,0.8)'],
                [0.5, 'rgba(59,130,246,0.8)'],
                [1, 'rgba(139,92,246,0.8)'],
              ],
              line: { width: 0 },
            },
            text: fares.map((f) => `₹${Number(f).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`),
            textposition: 'outside',
            textfont: { color: '#94a3b8', size: 9 },
            hovertemplate: '<b>%{x}</b><br>Avg Fare: ₹%{y:,.0f}<extra></extra>',
          },
        ]}
        layout={{
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: { color: '#475569', family: 'Inter, sans-serif', size: 10 },
          margin: { t: 10, r: 10, b: 60, l: 60 },
          xaxis: {
            gridcolor: 'rgba(203, 213, 225, 0.4)',
            linecolor: 'rgba(203, 213, 225, 0.6)',
            tickangle: -35,
            tickfont: { size: 9, color: '#64748b' },
          },
          yaxis: {
            gridcolor: 'rgba(203, 213, 225, 0.4)',
            linecolor: 'rgba(203, 213, 225, 0.6)',
            tickprefix: '₹',
            tickfont: { size: 10, color: '#64748b' },
          },
          height: 260,
          showlegend: false,
        }}
        config={PLOTLY_CONFIG}
        style={{ width: '100%' }}
      />
    </div>
  )
}
