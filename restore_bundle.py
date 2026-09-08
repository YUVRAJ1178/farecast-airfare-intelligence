"""
restore_bundle.py

The bundle was corrupted by patch_frontend.py which:
- Searched for a vY end marker that wasn't in the bundle (returned -1)
- vY_end = -1 + len(marker) = small number (~29)
- Did: bundle = bundle[:vY_start] + new_vY + bundle[29:]
  → Prepended new_vY but kept the ENTIRE original bundle from byte 29 onwards

This doubled the bundle. We need to reconstruct the original.

Strategy:
- The ORIGINAL bundle ends right before `G3.createRoot(...)` at approximately 
  the FIRST occurrence of the root render call.
- Everything from the FIRST root render call forward is the appended content.
- We extract: bundle[0:156196] (original preamble) + bundle from where new_vY ends
  to the FIRST root render.

But more reliably: find the NEW YY (from patch_frontend.py) which starts at ~9.3MB.
The bundle structure is:
  [0:156196]              = original bytes 0-156195
  [156196:156196+N]       = new vY inserted by patch_frontend.py
  [156196+N : end-M]      = original bundle from byte 29 to end  (the doubled part)
                            This contains: original vY at byte 156196-29+N, original zY, 
                            ORIGINAL YY, then appended NEW YY from patch_frontend.py

The FIRST root render in the current bundle is from the ORIGINAL (it would appear 
before the second new YY's root render at position 9,346,764).

Plan: Find the first occurrence of the root render string, take everything before it
as the "working bundle up to root render", then add just the root render call.

BUT - the original YY (pre-patch) is broken because patch_frontend.py replaced it
with new_YY at the end. Let me think differently.

The CLEANEST fix: 
1. Find where the original clean section ends (position of the first root render)
2. We know the ORIGINAL content before vY insertion was at bytes [0:156196]
3. We know the duplicate of the original bundle starts at ~156196+N where N = len(new_vY)
4. Extract: [original_preamble(0:156196)] + [SKIP new_vY] + [duplicate_original_bundle]
   BUT now we need to find N (length of inserted new_vY)

SIMPLER APPROACH:
The current bundle has root render at two positions:
  - First root render: the DUPLICATE original's root render
  - Second root render: the NEW YY's root render at 9,346,764

The second root render (9,346,764) belongs to the NEW YY function we want.
The FIRST root render belongs to the duplicate original's YY which we DON'T want.

Find the first root render position, extract from there back to find the start of
original YY (duplicate), and cut everything from there.

Then: clean_bundle = bundle[0:first_original_YY_duplicate] + new_YY_region
Where new_YY_region = bundle[9331308:9346764+len(root_render_call)]
"""
import re

BUNDLE_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'

print("Loading bundle...")
with open(BUNDLE_PATH, 'r', encoding='utf-8') as f:
    bundle = f.read()
print(f"Current size: {len(bundle):,} bytes")

ROOT_RENDER = 'G3.createRoot(document.getElementById("root"))'

# Find ALL root render positions
root_positions = [m.start() for m in re.finditer(re.escape(ROOT_RENDER), bundle)]
print(f"Root render positions: {root_positions}")

# Find ALL YY positions
yy_positions = [m.start() for m in re.finditer(r'function YY\(\)', bundle)]
print(f"YY positions: {yy_positions}")

# The LAST YY (9,331,308) and LAST root render (9,346,764) are the good patched ones
# The FIRST root render is from the duplicate original we want to cut out

# Strategy: 
# good_bundle = bundle[0 : first_occurrence_of_duplicate_YY] + bundle[last_YY : last_root_render + len_of_render]
# The "duplicate_YY" starts at yy_positions[0] if there are more than one
# OR we need to find where the duplicate original content starts

# The original preamble before vY insertion: bundle[0:156196]
# After patch, at 156196 starts the new vY (~3000 chars)
# Then starts the duplicate: original bundle from byte 29

# Find the SECOND occurrence of vY (the duplicate)
vy_positions = [m.start() for m in re.finditer(r'function vY\(', bundle)]
print(f"vY positions: {vy_positions}")

# Second vY is the start of the duplicate original chunk
# Everything from vy_positions[0] to vy_positions[1] is the new_vY content
new_vy_len = vy_positions[1] - vy_positions[0]
print(f"new_vY length in bundle: {new_vy_len}")

