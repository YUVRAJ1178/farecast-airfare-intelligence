with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
matches = [m.start() for m in re.finditer(r'var\s+\$9', bak)]
print('var $9 at:', matches)
for m in matches:
    print(f'At {m}:', repr(bak[m-40:m+40]))
