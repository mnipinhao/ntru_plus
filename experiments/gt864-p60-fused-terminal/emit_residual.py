#!/usr/bin/env python3
"""Residual delivery for the (top,t) groups the producers could not fuse.

Standalone, so registers are plentiful: the four ternary constants stay resident
in v20-v23 instead of being reloaded per burst.

ABI: x0 natural output base, x1 scratch base, x4 composite table (+constants).
"""
import json
from pathlib import Path
D = json.load(open('deferred.json'))['bank0']
CONST = 1024
BASE = {'b0': (0, 512), 'b1': (256, 768), 'b2': (1024, 1280)}

L = ["#ifdef __APPLE__", "#define p60_residual _p60_residual", "#endif",
     ".text", ".p2align 4", ".global p60_residual", "p60_residual:",
     "p60_residual_slothy_start:"]
E = L.append
E(f"        ldr q20, [x4, #{CONST}]")
E(f"        ldr q21, [x4, #{CONST+16}]")
E(f"        ldr q22, [x4, #{CONST+32}]")
E(f"        ldr q23, [x4, #{CONST+48}]")

def norm(v):
    return [f"        cmgt v16.8h, v{v}.8h, v20.8h",
            f"        cmgt v17.8h, v21.8h, v{v}.8h",
            f"        add v{v}.8h, v{v}.8h, v16.8h",
            f"        sub v{v}.8h, v{v}.8h, v17.8h",
            f"        sqrdmulh v16.8h, v{v}.8h, v22.8h",
            f"        mls v{v}.8h, v16.8h, v23.8h"]

for top, t in D:
    o0 = BASE['b0'][top] + 16*t
    o1 = BASE['b1'][top] + 16*t
    o2 = BASE['b2'][top] + 16*t
    base = 864*top + 54*t
    E(f"        // (top {top}, t {t}) -> natural byte {base}")
    E(f"        ldr q0, [x1, #{o0}]")
    E(f"        ldr q4, [x1, #{o1}]")
    E(f"        ldr q2, [x1, #{o2}]")      # bank2 was normalised by its producer
    L.extend(norm(0)); L.extend(norm(4))
    E("        ext v1.16b, v0.16b, v0.16b, #8")
    E("        ext v5.16b, v4.16b, v4.16b, #8")
    E("        ext v6.16b, v2.16b, v2.16b, #8")
    E(f"        add x3, x0, #{base}")
    E("        st3 {v0.4h, v1.4h, v2.4h}, [x3]")
    E(f"        add x3, x0, #{base+24}")
    E("        st3 {v4.4h, v5.4h, v6.4h}, [x3]")
E("p60_residual_slothy_end:")
E("        ret")
E("#if defined(__ELF__)")
E('.section .note.GNU-stack,"",%progbits')
E("#endif")
Path('residual.S').write_text("\n".join(L) + "\n")
n = sum(1 for l in L if l.startswith("        ") and not l.strip().startswith("//"))
print(f"  residual.S: {len(D)} groups, {n} instructions "
      f"(vs p29_main_route's 873 for all 32)")
