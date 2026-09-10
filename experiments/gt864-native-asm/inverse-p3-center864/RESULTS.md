# P3-A — constant-resident complete inverse centering

P3-A changes only the final normalization boundary of `gt864_native_inverse`.
The P2 baseline calls a 46-instruction `center32` leaf 27 times.  Each call
recreates `q=3457`, Barrett reciprocal `9`, and `halfq=1728`, and the wrapper
pays 27 calls plus its own loop.  P3-A uses one `center864` call whose public
27-iteration loop keeps those three vectors resident.

The arithmetic per coefficient is unchanged: Barrett reduction followed by
branchless correction to `[-1728,1728]`.  Input remains natural-order R0 with
the closed Inverse producer bound `abs <= 6912`; output remains natural-order,
centered R0.  The kernel reads and writes exactly 1,728 bytes in place.

## Static and correctness gates

- Fixed allocation: constants `v0-v2`, data `v3-v6`, temporaries `v7-v10`.
- Slothy Cortex-A76 timing schedule: 40 instructions and 37 modeled cycles per
  64-byte iteration, zero spill, all overlapping loads before stores.
- Differential oracle: every scalar value in `[-6912,6912]`, 4,096 random
  864-coefficient vectors, and input/output canaries passed.
- Pi 5: six repetitions each passed 24 valid KEM cases, 24 tampered cases, 256
  exact Inverse comparisons, and 256 exact-alias Inverse comparisons.  Both
  isolated packages passed `manifest-check`, `test_kem`, and 100-case KAT.

## Paired Pi 5 PMU versus production P2

| Boundary | P2 cycles | P3-A cycles | Delta | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Inverse | 7230.391 | 7017.531 | -212.859 (-2.94%) | -235 | -52 |
| Decaps | 44206.275 | 43994.000 | -212.275 (-0.48%) | -235 | -52 |
| Keygen | 46482.375 | 46488.750 | +6.375 noise | 0 | 0 |
| Encaps | 45999.225 | 45996.950 | -2.275 noise | 0 | 0 |

The exact instruction/branch delta propagates one-for-one from Inverse to
Decaps, while non-consumers are unchanged.  P3-A is therefore promoted.
P3 remains active: P3-B will test whether the I16/tail producers can emit
centered values directly and remove the separate 1,728-byte reread/rewrite.
