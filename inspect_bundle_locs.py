with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

pos_dash = bundle.find('dashboardSummary:()=>vh("/dashboard-summary")')
print('dashboardSummary pos:', pos_dash)

pos_yy = bundle.find('function YY()')
print('YY start pos:', pos_yy)

pos_root = bundle.find('G3.createRoot(document.getElementById("root"))')
print('root render pos:', pos_root)

pos_vy = bundle.find('function vY({filters:$,onFilterChange:se})')
print('vY start pos:', pos_vy)

pos_zy = bundle.find('function zY({filters:$})')
print('zY start pos:', pos_zy)
