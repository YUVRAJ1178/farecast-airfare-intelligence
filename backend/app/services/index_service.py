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
    query = db.query(AirfareObservation).filter(
        AirfareObservation.origin == origin,
        AirfareObservation.destination == destination,
        AirfareObservation.is_demo_anomaly == False,  # Exclude seeded anomalies
    )

    if cabin_class and cabin_class.lower() != "all":
        query = query.filter(AirfareObservation.cabin_class == cabin_class)

    all_obs = query.all()
    if not all_obs:
        logger.warning(f"No observations found for route {origin}→{destination}")
        return None

    df = pd.DataFrame([{
        "fare": o.fare,
        "travel_date": o.travel_date,
        "cabin_class": o.cabin_class,
    } for o in all_obs])

    df["travel_date"] = pd.to_datetime(df["travel_date"])

    # Baseline fares
    baseline_mask = (
        (df["travel_date"].dt.date >= baseline_start) &
        (df["travel_date"].dt.date <= baseline_end)
    )
    baseline_df = df[baseline_mask]

    if len(baseline_df) < 5:
        logger.warning(
            f"Insufficient baseline data for {origin}→{destination}: "
            f"{len(baseline_df)} rows. Need at least 5."
        )
        # Use overall median as fallback baseline
        baseline_avg = float(df["fare"].median())
        baseline_label = "overall median (insufficient baseline period data)"
    else:
        baseline_avg = float(baseline_df["fare"].mean())
        baseline_label = f"{baseline_start} to {baseline_end}"

    # Period fares
    period_mask = (
        (df["travel_date"].dt.date >= period_start) &
        (df["travel_date"].dt.date <= period_end)
    )
    period_df = df[period_mask]

    if len(period_df) < 3:
        logger.warning(
            f"Insufficient period data for {origin}→{destination} "
            f"({period_start} to {period_end}): {len(period_df)} rows"
        )
        return None

    period_avg = float(period_df["fare"].mean())

    if baseline_avg <= 0:
        logger.error(f"Invalid baseline average fare: {baseline_avg}")
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
        "observation_count": len(period_df),
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
    Compute monthly index values for a route over all available data.
    Returns a list of monthly index dicts for charting.
    """
    query = db.query(AirfareObservation).filter(
        AirfareObservation.origin == origin,
        AirfareObservation.destination == destination,
        AirfareObservation.is_demo_anomaly == False,
    )
    if cabin_class and cabin_class.lower() != "all":
        query = query.filter(AirfareObservation.cabin_class == cabin_class)

    all_obs = query.all()
    if not all_obs:
        return []

    df = pd.DataFrame([{
        "fare": o.fare,
        "travel_date": pd.to_datetime(o.travel_date),
    } for o in all_obs])

    # Baseline
    baseline_mask = (
        (df["travel_date"].dt.date >= baseline_start) &
        (df["travel_date"].dt.date <= baseline_end)
    )
    baseline_df = df[baseline_mask]
    if len(baseline_df) < 5:
        baseline_avg = float(df["fare"].median())
        baseline_label = "overall median"
    else:
        baseline_avg = float(baseline_df["fare"].mean())
        baseline_label = f"{baseline_start} to {baseline_end}"

    if baseline_avg <= 0:
        return []

    # Monthly grouping
    df["year_month"] = df["travel_date"].dt.to_period("M")
    monthly = df.groupby("year_month")["fare"].agg(["mean", "count"])

    results = []
    for period, row in monthly.iterrows():
        if row["count"] < 3:
            continue  # Skip months with too few observations
        avg_fare = float(row["mean"])
        index_val = (avg_fare / baseline_avg) * 100.0
        results.append({
            "period": str(period),
            "avg_fare": round(avg_fare, 2),
            "index_value": round(index_val, 2),
            "baseline_fare": round(baseline_avg, 2),
            "observation_count": int(row["count"]),
            "origin": origin,
            "destination": destination,
            "baseline_period": baseline_label,
            "is_prototype": True,
        })

    return sorted(results, key=lambda x: x["period"])


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

    # Compute aggregate monthly series by averaging all route monthly series
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
    monthly_series = []
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
