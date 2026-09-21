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
# ntt.S allocates nothing: its 1792-byte scratch is the caller's, and
# ntt_api.c clears it, which is why this pins the C side instead.
require("ntt.S", ("mov x21, x2",))
require("ntt_api.c", ("int16_t scratch[896];", "secure_clear(scratch, sizeof scratch);"))
require("inverse.S",("movi v8.16b, #0","movi v31.16b, #0"))
print("production zeroization source coverage: ok")
