css_content = '''/* ============================================================
   FARECAST — Airfare Intelligence Platform for India
   "Smarter Skies. Better Decisions."
   Professional Light-Mode SaaS Design System
   ============================================================ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  /* Core Backgrounds */
  --bg-primary: #f1f5f9;
  --bg-secondary: #ffffff;
  --bg-card: #ffffff;
  --bg-card-hover: #f8fafc;
  --bg-accent: #f1f5f9;
  --bg-app: #f1f5f9;
  --bg-input: #f8fafc;
  --bg-input-focus: #ffffff;

  /* Sidebar Dark Theme (SaaS Navigation) */
  --bg-sidebar: #0f172a;
  --bg-sidebar-hover: #1e293b;
  --bg-sidebar-active: #1d4ed8;
  --text-sidebar: #cbd5e1;
  --text-sidebar-muted: #64748b;

  /* Primary Aviation Accents */
  --accent-blue: #1d4ed8;
  --accent-blue-light: #2563eb;
  --accent-blue-glow: rgba(29, 78, 216, 0.08);
  --accent-primary: #1d4ed8;
  --accent-primary-light: #3b82f6;
  --accent-primary-pale: #eff6ff;
  --accent-primary-border: #bfdbfe;

  /* Status Colors */
  --accent-green: #059669;
  --accent-green-pale: #ecfdf5;
  --accent-green-border: #a7f3d0;
  --accent-red: #dc2626;
  --accent-red-pale: #fef2f2;
  --accent-red-border: #fecaca;
  --accent-orange: #d97706;
  --accent-orange-pale: #fffbeb;
  --accent-orange-border: #fde68a;
  --accent-purple: #7c3aed;
  --accent-purple-pale: #f5f3ff;
  --accent-cyan: #0891b2;

  /* Index specific */
  --index-up: #dc2626;
  --index-neutral: #1d4ed8;
  --index-down: #059669;

  /* Text Colors for High Readability */
  --text-primary: #0f172a;
  --text-main: #0f172a;
  --text-secondary: #334155;
  --text-muted: #64748b;
  --text-accent: #1d4ed8;

  /* Borders */
  --border: #e2e8f0;
  --border-strong: #cbd5e1;
  --border-accent: #bfdbfe;

  /* Shadows */
  --shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.05);
  --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.08), 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
  --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04);
  --shadow-card: 0 1px 3px rgba(15, 23, 42, 0.08), 0 1px 2px rgba(15, 23, 42, 0.04);

  /* Dimensions */
  --sidebar-width: 240px;
  --sidebar-collapsed-width: 64px;
  --topbar-height: 60px;

  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Radii */
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition: 200ms ease;
  --transition-slow: 300ms ease;
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-sans);
  background: var(--bg-app);
  color: var(--text-primary);
  min-height: 100vh;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

/* App Shell */
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--bg-app);
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-sidebar);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 200;
  transition: width var(--transition-slow) cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  min-height: 70px;
  flex-shrink: 0;
  position: relative;
}

.sidebar-logo {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #1d4ed8, #7c3aed);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(29, 78, 216, 0.4);
}

.sidebar-brand-text {
  overflow: hidden;
  white-space: nowrap;
  transition: opacity var(--transition);
}

.sidebar.collapsed .sidebar-brand-text {
  opacity: 0;
  width: 0;
}

.sidebar-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.sidebar-tagline {
  font-size: 0.58rem;
  color: var(--text-sidebar-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 1px;
}

.sidebar-toggle {
  position: absolute;
  top: 23px;
  right: -12px;
  width: 24px;
  height: 24px;
  background: #1d4ed8;
  border: 2.5px solid #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 9px;
  color: #fff;
  transition: all var(--transition);
  z-index: 10;
  box-shadow: var(--shadow-sm);
}

.sidebar-toggle:hover {
  background: #2563eb;
  transform: scale(1.1);
}

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-section-label {
  font-size: 0.58rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-sidebar-muted);
  padding: 10px 10px 5px;
  white-space: nowrap;
  overflow: hidden;
  transition: opacity var(--transition);
}

.sidebar.collapsed .sidebar-section-label {
  opacity: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-sidebar);
  font-size: 0.84rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  position: relative;
  margin-bottom: 2px;
}

.nav-item:hover {
  background: var(--bg-sidebar-hover);
  color: #fff;
}

.nav-item.active {
  background: var(--bg-sidebar-active);
  color: #fff;
  font-weight: 600;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 6px;
  bottom: 6px;
  width: 3px;
  background: #93c5fd;
  border-radius: 0 3px 3px 0;
}

.nav-icon {
  font-size: 1rem;
  flex-shrink: 0;
  width: 20px;
  text-align: center;
  line-height: 1;
}

.nav-label {
  transition: opacity var(--transition);
  overflow: hidden;
}

.sidebar.collapsed .nav-label {
  opacity: 0;
  width: 0;
}

.sidebar-footer {
  padding: 12px 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.sidebar-footer-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  overflow: hidden;
}

.sidebar-footer-text {
  overflow: hidden;
  white-space: nowrap;
  transition: opacity var(--transition);
}

.sidebar.collapsed .sidebar-footer-text {
  opacity: 0;
  width: 0;
}

.sidebar-footer-label {
  font-size: 0.62rem;
  color: var(--text-sidebar-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.sidebar-footer-val {
  font-size: 0.72rem;
  color: #60a5fa;
  font-weight: 600;
  font-family: var(--font-mono);
}

/* Main Area */
.main-area {
  flex: 1;
  margin-left: var(--sidebar-width);
  transition: margin-left var(--transition-slow) cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-app);
}

.main-area.sidebar-collapsed {
  margin-left: var(--sidebar-collapsed-width);
}

/* Topbar */
.topbar {
  height: var(--topbar-height);
  background: #ffffff;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-xs);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.topbar-page-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
}

.topbar-page-subtitle {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 1px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: var(--radius-xl);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.topbar-badge.live {
  background: var(--accent-green-pale);
  color: var(--accent-green);
  border: 1px solid var(--accent-green-border);
}

.topbar-badge.demo {
  background: var(--accent-orange-pale);
  color: var(--accent-orange);
  border: 1px solid var(--accent-orange-border);
}

.topbar-badge.historical {
  background: var(--accent-primary-pale);
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary-border);
}

.topbar-date {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
}

/* Page Content */
.page-content {
  flex: 1;
  padding: 24px;
  max-width: 1600px;
  width: 100%;
}

/* Section Headers */
.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 16px;
}

.section-header-left {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.section-eyebrow {
  font-size: 0.63rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--accent-primary);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.section-subtitle {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 2px;
}

/* Cards */
.card {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--transition), border-color var(--transition);
}

.card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-strong);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.card-title {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 8px;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  position: relative;
  overflow: hidden;
  transition: all var(--transition);
  box-shadow: var(--shadow-card);
}

.kpi-card:hover {
  box-shadow: var(--shadow-lg);
  border-color: var(--accent-primary-border);
  transform: translateY(-2px);
}

.kpi-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--kpi-accent, var(--accent-primary));
  opacity: 0;
  transition: opacity var(--transition);
}

.kpi-card:hover::after {
  opacity: 1;
}

.kpi-label {
  font-size: 0.63rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.kpi-value {
  font-size: 1.65rem;
  font-weight: 800;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  line-height: 1;
  letter-spacing: -0.03em;
}

.kpi-value.positive { color: var(--accent-green); }
.kpi-value.negative { color: var(--accent-red); }
.kpi-value.index { color: var(--accent-primary); }

.kpi-unit {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 6px;
  line-height: 1.4;
}

.kpi-icon {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  background: #f1f5f9;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow-card);
  min-height: 300px;
}

.chart-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 3px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-subtitle {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-bottom: 14px;
}

/* Filter Panel */
.filter-panel, .filter-bar {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 20px;
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  align-items: flex-end;
  box-shadow: var(--shadow-card);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 150px;
}

.filter-label {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

.filter-select, .filter-input {
  background: #f8fafc;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  padding: 8px 12px;
  font-size: 0.85rem;
  font-family: var(--font-sans);
  outline: none;
  transition: all var(--transition-fast);
  -webkit-appearance: none;
  cursor: pointer;
}

.filter-select:focus, .filter-input:focus {
  border-color: var(--accent-primary);
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.12);
}

.filter-select:hover, .filter-input:hover {
  border-color: var(--border-strong);
}

input[type="date"].filter-input {
  cursor: pointer;
  min-width: 160px;
}

/* Buttons */
.btn-primary {
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 9px 20px;
  font-size: 0.85rem;
  font-weight: 600;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 1px 3px rgba(29, 78, 216, 0.3);
}

.btn-primary:hover {
  background: #1e40af;
  box-shadow: 0 4px 12px rgba(29, 78, 216, 0.35);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: #f8fafc;
  color: var(--text-secondary);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 8px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary:hover {
  background: #ffffff;
  border-color: var(--border-strong);
  color: var(--text-primary);
}

/* Anomaly Panel */
.anomaly-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.anomaly-item {
  background: #f8fafc;
  border: 1.5px solid var(--border);
  border-left: 4px solid var(--accent-red);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  position: relative;
  transition: all var(--transition-fast);
}

.anomaly-item:hover {
  box-shadow: var(--shadow-sm);
}

.anomaly-item.severity-medium { border-left-color: var(--accent-orange); }
.anomaly-item.severity-low { border-left-color: var(--accent-primary-light); }
.anomaly-item.severity-critical {
  border-left-color: #991b1b;
  background: var(--accent-red-pale);
}

.anomaly-item.is-demo::after {
  content: 'DEMO';
  position: absolute;
  top: 8px;
  right: 10px;
  font-size: 0.58rem;
  font-weight: 700;
  color: var(--accent-orange);
  background: var(--accent-orange-pale);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--accent-orange-border);
}

.anomaly-route {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.anomaly-fares {
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.anomaly-deviation {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.9rem;
}

.anomaly-deviation.positive { color: var(--accent-red); }
.anomaly-deviation.negative { color: var(--accent-green); }

.severity-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 9px;
  border-radius: 20px;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 6px;
}

.severity-badge.HIGH, .severity-badge.CRITICAL {
  background: var(--accent-red-pale);
  color: var(--accent-red);
  border: 1px solid var(--accent-red-border);
}

.severity-badge.MEDIUM {
  background: var(--accent-orange-pale);
  color: var(--accent-orange);
  border: 1px solid var(--accent-orange-border);
}

.severity-badge.LOW {
  background: var(--accent-primary-pale);
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary-border);
}

/* Prediction Card */
.prediction-card {
  background: #ffffff;
  border: 1.5px solid var(--accent-primary-border);
  border-radius: var(--radius);
  padding: 22px;
  box-shadow: var(--shadow-card);
}

.prediction-fare {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
  margin: 14px 0 6px;
  letter-spacing: -0.04em;
}

.prediction-range {
  font-size: 0.78rem;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}

.confidence-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.63rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-top: 8px;
}

.confidence-badge.high {
  background: var(--accent-green-pale);
  color: var(--accent-green);
  border: 1px solid var(--accent-green-border);
}

.confidence-badge.medium {
  background: var(--accent-orange-pale);
  color: var(--accent-orange);
  border: 1px solid var(--accent-orange-border);
}

.confidence-badge.low {
  background: var(--accent-red-pale);
  color: var(--accent-red);
  border: 1px solid var(--accent-red-border);
}

/* Index Display */
.index-display {
  text-align: center;
  padding: 16px;
}

.index-number {
  font-size: 3.4rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  background: linear-gradient(135deg, var(--accent-primary), #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  letter-spacing: -0.04em;
}

.index-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 8px;
}

.index-change {
  font-size: 0.88rem;
  font-weight: 700;
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 20px;
}

.index-change.up {
  background: var(--accent-red-pale);
  color: var(--accent-red);
}

.index-change.down {
  background: var(--accent-green-pale);
  color: var(--accent-green);
}

.index-note {
  font-size: 0.67rem;
  color: var(--text-muted);
  font-style: italic;
  margin-top: 14px;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  text-align: left;
  line-height: 1.5;
}

/* Status Banner */
.data-source-banner {
  padding: 7px 24px;
  text-align: center;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.data-source-banner.live {
  background: var(--accent-green-pale);
  color: var(--accent-green);
  border-bottom: 1px solid var(--accent-green-border);
}

.data-source-banner.demo {
  background: var(--accent-orange-pale);
  color: var(--accent-orange);
  border-bottom: 1px solid var(--accent-orange-border);
}

.data-source-banner.historical {
  background: var(--accent-primary-pale);
  color: var(--accent-primary);
  border-bottom: 1px solid var(--accent-primary-border);
}

/* Tab Bar */
.tab-bar {
  display: flex;
  gap: 2px;
  background: #f1f5f9;
  border-radius: var(--radius-sm);
  padding: 3px;
  width: fit-content;
  margin-bottom: 20px;
  border: 1px solid var(--border);
}

.tab-btn {
  padding: 7px 18px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-family: var(--font-sans);
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  background: #ffffff;
  color: var(--accent-primary);
  box-shadow: var(--shadow-sm);
}

/* Loading & Error */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: var(--text-muted);
  gap: 12px;
  font-size: 0.9rem;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  padding: 32px 24px;
  color: var(--accent-red);
  text-align: center;
  font-size: 0.88rem;
  background: var(--accent-red-pale);
  border-radius: var(--radius);
  border: 1px solid var(--accent-red-border);
}

.empty-state {
  padding: 40px 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
}

/* Live Dot Pulse */
@keyframes pulse-ring {
  0% { box-shadow: 0 0 0 0 rgba(5, 150, 105, 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(5, 150, 105, 0); }
  100% { box-shadow: 0 0 0 0 rgba(5, 150, 105, 0); }
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-green);
  display: inline-block;
  animation: pulse-ring 2s ease-in-out infinite;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* Chip */
.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.chip.blue {
  background: var(--accent-primary-pale);
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary-border);
}

.chip.green {
  background: var(--accent-green-pale);
  color: var(--accent-green);
  border: 1px solid var(--accent-green-border);
}

.chip.orange {
  background: var(--accent-orange-pale);
  color: var(--accent-orange);
  border: 1px solid var(--accent-orange-border);
}

/* Footer */
.dashboard-footer {
  padding: 20px 24px;
  border-top: 1px solid var(--border);
  background: #ffffff;
  color: var(--text-muted);
  font-size: 0.78rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.footer-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: var(--accent-primary-pale);
  border: 1px solid var(--accent-primary-border);
  border-radius: var(--radius-xl);
  color: var(--accent-primary);
  font-size: 0.72rem;
  font-weight: 600;
}

.footer-links {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.footer-disclaimer {
  width: 100%;
  font-size: 0.7rem;
  color: var(--text-muted);
  line-height: 1.5;
}

/* Page enter animation */
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-enter {
  animation: fadeSlideIn 0.22s ease forwards;
}

/* Plotly overrides */
.js-plotly-plot .plotly .modebar {
  display: none !important;
}

/* SVG Radar Map Text Contrast Overrides */
svg text {
  font-family: var(--font-sans);
}
#busy-airspace-zones text,
svg text[font-family="monospace"] {
  fill: #94a3b8 !important;
}
svg g text[fill="var(--text-primary)"] {
  fill: #f8fafc !important;
}
svg g text[fill="var(--text-secondary)"] {
  fill: #cbd5e1 !important;
}
svg g text[fill="var(--text-muted)"] {
  fill: #94a3b8 !important;
}

/* Light mode table styling */
table td, table th {
  color: #1e293b;
}
table th {
  color: #475569;
  font-weight: 600;
}
table tr:hover {
  background: rgba(241, 245, 249, 0.7) !important;
}

/* Responsive */
@media (max-width: 1280px) {
  .kpi-grid { grid-template-columns: repeat(3, 1fr); }
  .charts-grid { grid-template-columns: 1fr; }
}

@media (max-width: 1024px) {
  .sidebar { width: var(--sidebar-collapsed-width); }
  .sidebar .sidebar-brand-text,
  .sidebar .nav-label,
  .sidebar .sidebar-section-label,
  .sidebar .sidebar-footer-text { opacity: 0; width: 0; }
  .main-area { margin-left: var(--sidebar-collapsed-width); }
}

@media (max-width: 768px) {
  .page-content { padding: 16px; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-panel, .filter-bar { flex-direction: column; }
  .charts-grid { grid-template-columns: 1fr; }
}
'''

with open('frontend/src/index.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

with open('frontend/dist/assets/index-CVHLz7nN.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

print('Updated both frontend/src/index.css and frontend/dist/assets/index-CVHLz7nN.css')
