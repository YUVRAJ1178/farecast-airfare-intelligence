"""
Airfare Intelligence Platform — Data Seeding Service
Seeds processed CSV data into PostgreSQL on startup.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime, date

import pandas as pd

from sqlalchemy.orm import Session
from backend.app.models import AirfareObservation, Route
from backend.app.database import get_engine

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
PROCESSED_CSV = PROJECT_ROOT / "data" / "processed" / "airfare_clean.csv"


def seed_observations_from_csv(db: Session, csv_path: Path = PROCESSED_CSV, force: bool = False, max_rows: int = 50000) -> int:
    """
    Load processed airfare CSV and insert records into PostgreSQL/SQLite.
    Replaces legacy demo data when real data is available.

    Returns number of rows inserted.
    """
    if not csv_path.exists():
        logger.warning(
            f"Processed data not found at {csv_path}. "
            "Run: python data/ingest.py"
        )
        return 0

    # Check existing data
    existing = db.query(AirfareObservation).count()
    has_only_demo = False
    if existing > 0:
        demo_count = db.query(AirfareObservation).filter(AirfareObservation.source == "demo").count()
        has_only_demo = (demo_count == existing)

    if existing > 0 and not force and not has_only_demo:
        logger.info(f"Database already has {existing:,} observations — skipping seed.")
        return 0

    if has_only_demo or force:
        logger.info(f"Clearing {existing:,} legacy observations to load real historical dataset...")
        db.query(AirfareObservation).delete()
        db.commit()

    logger.info(f"Seeding database from real dataset: {csv_path}...")
    df = pd.read_csv(csv_path, low_memory=False)
    logger.info(f"Loaded {len(df):,} rows from CSV")

    # If max_rows is set and df is larger, sample evenly across all dates for quick database performance
    if max_rows and len(df) > max_rows:
        df = df.sample(n=max_rows, random_state=42).sort_values("travel_date").copy()
        logger.info(f"Selected {len(df):,} evenly distributed records for database store")

    # Prepare DataFrame columns
    now = datetime.utcnow()
    df["source"] = df["source"].fillna("kaggle_historical").astype(str)
    df["airline"] = df["airline"].fillna("Unknown").astype(str)
    df["origin"] = df["origin"].fillna("DEL").astype(str).str[:10]
    df["destination"] = df["destination"].fillna("BOM").astype(str).str[:10]
    df["cabin_class"] = df["cabin_class"].fillna("Economy").astype(str)
    df["currency"] = "INR"
    df["stops"] = pd.to_numeric(df["stops"], errors="coerce").fillna(0).astype(int)
    df["fare"] = pd.to_numeric(df["fare"], errors="coerce").fillna(5000.0).astype(float)
    df["duration_minutes"] = pd.to_numeric(df["duration_minutes"], errors="coerce").fillna(120).astype(int)
    df["days_left"] = pd.to_numeric(df["days_left"], errors="coerce").fillna(15).astype(int)
    df["is_demo_anomaly"] = False
    df["collected_at"] = now
    df["created_at"] = now

    parsed_dates = pd.to_datetime(df["travel_date"], errors="coerce")
    df["travel_date"] = parsed_dates.dt.date.fillna(date(2023, 6, 1))
    df["booking_date"] = pd.to_datetime(df["booking_date"], errors="coerce").dt.date.fillna(df["travel_date"])
    df["departure_time"] = df["departure_time"].fillna("10:00").astype(str)
    df["arrival_time"] = df["arrival_time"].fillna("12:00").astype(str)

    # Bulk insert
    cols = [
        "source", "airline", "origin", "destination", "travel_date",
        "booking_date", "departure_time", "arrival_time", "stops",
        "duration_minutes", "cabin_class", "fare", "currency",
        "days_left", "is_demo_anomaly", "collected_at", "created_at"
    ]
    records = df[cols].to_dict(orient="records")

    batch_size = 5000
    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        db.bulk_insert_mappings(AirfareObservation, batch)
        db.commit()
        inserted += len(batch)
        logger.info(f"  Inserted {inserted:,}/{len(records):,} rows...")

    # Populate routes lookup table
    _populate_routes(db)

    # Detect anomalies on real data
    try:
        from backend.app.services.anomaly_service import detect_isolation_forest_anomalies, save_anomalies
        anomalies = detect_isolation_forest_anomalies(db, contamination=0.01)
        if anomalies:
            save_anomalies(db, anomalies[:50])
            logger.info(f"Saved {min(len(anomalies), 50)} real-data anomaly records to database")
    except Exception as e:
        logger.warning(f"Anomaly detection post-seeding warning: {e}")

    logger.info(f"Seeding complete: {inserted:,} real historical rows loaded")
    return inserted


def _populate_routes(db: Session):
    """Populate routes lookup table from observations."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    from data.schema import IATA_CITY_MAP

    from sqlalchemy import text
    routes_data = db.execute(
        text(
            "SELECT origin, destination, COUNT(*) as cnt "
            "FROM airfare_observations "
            "GROUP BY origin, destination"
        )
    ).fetchall()

    for row in routes_data:
        existing = db.query(Route).filter(
            Route.origin == row[0],
            Route.destination == row[1],
        ).first()
        if not existing:
            route = Route(
                origin=row[0],
                destination=row[1],
                origin_name=IATA_CITY_MAP.get(row[0]),
                destination_name=IATA_CITY_MAP.get(row[1]),
                observation_count=int(row[2]),
            )
            db.add(route)

    db.commit()
    logger.info(f"Routes table populated: {len(routes_data)} unique routes")
