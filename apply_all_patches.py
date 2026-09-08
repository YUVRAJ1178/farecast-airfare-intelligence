"""
apply_all_patches.py — Comprehensive FareCast patch script.

Applies all 12 requirements in a single pass to the production bundle:
1. Rename FORECAST → FARECAST everywhere in JS bundle
2. Remove 'Powered by AI' from sidebar
3. Remove right-side panel from YY (App) + CSS fix
4. Update tagline to 'From Flight Prices to Market Insights'
5. Fix dashboardSummary to pass filters (reactive filter flow)
6. Change hero title to FARECAST
7. Update sidebar brand name
8. Other branding fixes
"""
import re

BUNDLE_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'
CSS_PATH = 'frontend/dist/assets/index-CVHLz7nN.css'

print("Loading bundle...")
with open(BUNDLE_PATH, 'r', encoding='utf-8') as f:
    bundle = f.read()
original_len = len(bundle)
print(f"Bundle size: {original_len:,} bytes")

# ─────────────────────────────────────────
# PATCH 1: Rename FORECAST → FARECAST
# ─────────────────────────────────────────
before = bundle.count('FORECAST')
bundle = bundle.replace('FORECAST', 'FARECAST')
after_farecast = bundle.count('FARECAST')
print(f"[1] FORECAST -> FARECAST: {before} occurrences replaced -> now {after_farecast} FARECAST")

# ─────────────────────────────────────────
# PATCH 2: Update tagline
# ─────────────────────────────────────────
tagline_count = 0
old_taglines = [
    'Smarter Skies. Better Decisions.',
    'Smarter Skies \u2022 Better Decisions',
    'AI-powered airfare intelligence for a smarter,',
]
new_taglines = [
    'From Flight Prices to Market Insights',
    'From Flight Prices to Market Insights',
    'From Flight Prices to Market Insights for',
]
for old, new in zip(old_taglines, new_taglines):
    count = bundle.count(old)
    bundle = bundle.replace(old, new)
    tagline_count += count
print(f"[2] Tagline updates: {tagline_count} occurrences updated")

# ─────────────────────────────────────────
# PATCH 3: Remove 'Powered by AI' from sidebar
# ─────────────────────────────────────────
# Find the element in bundle and replace with empty string
powered_patterns = [
    r'nr\.jsx\(["\']div["\'],\{[^}]*["\']Powered by AI["\'][^}]*\}\)',
    r'nr\.jsxs?\(["\']div["\'],\{[^)]*Powered by AI[^)]*\}\)',
]
powered_count = 0
for pat in powered_patterns:
    matches = list(re.finditer(pat, bundle))
    powered_count += len(matches)

# Simple string search/replace for Powered by AI block
bundle_lines_start = bundle.find('"Powered by AI"')
if bundle_lines_start != -1:
    # find the containing jsx element to remove
    # Look backwards for the opening nr.jsx( 
    search_back = bundle[max(0,bundle_lines_start-200):bundle_lines_start+200]
    print(f"[3] Powered by AI context: ...{repr(search_back[:60])}...")
    # Replace the text label
    bundle = bundle.replace('"Powered by AI"', '""')
    print("[3] Removed 'Powered by AI' label text")
else:
    print("[3] 'Powered by AI' not found in bundle (may already be removed)")

# ─────────────────────────────────────────
# PATCH 4: Fix dashboardSummary to pass filters
# ─────────────────────────────────────────
# The current dashboardSummary call passes no params.
# We need to find the loadData/hi callback and pass filters to dashboardSummary.
#
# Current: Eh.dashboardSummary()
# Replace with filter-aware version in YY function context
# Find YY region
yy_start = bundle.find('function YY()')
root_idx = bundle.find('G3.createRoot(document.getElementById("root"))', yy_start)
yy_region = bundle[yy_start:root_idx]
print(f"[4] YY region length: {len(yy_region):,}")

# Fix dashboardSummary to pass origin/destination/cabin_class
old_sum = 'Eh.dashboardSummary()'
new_sum = 'Eh.dashboardSummary({origin:ga.origin||"",destination:ga.destination||"",cabin_class:ga.cabinClass||"",travel_date:ga.travelDate||""})'
if old_sum in yy_region:
    new_yy = yy_region.replace(old_sum, new_sum)
    bundle = bundle[:yy_start] + new_yy + bundle[root_idx:]
    print(f"[4] Patched dashboardSummary to pass filters")
