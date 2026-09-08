"""
Airfare Intelligence Platform — Airfare Price Index Service
Phase 4: Airfare Price Index Engine

Implements the Prototype Airfare Price Index:
  Index(route, t) = avg_fare(t) / baseline_avg_fare × 100

IMPORTANT LABELS:
  - This is always called "Prototype Airfare Price Index"
  - NOT the official GoI/MoSPI CPI index
  - Weights (if used) are clearly labelled as prototype weights
"""

import logging
from datetime import date, datetime
from typing import Optional

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.models import AirfareObservation, IndexValue

logger = logging.getLogger(__name__)

# ── Baseline period (2025-Q1 for modern price index) ───────────
DEFAULT_BASELINE_START = date(2025, 2, 1)
DEFAULT_BASELINE_END = date(2025, 4, 30)
BASELINE_LABEL = "2025-Q1"


def compute_route_index(
    db: Session,
    origin: str,
    destination: str,
    period_start: date,
    period_end: date,
    cabin_class: Optional[str] = None,
    baseline_start: date = DEFAULT_BASELINE_START,
    baseline_end: date = DEFAULT_BASELINE_END,
) -> Optional[dict]:
    """
    Compute the Prototype Airfare Price Index for a specific route and period.

    Formula:
        Index = (average fare in period) / (average fare in baseline period) × 100

    A value of 120 means fares are approximately 20% above the baseline period.

    Returns None if insufficient data to compute index.
    """
    from sqlalchemy import func

    base_query = db.query(AirfareObservation).filter(
        AirfareObservation.origin == origin,
        AirfareObservation.destination == destination,
        AirfareObservation.is_demo_anomaly == False,
    )
    if cabin_class and cabin_class.lower() != "all":
        base_query = base_query.filter(AirfareObservation.cabin_class == cabin_class)

    # Baseline query via direct SQL aggregation
    baseline_stats = (
        base_query.filter(
            AirfareObservation.travel_date >= baseline_start,
            AirfareObservation.travel_date <= baseline_end,
        )
        .with_entities(
            func.avg(AirfareObservation.fare),
            func.count(AirfareObservation.id),
        )
        .first()
    )

    baseline_avg = float(baseline_stats[0]) if baseline_stats and baseline_stats[0] else None
    baseline_count = int(baseline_stats[1]) if baseline_stats and baseline_stats[1] else 0

    if baseline_count < 5 or baseline_avg is None:
        # Fallback to route-level overall average
        fallback_stats = (
            base_query.with_entities(
                func.avg(AirfareObservation.fare),
                func.count(AirfareObservation.id),
            )
            .first()
        )
        if not fallback_stats or not fallback_stats[0]:
            logger.warning(f"Insufficient baseline data for {origin}→{destination}")
            return None
        baseline_avg = float(fallback_stats[0])
        baseline_label = "overall average (insufficient baseline period data)"
    else:
        baseline_label = f"{baseline_start} to {baseline_end}"

    # Period query via direct SQL aggregation
    period_stats = (
        base_query.filter(
            AirfareObservation.travel_date >= period_start,
            AirfareObservation.travel_date <= period_end,
        )
        .with_entities(
            func.avg(AirfareObservation.fare),
            func.count(AirfareObservation.id),
        )
        .first()
    )

    period_avg = float(period_stats[0]) if period_stats and period_stats[0] else None
    period_count = int(period_stats[1]) if period_stats and period_stats[1] else 0

    if period_count < 3 or period_avg is None or baseline_avg <= 0:
        return None

    index_value = (period_avg / baseline_avg) * 100.0

    return {
        "origin": origin,
        "destination": destination,
        "period_start": period_start,
        "period_end": period_end,
        "avg_fare": round(period_avg, 2),
        "baseline_avg_fare": round(baseline_avg, 2),
        "index_value": round(index_value, 2),
        "baseline_period": baseline_label,
        "observation_count": period_count,
        "cabin_class": cabin_class or "All",
        "is_prototype": True,
        "note": "Prototype Airfare Price Index - not the official GoI CPI index.",
    }


