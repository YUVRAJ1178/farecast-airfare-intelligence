"""
Airfare Intelligence Platform — Demo / Synthetic Data Generator
Phase 2: Historical Data Ingestion

This module generates realistic synthetic airfare data for DEMO MODE.

IMPORTANT LABELLING:
  - All generated data is tagged with source = DataSource.DEMO
  - This data is NEVER presented as real or live
  - The UI must always show "Historical / Demo Data" when this data is displayed
"""

import logging
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.schema import DataSource, IATA_CITY_MAP

logger = logging.getLogger(__name__)

# Seed for reproducibility
RNG_SEED = 42
rng = np.random.default_rng(RNG_SEED)

# ── Route definitions (major Indian city pairs) ───────────────
DEMO_ROUTES = [
    ("DEL", "BOM"), ("BOM", "DEL"),
    ("DEL", "BLR"), ("BLR", "DEL"),
    ("DEL", "HYD"), ("HYD", "DEL"),
    ("DEL", "MAA"), ("MAA", "DEL"),
    ("DEL", "CCU"), ("CCU", "DEL"),
    ("BOM", "BLR"), ("BLR", "BOM"),
    ("BOM", "HYD"), ("HYD", "BOM"),
    ("BOM", "MAA"), ("MAA", "BOM"),
    ("BOM", "CCU"), ("CCU", "BOM"),
    ("BLR", "HYD"), ("HYD", "BLR"),
    ("BLR", "MAA"), ("MAA", "BLR"),
    ("BLR", "CCU"), ("CCU", "BLR"),
    ("HYD", "CCU"), ("CCU", "HYD"),
    ("HYD", "MAA"), ("MAA", "HYD"),
    ("CCU", "MAA"), ("MAA", "CCU"),
    # Regional & secondary routes
    ("AMD", "DEL"), ("DEL", "AMD"),
    ("AMD", "BOM"), ("BOM", "AMD"),
    ("GOI", "BOM"), ("BOM", "GOI"),
    ("GOI", "DEL"), ("DEL", "GOI"),
    ("GOI", "BLR"), ("BLR", "GOI"),
    ("JAI", "BOM"), ("BOM", "JAI"),
    ("JAI", "DEL"), ("DEL", "JAI"),
    ("COK", "DEL"), ("DEL", "COK"),
    ("COK", "BOM"), ("BOM", "COK"),
    ("COK", "BLR"), ("BLR", "COK"),
    ("PNQ", "DEL"), ("DEL", "PNQ"),
    ("PNQ", "BLR"), ("BLR", "PNQ"),
    ("GAU", "DEL"), ("DEL", "GAU"),
    ("GAU", "CCU"), ("CCU", "GAU"),
    ("LKO", "DEL"), ("DEL", "LKO"),
    ("LKO", "BOM"), ("BOM", "LKO"),
    ("PAT", "DEL"), ("DEL", "PAT"),
    ("SXR", "DEL"), ("DEL", "SXR"),
    ("ATQ", "DEL"), ("DEL", "ATQ"),
    ("IXC", "DEL"), ("DEL", "IXC"),
    ("IXC", "BOM"), ("BOM", "IXC"),
]

DEMO_AIRLINES = [
    "IndiGo",
    "Air India",
    "SpiceJet",
    "Vistara",
    "AirAsia India",
    "Akasa Air",
    "Go First",
]

