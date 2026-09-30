#!/usr/bin/env python3
"""Static source checks for the NTRU+1152 cleanup policy (docs/IMPLEMENTATION.md,
section Cleanup policy).

The clears, the declassifications and the SIMD register wipe must be present in
the sources.  The register wipe can only be checked here: test_zeroization's
hook sees only clears made through secure_clear, and test_abi checks that
callee-saved registers are preserved, not that volatile ones are erased.
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
# check meaningful on every platform.
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
# Assembly working frames are not wiped, but no leaf allocates memory the caller
# cannot name: the transforms take their scratch as an argument.
require("ntt.S", ("mov x21, x2",))
require("api_glue.c", ("int16_t scratch[1152];",))
require("symmetric.c", ("secure_clear(data, sizeof data);",))
# The decapsulation inverse's scratch lives in kem.c's io union, which is
# cleared as a whole; the static assert keeps the union covering the scratch.
require("kem.c", ("poly_invntt_ternary(&m, &m, io.invntt);",
                  "secure_clear(&io,sizeof io);",
                  "sizeof io.b >= sizeof io.invntt"))
# Released by design, as in Official: sk decode status and keygen's retry.
require("kem.c", ("declassify_poly_frombytes(&f,sk)",
                  "declassify_poly_frombytes(&hinv,sk+NTRUPLUS_POLYBYTES)",
                  "ntruplus_declassify(&r, sizeof r);"))
# baseinv branches on non-invertibility only after declassifying it.
require("inverse.c", ("ntruplus_declassify(&invertible, sizeof invertible);",))
require("fips202.c", ("secure_clear(s, sizeof s);", "secure_clear(tail, sizeof tail);"))

# The register wipe costs one cycle and covers volatile SIMD state that no later
# work overwrites, unlike a stack frame.  All thirty-two are enumerated, so
# dropping any one of them fails the check.
require("inverse_ntt.S", tuple(f"movi v{n}.16b, #0" for n in range(32)))

print("NTRU+1152 zeroization source coverage: ok")
