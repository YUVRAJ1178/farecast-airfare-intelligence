"""
Airfare Intelligence Platform — DGCA Backtesting Routes
Phase 6: FastAPI Route Extension
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.services.backtesting_service import (
    run_30day_dgca_backtest,
    get_available_backtest_routes,
)

router = APIRouter()


@router.get("/dgca/30-day", tags=["DGCA Backtesting"])
async def get_30day_backtest(
    origin: Optional[str] = Query(None, description="Optional Origin IATA code, e.g. DEL"),
    destination: Optional[str] = Query(None, description="Optional Destination IATA code, e.g. BOM"),
    db: Session = Depends(get_db),
):
    """
    30-day regulatory backtest evaluating platform fares against published
    DGCA Statutory Fare Cap Bounds (CAR Section 3 Series M Part I).
    """
    return run_30day_dgca_backtest(db=db, origin=origin, destination=destination)


@router.get("/dgca/regulatory-bands", tags=["DGCA Backtesting"])
async def get_regulatory_bands_benchmark(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Explicit alias for Regulatory Fare-Band Benchmark (CAR Section 3 Series M Part I).
    """
    return run_30day_dgca_backtest(db=db, origin=origin, destination=destination)


@router.get("/dgca/monthly-benchmark", tags=["DGCA Backtesting"])
async def get_dgca_monthly_benchmark(
    period: str = Query("2025-02", description="Calendar month period, e.g. 2025-02, 2025-03, 2025-04"),
    db: Session = Depends(get_db),
):
    """
    Genuine DGCA Monthly Average Fare Benchmark.
    Sourced from official Ministry of Civil Aviation / DGCA Tariff Monitoring Unit (TMU)
    sector reviews presented in parliamentary disclosures.
    """
    from backend.app.services.dgca_monthly_service import run_dgca_monthly_comparison
    return run_dgca_monthly_comparison(db=db, period_label=period)


@router.get("/dgca/routes", tags=["DGCA Backtesting"])
async def get_backtest_routes(db: Session = Depends(get_db)):
    """Return top routes available for backtesting analysis."""
    return get_available_backtest_routes(db=db)


@router.get("/dgca/summary", tags=["DGCA Backtesting"])
async def get_backtest_summary(db: Session = Depends(get_db)):
    """Return quick KPI validation summary for dashboard header."""
    res = run_30day_dgca_backtest(db=db)
    return res.get("summary", {})

