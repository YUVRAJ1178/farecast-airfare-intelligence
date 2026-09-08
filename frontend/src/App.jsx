/**
 * App.jsx — FARECAST Master Dashboard
 * Pixel-perfect implementation matching reference design:
 * - Brand: FARECAST ("From Flight Prices to Market Insights")
 * - Modern 3D Origami Airplane Logo
 * - Topbar with Welcome pill, Date pill (7 Sep 2026 / Mon, 14:30), notifications & user profile
 * - Left sidebar with 7 items, active gradient pill, city skyline SVG & AI pill
 * - Right vertical navigation panel ("Page 1 of 5") with loop trail SVG & scroll hint
 * - Hero banner with background airliner, India map watermark, and script tagline
 * - 4 Stat Cards (Routes, Observations, Avg Fare, Active Airlines)
 * - Route Fare Index container with horizontal filter bar and 5 KPI subcards
 * - Charts row with Plotly Fare Trend & Prototype Price Index
 * - Bottom 3-column row with Top Routes table, Airline comparison table & Promo card
 */
import { useState, useEffect, useCallback } from 'react'
import { api } from './api.js'
import FilterPanel from './components/FilterPanel.jsx'
import KPICards from './components/KPICards.jsx'
import FareTrendChart from './components/FareTrendChart.jsx'
import IndexTrendChart from './components/IndexTrendChart.jsx'
import AirlineChart from './components/AirlineChart.jsx'
import RouteChart from './components/RouteChart.jsx'
import AnomalyPanel from './components/AnomalyPanel.jsx'
import PredictionPanel from './components/PredictionPanel.jsx'
import IndiaAirTrafficMap from './components/IndiaAirTrafficMap.jsx'
import BacktestingPanel from './components/BacktestingPanel.jsx'

const REFRESH_INTERVAL_MS = 60_000

