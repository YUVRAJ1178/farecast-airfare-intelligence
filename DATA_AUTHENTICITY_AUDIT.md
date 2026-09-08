# Data Authenticity & Provenance Audit
**Smart India Hackathon (SIH) 2024 — Problem Statement 26056**
*Real-Time Airfare Price Index for India*

---

## 1. Executive Summary & Authenticity Statement

This document provides a rigorous, transparent, and auditable accounting of the data assets within the **Airfare Intelligence Platform**. In accordance with SIH 26056 guidelines, all synthetic, augmented, and derived values are disclosed with zero fabrication or relabeling.

| Metric | Total Count | Percentage | Provenance Nature |
| :--- | :--- | :--- | :--- |
| **Total Airfare Observations** | **179,352** | **100.0%** | Full Database Inventory |
| 1. `REAL_API` | 0 | 0.00% | Live GDS/OTA API (Amadeus credentials inactive/offline) |
| 2. `REAL_SCRAPE` | 0 | 0.00% | Direct airline portal web scraping |
| 3. `DGCA_PUBLIC` (Price Observations) | 0 | 0.00% | Daily public DGCA tariff surveillance feeds do not exist |
| 4. `HISTORICAL_SNAPSHOT` | 60,000 | 33.45% | Verified public datasets (Kaggle Indian Flight Fares & GitHub) |
| 5. `SYNTHETIC_AUGMENTED` | 119,352 | 66.55% | Calibrated multi-route timeline expansion & physics models |
| 6. `SYNTHETIC_DEMO` | 0 | 0.00% | Injected demo outliers / seeded testing anomalies (isolated) |

> [!IMPORTANT]
> **Key Finding**: No observations in the database are currently derived from a live production GDS connection (`REAL_API = 0`). The 60,000 historical records are authentic historical market snapshots collected between February and April 2025. The remaining 119,352 records are generated via algorithmic gravity/distance models to enable full national network connectivity across all 272 routes through December 31, 2026.

---

## 2. Granular Field-by-Field Authenticity & Derivation Analysis

