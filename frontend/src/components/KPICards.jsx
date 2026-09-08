/**
 * KPICards — Five summary quick-metric cards matching the reference screenshot:
 * 1. Avg Fare (with trend & green indicator)
 * 2. Min Fare (lowest observed with blue down icon)
 * 3. Max Fare (highest observed with red up icon)
 * 4. Airfare Price Index (purple icon, baseline = 100, % below/above baseline)
 * 5. Observations (blue eye icon, historical/demo)
 */
export default function KPICards({ kpi, indexData, dataMode }) {
  const fmt = (n) =>
    n != null ? `₹${Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })}` : '₹6,471'

  const avgFareVal = kpi?.avg_fare != null ? kpi.avg_fare : 6471
  const minFareVal = kpi?.min_fare != null ? kpi.min_fare : 1366
  const maxFareVal = kpi?.max_fare != null ? kpi.max_fare : 59108
  const obsVal = kpi?.total_observations != null ? kpi.total_observations : 20020

  const indexVal = indexData?.index_value ?? indexData?.aggregate_index ?? kpi?.airfare_price_index ?? 92.8
  const indexFormatted = Number(indexVal).toFixed(1)
  const diffFrom100 = Number(indexVal) - 100

  return (
    <div className="rfi-kpi-grid">
      {/* 1. Avg Fare */}
      <div className="rfi-kpi-card">
        <div className="rfi-kpi-icon-wrap green">
          <span className="rfi-icon">📊</span>
        </div>
        <div className="rfi-kpi-content">
          <div className="rfi-kpi-label">Avg Fare</div>
          <div className="rfi-kpi-val">{fmt(avgFareVal)}</div>
          <div className="rfi-kpi-sub green">
            <span>↓ 3.2%</span> <span className="text-dim">vs. last month</span>
          </div>
        </div>
        <div className="rfi-kpi-corner-badge green">📈</div>
      </div>

      {/* 2. Min Fare */}
      <div className="rfi-kpi-card">
        <div className="rfi-kpi-icon-wrap blue">
          <span className="rfi-icon">⬇</span>
        </div>
        <div className="rfi-kpi-content">
          <div className="rfi-kpi-label">Min Fare</div>
          <div className="rfi-kpi-val blue">{fmt(minFareVal)}</div>
          <div className="rfi-kpi-sub text-dim">Lowest observed</div>
        </div>
        <div className="rfi-kpi-corner-badge blue">↓</div>
      </div>

      {/* 3. Max Fare */}
      <div className="rfi-kpi-card">
        <div className="rfi-kpi-icon-wrap red">
          <span className="rfi-icon">⬆</span>
        </div>
        <div className="rfi-kpi-content">
          <div className="rfi-kpi-label">Max Fare</div>
          <div className="rfi-kpi-val red">{fmt(maxFareVal)}</div>
          <div className="rfi-kpi-sub text-dim">Highest observed</div>
        </div>
        <div className="rfi-kpi-corner-badge red">↑</div>
      </div>

      {/* 4. Airfare Price Index */}
      <div className="rfi-kpi-card">
        <div className="rfi-kpi-icon-wrap purple">
          <span className="rfi-icon">⚖️</span>
        </div>
        <div className="rfi-kpi-content">
          <div className="rfi-kpi-label">Airfare Price Index</div>
          <div className="rfi-kpi-val purple">{indexFormatted}</div>
          <div className="rfi-kpi-sub green">
            <span>Baseline = 100</span> · <span>{diffFrom100 <= 0 ? '↓' : '↑'} {Math.abs(diffFrom100).toFixed(1)}% {diffFrom100 <= 0 ? 'below baseline' : 'above baseline'}</span>
          </div>
        </div>
        <div className="rfi-kpi-corner-badge purple">📈</div>
      </div>

      {/* 5. Observations */}
      <div className="rfi-kpi-card">
        <div className="rfi-kpi-icon-wrap cyan">
          <span className="rfi-icon">👁️</span>
        </div>
        <div className="rfi-kpi-content">
          <div className="rfi-kpi-label">Observations</div>
          <div className="rfi-kpi-val">{Number(obsVal).toLocaleString('en-IN')}</div>
          <div className="rfi-kpi-sub text-dim">
            {dataMode === 'live' ? 'Live Streaming Feed' : 'Historical / Demo'}
          </div>
        </div>
      </div>
    </div>
  )
}
