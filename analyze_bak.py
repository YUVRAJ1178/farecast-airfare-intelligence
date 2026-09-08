import re

with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

print('Length of bak:', len(bak))

for m in re.finditer(r'document\.getElementById\("root"\)', bak):
    print('root at:', m.start(), repr(bak[m.start()-20:m.start()+60]))

for comp in ['vY', 'hY', 'TY', 'SY', 'CY', 'PY', 'DY', 'zY', 'FY', 'BY', 'HY', 'YY']:
    indices = [m.start() for m in re.finditer(r'function\s+' + comp + r'\(', bak)]
    print(f'function {comp}: {len(indices)} occurrences at {indices}')
