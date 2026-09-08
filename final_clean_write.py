"""
final_clean_write.py

The bundle is: 
  [0:156196]   = preamble (correct)
  [156196:315556] = duplicate new_vY (EXTRA COPY — this is the one added by patch runs)
  [315556:end]  = original bundle from vY onwards (this has correct vY, zY, YY, root)

Wait — but the issue is that [315556:] also has duplicates (vY at 315556, 4791200, 4950560).

Let me check: what's at 4791200 and 4950560?
Are they additional COPIES of new_vY?

From the gap analysis: gaps = [159360, 4,475,644, 159360]
- vY[0]=156196, vY[1]=315556 → gap=159360  (new_vY block)
- vY[1]=315556, vY[2]=4791200 → gap=4,475,644  (big original-like block)
- vY[2]=4791200, vY[3]=4950560 → gap=159360  (another new_vY block)

And each new_vY block is 159360 chars (identical, confirmed).

So the structure in [315556:] is:
[315556:4791200] = 4,475,644 chars = original bundle from vY to the point where 
                    patch_frontend.py spliced in another new_vY copy
[4791200:4950560] = another new_vY copy (EXTRA)
[4950560:9331308] = rest of original bundle from vY end onwards (with library code + zY + BY + HY)
[9331308:9346866] = new YY + root render

So the ORIGINAL bundle (pre-any-patch) would be:
[0:156196] preamble + [315556:4791200] original_vY_to_splice_point + [4950560:9331308] rest_of_funcs

But the splice point at 4791200 would mean the original vY + all functions from 315556 to 4791200 = 4,475,644 chars.
In the original (clean) bundle, this should have been just vY + library code + other components.

Wait — let me verify: after the 4th vY at 4950560, the content is '=vd();G.exports=...' 
which is a continuation of a bundle module (node_modules/fast-isnumeric). This suggests
4950560+159360 = 5109920 is MID-STATEMENT in the original bundle.

This confirms: patch_frontend.py was run on the bundle that ALREADY had one new_vY prepended.
The second run found new_vY again at 315556 (it was already there) and prepended ANOTHER copy,
pushing the boundary further.

The CLEAN bundle is:
  preamble[0:156196] + original_from_vY[315556:4791200] + rest[4950560:9346866]

Let me verify this builds a coherent bundle.
"""
import re

BAK_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js.bak'
OUT_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'

with open(BAK_PATH, 'r', encoding='utf-8') as f:
    bak = f.read()

# Verify boundary connections
# End of preamble (156186:156196) connects to start of vY (315556:315566)
preamble_end = bak[156186:156196]
vy_start = bak[315556:315566]
print(f"Preamble ends with: {repr(preamble_end)}")
print(f"vY starts with: {repr(vy_start)}")
# The preamble ends with: 'h (IXC)"};'
# The vY starts with: 'function vY'
# These don't connect directly — we need to JOIN them properly.
# In the original, preamble ended with '};' then vY started with 'function vY'

# Check if they connect cleanly:
original_join = preamble_end + vy_start
print(f"Join: {repr(original_join)}")
# Should be: '...IXC)"};function vY...' which IS valid JS!

# Now check the CUT at 4791200 and RESUME at 4950560
cut_end = bak[4791190:4791210]
resume_start = bak[4950560:4950580]
print(f"\nCut at 4791200: ending with: {repr(bak[4791150:4791200])}")
print(f"Resume at 4950560: starting with: {repr(bak[4950560:4950620])}")

# The cut ends mid-content at 4791200 (which is a duplicate new_vY start)
# The resume at 4950560 starts with function vY (another new_vY copy)
# We WANT to skip from just before 4791200 to just after 4950560
# = skip TWO new_vY copies (159360*2 = 318720 chars)

# What's at 4791200-5? (the byte just before the 3rd vY copy)
print(f"\nJust before 3rd vY copy: {repr(bak[4791185:4791205])}")
# And what's at 4950560+159360=5109920?
print(f"Just after 4th vY copy: {repr(bak[5109910:5109930])}")

# So the join is: bak[4791200-X:4791200] → bak[5109920:5109920+Y]
# where X is chars to complete the statement before 4791200
# and Y is chars to start a clean statement after 5109920

# Actually: if we build [preamble][315556:4791200][4950560:end]
# the join at 4791200→4950560 boundary must be checked:
# What's right before 4791200?
pre_cut = bak[4791150:4791200]
# What's right after 4950560?
post_cut = bak[4950560:4950610]
print(f"\nPre-cut (before 4791200): {repr(pre_cut)}")
print(f"Post-cut (after 4950560): {repr(post_cut)}")
# The same content would appear on BOTH sides since they're both vY starts!

