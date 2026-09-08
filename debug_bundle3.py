"""
Critical check: find where function vY actually ends vs where zY starts.
The issue might be that vY find is finding the WRONG function if there are two.
"""
with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

import re

# Find ALL occurrences of function vY and zY
vy_positions = [m.start() for m in re.finditer(r'function vY\(', bundle)]
zy_positions = [m.start() for m in re.finditer(r'function zY\(', bundle)]
yy_positions = [m.start() for m in re.finditer(r'function YY\(', bundle)]

print("vY positions:", vy_positions)
print("zY positions:", zy_positions)
print("YY positions:", yy_positions)

# Show context around each vY
for pos in vy_positions:
    print(f"\nvY at {pos}:")
    print(repr(bundle[pos:pos+120]))

# Check if the old vY content still exists (from before patching)
old_vY_marker = 'children:"Reset Filters"'
old_count = bundle.count(old_vY_marker)
print(f"\nOld vY 'Reset Filters' count: {old_count}")

# Check new vY content
new_vY_marker = 'Apply Filters'
new_count = bundle.count(new_vY_marker)
print(f"New 'Apply Filters' count: {new_count}")

# Look at what's around position ~156196 - original vY
orig_vy = bundle[156196:156196+300]
print(f"\nOriginal vY position context:")
print(repr(orig_vy))
