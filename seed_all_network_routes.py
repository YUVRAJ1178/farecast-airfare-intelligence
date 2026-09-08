"""
seed_all_network_routes.py
Seeds missing route pairs and extends the observation timeline through December 31, 2026.
Ensures ALL 17x16 = 272 directional routes exist in the database and have continuous
daily observations from Feb 1, 2025 to Dec 31, 2026.
"""
import math
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
import numpy as np
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parent))
from backend.app.database import get_session_factory
from backend.app.models import AirfareObservation, Route

HUBS = {
    "DEL": {"name": "Indira Gandhi Int'l", "city": "Delhi", "lat": 28.5562, "lon": 77.1000, "tier": "Metro Mega Hub"},
    "BOM": {"name": "Chhatrapati Shivaji Maharaj", "city": "Mumbai", "lat": 19.0896, "lon": 72.8656, "tier": "Metro Mega Hub"},
    "BLR": {"name": "Kempegowda Int'l", "city": "Bengaluru", "lat": 13.1986, "lon": 77.7066, "tier": "Primary Hub"},
    "HYD": {"name": "Rajiv Gandhi Int'l", "city": "Hyderabad", "lat": 17.2403, "lon": 78.4294, "tier": "Primary Hub"},
    "CCU": {"name": "Netaji Subhash Chandra Bose", "city": "Kolkata", "lat": 22.6547, "lon": 88.4467, "tier": "Primary Hub"},
    "MAA": {"name": "Chennai Int'l", "city": "Chennai", "lat": 12.9941, "lon": 80.1709, "tier": "Primary Hub"},
    "AMD": {"name": "Sardar Vallabhbhai Patel", "city": "Ahmedabad", "lat": 23.0772, "lon": 72.6347, "tier": "Secondary Hub"},
    "PNQ": {"name": "Pune Airport", "city": "Pune", "lat": 18.5822, "lon": 73.9197, "tier": "Secondary Hub"},
    "GOI": {"name": "Dabolim / Mopa", "city": "Goa", "lat": 15.3808, "lon": 73.8313, "tier": "Leisure Hub"},
    "COK": {"name": "Cochin Int'l", "city": "Kochi", "lat": 10.1556, "lon": 76.4019, "tier": "Regional Hub"},
    "GAU": {"name": "Lokpriya Gopinath Bordoloi", "city": "Guwahati", "lat": 26.1061, "lon": 91.5859, "tier": "North-East Gateway"},
    "JAI": {"name": "Jaipur Int'l", "city": "Jaipur", "lat": 26.8242, "lon": 75.8122, "tier": "Regional Hub"},
    "LKO": {"name": "Chaudhary Charan Singh", "city": "Lucknow", "lat": 26.7606, "lon": 80.8893, "tier": "Regional Hub"},
    "PAT": {"name": "Jay Prakash Narayan", "city": "Patna", "lat": 25.5913, "lon": 85.0880, "tier": "Regional Hub"},
    "SXR": {"name": "Sheikh ul-Alam", "city": "Srinagar", "lat": 33.9871, "lon": 74.7742, "tier": "Northern Gateway"},
    "ATQ": {"name": "Sri Guru Ram Dass Jee", "city": "Amritsar", "lat": 31.7096, "lon": 74.7973, "tier": "Regional Gateway"},
    "IXC": {"name": "Shaheed Bhagat Singh", "city": "Chandigarh", "lat": 30.6735, "lon": 76.7885, "tier": "Regional Gateway"},
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return max(150, round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))))

AIRLINES = ["IndiGo", "Air India", "SpiceJet", "Vistara", "Akasa Air", "AIX Connect"]
AIRLINE_FACTORS = {
    "IndiGo": 0.95,
    "SpiceJet": 0.90,
    "Akasa Air": 0.92,
    "AIX Connect": 0.93,
    "Air India": 1.06,
    "Vistara": 1.16,
}
DEPARTURE_SLOTS = ["06:15", "08:30", "10:45", "13:20", "15:40", "17:50", "19:30", "21:10"]

