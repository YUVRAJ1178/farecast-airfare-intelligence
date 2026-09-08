import sys
sys.stdout.reconfigure(encoding='utf-8')

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    target1 = 'children:["\u20b9",ma.dgca_benchmark_fare.toLocaleString("en-IN")]'
    repl1 = 'children:["\u20b9",(ma.dgca_benchmark_fare??ma.dgca_fare??0).toLocaleString("en-IN")]'
    
    target2 = 'children:ma.delta>=0?`+\u20b9${ma.delta.toFixed(0)}`:`-\u20b9${Math.abs(ma.delta).toFixed(0)}`'
    repl2 = 'children:(ma.delta??(ma.platform_fare-(ma.dgca_benchmark_fare??ma.dgca_fare??0)))>=0?`+\u20b9${Number(ma.delta??(ma.platform_fare-(ma.dgca_benchmark_fare??ma.dgca_fare??0))).toFixed(0)}`:`-\u20b9${Math.abs(Number(ma.delta??(ma.platform_fare-(ma.dgca_benchmark_fare??ma.dgca_fare??0)))).toFixed(0)}`'

    target3 = 'children:[ma.pct_error.toFixed(2),"%"]'
    repl3 = 'children:[Number(ma.pct_error??ma.ape_pct??0).toFixed(2),"%"]'

    target4 = 'children:ma.status'
    repl4 = 'children:ma.status||(ma.compliance_status==="COMPLIANT"?"PASSED":"FAILED")'

    modified = False
    for t, r in [(target1, repl1), (target2, repl2), (target3, repl3), (target4, repl4)]:
        if t in content:
            content = content.replace(t, r)
            print(f"Replaced {t[:30]}... in {filepath}")
            modified = True
        else:
            print(f"Target not found: {t[:30]}... in {filepath}")

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully wrote {filepath}")
    else:
        print(f"No changes made to {filepath}")

patch_file('frontend/dist/assets/index-DJ3zwA0y.js')
patch_file('by_extracted.js')
