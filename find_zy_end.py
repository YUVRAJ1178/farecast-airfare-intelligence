with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

def safe_print(title, s):
    clean = s.encode('ascii', 'backslashreplace').decode('ascii')
    print(title, clean)

marker = 'calibrated against DGCA historical medians.'
pos = 0
while True:
    idx = bak.find(marker, pos)
    if idx == -1:
        break
    safe_print(f"Marker at {idx}", "")
    end = idx + len(marker)
    safe_print("Next 200 chars:", bak[end:end+200])
    pos = end + 1
