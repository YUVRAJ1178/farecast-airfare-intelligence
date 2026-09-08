/**
 * AirlineChart — Horizontal bar chart comparing average fares by airline.
 */
import Plot from 'react-plotly.js'

const PLOTLY_CONFIG = { displayModeBar: false, responsive: true }

const AIRLINE_COLORS = {
  'IndiGo':       '#4f46e5',
  'Air India':    '#dc2626',
  'SpiceJet':     '#ea580c',
  'Vistara':      '#7c3aed',
  'AirAsia India':'#d97706',
  'Akasa Air':    '#0891b2',
  'Go First':     '#16a34a',
}

export default function AirlineChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="chart-card">
        <div className="chart-title">✈ Airline Fare Comparison</div>
        <div className="empty-state">No airline data available</div>
      </div>
    )
  }

  const sorted = [...data].sort((a, b) => a.avg_fare - b.avg_fare)
  const airlines = sorted.map((d) => d.airline)
  const fares = sorted.map((d) => d.avg_fare)
  const colors = airlines.map((a) => AIRLINE_COLORS[a] || '#3b82f6')

  return (
    <div className="chart-card">
      <div className="chart-title">
        ✈ Airline Fare Comparison
        <span className="chart-subtitle">avg economy fare</span>
      </div>
      <Plot
        data={[
          {
            x: fares,
            y: airlines,
            type: 'bar',
            orientation: 'h',
            marker: {
              color: colors,
              opacity: 0.85,
              line: { width: 0 },
            },
            text: fares.map((f) => `₹${Number(f).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`),
            textposition: 'outside',
            textfont: { color: '#94a3b8', size: 10 },
            hovertemplate: '<b>%{y}</b><br>Avg Fare: ₹%{x:,.0f}<extra></extra>',
          },
        ]}
        layout={{
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: { color: '#475569', family: 'Inter, sans-serif', size: 11 },
          margin: { t: 10, r: 80, b: 30, l: 110 },
          xaxis: {
            gridcolor: 'rgba(203, 213, 225, 0.4)',
            linecolor: 'rgba(203, 213, 225, 0.6)',
            tickprefix: '₹',
            tickfont: { size: 10, color: '#64748b' },
          },
          yaxis: {
            gridcolor: 'rgba(203, 213, 225, 0.4)',
            linecolor: 'rgba(203, 213, 225, 0.6)',
            tickfont: { size: 11, color: '#334155' },
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
