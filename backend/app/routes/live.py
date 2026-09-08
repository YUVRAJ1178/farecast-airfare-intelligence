"""
Live fare search routes.

Active provider : Ignav  (POST /live/ignav/search)
Legacy provider : Amadeus (POST /live/search  — kept for backward compatibility)
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import AirfareObservation
from backend.app.schemas import (
    AmadeusSearchRequest,
    AmadeusSearchResponse,
    FareObservationResponse,
    IgnavSearchRequest,
    IgnavSearchResponse,
)
from backend.app.services.amadeus_service import get_amadeus_service
from backend.app.services.ignav_service import get_ignav_service

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# PRIMARY: Ignav live fare search  (REAL_API  provider)
# ─────────────────────────────────────────────────────────────

@router.post("/live/ignav/search", response_model=IgnavSearchResponse, tags=["Live Data"])
async def search_ignav_flights(
    request: IgnavSearchRequest,
    save: bool = True,
    db: Session = Depends(get_db),
):
    """
    Search for live one-way flights using the Ignav Flight Prices API.

    - Requires IGNAV_API_KEY in .env (server-side only — never sent to frontend)
    - Results tagged source='ignav', source_provenance='REAL_API'
    - Fields not provided by Ignav are stored as NULL — no fabrication
    - If IGNAV_API_KEY not set, returns 503 with instructions
    """
    ignav = get_ignav_service()

    if not ignav.is_available:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Ignav API key not configured",
                "action": (
                    "Set IGNAV_API_KEY in your .env file. "
                    "Register at https://ignav.com"
                ),
                "mode": "historical",
                "message": "App is running in Historical/Demo mode without live fares.",
            },
        )

    fares = ignav.search_flights(
        origin=request.origin,
        destination=request.destination,
        departure_date=request.departure_date,
        adults=request.adults,
        cabin_class=request.cabin_class,
        max_stops=request.max_stops,
        market=request.market,
    )

    saved_ids: list[int] = []
    if save and fares:
        # Only persist DB-schema fields; strip Ignav-internal metadata keys (_ignav_id etc.)
        db_fields = {c.key for c in AirfareObservation.__table__.columns}
        for fare_dict in fares:
            clean = {k: v for k, v in fare_dict.items() if k in db_fields}
            obs = AirfareObservation(**clean)
            db.add(obs)
        db.flush()
        db.commit()

    # Build response (assign id=0 for unsaved, real id after flush above)
    fare_responses: list[FareObservationResponse] = []
    valid_fields = set(FareObservationResponse.model_fields)
    for f in fares:
        fare_responses.append(
            FareObservationResponse(
                id=0,
                **{k: v for k, v in f.items() if k in valid_fields},
            )
        )

    return IgnavSearchResponse(
        source="ignav",
        provider="Ignav",
        origin=request.origin,
        destination=request.destination,
        departure_date=request.departure_date,
        results_count=len(fares),
        fares=fare_responses,
        fetched_at=datetime.utcnow(),
    )


# ─────────────────────────────────────────────────────────────
# LEGACY: Amadeus live search  (kept for backward compatibility)
# ─────────────────────────────────────────────────────────────

@router.post("/live/search", response_model=AmadeusSearchResponse, tags=["Live Data"])
async def search_live_flights(
    request: AmadeusSearchRequest,
    save: bool = True,
    db: Session = Depends(get_db),
):
    """
    [LEGACY] Search for live flights using Amadeus API.
    The active live provider is now Ignav — use POST /live/ignav/search instead.

    - Requires AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET in .env
    - Results tagged source='amadeus', source_provenance='REAL_API'
    """
    amadeus = get_amadeus_service()

    if not amadeus.is_available:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Amadeus API credentials not configured",
                "action": (
                    "Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET in your .env file. "
                    "Register at https://developers.amadeus.com/ — "
                    "Or use the active provider: POST /live/ignav/search"
                ),
                "mode": "demo",
                "message": "App is running in Historical/Demo mode.",
            },
        )

    fares = amadeus.search_flights(
        origin=request.origin,
        destination=request.destination,
        departure_date=request.departure_date,
        adults=request.adults,
        cabin_class=request.cabin_class,
    )

    if save and fares:
        db_fields = {c.key for c in AirfareObservation.__table__.columns}
        for fare_dict in fares:
            clean = {k: v for k, v in fare_dict.items() if k in db_fields}
            obs = AirfareObservation(**clean)
            db.add(obs)
        db.commit()

    fare_responses: list[FareObservationResponse] = []
    valid_fields = set(FareObservationResponse.model_fields)
    for f in fares:
        fare_responses.append(
            FareObservationResponse(
                id=0,
                **{k: v for k, v in f.items() if k in valid_fields},
            )
        )

    return AmadeusSearchResponse(
        origin=request.origin,
        destination=request.destination,
        departure_date=request.departure_date,
        results_count=len(fares),
        fares=fare_responses,
        fetched_at=datetime.utcnow(),
    )


# ─────────────────────────────────────────────────────────────
# Live-status endpoint
# ─────────────────────────────────────────────────────────────

@router.get("/live-status", tags=["Live Data"])
async def live_status():
    """
    Returns the live data source status for all configured providers.
    Reports whether Ignav (primary) and Amadeus (legacy) are active.
    """
    ignav = get_ignav_service()
    amadeus = get_amadeus_service()

    ignav_status = ignav.get_status()
    amadeus_status = amadeus.get_status()

    overall = "live" if ignav_status["status"] in ("active", "configured") else "historical"

    return {
        "overall_mode": overall,
        "primary_provider": "ignav",
        "ignav": ignav_status,
        "amadeus": amadeus_status,
        "note": (
            "Ignav is the active REAL_API_FARES provider. "
            "Amadeus is retained as a legacy fallback. "
            "source_provenance=REAL_API for all live data."
        ),
    }

