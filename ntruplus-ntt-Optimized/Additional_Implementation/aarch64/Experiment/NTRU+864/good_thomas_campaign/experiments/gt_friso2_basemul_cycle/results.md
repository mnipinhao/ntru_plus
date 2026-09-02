# Results

Status: **passed as an isolated experimental BaseMul candidate.**

- Local: 73 boundary/random cases for staged/direct BaseMul and BaseMulAdd,
  direct BaseMul `out==a/b`, and BaseMulAdd `out==a/b/c`; zero modulo-q
  mismatches.
- Range: maximum direct int32 accumulator `1,175,921,686`; all reduction and
  finish representatives fit their signed lane widths and preserve R0 output.
- Pi 5 correctness: 64 BaseMul, 64 direct aliases, and 64 BaseMulAdd cases per
  benchmark order pass before timing.
- BaseMul: `2579.606 -> 2245.412` p50 cycles, saving `334.194` or `12.955%`;
  kernel instructions `2808 -> 2447`.
- BaseMulAdd: `2872.696 -> 2369.547` p50 cycles, saving `503.149` or `17.515%`;
  kernel instructions `3243 -> 2881`.
- Three repetitions agree, 366 samples per variant, tiny BaseMul IQRs, and
  `throttled=0x0` throughout.
- Returned GCC code is stackless, call-free, spill-free, and avoids `v8-v15`.

The measured BaseMul saving establishes a 334-cycle budget for the combined
two-Forward plus one-Inverse FR-ISO2 absorption path.  Whether a fused scaled
NTT9 can stay inside that budget remains open.
