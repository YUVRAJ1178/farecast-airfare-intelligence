"""
Airfare Intelligence Platform — Seed Regional & Non-Metro Routes
Populates realistic historical observations for regional hubs (AMD, GOI, JAI, COK, PNQ, GAU, LKO, PAT, SXR, ATQ, IXC)
matching the exact 2025-02 to 2026-09 timeline and baseline structure.
"""

import logging
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.database import get_session_factory
from backend.app.models import AirfareObservation, Route
from data.schema import IATA_CITY_MAP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_regional")

# Regional & secondary route pairs with base fares (Economy INR) and durations (min)
REGIONAL_SPECS = [
    # Ahmedabad
    ("AMD", "DEL", 3600, 85),
    ("DEL", "AMD", 3600, 85),
    ("AMD", "BOM", 3200, 75),
    ("BOM", "AMD", 3200, 75),
    # Goa
    ("GOI", "BOM", 3500, 75),
    ("BOM", "GOI", 3500, 75),
    ("GOI", "DEL", 5800, 145),
    ("DEL", "GOI", 5800, 145),
    ("GOI", "BLR", 3200, 75),
    ("BLR", "GOI", 3200, 75),
    # Jaipur
    ("JAI", "BOM", 4600, 110),
    ("BOM", "JAI", 4600, 110),
    ("JAI", "DEL", 2800, 60),
    ("DEL", "JAI", 2800, 60),
    # Kochi
    ("COK", "DEL", 6500, 190),
    ("DEL", "COK", 6500, 190),
    ("COK", "BOM", 4500, 115),
    ("BOM", "COK", 4500, 115),
    ("COK", "BLR", 2800, 65),
    ("BLR", "COK", 2800, 65),
    # Pune
    ("PNQ", "DEL", 4800, 130),
    ("DEL", "PNQ", 4800, 130),
    ("PNQ", "BLR", 3800, 95),
    ("BLR", "PNQ", 3800, 95),
    # Guwahati
    ("GAU", "DEL", 5600, 155),
    ("DEL", "GAU", 5600, 155),
    ("GAU", "CCU", 3200, 75),
    ("CCU", "GAU", 3200, 75),
    # Lucknow
    ("LKO", "DEL", 2900, 70),
    ("DEL", "LKO", 2900, 70),
    ("LKO", "BOM", 4800, 130),
    ("BOM", "LKO", 4800, 130),
    # Patna
    ("PAT", "DEL", 4200, 100),
    ("DEL", "PAT", 4200, 100),
    # Srinagar
    ("SXR", "DEL", 5200, 95),
    ("DEL", "SXR", 5200, 95),
    # Amritsar
    ("ATQ", "DEL", 3100, 65),
    ("DEL", "ATQ", 3100, 65),
    # Chandigarh
    ("IXC", "DEL", 2800, 60),
    ("DEL", "IXC", 2800, 60),
    ("IXC", "BOM", 4900, 135),
    ("BOM", "IXC", 4900, 135),
]

AIRLINES = ["IndiGo", "Air India", "SpiceJet", "Vistara", "Akasa Air"]
AIRLINE_FACTORS = {
    "IndiGo": 0.94,
    "SpiceJet": 0.89,
    "Akasa Air": 0.91,
    "Air India": 1.05,
    "Vistara": 1.15,
}

DEPARTURE_SLOTS = ["06:15", "08:30", "10:45", "13:20", "15:40", "17:50", "19:30", "21:10"]

# Ensure IATA_CITY_MAP has all names
ADDITIONAL_CITIES = {
    "AMD": "Ahmedabad",
    "GOI": "Goa",
    "JAI": "Jaipur",
    "COK": "Kochi",
    "PNQ": "Pune",
    "GAU": "Guwahati",
    "LKO": "Lucknow",
    "PAT": "Patna",
    "SXR": "Srinagar",
    "ATQ": "Amritsar",
    "IXC": "Chandigarh",
}

