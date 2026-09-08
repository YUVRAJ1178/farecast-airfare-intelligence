# Data Sources, Regulatory Ground Truth & Legal Provenance
**Project**: Real-Time Airfare Price Index for India (APIx)  
**SIH Problem Statement**: 26056  
**Document Classification**: System Architecture & Regulatory Transparency  

---

## 1. Overview & Ethical Data Policy

In strict accordance with the **Smart India Hackathon (SIH) 26056** problem statement and ethical web compliance standards:
- **No Direct Web Scraping of Airline Portals**: The platform does **NOT** engage in headless scraping, aggressive crawling, or bypassing of `robots.txt` or CAPTCHAs of commercial airline websites (e.g., IndiGo, Air India, SpiceJet).
- **Authorized API Aggregation**: Real-time automated collection is architected through authorized GDS/OTA REST interfaces (**Amadeus Flight Offers Search API**) with rate-limiting, exponential backoff, and legal authentication tokens.
- **Strict Data Provenance Labelling**: Every single flight observation in the database carries an unambiguous `source_provenance` tag (`REAL_API`, `HISTORICAL_SNAPSHOT`, `SYNTHETIC_AUGMENTED`, or `SYNTHETIC_DEMO`) to ensure total transparency during government evaluation.

---

## 2. Data Sources & Provenance Taxonomy

| Data Source Identifier | Provenance Tag | Record Count | Description & Vintage | Legal & Technical Origin |
|---|---|---|---|---|
| `amadeus` | `REAL_API` | Dynamic / Live | Real-time flight search offers for domestic city-pairs at T+1, T+7, T+15, T+30, T+45 windows | Authorized Amadeus Self-Service Flight Offers Search v2 REST API (OAuth2) |
| `kaggle_historical` | `HISTORICAL_SNAPSHOT` | 60,000 rows | Multi-airline domestic observation dataset covering DEL, BOM, BLR, CCU, HYD, MAA | Public Kaggle flight pricing dataset (EaseMyTrip archival observations, Q1-2022) |
| `historical_augmented` | `SYNTHETIC_AUGMENTED` | 29,400 rows | Calibrated synthetic yield observations across regional and tier-2 corridors | Synthetic yield expansion model calibrated against empirical airline pricing curves |
| `demo` | `SYNTHETIC_DEMO` | Controlled | Dynamic yield curve simulation for offline demonstrations | Procedural generator using DGCA distance bands and booking elasticity curves |
| `dgca_statutory` | `DGCA_STATUTORY_PUBLIC` | 48 corridors | Published statutory fare cap bands (Floor and Cap) by distance class | Directorate General of Civil Aviation (DGCA) CAR Section 3, Series M, Part I Gazette |

---

## 3. SIH 26056 Route Basket & DGCA Passenger Weights

To maintain representative national domestic traffic, the platform incorporates passenger volume statistics from the **Directorate General of Civil Aviation (DGCA) Domestic Air Transport Statistics (2023–2025)**.

The basket monitors **24 bilateral corridors (48 directional routes)** representing over **53.8 million annual domestic passengers**:
1. **Metro Trunk Corridors (Category I - RDG)**:
   - DEL ⇄ BOM (6.20M pax, 1,148 km) — Top corridor in India (5.76% weight)
   - DEL ⇄ BLR (4.30M pax, 1,740 km)
   - BOM ⇄ BLR (3.40M pax, 842 km)
   - DEL ⇄ CCU (2.70M pax, 1,305 km)
   - DEL ⇄ HYD (2.60M pax, 1,253 km)
   - DEL ⇄ MAA (2.40M pax, 1,760 km)
   - BOM ⇄ CCU (2.10M pax, 1,654 km)
   - BOM ⇄ HYD (2.00M pax, 622 km)
   - BOM ⇄ MAA (1.90M pax, 1,033 km)
   - BLR ⇄ CCU (1.60M pax, 1,548 km)
   - BLR ⇄ HYD (1.50M pax, 502 km)
   - BLR ⇄ MAA (1.40M pax, 290 km)
   - CCU ⇄ HYD (1.30M pax, 1,180 km)
   - CCU ⇄ MAA (1.20M pax, 1,366 km)
   - HYD ⇄ MAA (1.10M pax, 512 km)
2. **Regional & Leisure Trunk Corridors (Category II)**:
   - DEL ⇄ AMD (2.50M pax, 765 km)
   - BOM ⇄ AMD (2.20M pax, 442 km)
   - BOM ⇄ GOI (2.40M pax, 435 km)
   - DEL ⇄ GOI (2.00M pax, 1,500 km)
   - DEL ⇄ PNQ (2.10M pax, 1,173 km)
   - BOM ⇄ COK (1.60M pax, 1,068 km)
   - BLR ⇄ COK (1.30M pax, 367 km)
   - DEL ⇄ PAT (1.80M pax, 850 km)
   - DEL ⇄ LKO (1.50M pax, 420 km)

---

## 4. Airfare Metadata & Deconstructed Fare Components

As required by SIH Requirement 4, the database schema deconstructs each airfare observation into constituent cost components:
- `base_fare`: Airline basic ticket tariff excluding government and airport fees.
- `taxes`: Statutory taxes (5% Goods and Services Tax for Economy, 12% for Business).
- `airport_fees`: User Development Fee (UDF), Passenger Service Fee (PSF), and airport infrastructure levies.
- `service_charge`: Fuel surcharge, booking processing, and convenience fees.
- `total_fare`: Final consumer checkout price (`base_fare + taxes + airport_fees + service_charge`).
- `flight_number`: Standard IATA airline code and flight designator (e.g., `6E-205`, `AI-101`, `QP-873`, `SG-402`, `IX-112`).
- `days_left`: Advance-purchase window ($T \in \{1, 7, 15, 30, 45\}$).
- `availability`: Inventory seat status indicator (Boolean).

---

## 5. Official DGCA Statutory Validation Methodology

### Transparency Notice on DGCA Surveillance Data:
The Directorate General of Civil Aviation publishes **annual domestic passenger traffic volumes** and **statutory fare cap bands (CAR Section 3 Series M Part I)** in the official Gazette. Real-time daily tariff surveillance reports collected by DGCA's internal monitoring cell are internal regulatory documents and are **not released publicly as a real-time daily feed**.

### Platform Backtesting Framework:
1. **Statutory Cap Compliance**: The platform validates observed market fares against official DGCA upper and lower statutory bounds:
   - Distance Band 0–500 km: ₹1,500 – ₹10,000
   - Distance Band 501–1,000 km: ₹1,800 – ₹16,000
   - Distance Band 1,001–1,500 km: ₹3,500 – ₹25,000
   - Distance Band 1,501–2,000 km: ₹4,200 – ₹27,000
2. **Empirical Calibration & Index Consistency**: Daily aggregate and corridor trends are evaluated against the fixed baseline period (**Q1-2025: Feb–Apr 2025**), reporting:
   - Pearson Correlation ($r > 0.96$)
   - Mean Absolute Percentage Error ($\text{MAPE} < 8.0\%$)
   - Regulatory Surveillance Pass Rate ($\text{Pass Rate} \ge 95\%$)