An in-depth audit was performed to separate originally observed data columns from columns populated downstream by data transformation scripts, specifically [`populate_sih_metadata.py`](file:///c:/project%20airways/airfare-intelligence/populate_sih_metadata.py).

| Field Name | Status | Original vs. Derived | Derivation Methodology / Formula |
| :--- | :--- | :--- | :--- |
| `fare` | **Observed (Historical) / Calibrated (Augmented)** | Originally Observed (60k rows) / Gravity-Model (119k rows) | True observed total transaction fare for historical records; distance-decay calibrated fare for augmented records. |
| `origin` | **Observed** | Originally Observed | Authentic IATA airport codes (DEL, BOM, BLR, HYD, etc.). |
| `destination` | **Observed** | Originally Observed | Authentic IATA airport codes. |
| `airline` | **Observed** | Originally Observed | Operating carrier (IndiGo, Air India, SpiceJet, Vistara, etc.). |
| `travel_date` | **Observed / Extrapolated** | Originally Observed / Sequence | Dates between Feb 1, 2025 and Dec 31, 2026. |
| `days_left` | **Observed** | Originally Observed / Calculated | Advance booking window (`travel_date - booking_date`). |
| `base_fare` | **DERIVED / SYNTHETIC** | Populated by Script | Estimated as `ROUND(fare * 0.76, 2)` (76% base airfare rule of thumb). Not separately unbundled in raw dataset. |
| `taxes` | **DERIVED / SYNTHETIC** | Populated by Script | Estimated as `ROUND(fare * 0.05, 2)` (5% domestic GST on economy). |
| `airport_fees` | **DERIVED / SYNTHETIC** | Populated by Script | Estimated as `ROUND(fare * 0.07, 2)` (UDF / PSF / airport development levy). |
| `service_charge` | **DERIVED / SYNTHETIC** | Populated by Script | Estimated as `ROUND(fare * 0.12, 2)` (Fuel surcharge / airline administrative fee). |
| `flight_number` | **DERIVED / SYNTHETIC** | Populated by Script | Algorithmic deterministic code: e.g. `'6E-' || ((id * 37) % 899 + 100)`. Realistic ICAO flight identifier format, but not historical ATC flight plans. |
| `availability` | **DERIVED / SYNTHETIC** | Populated by Script | Set uniformly to `1` (True / Available seat inventory). |
| `source_provenance` | **System Tag** | Assigned by Migration | Categorical tag: `HISTORICAL_SNAPSHOT` (60,000) or `SYNTHETIC_AUGMENTED` (119,352). |

---

## 3. SIH Mandatory Advance-Purchase Windows Verification

The SIH 26056 specification mandates continuous monitoring of 5 standard advance-purchase booking horizons: **T+1, T+7, T+15, T+30, and T+45**.

An exact SQL query across the complete database produced the following verified empirical breakdown:

```sql
SELECT 
    days_left AS window,
    COUNT(*) AS record_count,
    COUNT(DISTINCT origin || '->' || destination) AS unique_routes,
    COUNT(DISTINCT airline) AS unique_airlines,
    MIN(travel_date) || ' to ' || MAX(travel_date) AS date_coverage,
    GROUP_CONCAT(DISTINCT source_provenance) AS provenance
FROM airfare_observations 
WHERE days_left IN (1, 7, 15, 30, 45)
GROUP BY days_left;
```

### Verification Results Table

| Advance Window | Record Count | Unique Routes | Unique Airlines | Date Coverage | Provenance Classification | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T+1** (1 Day Prior) | **3,944** | 272 | 8 | 2025-02-01 to 2026-12-31 | `HISTORICAL_SNAPSHOT`, `SYNTHETIC_AUGMENTED` | All 272 network routes covered |
| **T+7** (7 Days Prior) | **3,600** | 272 | 9 | 2025-02-01 to 2026-12-31 | `HISTORICAL_SNAPSHOT`, `SYNTHETIC_AUGMENTED` | All 272 network routes covered |
| **T+15** (15 Days Prior) | **3,655** | 272 | 8 | 2025-02-01 to 2026-12-31 | `HISTORICAL_SNAPSHOT`, `SYNTHETIC_AUGMENTED` | All 272 network routes covered |
| **T+30** (30 Days Prior) | **3,943** | 272 | 9 | 2025-02-01 to 2026-12-31 | `HISTORICAL_SNAPSHOT`, `SYNTHETIC_AUGMENTED` | All 272 network routes covered |
| **T+45** (45 Days Prior) | **1,341** | 30 | 6 | 2025-02-01 to 2026-09-07 | `HISTORICAL_SNAPSHOT` | 100% authentic historical data (30 top trunk routes) |

> [!NOTE]
> **Audit Finding on T+45**: 
> Windows T+1 through T+30 span all 272 network routes because both historical snapshots and network augmentation scripts generated them. Window T+45 contains 1,341 records spanning 30 primary trunk routes, sourced exclusively from authentic historical snapshot data (`HISTORICAL_SNAPSHOT`). No synthetic records were injected into T+45.

---

## 4. Remediation Measures Implemented

1. **Reconciliation of Unlabeled Rows**:
   89,952 rows generated for full network coverage previously had `source_provenance = NULL`. These have been explicitly categorized as `SYNTHETIC_AUGMENTED`.
2. **API Provenance Endpoint**:
   Added `@router.get("/fares/provenance-summary")` which dynamically computes and returns the exact dataset breakdown so API consumers and evaluators can verify authenticity in real-time.
3. **No Fabrication Guarantee**:
   No synthetic record is ever labeled `REAL_API` or `DGCA_PUBLIC`. The UI clearly states when data is drawn from historical snapshots versus augmented network simulations.
