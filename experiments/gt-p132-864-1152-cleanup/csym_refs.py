"""P132, second pass of csym.py: every global defined as C_SYM(X) in a tree is
referenced as C_SYM(X) everywhere in that tree's assembly (calls from other
files, SUPPORT macro arguments).  Comments untouched.  usage: csym_refs.py TREE"""
import re, sys, pathlib
T = pathlib.Path(sys.argv[1]); files = sorted(T.glob('*.S'))
G = {m.group(1) for f in files for m in re.finditer(r'\.globa?l\s+C_SYM\((\w+)\)', f.read_text())}
pat = re.compile(r'(?<![\w.(])(' + '|'.join(sorted(G, key=len, reverse=True)) + r')\b(?!\s*\))')
for f in files:
    lines = f.read_text().split('\n'); out = []; n = 0; incom = False
    for l in lines:
        if incom:
            out.append(l); incom = '*/' not in l; continue
        if l.lstrip().startswith(('//', '/*', '*')):
            out.append(l); incom = l.lstrip().startswith('/*') and '*/' not in l; continue
        code, sep, com = l.partition('//')
        new = pat.sub(lambda m: f'C_SYM({m.group(1)})', code)
        n += new != code; out.append(new + sep + com)
    s = '\n'.join(out)
    if n and '#define C_SYM(' not in s:
        s = open(pathlib.Path(__file__).with_name('csym.py')).read().split('DEFINE = """')[1].split('"""')[0] + '\n' + s
    f.write_text(s)
    if n: print(f'{f.name}: {n} lines')
