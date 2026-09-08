with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

p1 = bak[0:156196]
p2 = bak[315556:318749]
p3 = bak[318749:4627801]
p4 = bak[9262805:]

clean_bundle = p1 + p2 + p3 + p4

print("Total length:", len(clean_bundle))

# Join 1 check:
print("Join 1 (p1 -> p2):", repr(clean_bundle[156196-30:156196+40]))

# Join 2 check:
j2 = len(p1) + len(p2)
print("Join 2 (p2 -> p3):", repr(clean_bundle[j2-30:j2+40]))

# Join 3 check:
j3 = len(p1) + len(p2) + len(p3)
print("Join 3 (p3 -> p4):", repr(clean_bundle[j3-30:j3+40]))

print("End of clean bundle:", repr(clean_bundle[-80:]))

import re
components = ['hY', 'vY', 'TY', 'SY', 'CY', 'PY', 'DY', 'zY', 'FY', 'BY', 'HY', 'YY']
for comp in components:
    matches = list(re.finditer(r'function\s+' + comp + r'\(', clean_bundle))
    print(f'function {comp}: count={len(matches)}, pos={[m.start() for m in matches]}')

roots = list(re.finditer(r'createRoot\(document\.getElementById\("root"\)\)', clean_bundle))
print(f'Root renders: count={len(roots)}, pos={[m.start() for m in roots]}')

opens = clean_bundle.count('{')
closes = clean_bundle.count('}')
print(f'Braces: {opens} open, {closes} close, diff={opens-closes}')

open_p = clean_bundle.count('(')
close_p = clean_bundle.count(')')
print(f'Parens: {open_p} open, {close_p} close, diff={open_p-close_p}')

open_b = clean_bundle.count('[')
close_b = clean_bundle.count(']')
print(f'Brackets: {open_b} open, {close_b} close, diff={open_b-close_b}')