# The duplicate original starts at vy_positions[1] - 30 (because original started at byte 29+some_offset)
# Actually: bundle[vy_positions[1]:] should look like original bundle from ~byte 156166 (156196-30)
# We want to:
# 1. Keep bundle[0:vy_positions[0]]  = original preamble (bytes 0..156195)
# 2. Skip new_vY 
# 3. Take from vy_positions[1] back to find where duplicate preamble starts
# 4. The duplicate preamble would be bytes 29..156165 of the original (~156137 bytes)
# But since vY was at 156196 in original, the duplicate of bytes 29..156195 would be 
# 156167 bytes preceding vy_positions[1]

# So the COMPLETE duplicate original (from byte 29 to end of original) starts at:
# vy_positions[1] - (156196 - 29)  = vy_positions[1] - 156167
duplicate_start = vy_positions[1] - (156196 - 29)
print(f"Estimated duplicate start: {duplicate_start}")

# Verify: bundle[duplicate_start:duplicate_start+50]
print(f"At duplicate start: {repr(bundle[duplicate_start:duplicate_start+80])}")

# The new (patched) YY is at last yy position
new_yy_pos = yy_positions[-1]
# The last root render position
last_root_pos = root_positions[-1]
root_render_full = bundle[last_root_pos:last_root_pos+100]
# Find end of root render statement
root_end = last_root_pos + len(bundle[last_root_pos:].split(';')[0]) + 1
print(f"Root render end: {root_end}")
print(f"Root render content: {repr(bundle[last_root_pos:root_end])}")

# Construct clean bundle:
# preamble(0:vy_positions[0]) + skip new_vY + duplicate_original(vy_positions[1]:new_yy_pos) 
# + new_yy(new_yy_pos:root_end)
# BUT the duplicate_original already has the OLD YY which was also replaced.
# We want duplicate_original ONLY up to where old YY starts (the duplicate of YY).

# Find old YY in duplicate region
old_yy_in_dup = [p for p in yy_positions if p > vy_positions[1] and p < new_yy_pos]
print(f"Old YY positions in duplicate: {old_yy_in_dup}")

if old_yy_in_dup:
    # Take duplicate original up to the old YY (which was replaced by new YY appended at end)
    dup_end = old_yy_in_dup[0]
    clean_bundle = bundle[0:vy_positions[0]] + bundle[vy_positions[1]:dup_end] + bundle[new_yy_pos:root_end]
else:
    # No old YY found in duplicate - take everything up to new YY
    clean_bundle = bundle[0:vy_positions[0]] + bundle[vy_positions[1]:new_yy_pos] + bundle[new_yy_pos:root_end]

print(f"\nClean bundle size: {len(clean_bundle):,}")

# Verify key elements
print(f"vY count: {clean_bundle.count('function vY(')}")
print(f"zY count: {clean_bundle.count('function zY(')}")
print(f"YY count: {clean_bundle.count('function YY()')}")
print(f"root render count: {clean_bundle.count(ROOT_RENDER)}")
print(f"FARECAST count: {clean_bundle.count('FARECAST')}")
print(f"Apply Filters: {'YES' if 'Apply Filters' in clean_bundle else 'NO'}")
print(f"right-panel: {'YES' if 'right-panel' in clean_bundle else 'NO'}")

# Check brace balance in new YY
new_yy_region = clean_bundle[clean_bundle.find('function YY()'):]
opens = new_yy_region[:clean_bundle.find(ROOT_RENDER, clean_bundle.find('function YY()')) - clean_bundle.find('function YY()')].count('{')
closes = new_yy_region[:clean_bundle.find(ROOT_RENDER, clean_bundle.find('function YY()')) - clean_bundle.find('function YY()')].count('}')
print(f"New YY brace balance: {opens} open, {closes} close, diff={opens-closes}")

if len(clean_bundle) < 4000000:
    print("WARNING: Clean bundle seems too small, aborting save!")
else:
    backup_path = 'frontend/dist/assets/index-DJ3zwA0y.js.bak'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(bundle)
    print(f"Backup saved to {backup_path}")
    
    with open(BUNDLE_PATH, 'w', encoding='utf-8') as f:
        f.write(clean_bundle)
    print(f"Clean bundle written: {len(clean_bundle):,} bytes")
