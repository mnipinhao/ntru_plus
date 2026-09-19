#!/usr/bin/env python3
"""Emit fused producer+route windows together with their live-out declaration.

A window is a slice of the producer, so Slothy needs to be told which symbolic
values leave it.  Live-out = defined inside the window and still used in the
full producer after the window ends, plus anything the route leaves behind.
"""
import json, re
from pathlib import Path

PROD = Path('../gt864-p28-paired-i16/candidate-main.sym.S')
SYM = re.compile(r'[VQD]<([A-Za-z0-9_]+)>')
lines = []
for l in PROD.read_text().splitlines():
    s = re.sub(r'//.*', '', l).rstrip()
    t = s.strip()
    if not t or t.startswith(('.', '#')) or t.endswith(':'):
        continue
    lines.append(s)
store_at = [i for i, s in enumerate(lines) if s.strip().startswith('str ')]

def defs_uses(s):
    syms = SYM.findall(s)
    if not syms: return set(), set()
    op = s.strip().split()[0].lower()
    if op.startswith(('str', 'st1', 'st2', 'st3', 'st4', 'stur')):
        return set(), set(syms)
    if op in ('mls', 'mla', 'smlal', 'smlal2', 'ins', 'sri', 'sli'):
        return {syms[0]}, set(syms)
    return {syms[0]}, set(syms[1:])

def chain(tag, val):
    return [
        f"    ldr Q<{tag}_hi>, [x4, #0]",
        f"    ldr Q<{tag}_lo>, [x4, #16]",
        f"    cmgt V<{tag}_ab>.8h, V<{val}>.8h, V<{tag}_hi>.8h",
        f"    cmgt V<{tag}_be>.8h, V<{tag}_lo>.8h, V<{val}>.8h",
        f"    add V<{val}>.8h, V<{val}>.8h, V<{tag}_ab>.8h",
        f"    sub V<{val}>.8h, V<{val}>.8h, V<{tag}_be>.8h",
        f"    ldr Q<{tag}_rs>, [x4, #32]",
        f"    sqrdmulh V<{tag}_qt>.8h, V<{val}>.8h, V<{tag}_rs>.h[0]",
        f"    mls V<{val}>.8h, V<{tag}_qt>.8h, V<{tag}_rs>.h[1]",
        f"    ldr Q<{tag}_p2>, [x1, #0]",
        f"    ext V<{tag}_c1>.16b, V<{val}>.16b, V<{val}>.16b, #8",
        f"    add X<{tag}_ptr>, x2, #{24*int(tag[2:])}",

        f"    st3 {{V<{val}>.4h, V<{tag}_c1>.4h, V<{tag}_p2>.4h}}, [X<{tag}_ptr>]",
    ]

def window(nstores, path):
    end   = store_at[nstores - 1]
    start = max(0, store_at[0] - 40)
    body, k, defined = [], 0, set()
    for i in range(start, end + 1):
        s = lines[i]
        d, _ = defs_uses(s)
        defined |= d
        if s.strip().startswith('str '):
            m = SYM.search(s); body += chain(f"rt{k}", m.group(1)); k += 1
        else:
            body.append(s)
    # anything defined in the window and still used later in the full producer
    later = set()
    for i in range(end + 1, len(lines)):
        _, u = defs_uses(lines[i]); later |= u
    live_out = sorted(defined & later)
    Path(path).write_text(
        "#ifdef __APPLE__\n#define fused_probe _fused_probe\n#endif\n"
        ".text\n.p2align 4\n.global fused_probe\nfused_probe:\n"
        "fused_start:\n" + "\n".join(body) + "\nfused_end:\n    ret\n")
    Path(path.replace('.S', '.outputs.json')).write_text(json.dumps(live_out, indent=1))
    return len(body), k, len(live_out)

for n in (4, 8, 16, 32):
    ln, k, lo = window(n, f"win-{n:02d}.S")
    print(f"  win-{n:02d}.S : {ln:4d} instructions, {k:2d} fused outputs, {lo:2d} live-out values")
