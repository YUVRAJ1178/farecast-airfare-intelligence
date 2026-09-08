"""
Regenerate anomalies with balanced severity diversity (LOW, MEDIUM, HIGH, CRITICAL)
and clear explanations matching SIH 26056 Requirement 8.
"""
import random
from collections import defaultdict
from backend.app.database import get_db
from backend.app.services.anomaly_service import detect_iqr_anomalies
from backend.app.models import Anomaly

db = next(get_db())

print("Detecting IQR anomalies across all routes...")
all_anomalies = detect_iqr_anomalies(db, lookback_days=180, iqr_multiplier=1.5)
print(f"Total raw anomalies detected: {len(all_anomalies)}")

by_sev = defaultdict(list)
for a in all_anomalies:
    by_sev[a["severity"]].append(a)

for sev, items in by_sev.items():
    print(f"  {sev}: {len(items)}")

# Sample a balanced set of ~200 anomalies: 50 LOW, 50 MEDIUM, 50 HIGH, 50 CRITICAL
selected = []
random.seed(42)

for sev in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
    pool = by_sev.get(sev, [])
    sample_size = min(50, len(pool))
    if pool:
        sampled = random.sample(pool, sample_size)
        selected.extend(sampled)

print(f"Selected {len(selected)} balanced anomalies.")

# Clear existing table and insert balanced set
db.query(Anomaly).delete()
db.commit()

for a in selected:
    record = Anomaly(**{k: v for k, v in a.items() if hasattr(Anomaly, k)})
    db.add(record)

db.commit()
print("Saved balanced anomaly set to database.")

# Verify counts in DB
from sqlalchemy import func
counts = db.query(Anomaly.severity, func.count(Anomaly.id)).group_by(Anomaly.severity).all()
print("New database distribution:", counts)
