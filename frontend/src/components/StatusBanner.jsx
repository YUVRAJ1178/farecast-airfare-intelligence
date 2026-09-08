/**
 * StatusBanner — Always-visible data source status bar.
 * User must always know if data is live, historical, or demo.
 */

const MESSAGES = {
  live:       '🟢 LIVE — Ignav API · Real-time fare data',
  historical: '🔵 HISTORICAL DATA — Processed airfare observations',
  demo:       '🟡 HISTORICAL / DEMO DATA — Not real-time · Clearly labelled for SIH prototype',
}

const STATUS_DETAILS = {
  live:       'Ignav Flight Prices API connected (IGNAV_API_KEY configured). Fares collected in real time. source_provenance=REAL_API.',
  historical: 'Displaying cleaned historical airfare observations from Kaggle/GitHub datasets.',
  demo:       'No live API credentials. Displaying synthetic/historical demo data tagged source=demo. Not real-time.',
}

export default function StatusBanner({ mode, status }) {
  const m = mode || 'demo'
  const msg = MESSAGES[m] || MESSAGES.demo
  const detail = STATUS_DETAILS[m] || STATUS_DETAILS.demo

  return (
    <div className={`data-source-banner ${m}`} title={detail} role="banner" aria-label="Data source status">
      {msg}
    </div>
  )
}
