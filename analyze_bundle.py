with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

import re

# Find functions
funcs = ['vY', 'hY', 'TY', 'SY', 'CY', 'PY', 'DY', 'zY', 'FY', 'BY', 'HY', 'YY']
for fn in funcs:
    pattern = rf'function {fn}\s*\('
    m = re.search(pattern, bundle)
    if m:
        print(f'{fn} found at index {m.start()}')
    else:
        print(f'{fn} NOT found')
