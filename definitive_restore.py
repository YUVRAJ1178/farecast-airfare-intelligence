"""
DEFINITIVE RESTORE

Theory confirmed:
- patch_frontend.py was run 4 times, each time prepending new_vY (159360 chars)
- The clean bundle = original[0:156196] + new_vY[one copy] + original[156196:]
- In BAK: original[156196:] = BAK[315556:4791200] + BAK[4950560:9331308] + BAK[9331308:end]
  Wait no... 

After 4 runs of patch_frontend.py, the bundle structure is:
BAK = P + V + V + V + V + R
where P = preamble (156196 chars), V = new_vY (159360 chars), R = original_rest_after_vY

So: P = BAK[0:156196]
    V1 = BAK[156196:315556]
    V2 = BAK[315556:474916]     [315556+159360=474916]
    V3 = BAK[474916:634276]     [474916+159360=634276]
    V4 = BAK[634276:793636]     [634276+159360=793636]
    R = BAK[793636:]

Verify: 4 * 159360 = 637440
156196 + 637440 = 793636
BAK[793636:] should be the original_rest_after_vY

Let's check: does BAK[793636:] start cleanly? Does it start with library code?
If so, then clean = P + V1 + R = BAK[0:315556] + BAK[793636:]
"""

import re

BAK_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js.bak'
OUT_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'

with open(BAK_PATH, 'r', encoding='utf-8') as f:
    bak = f.read()
print(f"BAK size: {len(bak):,}")

# Verify 4 vY insertions theory
# V1: 156196:315556 (159360)
# V2: 315556:474916 (159360)  
# V3: 474916:634276 (159360)
# V4: 634276:793636 (159360)
# R:  793636:end

# Check if V1==V2==V3==V4
v1 = bak[156196:315556]
v2 = bak[315556:474916]
v3 = bak[474916:634276]
v4 = bak[634276:793636]
print(f"V1==V2: {v1==v2}")
print(f"V2==V3: {v2==v3}")
print(f"V3==V4: {v3==v4}")

# Check what R starts with
r_start = bak[793636:793736]
print(f"\nR starts at 793636: {repr(r_start)}")

# Check what's right before V1 (end of preamble)
print(f"End of preamble: {repr(bak[156186:156196])}")

# vY positions in original: [156196, 315556, 4791200, 4950560]
# But with theory of 4 insertions: vY should be at:
# 156196, 315556, 474916, 634276, 793636 (5th would be R's vY... which is the real original vY)
vY_positions_actual = [m.start() for m in re.finditer(r'function vY\(', bak)]
print(f"\nActual vY positions: {vY_positions_actual}")
# We have 4 positions: [156196, 315556, 4791200, 4950560]
# Theory predicts: [156196, 315556, 474916, 634276, 793636]
# These don't match! The actual 3rd vY is at 4791200, not 474916.

# This means the 4-insertion theory is WRONG.
# Let me reconsider.

# What IS at 474916?
print(f"\nAt 474916: {repr(bak[474916:475016])}")
# And at 634276:
print(f"At 634276: {repr(bak[634276:634376])}")

# What about finding the EXACT structure by looking at what's between vY positions?
# [156196:315556] size=159360 - claimed new vY 
# [315556:4791200] size=4475644 - BIG block
# [4791200:4950560] size=159360 - another new vY
# [4950560:end] size=4396307 - rest

# If patch_frontend.py ran twice:
# Run 1: bundle = original_preamble + original_rest_after_vY_start(was 156196)
#         → new = preamble + new_vY + original_from_byte28 
#                (vY_end was 28 not 156196, so it included preamble[28:] in the "rest")
# Actually the vY_end was -1+len(marker) ≈ some small number like 28.
# So: new = original[:156196] + new_vY + original[28:]

# Run 1 result size: 156196 + 159360 + (original_size - 28)
# If original was 4,740,419 bytes: 156196 + 159360 + 4740391 = 5,055,947
# But current BAK is 9,346,867 which is much larger.

# Run 2 on Run1: found vY at 156196 in Run1 output
# vY_end in Run1 = same bad end ≈ 28
# new = run1[:156196] + new_vY + run1[28:]
# = preamble + new_vY + (preamble[28:156196] + new_vY + original[28:])
# = P + V + preamble[28:] + V + original[28:]

# preamble[28:] = 156168 chars
# preamble[28:156196] connects to original[28:]

# In Run2 output, vY positions would be at:
# 156196 (V1), 156196+159360+156168 = 471724 (V2 = inside "preamble[28:]...original[28:]" area)
# But actual positions are 156196, 315556, 4791200, 4950560
# 315556 ≠ 471724, so the 2-run theory is also wrong.

# I need to just SEARCH for what makes sense structurally.
# The bundle has 4 vY copies. Gaps: [159360, 4475644, 159360]
# GAP PATTERN: V, BIG, V
# The BIG block (4.47MB) between 315556 and 4791200 likely contains the ENTIRE original bundle
# from preamble[29:] through YY. Let me check:

# Does [315556:4791200] contain both hY and TY and old YY?
block = bak[315556:4791200]
print(f"\n[315556:4791200] analysis:")
print(f"  Size: {len(block):,}")
print(f"  Has hY: {'function hY(' in block}")
print(f"  Has TY: {'function TY(' in block}")
print(f"  Has zY: {'function zY(' in block}")  
print(f"  Has YY: {'function YY()' in block}")
print(f"  Has root render: {'G3.createRoot' in block}")
print(f"  First 80: {repr(block[:80])}")
print(f"  Last 80: {repr(block[-80:])}")
