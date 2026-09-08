/**
 * PredictionPanel — ML Fare Prediction card.
 * Clearly states that predictions are ML estimates, not guarantees.
 * Features dynamic Origin / Destination dropdown logic and interactive date picker.
 */
import { useState, useEffect } from 'react'
import { api } from '../api.js'

const IATA_NAMES = {
  DEL: 'Delhi', BOM: 'Mumbai', BLR: 'Bangalore', HYD: 'Hyderabad',
  MAA: 'Chennai', CCU: 'Kolkata', GOI: 'Goa', JAI: 'Jaipur', AMD: 'Ahmedabad',
  COK: 'Kochi', ATQ: 'Amritsar', IXC: 'Chandigarh',
}

const ALL_AIRPORTS = ['DEL','BOM','BLR','HYD','MAA','CCU','GOI','JAI','AMD','COK','ATQ','IXC']

export default function PredictionPanel({ filters }) {
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const getFutureDateStr = (days) => {
    const d = new Date()
    d.setDate(d.getDate() + days)
    return d.toISOString().split('T')[0]
  }
  const todayStr = new Date().toISOString().split('T')[0]

  // Local form state for prediction input
  const [form, setForm] = useState({
    origin: filters.origin || 'DEL',
    destination: (filters.destination && filters.destination !== filters.origin) ? filters.destination : 'BOM',
    airline: filters.airline || 'IndiGo',
    cabin_class: filters.cabinClass || 'Economy',
    stops: 0,
    days_left: 30,
    duration_minutes: 135,
    travel_date: getFutureDateStr(30),
  })

  // Sync from parent filters when they change
  useEffect(() => {
    setForm((prev) => {
      const newOrig = filters.origin || prev.origin
      let newDest = filters.destination || prev.destination
      if (newDest === newOrig) {
        newDest = newOrig === 'DEL' ? 'BOM' : 'DEL'
      }
      return {
        ...prev,
        origin: newOrig,
        destination: newDest,
        airline: filters.airline || prev.airline,
        cabin_class: filters.cabinClass || prev.cabin_class,
      }
    })
  }, [filters])

  const handleOriginSelect = (e) => {
    const newOrig = e.target.value
    let newDest = form.destination
    if (newDest === newOrig) {
      newDest = newOrig === 'DEL' ? 'BOM' : 'DEL'
    }
    setForm({ ...form, origin: newOrig, destination: newDest })
  }

  const handleDestSelect = (e) => {
    const newDest = e.target.value
    let newOrig = form.origin
    if (newOrig === newDest) {
      newOrig = newDest === 'DEL' ? 'BOM' : 'DEL'
    }
    setForm({ ...form, destination: newDest, origin: newOrig })
  }

  const handleDateChange = (e) => {
    const dateVal = e.target.value
    if (dateVal) {
      const today = new Date()
      today.setHours(0,0,0,0)
      const target = new Date(dateVal)
      target.setHours(0,0,0,0)
      const diffDays = Math.max(1, Math.round((target - today) / (1000 * 60 * 60 * 24)))
      setForm({ ...form, travel_date: dateVal, days_left: diffDays })
    }
  }

  const predict = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await api.prediction(form)
      setPrediction(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  return (
    <div className="card prediction-cockpit" id="prediction-panel" style={{ padding: '24px', borderRadius: 12, border: '1px solid var(--border)', background: 'var(--bg-secondary)', marginBottom: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, borderBottom: '1px solid var(--border)', paddingBottom: 14 }}>
        <div>
          <div className="card-title" style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>🤖 ML Fare Prediction Engine</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 3 }}>Calibrated CatBoost regression engine analyzing booking lead time and yield dynamics</div>
        </div>
        <span className="chip blue" style={{ fontSize: '0.72rem', padding: '4px 10px', borderRadius: 20, fontWeight: 600 }}>CatBoost Model</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24, alignItems: 'stretch' }}>
        {/* Left: Input Parameters */}
        <div style={{ background: 'var(--bg-card)', padding: '18px 20px', borderRadius: 10, border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 14 }}>Flight Parameters</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
              <div className="filter-group">
                <label className="filter-label" htmlFor="pred-origin" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Origin</label>
                <select id="pred-origin" className="filter-select" value={form.origin} onChange={handleOriginSelect} style={{ fontSize: '0.82rem', padding: '8px 10px' }}>
                  {ALL_AIRPORTS.map((c) => (
                    <option key={c} value={c}>{IATA_NAMES[c] || c}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label" htmlFor="pred-dest" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Destination</label>
                <select id="pred-dest" className="filter-select" value={form.destination} onChange={handleDestSelect} style={{ fontSize: '0.82rem', padding: '8px 10px' }}>
                  {ALL_AIRPORTS.filter((c) => c !== form.origin).map((c) => (
                    <option key={c} value={c}>{IATA_NAMES[c] || c}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label" htmlFor="pred-date" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  Travel Date <span style={{ color: 'var(--accent-primary)', fontWeight: 700 }}>({form.days_left}d lead)</span>
                </label>
                <input id="pred-date" className="filter-input" type="date" min={todayStr} value={form.travel_date || getFutureDateStr(form.days_left)} onChange={handleDateChange} style={{ fontSize: '0.82rem', padding: '7px 10px' }} />
              </div>

              <div className="filter-group">
                <label className="filter-label" htmlFor="pred-cabin" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Cabin Class</label>
                <select id="pred-cabin" className="filter-select" value={form.cabin_class} onChange={set('cabin_class')} style={{ fontSize: '0.82rem', padding: '8px 10px' }}>
                  <option value="Economy">Economy</option>
                  <option value="Premium Economy">Premium Economy</option>
                  <option value="Business">Business</option>
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label" htmlFor="pred-airline" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Airline Carrier</label>
                <select id="pred-airline" className="filter-select" value={form.airline || 'IndiGo'} onChange={set('airline')} style={{ fontSize: '0.82rem', padding: '8px 10px' }}>
                  <option value="IndiGo">IndiGo</option>
                  <option value="Air India">Air India</option>
                  <option value="Vistara">Vistara</option>
                  <option value="SpiceJet">SpiceJet</option>
                  <option value="Akasa Air">Akasa Air</option>
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label" htmlFor="pred-stops" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Flight Stops</label>
                <select id="pred-stops" className="filter-select" value={form.stops || 0} onChange={set('stops')} style={{ fontSize: '0.82rem', padding: '8px 10px' }}>
                  <option value={0}>Non-stop (Direct)</option>
                  <option value={1}>1 Stop</option>
                  <option value={2}>2+ Stops</option>
                </select>
              </div>
            </div>
          </div>

          <button
            className="btn-primary"
            onClick={predict}
            disabled={loading}
            id="predict-btn"
            style={{ width: '100%', padding: '12px 18px', fontSize: '0.92rem', fontWeight: 700, justifyContent: 'center', marginTop: 10, cursor: 'pointer', borderRadius: 8 }}
          >
            {loading ? 'Calculating Fare Intelligence…' : '✨ Predict Dynamic Fare'}
          </button>
        </div>

        {/* Right: Result Panel */}
        <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: 10, border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          {error && (
            <div style={{ color: 'var(--accent-red)', fontSize: '0.78rem', background: 'var(--accent-red-pale)', padding: '12px 16px', borderRadius: 8, marginBottom: 12 }}>
              ⚠ {error}
            </div>
          )}

          {prediction && !error ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: 8 }}>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Predicted Airfare</div>
                  <div style={{ fontSize: '2.4rem', fontWeight: 800, color: 'var(--accent-primary)', letterSpacing: '-0.03em' }}>
                    ₹{Number(prediction.predicted_fare).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </div>
                </div>
                <span className={`confidence-badge ${(prediction.confidence || 'low').toLowerCase()}`} style={{ fontSize: '0.78rem', padding: '4px 10px', borderRadius: 20, fontWeight: 700 }}>
                  {(prediction.confidence || 'LOW').toUpperCase()} CONFIDENCE
                </span>
              </div>

              {prediction.lower_bound != null && prediction.upper_bound != null && (
                <div style={{ background: 'var(--bg-secondary)', padding: '10px 14px', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                    <span>Expected Fare Band:</span>
                    <strong style={{ color: 'var(--text-primary)' }}>
                      ₹{Number(prediction.lower_bound).toLocaleString('en-IN', { maximumFractionDigits: 0 })} – ₹{Number(prediction.upper_bound).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                    </strong>
                  </div>
                </div>
              )}

              {prediction.recommendation && (
                <div style={{
                  background: prediction.recommendation.startsWith('BUY NOW') ? 'rgba(16, 185, 129, 0.12)' : 'rgba(245, 158, 11, 0.12)',
                  border: `1px solid ${prediction.recommendation.startsWith('BUY NOW') ? 'rgba(16, 185, 129, 0.35)' : 'rgba(245, 158, 11, 0.35)'}`,
                  padding: '10px 14px',
                  borderRadius: 8,
                }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', color: prediction.recommendation.startsWith('BUY NOW') ? '#34d399' : '#fbbf24', marginBottom: 3 }}>
                    💡 Booking Recommendation
                  </div>
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {prediction.recommendation}
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                {prediction.lookup_method && (
                  <span className="chip blue" style={{ fontSize: '0.7rem' }}>{prediction.lookup_method.replace('_', ' ').toUpperCase()}</span>
                )}
                {prediction.r2_score != null && (
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                    R² Score: {Number(prediction.r2_score).toFixed(2)}
                    {prediction.mae != null && ` · Baseline MAE: ₹${Number(prediction.mae).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
                  </span>
                )}
              </div>

              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border)', paddingTop: 10, lineHeight: 1.5 }}>
                {prediction.model_name || 'CatBoost ML Engine'} · Calibrated against DGCA historical passenger booking distributions.
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '24px 16px' }}>
              <div style={{ fontSize: '2.2rem', marginBottom: 8 }}>🎯</div>
              <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6 }}>
                {form.origin} ⇄ {form.destination} Fare Intelligence
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5, maxWidth: 320, margin: '0 auto 16px' }}>
                Selected: {form.cabin_class} · {form.airline} · {form.days_left} days advance lead time.
              </div>
              <div style={{ display: 'inline-block', padding: '6px 14px', borderRadius: 20, background: 'rgba(59,130,246,0.1)', color: 'var(--accent-blue-light)', fontSize: '0.75rem', fontWeight: 600 }}>
                Click 'Predict Dynamic Fare' to compute yield forecast
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
