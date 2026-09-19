#!/usr/bin/env python3
"""Emit fused producer+route windows in Slothy symbolic form.

A window is a contiguous slice of the P28 producer that contains K output stores,
with each store replaced by the variant-C route chain for that output: the Q stays
in registers, the ternary constants are reloaded from memory instead of being held
live, and delivery is one ST3.
"""
import re, sys
from pathlib import Path

PROD = Path('../gt864-p28-paired-i16/candidate-main.sym.S')
lines = []
for l in PROD.read_text().splitlines():
    s = re.sub(r'//.*', '', l).rstrip()
    t = s.strip()
    if not t or t.startswith(('.', '#')) or t.endswith(':'):
        continue
    lines.append(s)

store_at = [i for i, s in enumerate(lines) if s.strip().startswith('str ')]

def chain(tag, val):
    """Variant-C route chain: no constant stays live across the burst."""
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
        f"    st3 {{V<{val}>.4h, V<{tag}_c1>.4h, V<{tag}_p2>.4h}}, [x2], #24",
    ]

def window(nstores, path):
    end = store_at[nstores - 1]
    start = store_at[0] - 40
    out, k = [], 0
    for i in range(max(0, start), end + 1):
        s = lines[i]
        if s.strip().startswith('str '):
            m = re.search(r'[VQD]<([A-Za-z0-9_]+)>', s)
            out += chain(f"rt{k}", m.group(1)); k += 1
        else:
            out.append(s)
    body = "\n".join(out)
    Path(path).write_text(
        "#ifdef __APPLE__\n#define fused_probe _fused_probe\n#endif\n"
        ".text\n.p2align 4\n.global fused_probe\nfused_probe:\n"
        "fused_start:\n" + body + "\nfused_end:\n    ret\n")
    return len(out), k

for n in (2, 4, 6, 8, 12, 16):
    ln, k = window(n, f"window-{n:02d}.S")
    print(f"  window-{n:02d}.S : {ln:4d} instructions, {k} fused outputs")
