# Results

Two independent campaigns each used 256 balanced blocks, CPU 1, ASLR enabled,
and four discarded warm-up launches per fixed ELF image. Positive values mean
GT is slower than Official.

| Point | Exact production prefix | Run 1 median (95% CI) | Run 2 median (95% CI) |
|---|---|---:|---:|
| A1 | Decode complete | +25.83 ([+25.23, +26.38]) | +26.77 ([+26.21, +27.38]) |
| A2 | + hash_f and hash_h | +103.35 ([+89.58, +121.13]) | +87.79 ([+76.81, +98.83]) |
| A3 | + CBD(r) | +96.23 ([+88.75, +106.63]) | +89.96 ([+82.21, +100.92]) |
| B1 | + frontend and Forward(r) | +45.85 ([+37.04, +54.71]) | +34.25 ([+21.54, +41.25]) |
| B2 | + r-hat serializer | +85.25 ([+75.46, +93.96]) | +86.27 ([+77.46, +100.42]) |
| B3 | + hash_g | +191.33 ([+174.38, +205.08]) | +198.21 ([+186.42, +206.90]) |
| D | + m path, BaseMul, add; production cleanup | +138.17 ([+121.08, +146.54]) | +131.94 ([+121.67, +140.58]) |
| T0 | same semantic point as D; minimal exit | +154.69 ([+147.00, +166.29]) | +155.48 ([+141.46, +164.35]) |
| T1 | + final ciphertext serializer; minimal exit | +195.98 ([+181.48, +210.46]) | +203.21 ([+187.52, +218.21]) |
| E | complete byte-exact production Encap | +202.50 ([+189.88, +218.29]) | +205.50 ([+190.35, +211.00]) |

## Interpretation

The three coarse frontiers from 049 are now resolved:

1. Decode creates only a modest initial debt. The main Entry-to-A divergence
   appears across the `hash_f`/`hash_h` frontier. CBD does not enlarge it.
2. Forward(r) is a recovery region. The r-hat serializer worsens the frontier
   moderately, and `hash_g` is the largest repeatable worsening in the entire
   map.
3. With the matched minimal exit, the final ciphertext serializer produces a
   clear worsening. T1 and complete E are close in both runs, so cleanup/return
   is not the missing large debt.

These statements describe movement of the cumulative production frontier.
They do not assign the numerical difference between rows to an isolated
component. In particular, the large hash-frontier movements may include hash
body placement, producer-to-hash state, stack/data address, and caller history.

## Decision

Attribution is closed for N5 and B3: both are recovery zones. If optimization
continues, the only high-value target is the exact-production hash-facing
boundary, especially r-hat serialization into `hash_g`. Codec-only rescheduling
is secondary, and cleanup/return tuning is closed.

## Hash implementation audit

The frozen ELFs do not contain different hash algorithms. After normalizing
addresses and call targets, `hash_f`, `hash_g`, and `hash_h` have identical
instruction sequences and identical sizes in Official and GT:

| Symbol | Size | Official VA | GT VA |
|---|---:|---:|---:|
| hash_f | 107 B | 0x5ab0 | 0x8f90 |
| hash_g | 125 B | 0x5b20 | 0x9000 |
| hash_h | 151 B | 0x5ba0 | 0x9080 |
| fips202avx_shake256 | 414 B | 0x72d0 | 0xaf80 |

Thus 050 is not evidence that GT performs extra cryptographic hash work. The
remaining mechanism is an exact-image interaction involving hash code placement
and/or producer-to-hash execution and data state. A future gate must target
that handoff directly; rewriting SHAKE arithmetic is not justified.

## Subsequent correction (051, 052, 052A)

Later gates narrow this interpretation further:

- 051 shows that both Encap Q24 producers require the full reducer in all 48
  packets and all 768 lanes, so stale `lazy10788/highrange12699` names do not
  explain this frontier.
- 052 times the same physical `hash_g` after Official and GT producers and gets
  exactly `GT-Official = 0` TSC over 256 launches. `mfence` and common-copy
  normalization are also neutral. Producer-to-hash execution/data state is
  therefore rejected as the approximately 100-cycle explanation.
- 052A confirms B2/B3 are equal-sized in-place patches and do not relocate any
  earlier prefix or later symbol. However, they exit from different sites and
  are not a matched executable interval. Official and GT also place identical
  hash/SHAKE instruction sequences at substantially different virtual/page
  offsets.

Accordingly, the B2-to-B3 movement must not be called a `hash_g` component cost
or an intrinsic Hash hotspot. The accurate statement is: crossing the hash
checkpoint is the largest cumulative frontier movement in 050, while the only
remaining Hash-related mechanism is production code-address geometry.

Experiment 053 subsequently tests that last mechanism with byte-identical Hash
and SHAKE clones in a 2x2 production-like page-offset factorial. All effects are
only -2 to +2 TSC and the duplicate control is exactly neutral. Hash/SHAKE code
address geometry is therefore also closed. The approximately 100-cycle B2/B3
movement is now classified as non-component cumulative checkpoint behavior and
must not be used as a Hash optimization budget.
## 054 direct serializer-boundary correction

`GT32-SERIALIZER-BOUNDARY-054` replaced cumulative checkpoint subtraction with
a direct same-ELF serializer comparison on the two real Encap producer outputs.
Both Q24 sites are intrinsically about **+20 TSC** slower than Official
`poly_tobytes` (256/256 launches, bootstrap CI `[20,20]`).  Region PMU reports
about +22--25 core cycles per site.

Consequently the two serializers account for only about 40 TSC together.  The
larger B2/B3 and later cumulative movements in this document remain
non-component compositional effects and are not Q24 or Hash optimization
budgets.
