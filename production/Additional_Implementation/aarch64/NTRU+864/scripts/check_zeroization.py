#!/usr/bin/env python3
"""Static source checks for the NTRU+864 cleanup policy (docs/IMPLEMENTATION.md,
section Cleanup policy)."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def require(path, needles):
    text=(ROOT/path).read_text()
    for n in needles:
        if n not in text: raise SystemExit(f"{path}: missing {n!r}")
# The barrier is the mechanism: it is what stops the clear being removed as a
# dead store.  Pinning it rather than one libc's name for the clear keeps the
# check meaningful on every platform.
require("secure_clear.h",("SECURE_CLEAR_AUDIT_HOOK",
                          '__asm__ volatile("" : : "r"(v) : "memory")',
                          "volatile uint8_t *p"))
require("kem.c",("secure_clear(&f, sizeof f);","secure_clear(&ginv, sizeof ginv);",
                 "secure_clear(msg,sizeof msg);","secure_clear(&m,sizeof m);"))
require("symmetric.c",("secure_clear(data, sizeof data);",))
# The decapsulation inverse's scratch lives in kem.c's io union, which is
# cleared as a whole; the static assert keeps the union covering the scratch.
require("kem.c", ("poly_invntt_ternary(&m, &m, io.invntt);",
                  "secure_clear(&io,sizeof io);",
                  "sizeof io.b >= sizeof io.invntt"))
# Released by design, as in Official: sk decode status and keygen's retry.
require("kem.c", ("declassify_poly_frombytes(&f,sk)",
                  "declassify_poly_frombytes(&hinv,sk+NTRUPLUS_POLYBYTES)",
                  "ntruplus_declassify(&r, sizeof r);"))
# Assembly working frames are not wiped.  What is pinned is what the policy
# keeps: the leaves allocate nothing the caller cannot name, and the volatile
# SIMD registers are erased, which costs a cycle and covers state no later work
# overwrites.
require("ntt.S", ("mov x21, x2",))
require("api_glue.c", ("int16_t scratch[896];",))
require("inverse.S",("movi v8.16b, #0","movi v31.16b, #0"))
print("NTRU+864 zeroization source coverage: ok")
