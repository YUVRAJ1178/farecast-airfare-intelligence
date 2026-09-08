with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

import re
# Remove single-line comments in JS
cleaned_lines = []
for line in bundle.split('\n'):
    stripped = line.strip()
    if stripped.startswith('//'):
        continue
    cleaned_lines.append(line)

new_bundle = '\n'.join(cleaned_lines)
with open('frontend/dist/assets/index-DJ3zwA0y.js', 'w', encoding='utf-8') as f:
    f.write(new_bundle)

print('Cleaned comments from bundle. Total lines:', len(cleaned_lines))