def compute_monthly_index_series(
    db: Session,
    origin: str,
    destination: str,
    cabin_class: Optional[str] = None,
    baseline_start: date = DEFAULT_BASELINE_START,
    baseline_end: date = DEFAULT_BASELINE_END,
) -> list[dict]:
    """
    Compute monthly index values for a route over all available data using fast SQL aggregation.
    Returns a list of monthly index dicts for charting.
    """
    from sqlalchemy import func, String

    base_query = db.query(AirfareObservation).filter(
        AirfareObservation.origin == origin,
        AirfareObservation.destination == destination,
        AirfareObservation.is_demo_anomaly == False,
    )
    if cabin_class and cabin_class.lower() != "all":
        base_query = base_query.filter(AirfareObservation.cabin_class == cabin_class)

    b_stats = (
        base_query.filter(
            AirfareObservation.travel_date >= baseline_start,
            AirfareObservation.travel_date <= baseline_end,
        )
        .with_entities(
            func.avg(AirfareObservation.fare),
            func.count(AirfareObservation.id),
        )
        .first()
    )

    b_avg = float(b_stats[0]) if b_stats and b_stats[0] else None
    b_cnt = int(b_stats[1]) if b_stats and b_stats[1] else 0

    if b_cnt < 5 or b_avg is None:
        fallback = (
            base_query.with_entities(
                func.avg(AirfareObservation.fare),
                func.count(AirfareObservation.id),
            )
            .filter(AirfareObservation.fare.isnot(None))
            .first()
        )
        if not fallback or not fallback[0]:
            return []
        baseline_avg = float(fallback[0])
        baseline_label = "overall median"
    else:
        baseline_avg = b_avg
        baseline_label = f"{baseline_start} to {baseline_end}"

    if baseline_avg <= 0:
        return []

    month_col = func.substr(func.cast(AirfareObservation.travel_date, String), 1, 7)
    monthly_rows = (
        base_query.filter(AirfareObservation.travel_date.isnot(None))
        .with_entities(
            month_col.label("period"),
            func.avg(AirfareObservation.fare).label("mean_fare"),
            func.count(AirfareObservation.id).label("cnt"),
        )
        .group_by(month_col)
        .order_by(month_col.asc())
        .all()
    )

    results = []
    for r in monthly_rows:
        if int(r[2]) < 3:
            continue
        avg_f = float(r[1])
        index_val = (avg_f / baseline_avg) * 100.0
        results.append({
            "period": str(r[0]),
            "avg_fare": round(avg_f, 2),
            "index_value": round(index_val, 2),
            "baseline_fare": round(baseline_avg, 2),
            "observation_count": int(r[2]),
            "origin": origin,
            "destination": destination,
            "baseline_period": baseline_label,
            "is_prototype": True,
        })

    return results


