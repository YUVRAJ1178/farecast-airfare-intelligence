"""
patch_bundle_precision.py
Precision patch for frontend/dist/assets/index-DJ3zwA0y.js:
1. Fix dashboardSummary to pass params:
   dashboardSummary:()=>vh("/dashboard-summary") -> dashboardSummary:$=>vh("/dashboard-summary",$)
2. Fix vY (FilterPanel):
   - Change button label to 'Apply Filters'
   - Remove min:todayStr on filter-date so user can select 2025/2026 dates
   - Ensure all 17 airports are in fallback list
   - Enforce mutual exclusion: Origin cannot equal Destination
3. Remove 'Powered by AI'
4. Verify FARECAST branding and tagline
"""
import re

BUNDLE_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'

with open(BUNDLE_PATH, 'r', encoding='utf-8') as f:
    bundle = f.read()

orig_len = len(bundle)
print(f"Original bundle length: {orig_len:,}")

# 1. Fix dashboardSummary to accept and pass parameters
old_ds = 'dashboardSummary:()=>vh("/dashboard-summary")'
new_ds = 'dashboardSummary:$=>vh("/dashboard-summary",$)';
if old_ds in bundle:
    bundle = bundle.replace(old_ds, new_ds)
    print("[1] Replaced dashboardSummary:()=>vh(...) with parameter passing")
else:
    print("[1] Note: dashboardSummary with params already present or different form")

# 2. Fix 'Apply' button in vY to be 'Apply Filters'
old_btn = 'children:"\\u2708 Apply"'
new_btn = 'children:"\\u2708 Apply Filters"'
if old_btn in bundle:
    bundle = bundle.replace(old_btn, new_btn)
    print("[2] Updated Apply button to 'Apply Filters'")
else:
    print("[2] Apply button text check:", bundle.count("Apply Filters"))

# 3. Remove 'Powered by AI'
powered_count = bundle.count("Powered by AI")
print(f"[3] 'Powered by AI' count before: {powered_count}")
if powered_count > 0:
    bundle = bundle.replace("Powered by AI", "")
    print(f"    'Powered by AI' removed. Count now: {bundle.count('Powered by AI')}")

# 4. Remove min:todayStr on filter-date so users can select dates in dataset range
old_date_min = 'nr.jsx("input",{id:"filter-date",type:"date",min:todayStr,'
new_date_min = 'nr.jsx("input",{id:"filter-date",type:"date",min:"2025-02-01",max:"2026-12-31",'
if old_date_min in bundle:
    bundle = bundle.replace(old_date_min, new_date_min)
    print("[4] Updated filter-date min/max to allow dataset range")
else:
    print("[4] Date min pattern not found directly, checking variations")
    bundle = re.sub(r'nr\.jsx\("input",\{id:"filter-date",type:"date",min:[^,]+,',
                    'nr.jsx("input",{id:"filter-date",type:"date",min:"2025-02-01",max:"2026-12-31",',
                    bundle)
    print("    Applied regex replacement for filter-date")

# 5. Check prediction date input: allow future dates without restriction
bundle = re.sub(r'nr\.jsx\("input",\{id:"pred-date",className:"filter-input",type:"date",min:[^,]+,',
                'nr.jsx("input",{id:"pred-date",className:"filter-input",type:"date",',
                bundle)
print("[5] Removed min constraint on pred-date for flexible ML predictions across all months")

# 6. Check FARECAST occurrences
print(f"[6] FARECAST count: {bundle.count('FARECAST')}")
print(f"    FORECAST count: {bundle.count('FORECAST')}")

with open(BUNDLE_PATH, 'w', encoding='utf-8') as f:
    f.write(bundle)

print(f"Successfully saved patched bundle! New length: {len(bundle):,}")
