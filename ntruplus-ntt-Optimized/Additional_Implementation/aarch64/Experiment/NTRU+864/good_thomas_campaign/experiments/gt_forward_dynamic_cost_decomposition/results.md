# M5Q results

M5Q passes as a decomposition/understanding gate.

- The 633-instruction symbolic helper aligns one-to-one with the returned
  order-preserving allocated artifact.  All 513 symbolic vector lifetimes were
  recovered; allocation uses `v0-v7,v18-v31` plus fixed `v16/v17`, never
  `v8-v15`.
- Static dynamic path: 849 top split + 3,960 pass 2 + 16 outer wrapper =
  exactly 4,825 GT instructions.
- Pi 5 noop establishes 8.00105 common harness instructions.  PMU then yields
  exact kernel counts: Official 4,028, GT 4,825, top split 849, pass 2 3,960.
- The M5P excess is therefore exactly 797 kernel instructions, not measurement
  noise or an ABI adapter.
- Overall Pi 5 p50 cycles across 366 samples: Official 4,394.09, GT 4,698.59,
  top split 669.23, pass 2 4,032.86.  All three repetitions agree.
- Every one of six remote processes passed 64 disjoint and 64 exact-alias full
  Forward comparisons.  Temperature was 57.1--63.1 C and throttling remained
  `0x0`.

The largest instruction owner is the pair of transpose/twist/oriented-NTT9
blocks: 1,998 instructions over six banks.  Main NTT16 is next at 990.  This
does not prove either stage is wasteful; it only fixes where any removal must
come from.

Formal source SHA-256 includes analyzer
`2e436299be49469ce76a84be1fe397e9f45e8effb50dce94b812905df5a1b33d`,
runner `533f3fc4db29593af65d5e9847f868a9892ded4c049a7c4530c7ad1841222314`,
and PMU harness
`5332d669231e8da1b5e3c8fa44fe71645e2fe8a48d74873836c2e5618efdcd11`.
