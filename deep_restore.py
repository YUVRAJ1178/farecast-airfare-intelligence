"""
deep_restore.py

The bundle has 3 copies of vY, 2 of zY, 1 of YY (correct).
The original bundle should have exactly 1 vY, 1 zY, 1 YY.

Let's understand the structure:
- The current bundle structure (post restore_bundle.py) is still corrupted.
- vY positions: [156196, 315556, 4791200]  (3 copies)

The REAL original bundle would:
1. Have vY at 156196 exactly once
2. Have all component functions (hY/TY/SY/CY/PY/DY/zY/BY/HY/FY) in between
3. Have YY near the end, followed by root render

The key insight: In the ORIGINAL bundle, function positions were:
- vY: 156196
- hY: 153398 (BEFORE vY, so it's not the filter panel)
- BY: 4476895
- HY: 4510853
- YY: 4536944
- root: ~4568519

So the original bundle was approximately 4.57MB.

Current bundle at 9.18MB still has duplicates.
Let me find where the ORIGINAL bundle actually ends.

The root render call in the ORIGINAL bundle would have been at ~4,568,519.
After the patch, the new YY was appended AFTER this original root render.

Wait - looking at the current bundle - there's only ONE root render now (at 9,346,764).
This means restore_bundle.py already removed one root render.

Let me count vY more carefully and find the original preamble boundary.
The preamble (bytes 0 to 156196) should only exist ONCE.
The duplicate vY at 315556 = 156196 + 159360 means the duplicate original starts at 315556 - (156196-29) = 315556 - 156167 = 159389.
But the ORIGINAL preamble runs from 0 to 156195.
So at position 159389, there's a THIRD copy of the preamble bytes starting at byte 29.

This means the bundle structure is:
[0:156196] = original preamble bytes 0-156195
[156196:315556] = new vY (159360 chars)
[315556:] = duplicate of original bytes 29 onwards

Wait: 315556 - 29 = 315527. But original vY was at 156196. In the duplicate (starting at 159389 = 156196 + 3193?), vY should appear at 159389 + (156196-29) = 159389 + 156167 = 315556. Yes! That matches.

So the full structure is:
[0:156196] = original bytes 0..156195 (preamble)
[156196:315556] = new vY (inserted content)  
[315556:9346866] = duplicate of original bytes 29..end_of_original_bundle

So the ORIGINAL bundle was:
bytes 0..156195 (the preamble)  
bytes 156196..original_end (vY + rest of original)

And original_end = total_len_of_duplicate + 29 = (9346866 - 315556) + 29 + ... hmm

Actually: duplicate_section = bundle[315556:] 
This equals original_bundle[29:] 
So original_bundle = original_bundle[0:29] + bundle[315556:]
                   = bundle[0:29] + bundle[315556:]

Let's verify: original_bundle[0:29] should be the first 29 bytes of the preamble.
bundle[315556:315556+50] should equal original_bundle[29:79] = bundle[29:79]
"""
with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

print(f"Bundle size: {len(bundle):,}")

# Verify the theory: bundle[29:79] == bundle[315556:315606]?
chunk_a = bundle[29:79]
chunk_b = bundle[315556:315606]
print(f"Original bytes[29:79]: {repr(chunk_a)}")
print(f"Duplicate  bytes[315556:315606]: {repr(chunk_b)}")
print(f"Match: {chunk_a == chunk_b}")

# So the original bundle = bundle[0:29] + bundle[315556:]
# But we also need to account for the new YY appended at the end
# The new YY was appended by patch_frontend.py IN THE ORIGINAL run
# So bundle[315556:] = original[29:original_YY_end] + new_YY + root_render

# Find where the OLD YY (in the duplicate) ends and new YY begins
# The duplicate original had its own YY replaced by new_YY
# So in bundle[315556:], the YY positions tell us where old was replaced with new

import re
# In the full bundle, we have yy at [9331308]
# In the duplicate region (starting at 315556), where would old YY have been?
# Old YY was at original position ~4536944
# In duplicate: 315556 + (4536944 - 29) = 315556 + 4536915 = 4852471
yy_in_dup = 315556 + (4536944 - 29)
print(f"\nExpected old YY in duplicate at: {yy_in_dup}")
yy_positions = [m.start() for m in re.finditer(r'function YY\(\)', bundle)]
print(f"Actual YY positions: {yy_positions}")

# So the duplicate does NOT have old YY (it was replaced).
# bundle[315556:9331308] = original[29:4536944] (with YY stripped from the end)
# bundle[9331308:9346866] = new YY + root render

# Therefore the CLEAN original bundle reconstruction:
# original = bundle[0:29] + bundle[315556:]
# But we need to ALSO handle that the new vY (from patch_frontend.py) needs to stay.
# The new vY is at bundle[156196:315556].
# The original vY was at bundle[315556 + (156196-29) : ...] i.e., at position 315556+156167 = 471723

# We want:
# preamble[0:156196] + new_vY[156196:315556] + rest_of_original_without_old_vY

# The original bundle content (without the new_vY) starts at position 315556 in current bundle.
# But 315556 corresponds to original byte 29.
# Original byte 29..156195 = the preamble remainder (already in current bundle[0:156196] but 29..156195 is duplicated in 315556..471556)
# Original byte 156196 (the original vY) = now at current bundle position 315556+(156196-29) = 471723

# So clean bundle with new vY:
# bundle[0:156196]         = preamble (bytes 0-156195)
# bundle[156196:315556]    = new vY  
# bundle[471723:]          = rest of original from AFTER original vY start
#   BUT wait - we need to SKIP the original vY too! The original vY was at 156196, ran until some end.
#   Where did original vY end? Let's find it.

orig_vy_in_dup = 471723  # position of original vY in current (corrupted) bundle
print(f"\nOriginal vY in current bundle at: {orig_vy_in_dup}")
print(f"Context: {repr(bundle[orig_vy_in_dup:orig_vy_in_dup+100])}")

# Original vY ends where the next function starts
# In the original, what came after vY? The next function.
# Let's find the next 'function ' after orig_vy_in_dup
next_func = bundle.find('\nfunction ', orig_vy_in_dup + 10)
print(f"Next function after orig vY: {next_func}")
print(f"Context: {repr(bundle[next_func:next_func+60])}")

# So the original vY ran from 471723 to next_func
orig_vy_end = next_func  
print(f"Original vY size in duplicate: {orig_vy_end - orig_vy_in_dup} chars")

# Clean bundle = preamble + new_vY + (skip orig preamble duplicate) + (skip orig vY) + rest
# = bundle[0:156196] + bundle[156196:315556] + bundle[orig_vy_end:]
# = bundle[0:315556] + bundle[orig_vy_end:]

clean = bundle[0:315556] + bundle[orig_vy_end:]
print(f"\nClean bundle size: {len(clean):,}")
print(f"vY count: {clean.count('function vY(')}")
print(f"zY count: {clean.count('function zY(')}")
print(f"YY count: {clean.count('function YY()')}")
print(f"root render count: {clean.count('G3.createRoot')}")
print(f"FARECAST: {clean.count('FARECAST')}")
print(f"Apply Filters: {'YES' if 'Apply Filters' in clean else 'NO'}")
print(f"right-panel: {'YES' if 'right-panel' in clean else 'NO'}")

# Verify preamble connects correctly
print(f"\nAt join point (315556-50 to 315556+50):")
print(repr(bundle[315506:315606]))
print(f"\nIn clean bundle at same area (315506 to 315606):")
print(repr(clean[315506:315606]))
