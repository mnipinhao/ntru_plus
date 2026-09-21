#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def require(path, needles):
    text=(ROOT/path).read_text()
    for n in needles:
        if n not in text: raise SystemExit(f"{path}: missing {n!r}")
# The barrier is the mechanism: it is what stops the clear being removed as a
# dead store.  Pinning it rather than one libc's name for the clear keeps the
# gate meaningful on every platform.
require("secure_clear.h",("SECURE_CLEAR_AUDIT_HOOK",
                          '__asm__ volatile("" : : "r"(v) : "memory")',
                          "volatile uint8_t *p"))
require("kem.c",("secure_clear(&f, sizeof f);","secure_clear(&ginv, sizeof ginv);",
                 "secure_clear(msg,sizeof msg);","secure_clear(&m,sizeof m);"))
require("symmetric.c",("secure_clear(data, sizeof data);",))
# Official-aligned cleanup, as NTRU+768 adopted: assembly working frames are
# not wiped.  What is pinned is what survives that policy -- the leaves allocate
# nothing the caller cannot name, and the volatile SIMD registers are still
# erased, which costs a cycle and covers state no later work overwrites.
require("ntt.S", ("mov x21, x2",))
require("ntt_api.c", ("int16_t scratch[896];",))
require("inverse.S",("movi v8.16b, #0","movi v31.16b, #0"))
for f in ("inverse.S", "ntt.S"):
    t=(ROOT/f).read_text()
    for retired in (".Lbinv_zero_scratch", ".Lp13inv_wipe", ".Lp0b_clear_1792"):
        if retired in t: raise SystemExit(f"{f}: retired frame wipe {retired} is back")
print("production zeroization source coverage: ok")
