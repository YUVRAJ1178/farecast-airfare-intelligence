with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
matches = [m.start() for m in re.finditer(r'Reset', bak)]
print(f"Total occurrences of 'Reset': {len(matches)}")
for m in matches[:10]:
    print(f"At {m}:", repr(bak[m-30:m+50]))
