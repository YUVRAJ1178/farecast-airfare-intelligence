# 🚀 Production Deployment Guide — Airfare Intelligence Platform (FareCast)
**Smart India Hackathon Problem Statement 26056: Real-Time Airfare Price Index for India**

---

## 1. Production Architecture Overview

```
 [ Public Internet / Evaluators / Mobile ]
                     │  (Public HTTPS)
                     ▼
         [ Cloudflare Global Edge ]
   (SSL termination, DDoS protection, CDN)
                     │  (Encrypted QUIC/HTTP2 Tunnel)
                     ▼
       [ Cloudflare Tunnel Client ]
       (bin/cloudflared.exe Daemon)
                     │  (127.0.0.1:8000)
                     ▼
        [ FastAPI Production Core ]
         ├── Static SPA Mount (/app/, /assets/)
         ├── REST API Engine (/health, /prediction, /live/ignav, /fares, /index)
         ├── Yield-Management + RF Machine Learning Model Blend
         ├── Server-Side Secret Management (.env / IGNAV_API_KEY)
         └── SQLite High-Performance Engine (airfare.db — 179k Observations)
```

---

## 2. Active Production URLs

- **Frontend Dashboard (SPA)**: `https://ozone-functionality-displays-passion.trycloudflare.com/app/`
- **Backend API Base**: `https://ozone-functionality-displays-passion.trycloudflare.com/`
- **Interactive Swagger Documentation**: `https://ozone-functionality-displays-passion.trycloudflare.com/docs`
- **System Health**: `https://ozone-functionality-displays-passion.trycloudflare.com/health`
- **Live Ignav Search**: `https://ozone-functionality-displays-passion.trycloudflare.com/live/ignav/search`
- **DGCA 30-Day Backtesting**: `https://ozone-functionality-displays-passion.trycloudflare.com/backtesting/dgca/30-day`

---

## 3. Security & Secret Configuration

1. **Server-Side API Key Isolation**:
   - `IGNAV_API_KEY` is loaded exclusively inside Python processes via `.env`.
   - The key is **never** sent to the client browser, never embedded in JS bundles, and never logged in console outputs.
   - All live requests originate server-side from FastAPI to the Ignav Flight Prices API.
2. **Git Hygiene**:
   - `.env`, `*.env`, `bin/`, and `*.exe` are strictly listed in `.gitignore`.
3. **CORS & Zero Localhost Dependencies**:
   - The frontend dynamically determines the API base URL via `window.location.origin`.
   - No hardcoded `localhost:8000` remains in the client bundle.
   - Works uniformly across HTTP, HTTPS, local ports, and external domains.

---

## 4. Redeployment & Management Instructions

### To Start the Production Stack:
Run the production launcher:
```powershell
py -3 start_production.py
```

### To Run Standalone:
1. Start the FastAPI backend with Windows Selector event loop policy:
   ```powershell
   py -3 run_server.py
   ```
2. In a separate terminal, launch the Cloudflare tunnel:
   ```powershell
   .\bin\cloudflared.exe tunnel --url http://127.0.0.1:8000
   ```

### To Verify Health & Endpoints:
```powershell
py -3 test_production_deploy.py
```