# Hmm, this approach is getting complex. Let me try the simplest possible fix:
# The LAST-GOOD portion of the bundle is just [preamble + final good block]
# The final good block = everything from the LAST vY position onwards
# (the 4th vY at 4950560 is the last copy)
# After the 4th vY ends, we have the original continuation code.

# APPROACH: Take preamble + LAST copy of vY + everything after
# preamble = bak[0:156196]  
# last vY = bak[4950560:4950560+159360] = bak[4950560:5109920]
# rest after last vY = bak[5109920:]
# 
# But we need to check: does bak[5109920:] START cleanly?
# We saw it starts with: '=vd();G.exports=...'
# That '=' means we're inside a statement! This is broken.

# The issue is that bak[5109920] = '=' is part of:
# '...{var h=vd();G.exports=function...'
# The 'h' that precedes it was cut by inserting new_vY at 4791200.
# So at position 4791200, we INTERRUPTED a mid-statement to insert new_vY.

# We need to find where the statement that was interrupted starts.
# Search BACKWARDS from 5109920 for the start of this statement.
# The statement is within: '{var h=vd();G.exports=...'
# We need to find the '{' before this.

# Alternatively: find the matching content in [315556:4791200] 
# bak[4791190:4791200] = right before the 3rd vY copy
pre_3rd_vy = bak[4791180:4791200]
print(f"\nLast 20 chars before 3rd vY copy: {repr(pre_3rd_vy)}")

# If this is '...{var h' then we need to backtrack to find the full statement start
# to properly re-join with bak[4950560+159360:]

# But actually: the content at bak[315556:4791200] has the original vY through to 
# the MIDDLE of a statement. And bak[4950560:5109920] is the 4th new_vY (which we want to keep once).
# And bak[5109920:] continues from the middle of that statement (bad start).

# REAL SOLUTION: Both 3rd and 4th vY blocks are IDENTICAL and they're duplicates inserted.
# The content that was CUT (interrupted) would be at 315556+(4791200-315556) = 4791200.
# In the ORIGINAL (first-time patch) bundle, this content would have been continuous.
# The ORIGINAL (first-time patch) bundle = bak[315556:] if we remove the second vY insertion.

# The second vY was inserted at position 4791200 in the (already-once-patched) bundle.
# It was the result of running patch_frontend.py a SECOND time on [bak].
# vY at 4791200 was found (= bak[315556:315556+(4791200-315556)] = bak from 315556 
# which had vY right at start at 315556, and then another at 315556+4475644=4791200).

# So [315556:4791200] is a COMPLETE first-patch bundle from vY onwards.
# And [4791200:4950560] is an EXTRA new_vY (from second patch run).
# And [4950560:] is the continuation of [315556:4791200] from char 4791200-315556=4475644

# Therefore: [315556:4791200] + [4950560:end] = complete first-patch bundle from vY onwards
# = [315556:4791200] + [4950560:end]
# But [4950560:end] STARTS with 4th new_vY!

# Oh wait: [4950560:] starts with function vY (4th copy).
# [315556:4791200] ends and the content from 315556+4475644=4791200 would have had:
#   continuation of a statement (the '=vd()' part that was cut)

# So in the ONCE-patched bundle (315556..4791200), the content was interrupted at char 4475644
# by the SECOND patch_frontend.py run, which inserted new_vY at that position.

# The content that should follow [315556:4791200] is bak[4950560+159360:] = bak[5109920:]
# = '=vd();G.exports=...' which starts with = (mid-statement).

# And [315556:4791200] ends with: what was right before position 4791200 in once-patched bundle
# = what's at position 4791180-4791200 in bak

print(f"\nFINAL ANALYSIS:")
print(f"[315556:4791200] last 50: {repr(bak[4791150:4791200])}")
print(f"[4950560:5110000] first after 4th vY end: {repr(bak[5109915:5109960])}")

# CONCLUSION:
# The join [315556:4791200] + [5109920:] is:
# ...{var h + =vd();G.exports=...
# = '{var h=vd();G.exports=...' which IS VALID!
# The 'h' is the last char before 4791200, and '=vd()...' is right after 5109920!

# Let's verify: last char before 4791200
print(f"Last char before 4791200: {repr(bak[4791199])}")
# And first char after 5109920
print(f"First char at 5109920: {repr(bak[5109920])}")
