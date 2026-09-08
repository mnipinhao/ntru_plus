# BINV-FR0: native leaf inverse, default-off

Production is unchanged. `baseinv.c` reads/writes FR0 directly; 36 tiles of
three vectors, eight cubic leaves per tile. Existing zeta table is z*R.
Input: arbitrary int16 FR0 representatives, normalized at load.
Internal: Montgomery R1; output centered R0. No official layout arrays.
Three independent 12-vector prefix/recovery chains, one vector exponentiation,
then denominator precomputation shared by the three component products.

Two modes: default conservative centered reduction after each product/add;
`-DFR0_LAZY` keeps all multiply operands <=4000 and REDC outputs <2000,
with centered reduction only at input and final output. See proof.py.
Noninvertible input returns 1 and zeroes output. Aliasing is supported.
No leaf-dependent memory addresses; final invertibility decision is the
existing API's secret-dependent failure/retry boundary. This is not a full
binary constant-time/security certification, and scratch zeroization is pending.

Pi5/GCC14.2.0, core3, six paired processes with 41 samples each, same harness
as production. 512 boundary/random tests, 288 individual zero-leaf positions,
in-place alias, cubic product identity and old-BaseInv congruence passed.
All six processes passed valid/tampered/malformed full-KEM differential tests.

| Candidate | Baseline Keygen | Candidate Keygen | Decision |
|---|---:|---:|---|
| Conservative | 54114.500 | 67768.375 | Reject: normalization cost |
| Lazy | 54115.750 | 53201.875 | Keep experimental: -913.875 cycles (-1.69%) |

Lazy Encaps 46090.275 -> 46100.775 and Decaps 44418.925 -> 44424.975;
those callers do not use BaseInv and their arithmetic is unchanged.
Not a production promotion: no new KAT, dedicated ABI-sentinel or full
compiler constant-time audit yet. Not a claim of closing SUPERCOP's BaseInv gap.
The prototype remains intrinsics, not a scheduled asm implementation.

Reproduce in /home/pi/ntruplus-experiments/gt864-fr0-native-baseinv:
`EXTRA_FLAGS=-DFR0_LAZY sh build.sh`; run proof.py locally.
Copy production test/paired.c and ids.h into the isolated directory first.
The script reuses frozen production objects, replacing only the KEM BaseInv call.
