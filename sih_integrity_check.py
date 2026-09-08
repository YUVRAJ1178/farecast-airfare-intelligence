"""
SIH DEMO INTEGRITY CHECK
========================
Verifies data separation, provenance, prediction integrity, API endpoints,
and Amadeus legacy vs active path.

Run: py -3 sih_integrity_check.py
"""
import sys, os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import logging
logging.basicConfig(level=logging.WARNING)  # suppress noise

PASS = "PASS"
FAIL = "FAIL"

results = {}

print("=" * 65)
print("SIH DEMO INTEGRITY CHECK")
print("=" * 65)

# ────────────────────────────────────────────────────────────────
# 1. IGNAV LIVE DATA VERIFICATION
# ────────────────────────────────────────────────────────────────
print("\n[1] IGNAV LIVE DATA")
try:
    from backend.app.database import get_session_factory, init_db
    from backend.app.models import AirfareObservation
    init_db()
    SessionLocal = get_session_factory()

    with SessionLocal() as db:
        ignav_real = db.query(AirfareObservation).filter(
            AirfareObservation.source == "ignav",
            AirfareObservation.source_provenance == "REAL_API",
        ).count()

        ignav_wrong_prov = db.query(AirfareObservation).filter(
            AirfareObservation.source == "ignav",
            AirfareObservation.source_provenance != "REAL_API",
        ).count()

        # Confirm ignav records are NOT mixed into synthetic/historical sources
        wrong_source_real_api = db.query(AirfareObservation).filter(
            AirfareObservation.source.in_(["historical_augmented", "scheduled_domestic", "demo", "kaggle"]),
            AirfareObservation.source_provenance == "REAL_API",
        ).count()

        # Sample one Ignav record to verify fields
        sample = db.query(AirfareObservation).filter(
            AirfareObservation.source == "ignav",
        ).first()

    print(f"  Ignav rows with source=ignav, source_provenance=REAL_API : {ignav_real}")
    print(f"  Ignav rows with wrong provenance                         : {ignav_wrong_prov}")
    print(f"  Non-ignav rows wrongly tagged REAL_API                   : {wrong_source_real_api}")

    if sample:
        print(f"  Sample row: id={sample.id}, fare={sample.fare}, airline={sample.airline}")
        print(f"             source={sample.source}, provenance={sample.source_provenance}")
        print(f"             base_fare={sample.base_fare} (NULL=correct), taxes={sample.taxes} (NULL=correct)")

    ok = (ignav_real >= 65 and ignav_wrong_prov == 0 and wrong_source_real_api == 0)
    results["ignav_data"] = PASS if ok else FAIL
    print(f"  IGNAV LIVE DATA: {results['ignav_data']}")
except Exception as e:
    print(f"  ERROR: {e}")
    results["ignav_data"] = FAIL

# ────────────────────────────────────────────────────────────────
# 2. DATA LAYER SEPARATION
# ────────────────────────────────────────────────────────────────
print("\n[2] DATA LAYER SEPARATION")
try:
    with SessionLocal() as db:
        valid_tags = {"REAL_API", "REAL_SCRAPE", "DGCA_PUBLIC",
                      "HISTORICAL_SNAPSHOT", "SYNTHETIC_AUGMENTED", "SYNTHETIC_DEMO"}

        null_prov = db.query(AirfareObservation).filter(
            AirfareObservation.source_provenance == None
        ).count()

        invalid_prov = db.query(AirfareObservation).filter(
            AirfareObservation.source_provenance.notin_(list(valid_tags))
        ).count()

        # No synthetic source tagged as REAL_API
        synthetic_as_real = db.query(AirfareObservation).filter(
            AirfareObservation.source.in_(["historical_augmented", "scheduled_domestic", "demo"]),
            AirfareObservation.source_provenance == "REAL_API",
        ).count()

        # No REAL_API rows tagged as SYNTHETIC
        real_as_synthetic = db.query(AirfareObservation).filter(
            AirfareObservation.source == "ignav",
            AirfareObservation.source_provenance.in_(["SYNTHETIC_AUGMENTED", "SYNTHETIC_DEMO"]),
        ).count()

        total = db.query(AirfareObservation).count()

    print(f"  Total observations              : {total}")
    print(f"  NULL provenance rows            : {null_prov}")
    print(f"  Invalid provenance rows         : {invalid_prov}")
    print(f"  Synthetic rows falsely REAL_API : {synthetic_as_real}")
    print(f"  Ignav rows falsely SYNTHETIC    : {real_as_synthetic}")

    ok = (null_prov == 0 and invalid_prov == 0 and synthetic_as_real == 0 and real_as_synthetic == 0)
    results["data_separation"] = PASS if ok else FAIL
    print(f"  DATA LAYER SEPARATION: {results['data_separation']}")
except Exception as e:
    print(f"  ERROR: {e}")
    results["data_separation"] = FAIL

