"""Print an apply_patch payload for the P1 symbolic candidate."""
import sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parent))
from generate import DAG


def build():
    d = DAG()
    x, y, z = [d.load(f"a{i}", "x1", 16 * i) for i in range(3)]
    xy = d.mm(x, y)
    a = d.mm(xy, z)             # a^1
    a2 = d.mm(a, a)
    a4 = d.mm(a2, a2)
    a8 = d.mm(a4, a4)
    a16 = d.mm(a8, a8)
    a17 = d.mm(a16, a)
    a32 = d.mm(a16, a16)
    a64 = d.mm(a32, a32)
    a128 = d.mm(a64, a64)
    a145 = d.mm(a128, a17)
    a273 = d.mm(a145, a128)
    a546 = d.mm(a273, a273)
    a691 = d.mm(a546, a145)
    a1382 = d.mm(a691, a691)
    a2764 = d.mm(a1382, a1382)
    inv = d.mm(a2764, a691)     # a^3455 = a^-1
    invxy = d.mm(inv, z)
    result = [d.mm(invxy, y), d.mm(invxy, x), d.mm(inv, xy)]
    for i, value in enumerate(result):
        d.store(value, "x0", 16 * i)
    return d.lines


lines = [
    ".text",
    ".global binv_inverse3",
    "binv_inverse3:",
    "// P1: shortest 15-multiplication addition chain for exponent 3455.",
    "// live-in: x0 output pointer, x1 input pointer; live-out: pointers unchanged and output memory updated.",
    "// coefficient range: R1 inputs abs <=4000 and nonzero; R1 outputs and every REDC abs <2000.",
    "// reserved physical registers: x18-x30 and sp; public wrapper preserves d8-d15 once per BaseInv.",
    "binv_inverse3_slothy_start:",
] + ["    " + line for line in build()] + [
    "binv_inverse3_slothy_end:",
    "    ret",
    "",
]

print("*** Begin Patch")
print("*** Add File: experiments/gt864-native-asm/baseinv-addition-chain/candidate.sym.S")
for line in lines:
    print("+" + line)
print("*** End Patch")
