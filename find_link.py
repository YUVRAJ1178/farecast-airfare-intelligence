with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
matches = [m.start() for m in re.finditer(r'createElement\("link"\)', bak)]
print('createElement("link") at:', matches)

for m in matches:
    print(f'At {m}:', repr(bak[max(0, m-50):m+50]))
