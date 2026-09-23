"""P132: make every non-global named label in a tree's assembly assembler-local
(.L prefix), and delete labels nothing references (Slothy region markers and
the like).  Global means named by .global, directly, through C(...), or through
a `#define name _name` alias.  Labels inside macros (containing a backslash)
are left alone.  Verified by codehash.sh: the code bytes do not change.
usage: labels.py FILE...   (not for the Keccak files, which are shared with NTRU+768)"""
import re, sys
for p in sys.argv[1:]:
    s = open(p).read()
    nocomment = re.sub(r'/\*.*?\*/', lambda m: '\n' * m.group(0).count('\n'), s, flags=re.S)
    lines = nocomment.split('\n')          # labels and uses are looked for outside /* */ only
    glob = set()
    for l in lines:
        for m in re.finditer(r'\.globa?l\s+(?:C\(|C_SYM\()?_?([A-Za-z_][A-Za-z0-9_]*)', l): glob.add(m.group(1))
        m = re.match(r'#define\s+([A-Za-z_][A-Za-z0-9_]*)\s+_\1\b', l)
        if m: glob.add(m.group(1))
    labels = [m.group(1) for l in lines for m in [re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*):\s*(//.*)?$', l)] if m]
    local = [x for x in labels if x.lstrip('_') not in glob and not x.startswith('L')]
    code = '\n'.join(l for l in lines if not re.match(r'^\s*[A-Za-z_][A-Za-z0-9_]*:\s*(//.*)?$', l))
    renamed = deleted = 0
    src = s.split('\n'); mask = nocomment.split('\n')   # same line count
    for x in sorted(set(local), key=len, reverse=True):
        pat = re.compile(r'(?<![\w.])' + re.escape(x) + r'\b')
        used = pat.search(code)
        for i, (l, m) in enumerate(zip(src, mask)):
            if not pat.search(m) or l.lstrip().startswith('//'): continue
            if used: src[i] = pat.sub('.L' + x, l)
            elif re.match(r'^\s*' + re.escape(x) + r':\s*(//.*)?$', l): src[i] = None
        if used: print('   local:', x); renamed += 1
        else: deleted += 1
    s = '\n'.join(l for l in src if l is not None)
    open(p, 'w').write(s)
    print(f'{p.split("/")[-1]}: {renamed} labels made local, {deleted} unreferenced labels deleted')
