with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    js = f.read()

print('Bundle size:', len(js))
print('Has createRoot:', 'getElementById("root")' in js)
components = ['hY', 'vY', 'TY', 'SY', 'CY', 'PY', 'DY', 'zY', 'FY', 'BY', 'HY', 'YY']
for c in components:
    cnt = js.count(f'function {c}(')
    print(f'function {c}(): count = {cnt}')
