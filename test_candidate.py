with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

candidate = bak[0:31] + bak[4635004:]

print("Candidate length:", len(candidate))
print("Starts with:", repr(candidate[:80]))
print("Ends with:", repr(candidate[-80:]))

import re
for comp in ['vY', 'hY', 'TY', 'SY', 'CY', 'PY', 'DY', 'zY', 'FY', 'BY', 'HY', 'YY']:
    matches = list(re.finditer(r'function\s+' + comp + r'\(', candidate))
    print(f'function {comp}: count={len(matches)}, pos={[m.start() for m in matches]}')

roots = list(re.finditer(r'createRoot\(document\.getElementById\("root"\)\)', candidate))
print(f'Root renders: count={len(roots)}, pos={[m.start() for m in roots]}')

# Check syntax / brace balance
opens = candidate.count('{')
closes = candidate.count('}')
print(f'Braces: {opens} open, {closes} close, diff={opens-closes}')

open_p = candidate.count('(')
close_p = candidate.count(')')
print(f'Parens: {open_p} open, {close_p} close, diff={open_p-close_p}')

open_b = candidate.count('[')
close_b = candidate.count(']')
print(f'Brackets: {open_b} open, {close_b} close, diff={open_b-close_b}')