# Base fares per route (approximate realistic INR values for Economy)
BASE_FARES: dict[tuple[str, str], float] = {
    ("DEL", "BOM"): 4500, ("BOM", "DEL"): 4500,
    ("DEL", "BLR"): 5200, ("BLR", "DEL"): 5200,
    ("DEL", "HYD"): 4800, ("HYD", "DEL"): 4800,
    ("DEL", "MAA"): 5500, ("MAA", "DEL"): 5500,
    ("DEL", "CCU"): 4200, ("CCU", "DEL"): 4200,
    ("BOM", "BLR"): 3800, ("BLR", "BOM"): 3800,
    ("BOM", "HYD"): 4000, ("HYD", "BOM"): 4000,
    ("BOM", "MAA"): 4200, ("MAA", "BOM"): 4200,
    ("BOM", "CCU"): 5500, ("CCU", "BOM"): 5500,
    ("BLR", "HYD"): 2800, ("HYD", "BLR"): 2800,
    ("BLR", "MAA"): 2500, ("MAA", "BLR"): 2500,
    ("BLR", "CCU"): 5200, ("CCU", "BLR"): 5200,
    ("HYD", "CCU"): 4600, ("CCU", "HYD"): 4600,
    ("HYD", "MAA"): 3200, ("MAA", "HYD"): 3200,
    ("CCU", "MAA"): 4800, ("MAA", "CCU"): 4800,
    ("GOI", "DEL"): 5800, ("DEL", "GOI"): 5800,
    ("GOI", "BOM"): 3500, ("BOM", "GOI"): 3500,
    ("GOI", "BLR"): 3200, ("BLR", "GOI"): 3200,
    ("JAI", "BOM"): 4600, ("BOM", "JAI"): 4600,
    ("JAI", "DEL"): 2800, ("DEL", "JAI"): 2800,
    ("AMD", "DEL"): 3600, ("DEL", "AMD"): 3600,
    ("AMD", "BOM"): 3200, ("BOM", "AMD"): 3200,
    ("COK", "DEL"): 6500, ("DEL", "COK"): 6500,
    ("COK", "BOM"): 4500, ("BOM", "COK"): 4500,
    ("COK", "BLR"): 2800, ("BLR", "COK"): 2800,
    ("PNQ", "DEL"): 4800, ("DEL", "PNQ"): 4800,
    ("PNQ", "BLR"): 3800, ("BLR", "PNQ"): 3800,
    ("GAU", "DEL"): 5600, ("DEL", "GAU"): 5600,
    ("GAU", "CCU"): 3200, ("CCU", "GAU"): 3200,
    ("LKO", "DEL"): 2900, ("DEL", "LKO"): 2900,
    ("LKO", "BOM"): 4800, ("BOM", "LKO"): 4800,
    ("PAT", "DEL"): 4200, ("DEL", "PAT"): 4200,
    ("SXR", "DEL"): 5200, ("DEL", "SXR"): 5200,
    ("ATQ", "DEL"): 3100, ("DEL", "ATQ"): 3100,
    ("IXC", "DEL"): 2800, ("DEL", "IXC"): 2800,
    ("IXC", "BOM"): 4900, ("BOM", "IXC"): 4900,
}

# Cabin class fare multipliers
CABIN_MULTIPLIERS = {
    "Economy": 1.0,
    "Premium Economy": 1.8,
    "Business": 3.5,
}

# Stops fare adjustment
STOPS_ADJUSTMENT = {
    0: 1.05,   # Non-stop is often more expensive
    1: 1.0,    # One stop is baseline
    2: 0.85,   # More stops = cheaper usually
}

# Airline price factor (relative to base — simulates market positioning)
AIRLINE_FACTORS = {
    "IndiGo": 0.92,
    "SpiceJet": 0.88,
    "AirAsia India": 0.85,
    "Akasa Air": 0.90,
    "Go First": 0.88,
    "Air India": 1.05,
    "Vistara": 1.18,
}

DEPARTURE_SLOTS = ["06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"]

