/**
 * AnomalyPanel — Displays detected fare anomalies.
 * Demo anomalies are clearly labelled DEMO.
 * Never presents fabricated data as live.
 */

const SEVERITY_ICONS = { CRITICAL: '🔴', HIGH: '🟠', MEDIUM: '🟡', LOW: '🔵' }

function AnomalyItem({ anomaly }) {
  const {
    origin,
    destination,
    observed_fare,
    expected_baseline,
    expected_low,
    expected_high,
    pct_deviation,
    severity,
    is_demo,
    airline,
    detected_at,
    route,
  } = anomaly

  const routeLabel = route || (origin && destination ? `${origin} → ${destination}` : '—')
  const icon = SEVERITY_ICONS[severity] || '⚠'
  const devSign = (pct_deviation || 0) >= 0 ? '+' : ''
  const devClass = (pct_deviation || 0) >= 0 ? 'positive' : 'negative'
  const severityClass = (severity || '').toLowerCase()

  return (
    <div className={`anomaly-item severity-${severityClass} ${is_demo ? 'is-demo' : ''}`}>
      <div className="anomaly-route">
        {icon} {routeLabel}
        {airline && <span style={{ fontWeight: 400, color: 'var(--text-muted)', fontSize: '0.8rem' }}> · {airline}</span>}
      </div>
      <div className="anomaly-fares">
        Observed:{' '}
        <strong style={{ color: 'var(--text-primary)' }}>
          ₹{Number(observed_fare || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
        </strong>
        <br />
        Expected:{' '}
        {expected_low && expected_high
          ? `₹${Number(expected_low).toLocaleString('en-IN', { maximumFractionDigits: 0 })} – ₹${Number(expected_high).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
          : `₹${Number(expected_baseline || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 6 }}>
        <span className={`anomaly-deviation ${devClass}`}>
          {devSign}{(pct_deviation || 0).toFixed(1)}%
        </span>
        <span className={`severity-badge ${severity || 'LOW'}`}>{severity || 'LOW'}</span>
        {anomaly.detection_method && (
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            via {anomaly.detection_method}
          </span>
        )}
      </div>
      {anomaly.explanation && (
        <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary, #94a3b8)', marginTop: 5, lineHeight: 1.3 }}>
          💡 {anomaly.explanation}
        </div>
      )}
      {detected_at && (
        <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', marginTop: 4 }}>
          {new Date(detected_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}
        </div>
      )}
    </div>
  )
}

export default function AnomalyPanel({ anomalies }) {
  return (
    <div className="card" id="anomaly-panel">
      <div className="card-title">⚠ Price Anomalies</div>
      {!anomalies || anomalies.length === 0 ? (
        <div className="empty-state" style={{ padding: '20px 0' }}>
          No anomalies detected
        </div>
      ) : (
        <div className="anomaly-list">
          {anomalies.map((a, i) => (
            <AnomalyItem key={a.id || i} anomaly={a} />
          ))}
        </div>
      )}
    </div>
  )
}
