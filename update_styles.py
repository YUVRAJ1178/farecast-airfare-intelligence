"""
update_styles.py
Applies comprehensive, beautiful styles for Route Fare Index KPI cards,
sidebar branding, and eliminates the right margin.
"""

def get_kpi_css():
    return '''
/* ============================================================
   FARECAST — ROUTE FARE INDEX KPI CARDS & DASHBOARD ENHANCEMENTS
   ============================================================ */

/* 1. Main Area Layout - No empty right space */
.main-area,
.main-area.with-right-panel {
  margin-left: 260px !important;
  margin-right: 0 !important;
  max-width: calc(100vw - 260px) !important;
  width: auto !important;
  flex: 1 1 auto !important;
  box-sizing: border-box !important;
  transition: margin-left 0.25s ease !important;
}

.sidebar-collapsed .main-area,
.main-area.sidebar-collapsed {
  margin-left: 72px !important;
  max-width: calc(100vw - 72px) !important;
}

/* 2. Sidebar Branding & Tagline — No truncation, no ellipsis */
.sidebar {
  width: 260px !important;
  background: #ffffff !important;
  border-right: 1px solid #e2e8f0 !important;
}

.sidebar.collapsed {
  width: 72px !important;
}

.sidebar-brand {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  padding: 16px 14px !important;
  border-bottom: 1px solid #f1f5f9 !important;
  overflow: visible !important;
}

.sidebar-brand-text {
  flex: 1 1 auto !important;
  min-width: 0 !important;
  overflow: visible !important;
  white-space: normal !important;
  display: flex !important;
  flex-direction: column !important;
}

.sidebar-name {
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
  font-size: 1.2rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.02em !important;
  color: #1d4ed8 !important;
  line-height: 1.15 !important;
}

.sidebar-tagline {
  font-size: 0.62rem !important;
  color: #64748b !important;
  font-weight: 500 !important;
  margin-top: 3px !important;
  line-height: 1.25 !important;
  white-space: normal !important;
  word-wrap: break-word !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

/* Hide Powered by AI if present */
.sidebar-ai-pill,
.sidebar-powered {
  display: none !important;
}

/* 3. Route Fare Index KPI Cards Grid */
.kpi-grid,
.rfi-kpi-grid,
.rfi-kpi-subcards {
  display: grid !important;
  grid-template-columns: repeat(5, 1fr) !important;
  gap: 16px !important;
  margin: 16px 0 24px 0 !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

@media (max-width: 1280px) {
  .kpi-grid,
  .rfi-kpi-grid,
  .rfi-kpi-subcards {
    grid-template-columns: repeat(3, 1fr) !important;
  }
}

@media (max-width: 820px) {
  .kpi-grid,
  .rfi-kpi-grid,
  .rfi-kpi-subcards {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

@media (max-width: 540px) {
  .kpi-grid,
  .rfi-kpi-grid,
  .rfi-kpi-subcards {
    grid-template-columns: 1fr !important;
  }
}

/* 4. Individual KPI Card Styling */
.kpi-card,
.rfi-kpi-card,
.kpi-subcard {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 12px !important;
  padding: 16px 18px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  position: relative !important;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02) !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  min-height: 110px !important;
  box-sizing: border-box !important;
}

.kpi-card:hover,
.rfi-kpi-card:hover,
.kpi-subcard:hover {
  border-color: #cbd5e1 !important;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08) !important;
  transform: translateY(-2px) !important;
}

/* Icons in KPI cards */
.kpi-icon {
  font-size: 1.3rem !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 34px !important;
  height: 34px !important;
  border-radius: 8px !important;
  background: #f1f5f9 !important;
  margin-bottom: 8px !important;
}

#kpi-avg-fare .kpi-icon { background: #dcfce7 !important; color: #16a34a !important; }
#kpi-min-fare .kpi-icon { background: #e0f2fe !important; color: #0284c7 !important; }
#kpi-max-fare .kpi-icon { background: #fee2e2 !important; color: #dc2626 !important; }
#kpi-price-index .kpi-icon { background: #f3e8ff !important; color: #9333ea !important; }
#kpi-observations .kpi-icon { background: #e0f2fe !important; color: #0891b2 !important; }

/* Labels */
.kpi-label,
.rfi-kpi-label,
.kpi-subcard-label {
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  color: #64748b !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
  margin-bottom: 6px !important;
}

/* Values */
.kpi-value,
.rfi-kpi-val,
.kpi-subcard-val {
  font-size: 1.45rem !important;
  font-weight: 800 !important;
  color: #0f172a !important;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
  line-height: 1.2 !important;
  margin-bottom: 4px !important;
  letter-spacing: -0.02em !important;
}

.kpi-value.positive, .rfi-kpi-val.positive, .kpi-subcard-val.positive {
  color: #059669 !important;
}
.kpi-value.negative, .rfi-kpi-val.negative, .kpi-subcard-val.negative {
  color: #dc2626 !important;
}
.kpi-value.index, .rfi-kpi-val.purple, .kpi-subcard-val.purple {
  color: #7c3aed !important;
}

/* Units & Subtitles */
.kpi-unit,
.rfi-kpi-sub,
.kpi-subcard-sub {
  font-size: 0.68rem !important;
  color: #64748b !important;
  margin-top: auto !important;
  line-height: 1.3 !important;
}

.kpi-unit.positive, .rfi-kpi-sub.green, .kpi-subcard-sub.green {
  color: #059669 !important;
  font-weight: 600 !important;
}

/* Filter panel in Route Fare Index */
.filter-panel {
  display: flex !important;
  gap: 12px !important;
  align-items: flex-end !important;
  flex-wrap: wrap !important;
  background: #ffffff !important;
  padding: 16px 20px !important;
  border-radius: 12px !important;
  border: 1px solid #e2e8f0 !important;
  margin-bottom: 20px !important;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03) !important;
}

.filter-group {
  display: flex !important;
  flex-direction: column !important;
  gap: 5px !important;
  flex: 1 1 130px !important;
  min-width: 120px !important;
}

.filter-label {
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  color: #64748b !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
}

.filter-select,
.filter-input {
  font-size: 0.82rem !important;
  padding: 8px 12px !important;
  border-radius: 8px !important;
  background: #f8fafc !important;
  color: #0f172a !important;
  border: 1px solid #cbd5e1 !important;
  outline: none !important;
  transition: border-color 0.15s ease !important;
  box-sizing: border-box !important;
  width: 100% !important;
}

.filter-select:focus,
.filter-input:focus {
  border-color: #3b82f6 !important;
  background: #ffffff !important;
}

/* Buttons */
.btn-primary {
  background: #1d4ed8 !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 4px rgba(29, 78, 216, 0.2) !important;
  transition: all 0.15s ease !important;
}

.btn-primary:hover {
  background: #1e40af !important;
  box-shadow: 0 4px 8px rgba(29, 78, 216, 0.3) !important;
  transform: translateY(-1px) !important;
}

.btn-secondary {
  background: #f1f5f9 !important;
  color: #334155 !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  transition: all 0.15s ease !important;
}

.btn-secondary:hover {
  background: #e2e8f0 !important;
}
'''

def main():
    css_addition = get_kpi_css()
    
    # Update frontend/src/index.css
    with open('frontend/src/index.css', 'a', encoding='utf-8') as f:
        f.write('\n' + css_addition)
    print("Appended to frontend/src/index.css")
    
    # Update frontend/dist/assets/index-CVHLz7nN.css
    with open('frontend/dist/assets/index-CVHLz7nN.css', 'a', encoding='utf-8') as f:
        f.write('\n' + css_addition)
    print("Appended to frontend/dist/assets/index-CVHLz7nN.css")

if __name__ == '__main__':
    main()
