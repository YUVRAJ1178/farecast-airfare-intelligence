with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

def safe_print(title, s):
    clean = str(s).encode('ascii', 'backslashreplace').decode('ascii')
    print(title, clean)

safe_print("Exact slice around 9269965:", repr(bak[9269965:9270035]))
safe_print("const P7 offset:", bak.find('const P7={', 9269900))
