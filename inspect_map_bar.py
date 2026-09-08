with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

def safe_print(title, s):
    clean = str(s).encode('ascii', 'backslashreplace').decode('ascii')
    print(title, clean)

idx = bundle.find('Filter Corridors:')
safe_print("Filter Corridors context:", bundle[idx-100:idx+400])
