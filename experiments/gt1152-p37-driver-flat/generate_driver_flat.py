"""Flatten invntt_ternary_asm's two loop nests into straight-line call sites.

P36 measured the driver skeleton at 275 of the inverse's 6,220 cycles, and it
is the only item in that transform that is plain waste rather than a price paid
for the decomposition.  Per `packed_i9` call the shipped driver issues

    mov x8, #8      ; madd x1, x26, x8, x1
    mov x8, #1152   ; madd x2, x26, x8, x2
    mov x8, #64     ; madd x2, x28, x8, x2
    mov x8, #576    ; madd x3, x26, x8, x3
    mov x8, #288    ; madd x3, x28, x8, x3

-- five loop-invariant constants reloaded on each of sixteen iterations, into
chained three-cycle `madd`s, in a nest whose strides are fixed at assembly
time.  Because the nest is only 2 x 4 x 2 and 4 x 2, every call site's four
pointers are a base register plus a constant that fits an `add` immediate
(largest is 2190, the limit is 4095), so the whole nest becomes

    add x0, x25, #K0
    add x1, x25, #K1
    add x2, x20, #K2
    add x3, x21, #K3
    bl  C(packed_i9)

The constants are not transcribed.  They are computed here from the same index
algebra the shipped driver evaluates at run time, and `verify_constants.py`
checks them against an independent simulation of that arithmetic.

Loop order is preserved (top, component, block; then component, half) so the
sequence of calls -- and therefore every kernel's view of the scratch -- is
byte-for-byte what it was.  The call sites are provably independent anyway:
their 128 tail-region halfword slots are distinct and exactly fill bytes
2048..2303 of the scratch.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "gt1152-p10-kem/inverse_ntt.S"

# ---- the two nests, exactly as the shipped driver writes them ---------------

NEST_I9 = """    mov x26, #0                // top
.Lp8inv_top:
    mov x27, #0                // component
.Lp8inv_component:
    mov x28, #0                // eight-column block
.Lp8inv_i9:
    add x0, x25, x27, lsl #9
    add x0, x0, x28, lsl #7
    add x0, x0, x26, lsl #3
    add x1, x25, #2048
    add x1, x1, x28, lsl #7
    mov x8, #8
    madd x1, x26, x8, x1
    add x1, x1, x27, lsl #1
    mov x8, #1152
    madd x2, x26, x8, x20
    mov x8, #64
    madd x2, x28, x8, x2
    add x2, x2, x27, lsl #4
    mov x8, #576
    madd x3, x26, x8, x21
    mov x8, #288
    madd x3, x28, x8, x3
    bl C(packed_i9)
    add x28, x28, #1
    cmp x28, #2
    b.ne .Lp8inv_i9
    add x27, x27, #1
    cmp x27, #4
    b.ne .Lp8inv_component
    add x26, x26, #1
    cmp x26, #2
    b.ne .Lp8inv_top
"""

NEST_MAIN = """    mov x26, #0                // component
.Lp8inv_main_component:
    mov x27, #0                // four-row half
.Lp8inv_main:
    add x0, x19, x26, lsl #1
    mov x8, #32
    madd x0, x27, x8, x0
    add x1, x25, x26, lsl #9
    add x1, x1, x27, lsl #8
    mov x2, #0
    mov x3, x22
    mov x4, x23
    // KEM-only helper: representatives are closed against the ternary consumer.
    bl C(invntt16_asm)
    add x27, x27, #1
    cmp x27, #2
    b.ne .Lp8inv_main
    add x26, x26, #1
    cmp x26, #4
    b.ne .Lp8inv_main_component
