# P2 — two-tile BaseInv numerator and SIMD failure aggregation

P2 preserves the public BaseInv ABI, the three-chain denominator layout, exact
input/output alias support, scratch wiping, and the single aggregate failure
branch.  It changes two independent internal costs.

## P2-A

Two adjacent steps in one chain are evaluated by a single 160-instruction
Slothy region.  The second tile uses input/output `+48`, zeta `+16`, and
denominator `+48`; this is already the existing scratch layout.  Both tile DAGs
share q, qinv, R mod q, and the Barrett-Shoup multiplier.  Slothy found a
163-cycle Cortex-A76 schedule using `v0-v31` with no spill.  The wrapper makes
18 calls rather than 36.

## P2-B

The old scalar loop performed 24 `LDRH/CMP/CSET/ORR/SUBS/B.NE` iterations.
The replacement loads three Q vectors, compares every halfword with zero,
OR-reduces the masks, then applies `UMAXV` and `UMOV`.  It reads the same 48
bytes, has no secret-dependent address, visits every lane, and branches only
after aggregation.

## Pi 5 results versus committed P1 (`383a65ac`)

| Candidate | Boundary | P1 cycles | Candidate cycles | Delta | Instructions |
|---|---:|---:|---:|---:|---:|
| P2-A | BaseInv success | 5452.985 | 5290.062 | -162.923 | -396 |
| P2-B | BaseInv success | 5450.422 | 5381.750 | -68.672 | -137 |
| P2-AB | BaseInv success | 5450.860 | 5214.297 | -236.563 (-4.34%) | -533 |
| P2-AB | BaseInv failure | 3598.688 | 3326.094 | -272.594 (-7.57%) | -533 |
| P2-AB | Keygen | 46998.875 | 46503.875 | -495.000 (-1.05%) | -1066 |

Keygen invokes BaseInv twice, hence its exact instruction delta is twice the
per-call delta.  Encaps and Decaps do not invoke BaseInv and show zero
instruction change; their small cycle differences are noise, not P2 benefit.

All four isolated packages produced the same 100-case KAT hash.  The paired
harness also passed 24 deterministic valid KEM cases, 24 tampered-ciphertext
comparisons, modular BaseInv comparison, and the zero-input failure case.
