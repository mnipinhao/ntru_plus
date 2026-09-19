#!/usr/bin/env python3
"""Control: the same work as win-NN.S but NOT fused.

The producer keeps its 32 stores; the route runs afterwards as its own block and
reloads what the producer wrote.  Scheduling both under identical Slothy settings
isolates the effect of fusion from the effect of the settings.
"""
import json, re
from pathlib import Path
PROD = Path('../gt864-p28-paired-i16/candidate-main.sym.S')
SYM = re.compile(r'[VQD]<([A-Za-z0-9_]+)>')
lines = []
for l in PROD.read_text().splitlines():
    s = re.sub(r'//.*', '', l).rstrip(); t = s.strip()
    if not t or t.startswith(('.', '#')) or t.endswith(':'): continue
    lines.append(s)
store_at = [i for i, s in enumerate(lines) if s.strip().startswith('str ')]

def defs_uses(s):
    syms = SYM.findall(s)
    if not syms: return set(), set()
    op = s.strip().split()[0].lower()
    if op.startswith(('str','st1','st2','st3','st4','stur')): return set(), set(syms)
    if op in ('mls','mla','smlal','smlal2','ins','sri','sli'): return {syms[0]}, set(syms)
    return {syms[0]}, set(syms[1:])

def route_block(k):
    """Same 12-step chain, but the value is reloaded instead of kept in a register."""
    t = f"u{k}"
    return [
        f"    ldr Q<{t}_v>, [x0, #{16*k}]",
        f"    ldr Q<{t}_hi>, [x4, #0]",
        f"    ldr Q<{t}_lo>, [x4, #16]",
        f"    cmgt V<{t}_ab>.8h, V<{t}_v>.8h, V<{t}_hi>.8h",
        f"    cmgt V<{t}_be>.8h, V<{t}_lo>.8h, V<{t}_v>.8h",
        f"    add V<{t}_v>.8h, V<{t}_v>.8h, V<{t}_ab>.8h",
        f"    sub V<{t}_v>.8h, V<{t}_v>.8h, V<{t}_be>.8h",
        f"    ldr Q<{t}_rs>, [x4, #32]",
        f"    sqrdmulh V<{t}_qt>.8h, V<{t}_v>.8h, V<{t}_rs>.h[0]",
        f"    mls V<{t}_v>.8h, V<{t}_qt>.8h, V<{t}_rs>.h[1]",
        f"    ldr Q<{t}_p2>, [x1, #0]",
        f"    ext V<{t}_c1>.16b, V<{t}_v>.16b, V<{t}_v>.16b, #8",
        f"    add X<{t}_ptr>, x2, #{24*k}",

        f"    st3 {{V<{t}_v>.4h, V<{t}_c1>.4h, V<{t}_p2>.4h}}, [X<{t}_ptr>]",
    ]

def build(nstores, path):
    end, start = store_at[nstores-1], max(0, store_at[0]-40)
    body, defined = [], set()
    for i in range(start, end+1):
        d,_ = defs_uses(lines[i]); defined |= d
        body.append(lines[i])            # producer keeps its stores
    for k in range(nstores):
        body += route_block(k)
    later = set()
    for i in range(end+1, len(lines)):
        _,u = defs_uses(lines[i]); later |= u
    live_out = sorted(defined & later)
    Path(path).write_text(
        "#ifdef __APPLE__\n#define fused_probe _fused_probe\n#endif\n"
        ".text\n.p2align 4\n.global fused_probe\nfused_probe:\n"
        "fused_start:\n" + "\n".join(body) + "\nfused_end:\n    ret\n")
    Path(path.replace('.S','.outputs.json')).write_text(json.dumps(live_out, indent=1))
    return len(body), len(live_out)

for n in (16, 32):
    ln, lo = build(n, f"unfused-{n:02d}.S")
    print(f"  unfused-{n:02d}.S : {ln:4d} instructions, {lo} live-out")
