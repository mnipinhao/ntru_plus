# GT9X16-PROD3-AOS-BRANCH0

## Result

One complete branch now executes in place from the existing 1,152-byte
top-split AoS backing to the exact P2-B/MA2 materialized ABI:

```text
top-split branch AoS
-> T0 twist + complete register-resident paper-R2 NTT9 per q-block
-> one AoS NTT9 materialization
-> D8/D4 per physical-P row
-> D2/D1 + coefficient-plane transpose
-> exact MA2 packed-lane formation
-> overwrite the same 1,152-byte backing
```

Top-split, T0, R2, D8/D4/D2/D1 arithmetic, P/Q semantic identities, scale
four, reduction policy, and MA2 itself are unchanged. There is no second
branch, caller, benchmark, wavefront, T1/T2 twist absorption, or MA2 fusion.

## Independent exact oracle

The candidate is compared against the current G0/P2-B branch by running both
terminal pairs and comparing all 576 `int16_t` cells raw. No canonicalization
is allowed. The test passes:

- zero, alternating, and every positive/negative coefficient impulse;
- 4,099 random `[-1,1]` polynomial inputs;
- unaligned-but-`int16_t`-aligned in-place backing;
- prefix and suffix canaries.

This differential exposed and corrected two assumptions that the isolated C1
test could not detect. AoS D2 needs separate lo/hi packed twiddle vectors, and
the 24-route C1 transpose stops at AoS physical-q planes rather than the frozen
MA2 packed-lane order.

## Corrected movement and arithmetic ledger

The linked 8,259-byte leaf has:

| class / one branch | count |
| --- | ---: |
| source loads | 36 |
| NTT9 materialization stores | 36 |
| NTT16 boundary reloads | 36 |
| final MA2 stores | 36 |
| total data loads / stores | 72 / 72 |
| T0 Montgomery chains | 36 |
| paper-R2 Montgomery chains | 40 |
| adjusted NTT16 Montgomery chains | 72 |
| total Montgomery chains | 148 |
| Barrett vectors | 36 |
| routing | 288 |

Routing is 32 per physical-P tile: 24 through D2/D1 and the hierarchical
transpose, plus four `vpshufb` and four `vpermq` operations for exact MA2
packed-lane formation. Therefore the corrected full two-branch projection is
576 routes, not the earlier static 432. Against the 936-route G0/P2-B linked
control, the remaining static routing credit is 360.

The complete-NTT9 q-block schedule keeps all nine data vectors resident across
both radix-3 layers. This reduces the corrected full-forward data projection
to 144 loads and 144 stores after top split, versus 288 and 216 for G0/P2-B.

## ABI, overwrite, and register audit

The leaf has no call, conditional branch, stack frame, stack reference, vector
spill, or `vzeroupper`. It uses all sixteen YMM registers during T0/NTT9 and
peaks at twelve during D8-to-MA2. The function entry and all 199 generated
constant vectors are explicitly `.p2align 5`; data accesses remain `vmovdqu`,
so no stronger caller alignment contract is introduced.

The linked instruction stream proves the in-place last-use rule:

- for each q-block, all nine source rows load before any of its nine NTT9
  destinations store;
- for each physical-P row, all four AoS vectors reload before any of its four
  MA2 plane destinations overwrite the row.

The existing 1,152-byte branch backing is sufficient; extra array storage is
zero.

## Range

The generated proof records cutpoints after T0, NTT9 R1/R2, and every
D8/D4/D2/D1 stage for all nine physical-P rows. It reuses the same arithmetic
representatives and proves all preoperations remain signed-i16 safe. No new
reduction or representative normalization was introduced.

## Decision

Branch0 is machine-feasible and exact, but it is not a performance claim. The
important correction is that exact MA2 materialization costs 32 routes per
tile, while the register-resident two-layer NTT9 removes an additional
materialization relative to the earlier static schedule.

The next review gate is `GT9X16-PROD3-AOS-FULL`: add branch 1 with its own T0
constants and prove the complete 2,304-byte MA2 producer raw-exact. Only after
that full producer closes may the G0/P2-B versus PROD3-AOS SUPERCOP-derived
serious boundary pricing be authorized.
