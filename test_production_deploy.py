import urllib.request, json

BASE_URL = "https://ozone-functionality-displays-passion.trycloudflare.com"

print("=" * 65)
print("TESTING PRODUCTION DEPLOYMENT")
print("Target:", BASE_URL)
print("=" * 65)

tests = {}

# 1. Health
try:
    with urllib.request.urlopen(f"{BASE_URL}/health", timeout=15) as r:
        data = json.loads(r.read().decode())
        print(f"1. Health: HTTP {r.status} -> {data.get('status')}, ignav={data.get('ignav')}")
        tests["health"] = (r.status == 200 and data.get("status") == "ok")
except Exception as e:
    print(f"1. Health ERROR: {e}")
    tests["health"] = False

# 2. Frontend /app/
try:
    with urllib.request.urlopen(f"{BASE_URL}/app/", timeout=15) as r:
        html = r.read().decode('utf-8', errors='ignore')
        has_root = '<div id="root">' in html
        has_js = '/assets/index-DJ3zwA0y.js' in html
        print(f"2. Frontend /app/: HTTP {r.status}, has_root={has_root}, has_js={has_js}")
        tests["frontend"] = (r.status == 200 and has_root and has_js)
except Exception as e:
    print(f"2. Frontend ERROR: {e}")
    tests["frontend"] = False

# 3. Static JS asset
try:
    with urllib.request.urlopen(f"{BASE_URL}/assets/index-DJ3zwA0y.js", timeout=15) as r:
        content_len = len(r.read())
        print(f"3. JS Asset: HTTP {r.status}, length={content_len}")
        tests["js_asset"] = (r.status == 200 and content_len > 4000000)
except Exception as e:
    print(f"3. JS Asset ERROR: {e}")
    tests["js_asset"] = False

# 4. Docs
try:
    with urllib.request.urlopen(f"{BASE_URL}/docs", timeout=15) as r:
        print(f"4. Swagger Docs: HTTP {r.status}")
        tests["docs"] = (r.status == 200)
except Exception as e:
    print(f"4. Docs ERROR: {e}")
    tests["docs"] = False

# 5. Prediction
try:
    payload = json.dumps({
        "airline": "IndiGo",
        "origin": "DEL",
        "destination": "BOM",
        "cabin_class": "Economy",
        "stops": 0,
        "days_left": 14,
        "duration_minutes": 130,
        "departure_hour": 10
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/prediction/",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode())
        print(f"5. Prediction: HTTP {r.status} -> INR {data.get('predicted_fare')} ({data.get('recommendation')})")
        tests["prediction"] = (r.status == 200 and data.get("predicted_fare", 0) > 0)
except Exception as e:
    print(f"5. Prediction ERROR: {e}")
    tests["prediction"] = False

# 6. Live Ignav search
try:
    payload = json.dumps({
        "origin": "DEL",
        "destination": "BOM",
        "departure_date": "2026-10-08",
        "adults": 1,
        "cabin_class": "Economy",
        "market": "IN"
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/live/ignav/search",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
        count = data.get("results_count", 0)
        cheapest = data.get("fares", [{}])[0].get("fare")
        print(f"6. Live Ignav Search: HTTP {r.status} -> {count} offers, cheapest=INR {cheapest}")
        tests["ignav"] = (r.status == 200 and count > 0)
except Exception as e:
    print(f"6. Live Ignav Search ERROR: {e}")
    tests["ignav"] = False

# 7. Provenance summary
try:
    with urllib.request.urlopen(f"{BASE_URL}/fares/provenance-summary", timeout=15) as r:
        data = json.loads(r.read().decode())
        total = data.get("total_observations")
        counts = data.get("counts", {})
        status = data.get("audit_status")
        print(f"7. Provenance Summary: HTTP {r.status} -> Total={total}, REAL_API={counts.get('REAL_API')}, status={status}")
        tests["provenance"] = (r.status == 200 and status == "VERIFIED_HONEST")
except Exception as e:
    print(f"7. Provenance ERROR: {e}")
    tests["provenance"] = False

# 8. DGCA monthly benchmark
try:
    with urllib.request.urlopen(f"{BASE_URL}/backtesting/dgca/monthly-benchmark", timeout=15) as r:
        data = json.loads(r.read().decode())
        print(f"8. DGCA Benchmark: HTTP {r.status} -> {len(data)} sectors")
        tests["dgca_benchmark"] = (r.status == 200 and len(data) > 0)
except Exception as e:
    print(f"8. DGCA Benchmark ERROR: {e}")
    tests["dgca_benchmark"] = False

# 9. 30-day backtesting
try:
    with urllib.request.urlopen(f"{BASE_URL}/backtesting/dgca/30-day", timeout=15) as r:
        data = json.loads(r.read().decode())
        mape = data.get("summary", {}).get("mape")
        print(f"9. 30-Day Backtesting: HTTP {r.status} -> MAPE={mape}%")
        tests["backtesting_30d"] = (r.status == 200 and mape is not None)
except Exception as e:
    print(f"9. 30-Day Backtesting ERROR: {e}")
    tests["backtesting_30d"] = False

# 10. Traffic map
try:
    with urllib.request.urlopen(f"{BASE_URL}/index/traffic-map", timeout=15) as r:
        data = json.loads(r.read().decode())
        hubs = len(data.get("hubs", []))
        corridors = len(data.get("corridors", []))
        print(f"10. Traffic Map: HTTP {r.status} -> {hubs} hubs, {corridors} corridors")
        tests["traffic_map"] = (r.status == 200 and hubs > 0 and corridors > 0)
except Exception as e:
    print(f"10. Traffic Map ERROR: {e}")
    tests["traffic_map"] = False

print("=" * 65)
print("PRODUCTION VERIFICATION SUMMARY")
print("=" * 65)
all_pass = all(tests.values())
for k, v in tests.items():
    print(f"  {k:<20}: {'PASS' if v else 'FAIL'}")
print("=" * 65)
print(f"OVERALL PRODUCTION STATUS: {'SUCCESS' if all_pass else 'FAIL'}")
print("=" * 65)
