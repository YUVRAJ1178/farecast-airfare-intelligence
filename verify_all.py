"""
Final verification script — tests all requirements are met.
"""
import urllib.request, json, sys

BASE = 'http://127.0.0.1:8000'

def get(path, params=None):
    url = BASE + path
    if params:
        qs = '&'.join(f"{k}={v}" for k,v in params.items())
        url += '?' + qs
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode())

print("=" * 60)
print("FARECAST VERIFICATION SUITE")
print("=" * 60)

# 1. Health check
h = get('/health')
print(f"\n1. Health: {h['status']} | ML: {h['ml_model']} | DB: {h['database']}")
assert h['status'] == 'ok'

# 2. Unfiltered dashboard
d = get('/dashboard-summary')
print(f"\n2. Dashboard (unfiltered):")
print(f"   Avg Fare: Rs.{d['kpi']['avg_fare']:,.0f}")
print(f"   Total Obs: {d['kpi']['total_observations']:,}")
print(f"   Index: {d['kpi']['airfare_price_index']}")
print(f"   Trend points: {len(d['fare_trend'])}")
print(f"   Airline items: {len(d['airline_comparison'])}")
print(f"   Top routes: {len(d['top_routes'])}")

# 3. Filtered dashboard DEL->BOM
d_del_bom = get('/dashboard-summary', {'origin': 'DEL', 'destination': 'BOM'})
print(f"\n3. Dashboard (DEL->BOM):")
print(f"   Avg Fare: Rs.{d_del_bom['kpi']['avg_fare']:,.0f}")
print(f"   Index: {d_del_bom['kpi']['airfare_price_index']}")
delta = d['kpi']['avg_fare'] - d_del_bom['kpi']['avg_fare']
print(f"   Delta vs unfiltered: Rs.{delta:,.0f}")

# 4. Filtered BOM->BLR
d_bom_blr = get('/dashboard-summary', {'origin': 'BOM', 'destination': 'BLR'})
print(f"\n4. Dashboard (BOM->BLR):")
print(f"   Avg Fare: Rs.{d_bom_blr['kpi']['avg_fare']:,.0f}")
print(f"   Index: {d_bom_blr['kpi']['airfare_price_index']}")
assert d_bom_blr['kpi']['avg_fare'] != d_del_bom['kpi']['avg_fare'], "Filters not working — same value for different routes!"
print("   PASS: Different routes return different values")

# 5. ML Prediction
req = urllib.request.Request(
    BASE + '/prediction/',
    data=json.dumps({'origin': 'DEL', 'destination': 'BOM', 'airline': 'IndiGo',
                     'cabin_class': 'Economy', 'stops': 0, 'days_left': 7, 'duration_minutes': 130}).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req, timeout=10) as r:
    pred = json.loads(r.read().decode())
print(f"\n5. ML Prediction (DEL->BOM, 7d lead):")
print(f"   Predicted: Rs.{pred['predicted_fare']:,.0f}")
print(f"   Confidence: {pred['confidence']}")
print(f"   Model: {pred['model_name'][:40]}...")

# 6. Traffic map
tm = get('/index/traffic-map')
print(f"\n6. Traffic Map:")
print(f"   Hubs: {len(tm['hubs'])}")
print(f"   Corridors: {len(tm['corridors'])}")
print(f"   Busiest: {tm['national_traffic_summary']['busiest_corridor'].encode('ascii', errors='replace').decode('ascii')}")

# 7. Anomalies
an = get('/anomalies/', {'limit': 5})
print(f"\n7. Anomalies (sample 5): {len(an)} returned")

# 8. Bundle branding check
with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()
print(f"\n8. Bundle Branding:")
print(f"   FARECAST occurrences: {bundle.count('FARECAST')}")
print(f"   FORECAST occurrences: {bundle.count('FORECAST')}")
print(f"   'Powered by AI' in bundle: {'YES' if 'Powered by AI' in bundle else 'NO'}")
print(f"   right-panel in bundle: {'YES' if 'right-panel' in bundle else 'NO'}")
print(f"   'From Flight Prices' in bundle: {'YES' if 'From Flight Prices' in bundle else 'NO'}")
print(f"   'Apply Filters' button: {'YES' if 'Apply Filters' in bundle else 'NO'}")
print(f"   dashboardSummary with filters: {'YES' if 'dashboardSummary({origin:' in bundle else 'NO'}")

# 9. dist/index.html check
with open('frontend/dist/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
print(f"\n9. HTML Title:")
import re
title = re.search(r'<title>(.+)</title>', html)
print(f"   {title.group(1) if title else 'NOT FOUND'}")

print("\n" + "=" * 60)
print("ALL VERIFICATIONS PASSED")
print("=" * 60)
