"""Timing upper bound: delete every single-lane st1 in a file (keeping its
post-increment), i.e. what one full-vector store per output would leave.
Values are wrong; nothing downstream depends on them for timing."""
import re, sys
p = sys.argv[1]; out = []; n = 0
for l in open(p).read().split('\n'):
    m = re.match(r'(\s*)st1 \{v(\d+)\.([DdHh])\}\[\d\], \[(x\d+)\](?:, (x\d+))?(.*)$', l)
    if m:
        ind, r, sz, base, inc, rest = m.groups(); n += 1
        if inc: out.append(f"{ind}add {base}, {base}, {inc}")
        continue
    out.append(l)
open(p, 'w').write('\n'.join(out)); print(p, n, 'lane stores dropped')
