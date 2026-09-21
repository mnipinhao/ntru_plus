# P76 — the missing zeroization gate, and the regression it would have caught

NTRU+768 and NTRU+864 have each carried a `scripts/check_zeroization.py` since
the P0 work.  NTRU+1152 never did.  Writing one found that the gap was not
theoretical.

## P68 removed the SIMD register wipe

The pre-P68 driver used a `RESTORE_PUBLIC` macro whose comment reads *"Erase
volatile SIMD state, including high halves of v8-v15"* and which zeroed all
thirty-two vector registers before restoring `d8-d15`.  P68 rewrote the driver
from scratch and gave it a plain `ldp`/`ret` epilogue.  The wipe went with it.

Counting `movi vN.16b, #0` across the assembly:

| | |
|---|---:|
| NTRU+864 production `inverse.S` | 34 |
| NTRU+1152 `inverse_ntt.S`, P68 through P75 | **1** (the wipe loop's zero source) |

Nothing caught it for eight gates:

- `test_zeroization`'s audit hook only fires inside the C primitive, and the
  documentation says so — *"Assembly clearing is checked statically because the
  portable hook cannot intercept stores emitted directly by handwritten
  assembly."*  Its `clear_bytes=34000` never moved.
- `test_abi` checks that callee-saved registers are **preserved**, which is a
  different property from volatile ones being **erased**.  All sentinels read
  `mask=0x00000` before and after.

Restored, and it should never have been dropped: **+1 cycle on A76, +0.0ns on
M2.**

## The gate

`scripts/check_zeroization.py` pins, in the shape 864's uses:

- `secure_clear.h` — the **barrier**, which is the mechanism that stops the
  clear being removed as a dead store, plus the fallback loop and the audit hook
- `kem.c` — key material, coins, messages and derived polynomials on every path
- `symmetric.c`, `fips202.c` — the hash and sponge buffers
- `inverse_ntt.S` — the 2,304-byte scratch wipe loop **and all thirty-two
  register wipes, enumerated rather than sampled**, because P68 removed exactly
  that block

It is wired into `make tests` alongside `check-inplace`, so both static gates
run before any test binary is built.

## The gate was tested by breaking things

A gate that cannot fail is worth nothing, so each regression was reintroduced
and the gate re-run:

| injected regression | result |
|---|---|
| remove the 32 `movi` (reproduces P68) | `missing 'movi v1.16b, #0'`, exit 1 |
| remove the scratch wipe loop | `missing '.Lp68_wipe:'`, exit 1 |
| remove the `secure_clear` barrier | `missing '__asm__ volatile(...)'`, exit 1 |
| all restored | ok |

## Why the scratch wipe is pinned at all

`inverse_ntt.S` is the only assembly leaf in this tree that owns secret-bearing
memory the C caller cannot reach: the Good-Thomas decomposition cannot run in
place (P72 established that `invntt16` blocks it, 72 of 72 cross-call ranges
overlapping), so the driver allocates 2,304 bytes of its own.  `add sp` does not
erase them.  Only that assembly can clear them, which is why the wipe exists and
why a static gate is the only thing that can check it.
