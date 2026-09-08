import re

with open('yy_extracted.js', 'r', encoding='utf-8') as f:
    yy = f.read()

print('Length of YY:', len(yy))
# Find nav items
nav_match = re.search(r'const navItems\s*=\s*(\[[^\]]+\])', yy)
if nav_match:
    print('navItems:', nav_match.group(1))

# Check tabs
print('Rendered tabs:')
for m in re.finditer(r'activeTab\s*===?\s*"([^"]+)"', yy):
    print(' -', m.group(1))

# Check right panel
print('Has right-panel:', 'right-panel' in yy)
print('Has sidebar-ai-pill:', 'sidebar-ai-pill' in yy)
print('Has FORECAST:', 'FORECAST' in yy)
print('Has Smarter Skies:', 'Smarter Skies' in yy)
