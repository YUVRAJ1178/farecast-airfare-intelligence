"""Anomaly detection routes."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Anomaly
from backend.app.schemas import AnomalyResponse
from backend.app.services.anomaly_service import run_anomaly_detection

router = APIRouter()


@router.get("/", response_model=List[AnomalyResponse])
async def get_anomalies(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    is_demo: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    List detected airfare anomalies.
    Demo anomalies are always marked is_demo=true.
    """
    query = db.query(Anomaly).filter(Anomaly.is_active == True)

    if origin:
        query = query.filter(Anomaly.origin == origin.upper())
    if destination:
        query = query.filter(Anomaly.destination == destination.upper())
    if severity:
        query = query.filter(Anomaly.severity == severity.upper())
    if is_demo is not None:
        query = query.filter(Anomaly.is_demo == is_demo)

    anomalies = query.order_by(Anomaly.detected_at.desc()).limit(limit).all()
    return anomalies


@router.post("/detect")
async def trigger_detection(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Trigger anomaly detection run.
    Detects and stores anomalies using IQR + Isolation Forest.
    """
    anomalies = run_anomaly_detection(
        db=db, origin=origin, destination=destination, save_to_db=True
    )
    return {
        "detected": len(anomalies),
        "note": "Demo anomalies are tagged is_demo=true. Live anomalies require real data.",
    }
