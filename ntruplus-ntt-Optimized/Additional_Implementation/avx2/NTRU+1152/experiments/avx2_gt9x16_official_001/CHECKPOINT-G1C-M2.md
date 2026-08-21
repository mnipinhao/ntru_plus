# Checkpoint G1C-M2: live BMScale boundary credit

G1C-M2 audits every live value in the actual BMScale tail, builds an exact
materialized control, and prices the already-correct linked C2-L edge. It does
not alter Official BMScale arithmetic and does not measure SUPERCOP or a KEM.

## Live-basis result

`generated/g1c-m2-live-basis.json` is source-locked to the assembly fragments.
The early live set contains `c0`, `c1`, `c2`, and the four inputs needed to
finish `c3`; the late set contains the `c3` partial products and final sums.
Every BMScale tail operation is lane-separable. The inverse distance-1 relation
pairs adjacent physical q lanes inside each `c_j`; it does not pair terminal
coefficients `c0/c1` or `c2/c3`. Consequently, no earlier live intermediate
already contains the required adjacent-lane mix.

Under the current interleaved ABI and allowed AVX2 primitives, one canonical
`c_j` vector needs one adjacent-lane mix, two sum/difference forms, four
Montgomery-twist instructions, and one blend: eight instructions per vector,
32 per row. C2-L realizes this scoped bound. Distributing D1 into earlier
partial products duplicates the lane mix and linear/Montgomery chains, so that
candidate is rejected for a head-only leaf.

The retained full-inverse candidate is split-after-D1. It omits the final
blend and costs seven instructions per vector before storage, but doubles the
live vectors and would require eight stores per row if materialized. It is only
credible when distance 2/4/8 consume that split state in the same leaf or absorb
its packing cost.

## Exact control and correctness

The M2 control executes the identical BMScale instruction order, writes all 72
raw result vectors, reloads them, executes the identical D1 arithmetic, and
overwrites the boundary with 72 post-D1 vectors. C2-L writes only the 72
post-D1 vectors. The static difference is therefore 72 raw stores plus 72 edge
loads, or 144 avoided boundary memory instructions.

Both paths are bit-exact against the independent scalar oracle for 1,003
producer-real cases and all 1,152 cells. Boundary, random, input immutability,
output canary, range, sanitizer, ABI, and constant-time-static gates pass. Both
leaves are straight-line and free of calls, frames, stack references, spills,
and `vzeroupper`.

## Paired diagnostic

On Intel Core Ultra 7 155H CPU 1, nine fresh pinned launches used the same
binary, compiler flags, producer-real input residency, output buffer, 16
balanced ABBA/BAAB blocks, and 96 observations per slot:

| Path | Median cycles |
|---|---:|
| Exact materialized control | 610 |
| Linked C2-L | 588 |
| Candidate minus control | -22 |

All 9/9 launch deltas favor C2-L; the median delta is -22 cycles and the ratio
is 0.9639. The machine-readable record is
`results/g1c-m2-intel155h-20260821-001/g1c-m2-paired.json`.

## Decision

This is a strong edge success and authorizes G1C-M3: compare a complete
materialized/interleaved adjusted inverse16 with a linked split-state leaf that
carries D1 through distances 2, 4, and 8. C2-L remains the head-only control,
and paired-row scheduling remains available if split-state register pressure
requires it. BaseInv normalization is still open and excluded from this gate.

The result does not select F1 or qualify production. F1-B1's 58.5-cycle debt
per forward (117 cycles on a two-forward path) and F5's 22-cycle edge credit
are independent prices; they must not be netted until G2 names a complete path
that contains both. In particular, an F0-forward plus consumer-native BMScale
plus F5-inverse path pays no F1 debt. Official remains the zero-conversion
production baseline; formal decisions still require the pinned SUPERCOP
workflow and KEM evidence.
