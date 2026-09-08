/**
 * FilterPanel — Route, airline, cabin class, and travel date filters.
 * Fetches available routes and airlines from the backend.
 * Features dynamic Origin / Destination logic to prevent same-city selection
 * and auto-reset destination when origin changes.
 */
import { useState, useEffect } from 'react'
import { api } from '../api.js'

const CABIN_CLASSES = ['', 'Economy', 'Premium Economy', 'Business']

const IATA_NAMES = {
  DEL: 'Delhi (DEL)', BOM: 'Mumbai (BOM)', BLR: 'Bangalore (BLR)',
  HYD: 'Hyderabad (HYD)', MAA: 'Chennai (MAA)', CCU: 'Kolkata (CCU)',
  GOI: 'Goa (GOI)', JAI: 'Jaipur (JAI)', AMD: 'Ahmedabad (AMD)',
  COK: 'Kochi (COK)', ATQ: 'Amritsar (ATQ)', IXC: 'Chandigarh (IXC)',
  LKO: 'Lucknow (LKO)', GAU: 'Guwahati (GAU)', PAT: 'Patna (PAT)',
  SXR: 'Srinagar (SXR)', PNQ: 'Pune (PNQ)',
}

export default function FilterPanel({ filters, onFilterChange }) {
  const [routes, setRoutes] = useState([])
  const [airlines, setAirlines] = useState([])

  useEffect(() => {
    api.routes().then(setRoutes).catch(() => {})
    api.airlines().then(setAirlines).catch(() => {})
  }, [])

  const origins = [...new Set(routes.map((r) => r.origin))].sort()
  const destinations = routes
    .filter((r) => !filters.origin || r.origin === filters.origin)
    .map((r) => r.destination)
    .filter((v, i, a) => a.indexOf(v) === i && v !== filters.origin)
    .sort()

  const handleOriginChange = (e) => {
    const val = e.target.value
    const newDest = filters.destination === val ? '' : filters.destination
    onFilterChange({ ...filters, origin: val, destination: newDest })
  }

  const handleDestChange = (e) => {
    const val = e.target.value
    const newOrig = filters.origin === val ? '' : filters.origin
    onFilterChange({ ...filters, destination: val, origin: newOrig })
  }

  const set = (key) => (e) => onFilterChange({ ...filters, [key]: e.target.value })

  const reset = () =>
    onFilterChange({ origin: '', destination: '', airline: '', cabinClass: 'Economy', travelDate: '' })

  const todayStr = new Date().toISOString().split('T')[0]

  return (
    <div className="filter-panel">
      {/* Origin */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-origin">Origin</label>
        <div className="filter-input-wrap">
          <select id="filter-origin" className="filter-select" value={filters.origin || 'DEL'} onChange={handleOriginChange}>
            <option value="">All Origins</option>
            {origins.map((o) => (
              <option key={o} value={o}>{IATA_NAMES[o] || o}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Destination */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-destination">Destination</label>
        <div className="filter-input-wrap">
          <select id="filter-destination" className="filter-select" value={filters.destination || ''} onChange={handleDestChange}>
            <option value="">All Destinations</option>
            {destinations.map((d) => (
              <option key={d} value={d}>{IATA_NAMES[d] || d}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Airline */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-airline">Airline</label>
        <div className="filter-input-wrap">
          <select id="filter-airline" className="filter-select" value={filters.airline || ''} onChange={set('airline')}>
            <option value="">All Airlines</option>
            {airlines.map((a) => (
              <option key={a.name || a} value={a.name || a}>{a.name || a}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Travel Date */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-date">Travel Date</label>
        <div className="filter-input-wrap">
          <input
            id="filter-date"
            type="date"
            min={todayStr}
            className="filter-input"
            value={filters.travelDate || ''}
            onChange={set('travelDate')}
          />
        </div>
      </div>

      {/* Cabin Class */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-cabin">Cabin Class</label>
        <div className="filter-input-wrap">
          <select id="filter-cabin" className="filter-select" value={filters.cabinClass || 'Economy'} onChange={set('cabinClass')}>
            {CABIN_CLASSES.filter(Boolean).map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Apply Filters & Reset */}
      <div className="filter-actions">
        <button className="btn-apply-filters" onClick={() => onFilterChange({ ...filters })} id="filter-apply">
          <span>✈</span> Apply Filters
        </button>
        <button className="btn-filter-reset" onClick={reset} id="filter-reset" title="Reset all filters">
          ↺
        </button>
      </div>
    </div>
  )
}
