# Results

`make check` passes 49 boundary, impulse, and deterministic randomized FR-0
cases within M5C's `[-2168,2168]` contract. Pass 1 and pass 2 match M5D
coefficientwise modulo q with zero mismatches. The new reduction deliberately
chooses different noncanonical representatives in 385 pass-1 and 673 pass-2
comparisons. Sentinel checks report zero writes to the 32 P8 tail-padding
coefficients.

The fixed-multiply proof exhausts all 65,536 signed halfword inputs for 270
distinct constants: 17,694,720 congruence checks, zero failures, and maximum
output magnitude 3444. The derived inverse bound peaks at 17,220 during NTT16
and gives a final output bound 6888; the observed maximum is 3568.

The disassembly audit reports:

- zero stack references, branches, `v8-v15` references, or coefficient spills
  in all three arithmetic blocks;
- 297 instructions / 1,188 bytes for inverse NTT9;
- 811 instructions / 3,244 bytes for main inverse NTT16;
- 715 instructions / 2,860 bytes for tail inverse NTT16;
- 7,292 total assembly bytes, down 32.1% from initial M5E;
- 197 exact `mul/sqrdmulh/mls` triplets and zero widening-Montgomery instructions;
- two meaningful 1,728-byte input/output boundaries and no top scratch.

The feature scanner reports no optional AArch64 features and the
secret-independence scanner reports zero warnings. The conservative Neon
pattern scanner reports 28 cross-lane/transpose, six lane
extract/insert/broadcast, and 21 rounding-high-multiply sites. The last group is
covered by the exhaustive Algorithm-10 proof; the others are public-layout
operations, not secret-dependent indices, and remain part of measured cost.

Three same-binary local M5E-r1 runs (31 samples, 2,000 iterations per sample)
give
median-of-medians in nanoseconds:

| Component | M5D intrinsic | M5E assembly | Change |
| --- | ---: | ---: | ---: |
| pass 1 | 380.854 | 199.771 | -47.5% |
| pass 2 | 680.792 | 342.708 | -49.7% |
| combined | 1065.938 | 545.354 | -48.8% |

Against the initial M5E assembly's recorded 919.750 ns combined median, r1 is
40.7% lower. This joint number includes both the arithmetic replacement and
the independent grouping; no Slothy scheduling claim is made.

This diagnostic establishes a local direction only. It is not target-host
PMU attribution, full Forward/KEM, or SUPERCOP evidence.
