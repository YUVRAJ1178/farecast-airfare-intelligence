"""
clean_restore_final.py

Analysis shows:
- vY[0] at 156196: new patched vY (159360 chars)  ← GOOD (has Apply Filters)
- vY[1] at 315556: duplicate starts here (size 4,475,644 until vY[2])
- vY[2] at 4791200: another new vY copy (159360 chars)
- vY[3] at 4950560: another duplicate

After last vY at 4950560, the rest contains: middle functions + zY + FY/BY/HY + new YY + root

FY at 9270527, BY at 9271259, HY at 9305217, new YY at 9331308 (from earlier analysis)

So the bundle is structured as:
[0:156196]          = preamble (original, good)
[156196:315556]     = NEW vY (good, patched version with Apply Filters)
[315556:4791200]    = DUPLICATE block #1 (4.47MB of garbage including more vY, functions)
[4791200:4950560]   = another NEW vY copy (duplicate, bad)
[4950560:9270527]   = more middle functions (TY, SY, CY, PY, DY, zY, etc.)
[9270527:9305217+?] = FY, BY, HY (first occurrences only!)
[9331308:9346866]   = new YY + root render (good!)

Wait but that means: EVERYTHING from 315556 to 4791200 is a corrupted duplicate block.
And from 4791200 to 4950560 is another new vY copy.
And from 4950560 onwards is the REST of the original bundle's functions.

Let me verify: what's at position 4791200?
What's at position 4950560?

The CLEAN bundle should be:
preamble[0:156196] + new_vY[156196:315556] + middle_funcs[4950560:9331308] + new_YY[9331308:end]

Let me verify what's in [4950560:9270527] vs what should be there.
"""
import re

BAK_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js.bak'
OUT_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'

with open(BAK_PATH, 'r', encoding='utf-8') as f:
    bak = f.read()
print(f"Backup size: {len(bak):,}")

# Check what's at 4950560
pos = 4950560
print(f"\nAt 4950560: {repr(bak[pos:pos+100])}")

# Check what's at 4791200
pos = 4791200
print(f"At 4791200: {repr(bak[pos:pos+100])}")

# Check what comes right after the 4th vY (4950560 + 159360)
pos = 4950560 + 159360
print(f"After 4th vY at {pos}: {repr(bak[pos:pos+100])}")

# Find all functions in [4950560:9270527]
middle = bak[4950560:9270527]
funcs = re.findall(r'function ([A-Z][A-Za-z0-9]*)\(', middle)
print(f"\nFunctions in [4950560:9270527]: {funcs[:30]}")

# Is zY in there?
zy_in_middle = [m.start()+4950560 for m in re.finditer(r'function zY\(', bak[4950560:9270527])]
print(f"zY positions in middle region: {zy_in_middle}")

# Check what's right before new YY (9331308)
print(f"\nBefore new YY: {repr(bak[9331248:9331308])}")

# BUILD THE CLEAN BUNDLE:
# Strategy: 
# preamble + new_vY + skip_dup_block + middle_functions + new_YY

# The "middle functions" are everything after the 4th vY up to new YY
# = bak[4950560+159360 : 9331308]
# But we need to verify this doesn't include a duplicate of vY itself

after_4th_vy = 4950560 + 159360  # = 5109920
region_after_4th_vy = bak[after_4th_vy:9331308]

vy_in_region = region_after_4th_vy.count('function vY(')
zy_in_region = region_after_4th_vy.count('function zY(')
print(f"\nIn region [5109920:9331308]:")
print(f"  Size: {len(region_after_4th_vy):,}")
print(f"  vY count: {vy_in_region}")
print(f"  zY count: {zy_in_region}")
print(f"  First 100: {repr(region_after_4th_vy[:100])}")
print(f"  Last 100: {repr(region_after_4th_vy[-100:])}")

# Build the clean bundle
preamble = bak[0:156196]
new_vy = bak[156196:315556]
middle_funcs = bak[5109920:9331308]
new_yy_and_root = bak[9331308:9346866]

clean = preamble + new_vy + middle_funcs + new_yy_and_root
print(f"\nClean bundle size: {len(clean):,}")
print(f"vY count: {clean.count('function vY(')}")
print(f"zY count: {clean.count('function zY(')}")
print(f"YY count: {clean.count('function YY()')}")
print(f"root render: {clean.count('G3.createRoot')}")
print(f"FARECAST: {clean.count('FARECAST')}")
print(f"Apply Filters: {'YES' if 'Apply Filters' in clean else 'NO'}")
print(f"right-panel: {'YES' if 'right-panel' in clean else 'NO'}")
print(f"From Flight Prices: {'YES' if 'From Flight Prices' in clean else 'NO'}")
print(f"dashboardSummary with filters: {'YES' if 'dashboardSummary({origin:' in clean else 'NO'}")

# Verify the join at preamble->new_vy->middle makes sense
print(f"\nJoin1 (end of preamble): {repr(clean[156186:156206])}")
print(f"Join2 (end of new_vy -> middle): {repr(clean[315546:315576])}")

# Check brace balance in hY (KPI cards, known function)
hy_start = clean.find('function hY(')
print(f"\nhY at: {hy_start}")
if hy_start != -1:
    print(f"hY context: {repr(clean[hy_start:hy_start+80])}")

if len(clean) > 4000000 and clean.count('function vY(') == 1 and clean.count('function YY()') == 1:
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(clean)
    print(f"\nSUCCESS: Clean bundle written to {OUT_PATH}")
else:
    print(f"\nERROR: Bundle validation failed, not writing.")
