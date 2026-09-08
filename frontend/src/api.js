/**
 * API client for Airfare Intelligence backend.
 * Base URL from environment variable, falls back to localhost.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000')

async function apiGet(path, params = {}) {
  const url = new URL(`${BASE_URL}${path}`)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') {
      url.searchParams.set(k, v)
    }
  })
  const res = await fetch(url.toString())
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `API error ${res.status}`)
  }
  return res.json()
}

async function apiPost(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `API error ${res.status}`)
  }
  return res.json()
}

export const api = {
  health: () => apiGet('/health'),
  liveStatus: () => apiGet('/live-status'),
  dashboardSummary: (params) => apiGet('/dashboard-summary', params || {}),
  routes: () => apiGet('/fares/routes'),
  airlines: () => apiGet('/fares/airlines'),
  fares: (params) => apiGet('/fares/', params),
  indexRoute: (origin, destination, params) =>
    apiGet(`/index/${origin}/${destination}`, params),
  indexAggregate: (params) => apiGet('/index/', params),
  dgcaWeights: () => apiGet('/index/dgca-weights'),
  /** Post to /prediction/ — returns PredictionResponse */
  predict: (body) => apiPost('/prediction/', body),
  /** Alias used by PredictionPanel */
  prediction: (body) => apiPost('/prediction/', body),
  anomalies: (params) => apiGet('/anomalies/', params),
  triggerDetection: () => apiPost('/anomalies/detect', {}),
  dgcaBacktest: (params) => apiGet('/backtesting/dgca/30-day', params),
  dgcaBacktestRoutes: () => apiGet('/backtesting/dgca/routes'),
  trafficMap: () => apiGet('/index/traffic-map'),
  provenanceSummary: () => apiGet('/fares/provenance-summary'),
  /**
   * Trigger a live Ignav fare search via the backend.
   * The IGNAV_API_KEY is server-side only — this only POSTs search parameters.
   * body: { origin, destination, departure_date, adults?, cabin_class?, market? }
   */
  searchIgnav: (body) => apiPost('/live/ignav/search', body),
}