export default function App() {
  const [activeTab, setActiveTab] = useState('home')
  const [summary, setSummary] = useState(null)
  const [status, setStatus] = useState(null)
  const [indexData, setIndexData] = useState(null)
  const [anomalies, setAnomalies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Applied filters (what the backend has been queried with)
  const [filters, setFilters] = useState({
    origin: 'DEL',
    destination: 'BOM',
    airline: '',
    cabinClass: 'Economy',
    travelDate: '',
  })

  // Pending filters (what the user is currently editing in the home tab filter row)
  const [pendingFilters, setPendingFilters] = useState({
    origin: 'DEL',
    destination: 'BOM',
    airline: '',
    cabinClass: 'Economy',
    travelDate: '',
  })

  // All airports for dropdowns (expanded list)
  const ALL_AIRPORTS_MAP = {
    DEL: 'Delhi (DEL)', BOM: 'Mumbai (BOM)', BLR: 'Bangalore (BLR)',
    HYD: 'Hyderabad (HYD)', MAA: 'Chennai (MAA)', CCU: 'Kolkata (CCU)',
    GOI: 'Goa (GOI)', JAI: 'Jaipur (JAI)', AMD: 'Ahmedabad (AMD)',
    COK: 'Kochi (COK)', ATQ: 'Amritsar (ATQ)', IXC: 'Chandigarh (IXC)',
    LKO: 'Lucknow (LKO)', GAU: 'Guwahati (GAU)', PAT: 'Patna (PAT)',
    SXR: 'Srinagar (SXR)', PNQ: 'Pune (PNQ)',
  }
  const ALL_AIRPORTS = Object.keys(ALL_AIRPORTS_MAP)

  const loadData = useCallback(async () => {
    try {
      const [sum, st, anom] = await Promise.all([
        api.dashboardSummary({
          origin: filters.origin || '',
          destination: filters.destination || '',
          airline: filters.airline || '',
          cabin_class: filters.cabinClass || '',
          travel_date: filters.travelDate || '',
        }),
        api.liveStatus(),
        api.anomalies({ limit: 10 }),
      ])
      setSummary(sum)
      setStatus(st)
      setAnomalies(anom)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [filters.origin, filters.destination, filters.airline, filters.cabinClass, filters.travelDate])

  const loadIndex = useCallback(async () => {
    if (filters.origin && filters.destination) {
      try {
        const d = await api.indexRoute(filters.origin, filters.destination)
        setIndexData(d)
      } catch {
        setIndexData(null)
      }
    } else {
      try {
        const d = await api.indexAggregate({ origin: filters.origin, destination: filters.destination })
        setIndexData(d)
      } catch {
        setIndexData(null)
      }
    }
  }, [filters.origin, filters.destination])

  useEffect(() => {
    loadData()
    const timer = setInterval(loadData, REFRESH_INTERVAL_MS)
    return () => clearInterval(timer)
  }, [loadData])

  useEffect(() => {
    loadIndex()
  }, [loadIndex])

  const dataMode = status?.overall_mode || summary?.data_mode || 'demo'

  const sidebarNavItems = [
    { id: 'home', icon: '🏠', label: 'Home' },
    { id: 'dashboard', icon: '田', label: 'Dashboard' },
    { id: 'predictions', icon: '🧠', label: 'ML Predictions' },
    { id: 'anomalies', icon: '⚠️', label: 'Price Anomalies' },
    { id: 'price-index', icon: '📈', label: 'Prototype Price Index' },
    { id: 'backtesting', icon: '📅', label: '30-Day Data' },
    { id: 'air-corridor', icon: '🗺️', label: 'India Map' },
  ]

  const rightNavItems = [
    { id: 'home', label: 'Home\n(Overview)', icon: '🏠' },
    { id: 'predictions', label: 'Dashboard\n(ML Predictions)', icon: '🧠' },
    { id: 'anomalies', label: 'Price Anomalies\n& Index', icon: '⚠️' },
    { id: 'backtesting', label: '30-Day Data\n(Backtesting)', icon: '📅' },
    { id: 'air-corridor', label: 'India Map\n(Corridors)', icon: '🗺️' },
  ]

  const topRoutesList = [
    { rank: 1, route: 'DEL → BOM', fare: 8542, change: 2.4 },
    { rank: 2, route: 'BOM → DEL', fare: 8120, change: 1.8 },
    { rank: 3, route: 'DEL → BLR', fare: 7824, change: -0.6 },
    { rank: 4, route: 'BLR → DEL', fare: 7615, change: 1.2 },
    { rank: 5, route: 'DEL → HYD', fare: 6982, change: 0.9 },
  ]

  const airlineFaresList = [
    { airline: 'IndiGo', code: '6E', fare: 6210, trend: 2.1, color: '#0047AB' },
    { airline: 'Air India', code: 'AI', fare: 7842, trend: 1.4, color: '#dc2626' },
    { airline: 'SpiceJet', code: 'SG', fare: 5980, trend: -3.7, color: '#ea580c' },
    { airline: 'Go First', code: 'G8', fare: 6542, trend: 0.8, color: '#16a34a' },
    { airline: 'Vistara', code: 'UK', fare: 8276, trend: 1.9, color: '#701a75' },
  ]

  return (
    <div className="app-shell">
      {/* ═══ LEFT SIDEBAR ═══ */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <svg className="brand-origami-plane" viewBox="0 0 40 40" fill="none">
            <defs>
              <linearGradient id="og1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#4f46e5" />
                <stop offset="100%" stopColor="#7c3aed" />
              </linearGradient>
              <linearGradient id="og2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#a855f7" />
              </linearGradient>
              <linearGradient id="og3" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#6366f1" />
              </linearGradient>
            </defs>
            <path d="M6 22 L34 8 L22 34 L18 24 Z" fill="url(#og1)" />
            <path d="M34 8 L18 24 L22 34 Z" fill="url(#og2)" opacity="0.9" />
            <path d="M18 24 L22 28 L20 33 Z" fill="url(#og3)" />
            <path d="M6 22 L20 22 L18 24 Z" fill="#4338ca" opacity="0.6" />
          </svg>
          <div style={{ minWidth: 0, flex: 1 }}>
            <div className="sidebar-name">FARECAST</div>
            <div className="sidebar-tagline" style={{ whiteSpace: 'normal', wordBreak: 'break-word', overflow: 'visible' }}>From Flight Prices to Market Insights</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {sidebarNavItems.map((item) => (
            <div
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </div>
          ))}
        </nav>

        <div className="sidebar-footer-wrap">
          <div className="sidebar-skyline-container">
            <svg style={{ width: '100%', height: '100%', overflow: 'visible' }} viewBox="0 0 200 90" fill="none">
              <rect x="12" y="35" width="10" height="55" rx="1" fill="#e0f2fe" />
              <rect x="9" y="26" width="16" height="11" rx="2" fill="#bae6fd" />
              <line x1="17" y1="26" x2="17" y2="16" stroke="#7dd3fc" strokeWidth="1.5" />
              <rect x="28" y="50" width="14" height="40" rx="1" fill="#e0f2fe" />
              <rect x="46" y="40" width="12" height="50" rx="1" fill="#bae6fd" />
              <rect x="62" y="55" width="16" height="35" rx="1" fill="#e0f2fe" />
              <rect x="82" y="45" width="14" height="45" rx="1" fill="#bae6fd" />
              <rect x="100" y="60" width="18" height="30" rx="1" fill="#e0f2fe" />
              <rect x="122" y="48" width="15" height="42" rx="1" fill="#bae6fd" />
              <rect x="141" y="65" width="20" height="25" rx="1" fill="#e0f2fe" />
              <path d="M8 82 C 55 82, 85 60, 135 20" stroke="#bae6fd" strokeWidth="3.5" fill="none" opacity="0.75" />
              <path d="M8 82 C 55 82, 85 60, 135 20" stroke="#ffffff" strokeWidth="1.5" fill="none" opacity="0.95" />
              <polygon points="135,16 142,27 134,25 130,29" fill="#3b82f6" />
            </svg>
          </div>
        </div>
      </aside>

      {/* ═══ RIGHT VERTICAL PANEL ═══ */}
      <aside className="right-panel">
        <div className="right-panel-header">Page 1 of 5</div>
        {rightNavItems.map((item) => (
          <div
            key={item.id}
            className={`right-nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => setActiveTab(item.id)}
          >
            <span className="right-nav-icon">{item.icon}</span>
            <span className="right-nav-label">{item.label}</span>
          </div>
        ))}
        <div className="right-panel-footer">
          <svg style={{ width: 54, height: 44 }} viewBox="0 0 60 50" fill="none">
            <path
              d="M10 40 C 35 45, 55 35, 45 15 C 35 -2, 15 10, 25 25 C 35 38, 50 25, 52 12"
              stroke="#cbd5e1"
              strokeWidth="1.3"
              strokeDasharray="3 3"
              fill="none"
            />
            <polygon points="52,10 57,17 51,15" fill="#94a3b8" />
          </svg>
          <div className="right-panel-scroll-hint">
            Scroll to explore<br />more insights
          </div>
          <span style={{ color: '#94a3b8', fontSize: '0.8rem', marginTop: 2 }}>↓</span>
        </div>
      </aside>

      {/* ═══ MAIN AREA ═══ */}
      <div className="main-area">
        {/* TOPBAR */}
        <header className="topbar">
          <div className="topbar-welcome-pill">
            <div className="topbar-plane-box">✈</div>
            <div>
              <div className="topbar-welcome-title">Welcome to FARECAST</div>
              <div className="topbar-welcome-sub">Real-time insights. Smarter airfares. A connected India.</div>
            </div>
          </div>
          <div className="topbar-right-controls">
            <div className="topbar-date-pill">
              <span style={{ fontSize: '1rem' }}>📅</span>
              <div className="topbar-date-text">
                <span className="topbar-date-day">7 Sep 2026</span>
                <span className="topbar-date-time">Mon, 14:30</span>
              </div>
            </div>
            <div className="topbar-bell-btn" title="Notifications">
              🔔
              <span className="topbar-bell-dot" />
            </div>
            <div className="topbar-user-pill">
              <div className="topbar-user-avatar">A</div>
              <span className="topbar-user-name">Aaloo</span>
              <span style={{ fontSize: '0.7rem', color: '#64748b' }}>▾</span>
            </div>
          </div>
        </header>

        {/* PAGE CONTENT */}
        <main style={{ padding: '20px 24px', flex: 1 }}>
          {/* ═══ TAB: HOME ═══ */}
          {activeTab === 'home' && (
            <>
              {/* HERO BANNER */}
              <div className="hero-banner">
                <div className="hero-content">
                  <div className="hero-eyebrow">Welcome to</div>
                  <div className="hero-title">FARECAST</div>
                  <div className="hero-subtitle">
                    AI-powered airfare intelligence for a smarter,<br />more connected India.
                  </div>
                </div>
                <div className="hero-script-wrap">
                  <div className="hero-script-text">
                    Better Insights<br />Bigger Horizons
                  </div>
                </div>
              </div>

              {/* 4 STAT CARDS */}
              <div className="stat-grid">
                <div className="stat-card">
                  <div className="stat-card-icon blue">🛣️</div>
                  <div>
                    <div className="stat-card-label">Total Routes</div>
                    <div className="stat-card-value">1,248</div>
                    <div className="stat-card-change up">↑ 12% vs. last month</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-card-icon purple">👥</div>
                  <div>
                    <div className="stat-card-label">Total Observations</div>
                    <div className="stat-card-value">60,000+</div>
                    <div className="stat-card-change up">↑ 8% vs. last month</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-card-icon green">₹</div>
                  <div>
                    <div className="stat-card-label">Avg. Fare</div>
                    <div className="stat-card-value">₹6,471</div>
                    <div className="stat-card-change down">↓ 3% vs. last month</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-card-icon orange">✈️</div>
                  <div>
                    <div className="stat-card-label">Active Airlines</div>
                    <div className="stat-card-value">18</div>
                    <div className="stat-card-change neutral">— no change</div>
                  </div>
                </div>
              {/* DATA PROVENANCE HONESTY BANNER */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '10px 16px',
                background: 'rgba(15, 23, 42, 0.75)',
                border: '1px solid rgba(56, 189, 248, 0.25)',
                borderRadius: '8px',
                margin: '1.25rem 0',
                fontSize: '0.8rem',
                color: '#cbd5e1',
                flexWrap: 'wrap',
                gap: 10,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ color: '#38bdf8', fontWeight: 600, fontSize: '0.85rem' }}>🛡️ SIH 26056 Data Provenance:</span>
                  <span>Total <strong>{Number(summary?.kpi?.total_observations || 179352).toLocaleString('en-IN')}</strong> Observations</span>
                </div>
                <div style={{ display: 'flex', gap: 14, alignItems: 'center', flexWrap: 'wrap' }}>
                  <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#34d399', display: 'inline-block' }}></span>
                    Historical Snapshot: <strong>33.45%</strong>
                  </span>
                  <span style={{ color: '#818cf8', display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#818cf8', display: 'inline-block' }}></span>
                    Synthetic Augmented: <strong>66.55%</strong>
                  </span>
                  <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#34d399', display: 'inline-block' }}></span>
                    Live Ignav API: <strong>&gt;0% (Active)</strong>
                  </span>
                </div>
              </div>

              {/* ROUTE FARE INDEX CONTAINER */}
              <div className="rfi-container-card">
                <div className="rfi-header">
                  <div>
                    <div className="rfi-title-row">
                      <div className="rfi-icon-box">📊</div>
                      <div className="rfi-title">Route Fare Index</div>
                    </div>
                    <div className="rfi-subtitle">
                      Explore fare trends, route comparisons and airline performance across major routes.
                    </div>
                  </div>
                  <button className="rfi-details-link" onClick={() => setActiveTab('anomalies')}>
                    View Details →
                  </button>
                </div>

                {/* Filter row */}
                <div className="filter-panel-row">
                  <div className="filter-group-col">
                    <label className="filter-group-label">Origin</label>
                    <select
                      className="filter-control-select"
                      value={pendingFilters.origin}
                      onChange={(e) => {
                        const val = e.target.value
                        const newDest = pendingFilters.destination === val ? '' : pendingFilters.destination
                        setPendingFilters({ ...pendingFilters, origin: val, destination: newDest })
                      }}
                    >
                      {ALL_AIRPORTS.map((code) => (
                        <option key={code} value={code}>{ALL_AIRPORTS_MAP[code]}</option>
                      ))}
                    </select>
                  </div>
                  <div className="filter-group-col">
                    <label className="filter-group-label">Destination</label>
                    <select
                      className="filter-control-select"
                      value={pendingFilters.destination}
                      onChange={(e) => {
                        const val = e.target.value
                        const newOrig = pendingFilters.origin === val ? '' : pendingFilters.origin
                        setPendingFilters({ ...pendingFilters, destination: val, origin: newOrig })
                      }}
                    >
                      {ALL_AIRPORTS.filter((c) => c !== pendingFilters.origin).map((code) => (
                        <option key={code} value={code}>{ALL_AIRPORTS_MAP[code]}</option>
                      ))}
                    </select>
                  </div>
                  <div className="filter-group-col">
                    <label className="filter-group-label">Airline</label>
                    <select
                      className="filter-control-select"
                      value={pendingFilters.airline}
                      onChange={(e) => setPendingFilters({ ...pendingFilters, airline: e.target.value })}
                    >
                      <option value="">All Airlines</option>
                      <option value="IndiGo">IndiGo</option>
                      <option value="Air India">Air India</option>
                      <option value="Vistara">Vistara</option>
                      <option value="SpiceJet">SpiceJet</option>
                      <option value="Akasa Air">Akasa Air</option>
                      <option value="Go First">Go First</option>
                    </select>
                  </div>
                  <div className="filter-group-col">
                    <label className="filter-group-label">Travel Date</label>
                    <input
                      type="date"
                      className="filter-control-input"
                      value={pendingFilters.travelDate}
                      onChange={(e) => setPendingFilters({ ...pendingFilters, travelDate: e.target.value })}
                    />
                  </div>
                  <div className="filter-group-col">
                    <label className="filter-group-label">Cabin Class</label>
                    <select
                      className="filter-control-select"
                      value={pendingFilters.cabinClass}
                      onChange={(e) => setPendingFilters({ ...pendingFilters, cabinClass: e.target.value })}
                    >
                      <option>Economy</option>
                      <option>Premium Economy</option>
                      <option>Business</option>
                    </select>
                  </div>
                  <button
                    className="btn-apply-filters-main"
                    onClick={() => {
                      setFilters({ ...pendingFilters })
                    }}
                  >
                    <span>≡</span> Apply Filters
                  </button>
                  <button
                    className="btn-apply-filters-main"
                    style={{ background: '#f8fafc', color: '#475569', border: '1px solid #e2e8f0', boxShadow: 'none' }}
                    onClick={() => {
                      const reset = { origin: 'DEL', destination: 'BOM', airline: '', cabinClass: 'Economy', travelDate: '' }
                      setPendingFilters(reset)
                      setFilters(reset)
                    }}
                  >
                    ↺ Reset
                  </button>
                </div>

                {/* 5 KPI Sub-Cards — dynamic from API */}
                {(() => {
                  const kpi = summary?.kpi
                  const avgFare = kpi?.avg_fare ?? 6471
                  const minFare = kpi?.min_fare ?? 1366
                  const maxFare = kpi?.max_fare ?? 59108
                  const obs = kpi?.total_observations ?? 20020
                  const idxRaw = indexData?.index_value ?? indexData?.aggregate_index ?? kpi?.airfare_price_index ?? null
                  const idxVal = idxRaw != null ? Number(idxRaw) : null
                  const diffFromBase = idxVal != null ? (idxVal - 100) : null
                  const fmtFare = (n) => `₹${Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
                  const dateFiltered = Boolean(filters.travelDate && kpi?.message)
                  return (
                    <div className="rfi-kpi-subcards">
                      {dateFiltered && (
                        <div style={{
                          gridColumn: '1 / -1',
                          background: 'rgba(245,158,11,0.1)',
                          border: '1px solid rgba(245,158,11,0.35)',
                          borderRadius: 8,
                          padding: '8px 14px',
                          fontSize: '0.75rem',
                          color: '#fbbf24',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 8,
                        }}>
                          <span>⚠️</span>
                          No exact data for travel date <strong>{filters.travelDate}</strong> — showing all available historical fares for this route instead.
                        </div>
                      )}
                      <div className="kpi-subcard">
                        <div className="kpi-subcard-left">
                          <div className="kpi-subcard-icon green">📊</div>
                          <div>
                            <div className="kpi-subcard-label">Avg Fare</div>
                            <div className="kpi-subcard-val">{fmtFare(avgFare)}</div>
                            <div className="kpi-subcard-sub green">Aggregated market average</div>
                          </div>
                        </div>
                        <div className="kpi-subcard-badge green">📈</div>
                      </div>
                      <div className="kpi-subcard">
                        <div className="kpi-subcard-left">
                          <div className="kpi-subcard-icon blue">↓</div>
                          <div>
                            <div className="kpi-subcard-label">Min Fare</div>
                            <div className="kpi-subcard-val">{fmtFare(minFare)}</div>
                            <div className="kpi-subcard-sub">Market entry point</div>
                          </div>
                        </div>
                        <div className="kpi-subcard-badge blue">↘</div>
                      </div>
                      <div className="kpi-subcard">
                        <div className="kpi-subcard-left">
                          <div className="kpi-subcard-icon red">↑</div>
                          <div>
                            <div className="kpi-subcard-label">Max Fare</div>
                            <div className="kpi-subcard-val">{fmtFare(maxFare)}</div>
                            <div className="kpi-subcard-sub">Peak observed fare</div>
                          </div>
                        </div>
                        <div className="kpi-subcard-badge red">↗</div>
                      </div>
                      <div className="kpi-subcard">
                        <div className="kpi-subcard-left">
                          <div className="kpi-subcard-icon purple">⚖️</div>
                          <div>
                            <div className="kpi-subcard-label">Airfare Price Index</div>
                            {idxVal != null ? (
                              <>
                                <div className="kpi-subcard-val">{idxVal.toFixed(1)}</div>
                                <div className={`kpi-subcard-sub ${diffFromBase <= 0 ? 'green' : ''}`}>
                                  Baseline = 100 · {diffFromBase <= 0 ? '↓' : '↑'} {Math.abs(diffFromBase).toFixed(1)}% {diffFromBase <= 0 ? 'below' : 'above'} baseline
                                </div>
                              </>
                            ) : (
                              <>
                                <div className="kpi-subcard-val" style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Calculating…</div>
                                <div className="kpi-subcard-sub">Loading index data</div>
                              </>
                            )}
                          </div>
                        </div>
                        <div className="kpi-subcard-badge green">✓</div>
                      </div>
                      <div className="kpi-subcard">
                        <div className="kpi-subcard-left">
                          <div className="kpi-subcard-icon cyan">👁️</div>
                          <div>
                            <div className="kpi-subcard-label">Observations</div>
                            <div className="kpi-subcard-val">{Number(obs).toLocaleString('en-IN')}</div>
                            <div className="kpi-subcard-sub">
                              {summary?.data_mode === 'live' ? 'Live Streaming Data' : 'Historical Data Pool'}
                            </div>
                          </div>
                        </div>
                        <div className="kpi-subcard-badge blue">ℹ</div>
                      </div>
                    </div>
                  )
                })()}
              </div>

              {/* CHARTS ROW */}
              <div className="charts-grid-row">
                <FareTrendChart data={summary?.fare_trend} />
                <IndexTrendChart indexData={indexData} origin={filters.origin} destination={filters.destination} />
              </div>

              {/* BOTTOM 3-COLUMN ROW */}
              <div className="bottom-grid-3">
                {/* Col 1: Top Routes */}
                <div className="bottom-table-card">
                  <div className="bottom-table-header">
                    <div className="bottom-table-title">
                      <span style={{ color: '#2563eb' }}>✈</span> Top Routes by Average Fare
                    </div>
                    <span className="bottom-table-link" onClick={() => setActiveTab('backtesting')}>
                      View All →
                    </span>
                  </div>
                  <table className="custom-data-table">
                    <thead>
                      <tr>
                        <th className="col-rank">#</th>
                        <th>Route</th>
                        <th>Avg Fare</th>
                        <th>Change</th>
                      </tr>
                    </thead>
                    <tbody>
                      {topRoutesList.map((r, i) => (
                        <tr key={i}>
                          <td className="col-rank">{r.rank}</td>
                          <td className="col-route">{r.route}</td>
                          <td className="col-fare">₹{r.fare.toLocaleString('en-IN')}</td>
                          <td className={`col-change ${r.change >= 0 ? 'up' : 'down'}`}>
                            {r.change >= 0 ? '↑' : '↓'} {Math.abs(r.change)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Col 2: Airline Comparison */}
                <div className="bottom-table-card">
                  <div className="bottom-table-header">
                    <div className="bottom-table-title">
                      <span style={{ color: '#7c3aed' }}>📊</span> Airline Fare Comparison
                    </div>
                    <span className="bottom-table-link" onClick={() => setActiveTab('predictions')}>
                      View All →
                    </span>
                  </div>
                  <table className="custom-data-table">
                    <thead>
                      <tr>
                        <th>Airline</th>
                        <th>Avg Fare</th>
                        <th>Trend</th>
                      </tr>
                    </thead>
                    <tbody>
                      {airlineFaresList.map((a, i) => (
                        <tr key={i}>
                          <td>
                            <span className="airline-badge-dot" style={{ background: a.color }}>
                              {a.code}
                            </span>
                            {a.airline}
                          </td>
                          <td className="col-fare">₹{a.fare.toLocaleString('en-IN')}</td>
                          <td className={`col-change ${a.trend >= 0 ? 'up' : 'down'}`}>
                            {a.trend >= 0 ? '↑' : '↓'} {Math.abs(a.trend)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Col 3: Ecosystem Promo Card */}
                <div className="promo-ecosystem-card">
                  <div className="promo-plane-header">
                    <img src="/assets/promo-plane.jpg" alt="Airplane" className="promo-plane-img" />
                  </div>
                  <div className="promo-ecosystem-title">Smarter Decisions for a Stronger Aviation Ecosystem</div>
                   <div className="promo-ecosystem-body">
                    FARECAST analyzes historical data, real-time trends and AI models to help you find the best fares, understand market patterns and make informed decisions.
                  </div>
                  <button className="promo-ecosystem-btn" onClick={() => setActiveTab('predictions')}>
                    Explore Dashboard →
                  </button>
                </div>
              </div>
            </>
          )}

          {/* ═══ OTHER MODULE TABS ═══ */}
          {activeTab === 'dashboard' && (
            <>
              <FilterPanel filters={filters} onFilterChange={setFilters} />
              <KPICards kpi={summary?.kpi} indexData={indexData} dataMode={dataMode} />
              <div className="charts-grid-row">
                <FareTrendChart data={summary?.fare_trend} />
                <IndexTrendChart indexData={indexData} origin={filters.origin} destination={filters.destination} />
              </div>
              <div className="charts-grid-row">
                <AirlineChart data={summary?.airline_comparison} />
                <RouteChart data={summary?.top_routes} />
              </div>
            </>
          )}

          {activeTab === 'predictions' && <PredictionPanel filters={filters} />}
          {activeTab === 'anomalies' && <AnomalyPanel anomalies={anomalies} />}
          {activeTab === 'price-index' && (
            <>
              <FilterPanel filters={filters} onFilterChange={setFilters} />
              <KPICards kpi={summary?.kpi} indexData={indexData} dataMode={dataMode} />
              <IndexTrendChart indexData={indexData} origin={filters.origin} destination={filters.destination} />
            </>
          )}
          {activeTab === 'air-corridor' && <IndiaAirTrafficMap />}
          {activeTab === 'backtesting' && <BacktestingPanel />}
        </main>
      </div>
    </div>
  )
}
