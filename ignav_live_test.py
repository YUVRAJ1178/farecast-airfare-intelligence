"""
IGNAV LIVE INTEGRATION TEST
===========================
Makes a genuine Ignav API call for DEL → BOM, stores the result in the DB,
and prints a structured report.

SECURITY:
- IGNAV_API_KEY read from .env — never printed, never hardcoded
- Run from project root: py -3 ignav_live_test.py
"""
import sys
import os
from pathlib import Path
from datetime import date, datetime, timedelta

# ── Path setup ───────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# ── Logging ──────────────────────────────────────────────────
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("ignav_live_test")

# ── Suppress key in any log output ───────────────────────────
api_key = os.getenv("IGNAV_API_KEY", "")
if not api_key:
    print("\n[FATAL] IGNAV_API_KEY not set in .env — cannot proceed.")
    sys.exit(1)

print("\n" + "=" * 60)
print("IGNAV LIVE INTEGRATION TEST -- DEL -> BOM")
print("=" * 60)

# ── Make the live Ignav call ──────────────────────────────────
from backend.app.services.ignav_service import IgnavService

svc = IgnavService()

# Use a departure date ~30 days out (must be a future date)
departure = date.today() + timedelta(days=30)
print(f"\nQuerying: DEL -> BOM  |  Departure: {departure}  |  Economy  |  1 adult")
print("Sending live request to Ignav API...\n")

fares = svc.search_flights(
    origin="DEL",
    destination="BOM",
    departure_date=departure,
    adults=1,
    cabin_class="Economy",
    market="IN",
)

# ── Report API call result ────────────────────────────────────
if not fares:
    print("IGNAV API REQUEST: FAILED (0 results returned or API error)")
    print("REAL FARE RECEIVED: NO")
    ignav_ok = False
else:
    ignav_ok = True
    print(f"IGNAV API REQUEST: SUCCESS ({len(fares)} fare(s) returned)")
    print(f"REAL FARE RECEIVED: YES")
    # Show first fare summary (never print the key)
    f0 = fares[0]
    print(f"FARE:              INR {f0['fare']:.2f} {f0['currency']}")
    print(f"AIRLINE:           {f0['airline']}")
    print(f"FLIGHT NUMBER:     {f0.get('flight_number', 'N/A')}")
    print(f"DEPARTURE:         {f0.get('departure_time', 'N/A')}")
    print(f"ARRIVAL:           {f0.get('arrival_time', 'N/A')}")
    print(f"STOPS:             {f0.get('stops', 'N/A')}")
    print(f"SOURCE:            {f0['source']}")
    print(f"PROVENANCE:        {f0['source_provenance']}")
    print(f"COLLECTED AT:      {f0['collected_at']}")

# ── Persist to database ───────────────────────────────────────
print("\n--- DATABASE STORAGE ---")
db_ok = False
stored_id = None
if fares:
    try:
        from backend.app.database import get_session_factory, init_db
        from backend.app.models import AirfareObservation, Base

        init_db()
        SessionLocal = get_session_factory()
        db_cols = {c.key for c in AirfareObservation.__table__.columns}

        with SessionLocal() as db:
            stored = []
            for fare_dict in fares:
                clean = {k: v for k, v in fare_dict.items() if k in db_cols}
                obs = AirfareObservation(**clean)
                db.add(obs)
                stored.append(obs)
            db.flush()
            ids = [o.id for o in stored]
            db.commit()

        # Verify read-back
        with SessionLocal() as db:
            check = (
                db.query(AirfareObservation)
                .filter(
                    AirfareObservation.source == "ignav",
                    AirfareObservation.source_provenance == "REAL_API",
                    AirfareObservation.origin == "DEL",
                    AirfareObservation.destination == "BOM",
                )
                .order_by(AirfareObservation.id.desc())
                .first()
            )
            if check:
                stored_id = check.id
                db_ok = True
                print(f"DATABASE STORAGE: PASS  (row id={stored_id}, fare=INR {check.fare:.2f})")
                print(f"  source_provenance = {check.source_provenance}")
                print(f"  provider (source) = {check.source}")
            else:
                print("DATABASE STORAGE: FAIL  (row not found after commit)")
    except Exception as e:
        print(f"DATABASE STORAGE: FAIL  ({e})")
else:
    print("DATABASE STORAGE: SKIP (no fares to store)")

# ── Check /fares/provenance-summary ──────────────────────────
print("\n--- PROVENANCE SUMMARY ---")
try:
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)
    resp = client.get("/fares/provenance-summary")
    if resp.status_code == 200:
        prov = resp.json()
        real_api_count = prov.get("counts", {}).get("REAL_API", 0)
        real_api_pct = prov.get("percentages", {}).get("REAL_API", 0.0)
        print(f"REAL_API count: {real_api_count}  ({real_api_pct:.2f}%)")
        print(f"Total observations: {prov.get('total_observations', '?')}")
        print(f"Audit status: {prov.get('audit_status', '?')}")
        prov_pass = real_api_count >= (len(fares) if fares else 0)
        print(f"REAL_API PROVENANCE: {'PASS' if prov_pass else 'FAIL'}")
    else:
        print(f"REAL_API PROVENANCE: FAIL (HTTP {resp.status_code})")
        prov_pass = False
except Exception as e:
    print(f"REAL_API PROVENANCE: FAIL ({e})")
    prov_pass = False

# ── Check /prediction/ ────────────────────────────────────────
print("\n--- PREDICTION ENDPOINT ---")
pred_pass = False
try:
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)
    resp = client.get("/prediction/")
    pred_pass = resp.status_code == 200
    data = resp.json()
    print(f"Status: {resp.status_code}")
    print(f"Model ready: {data.get('model_ready', '?')}")
    print(f"PREDICTION: {'PASS' if pred_pass else 'FAIL'}")
except Exception as e:
    print(f"PREDICTION: FAIL ({e})")

# ── Final report ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)
print(f"IGNAV API REQUEST:     {'SUCCESS' if ignav_ok else 'FAILED'}")
print(f"REAL FARE RECEIVED:    {'YES' if ignav_ok else 'NO'}")
if ignav_ok:
    f0 = fares[0]
    print(f"FARE:                  INR {f0['fare']:.2f} {f0['currency']}")
    print(f"AIRLINE:               {f0['airline']}")
else:
    print("FARE:                  N/A")
    print("AIRLINE:               N/A")
print(f"REAL_API PROVENANCE:   {'PASS' if prov_pass else 'FAIL'}")
print(f"DATABASE STORAGE:      {'PASS' if db_ok else 'FAIL'}")
print(f"PREDICTION:            {'PASS' if pred_pass else 'FAIL'}")
print("=" * 60)
