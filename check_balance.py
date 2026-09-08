with open('frontend/dist/assets/index-DJ3zwA0y.js', 'r', encoding='utf-8') as f:
    bundle = f.read()

def check_balance(code, name):
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    for i, ch in enumerate(code):
        if ch in '({[':
            stack.append((ch, i))
        elif ch in ')}]':
            if not stack:
                print(f'{name}: Unexpected closing {ch} at char {i}')
                return False
            top, pos = stack.pop()
            if pairs[ch] != top:
                print(f'{name}: Mismatched {top} at {pos} with {ch} at {i}')
                return False
    if stack:
        print(f'{name}: Unclosed brackets count: {len(stack)}, first: {stack[0]}')
        return False
    print(f'{name}: Brackets perfectly balanced!')
    return True

vY_start = bundle.find('function vY(')
next_var = bundle.find('var $9={}', vY_start)
check_balance(bundle[vY_start:next_var], 'vY')

zY_start = bundle.find('function zY(')
P7_pos = bundle.find('const P7=', zY_start)
check_balance(bundle[zY_start:P7_pos], 'zY')

YY_start = bundle.find('function YY(')
root_idx = bundle.find('G3.createRoot', YY_start)
check_balance(bundle[YY_start:root_idx], 'YY')

check_balance(bundle, 'FULL BUNDLE')
