with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

def safe_print(title, s):
    clean = s.encode('ascii', 'backslashreplace').decode('ascii')
    print(title, clean)

safe_print('Context around 4788402 (hY 3):', bak[4788402-150:4788402+150])
safe_print('Context around 4947762 (hY 4):', bak[4947762-150:4947762+150])
safe_print('Context around 4635004:', bak[4635004-100:4635004+100])
safe_print('Context around 4627801+8000 (after zY1):', bak[4627801+7500:4627801+8500])