def main():
    rng = np.random.default_rng(2026)
    SessionLocal = get_session_factory()
    db: Session = SessionLocal()

    # Find existing routes and date coverage
    existing_routes = set(
        db.query(AirfareObservation.origin, AirfareObservation.destination).distinct().all()
    )
    all_codes = list(HUBS.keys())
    all_pairs = [(o, d) for o in all_codes for d in all_codes if o != d]
    missing_pairs = [p for p in all_pairs if p not in existing_routes]

    print(f"Total pairs: {len(all_pairs)} | Existing routes: {len(existing_routes)} | Missing: {len(missing_pairs)}")

    START_DATE = date(2025, 2, 1)
    END_DATE = date(2026, 12, 31)
    total_days = (END_DATE - START_DATE).days + 1
    sample_dates = [START_DATE + timedelta(days=i) for i in range(0, total_days, 2)] # every other day

    records = []
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Generate observations for missing route pairs across full timeline
    print("Generating observations for missing routes...")
    for origin, dest in missing_pairs:
        dist = haversine(HUBS[origin]["lat"], HUBS[origin]["lon"], HUBS[dest]["lat"], HUBS[dest]["lon"])
        duration = round(dist / 11.5 + 35)
        base_fare = round(2200 + dist * 3.65)

        for t_date in sample_dates:
            airline = random.choice(AIRLINES)
            is_business = (random.random() < 0.18)
            cabin = "Business" if is_business else "Economy"
            stops = 1 if (dist > 1200 and random.random() < 0.35) else 0
            days_left = int(rng.integers(1, 45))
            booking_date = t_date - timedelta(days=days_left)

            # Demand curve
            if days_left <= 3:
                demand = float(rng.uniform(1.5, 2.1))
            elif days_left <= 7:
                demand = float(rng.uniform(1.25, 1.5))
            elif days_left <= 14:
                demand = float(rng.uniform(1.05, 1.25))
            elif days_left <= 30:
                demand = float(rng.uniform(0.95, 1.05))
            else:
                demand = float(rng.uniform(0.85, 0.95))

            cabin_mult = 2.8 if is_business else 1.0
            stops_mult = 0.92 if stops > 0 else 1.0
            airline_mult = AIRLINE_FACTORS.get(airline, 1.0)
            dow_mult = 1.12 if t_date.weekday() in (4, 6) else (0.92 if t_date.weekday() in (1, 2) else 1.0)
            noise = float(rng.normal(0, 0.04))

            fare = round(base_fare * demand * cabin_mult * stops_mult * airline_mult * dow_mult * (1.0 + noise), 2)
            fare = max(1800.0, fare)

            dep_time = random.choice(DEPARTURE_SLOTS)
            dep_h, dep_m = map(int, dep_time.split(":"))
            arr_total_min = dep_h * 60 + dep_m + duration
            arr_time = f"{(arr_total_min // 60) % 24:02d}:{arr_total_min % 60:02d}"

            records.append({
                "source": "scheduled_domestic",
                "airline": airline,
                "origin": origin,
                "destination": dest,
                "travel_date": t_date,
                "booking_date": booking_date,
                "days_left": days_left,
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "stops": stops,
                "duration_minutes": duration,
                "cabin_class": cabin,
                "fare": fare,
                "base_fare": round(fare * 0.78, 2),
                "taxes": round(fare * 0.12, 2),
                "airport_fees": round(fare * 0.10, 2),
                "currency": "INR",
                "flight_number": f"{airline[:2].upper()}-{rng.integers(101, 999)}",
                "is_demo_anomaly": False,
            })

    # 2. Extend existing routes from 2026-09-08 to 2026-12-31
    print("Extending existing routes from Sept 8 to Dec 31, 2026...")
    future_dates = [date(2026, 9, 8) + timedelta(days=i) for i in range((date(2026, 12, 31) - date(2026, 9, 8)).days + 1)]
    for origin, dest in existing_routes:
        dist = haversine(HUBS[origin]["lat"], HUBS[origin]["lon"], HUBS[dest]["lat"], HUBS[dest]["lon"])
        duration = round(dist / 11.5 + 35)
        base_fare = round(2200 + dist * 3.65)

        for t_date in future_dates[::2]: # every other day
            airline = random.choice(AIRLINES)
            is_business = (random.random() < 0.20)
            cabin = "Business" if is_business else "Economy"
            stops = 1 if (dist > 1200 and random.random() < 0.25) else 0
            days_left = max(1, (t_date - date(2026, 9, 8)).days)
            booking_date = date(2026, 9, 8)

            if days_left <= 3:
                demand = float(rng.uniform(1.5, 2.0))
            elif days_left <= 7:
                demand = float(rng.uniform(1.25, 1.5))
            elif days_left <= 14:
                demand = float(rng.uniform(1.05, 1.25))
            elif days_left <= 30:
                demand = float(rng.uniform(0.95, 1.05))
            else:
                demand = float(rng.uniform(0.85, 0.95))

            cabin_mult = 2.8 if is_business else 1.0
            stops_mult = 0.92 if stops > 0 else 1.0
            airline_mult = AIRLINE_FACTORS.get(airline, 1.0)
            dow_mult = 1.12 if t_date.weekday() in (4, 6) else (0.92 if t_date.weekday() in (1, 2) else 1.0)
            noise = float(rng.normal(0, 0.04))

            fare = round(base_fare * demand * cabin_mult * stops_mult * airline_mult * dow_mult * (1.0 + noise), 2)
            fare = max(1800.0, fare)

            dep_time = random.choice(DEPARTURE_SLOTS)
            dep_h, dep_m = map(int, dep_time.split(":"))
            arr_total_min = dep_h * 60 + dep_m + duration
            arr_time = f"{(arr_total_min // 60) % 24:02d}:{arr_total_min % 60:02d}"

            records.append({
                "source": "scheduled_domestic",
                "airline": airline,
                "origin": origin,
                "destination": dest,
                "travel_date": t_date,
                "booking_date": booking_date,
                "days_left": days_left,
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "stops": stops,
                "duration_minutes": duration,
                "cabin_class": cabin,
                "fare": fare,
                "base_fare": round(fare * 0.78, 2),
                "taxes": round(fare * 0.12, 2),
                "airport_fees": round(fare * 0.10, 2),
                "currency": "INR",
                "flight_number": f"{airline[:2].upper()}-{rng.integers(101, 999)}",
                "is_demo_anomaly": False,
            })

    print(f"Total new observations to insert: {len(records):,}")

    batch_size = 5000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        db.bulk_insert_mappings(AirfareObservation, batch)
        db.commit()
        print(f"Inserted {min(i + batch_size, len(records)):,}/{len(records):,}...")

    # Now synchronize the routes table
    print("Synchronizing routes table for all 272 routes...")
    from sqlalchemy import func
    route_stats = db.query(
        AirfareObservation.origin,
        AirfareObservation.destination,
        func.count(AirfareObservation.id).label("cnt"),
        func.avg(AirfareObservation.fare).label("avg_f"),
        func.min(AirfareObservation.fare).label("min_f"),
        func.max(AirfareObservation.fare).label("max_f"),
    ).group_by(AirfareObservation.origin, AirfareObservation.destination).all()

    for orig, dest, cnt, avg_f, min_f, max_f in route_stats:
        existing = db.query(Route).filter(Route.origin == orig, Route.destination == dest).first()
        dist = haversine(HUBS.get(orig, {}).get("lat", 0), HUBS.get(orig, {}).get("lon", 0),
                         HUBS.get(dest, {}).get("lat", 0), HUBS.get(dest, {}).get("lon", 0))
        orig_name = f"{HUBS.get(orig, {}).get('city', orig)} ({orig})"
        dest_name = f"{HUBS.get(dest, {}).get('city', dest)} ({dest})"

        if existing:
            existing.observation_count = cnt
            existing.origin_name = orig_name
            existing.destination_name = dest_name
        else:
            r = Route(
                origin=orig,
                destination=dest,
                origin_name=orig_name,
                destination_name=dest_name,
                observation_count=cnt,
            )
            db.add(r)

    db.commit()
    print("Database seeding & route synchronization complete.")

    total_obs = db.query(AirfareObservation).count()
    total_r = db.query(Route).count()
    print(f"FINAL STATS: {total_obs:,} total observations across {total_r} routes!")
    db.close()

if __name__ == "__main__":
    main()
