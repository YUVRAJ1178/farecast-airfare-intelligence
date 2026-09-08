"""
precise_restore.py

Analysis findings:
- preamble[0:156196] ends with: 'h (IXC)"};'  (the city names map ends)
- new_vy[156196:315556] also ends with something
- middle region [5109920:9331308] starts with: '=vd();G.exports=...' (starts with =, not a statement)

This means the join is wrong — the middle region starts inside a statement.
We need to find the RIGHT boundary for the middle region.

The preamble ends at 156196 with the C7 object (city names).
After C7 comes: 'function vY(' at 156196 — that IS our new vY.

After new_vY ends at 315556, comes the DUPLICATE preamble (bytes 29-156196) starting at 315556.
Then the DUPLICATE new_vY at 315556+(156196-29) = 471723? No...

Actually from the analysis: vY positions are [156196, 315556, 4791200, 4950560]
gaps = [159360, 4475644, 159360]

So there are TWO gap types: 159360 (= new vY size) and 4,475,644.

This means:
- Block 1: new_vY at 156196, length 159360
- Block 2: something at 315556, length 4,475,644
- Block 3: new_vY copy at 4791200, length 159360
- Block 4: new_vY copy at 4950560

The 4.47MB block (315556 to 4791200) is a COMPLETE ORIGINAL BUNDLE copy minus preamble.
Because the original bundle was ~4.7MB, and the preamble was ~156KB, 
the rest would be ~4.57MB. But 4.47MB ≠ 4.57MB.

Actually the 4.47MB block contains original[29:original_vY_start-156196+29+...] hmm.

Let me just find the CORRECT split points by identifying what's at the boundaries.

"""
import re

BAK_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js.bak'
OUT_PATH = 'frontend/dist/assets/index-DJ3zwA0y.js'

with open(BAK_PATH, 'r', encoding='utf-8') as f:
    bak = f.read()
print(f"Backup: {len(bak):,}")

# The new_vY block: [156196:315556]
# It ends just before the second vY
# What does it end with?
print(f"\nnew_vY ends at 315556:")
print(f"  Last 80 before: {repr(bak[315476:315556])}")

# The duplicate block starts at 315556
# What does it start with?
print(f"\nDuplicate block starts at 315556:")
print(f"  First 80: {repr(bak[315556:315636])}")

# The 4th vY ends at 4950560+159360 = 5109920
# What comes just before 5109920?
print(f"\nBefore middle region at 5109920:")
print(f"  Last 80: {repr(bak[5109840:5109920])}")
print(f"  First 80 after: {repr(bak[5109920:5110000])}")

# The issue is the middle region [5109920:] starts mid-statement with '=vd();G.exports...'
# We need to find a clean boundary BEFORE 5109920.
# Let's look for the start of the statement that contains position 5109920

# The character before 5109920 in bak should be part of a statement
print(f"  Char at 5109919: {repr(bak[5109919])}")
print(f"  Chars 5109870-5109925: {repr(bak[5109870:5109925])}")

# Let's find a safe boundary by searching for a statement separator before 5109920
# A safe point would be after a '}' or ';' that ends a top-level statement

# Search backwards from 5109920 for a semicolon followed by newline
for i in range(5109920, 5109800, -1):
    if bak[i] == ';' or (bak[i] == '}' and bak[i+1] == '\n'):
        print(f"  Safe boundary at: {i}, char: {repr(bak[i:i+10])}")
        break

# The new_vY ENDS with ';}' which is fine. But the next char at 315556 is start of 
# duplicate preamble which starts at byte 29 of original.
# The duplicate preamble bytes 29..156196 would be 156167 chars
# Then duplicate new_vY starts at 315556+156167 = 471723

# Let's verify what's at position 471723 in bak
print(f"\nAt 471723: {repr(bak[471723:471823])}")

# The second vY is at 315556 (in bak) which is inside the duplicate block
# In the DUPLICATE, vY is at duplicate_byte_156196 = 315556 + (156196-29) = 471723
# But we SEE vY at 315556, not 471723!

# This means: bak[315556] is already the start of the duplicate's vY
# Therefore the duplicate starts DIRECTLY with vY (i.e., the duplicate starts at byte 156196, not byte 29)
# This would mean: bak[156196:315556] = new_vY (good)
# And bak[315556:] = original_bundle[156196:] (everything from old vY onwards)

# Verify: does bak[315556:315656] match what the original vY looked like?
print(f"\nbak[315556:315656] (should be original vY start):")
print(repr(bak[315556:315656]))

# And bak[156196:315556] should be the new vY
print(f"\nbak[156196:156296] (new vY start):")
print(repr(bak[156196:156296]))

# So the ORIGINAL bundle structure (before patch_frontend.py ran) was:
# [0:156196] = preamble
# [156196:original_end] = vY + everything else + YY + root

# After patch_frontend.py: it set vY_end = ~28 (because end marker not found, -1+len(marker))
# Then: bundle = bundle[:156196] + new_vY + bundle[28:]
# Result: [0:156196] preamble + new_vY + bundle[28:]
# = preamble + new_vY + original[28:]

# But original[28:] starts mid-preamble (preamble runs 0..156195)
# original[28:156196] = preamble bytes 28..156195 (nearly full preamble duplicate!)
# original[156196:] = original vY + everything + old YY

# So: bak = preamble[0:156196] + new_vY + preamble[28:156196] + orig_vY + rest + old_YY_replaced + new_YY + root

# preamble[28:156196] = 156168 chars
# At bak[315556] = preamble[28:156196]... but we see vY there!
# Let's check: 315556 - 159360 - 156196 = 315556 - 315556 = 0... no.
# 156196 + 159360 = 315556. So bak[315556] = bundle[28] of original.

# bundle[28] of original... what was there?
print(f"\nOriginal bundle[28:128] = bak[315556:315656]:")
print(repr(bak[315556:315656]))

# If this is truly 'function vY(' then original byte 28 started with 'function vY('
# That would mean the PREAMBLE was only 28 bytes long!

# Check if the preamble is actually shorter than 156196 chars
# Let's look at what's at bak[156196] vs bak[315556]
print(f"\nbak[156196:156296]:")
print(repr(bak[156196:156296]))
print(f"\nbak[315556:315656]:")
print(repr(bak[315556:315656]))
print(f"\nAre they equal? {bak[156196:156296] == bak[315556:315656]}")

# They're both 'function vY(' !!
# This means the NEW vY and the DUPLICATE vY are IDENTICAL!
# The patch_frontend.py's new_vY is EXACTLY the same content as what was already there.
# So patch_frontend.py actually REPLACED vY correctly! The duplication came from 
# running the script MULTIPLE TIMES!

# Count how many times new_vY content appears:
# The new vY contains 'handleOriginChange' (custom function added by patch)
has_origin_change = bak.count('handleOriginChange')
print(f"\nhandleOriginChange count: {has_origin_change}")

# Check the first few chars are different
print(f"\nbak[156196:156216]: {repr(bak[156196:156216])}")
print(f"bak[315556:315576]: {repr(bak[315556:315576])}")
