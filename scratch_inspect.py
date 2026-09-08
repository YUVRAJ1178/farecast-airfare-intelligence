with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

idx = bundle.find('function hY(')
print("hY at", idx)
print(bundle[idx:idx+2000].encode('ascii', 'backslashreplace').decode())
