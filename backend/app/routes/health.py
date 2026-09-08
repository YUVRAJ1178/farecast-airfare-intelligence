"""Health, system status routes."""
import os
from datetime import datetime

from fastapi import APIRouter

APP_VERSION = "1.0.0"
router = APIRouter()
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")


@router.get("/health")
async def health():
    from backend.app.database import check_db_connection
    from ml.predict import get_predictor
    from backend.app.services.amadeus_service import get_amadeus_service
    from backend.app.services.ignav_service import get_ignav_service

    db_status = check_db_connection()
    predictor = get_predictor()
    amadeus = get_amadeus_service()
    ignav = get_ignav_service()

    return {
        "status": "ok",
        "version": APP_VERSION,
        "database": db_status["status"],
        "ml_model": "ready" if predictor.is_ready else "not_trained",
        "ignav": "configured" if ignav.is_available else "not_configured",
        "amadeus": "configured" if amadeus.is_available else "not_configured",
        "live_provider": "ignav" if ignav.is_available else ("amadeus" if amadeus.is_available else "none"),
        "demo_mode": DEMO_MODE,
        "timestamp": datetime.now(),
    }