# Duration estimates per route (minutes)
ROUTE_DURATIONS: dict[tuple[str, str], int] = {
    ("DEL", "BOM"): 135, ("BOM", "DEL"): 135,
    ("DEL", "BLR"): 165, ("BLR", "DEL"): 165,
    ("DEL", "HYD"): 150, ("HYD", "DEL"): 150,
    ("DEL", "MAA"): 180, ("MAA", "DEL"): 180,
    ("DEL", "CCU"): 135, ("CCU", "DEL"): 135,
    ("BOM", "BLR"): 105, ("BLR", "BOM"): 105,
    ("BOM", "HYD"): 90,  ("HYD", "BOM"): 90,
    ("BOM", "MAA"): 120, ("MAA", "BOM"): 120,
    ("BOM", "CCU"): 180, ("CCU", "BOM"): 180,
    ("BLR", "HYD"): 70,  ("HYD", "BLR"): 70,
    ("BLR", "MAA"): 70,  ("MAA", "BLR"): 70,
    ("BLR", "CCU"): 150, ("CCU", "BLR"): 150,
    ("HYD", "CCU"): 130, ("CCU", "HYD"): 130,
    ("HYD", "MAA"): 75,  ("MAA", "HYD"): 75,
    ("CCU", "MAA"): 140, ("MAA", "CCU"): 140,
    ("GOI", "DEL"): 145, ("DEL", "GOI"): 145,
    ("GOI", "BOM"): 75,  ("BOM", "GOI"): 75,
    ("GOI", "BLR"): 75,  ("BLR", "GOI"): 75,
    ("JAI", "BOM"): 110, ("BOM", "JAI"): 110,
    ("JAI", "DEL"): 60,  ("DEL", "JAI"): 60,
    ("AMD", "DEL"): 85,  ("DEL", "AMD"): 85,
    ("AMD", "BOM"): 75,  ("BOM", "AMD"): 75,
    ("COK", "DEL"): 190, ("DEL", "COK"): 190,
    ("COK", "BOM"): 115, ("BOM", "COK"): 115,
    ("COK", "BLR"): 65,  ("BLR", "COK"): 65,
    ("PNQ", "DEL"): 130, ("DEL", "PNQ"): 130,
    ("PNQ", "BLR"): 95,  ("BLR", "PNQ"): 95,
    ("GAU", "DEL"): 155, ("DEL", "GAU"): 155,
    ("GAU", "CCU"): 75,  ("CCU", "GAU"): 75,
    ("LKO", "DEL"): 70,  ("DEL", "LKO"): 70,
    ("LKO", "BOM"): 130, ("BOM", "LKO"): 130,
    ("PAT", "DEL"): 100, ("DEL", "PAT"): 100,
    ("SXR", "DEL"): 95,  ("DEL", "SXR"): 95,
    ("ATQ", "DEL"): 65,  ("DEL", "ATQ"): 65,
    ("IXC", "DEL"): 60,  ("DEL", "IXC"): 60,
    ("IXC", "BOM"): 135, ("BOM", "IXC"): 135,
}


def _generate_fare(
    origin: str,
    destination: str,
    airline: str,
    cabin: str,
    stops: int,
    days_left: int,
) -> float:
    """Generate a realistic fare with noise and demand patterns."""
    base = BASE_FARES.get((origin, destination), 5000.0)

    # Demand curve: fares rise as days_left decreases (closer to departure)
    if days_left <= 3:
        demand_factor = rng.uniform(1.8, 2.8)
    elif days_left <= 7:
        demand_factor = rng.uniform(1.4, 1.9)
    elif days_left <= 14:
        demand_factor = rng.uniform(1.1, 1.5)
    elif days_left <= 30:
        demand_factor = rng.uniform(0.95, 1.2)
    elif days_left <= 60:
        demand_factor = rng.uniform(0.85, 1.0)
    else:
        demand_factor = rng.uniform(0.75, 0.95)

    cabin_mult = CABIN_MULTIPLIERS.get(cabin, 1.0)
    stops_adj = STOPS_ADJUSTMENT.get(stops, 1.0)
    airline_factor = AIRLINE_FACTORS.get(airline, 1.0)

    # Add realistic noise ±12%
    noise = rng.uniform(0.88, 1.12)

    fare = base * demand_factor * cabin_mult * stops_adj * airline_factor * noise
    return round(max(fare, 999.0), 0)  # Minimum realistic fare


