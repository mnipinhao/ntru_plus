#!/usr/bin/env python3
"""Generate the six-independent-bank physical-register P51 candidate."""

from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "candidate-equal-wide.S"
REGS = ((1, 2, 3, 4), (7, 8, 9, 10), (11, 12, 13, 14),
        (15, 16, 17, 18), (19, 20, 21, 22), (23, 24, 25, 26))
ACCS = (0, 5, 6, 0, 5, 6)


def main() -> None:
    body = []
    for index, ((a, b, c, d), acc) in enumerate(zip(REGS, ACCS)):
        body += [
            f"    /* Bank {index}: independent registers expose cross-bank ILP. */",
            f"    ldp q{a}, q{b}, [x0], #32",
            f"    ldp q{c}, q{d}, [x1], #32",
            f"    sub v{a}.8h, v{a}.8h, v{c}.8h",
            f"    sub v{b}.8h, v{b}.8h, v{d}.8h",
            f"    sqrdmulh v{c}.8h, v{a}.8h, v31.8h",
            f"    sqrdmulh v{d}.8h, v{b}.8h, v31.8h",
            f"    mls v{a}.8h, v{c}.8h, v30.8h",
            f"    mls v{b}.8h, v{d}.8h, v30.8h",
            f"    orr v{acc}.16b, v{acc}.16b, v{a}.16b",
            f"    orr v{acc}.16b, v{acc}.16b, v{b}.16b",
            "",
        ]
    wipe = [f"    movi v{reg}.16b, #0" for reg in range(27)]
    text = """/* P51 wide-register timing candidate: FR0 equality modulo q=3457. */
#ifdef __APPLE__
#define C(name) _##name
#else
#define C(name) name
#endif

.text
.p2align 4
.global C(gt864_fr0_equal_modq_asm)
C(gt864_fr0_equal_modq_asm):
    mov w8, #3457
    dup v30.8h, w8
    mov w8, #9
    dup v31.8h, w8
    movi v0.16b, #0
    movi v5.16b, #0
    movi v6.16b, #0
    mov w8, #9

.p2align 4
.Lp51_loop:
p51_loop_slothy_start:
""" + "\n".join(body) + """p51_loop_slothy_end:
    subs w8, w8, #1
    b.ne .Lp51_loop

    orr v0.16b, v0.16b, v5.16b
    orr v0.16b, v0.16b, v6.16b
    umaxv h0, v0.8h
    umov w0, v0.h[0]
    cmp w0, #0
    cset w0, ne

    /* Erase every vector which held a secret difference or residue. */
""" + "\n".join(wipe) + """
    movi v30.16b, #0
    movi v31.16b, #0
    ret
"""
    OUT.write_text(text)


if __name__ == "__main__":
    main()
