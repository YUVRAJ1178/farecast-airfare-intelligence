with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

marker = 't.createElement("link").relList;'
pos = bundle.find(marker)
if pos != -1:
    clean = '(function(){const se=document.createElement("link").relList;' + bundle[pos + len(marker):]
    print('Clean start:', repr(clean[:80]))
    with open('frontend/dist/assets/index-DJ3zwA0y.js', 'w', encoding='utf-8') as f:
        f.write(clean)
    print('Clean file written, length:', len(clean))
