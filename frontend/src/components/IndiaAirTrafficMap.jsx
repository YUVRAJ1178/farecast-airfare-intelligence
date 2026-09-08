import React, { useState, useEffect, useMemo } from 'react'
import { api } from '../api'
import { INDIA_MAINLAND_COORDS, INDIA_ISLANDS_COORDS, BUSY_AIRSPACE_ZONES } from '../data/indiaGeoData'

/**
 * IndiaAirTrafficMap Component
 * 
 * Interactive geo-spatial visualization of India's domestic air traffic corridors.
 * Accurately renders India's official boundaries (Survey of India composite standards)
 * with static visual highlights on high-density arterial corridors and busy metro airspace.
 * Zero distracting animations, optimized for clarity and analytical precision.
 */

// Geographic coordinate bounds for India viewport (adjusted for authentic proportions)
const MIN_LON = 67.0
const MAX_LON = 98.0
const MIN_LAT = 7.0
const MAX_LAT = 37.8

const SVG_WIDTH = 760
const SVG_HEIGHT = 820
const PADDING = 40

// Equirectangular projection mapping geographic lat/lon to SVG canvas coordinates
function project(lat, lon) {
  const x = PADDING + ((lon - MIN_LON) / (MAX_LON - MIN_LON)) * (SVG_WIDTH - 2 * PADDING)
  // Invert Y because SVG coordinates go down from top
  const y = PADDING + ((MAX_LAT - lat) / (MAX_LAT - MIN_LAT)) * (SVG_HEIGHT - 2 * PADDING)
  return { x, y }
}

