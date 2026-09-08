with open('frontend/dist/assets/index-DJ3zwA0y.js.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

target = 'var $9={},Z9={},K9={exports:{}},pY='
pos = bak.find(target)
print('pos of prop-types:', pos)
print('Before pos:', repr(bak[pos-60:pos]))
print('At pos:', repr(bak[pos:pos+80]))
