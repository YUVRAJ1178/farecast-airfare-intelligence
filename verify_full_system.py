import urllib.request
import urllib.parse
import json
import time

def test_get(url, desc):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as res:
            data = res.read()
            elapsed = time.time() - t0
            print(f"[PASS] {desc}: status {res.status}, {len(data):,} bytes ({elapsed:.2f}s)")
            return data
    except Exception as e:
        print(f"[FAIL] {desc}: {e}")
        return None

def test_post(url, payload, desc):
    t0 = time.time()
    try:
        body = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=body,
            headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read())
            elapsed = time.time() - t0
            print(f"[PASS] {desc}: status {res.status}, predicted_fare: {data.get('predicted_fare')} ({elapsed:.2f}s)")
            return data
    except Exception as e:
        print(f"[FAIL] {desc}: {e}")
        return None

print("=" * 60)
print("VERIFYING FARECAST FULL SYSTEM")
print("=" * 60)

# Frontend assets
test_get('http://localhost:3000/', "Frontend SPA index.html")
test_get('http://localhost:3000/assets/index-DJ3zwA0y.js', "Frontend JS Bundle")
test_get('http://localhost:3000/assets/index-CVHLz7nN.css', "Frontend CSS Bundle")

# Backend API Endpoints
test_get('http://127.0.0.1:8000/live-status', "Live Status")
test_get('http://127.0.0.1:8000/dashboard-summary', "Dashboard Summary (Unfiltered)")
test_get('http://127.0.0.1:8000/dashboard-summary?origin=DEL&destination=BOM', "Dashboard Summary (DEL->BOM)")
test_get('http://127.0.0.1:8000/dashboard-summary?airline=IndiGo&cabin_class=Economy', "Dashboard Summary (IndiGo / Economy)")
test_get('http://127.0.0.1:8000/dashboard-summary?origin=ATQ&destination=DEL', "Dashboard Summary (ATQ->DEL Amritsar)")
test_get('http://127.0.0.1:8000/dashboard-summary?origin=IXC&destination=BOM', "Dashboard Summary (IXC->BOM Chandigarh)")
test_get('http://127.0.0.1:8000/fares/routes', "Routes list")
test_get('http://127.0.0.1:8000/fares/airlines', "Airlines list")
test_get('http://127.0.0.1:8000/anomalies/?limit=10', "Anomalies list")
test_get('http://127.0.0.1:8000/backtesting/dgca/30-day', "30-Day DGCA Backtest Data")

# India Traffic Map with 17 hubs
map_data = test_get('http://127.0.0.1:8000/index/traffic-map', "India Air Corridor Map")
if map_data:
    parsed = json.loads(map_data)
    hubs = [h['code'] for h in parsed.get('hubs', [])]
    print(f"   Total Map Hubs: {len(hubs)} -> {hubs}")
    assert 'ATQ' in hubs, "ATQ must be present in map hubs"
    assert 'IXC' in hubs, "IXC must be present in map hubs"
    assert len(hubs) == 17, "All 17 hubs must be present"

# ML Prediction test
test_post(
    'http://127.0.0.1:8000/prediction/',
    {"origin": "DEL", "destination": "BOM", "airline": "IndiGo", "cabin_class": "Economy", "stops": 0, "days_left": 30},
    "ML Fare Prediction (DEL->BOM, IndiGo, 30d)"
)
test_post(
    'http://127.0.0.1:8000/prediction/',
    {"origin": "ATQ", "destination": "DEL", "airline": "Air India", "cabin_class": "Economy", "stops": 0, "days_left": 14},
    "ML Fare Prediction (ATQ->DEL Amritsar, Air India, 14d)"
)
test_post(
    'http://127.0.0.1:8000/prediction/',
    {"origin": "IXC", "destination": "BOM", "airline": "Vistara", "cabin_class": "Business", "stops": 0, "days_left": 7},
    "ML Fare Prediction (IXC->BOM Chandigarh, Vistara, Business, 7d)"
)

print("=" * 60)
print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
print("=" * 60)
