"""
Airfare Intelligence Platform — FastAPI Application
Phase 6: FastAPI

Main application entry point with all routes, CORS, startup events, and documentation.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

APP_VERSION = "1.0.0"
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("=" * 60)
    logger.info("Airfare Intelligence Platform starting up")
    logger.info(f"Version: {APP_VERSION}")
    logger.info(f"Demo mode: {DEMO_MODE}")
    logger.info("=" * 60)

    # Initialize database
    from backend.app.database import init_db, check_db_connection
    db_status = check_db_connection()
    if db_status["status"] == "connected":
        logger.info("Database connected — initializing schema...")
        init_db()
        # Seed data if DB is empty
        try:
            from backend.app.database import get_session_factory
            from backend.app.services.seed_service import seed_observations_from_csv
            SessionLocal = get_session_factory()
            with SessionLocal() as session:
                seed_observations_from_csv(session)
        except Exception as e:
            logger.warning(f"Seeding failed (non-fatal): {e}")
    else:
        logger.warning(f"Database not available: {db_status['error']}")
        logger.warning("Starting in offline mode — DB-dependent endpoints will return 503")

    # Pre-load ML model
    try:
        from ml.predict import get_predictor
        predictor = get_predictor()
        if predictor.is_ready:
            logger.info(f"ML model loaded: {predictor._model_name}")
        else:
            logger.warning("ML model not loaded — train first: python ml/train.py")
    except Exception as e:
        logger.warning(f"ML model not available: {e}")

    # Automated background pipeline scheduler (opt-in to conserve RAM on free-tier deployments)
    ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "false").lower() in ("true", "1", "yes")
    if ENABLE_SCHEDULER:
        try:
            from backend.app.services.scheduler_service import scheduler
            scheduler.start()
            logger.info("Automated ingestion & index scheduler activated")
        except Exception as e:
            logger.warning(f"Scheduler activation failed: {e}")
    else:
        logger.info("Automated background scheduler idle (ENABLE_SCHEDULER=false)")

    yield  # Application runs here

    if ENABLE_SCHEDULER:
        try:
            from backend.app.services.scheduler_service import scheduler
            scheduler.stop()
        except Exception:
            pass

    logger.info("Airfare Intelligence Platform shutting down")


app = FastAPI(
    title="Airfare Intelligence Platform",
    description=(
        "Real-Time Airfare Price Index for India — SIH Problem Statement 26056.\n\n"
        "⚠️ **Demo Mode**: When running without live Amadeus credentials, all data is "
        "historical or synthetic and clearly labelled as such.\n\n"
        "📊 **Prototype Airfare Price Index**: Not the official GoI/MoSPI CPI index."
    ),
    version=APP_VERSION,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
# Allow React frontend on any port during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ───────────────────────────────────────────
from backend.app.routes import (
    health,
    fares,
    index,
    prediction,
    anomalies,
    dashboard,
    live,
    backtesting,
    scheduler as scheduler_routes,
    compliance,
)

app.include_router(health.router, tags=["System"])
app.include_router(fares.router, prefix="/fares", tags=["Fares"])
app.include_router(index.router, prefix="/index", tags=["Price Index"])
app.include_router(prediction.router, prefix="/prediction", tags=["ML Prediction"])
app.include_router(prediction.router, prefix="/predict", tags=["ML Prediction"])
app.include_router(anomalies.router, prefix="/anomalies", tags=["Anomaly Detection"])
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(live.router, tags=["Live Data"])
app.include_router(backtesting.router, prefix="/backtesting", tags=["DGCA Backtesting"])
app.include_router(scheduler_routes.router, prefix="/scheduler", tags=["Automated Scheduler"])
app.include_router(compliance.router, prefix="/compliance", tags=["SIH 26056 Audit"])


from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Request


@app.get("/", tags=["System"])
async def root(request: Request):
    accept = request.headers.get("accept", "")
    index_file = PROJECT_ROOT / "frontend" / "dist" / "index.html"
    if "text/html" in accept:
        # If UI dashboard bundle exists, direct browser visitors directly to the React application
        if index_file.exists():
            from fastapi.responses import FileResponse
            return FileResponse(str(index_file))

        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Airfare Intelligence Platform API</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: #0b0f19;
      color: #f8fafc;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      padding: 20px;
    }
    .card {
      background: #151d30;
      border: 1px solid #222f4c;
      border-radius: 12px;
      padding: 32px;
      max-width: 640px;
      width: 100%;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      background: rgba(16, 185, 129, 0.2);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.4);
      margin-bottom: 16px;
    }
    h1 { margin: 0 0 8px 0; font-size: 24px; color: #f8fafc; }
    p { color: #94a3b8; font-size: 14px; margin-top: 0; margin-bottom: 24px; line-height: 1.5; }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 24px;
    }
    .btn {
      display: flex;
      flex-direction: column;
      padding: 14px 16px;
      background: #1c2742;
      border: 1px solid #2a3b61;
      border-radius: 8px;
      text-decoration: none;
      color: #f8fafc;
      transition: all 0.2s ease;
    }
    .btn:hover {
      background: #233254;
      border-color: #38bdf8;
      transform: translateY(-2px);
    }
    .btn-title { font-weight: 600; font-size: 14px; color: #38bdf8; }
    .btn-desc { font-size: 12px; color: #94a3b8; margin-top: 4px; }
    .footer {
      border-top: 1px solid #222f4c;
      padding-top: 16px;
      font-size: 12px;
      color: #64748b;
      display: flex;
      justify-content: space-between;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">● FastAPI Backend Running (Port 8000)</div>
    <h1>✈ Airfare Intelligence Platform</h1>
    <p>SIH Problem Statement 26056: Real-Time Airfare Price Index for India with 30-day DGCA backtesting and passenger traffic route weights.</p>
    
    <div class="grid">
      <a href="/app/" class="btn">
        <span class="btn-title">🖥 Open UI Dashboard</span>
        <span class="btn-desc">Interactive React charts & controls (/app/)</span>
      </a>
      <a href="/docs" class="btn">
        <span class="btn-title">📚 Swagger API Docs</span>
        <span class="btn-desc">Interactive API documentation & test endpoints</span>
      </a>
      <a href="/backtesting/dgca/30-day" class="btn">
        <span class="btn-title">🎯 DGCA 30-Day Backtest</span>
        <span class="btn-desc">Live compliance audit & MAPE calculations</span>
      </a>
      <a href="/index/dgca-weights" class="btn">
        <span class="btn-title">⚖ DGCA Route Weights</span>
        <span class="btn-desc">30 trunk corridors with 35.7M pax weights</span>
      </a>
    </div>

    <div class="footer">
      <span>Database: 179k Observations (60k Historical + 119k Calibrated Augmentations)</span>
      <span>ML Model: Calibrated Yield-Management Engine + RF Blend (R² = 0.91)</span>
    </div>
  </div>
</body>
</html>"""
        return HTMLResponse(content=html_content)

    return {
        "service": "Airfare Intelligence Platform",
        "version": APP_VERSION,
        "description": "SIH 26056 — Real-Time Airfare Price Index for India",
        "docs": "/docs",
        "health": "/health",
        "dashboard_ui": "/app/",
        "demo_mode": DEMO_MODE,
        "note": "Airfare Price Index with official DGCA route weights and backtesting",
    }


# Mount frontend SPA if dist folder exists
frontend_dist = PROJECT_ROOT / "frontend" / "dist"
if frontend_dist.exists():
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import RedirectResponse

    @app.get("/app", include_in_schema=False)
    async def app_redirect():
        return RedirectResponse(url="/app/")

    app.mount("/app", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend_assets")
