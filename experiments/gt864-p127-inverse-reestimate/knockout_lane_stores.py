"""Timing knockout: every single-lane st1 in a file becomes a plain str d/str h
to the same address with the same post-increment.  Values are wrong; the
instruction stream and addresses are the same otherwise."""
import re, sys
p = sys.argv[1]; out = []
for l in open(p).read().split('\n'):
    m = re.match(r'(\s*)st1 \{v(\d+)\.([DdHh])\}\[\d\], \[(x\d+)\](?:, (x\d+))?(.*)$', l)
    if m:
        ind, r, sz, base, inc, rest = m.groups()
        out.append(f"{ind}str {'d' if sz in 'Dd' else 'h'}{r}, [{base}]")
        if inc: out.append(f"{ind}add {base}, {base}, {inc}")
        continue
    out.append(l)
open(p, 'w').write('\n'.join(out))
print(p, sum(1 for l in open(p) if re.search(r'st1 \{v\d+\.[DH]\}\[', l)), 'lane stores left')
