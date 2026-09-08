"""
debug_bundle.py — Check bundle for obvious JS errors after patching.
"""
with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

print(f"Bundle size: {len(bundle):,}")

# Check YY function structure
yy_start = bundle.find('function YY()')
root_idx = bundle.find('G3.createRoot(document.getElementById("root"))', yy_start)
print(f"YY start: {yy_start}, root render: {root_idx}")
print(f"YY region size: {root_idx - yy_start:,}")

yy = bundle[yy_start:root_idx]

# Count brace balance in YY
opens = yy.count('{')
closes = yy.count('}')
print(f"Brace balance in YY: opens={opens}, closes={closes}, diff={opens-closes}")

# Check vY
vy_start = bundle.find('function vY(')
vy_end_marker = 'children:"Reset Filters"'
vy_end = bundle.find(vy_end_marker, vy_start)
if vy_end != -1:
    vy_end += len(vy_end_marker) + 20
    vy = bundle[vy_start:vy_end]
    opens_vy = vy.count('{')
    closes_vy = vy.count('}')
    print(f"vY brace balance: opens={opens_vy}, closes={closes_vy}, diff={opens_vy-closes_vy}")
else:
    print("vY end marker not found")

# Check zY
zy_start = bundle.find('function zY(')
print(f"zY start: {zy_start}")
if zy_start != -1:
    zy_snippet = bundle[zy_start:zy_start+100]
    print(f"zY snippet: {repr(zy_snippet)}")

# Check for obvious syntax issues - double function declarations
import re
func_names = re.findall(r'function ([A-Z][A-Z0-9]*)\(', bundle)
from collections import Counter
dupes = {k: v for k, v in Counter(func_names).items() if v > 1}
print(f"Duplicate function declarations: {dupes}")

# Check for unmatched template literals or obvious problems near YY
print(f"\nYY region first 500 chars:")
print(repr(yy[:500]))
print(f"\nYY region last 300 chars:")
print(repr(yy[-300:]))