export default function IndiaAirTrafficMap() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedCorridor, setSelectedCorridor] = useState(null)
  const [selectedHub, setSelectedHub] = useState(null)
  const [selectedZone, setSelectedZone] = useState(null)
  const [filterMode, setFilterMode] = useState('ALL') // 'ALL' | 'BUSY_ONLY' | 'CRITICAL' | 'TRUNK' | 'SOUTH'
  const [highlightBusy, setHighlightBusy] = useState(true) // Static highlight toggle
  const [activeTab, setActiveTab] = useState('map') // 'map' | 'leaderboard'

  useEffect(() => {
    async function loadTrafficData() {
      try {
        setLoading(true)
        const res = await api.trafficMap()
        setData(res)
        if (res.corridors && res.corridors.length > 0) {
          setSelectedCorridor(res.corridors[0]) // default select busiest (DEL-BOM)
        }
      } catch (err) {
        console.error('Failed to load traffic map data:', err)
        setError(err.message || 'Could not fetch traffic density data')
      } finally {
        setLoading(false)
      }
    }
    loadTrafficData()
  }, [])

  // Geographically accurate India mainland boundary SVG path
  const mainlandSvgPath = useMemo(() => {
    const pts = INDIA_MAINLAND_COORDS.map(([lon, lat]) => {
      const { x, y } = project(lat, lon)
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    return `M ${pts.join(' L ')} Z`
  }, [])

  // Geographically accurate Andaman & Nicobar and Lakshadweep islands
  const islandsSvgPaths = useMemo(() => {
    return INDIA_ISLANDS_COORDS.map(island => {
      const pts = island.map(([lon, lat]) => {
        const { x, y } = project(lat, lon)
        return `${x.toFixed(1)},${y.toFixed(1)}`
      })
      return `M ${pts.join(' L ')} Z`
    })
  }, [])

  // Project busy metro airspace zones
  const projectedBusyZones = useMemo(() => {
    return BUSY_AIRSPACE_ZONES.map(z => {
      const { x, y } = project(z.lat, z.lon)
      return { ...z, svgX: x, svgY: y }
    })
  }, [])

  // Filter corridors based on user choice
  const filteredCorridors = useMemo(() => {
    if (!data?.corridors) return []
    let list = data.corridors

    if (filterMode === 'BUSY_ONLY' || filterMode === 'CRITICAL') {
      list = list.filter(c => c.annual_pax_millions >= 2.5)
    } else if (filterMode === 'TRUNK') {
      list = list.filter(c => c.annual_pax_millions >= 2.0)
    } else if (filterMode === 'SOUTH') {
      const southHubs = ['BLR', 'MAA', 'HYD', 'COK']
      list = list.filter(c => southHubs.includes(c.origin) || southHubs.includes(c.destination))
    }

    if (selectedHub) {
      list = list.filter(c => c.origin === selectedHub.code || c.destination === selectedHub.code)
    }

    return list
  }, [data, filterMode, selectedHub])

  // Project hubs coordinates
  const projectedHubs = useMemo(() => {
    if (!data?.hubs) return []
    return data.hubs.map(h => {
      const { x, y } = project(h.lat, h.lon)
      return { ...h, svgX: x, svgY: y }
    })
  }, [data])

  // Map hub code to projected hub
  const hubLookup = useMemo(() => {
    const map = {}
    projectedHubs.forEach(h => { map[h.code] = h })
    return map
  }, [projectedHubs])

  // Compute curved flight paths with quadratic bezier arc
  const corridorPaths = useMemo(() => {
    return filteredCorridors.map(c => {
      const p1 = hubLookup[c.origin]
      const p2 = hubLookup[c.destination]
      if (!p1 || !p2) return null

      // Calculate midpoint
      const mx = (p1.svgX + p2.svgX) / 2
      const my = (p1.svgY + p2.svgY) / 2

      // Perpendicular vector for arching flight corridor curve
      const dx = p2.svgX - p1.svgX
      const dy = p2.svgY - p1.svgY
      const dist = Math.sqrt(dx * dx + dy * dy)

      // Bow height proportional to distance
      const bow = Math.min(dist * 0.16, 48)
      // Normal vector
      const nx = -dy / dist
      const ny = dx / dist

      const cx = mx + nx * bow
      const cy = my + ny * bow

      const pathStr = `M ${p1.svgX.toFixed(1)},${p1.svgY.toFixed(1)} Q ${cx.toFixed(1)},${cy.toFixed(1)} ${p2.svgX.toFixed(1)},${p2.svgY.toFixed(1)}`

      // Dynamic line width highlighting high-density traffic
      const isCritical = c.annual_pax_millions >= 4.0
      const isHeavy = c.annual_pax_millions >= 2.5
      const strokeWidth = isCritical ? 5.8 : isHeavy ? 4.2 : c.annual_pax_millions >= 1.8 ? 2.8 : 1.8

      return {
        ...c,
        pathStr,
        strokeWidth,
        isCritical,
        isHeavy,
        p1,
        p2,
        cx,
        cy,
      }
    }).filter(Boolean)
  }, [filteredCorridors, hubLookup])

  if (loading) {
    return (
      <div className="card" style={{ marginTop: 24, padding: 30, textAlign: 'center' }}>
        <div className="spinner" style={{ margin: '0 auto 16px' }} />
        <div style={{ color: 'var(--text-secondary)' }}>Loading DGCA Air Traffic Map & Corridor Density...</div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="card" style={{ marginTop: 24, padding: 24, color: 'var(--accent-orange)' }}>
        ⚠ Traffic Map Error: {error || 'No traffic corridor data available'}
      </div>
    )
  }

  const { national_traffic_summary } = data

  return (
    <div className="card" id="india-air-traffic-panel" style={{ marginTop: 24, padding: '24px 28px' }}>
      {/* Header & Meta */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 20 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: '1.4rem' }}>🗺️</span>
            <div className="card-title" style={{ margin: 0, fontSize: '1.25rem', letterSpacing: '-0.02em' }}>
              India Air Traffic Corridor & Density Map
            </div>
            <span style={{
              fontSize: '0.68rem',
              padding: '2px 8px',
              borderRadius: 20,
              background: 'rgba(16, 185, 129, 0.15)',
              color: 'var(--accent-green)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              fontWeight: 600,
            }}>
              LIVE DGCA BENCHMARK
            </span>
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: 4 }}>
            Geospatially authentic map of India highlighting high-density domestic passenger trunks and busy metro airspace.
          </div>
        </div>

        {/* View Switcher & Busy Highlight Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ display: 'flex', background: 'var(--bg-secondary)', borderRadius: 8, padding: 3, border: '1px solid var(--border)' }}>
            <button
              onClick={() => setActiveTab('map')}
              style={{
                background: activeTab === 'map' ? 'var(--accent-blue)' : 'transparent',
                color: activeTab === 'map' ? '#fff' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 6,
                padding: '6px 14px',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              Density Map
            </button>
            <button
              onClick={() => setActiveTab('leaderboard')}
              style={{
                background: activeTab === 'leaderboard' ? 'var(--accent-blue)' : 'transparent',
                color: activeTab === 'leaderboard' ? '#fff' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 6,
                padding: '6px 14px',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              Congestion Rankings
            </button>
          </div>

          {/* Static Busy Area Highlight Button */}
          <button
            onClick={() => setHighlightBusy(!highlightBusy)}
            style={{
              background: highlightBusy ? 'rgba(239, 68, 68, 0.16)' : 'var(--bg-secondary)',
              color: highlightBusy ? '#ef4444' : 'var(--text-muted)',
              border: `1px solid ${highlightBusy ? 'rgba(239, 68, 68, 0.45)' : 'var(--border)'}`,
              borderRadius: 8,
              padding: '6px 12px',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              transition: 'all 0.15s',
            }}
            title="Statically emphasize the busiest high-density air traffic corridors and metro congestion zones"
          >
            <span>🔥 Busy Areas Highlight: {highlightBusy ? 'ON' : 'OFF'}</span>
          </button>
        </div>
      </div>

      {/* Traffic Summary Metrics Banner */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: 12,
        marginBottom: 20,
        background: 'var(--bg-secondary)',
        padding: '14px 18px',
        borderRadius: 10,
        border: '1px solid var(--border)',
      }}>
        <div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Busiest Corridor</div>
          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--accent-red)', marginTop: 2 }}>
            {national_traffic_summary.busiest_corridor}
          </div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>DEL-BOM Primary Trunk (6.2M Pax)</div>
        </div>

        <div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Monitored Annual Pax</div>
          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--accent-blue-light)', marginTop: 2 }}>
            {data.total_monitored_pax_millions} Million
          </div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Across 15 top city-pairs</div>
        </div>

        <div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Daily Monitored Flights</div>
          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--accent-green)', marginTop: 2 }}>
            ~{national_traffic_summary.daily_monitored_departures.toLocaleString()} Flights/Day
          </div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Scheduled commercial domestic</div>
        </div>

        <div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Trunk Traffic Share</div>
          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--accent-orange)', marginTop: 2 }}>
            {national_traffic_summary.metro_trunk_share.split(' ')[0]}
          </div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Metro-to-metro concentration</div>
        </div>
      </div>

      {/* Filter Chips */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 16 }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Filter Corridors:</span>
        {[
          { id: 'ALL', label: 'All Corridors (15)' },
          { id: 'BUSY_ONLY', label: '🔥 Busy Corridors (>2.5M Pax)' },
          { id: 'TRUNK', label: 'Primary Trunks (>2.0M Pax)' },
          { id: 'SOUTH', label: 'Southern Triangle' },
        ].map(btn => (
          <button
            key={btn.id}
            onClick={() => { setFilterMode(btn.id); setSelectedHub(null); setSelectedZone(null); }}
            style={{
              background: filterMode === btn.id && !selectedHub ? 'rgba(59, 130, 246, 0.2)' : 'var(--bg-secondary)',
              color: filterMode === btn.id && !selectedHub ? 'var(--accent-blue-light)' : 'var(--text-secondary)',
              border: `1px solid ${filterMode === btn.id && !selectedHub ? 'var(--accent-blue)' : 'var(--border)'}`,
              borderRadius: 6,
              padding: '4px 10px',
              fontSize: '0.72rem',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            {btn.label}
          </button>
        ))}

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>Airport Hub:</span>
          <select
            id="map-airport-selector"
            value={selectedHub ? selectedHub.code : ''}
            onChange={(e) => {
              const code = e.target.value
              if (!code) { setSelectedHub(null); return; }
              const hub = data?.hubs?.find(h => h.code === code)
              if (hub) { setSelectedHub(hub); setSelectedZone(null); }
            }}
            style={{
              fontSize: '0.75rem',
              padding: '4px 8px',
              borderRadius: 6,
              background: 'var(--bg-secondary)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border)',
            }}
          >
            <option value="">-- All 17 Airport Hubs --</option>
            {(data?.hubs || []).map(h => (
              <option key={h.code} value={h.code}>{h.city} ({h.code}) - {h.tier}</option>
            ))}
          </select>
        </div>

        {selectedHub && (
          <button
            onClick={() => setSelectedHub(null)}
            style={{
              background: 'rgba(239, 68, 68, 0.15)',
              color: 'var(--accent-red)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: 6,
              padding: '4px 10px',
              fontSize: '0.72rem',
              cursor: 'pointer',
            }}
          >
            ✕ Reset Hub: {selectedHub.code}
          </button>
        )}

        {selectedZone && (
          <button
            onClick={() => setSelectedZone(null)}
            style={{
              background: 'rgba(239, 68, 68, 0.15)',
              color: 'var(--accent-red)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: 6,
              padding: '4px 10px',
              fontSize: '0.72rem',
              cursor: 'pointer',
            }}
          >
            ✕ Reset Zone: {selectedZone.name}
          </button>
        )}
      </div>

      {/* Main Content: Map or Leaderboard */}
      {activeTab === 'map' ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(300px, 1fr)', gap: 20, alignItems: 'start' }}>
          
          {/* SVG Map Container */}
          <div style={{
            position: 'relative',
            background: 'radial-gradient(circle at 50% 45%, #0f172a 0%, #060911 100%)',
            borderRadius: 12,
            border: '1px solid var(--border)',
            overflow: 'hidden',
            boxShadow: 'inset 0 0 45px rgba(0,0,0,0.7)',
          }}>
            {/* Ambient Map Graticule / Radar Grid */}
            <svg
              viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
              style={{ width: '100%', height: 'auto', display: 'block' }}
            >
              <defs>
                {/* Corridor Static Glow Filters */}
                <filter id="glow-critical" x="-25%" y="-25%" width="150%" height="150%">
                  <feGaussianBlur stdDeviation="3.0" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
                <filter id="glow-heavy" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="2.0" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>

                {/* Static Radial Halos for High-Density Busy Zones */}
                <radialGradient id="halo-delhi" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity="0.28" />
                  <stop offset="60%" stopColor="#ef4444" stopOpacity="0.10" />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity="0" />
                </radialGradient>
                <radialGradient id="halo-mumbai" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#f97316" stopOpacity="0.28" />
                  <stop offset="60%" stopColor="#f97316" stopOpacity="0.10" />
                  <stop offset="100%" stopColor="#f97316" stopOpacity="0" />
                </radialGradient>
                <radialGradient id="halo-south" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.22" />
                  <stop offset="65%" stopColor="#38bdf8" stopOpacity="0.08" />
                  <stop offset="100%" stopColor="#38bdf8" stopOpacity="0" />
                </radialGradient>
                <radialGradient id="halo-east" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#818cf8" stopOpacity="0.20" />
                  <stop offset="65%" stopColor="#818cf8" stopOpacity="0.06" />
                  <stop offset="100%" stopColor="#818cf8" stopOpacity="0" />
                </radialGradient>
              </defs>

              {/* Background Geographic Grids */}
              <g stroke="rgba(255, 255, 255, 0.04)" strokeWidth="1" strokeDasharray="4 6">
                {[150, 300, 450, 600, 750].map(y => (
                  <line key={`h-${y}`} x1="0" y1={y} x2={SVG_WIDTH} y2={y} />
                ))}
                {[150, 300, 450, 600].map(x => (
                  <line key={`v-${x}`} x1={x} y1="0" x2={x} y2={SVG_HEIGHT} />
                ))}
              </g>

              {/* Geographically Accurate Mainland India Boundary */}
              <path
                d={mainlandSvgPath}
                fill="rgba(30, 41, 59, 0.45)"
                stroke="rgba(56, 189, 248, 0.32)"
                strokeWidth="1.6"
                strokeLinejoin="round"
              />

              {/* Andaman & Nicobar and Lakshadweep Islands */}
              {islandsSvgPaths.map((path, idx) => (
                <path
                  key={`island-${idx}`}
                  d={path}
                  fill="rgba(30, 41, 59, 0.45)"
                  stroke="rgba(56, 189, 248, 0.32)"
                  strokeWidth="1.4"
                  strokeLinejoin="round"
                />
              ))}

              {/* Geographic Labels */}
              <text x="28" y="45" fill="rgba(255,255,255,0.22)" fontSize="9.5" fontFamily="monospace" fontWeight="600">37°N · JAMMU, KASHMIR & LADAKH</text>
              <text x="210" y="805" fill="rgba(255,255,255,0.22)" fontSize="9.5" fontFamily="monospace" fontWeight="600">INDIAN OCEAN · 8°N</text>
              <text x="520" y="580" fill="rgba(255,255,255,0.20)" fontSize="10" fontFamily="monospace" fontWeight="600">BAY OF BENGAL</text>
              <text x="50" y="580" fill="rgba(255,255,255,0.20)" fontSize="10" fontFamily="monospace" fontWeight="600">ARABIAN SEA</text>
              <text x="575" y="740" fill="rgba(255,255,255,0.18)" fontSize="8.5" fontFamily="monospace">ANDAMAN & NICOBAR</text>

              {/* Static Busy Airspace Zones (Heat Halos) */}
              {highlightBusy && (
                <g id="busy-airspace-zones">
                  {projectedBusyZones.map(zone => {
                    const isZoneSelected = selectedZone?.id === zone.id
                    const gradId = zone.id === 'delhi-ncr' ? 'halo-delhi'
                      : zone.id === 'mumbai-mmr' ? 'halo-mumbai'
                      : zone.id === 'southern-triangle' ? 'halo-south' : 'halo-east'

                    return (
                      <g
                        key={zone.id}
                        style={{ cursor: 'pointer' }}
                        onClick={() => setSelectedZone(isZoneSelected ? null : zone)}
                      >
                        {/* Radiant Radial Heat Halo */}
                        <circle
                          cx={zone.svgX}
                          cy={zone.svgY}
                          r={zone.radiusSvg}
                          fill={`url(#${gradId})`}
                          stroke={zone.strokeColor}
                          strokeWidth={isZoneSelected ? 2.0 : 1.2}
                          strokeDasharray={isZoneSelected ? 'none' : '3 3'}
                        />

                        {/* Static Zone Label Callout */}
                        <g transform={`translate(${zone.svgX}, ${zone.id === 'delhi-ncr' ? zone.svgY - zone.radiusSvg - 8 : zone.id === 'mumbai-mmr' ? zone.svgY + zone.radiusSvg + 12 : zone.svgY - zone.radiusSvg - 6})`}>
                          <rect
                            x="-60"
                            y="-9"
                            width="120"
                            height="16"
                            rx="4"
                            fill="rgba(15, 23, 42, 0.85)"
                            stroke={zone.color}
                            strokeWidth="0.8"
                          />
                          <text
                            x="0"
                            y="2.5"
                            textAnchor="middle"
                            fill={zone.color}
                            fontSize="7.5"
                            fontWeight="700"
                            letterSpacing="0.03em"
                          >
                            {zone.badge}
                          </text>
                        </g>
                      </g>
                    )
                  })}
                </g>
              )}

              {/* Flight Corridors (Curved Arcs) - Statically Highlighted */}
              <g id="flight-corridors">
                {corridorPaths.map(c => {
                  const isSelected = selectedCorridor && selectedCorridor.id === c.id
                  const isHubConnected = selectedHub && (c.origin === selectedHub.code || c.destination === selectedHub.code)
                  
                  // Static prominence calculation
                  let opacity = 0.8
                  if (selectedCorridor || selectedHub) {
                    opacity = isSelected || isHubConnected ? 1.0 : 0.18
                  } else if (highlightBusy) {
                    opacity = c.isCritical ? 1.0 : c.isHeavy ? 0.90 : 0.40
                  }

                  const activeWidth = isSelected ? c.strokeWidth + 2.5 : c.strokeWidth

                  return (
                    <g key={c.id} style={{ cursor: 'pointer' }} onClick={() => setSelectedCorridor(c)}>
                      {/* Wider invisible stroke for easy clicking/hovering */}
                      <path
                        d={c.pathStr}
                        fill="none"
                        stroke="transparent"
                        strokeWidth="18"
                      />

                      {/* Static Under-glow for Critical & Heavy High-Density Paths */}
                      {(c.isCritical || (c.isHeavy && highlightBusy)) && (
                        <path
                          d={c.pathStr}
                          fill="none"
                          stroke={c.color}
                          strokeWidth={activeWidth + 4}
                          strokeOpacity={opacity * 0.45}
                          filter="url(#glow-critical)"
                        />
                      )}

                      {/* Visible Corridor Arc */}
                      <path
                        d={c.pathStr}
                        fill="none"
                        stroke={c.color}
                        strokeWidth={activeWidth}
                        strokeOpacity={opacity}
                        strokeLinecap="round"
                        filter={c.isCritical ? 'url(#glow-heavy)' : undefined}
                      />

                      {/* Prominent Static Callout for India's #1 Busiest Corridor (DEL-BOM) */}
                      {c.id === 'DEL-BOM' && highlightBusy && (
                        <g transform={`translate(${c.cx - 75}, ${c.cy - 16})`} style={{ pointerEvents: 'none' }}>
                          <rect
                            x="0"
                            y="0"
                            width="150"
                            height="20"
                            rx="10"
                            fill="rgba(15, 23, 42, 0.94)"
                            stroke="#ef4444"
                            strokeWidth="1.2"
                            filter="url(#glow-heavy)"
                          />
                          <text
                            x="75"
                            y="13"
                            textAnchor="middle"
                            fill="#fff"
                            fontSize="8"
                            fontWeight="800"
                            letterSpacing="0.02em"
                          >
                            🔥 BUSIEST: DEL ⇄ BOM (6.2M)
                          </text>
                        </g>
                      )}
                    </g>
                  )
                })}
              </g>

              {/* Airport Hub Nodes (Clean Static Highlights) */}
              <g id="airport-hubs">
                {projectedHubs.map(hub => {
                  const isSelected = selectedHub && selectedHub.code === hub.code
                  const isCorridorEnd = selectedCorridor && (selectedCorridor.origin === hub.code || selectedCorridor.destination === hub.code)
                  const isMegaBusy = hub.rank <= 2 // DEL, BOM
                  
                  // Base hub radius proportional to passenger throughput
                  const radius = Math.max(5, Math.min(13, 4 + Math.sqrt(hub.total_pax_m) * 1.0))

                  return (
                    <g
                      key={hub.code}
                      transform={`translate(${hub.svgX}, ${hub.svgY})`}
                      style={{ cursor: 'pointer' }}
                      onClick={() => {
                        setSelectedHub(isSelected ? null : hub)
                      }}
                    >
                      {/* Static Highlight Outer Ring for Busy Hubs */}
                      {hub.rank <= 6 && (
                        <circle
                          r={radius + 3.5}
                          fill="none"
                          stroke={isSelected || isCorridorEnd ? 'var(--accent-orange)' : isMegaBusy ? '#ef4444' : 'rgba(56, 189, 248, 0.5)'}
                          strokeWidth="1.2"
                          strokeDasharray={isMegaBusy ? 'none' : '3 2'}
                        />
                      )}

                      {/* Outer Hub Node */}
                      <circle
                        r={radius}
                        fill={isSelected || isCorridorEnd ? '#f97316' : isMegaBusy ? '#7f1d1d' : '#1e293b'}
                        stroke={isSelected || isCorridorEnd ? '#fff' : isMegaBusy ? '#ef4444' : hub.rank <= 3 ? '#38bdf8' : '#64748b'}
                        strokeWidth={isSelected || isCorridorEnd ? 2.5 : isMegaBusy ? 2.0 : 1.6}
                      />

                      {/* Hub Center Dot */}
                      <circle
                        r={radius * 0.45}
                        fill={isSelected || isCorridorEnd ? '#fff' : isMegaBusy ? '#ef4444' : hub.rank <= 3 ? '#38bdf8' : '#94a3b8'}
                      />

                      {/* Airport IATA Code Label */}
                      <text
                        x={radius + 5}
                        y={4}
                        fill={isSelected || isCorridorEnd ? '#fff' : isMegaBusy ? '#fca5a5' : 'var(--text-primary)'}
                        fontSize={hub.rank <= 6 ? 11 : 9.5}
                        fontWeight={hub.rank <= 6 || isSelected ? 700 : 500}
                        style={{
                          textShadow: '0 1px 4px rgba(0,0,0,0.9)',
                          pointerEvents: 'none',
                        }}
                      >
                        {hub.code}
                      </text>

                      {/* City Name & Passenger Volume for Mega Hubs */}
                      {hub.rank <= 6 && (
                        <text
                          x={radius + 5}
                          y={15}
                          fill="var(--text-muted)"
                          fontSize="7.5"
                          fontWeight="400"
                          style={{ pointerEvents: 'none' }}
                        >
                          {hub.city} · <tspan fill={isMegaBusy ? '#ef4444' : 'var(--accent-blue-light)'} fontWeight="700">{hub.total_pax_m}M</tspan>
                        </text>
                      )}
                    </g>
                  )
                })}
              </g>

              {/* Map Legend (Internal Static Overview) */}
              <g transform={`translate(${SVG_WIDTH - 215}, 25)`}>
                <rect width="200" height="135" rx="8" fill="rgba(15, 23, 42, 0.90)" stroke="var(--border)" strokeWidth="1" />
                <text x="14" y="20" fill="var(--text-primary)" fontSize="9.5" fontWeight="700">CORRIDOR CONGESTION</text>

                <circle cx="20" cy="40" r="5" fill="#ef4444" />
                <text x="32" y="44" fill="var(--text-secondary)" fontSize="9">Critical (&gt;4.0M Pax/yr)</text>

                <circle cx="20" cy="62" r="4.5" fill="#f97316" />
                <text x="32" y="66" fill="var(--text-secondary)" fontSize="9">Heavy (2.5–4.0M Pax)</text>

                <circle cx="20" cy="84" r="4" fill="#38bdf8" />
                <text x="32" y="88" fill="var(--text-secondary)" fontSize="9">Moderate (1.8–2.5M Pax)</text>

                <circle cx="20" cy="106" r="3.5" fill="#818cf8" />
                <text x="32" y="110" fill="var(--text-secondary)" fontSize="9">Standard (&lt;1.8M Pax)</text>

                <line x1="14" y1="120" x2="186" y2="120" stroke="rgba(255,255,255,0.08)" />
                <circle cx="20" cy="126" r="3.5" fill="none" stroke="#ef4444" strokeWidth="1" strokeDasharray="2 2" />
                <text x="32" y="129" fill="var(--text-muted)" fontSize="7.5">Dashed circles = Busy Airspace</text>
              </g>
            </svg>
          </div>

          {/* Sidebar Detail Card */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Selected Zone Inspector (if clicked) */}
            {selectedZone && (
              <div style={{
                background: 'var(--bg-secondary)',
                borderRadius: 12,
                padding: '18px 20px',
                border: `1px solid ${selectedZone.color}40`,
                boxShadow: `0 4px 20px ${selectedZone.color}15`,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{
                    fontSize: '0.68rem',
                    padding: '3px 8px',
                    borderRadius: 6,
                    background: `${selectedZone.color}20`,
                    color: selectedZone.color,
                    border: `1px solid ${selectedZone.color}40`,
                    fontWeight: 700,
                  }}>
                    {selectedZone.badge}
                  </span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    Primary: {selectedZone.hub}
                  </span>
                </div>

                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fff', marginBottom: 4 }}>
                  {selectedZone.name}
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: 12 }}>
                  {selectedZone.description}
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 10,
                  background: 'var(--bg-card)',
                  padding: 12,
                  borderRadius: 8,
                }}>
                  <div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>ANNUAL PASSENGERS</div>
                    <div style={{ fontSize: '1.05rem', fontWeight: 700, color: selectedZone.color, marginTop: 2 }}>
                      {selectedZone.annual_pax}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>EST. DAILY FLIGHTS</div>
                    <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--accent-green)', marginTop: 2 }}>
                      {selectedZone.daily_flights}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Selected Corridor Inspector */}
            {selectedCorridor ? (
              <div style={{
                background: 'var(--bg-secondary)',
                borderRadius: 12,
                padding: '20px',
                border: `1px solid ${selectedCorridor.color}40`,
                boxShadow: `0 4px 20px ${selectedCorridor.color}15`,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <span style={{
                    fontSize: '0.68rem',
                    padding: '3px 8px',
                    borderRadius: 6,
                    background: `${selectedCorridor.color}20`,
                    color: selectedCorridor.color,
                    border: `1px solid ${selectedCorridor.color}40`,
                    fontWeight: 700,
                  }}>
                    {selectedCorridor.congestion} CONGESTION
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    {selectedCorridor.category}
                  </span>
                </div>

                <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#fff', marginBottom: 4 }}>
                  {selectedCorridor.origin} ⇄ {selectedCorridor.destination}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 16 }}>
                  {selectedCorridor.origin_city} to {selectedCorridor.destination_city} Air Corridor
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 12,
                  background: 'var(--bg-card)',
                  padding: 14,
                  borderRadius: 8,
                  marginBottom: 16,
                }}>
                  <div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>ANNUAL PASSENGERS</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: 2 }}>
                      {selectedCorridor.annual_pax_millions}M
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>NATIONAL TRAFFIC SHARE</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-cyan)', marginTop: 2 }}>
                      {selectedCorridor.traffic_share_pct}%
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>EST. DAILY FLIGHTS</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-orange)', marginTop: 2 }}>
                      ~{selectedCorridor.daily_flights_est} / day
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>AERIAL DISTANCE</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-secondary)', marginTop: 2 }}>
                      {selectedCorridor.distance_km} km
                    </div>
                  </div>
                </div>

                {/* Relative Load Bar */}
                <div style={{ marginBottom: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-muted)' }}>Corridor Load Intensity:</span>
                    <span style={{ color: selectedCorridor.color, fontWeight: 700 }}>
                      {((selectedCorridor.annual_pax_millions / 6.2) * 100).toFixed(0)}% of Peak
                    </span>
                  </div>
                  <div style={{ width: '100%', height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{
                      width: `${(selectedCorridor.annual_pax_millions / 6.2) * 100}%`,
                      height: '100%',
                      background: selectedCorridor.color,
                      borderRadius: 3,
                    }} />
                  </div>
                </div>
              </div>
            ) : (
              <div style={{
                background: 'var(--bg-secondary)',
                borderRadius: 12,
                padding: '24px',
                textAlign: 'center',
                color: 'var(--text-muted)',
                border: '1px solid var(--border)',
              }}>
                Hover or click any flight corridor on the map to inspect density metrics.
              </div>
            )}

            {/* Selected Hub Card (if airport clicked) */}
            {selectedHub && (
              <div style={{
                background: 'var(--bg-secondary)',
                borderRadius: 12,
                padding: '18px',
                border: '1px solid var(--accent-blue)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--accent-blue-light)', fontWeight: 600 }}>
                    SELECTED AIRPORT HUB
                  </span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    Rank #{selectedHub.rank} in India
                  </span>
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>
                  {selectedHub.name} ({selectedHub.code})
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 12 }}>
                  {selectedHub.city}, {selectedHub.tier}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', background: 'var(--bg-card)', padding: '10px 14px', borderRadius: 8 }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Annual Passenger Throughput:</span>
                  <strong style={{ color: 'var(--accent-green)' }}>{selectedHub.total_pax_m} Million</strong>
                </div>
              </div>
            )}

            {/* Quick Top 5 Corridors Quick-Select List */}
            <div style={{
              background: 'var(--bg-secondary)',
              borderRadius: 12,
              padding: '18px',
              border: '1px solid var(--border)',
            }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 12 }}>
                Busiest National Air Corridors (Top 5)
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {data.corridors.slice(0, 5).map((c, i) => {
                  const isSelected = selectedCorridor && selectedCorridor.id === c.id
                  return (
                    <div
                      key={c.id}
                      onClick={() => setSelectedCorridor(c)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '8px 12px',
                        borderRadius: 8,
                        background: isSelected ? 'rgba(59, 130, 246, 0.18)' : 'var(--bg-card)',
                        border: `1px solid ${isSelected ? 'var(--accent-blue)' : 'transparent'}`,
                        cursor: 'pointer',
                        transition: 'all 0.15s',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', width: 14 }}>
                          #{i + 1}
                        </span>
                        <div>
                          <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                            {c.origin} ⇄ {c.destination}
                          </div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                            {c.origin_city} - {c.destination_city}
                          </div>
                        </div>
                      </div>

                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.82rem', fontWeight: 700, color: c.color }}>
                          {c.annual_pax_millions}M pax
                        </div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                          {c.traffic_share_pct}% share
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Rankings Table View */
        <div style={{ overflowX: 'auto', background: 'var(--bg-secondary)', borderRadius: 12, border: '1px solid var(--border)' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)', background: 'var(--bg-card)' }}>
                <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>Rank</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>City-Pair Corridor</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>Distance</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>Annual Volume</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>National Share</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>Est. Daily Flights</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>Congestion Level</th>
              </tr>
            </thead>
            <tbody>
              {data.corridors.map((c, idx) => (
                <tr
                  key={c.id}
                  onClick={() => { setSelectedCorridor(c); setActiveTab('map'); }}
                  style={{
                    borderBottom: '1px solid rgba(255,255,255,0.04)',
                    cursor: 'pointer',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--text-muted)' }}>#{idx + 1}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>{c.origin} ⇄ {c.destination}</strong>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{c.origin_city} - {c.destination_city}</div>
                  </td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>{c.distance_km} km</td>
                  <td style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--text-primary)' }}>{c.annual_pax_millions}M Pax</td>
                  <td style={{ padding: '12px 16px', color: 'var(--accent-cyan)' }}>{c.traffic_share_pct}%</td>
                  <td style={{ padding: '12px 16px', color: 'var(--accent-orange)' }}>~{c.daily_flights_est}/day</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      fontSize: '0.68rem',
                      padding: '2px 8px',
                      borderRadius: 4,
                      background: `${c.color}20`,
                      color: c.color,
                      border: `1px solid ${c.color}40`,
                      fontWeight: 700,
                    }}>
                      {c.congestion}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