def seed_regional_routes():
    rng = np.random.default_rng(2026)
    SessionLocal = get_session_factory()
    db: Session = SessionLocal()

    start_date = date(2025, 2, 1)
    end_date = date(2026, 9, 7)
    total_days = (end_date - start_date).days

    # Check if already seeded
    existing_check = db.query(AirfareObservation).filter(
        AirfareObservation.origin.in_(["AMD", "GOI", "JAI", "COK"])
    ).count()

    if existing_check > 5000:
        logger.info(f"Regional observations already seeded ({existing_check} existing). Updating routes table...")
        _sync_routes(db)
        db.close()
        return

    logger.info(f"Generating observations for {len(REGIONAL_SPECS)} regional routes across {total_days} days...")

    records = []
    now = datetime.now()

    for origin, dest, base_fare, duration in REGIONAL_SPECS:
        # Generate ~35 observations per month (about 1-2 per day) across 20 months
        # That's ~700 observations per route, giving rock solid baseline & monthly indices
        obs_dates = [start_date + timedelta(days=int(d)) for d in np.linspace(0, total_days, 700)]
        for t_date in obs_dates:
            airline = random.choice(AIRLINES)
            is_business = (random.random() < 0.22)
            cabin = "Business" if is_business else "Economy"
            stops = 1 if (random.random() < 0.15) else 0
            days_left = int(rng.integers(1, 45))
            booking_date = t_date - timedelta(days=days_left)

            # Demand curve
            if days_left <= 3:
                demand = rng.uniform(1.6, 2.2)
            elif days_left <= 7:
                demand = rng.uniform(1.3, 1.6)
            elif days_left <= 14:
                demand = rng.uniform(1.05, 1.3)
            elif days_left <= 30:
                demand = rng.uniform(0.95, 1.1)
            else:
                demand = rng.uniform(0.85, 0.98)

            cabin_mult = 3.2 if is_business else 1.0
            stops_mult = 0.92 if stops > 0 else 1.0
            airline_mult = AIRLINE_FACTORS.get(airline, 1.0)
            noise = rng.uniform(0.92, 1.08)

            # Monthly seasonal adjustment (simulates realistic inflation / seasonal fare movement)
            # Baseline (Feb-Apr 2025) ~ 1.0, Summer ~ 1.08, Monsoon ~ 0.94, Festive (Oct-Dec) ~ 1.14
            m = t_date.month
            if m in [5, 6]:
                seasonal = 1.08
            elif m in [7, 8]:
                seasonal = 0.95
            elif m in [10, 11, 12]:
                seasonal = 1.15
            else:
                seasonal = 1.02

            fare = round(base_fare * demand * cabin_mult * stops_mult * airline_mult * seasonal * noise, 0)
            dep_time = random.choice(DEPARTURE_SLOTS)
            arr_dt = datetime.strptime(dep_time, "%H:%M") + timedelta(minutes=duration + (stops * 45))
            arr_time = arr_dt.strftime("%H:%M")

            records.append({
                "source": "historical_augmented",
                "airline": airline,
                "origin": origin,
                "destination": dest,
                "travel_date": t_date,
                "booking_date": booking_date,
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "stops": stops,
                "duration_minutes": duration + (stops * 45),
                "cabin_class": cabin,
                "fare": float(fare),
                "currency": "INR",
                "days_left": days_left,
                "is_demo_anomaly": False,
                "collected_at": now,
                "created_at": now,
            })

    # Bulk insert
    batch_size = 5000
    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        db.bulk_insert_mappings(AirfareObservation, batch)
        db.commit()
        inserted += len(batch)
        logger.info(f"Inserted {inserted}/{len(records)} regional records...")

    _sync_routes(db)
    db.close()
    logger.info("Regional route seeding complete.")

def _sync_routes(db: Session):
    """Ensure all routes in AirfareObservation exist in Route table with accurate counts."""
    from sqlalchemy import func
    route_counts = (
        db.query(
            AirfareObservation.origin,
            AirfareObservation.destination,
            func.count(AirfareObservation.id).label("cnt"),
        )
        .group_by(AirfareObservation.origin, AirfareObservation.destination)
        .all()
    )

    for orig, dest, count in route_counts:
        existing = db.query(Route).filter(
            Route.origin == orig,
            Route.destination == dest,
        ).first()

        orig_name = IATA_CITY_MAP.get(orig) or ADDITIONAL_CITIES.get(orig, orig)
        dest_name = IATA_CITY_MAP.get(dest) or ADDITIONAL_CITIES.get(dest, dest)

        if existing:
            existing.observation_count = count
            if not existing.origin_name:
                existing.origin_name = orig_name
            if not existing.destination_name:
                existing.destination_name = dest_name
        else:
            new_r = Route(
                origin=orig,
                destination=dest,
                origin_name=orig_name,
                destination_name=dest_name,
                observation_count=count,
            )
            db.add(new_r)

    # Delete any ghost routes with 0 observations
    ghost_routes = db.query(Route).all()
    valid_pairs = {(r[0], r[1]) for r in route_counts}
    for r in ghost_routes:
        if (r.origin, r.destination) not in valid_pairs:
            logger.info(f"Removing ghost route {r.origin}->{r.destination} with 0 obs")
            db.delete(r)

    db.commit()
    logger.info("Routes table synchronized with observation counts.")

if __name__ == "__main__":
    seed_regional_routes()
