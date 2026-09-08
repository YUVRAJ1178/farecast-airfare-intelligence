"""
final_restore.py

Take the backup (.bak) and examine it fresh to understand the true structure,
then produce a clean, working bundle.
"""
import re, hashlib

BAK_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js.bak'
OUT_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'

print("Loading backup bundle...")
with open(BAK_PATH, 'r', encoding='utf-8') as f:
    bak = f.read()
print(f"Backup size: {len(bak):,} bytes")

ROOT_RENDER = 'G3.createRoot(document.getElementById("root"))'
YY_MARKER = 'function YY()'

# Key positions in backup
vy_positions = [m.start() for m in re.finditer(r'function vY\(', bak)]
zy_positions = [m.start() for m in re.finditer(r'function zY\(', bak)]
yy_positions = [m.start() for m in re.finditer(re.escape(YY_MARKER), bak)]
root_positions = [m.start() for m in re.finditer(re.escape(ROOT_RENDER), bak)]

print(f"vY positions: {vy_positions}")
print(f"zY positions: {zy_positions}")
print(f"YY positions: {yy_positions}")
print(f"Root render positions: {root_positions}")

# In the backup (the 9.34MB file), there should be:
# - Last YY at 9,331,308 (from patch_frontend.py) → this is the good new YY
# - Last root render at 9,346,764 → good

# The GOOD portion we want is the new YY + its root render
new_yy_start = yy_positions[-1]
last_root = root_positions[-1]
root_end = last_root + len(ROOT_RENDER) + 3  # includes semicolon + newline
print(f"\nGood new YY: {new_yy_start} -> {root_end}")

# The vY we want is the FIRST one at 156196 (it's the good patched one with Apply Filters)
good_vy_start = vy_positions[0]
# The good vY ends just before the NEXT function OR we can find the next unique structure
# In the original bundle, after vY came hY (at 153398 which is BEFORE vY, so maybe it was TY etc.)
# Let's find what comes right after the good vY

# The good vY content was written by patch_frontend.py and includes "Reset Filters"
# It ends with '}'  followed by the next function
# The second vY at vy_positions[1] is where we should cut off vY content
good_vy_end = vy_positions[1]  # Cut right before second vY

print(f"\nGood vY: {good_vy_start} -> {good_vy_end}")
print(f"Good vY content snippet: {repr(bak[good_vy_start:good_vy_start+100])}")
print(f"Good vY end snippet: {repr(bak[good_vy_end-50:good_vy_end+50])}")

# What's between good_vy_end and new_yy_start?
# This contains duplicated original functions: hY, TY, SY, CY, PY, DY, zY, FY, BY, HY, old YY
# We need the ORIGINAL (non-duplicated) versions of these functions.
# The first occurrence of each should be the good one.

# Let's find zY positions:
print(f"\nzY positions: {zy_positions}")
# Take the FIRST zY (good one)
good_zy_start = zy_positions[0]
good_zy_end = zy_positions[1] if len(zy_positions) > 1 else new_yy_start
print(f"Good zY: {good_zy_start} -> {good_zy_end}")

# The structure between good_vy_end and new_yy_start includes:
# [good_vy_end : vy_positions[-1]] = duplicate functions (bad)
# We need original functions hY, TY, SY, CY, PY, DY, FY, BY, HY (not duplicated vY, zY, YY)
# These should appear once between good_vy_end and good_zy_start
# Then good zY from good_zy_start to good_zy_end  
# Then functions FY, BY, HY between good_zy_end and new_yy_start

# Find what unique functions appear between good_vy_end and good_zy_start
middle_region = bak[good_vy_end:good_zy_start]
print(f"\nMiddle region (between vY and first zY): size={len(middle_region)}")
funcs_in_middle = re.findall(r'function ([A-Z][A-Za-z0-9]*)\(', middle_region)
print(f"Functions: {funcs_in_middle}")

# The middle region contains: hY, TY, SY, CY, PY, DY
# These should all be valid (first occurrence = original).
# After zY we need: FY, BY, HY in their first occurrences

after_zy_positions = {}
for fn in ['FY', 'BY', 'HY']:
    pos = bak.find(f'function {fn}(', good_zy_end)
    after_zy_positions[fn] = pos

print(f"\nPositions of FY, BY, HY after first zY: {after_zy_positions}")

# FY/BY/HY first occurrences should be between good_zy_end and new_yy_start
# Let's find first occurrence of each
fy_positions = [m.start() for m in re.finditer(r'function FY\(', bak)]
by_positions = [m.start() for m in re.finditer(r'function BY\(', bak)]
hy_positions = [m.start() for m in re.finditer(r'function HY\(', bak)]
print(f"FY positions: {fy_positions}")
print(f"BY positions: {by_positions}")
print(f"HY positions: {hy_positions}")

# The "end" of the good region before new YY:
# Take everything up to new_yy_start that includes the first occurrence of HY
if hy_positions:
    good_hy_start = hy_positions[0]
    # HY runs until the next function (FY or BY or YY)
    next_after_hy = bak.find('\nfunction ', good_hy_start + 10)
    print(f"\nHY at {good_hy_start}, next function at {next_after_hy}: {repr(bak[next_after_hy:next_after_hy+30])}")

# BUILD THE CLEAN BUNDLE:
# Take: bak[0:good_vy_end] + bak[good_vy_end:new_yy_start] skipping duplicates + bak[new_yy_start:root_end]
# 
# Strategy: everything from 0 to new_yy_start but ONLY the first occurrence of each function
# The sections between first occurrences ARE the originals.

# SIMPLEST APPROACH that works:
# The content from 0 to vy_positions[-1] (4th vY) has 3 extra copies.
# Each copy is a complete repeat. Let's verify by checking size of each vY block.
for i in range(len(vy_positions)-1):
    block = bak[vy_positions[i]:vy_positions[i+1]]
    print(f"\nvY[{i}] to vY[{i+1}]: {vy_positions[i]} -> {vy_positions[i+1]}, size={len(block)}")
    # Does this block contain a complete app cycle (root render)?
    has_root = ROOT_RENDER in block
    has_yy = YY_MARKER in block
    print(f"  Contains root render: {has_root}, Contains YY: {has_yy}")

# Find the total size of the "UNIT" (one complete bundle copy)
# By looking at the gap between consecutive vY occurrences
gaps = [vy_positions[i+1] - vy_positions[i] for i in range(len(vy_positions)-1)]
print(f"\nGaps between vY occurrences: {gaps}")
print(f"Are gaps equal? {len(set(gaps)) == 1}")
