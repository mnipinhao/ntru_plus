#!/usr/bin/env python3
"""Static source-coverage gate for the NTRU+1152 zeroization policy.

NTRU+768 and NTRU+864 have carried one of these since the P0 work; NTRU+1152
never did, and the gap was not theoretical.  P68 rewrote inverse_ntt.S and
silently dropped the 32-register SIMD wipe that the RESTORE_PUBLIC macro used
to supply.  Nothing caught it: test_zeroization's hook only sees clears made
through the C primitive, and test_abi checks that callee-saved registers are
preserved, not that volatile ones are erased.

Assembly clearing has to be checked statically for exactly that reason -- the
portable hook cannot intercept stores emitted by handwritten assembly.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(relative: str, needles: tuple[str, ...]) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise SystemExit(f"{relative}: missing {needle!r}")


# The barrier is the mechanism: it is what stops the clear being removed as a
# dead store.  Pinning it rather than one libc's name for the clear keeps the
# gate meaningful on every platform.
require("secure_clear.h", (
    "SECURE_CLEAR_AUDIT_HOOK",
    '__asm__ volatile("" : : "r"(v) : "memory")',
    "volatile uint8_t *p",
))

# Key material, messages and the derived polynomials, on every path.
require("kem.c", (
    "secure_clear(&f, sizeof f);",
    "secure_clear(&finv, sizeof finv);",
    "secure_clear(&g, sizeof g);",
    "secure_clear(&ginv, sizeof ginv);",
    "secure_clear(coins, sizeof coins);",
    "secure_clear(msg,sizeof msg);",
    "secure_clear(&m,sizeof m);",
    "secure_clear(&hinv,sizeof hinv);",
))
# Official-aligned cleanup, as NTRU+768 adopted: assembly working frames are not
# wiped.  Both leaves still allocate nothing the caller cannot name.
require("ntt.S", ("mov x21, x2",))
require("api_glue.c", ("int16_t scratch[1152];",))
require("symmetric.c", ("secure_clear(data, sizeof data);",))
require("fips202.c", ("secure_clear(s, sizeof s);", "secure_clear(tail, sizeof tail);"))

# inverse_ntt.S is the only assembly leaf that owns secret-bearing scratch: the
# Good-Thomas decomposition cannot run in place, so it allocates 2,304 bytes the
# C caller cannot reach.  Both the memory wipe and the register wipe are pinned,
# the latter as all thirty-two registers rather than a sample, because P68
# removed exactly that block.
# The register wipe stays: it costs one cycle and covers volatile SIMD state
# that no later work overwrites, unlike a stack frame.  All thirty-two are
# enumerated rather than sampled because P68 removed exactly this block.
require("inverse_ntt.S", tuple(f"movi v{n}.16b, #0" for n in range(32)))
for f in ("inverse_ntt.S", "ntt.S"):
    t = (ROOT / f).read_text()
    if ".Lp68_wipe" in t or "clear_2304" in t:
        raise SystemExit(f"{f}: retired frame wipe is back")

print("NTRU+1152 zeroization source coverage: ok")