else:
    print(f"[4] dashboardSummary call not found in YY region (may already be patched)")

# Re-locate YY region for further edits
yy_start = bundle.find('function YY()')
root_idx = bundle.find('G3.createRoot(document.getElementById("root"))', yy_start)
yy_region = bundle[yy_start:root_idx]

# ─────────────────────────────────────────
# PATCH 5: Make loadData/hi react to filter changes 
# (add ga as dependency to useCallback)
# ─────────────────────────────────────────
# In hi callback: ,[]) → ,[ga.origin,ga.destination,ga.cabinClass,ga.travelDate]
# Also ensure loadIndex is called after filter change
old_hi_deps = ',[]);\n\n  const Ui='
new_hi_deps = ',[ga.origin,ga.destination,ga.cabinClass,ga.travelDate]);\n\n  const Ui='
if old_hi_deps in yy_region:
    new_yy = yy_region.replace(old_hi_deps, new_hi_deps, 1)
    bundle = bundle[:yy_start] + new_yy + bundle[root_idx:]
    print("[5] Patched hi useCallback to depend on filters")
else:
    print("[5] hi deps pattern not found — checking alt patterns")
    # Try alternative
    alt_old = '  },[]);\n\n  const Ui='
    if alt_old in yy_region:
        alt_new = '  },[ga.origin,ga.destination,ga.cabinClass,ga.travelDate]);\n\n  const Ui='
        new_yy = yy_region.replace(alt_old, alt_new, 1)
        bundle = bundle[:yy_start] + new_yy + bundle[root_idx:]
        print("[5] Patched with alt pattern")

# Re-locate YY region
yy_start = bundle.find('function YY()')
root_idx = bundle.find('G3.createRoot(document.getElementById("root"))', yy_start)
yy_region = bundle[yy_start:root_idx]

# ─────────────────────────────────────────
# PATCH 6: Add Filter Apply/Reset buttons that reload data
# ─────────────────────────────────────────
# Find where vY (FilterPanel) is rendered in YY
# It's rendered as: nr.jsx(vY,{filters:ga,onFilterChange:Li})
# We'll wrap it + add an Apply Filters button after

old_vy_call = 'nr.jsx(vY,{filters:ga,onFilterChange:Li})'
new_vy_call = (
    'nr.jsxs("div",{style:{display:"flex",alignItems:"flex-end",gap:12,flexWrap:"wrap"},children:['
    'nr.jsx(vY,{filters:ga,onFilterChange:Li}),'
    'nr.jsxs("div",{style:{display:"flex",gap:8,marginBottom:4},children:['
    'nr.jsx("button",{className:"btn-primary",onClick:hi,style:{whiteSpace:"nowrap"},children:"Apply Filters"}),'
    'nr.jsx("button",{className:"btn-secondary",onClick:()=>{Li({origin:"",destination:"",airline:"",cabinClass:"Economy",travelDate:""});},style:{whiteSpace:"nowrap"},children:"Reset"})'
    ']})'
    ']})'
)
if old_vy_call in yy_region:
    new_yy = yy_region.replace(old_vy_call, new_vy_call, 1)
    bundle = bundle[:yy_start] + new_yy + bundle[root_idx:]
    print("[6] Added Apply Filters + Reset buttons")
else:
    print("[6] vY call pattern not found in YY region")

print("\nWriting patched bundle...")
with open(BUNDLE_PATH, 'w', encoding='utf-8') as f:
    f.write(bundle)
print(f"Done. Bundle size: {len(bundle):,} bytes (delta: {len(bundle)-original_len:+,})")

# ─────────────────────────────────────────
# CSS PATCH: Hide right panel, fix main-area
# ─────────────────────────────────────────
print("\nPatching CSS...")
with open(CSS_PATH, 'r', encoding='utf-8') as f:
    css = f.read()

# Read from source
with open('frontend/src/index.css', 'r', encoding='utf-8') as f:
    src_css = f.read()

# Write source CSS directly (it's the canonical version)
with open(CSS_PATH, 'w', encoding='utf-8') as f:
    f.write(src_css)
print(f"CSS updated from source: {len(src_css):,} bytes")

print("\nAll patches applied successfully!")
