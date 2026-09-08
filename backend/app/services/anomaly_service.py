"""
Airfare Intelligence Platform — Anomaly Detection Service
Phase 6: FastAPI / Services

Detects unusual fare movements using:
  1. IQR-based statistical bounds (simple, robust, explainable)
  2. Isolation Forest (ML-based, for confirmation)

IMPORTANT:
  - No anomalies are fabricated in live mode
  - Demo anomalies in demo mode are always tagged is_demo=True
  - Detection is only as good as the underlying data
"""

import logging
from datetime import date, datetime
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from backend.app.models import Anomaly, AirfareObservation

logger = logging.getLogger(__name__)

# Severity thresholds (absolute percentage deviation from expected midpoint)
SEVERITY_THRESHOLDS = {
    "LOW": 20.0,       # 20–35% deviation
    "MEDIUM": 35.0,    # 35–60% deviation
    "HIGH": 60.0,      # 60–100% deviation
    "CRITICAL": 100.0, # >100% deviation
}


def _get_severity(pct_deviation: float) -> str:
    abs_dev = abs(pct_deviation)
    if abs_dev >= SEVERITY_THRESHOLDS["CRITICAL"]:
        return "CRITICAL"
    elif abs_dev >= SEVERITY_THRESHOLDS["HIGH"]:
        return "HIGH"
    elif abs_dev >= SEVERITY_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    else:
        return "LOW"


def detect_iqr_anomalies(
    db: Session,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    cabin_class: Optional[str] = None,
    lookback_days: int = 90,
    iqr_multiplier: float = 1.5,
    min_observations: int = 10,
) -> list[dict]:
    """
    Detect anomalies using Interquartile Range method.

    A fare is anomalous if it exceeds:
        Q1 - iqr_multiplier × IQR  (unusually low)
        Q3 + iqr_multiplier × IQR  (unusually high)

    Returns list of anomaly dicts (not yet saved to DB).
    """
    query = db.query(AirfareObservation).filter(
        AirfareObservation.is_demo_anomaly == False  # Don't detect our own seeds
    )

    if origin:
        query = query.filter(AirfareObservation.origin == origin)
    if destination:
        query = query.filter(AirfareObservation.destination == destination)
    if cabin_class and cabin_class.lower() != "all":
        query = query.filter(AirfareObservation.cabin_class == cabin_class)

    obs = query.all()
    if not obs:
        return []

    df = pd.DataFrame([{
        "id": o.id,
        "origin": o.origin,
        "destination": o.destination,
        "airline": o.airline,
        "fare": o.fare,
        "cabin_class": o.cabin_class,
        "travel_date": o.travel_date,
        "source": o.source,
    } for o in obs])

    anomalies = []

    # Group by route (and cabin class if specified)
    group_cols = ["origin", "destination"]
    if not cabin_class:
        group_cols.append("cabin_class")

    for group_keys, group_df in df.groupby(group_cols):
        if len(group_df) < min_observations:
            continue

        fares = group_df["fare"].values
        q1 = np.percentile(fares, 25)
        q3 = np.percentile(fares, 75)
        iqr = q3 - q1

        lower_bound = q1 - iqr_multiplier * iqr
        upper_bound = q3 + iqr_multiplier * iqr
        baseline = (q1 + q3) / 2.0

        # Find outliers
        outlier_mask = (fares < lower_bound) | (fares > upper_bound)
        outlier_rows = group_df[outlier_mask]

        for _, row in outlier_rows.iterrows():
            fare = row["fare"]
            pct_dev = ((fare - baseline) / baseline) * 100.0

            # Only report anomalies with at least LOW severity
            if abs(pct_dev) < SEVERITY_THRESHOLDS["LOW"]:
                continue

            if isinstance(group_keys, tuple):
                grp_origin = group_keys[0]
                grp_dest = group_keys[1]
            else:
                grp_origin = group_df["origin"].iloc[0]
                grp_dest = group_df["destination"].iloc[0]

            direction = "above route IQR upper bound" if pct_dev > 0 else "below route IQR lower bound"
            explanation = f"Observed fare ₹{fare:,.0f} is {pct_dev:+.1f}% {direction} (Expected corridor range: ₹{lower_bound:,.0f} – ₹{upper_bound:,.0f})"

            anomalies.append({
                "origin": grp_origin,
                "destination": grp_dest,
                "airline": row.get("airline"),
                "observed_fare": float(fare),
                "expected_low": round(float(lower_bound), 2),
                "expected_high": round(float(upper_bound), 2),
                "expected_baseline": round(float(baseline), 2),
                "pct_deviation": round(float(pct_dev), 2),
                "severity": _get_severity(pct_dev),
                "detection_method": f"IQR (k={iqr_multiplier})",
                "explanation": explanation,
                "is_demo": row.get("source", "").lower() in ("demo", "synthetic_demo"),
                "observation_date": row.get("travel_date"),
                "detected_at": datetime.utcnow(),
            })

    logger.info(f"IQR anomaly detection found {len(anomalies)} anomalies")
    return anomalies


