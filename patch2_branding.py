"""
patch2_branding.py — Patch the bundle to ensure:
1. 'Powered by AI' is removed from sidebar
2. FareCast branding in sidebar (FARECAST name)
3. Hero section tagline updated
4. Right panel removed from App shell
"""

BUNDLE_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'

with open(BUNDLE_PATH, 'r', encoding='utf-8') as f:
    bundle = f.read()

print(f"Bundle size: {len(bundle):,}")

# Check for Powered by AI
pos_pai = bundle.find('Powered by AI')
print(f"'Powered by AI' at pos: {pos_pai}")
if pos_pai != -1:
    print(f"Context: {repr(bundle[pos_pai-120:pos_pai+80])}")

# Check for right-panel
pos_rp = bundle.find('right-panel')
print(f"'right-panel' at pos: {pos_rp}")

# Check for FARECAST
pos_fc = bundle.find('FARECAST')
print(f"'FARECAST' at pos: {pos_fc}")

# Check for hero title FORECAST
pos_ft = bundle.find('FARECAST')
print(f"FARECAST count: {bundle.count('FARECAST')}")

# What text is in the sidebar currently?
pos_sidebar_brand = bundle.find('sidebar-name')
print(f"sidebar-name pos: {pos_sidebar_brand}")
if pos_sidebar_brand != -1:
    print(f"sidebar brand ctx: {repr(bundle[pos_sidebar_brand:pos_sidebar_brand+150])}")

# Find Apply Filters
pos_apply = bundle.find('Apply Filters')
print(f"'Apply Filters' pos: {pos_apply}")

# YY region fresh look
yy_start = bundle.find('function YY()')
root_idx = bundle.find('G3.createRoot(document.getElementById("root"))', yy_start)
yy_region = bundle[yy_start:root_idx]

# Check if right panel is still there
pos_right = yy_region.find('right-panel')
print(f"right-panel in YY: {'YES' if pos_right != -1 else 'NO'}")

print("Done.")