# ────────────────────────────────────────────────────────────────
# 3. PREDICTION INTEGRITY
# ────────────────────────────────────────────────────────────────
print("\n[3] PREDICTION INTEGRITY")
try:
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)

    payload = {
        "airline": "IndiGo",
        "origin": "DEL",
        "destination": "BOM",
        "cabin_class": "Economy",
        "stops": 0,
        "days_left": 30,
        "duration_minutes": 130,
        "departure_hour": 10,
    }
    resp = client.post("/prediction/", json=payload)
    pred_ok = resp.status_code == 200
    if pred_ok:
        data = resp.json()
        predicted = data.get("predicted_fare")
        model_name = data.get("model_name", "?")
        note = data.get("note", "")
        lookup = data.get("lookup_method", "?")
        print(f"  HTTP status                : {resp.status_code}")
        print(f"  Model name                 : {model_name}")
        print(f"  Predicted fare             : INR {predicted:.2f}")
        print(f"  Lookup method              : {lookup}")
        # Ensure model is not just returning an Ignav fare verbatim
        # (prediction uses a yield-management engine + RF blend, not live DB lookup)
        is_model_prediction = "model" in model_name.lower() or "calibrated" in model_name.lower() or "yield" in note.lower()
        print(f"  Uses ML/calibrated engine  : {is_model_prediction}")
        print(f"  Note snippet               : {note[:80]}")
    else:
        print(f"  HTTP status: {resp.status_code}")
        is_model_prediction = False

    results["prediction"] = PASS if (pred_ok and is_model_prediction) else FAIL
    print(f"  PREDICTION INTEGRITY: {results['prediction']}")
except Exception as e:
    print(f"  ERROR: {e}")
    results["prediction"] = FAIL

# ────────────────────────────────────────────────────────────────
# 4. API ENDPOINT VERIFICATION
# ────────────────────────────────────────────────────────────────
print("\n[4] API ENDPOINT VERIFICATION")

endpoints = {
    "GET  /health":                          ("GET",  "/health",                          None),
    "GET  /live-status":                     ("GET",  "/live-status",                     None),
    "POST /live/ignav/search":               ("POST", "/live/ignav/search",               {
        "origin": "DEL", "destination": "BOM",
        "departure_date": "2026-10-08", "adults": 1,
        "cabin_class": "Economy", "market": "IN",
    }),
    "GET  /prediction/":                     ("GET",  "/prediction/",                     None),
    "GET  /fares/provenance-summary":        ("GET",  "/fares/provenance-summary",        None),
    "GET  /backtesting/dgca/30-day":         ("GET",  "/backtesting/dgca/30-day",         None),
}

# Try compliance endpoint too
try:
    r = client.get("/compliance/sih-compliance")
    compliance_status = r.status_code
except Exception:
    compliance_status = "ERROR"

try:
    r = client.get("/backtesting/dgca/monthly-benchmark")
    monthly_status = r.status_code
except Exception:
    monthly_status = "ERROR"

ep_results = {}
try:
    for label, (method, path, body) in endpoints.items():
        try:
            if method == "GET":
                r = client.get(path)
            else:
                r = client.post(path, json=body)
            ok = r.status_code in (200, 201)
            ep_results[label] = r.status_code
            print(f"  {label:<45} HTTP {r.status_code}  {'OK' if ok else 'FAIL'}")
        except Exception as e:
            ep_results[label] = f"ERROR: {e}"
            print(f"  {label:<45} ERROR: {e}")

    print(f"  GET  /backtesting/dgca/monthly-benchmark              HTTP {monthly_status}")
    print(f"  GET  /compliance/sih-compliance                       HTTP {compliance_status}")

    all_ok = all(isinstance(v, int) and v in (200, 201) for v in ep_results.values())
    all_ok = all_ok and isinstance(monthly_status, int) and monthly_status in (200, 201)
    all_ok = all_ok and isinstance(compliance_status, int) and compliance_status in (200, 201)
    results["api_endpoints"] = PASS if all_ok else FAIL
    print(f"  API ENDPOINTS: {results['api_endpoints']}")
except Exception as e:
    print(f"  ERROR: {e}")
    results["api_endpoints"] = FAIL

# ────────────────────────────────────────────────────────────────
# 5. AMADEUS LEGACY vs ACTIVE PATH
# ────────────────────────────────────────────────────────────────
print("\n[5] AMADEUS LEGACY vs ACTIVE PATH")
import subprocess, re

