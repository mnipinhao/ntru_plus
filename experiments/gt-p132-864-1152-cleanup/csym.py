"""P132: one symbol spelling in NTRU+864/1152 assembly, as NTRU+768 has (P121):
C_SYM(X), which is _X on Mach-O and X on ELF.  Replaces three styles:
  dual   .global X + .global _X, X: + _X:      -> the _X spelling goes
  alias  #ifdef __APPLE__ / #define X _X / #endif  -> the block goes
  C()    #define C(name) _##name ...             -> renamed to C_SYM
Every code use of a converted name becomes C_SYM(X); comments are untouched.
Verified by codehash.sh.  usage: csym.py FILE..."""
import re, sys
DEFINE = """#ifndef C_SYM
#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#else
#define C_SYM(sym) sym
#endif
#endif
"""
for p in sys.argv[1:]:
    s = open(p).read(); names = set()
    # alias blocks
    def alias_block(m):
        body = m.group(1)
        defs = re.findall(r'#define\s+([A-Za-z_]\w*)\s+_\1\s*\n', body)
        rest = re.sub(r'#define\s+([A-Za-z_]\w*)\s+_\1\s*\n', '', body)
        if defs and not rest.strip():
            names.update(defs); return ''
        return m.group(0)
    s = re.sub(r'#ifdef __APPLE__\n((?:#define[^\n]*\n)+)#endif\n', alias_block, s)
    # C() macro block
    s, nC = re.subn(r'#ifdef __APPLE__\n#define C\(name\) _##name\n#else\n#define C\(name\) name\n#endif\n', '', s)
    if nC: s = re.sub(r'(?<![\w.])C\(', 'C_SYM(', s)
    # dual spellings
    lines = s.split('\n')
    dual = {m.group(1) for l in lines for m in [re.match(r'\s*\.globa?l\s+_([A-Za-z]\w*)\s*$', l)] if m}
    dual = {x for x in dual if any(re.match(r'\s*\.globa?l\s+' + x + r'\s*$', l) for l in lines)}
    lines = [l for l in lines if not re.match(r'\s*\.globa?l\s+_(' + '|'.join(dual) + r')\s*$', l)] if dual else lines
    lines = [l for l in lines if not re.match(r'\s*_(' + '|'.join(dual) + r'):\s*$', l)] if dual else lines
    names |= dual
    # rewrite code uses (outside // and /* */ comments)
    out, incom = [], False
    pat = re.compile(r'(?<![\w.])(' + '|'.join(sorted(names, key=len, reverse=True)) + r')\b') if names else None
    for l in lines:
        if pat is None: out.append(l); continue
        code, com = l, ''
        if incom:
            if '*/' in l: i = l.index('*/') + 2; com, code, incom = l[:i], l[i:], False
            else: out.append(l); continue
        if '/*' in code and '*/' not in code[code.index('/*'):]:
            i = code.index('/*'); code, com2 = code[:i], code[i:]; incom = True
        else: com2 = ''
        if '//' in code: i = code.index('//'); code, com3 = code[:i], code[i:]
        else: com3 = ''
        code = pat.sub(lambda m: f'C_SYM({m.group(1)})', code)
        code = code.replace('C_SYM(C_SYM(', 'C_SYM(').replace('))', ')') if 'C_SYM(C_SYM(' in code else code
        out.append(com + code + com3 + com2)
    s = '\n'.join(out)
    if ('C_SYM(' in s) and '#define C_SYM(' not in s: s = DEFINE + '\n' + s
    open(p, 'w').write(s)
    print(f'{p.split("/")[-1]}: {len(names)} names -> C_SYM' + (' (C() renamed)' if nC else ''))
