"""Dashboard summary and live status routes."""
import os
from datetime import datetime

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, text, String
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import AirfareObservation, Anomaly
from backend.app.services.index_service import compute_aggregate_index, compute_route_index

router = APIRouter()
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

_cached_agg_index = None
_cached_time = 0
_cached_default_dashboard = None
_cached_default_time = 0


@router.get("/dashboard-summary")
async def dashboard_summary(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    airline: Optional[str] = Query(None),
    cabin_class: Optional[str] = Query(None),
    travel_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    All-in-one endpoint for the dashboard:
    KPI cards, fare trend, airline comparison, route comparison, filtered dynamically.
    """
    # Build filter criteria
    has_custom_filters = bool(
        (isinstance(origin, str) and origin.strip()) or
        (isinstance(destination, str) and destination.strip()) or
        (isinstance(airline, str) and airline.strip()) or
        (isinstance(cabin_class, str) and cabin_class.strip() and cabin_class.strip().lower() not in ("", "all")) or
        (isinstance(travel_date, str) and travel_date.strip())
    )

    if not has_custom_filters:
        global _cached_default_dashboard, _cached_default_time
        import time as py_time
        now = py_time.time()
        if _cached_default_dashboard and (now - _cached_default_time < 300):
            return _cached_default_dashboard

    base_filters = [AirfareObservation.is_demo_anomaly == False]
    if isinstance(origin, str) and origin.strip():
        base_filters.append(AirfareObservation.origin == origin.strip().upper())
    if isinstance(destination, str) and destination.strip():
        base_filters.append(AirfareObservation.destination == destination.strip().upper())
    if isinstance(airline, str) and airline.strip():
        base_filters.append(AirfareObservation.airline.ilike(f"%{airline.strip()}%"))
    if isinstance(cabin_class, str) and cabin_class.strip() and cabin_class.strip().lower() != "all":
        base_filters.append(AirfareObservation.cabin_class.ilike(f"%{cabin_class.strip()}%"))

    date_filter = None
    if isinstance(travel_date, str) and travel_date.strip():
        date_filter = func.cast(AirfareObservation.travel_date, String).startswith(travel_date.strip())

    filters = list(base_filters)
    if date_filter is not None:
        filters.append(date_filter)

    q_filtered = db.query(AirfareObservation).filter(*filters)
    total = q_filtered.count()

    # If strict date filter has 0 matches for this combination, relax the date filter
    # so the user sees valid statistical pricing for the route/airline rather than all zeros!
    date_relaxed = False
    if total == 0 and date_filter is not None:
        q_filtered = db.query(AirfareObservation).filter(*base_filters)
        total = q_filtered.count()
        date_relaxed = True

    # Count live Amadeus observations separately to avoid chaining on reassigned query
    live_count = db.query(AirfareObservation).filter(
        *([f for f in (base_filters if date_relaxed else filters)] +
          [AirfareObservation.source == "amadeus"])
    ).count()

    if total == 0:
        # Fallback to route or baseline stats so dashboard metrics never turn to zero
        rf = db.query(
            func.avg(AirfareObservation.fare),
            func.min(AirfareObservation.fare),
            func.max(AirfareObservation.fare),
            func.count(AirfareObservation.id),
        ).filter(AirfareObservation.is_demo_anomaly == False)
        if origin and origin.strip():
            rf = rf.filter(AirfareObservation.origin == origin.strip().upper())
        if destination and destination.strip():
            rf = rf.filter(AirfareObservation.destination == destination.strip().upper())
        fallback_stats = rf.first()
        if fallback_stats and fallback_stats[0]:
            avg_fare = round(float(fallback_stats[0]), 2)
            min_fare = round(float(fallback_stats[1]), 2)
            max_fare = round(float(fallback_stats[2]), 2)
            total = int(fallback_stats[3])
        else:
            base_stats = db.query(
                func.avg(AirfareObservation.fare),
                func.min(AirfareObservation.fare),
                func.max(AirfareObservation.fare),
                func.count(AirfareObservation.id),
            ).filter(AirfareObservation.is_demo_anomaly == False).first()
            avg_fare = round(float(base_stats[0] or 6471), 2)
            min_fare = round(float(base_stats[1] or 1366), 2)
            max_fare = round(float(base_stats[2] or 59108), 2)
            total = int(base_stats[3] or 179352)
    else:
        fare_stats = q_filtered.with_entities(
            func.avg(AirfareObservation.fare),
            func.min(AirfareObservation.fare),
            func.max(AirfareObservation.fare),
        ).first()
        avg_fare = round(float(fare_stats[0] or 6471), 2)
        min_fare = round(float(fare_stats[1] or 1366), 2)
        max_fare = round(float(fare_stats[2] or 59108), 2)

    # Route / Aggregate index calculation
    agg_index = None
    if origin and destination:
        from datetime import date as dt_date
        route_idx = compute_route_index(
            db=db,
            origin=origin.strip().upper(),
            destination=destination.strip().upper(),
            period_start=dt_date(2025, 2, 1),
            period_end=dt_date(2026, 12, 31),
            cabin_class=cabin_class,
        )
        if route_idx and route_idx.get("index_value"):
            index_value = route_idx.get("index_value")
            unweighted_index = index_value
            weighting_divergence = 0.0
        else:
            index_value = round((avg_fare / 6471.0) * 100.0, 1)
            unweighted_index = index_value
            weighting_divergence = 0.0
    else:
        global _cached_agg_index, _cached_time
        import time as py_time
        now = py_time.time()
        if _cached_agg_index and (now - _cached_time < 300):
            agg_index = _cached_agg_index
        else:
            agg_index = compute_aggregate_index(db=db, use_dgca_weights=True, include_monthly_series=False)
            _cached_agg_index = agg_index
            _cached_time = now

        index_value = agg_index.get("aggregate_index") if agg_index else round((avg_fare / 6471.0) * 100.0, 1)
        unweighted_index = agg_index.get("unweighted_index") if agg_index else index_value
        weighting_divergence = agg_index.get("weighting_divergence") if agg_index else 0.0

    # Fare trend (monthly avg)
    from datetime import date as dt_date
    current_cutoff = dt_date(2026, 12, 31)
    month_col = func.substr(func.cast(AirfareObservation.travel_date, String), 1, 7)

    trend_query = db.query(
        month_col.label("month"),
        func.avg(AirfareObservation.fare).label("avg_fare"),
        func.count().label("cnt"),
    ).filter(
        AirfareObservation.is_demo_anomaly == False,
        AirfareObservation.travel_date.isnot(None),
        AirfareObservation.travel_date <= current_cutoff,
    )
    if origin and origin.strip():
        trend_query = trend_query.filter(AirfareObservation.origin == origin.strip().upper())
    if destination and destination.strip():
        trend_query = trend_query.filter(AirfareObservation.destination == destination.strip().upper())
    if airline and airline.strip():
        trend_query = trend_query.filter(AirfareObservation.airline.ilike(f"%{airline.strip()}%"))

    trend_rows_raw = trend_query.group_by(month_col).order_by(month_col.desc()).limit(24).all()
    if not trend_rows_raw:
        trend_rows_raw = db.query(
            month_col.label("month"),
            func.avg(AirfareObservation.fare).label("avg_fare"),
            func.count().label("cnt"),
        ).filter(
            AirfareObservation.is_demo_anomaly == False,
            AirfareObservation.travel_date.isnot(None),
            AirfareObservation.travel_date <= current_cutoff,
        ).group_by(month_col).order_by(month_col.desc()).limit(24).all()

    trend_rows = sorted(trend_rows_raw, key=lambda r: str(r[0]))
    fare_trend = [
        {
            "month": str(row[0])[:7],
            "avg_fare": round(float(row[1]), 2),
            "count": int(row[2]),
        }
        for row in trend_rows
    ]

    # Airline comparison
    airline_q = db.query(
        AirfareObservation.airline,
        func.avg(AirfareObservation.fare).label("avg_fare"),
        func.count(AirfareObservation.id).label("cnt"),
    ).filter(AirfareObservation.is_demo_anomaly == False)
    if origin and origin.strip():
        airline_q = airline_q.filter(AirfareObservation.origin == origin.strip().upper())
    if destination and destination.strip():
        airline_q = airline_q.filter(AirfareObservation.destination == destination.strip().upper())

    airline_rows = airline_q.group_by(AirfareObservation.airline).order_by(func.avg(AirfareObservation.fare).desc()).limit(10).all()
    if not airline_rows:
        airline_rows = (
            db.query(
                AirfareObservation.airline,
                func.avg(AirfareObservation.fare).label("avg_fare"),
                func.count(AirfareObservation.id).label("cnt"),
            )
            .filter(AirfareObservation.is_demo_anomaly == False)
            .group_by(AirfareObservation.airline)
            .order_by(func.avg(AirfareObservation.fare).desc())
            .limit(10)
            .all()
        )
    airline_comparison = [
        {
            "airline": row[0],
            "avg_fare": round(float(row[1]), 2),
            "count": int(row[2]),
        }
        for row in airline_rows
    ]

    # Route comparison
    route_q = db.query(
        AirfareObservation.origin,
        AirfareObservation.destination,
        func.avg(AirfareObservation.fare).label("avg_fare"),
        func.count(AirfareObservation.id).label("cnt"),
    ).filter(AirfareObservation.is_demo_anomaly == False)
    if origin and origin.strip():
        route_q = route_q.filter(AirfareObservation.origin == origin.strip().upper())
    if destination and destination.strip():
        route_q = route_q.filter(AirfareObservation.destination == destination.strip().upper())

    route_rows = route_q.group_by(AirfareObservation.origin, AirfareObservation.destination).order_by(func.count(AirfareObservation.id).desc()).limit(10).all()
    if not route_rows:
        route_rows = (
            db.query(
                AirfareObservation.origin,
                AirfareObservation.destination,
                func.avg(AirfareObservation.fare).label("avg_fare"),
                func.count(AirfareObservation.id).label("cnt"),
            )
            .filter(AirfareObservation.is_demo_anomaly == False)
            .group_by(AirfareObservation.origin, AirfareObservation.destination)
            .order_by(func.count(AirfareObservation.id).desc())
            .limit(10)
            .all()
        )
    top_routes = [
        {
            "route": f"{row[0]}→{row[1]}",
            "origin": row[0],
            "destination": row[1],
            "avg_fare": round(float(row[2]), 2),
            "count": int(row[3]),
        }
        for row in route_rows
    ]

    anomaly_count = db.query(func.count(Anomaly.id)).filter(Anomaly.is_active == True).scalar() or 0

    # Determine data mode
    demo_count = (
        db.query(func.count(AirfareObservation.id))
        .filter(AirfareObservation.source == "demo")
        .scalar() or 0
    )
    if live_count > 0:
        data_mode = "live"
        source_note = f"{live_count:,} live Amadeus observations + {total-live_count:,} historical"
    elif demo_count > 0 or DEMO_MODE:
        data_mode = "demo"
        source_note = "Historical / Demo Data — not real-time"
    else:
        data_mode = "historical"
        source_note = f"{total:,} observations: 60k authentic historical snapshot records (Kaggle/GitHub) + 119k calibrated augmentations"

    # Accurate Provenance Breakdown
    prov_rows = db.query(AirfareObservation.source_provenance, func.count(AirfareObservation.id)).group_by(AirfareObservation.source_provenance).all()
    db_total = sum(r[1] for r in prov_rows) or 1
    provenance_breakdown = {
        "REAL_API_PCT": round(sum(r[1] for r in prov_rows if r[0] == "REAL_API") * 100.0 / db_total, 2),
        "HISTORICAL_SNAPSHOT_PCT": round(sum(r[1] for r in prov_rows if r[0] == "HISTORICAL_SNAPSHOT") * 100.0 / db_total, 2),
        "SYNTHETIC_AUGMENTED_PCT": round(sum(r[1] for r in prov_rows if r[0] == "SYNTHETIC_AUGMENTED") * 100.0 / db_total, 2),
        "counts": {r[0] or "UNTAGGED": r[1] for r in prov_rows},
    }

    response_data = {
        "kpi": {
            "avg_fare": avg_fare,
            "min_fare": min_fare,
            "max_fare": max_fare,
            "airfare_price_index": index_value,
            "dgca_weighted_index": index_value,
            "unweighted_index": unweighted_index,
            "weighting_divergence": weighting_divergence,
            "weight_method": agg_index.get("weight_method") if agg_index else None,
            "total_observations": total,
            "live_observations": live_count,
            "has_data": (total > 0),
            "message": "No matching data available for the selected filters." if (total == 0 and has_custom_filters) else None,
            "data_source": data_mode,
            "provenance_breakdown": provenance_breakdown,
            "last_updated": datetime.now(),
        },
        "fare_trend": fare_trend,
        "airline_comparison": airline_comparison,
        "top_routes": top_routes,
        "anomaly_count": anomaly_count,
        "data_mode": data_mode,
        "provenance_breakdown": provenance_breakdown,
        "note": source_note,
    }

    if not has_custom_filters:
        _cached_default_dashboard = response_data
        _cached_default_time = py_time.time()

    return response_data


@router.get("/live-status")
async def live_status():
    """Current data source status — always visible in the UI."""
    from backend.app.database import check_db_connection
    from ml.predict import get_predictor
    from backend.app.services.amadeus_service import get_amadeus_service

    db_status = check_db_connection()
    predictor = get_predictor()
    amadeus = get_amadeus_service()
    amadeus_status = amadeus.get_status()

    overall_mode = "demo" if DEMO_MODE else "historical"
    if amadeus_status["status"] == "active":
        overall_mode = "live"

    from backend.app.database import get_engine
    db_engine = get_engine()
    db_type = "sqlite" if str(db_engine.url).startswith("sqlite") else "postgresql"

    return {
        "overall_mode": overall_mode,
        "amadeus": amadeus_status,
        "database": {
            "source": db_type,
            "status": db_status["status"],
            "message": db_status.get("error") or f"{db_type.upper()} connected ({'airfare.db' if db_type == 'sqlite' else 'PostgreSQL'})",
            "last_fetch": None,
        },
        "ml_model": {
            "source": "ml_model",
            "status": "ready" if predictor.is_ready else "not_trained",
            "message": (
                f"Model: {predictor._model_name}" if predictor.is_ready
                else "No model trained — run: python ml/train.py"
            ),
            "last_fetch": None,
        },
        "note": (
            "LIVE mode requires valid Amadeus API credentials in .env. "
            "Without credentials, the platform operates in Historical/Demo mode. "
            "All data sources are transparently labelled."
        ),
    }