"""

# ---- the same index algebra, evaluated here instead of at run time ----------

def sites_i9():
    for top in range(2):                       # x26, outer
        for comp in range(4):                  # x27
            for blk in range(2):               # x28, inner
                yield dict(
                    top=top, comp=comp, blk=blk,
                    x0=(comp << 9) + (blk << 7) + (top << 3),   # scratch
                    x1=2048 + (blk << 7) + top * 8 + (comp << 1),
                    x2=top * 1152 + blk * 64 + (comp << 4),     # in
                    x3=top * 576 + blk * 288)                   # invntt9 tables

def sites_main():
    for comp in range(4):                      # x26, outer
        for half in range(2):                  # x27, inner
            yield dict(comp=comp, half=half,
                       x0=(comp << 1) + half * 32,              # out
                       x1=(comp << 9) + (half << 8))            # scratch

IMM_MAX = 4095

def add_imm(dst, base, k, what):
    if not 0 <= k <= IMM_MAX:
        raise SystemExit(f"{what}: offset {k} outside the add immediate range")
    return f"    add {dst}, {base}, #{k}" if k else f"    mov {dst}, {base}"


def emit_i9(sites):
    out = ["    // packed_i9, sixteen straight-line call sites."
           "  Loop order is (top, component, block),",
           "    // the same order the nest ran in.  Bases: x25 scratch, x20 in,"
           " x21 invntt9 tables."]
    for s in sites:
        out.append(f"    // top {s['top']}, component {s['comp']}, block {s['blk']}")
        out.append(add_imm("x0", "x25", s["x0"], "i9 x0"))
        out.append(add_imm("x1", "x25", s["x1"], "i9 x1"))
        out.append(add_imm("x2", "x20", s["x2"], "i9 x2"))
        out.append(add_imm("x3", "x21", s["x3"], "i9 x3"))
        out.append("    bl C(packed_i9)")
    return "\n".join(out) + "\n"


def emit_main(sites):
    out = ["    // invntt16_asm, eight straight-line call sites, order (component, half).",
           "    // KEM-only helper: representatives are closed against the ternary consumer."]
    for s in sites:
        out.append(f"    // component {s['comp']}, half {s['half']}")
        out.append(add_imm("x0", "x19", s["x0"], "main x0"))
        out.append(add_imm("x1", "x25", s["x1"], "main x1"))
        out.append("    mov x2, #0")
        out.append("    mov x3, x22")
        out.append("    mov x4, x23")
        out.append("    bl C(invntt16_asm)")
    return "\n".join(out) + "\n"


def main():
    text = SRC.read_text()
    for name, nest in (("packed_i9 nest", NEST_I9), ("invntt16 nest", NEST_MAIN)):
        n = text.count(nest)
        if n != 1:
            raise SystemExit(f"anchor drift for the {name}: found {n}, expected 1")

    i9, mn = list(sites_i9()), list(sites_main())
    assert len(i9) == 16 and len(mn) == 8

    flat = text.replace(NEST_I9, emit_i9(i9)).replace(NEST_MAIN, emit_main(mn))

    # No loop counter may survive; x26-x28 are now unused in the body.
    body = flat.split(".global C(invntt_ternary_asm)")[1]
    for lbl in (".Lp8inv_top", ".Lp8inv_component", ".Lp8inv_i9",
                ".Lp8inv_main_component", ".Lp8inv_main"):
        if lbl in body:
            raise SystemExit(f"{lbl} survived the flattening")
    if re.search(r'\bmadd\b', body):
        raise SystemExit("a madd survived the flattening")

    flat = flat.replace(
        " * Generated by generate_driver.py from NTRU+864's inverse.S; do not edit.",
        " * Generated by gt1152-p37-driver-flat/generate_driver_flat.py from the\n"
        " * p07 loop-nest driver; do not edit.  P36 measured the nest's address\n"
        " * arithmetic at 275 cycles: five loop-invariant constants reloaded into\n"
        " * chained madds on each of sixteen iterations.  The nest is 2x4x2 and\n"
        " * 4x2, so every call site's pointers are a base plus a constant that\n"
        " * fits an add immediate, and the loops are gone.")

    (HERE / "inverse_ntt.S").write_text(flat)
    (HERE / "call-sites.json").write_text(json.dumps(
        {"packed_i9": i9, "invntt16_asm": mn}, indent=2) + "\n")
    n_static = sum(1 for l in flat.splitlines() if re.match(r'^\s+[a-z]', l))
    print(f"wrote inverse_ntt.S: {len(i9)} + {len(mn)} call sites, "
          f"{n_static} instructions (was "
          f"{sum(1 for l in text.splitlines() if re.match(r'^\s+[a-z]', l))})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
