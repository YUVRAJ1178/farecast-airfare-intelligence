import sys
with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

YY_start = bundle.find('function YY(')
root_idx = bundle.find('G3.createRoot(document.getElementById("root"))', YY_start)
print('YY bounds:', YY_start, 'to', root_idx)
YY_code = bundle[YY_start:root_idx]
sys.stdout.buffer.write(YY_code[:250].encode('utf-8'))
sys.stdout.buffer.write(b'\n...\n')
sys.stdout.buffer.write(YY_code[-250:].encode('utf-8'))
