# D1-P3B6 evidence

Status: **keep experimental; Pi 5 correctness/allocation passed, but the
1250-cycle promotion gate did not.**

- Exact composed-map SHA-256:
  `087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270`.
- The generated input order reproduces the P3B3 upper bound of sixteen live
  partial output vectors.  A 25-second randomized order search reduced active
  area but found no order below peak sixteen; this is still not a minimum
  proof.
- 256 complete inputs, including index tags, signed extrema and random values,
  match the independent composed-map scalar byte oracle.  Both exact buffer
  edges pass guard pages.
- Initial unconstrained C let Apple clang hoist future q-loads beyond the
  modeled frontier and produced five q-register stack spills.  The generator
  now emits empty public register-state barriers after each source q-vector.
  These do not generate instructions; they make the proven frontier part of
  the compiler contract and prevent lifetime expansion.
- After the barrier correction, the top-local core has zero stack references
  and uses `v0-v7` plus `v16-v30`.  Only the outer two-call wrapper has its
  ordinary 32-byte GPR call frame.
- The emitted Apple-clang top core is 5444 bytes / 1361 instructions.  It has
  54 FR0 q-loads plus one literal q-load, so two calls read all 108 FR0 vectors
  exactly once.  Code size and instruction count are materially larger than
  the rejected R9-local body and must be priced on Cortex-A76.

## Cortex-A76 target object audit

- Host: `pi@100.99.191.9`, Raspberry Pi 5 Cortex-A76 r4p1.
- Compiler: GCC 14.2.0, `-O3 -march=armv8-a+simd`.
- The generated top core has 1382 static instructions and 56 `ldr q` encodings.
  Fifty-four are the FR0 input vectors; the others are constant material.
- Its only stack references are the AAPCS64 save/restore pairs for `d8-d15`.
  There are no coefficient-vector spills and no stack scratch.  The outer
  two-top wrapper only saves/restores `x29/x30`.

## Paired PMU result

The benchmark used core 3, 400 calls/sample, 41 samples in each of both
execution orders, three complete repetitions, and medians over all 246 samples
per variant.  Correctness passed 128 complete inputs against the exact composed
map oracle before every timing process.  The Pi reported `throttled=0x0`.

| variant | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| P3B4 `r9_to` control | 1848.172 | 4360.060 | 182.010 |
| P3B6 input-once | 1502.463 | 2769.060 | 6.010 |
| candidate - control | -345.709 | -1591.000 | -176.000 |

P3B6 is 18.71% faster than the current P3B4 ToBytes control and removes 36.49%
of its retired instructions.  However, it is still 252.463 cycles above the
1250-cycle threshold required by the current Encaps break-even model.

Therefore this candidate is not linked into full KEM and is not promoted.  It
is retained as the exact-ABI, input-once experimental baseline because it
establishes that eliminating the two coefficient scratch passes is valuable;
the remaining cost is dominated by the straight-line 9-to-8 lane-routing and
per-output normalization/packing network.
