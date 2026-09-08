with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

# Let's inspect new_vY
# In patch_frontend.py, new_vY ends with:
# nr.jsx("button",{className:"btn-secondary",onClick:qn,id:"filter-reset",children:"Reset Filters"})\n  ]});\n}

marker = 'id:"filter-reset",children:"Reset Filters"})\n  ]});\n}'
pos = bak.find(marker)
print(f"Marker found at: {pos}")
if pos != -1:
    end_of_new_vy = pos + len(marker)
    print("End of new_vY:", end_of_new_vy)
    print("Next 200 chars:", repr(bak[end_of_new_vy:end_of_new_vy+200]))
