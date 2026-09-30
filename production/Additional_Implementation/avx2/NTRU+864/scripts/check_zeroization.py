#!/usr/bin/env python3
"""Static gate for the Official-aligned cleanup policy (docs/IMPLEMENTATION.md, section 8).

The package clears the same C buffers as Official NTRU+ AVX2 (and as the
AArch64 production packages' lower-clear policy): every secret stack buffer
and polynomial of kem.c, the batch-inversion scratch of baseinv.c, the
prefixed hash inputs of hash_g/hash_h, and the SHAKE state (mlkem-native
mlk_zeroize).  Assembly spill slots and caller-saved registers are not wiped;
the one kernel with stack spills (basemul_shoup.s) is pinned below so that a
change to its frame is noticed.  make zeroization additionally audits the
cleared bytes at run time.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def require(relative, needles):
    text = (ROOT / relative).read_text()
    for needle in needles:
        if needle not in text:
            raise SystemExit(f"{relative}: missing {needle!r}")
    return text


require("util.h", ("explicit_bzero(v, len);", "NTRUPLUS_SECURE_CLEAR_AUDIT_HOOK",
                   "secure_clear_audit_hook(v, audit_len);"))
kem = require("kem.c", (
    # keygen
    "secure_clear(&h, sizeof h);",
    "secure_clear(coins, sizeof coins);", "secure_clear(buf, sizeof buf);",
    "secure_clear(&f, sizeof f);", "secure_clear(&finv, sizeof finv);",
    "secure_clear(&g, sizeof g);", "secure_clear(&ginv, sizeof ginv);",
    # encap (derand + wrapper), including the invalid-pk path
    "secure_clear(msg, sizeof msg);", "secure_clear(&r, sizeof r);",
    "secure_clear(&m, sizeof m);", "secure_clear(ss, NTRUPLUS_SSBYTES);",
    # decap: every exit goes through cleanup
    "cleanup:", "secure_clear(buf1, sizeof buf1);", "secure_clear(buf2, sizeof buf2);",
    "secure_clear(buf3, sizeof buf3);", "secure_clear(&c, sizeof c);",
    "secure_clear(&hinv, sizeof hinv);"))
if kem.count("secure_clear(") != 22:
    raise SystemExit(f"kem.c: expected 22 secure_clear sites, found {kem.count('secure_clear(')}")
dec = kem[kem.index("int crypto_kem_dec("):]
if dec.count("return") != 1:
    raise SystemExit("kem.c: crypto_kem_dec must leave through its cleanup block only")
require("baseinv.c", ("secure_clear(pc, sizeof pc);", "secure_clear(R, sizeof R);",
                      "secure_clear(den, sizeof den);"))
sym = require("symmetric.c", ("secure_clear(data, sizeof data);",))
g = sym[sym.index("void hash_g"):sym.index("void hash_h")]
h = sym[sym.index("void hash_h"):]
if "secure_clear(data, sizeof data);" not in g or "secure_clear(data, sizeof data);" not in h:
    raise SystemExit("symmetric.c: hash_g and hash_h must clear their prefixed input copy")
# hash_f hashes the public key: no clear (Official).
fips = require("fips202.c", ("mlk_zeroize(&state, sizeof(state));",))
# mlk_zeroize itself is the package's: memset, then the compiler barrier.
require("mlkem_native_config.h", ("memset(ptr, 0, len);", '__asm__ volatile("" : : "r"(ptr) : "memory");'))
start = fips.index("void mlk_shake256(")
shake = fips[start:fips.index("\n}\n", start)]
if "mlk_zeroize(&state, sizeof(state));" not in shake:
    raise SystemExit("fips202.c: mlk_shake256 must zeroize its state")
# The Shoup kernel's frame (gcc spills): pinned, not wiped (policy above).
shoup = (ROOT / "basemul_shoup.s").read_text()
slots = sorted(set(re.findall(r"(-?\d+)\(%rsp\)", shoup)), key=int)
if slots != ["-64", "-32"]:
    raise SystemExit(f"basemul_shoup.s: stack slots changed to {slots}; re-audit the cleanup policy")
print("zeroization-source-check: Official-aligned C clear sites present; "
      f"basemul_shoup.s spill slots {slots} (%rsp offsets) documented, not wiped")