def detect_isolation_forest_anomalies(
    db: Session,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    contamination: float = 0.05,
    min_observations: int = 50,
) -> list[dict]:
    """
    Detect anomalies using Isolation Forest (sklearn).

    Uses: fare, days_left, stops as features.
    contamination: expected fraction of anomalies (default 5%).

    Returns list of anomaly dicts.
    """
    query = db.query(AirfareObservation).filter(
        AirfareObservation.is_demo_anomaly == False
    )
    if origin:
        query = query.filter(AirfareObservation.origin == origin)
    if destination:
        query = query.filter(AirfareObservation.destination == destination)

    obs = query.all()
    if len(obs) < min_observations:
        logger.info(
            f"Insufficient data for Isolation Forest ({len(obs)} rows, need {min_observations})"
        )
        return []

    df = pd.DataFrame([{
        "id": o.id,
        "origin": o.origin,
        "destination": o.destination,
        "airline": o.airline,
        "fare": o.fare,
        "stops": o.stops or 0,
        "days_left": o.days_left or 30,
        "travel_date": o.travel_date,
        "source": o.source,
    } for o in obs])

    feature_cols = ["fare", "stops", "days_left"]
    X = df[feature_cols].fillna(df[feature_cols].median())

    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
    )
    predictions = iso_forest.fit_predict(X)
    scores = iso_forest.decision_function(X)

    anomaly_mask = predictions == -1
    anomaly_df = df[anomaly_mask].copy()
    anomaly_df["anomaly_score"] = scores[anomaly_mask]

    anomalies = []
    for _, row in anomaly_df.iterrows():
        # Compute route baseline for context
        route_df = df[
            (df["origin"] == row["origin"]) &
            (df["destination"] == row["destination"])
        ]
        if len(route_df) < 5:
            continue

        q1 = np.percentile(route_df["fare"].values, 25)
        q3 = np.percentile(route_df["fare"].values, 75)
        baseline = (q1 + q3) / 2.0

        if baseline <= 0:
            continue

        pct_dev = ((row["fare"] - baseline) / baseline) * 100.0
        explanation = f"Multivariate outlier: fare ₹{row['fare']:,.0f} ({pct_dev:+.1f}% vs route baseline ₹{baseline:,.0f}) with {row.get('days_left', 0)}d advance window"

        anomalies.append({
            "origin": row["origin"],
            "destination": row["destination"],
            "airline": row.get("airline"),
            "observed_fare": float(row["fare"]),
            "expected_low": round(float(q1), 2),
            "expected_high": round(float(q3), 2),
            "expected_baseline": round(float(baseline), 2),
            "pct_deviation": round(float(pct_dev), 2),
            "severity": _get_severity(pct_dev),
            "detection_method": f"Isolation Forest (contamination={contamination})",
            "explanation": explanation,
            "is_demo": str(row.get("source", "")).lower() in ("demo", "synthetic_demo"),
            "observation_date": row.get("travel_date"),
            "detected_at": datetime.utcnow(),
        })

    logger.info(f"Isolation Forest detected {len(anomalies)} anomalies")
    return anomalies


def save_anomalies(db: Session, anomaly_dicts: list[dict]) -> int:
    """Persist anomaly records to DB. Returns count saved."""
    saved = 0
    for a in anomaly_dicts:
        record = Anomaly(**{k: v for k, v in a.items() if hasattr(Anomaly, k)})
        db.add(record)
        saved += 1
    db.commit()
    logger.info(f"Saved {saved} anomaly records to DB")
    return saved


def run_anomaly_detection(
    db: Session,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    save_to_db: bool = True,
) -> list[dict]:
    """
    Run both IQR and Isolation Forest detection.
    Merge and deduplicate results.
    """
    iqr_anomalies = detect_iqr_anomalies(db, origin=origin, destination=destination)
    iso_anomalies = detect_isolation_forest_anomalies(db, origin=origin, destination=destination)

    # Combine — simple approach: union by (origin, destination, fare)
    seen = set()
    combined = []
    for a in iqr_anomalies + iso_anomalies:
        key = (a["origin"], a["destination"], a["observed_fare"])
        if key not in seen:
            seen.add(key)
            combined.append(a)

    logger.info(f"Total unique anomalies detected: {len(combined)}")

    if save_to_db and combined:
        save_anomalies(db, combined)

    return combined