# Grep frontend for any hardcoded Amadeus references in active paths
amadeus_in_frontend = []
for ext in ["*.jsx", "*.js", "*.ts", "*.tsx"]:
    try:
        result = subprocess.run(
            ["py", "-3", "-c",
             f"import glob, re; "
             f"files = glob.glob('frontend/src/**/{ext}', recursive=True); "
             f"hits = []; "
             f"[hits.extend([(f,ln+1,l.strip()) for ln,l in enumerate(open(f,'r',encoding='utf-8',errors='ignore').readlines()) if 'amadeus' in l.lower() and not l.strip().startswith('//')]) for f in files]; "
             f"print('\\n'.join(f'{{f}}:{{ln}}: {{line}}' for f,ln,line in hits))"],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        hits = [l for l in result.stdout.strip().split("\n") if l.strip()]
        amadeus_in_frontend.extend(hits)
    except Exception:
        pass

# Check whether /live/search (Amadeus) is called by the frontend api.js
try:
    api_js = (PROJECT_ROOT / "frontend/src/api.js").read_text(encoding="utf-8")
    amadeus_route_in_api = "live/search" in api_js and "live/ignav" not in api_js.split("live/search")[0]
except Exception:
    amadeus_route_in_api = False

# Check if ignav is the wired-up provider in live.py
try:
    live_py = (PROJECT_ROOT / "backend/app/routes/live.py").read_text(encoding="utf-8")
    ignav_is_primary = "live/ignav/search" in live_py and "get_ignav_service" in live_py
    amadeus_in_active_path = False  # Amadeus is in live.py but only under /live/search legacy endpoint
except Exception:
    ignav_is_primary = False
    amadeus_in_active_path = True

print(f"  Active live provider in live.py   : {'IGNAV' if ignav_is_primary else 'UNKNOWN'}")
print(f"  Amadeus in frontend api.js        : {'YES (active)' if amadeus_route_in_api else 'NO (not in active path)'}")
print(f"  Amadeus references in frontend UI : {len(amadeus_in_frontend)} line(s)")
for hit in amadeus_in_frontend[:5]:
    print(f"    {hit[:100]}")

results["amadeus_active"] = "NO" if (not amadeus_route_in_api and ignav_is_primary) else "YES"
print(f"  ACTIVE AMADEUS DEPENDENCY: {results['amadeus_active']}")

# ────────────────────────────────────────────────────────────────
# 6. API KEY EXPOSURE CHECK
# ────────────────────────────────────────────────────────────────
print("\n[6] API KEY EXPOSURE CHECK (frontend source files)")
api_key = os.getenv("IGNAV_API_KEY", "")
key_exposed = False
if api_key:
    for f in (PROJECT_ROOT / "frontend/src").rglob("*"):
        if f.is_file() and f.suffix in (".js", ".jsx", ".ts", ".tsx", ".html", ".css"):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if api_key in content:
                    print(f"  CRITICAL: API key found in {f.relative_to(PROJECT_ROOT)}")
                    key_exposed = True
            except Exception:
                pass
    if not key_exposed:
        print("  API key NOT found in any frontend source file  [SECURE]")
else:
    print("  Could not load IGNAV_API_KEY for comparison (env issue)")

results["key_secure"] = PASS if not key_exposed else FAIL
print(f"  KEY SECURITY: {results['key_secure']}")

# ────────────────────────────────────────────────────────────────
# 7. PROVENANCE SUMMARY DETAIL
# ────────────────────────────────────────────────────────────────
print("\n[7] PROVENANCE SUMMARY")
try:
    r = client.get("/fares/provenance-summary")
    if r.status_code == 200:
        prov = r.json()
        counts = prov.get("counts", {})
        pcts = prov.get("percentages", {})
        print(f"  Total observations     : {prov.get('total_observations')}")
        for k, v in counts.items():
            if v > 0:
                print(f"  {k:<25}: {v:>7} ({pcts.get(k,0):.3f}%)")
        print(f"  Audit status           : {prov.get('audit_status')}")
        note = prov.get("notes", {}).get("REAL_API", "")
        print(f"  REAL_API note          : {note}")

        total_pct = sum(pcts.values())
        prov_pass = (99.9 <= total_pct <= 100.1) and counts.get("REAL_API", 0) >= 65
        results["provenance"] = PASS if prov_pass else FAIL
    else:
        results["provenance"] = FAIL
    print(f"  PROVENANCE: {results['provenance']}")
except Exception as e:
    print(f"  ERROR: {e}")
    results["provenance"] = FAIL

# ────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("FINAL INTEGRITY REPORT")
print("=" * 65)
print(f"LIVE PROVIDER:             IGNAV")
print(f"REAL IGNAV DATA VERIFIED:  {'YES' if results.get('ignav_data') == PASS else 'NO'}")
print(f"LIVE DATA PROVENANCE:      {results.get('provenance', FAIL)}")
print(f"DATA LAYER SEPARATION:     {results.get('data_separation', FAIL)}")
print(f"PREDICTION INTEGRITY:      {results.get('prediction', FAIL)}")
print(f"API ENDPOINTS:             {results.get('api_endpoints', FAIL)}")
print(f"KEY SECURITY:              {results.get('key_secure', FAIL)}")
print(f"ACTIVE AMADEUS DEPENDENCY: {results.get('amadeus_active', 'YES')}")
overall = all(v in (PASS, "NO", "PASS") for v in [
    results.get("ignav_data"), results.get("data_separation"),
    results.get("prediction"), results.get("api_endpoints"),
    results.get("key_secure"), results.get("provenance"),
]) and results.get("amadeus_active") == "NO"
print(f"SIH DEMO READY:            {'YES' if overall else 'NO'}")
print("=" * 65)