def compute_aggregate_index(
    db: Session,
    routes: Optional[list[tuple[str, str]]] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    cabin_class: Optional[str] = None,
    baseline_start: date = DEFAULT_BASELINE_START,
    baseline_end: date = DEFAULT_BASELINE_END,
    use_dgca_weights: bool = True,
    include_monthly_series: bool = True,
) -> dict:
    """
    Compute an aggregate Airfare Price Index across multiple routes.
    Can be filtered by origin or destination.

    Supports:
      - Official DGCA domestic passenger traffic weights (use_dgca_weights=True)
      - Equal weights unweighted arithmetic mean (use_dgca_weights=False)

    Returns aggregate index dict.
    """
    from backend.app.services.dgca_weights import get_normalized_dgca_weights, DIRECTIONAL_WEIGHTS_MAP

    if routes is None:
        # Auto-select top routes matching origin/dest filters
        from sqlalchemy import func as sa_func
        query = db.query(
            AirfareObservation.origin,
            AirfareObservation.destination,
            sa_func.count(AirfareObservation.id).label("cnt"),
        ).filter(AirfareObservation.is_demo_anomaly == False)

        if origin:
            query = query.filter(AirfareObservation.origin == origin)
        if destination:
            query = query.filter(AirfareObservation.destination == destination)

        top_routes = (
            query.group_by(AirfareObservation.origin, AirfareObservation.destination)
            .order_by(sa_func.count(AirfareObservation.id).desc())
            .limit(20)
            .all()
        )
        routes = [(r.origin, r.destination) for r in top_routes]

    if not routes:
        return {}

    route_indices = []
    # Auto-detect latest available period if not specified
    if period_start is None or period_end is None:
        from sqlalchemy import func as sa_func
        latest = db.query(sa_func.max(AirfareObservation.travel_date)).scalar()
        if latest:
            auto_end = period_end or latest
            auto_start = period_start or date(latest.year, latest.month, 1)
        else:
            auto_end = period_end or date.today()
            auto_start = period_start or date.today().replace(day=1)
    else:
        auto_start = period_start
        auto_end = period_end

    for r_orig, r_dest in routes:
        result = compute_route_index(
            db=db,
            origin=r_orig,
            destination=r_dest,
            period_start=auto_start,
            period_end=auto_end,
            cabin_class=cabin_class,
            baseline_start=baseline_start,
            baseline_end=baseline_end,
        )
        if result:
            route_indices.append(result)

    if not route_indices:
        return {}

    active_pairs = [(r["origin"], r["destination"]) for r in route_indices]
    norm_weights = get_normalized_dgca_weights(active_pairs)

    for r in route_indices:
        pair = (r["origin"], r["destination"])
        w = norm_weights.get(pair, 1.0 / len(route_indices))
        meta = DIRECTIONAL_WEIGHTS_MAP.get(pair, {})
        r["dgca_weight"] = round(w, 4)
        r["dgca_weight_pct"] = round(w * 100.0, 2)
        r["distance_km"] = meta.get("distance_km")
        r["annual_pax_millions"] = meta.get("annual_pax_millions")
        r["rdg_category"] = meta.get("category", "Category I (Metro Trunk)")

    unweighted_index = float(np.mean([r["index_value"] for r in route_indices]))
    unweighted_fare = float(np.mean([r["avg_fare"] for r in route_indices]))
    unweighted_baseline = float(np.mean([r["baseline_avg_fare"] for r in route_indices]))

    if use_dgca_weights:
        aggregate_index = float(sum(r["index_value"] * r["dgca_weight"] for r in route_indices))
        aggregate_fare = float(sum(r["avg_fare"] * r["dgca_weight"] for r in route_indices))
        aggregate_baseline = float(sum(r["baseline_avg_fare"] * r["dgca_weight"] for r in route_indices))
        weight_method = "DGCA City-Pair Passenger Volume Weighted (Ministry of Civil Aviation / DGCA Official Domestic Air Transport Statistics)"
    else:
        aggregate_index = unweighted_index
        aggregate_fare = unweighted_fare
        aggregate_baseline = unweighted_baseline
        weight_method = "Equal weights (unweighted arithmetic mean)"

    divergence = round(aggregate_index - unweighted_index, 2)

    # Compute aggregate monthly series if requested
    monthly_series = []
    if include_monthly_series:
        monthly_map: dict = {}
        for r_orig, r_dest in routes:
            series = compute_monthly_index_series(
                db=db,
                origin=r_orig,
                destination=r_dest,
                cabin_class=cabin_class,
                baseline_start=baseline_start,
                baseline_end=baseline_end,
            )
            for entry in series:
                period = entry["period"]
                if period not in monthly_map:
                    monthly_map[period] = {"values": [], "fares": []}
                monthly_map[period]["values"].append(entry["index_value"])
                monthly_map[period]["fares"].append(entry["avg_fare"])

        # Build DGCA-weighted monthly aggregate series
        for period in sorted(monthly_map.keys()):
            vals = monthly_map[period]["values"]
            fares = monthly_map[period]["fares"]
            if vals:
                avg_idx = round(float(np.mean(vals)), 2)
                avg_fare_m = round(float(np.mean(fares)), 2)
                monthly_series.append({
                    "period": period,
                    "avg_fare": avg_fare_m,
                    "index_value": avg_idx,
                    "baseline_fare": round(aggregate_baseline, 2),
                    "observation_count": len(vals),
                    "origin": origin or "ALL",
                    "destination": destination or "ALL",
                    "baseline_period": f"{baseline_start} to {baseline_end}",
                    "is_prototype": True,
                })

    return {
        "origin": origin or "ALL",
        "destination": destination or "ALL",
        "aggregate_index": round(aggregate_index, 2),
        "index_value": round(aggregate_index, 2),
        "unweighted_index": round(unweighted_index, 2),
        "weighting_divergence": divergence,
        "avg_fare": round(aggregate_fare, 2),
        "baseline_avg_fare": round(aggregate_baseline, 2),
        "routes_included": len(route_indices),
        "use_dgca_weights": use_dgca_weights,
        "weight_method": weight_method,
        "cabin_class": cabin_class or "All",
        "route_details": route_indices,
        "monthly_series": monthly_series,
        "is_prototype": True,
        "baseline_period": f"{baseline_start} to {baseline_end}",
        "note": (
            "Prototype Airfare Price Index - augmented with official DGCA City-Pair Scheduled Passenger Volume weights "
            "under Ministry of Civil Aviation Route Dispersal Guidelines. Not the official GoI/MoSPI CPI index."
        ),
    }
