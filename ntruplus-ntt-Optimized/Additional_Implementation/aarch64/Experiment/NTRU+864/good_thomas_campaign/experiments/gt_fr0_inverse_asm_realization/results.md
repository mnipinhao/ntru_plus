# Results

`make check` passes 49 boundary, impulse, and deterministic randomized FR-0
cases within M5C's `[-2168,2168]` contract. Pass 1 and pass 2 match M5D
coefficient-for-coefficient, including noncanonical representatives; both
exact mismatch counts are zero. Sentinel checks report zero writes to the 32
P8 tail-padding coefficients.

The disassembly audit reports:

- zero stack references, branches, `v8-v15` references, or coefficient spills
  in all three arithmetic blocks;
- 436 instructions / 1,744 bytes for inverse NTT9;
- 1,173 instructions / 4,692 bytes for main inverse NTT16;
- 1,077 instructions / 4,308 bytes for tail inverse NTT16;
- 10,744 total assembly bytes;
- two meaningful 1,728-byte input/output boundaries and no top scratch.

The feature scanner reports no optional AArch64 features and the
secret-independence scanner reports zero warnings. The conservative Neon
pattern scanner reports 30 cross-lane/transpose and 19 lane
extract/insert/broadcast sites. These are expected public-layout operations,
not secret-dependent indices; they remain part of the measured store/shuffle
cost.

Three same-binary local runs (31 samples, 2,000 iterations per sample) give
median-of-medians in nanoseconds:

| Component | M5D intrinsic | M5E assembly | Change |
| --- | ---: | ---: | ---: |
| pass 1 | 402.292 | 348.708 | -13.3% |
| pass 2 | 695.271 | 580.375 | -16.5% |
| combined | 1077.271 | 919.750 | -14.6% |

This diagnostic establishes a local direction only. It is not target-host
PMU attribution, full Forward/KEM, or SUPERCOP evidence.
