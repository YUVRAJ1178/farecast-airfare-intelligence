"""
Check what comes after YY to ensure root render is intact.
Also check vY and zY for correct ending syntax.
"""
with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

yy_start = bundle.find('function YY()')
root_idx = bundle.find('G3.createRoot(document.getElementById("root"))', yy_start)
print("After YY (150 chars):", repr(bundle[root_idx:root_idx+150]))

# Check vY properly ends
vy_start = bundle.find('function vY(')
# Find next top-level function after vY
vy_next = bundle.find('\nfunction ', vy_start+10)
print(f"\nvY region [{vy_start}:{vy_next}], size={vy_next-vy_start}")
vy_region = bundle[vy_start:vy_next]
print("vY last 200:", repr(vy_region[-200:]))

# Check zY properly ends
zy_start = bundle.find('function zY(')
zy_next = bundle.find('\nfunction ', zy_start+10)
print(f"\nzY region [{zy_start}:{zy_next}], size={zy_next-zy_start}")
zy_region = bundle[zy_start:zy_next]
print("zY last 200:", repr(zy_region[-200:]))

# Check if console.error or throw is accessible
# The error would show in browser console - simulate by looking for obvious JS syntax issues

# Look for the specific area where Apply Filters was inserted
apply_pos = bundle.find('Apply Filters')
print(f"\nApply Filters at: {apply_pos}")
print("Apply Filters context:", repr(bundle[apply_pos-100:apply_pos+200]))