def generate_demo_dataset(
    n_records: int = 50000,
    start_date: date = date(2023, 1, 1),
    end_date: date = date(2024, 6, 30),
    output_path: Path = None,
) -> pd.DataFrame:
    """
    Generate a synthetic demo dataset.

    Returns a DataFrame conforming to the normalized airfare schema
    with source = DataSource.DEMO.

    This data is clearly tagged and must NEVER be presented as real.
    """
    logger.info(f"Generating {n_records} synthetic DEMO fare observations...")

    records = []
    date_range = (end_date - start_date).days

    for _ in range(n_records):
        origin, destination = random.choice(DEMO_ROUTES)
        airline = random.choice(DEMO_AIRLINES)
        cabin = random.choices(
            list(CABIN_MULTIPLIERS.keys()),
            weights=[0.75, 0.10, 0.15],
            k=1,
        )[0]
        stops_weights = [0.55, 0.40, 0.05]
        stops = random.choices([0, 1, 2], weights=stops_weights, k=1)[0]
        days_left = int(rng.integers(1, 90))

        # Travel date
        travel_offset = int(rng.integers(0, date_range))
        travel_date = start_date + timedelta(days=travel_offset)
        booking_date = travel_date - timedelta(days=days_left)

        dep_time = random.choice(DEPARTURE_SLOTS)
        base_duration = ROUTE_DURATIONS.get((origin, destination), 120)
        duration = int(base_duration + (stops * rng.integers(30, 90)))
        arr_dt = datetime.strptime(dep_time, "%H:%M") + timedelta(minutes=duration)
        arr_time = arr_dt.strftime("%H:%M")

        fare = _generate_fare(origin, destination, airline, cabin, stops, days_left)

        records.append({
            "source": DataSource.DEMO,
            "airline": airline,
            "origin": origin,
            "destination": destination,
            "travel_date": travel_date,
            "booking_date": booking_date,
            "departure_time": dep_time,
            "arrival_time": arr_time,
            "stops": stops,
            "duration_minutes": duration,
            "cabin_class": cabin,
            "fare": fare,
            "currency": "INR",
            "days_left": days_left,
            "is_demo_anomaly": False,
            "collected_at": datetime.now(),
        })

    df = pd.DataFrame(records)
    logger.info(f"Generated demo dataset: {df.shape}")
    logger.info(f"Demo data NOTE: This is synthetic data tagged source='{DataSource.DEMO}'")
    logger.info(f"  Routes: {df.groupby(['origin','destination']).size().shape[0]}")
    logger.info(f"  Airlines: {sorted(df['airline'].unique())}")
    logger.info(f"  Fare range: ₹{df['fare'].min():,.0f} – ₹{df['fare'].max():,.0f}")
    logger.info(f"  Date range: {df['travel_date'].min()} – {df['travel_date'].max()}")

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Saved demo data to {output_path}")

    return df


def generate_demo_anomalies(df: pd.DataFrame, n_anomalies: int = 15) -> pd.DataFrame:
    """
    Seed clearly-labelled demo anomaly examples.
    These are injected fare observations that are unusual relative to the route baseline.
    They are ALWAYS tagged source=DataSource.DEMO and flagged is_demo_anomaly=True.
    """
    if df.empty:
        return df

    anomaly_records = []
    routes = list(df.groupby(["origin", "destination"]).groups.keys())
    selected_routes = random.sample(routes, min(n_anomalies, len(routes)))

    for origin, destination in selected_routes:
        route_df = df[(df["origin"] == origin) & (df["destination"] == destination)]
        if len(route_df) < 5:
            continue
        baseline = route_df["fare"].median()
        # Create an anomalously high fare (+50–150% above baseline)
        anomaly_factor = rng.uniform(1.5, 2.5)
        anomaly_fare = round(baseline * anomaly_factor, 0)

        sample = route_df.sample(1, random_state=42).iloc[0].to_dict()
        sample["fare"] = anomaly_fare
        sample["source"] = DataSource.DEMO
        sample["is_demo_anomaly"] = True
        anomaly_records.append(sample)

    if anomaly_records:
        anomaly_df = pd.DataFrame(anomaly_records)
        df = pd.concat([df, anomaly_df], ignore_index=True)
        logger.info(f"Injected {len(anomaly_records)} demo anomaly records (clearly tagged)")

    return df
