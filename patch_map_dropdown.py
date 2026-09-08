with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

target = 'children:Bn.label},Bn.id)),'
pos = bundle.find(target)
if pos == -1:
    raise Exception("Target pattern not found in bundle")

insert_pos = pos + len(target)

dropdown_code = (
    'nr.jsxs("div",{style:{marginLeft:"auto",display:"flex",alignItems:"center",gap:6},children:['
    'nr.jsx("span",{style:{fontSize:"0.72rem",color:"var(--text-muted)",fontWeight:600},children:"Airport Hub:"}),'
    'nr.jsxs("select",{'
    'id:"map-airport-selector",'
    'value:nn?nn.code:"",'
    'onChange:e=>{'
    'const c=e.target.value;'
    'if(!c){qn(null);return;}'
    'const h=($&&$.hubs)?$.hubs.find(v=>v.code===c):null;'
    'if(h){qn(h);va(null);}'
    '},'
    'style:{fontSize:"0.75rem",padding:"4px 8px",borderRadius:6,background:"var(--bg-secondary)",color:"var(--text-primary)",border:"1px solid var(--border)"},'
    'children:['
    'nr.jsx("option",{value:"",children:"-- All 17 Airport Hubs --"}),'
    '($&&$.hubs?$.hubs:[]).map(h=>nr.jsx("option",{value:h.code,children:`${h.city} (${h.code}) - ${h.tier}`},h.code))'
    ']'
    '})'
    ']}),'
)

new_bundle = bundle[:insert_pos] + dropdown_code + bundle[insert_pos:]

with open('frontend/dist/assets/index-DJ3zwA0y.js', 'w', encoding='utf-8') as f:
    f.write(new_bundle)

print("SUCCESS: Airport Hub selector dropdown added to India Map in bundle! Final size:", len(new_bundle))
