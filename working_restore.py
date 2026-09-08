"""
FINAL WORKING RESTORE

[315556:4791200] contains:
- Starts with function vY (same new patched vY)
- Has hY, TY, zY (all component functions)
- Has root render (OLD - before new YY was added)
- Ends with IXC city names (= C7 map closure, loops back to before vY)

So this block IS the complete once-patched bundle from vY to root render.
The root render inside it references OLD YY (not the new patched YY).

We want: preamble + vY + (everything between vY and old YY in block) + new YY + root

Find where old root render is in [315556:4791200]:
"""
import re

BAK_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js.bak'
OUT_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'

with open(BAK_PATH, 'r', encoding='utf-8') as f:
    bak = f.read()

block = bak[315556:4791200]
ROOT_RENDER = 'G3.createRoot(document.getElementById("root"))'
NEW_YY = 'function YY()'

root_in_block = block.find(ROOT_RENDER)
yy_in_block = block.find(NEW_YY)
print(f"Root render in block at: {root_in_block}")
print(f"YY in block at: {yy_in_block}")

# root render is at some position in the block
# This is the OLD root render which references OLD YY
# The OLD YY (before patch) ended at some position before this root render

# We want content UP TO where old YY starts
# Since block has no function YY(), the old YY may have been REPLACED already
# (patch_frontend.py replaced old YY with new YY appended at end of bak)

# The block has root render but NO YY - that means old YY was CUT from this block
# and new YY was appended at bak[9331308:]

# So in block: [root_in_block] onwards is: G3.createRoot(...).render(nr.jsx(eH.StrictMode,{children:nr.jsx(YY,{})}))
# The YY here refers to the NEW YY at bak[9331308]

# Wait - the block's root render would still render YY correctly IF YY is defined 
# somewhere in the bundle. The issue is the DUPLICATE DECLARATIONS, not the root render.

# The block [315556:4791200] already has the CORRECT structure:
# vY + lib code + hY + TY + SY + CY + PY + DY + zY + FY + BY + HY + root_render
# (no YY in block because it was replaced with new YY)

# The PREAMBLE section [0:156196] + the block [315556:4791200] is a COMPLETE clean bundle
# EXCEPT preamble already contains a vY call at 156196:315556 which we DON'T want to skip

# TEST: Build clean = preamble[0:156196] + block[315556:4791200] 
# (skipping the duplicate new_vY at 156196:315556)
# But preamble ends with C7 map '};' and block starts with 'function vY('
# So: ...IXC"};function vY( ... this is VALID JS!

# Then add the new YY + root render from bak[9331308:]
# But block already has its own root render! 
# So we'd have TWO root renders and NO YY definition visible to the first root render.

# CORRECT PLAN:
# 1. Take preamble[0:156196]  (ends with C7 closure)
# 2. Take block content BEFORE the root render: block[0:root_in_block]
#    = vY + all library + all component functions (no root render, no YY)
# 3. Add new YY: bak[9331308:]  (which includes new YY + root render)

# This gives us: preamble + vY + library + components + new YY + root render
# PERFECT!

clean_preamble = bak[0:156196]
block_content = block[0:root_in_block]  # everything up to (not including) old root render
new_yy_and_root = bak[9331308:]  # new YY + root render

print(f"\nParts:")
print(f"  Preamble: {len(clean_preamble):,}")
print(f"  Block content (no root): {len(block_content):,}")
print(f"  New YY+root: {len(new_yy_and_root):,}")
print(f"  Block root_in_block at: {root_in_block}")
print(f"  Block content ends with: {repr(block_content[-60:])}")
print(f"  New YY starts with: {repr(new_yy_and_root[:60])}")

# Check the join: block_content ends with... then new YY starts with function YY()
# Is there a '}' or ';' before function YY()? There should be.

clean = clean_preamble + block_content + new_yy_and_root

print(f"\nClean bundle size: {len(clean):,}")
print(f"vY count: {clean.count('function vY(')}")
print(f"zY count: {clean.count('function zY(')}")  
print(f"YY count: {clean.count('function YY()')}")
print(f"root render count: {clean.count(ROOT_RENDER)}")
print(f"hY count: {clean.count('function hY(')}")
print(f"TY count: {clean.count('function TY(')}")
print(f"FARECAST: {clean.count('FARECAST')}")
print(f"Apply Filters: {'YES' if 'Apply Filters' in clean else 'NO'}")
print(f"right-panel: {'YES' if 'right-panel' in clean else 'NO'}")
print(f"From Flight Prices: {'YES' if 'From Flight Prices' in clean else 'NO'}")
print(f"dashboardSummary with filters: {'YES' if 'dashboardSummary({origin:' in clean else 'NO'}")

# Verify brace balance of new YY
yy_start_in_clean = clean.find('function YY()')
root_in_clean = clean.find(ROOT_RENDER, yy_start_in_clean)
yy_region = clean[yy_start_in_clean:root_in_clean]
opens = yy_region.count('{')
closes = yy_region.count('}')
print(f"YY brace balance: {opens} open, {closes} close (diff={opens-closes})")

# Check join points
print(f"\nJoin1 (preamble->block): {repr(clean[156186:156220])}")
print(f"Join2 (block->new_YY): {repr(clean[len(clean_preamble)+len(block_content)-30:len(clean_preamble)+len(block_content)+40])}")

if (len(clean) > 4000000 
    and clean.count('function vY(') == 1 
    and clean.count('function YY()') == 1
    and clean.count(ROOT_RENDER) == 1
    and clean.count('FARECAST') >= 3):
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(clean)
    print(f"\n✓ SUCCESS: Clean bundle written: {len(clean):,} bytes")
else:
    print(f"\n✗ VALIDATION FAILED - not writing")
    print(f"  vY: {clean.count('function vY(')}, YY: {clean.count('function YY()')}")
    print(f"  root: {clean.count(ROOT_RENDER)}, FARECAST: {clean.count('FARECAST')}")
