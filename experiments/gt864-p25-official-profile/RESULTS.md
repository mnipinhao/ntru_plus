# P25 result — post-P24 selected-Official profiler

P25 measures exact GT864 P24 production revision
`d76a8289a8652e156665aff78bee6946183b2923` against the user-selected
SUPERCOP implementation at
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.
This fixed SUPERCOP target is not independently verified as latest upstream.

## Provenance and correctness

- GT was extracted by `git archive`; benchmark-time working-tree changes were
  excluded.
- Official tree SHA-256:
  `40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`.
- GT tree SHA-256:
  `c759162cae9a1c43df56fda819b97aafac1bafc317ff87588c3d65d3251cb898`.
- Fresh GT manifest/build/KEM/KAT passed.  KAT SHA-256:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Six processes each passed 100 exact cross-implementation transcripts and
  100 tampered-ciphertext rejections.
- Twelve cycle-profiler and 24 event-profiler instrumentation-equivalence
  processes passed.
- Pi 5 CPU 3, GCC 14.2.0, ondemand governor; unthrottled (`0x0`) from
  57.6 to 60.4 C.

## Clean full-KEM PMU

Each value is the median of 252 clean observations.  Negative delta means GT
is faster or retires less work.

| Operation | Official cycles | GT cycles | Cycle delta | Delta % | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|---:|
| Keygen | 44305.625 | 43137.875 | **-1167.750** | -2.636% | +4806.0 | +378.0 |
| Encaps | 46422.625 | 44982.175 | **-1440.450** | -3.103% | +2611.0 | -61.0 |
| Decaps | 40761.775 | 40067.250 | **-694.525** | -1.704% | +7358.0 | +36.5 |

GT therefore remains faster than this selected Official target for all three
complete operations, despite retiring more instructions.

## Matched call-site profile

Call counts are already aggregated per complete operation.  Official
`Inverse + Crepmod3` is compared with GT's fused `Inverse_to_ternary`; Official
Full ToBytes calls are compared with the actual GT Full/Small call mixture.
These instrumented medians diagnose boundaries and are not added to reconstruct
the clean full-KEM median.

| Operation / boundary | Official cycles | GT cycles | Cycle delta | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Keygen / Forward ×2 | 7533.750 | 6780.000 | -753.750 | +1110 | +22 |
| Keygen / BaseInv ×2 | 8363.500 | 8305.750 | -57.750 | +1792 | +396 |
| Keygen / BaseMul R0 ×2 | 4880.000 | 4349.000 | -531.000 | -356 | +2 |
| Keygen / ToBytes aggregate | 3327.000 | 3374.000 | **+47.000** | +2227 | -39 |
| Encaps / Forward ×2 | 7535.000 | 6788.550 | -746.450 | +1110 | +22 |
| Encaps / BaseMulAdd | 2900.000 | 2170.000 | -730.000 | -100 | +1 |
| Encaps / FromBytes checked | 751.000 | 725.050 | -25.950 | +234 | -13 |
| Encaps / ToBytes aggregate | 2217.650 | 2392.000 | **+174.350** | +1558 | -26 |
| Decaps / Forward ×2 | 7534.000 | 6777.750 | -756.250 | +1110 | +22 |
| Decaps / BaseMul R0 | 2439.000 | 2174.000 | -265.000 | -178 | +1 |
| Decaps / BaseMul Rinv | 1762.000 | 1757.875 | -4.125 | +770 | +73 |
| Decaps / FromBytes checked ×3 | 2262.000 | 2165.500 | -96.500 | +701 | -39 |
| Decaps / Inverse to ternary | 4620.000 | 4900.675 | **+280.675** | +3740 | +57 |
| Decaps / ToBytes aggregate | 2214.000 | 2392.000 | **+178.000** | +1558 | -26 |

## Decision

P26 is a matched-boundary Inverse deficit audit.  P21 already measured the GT
interior and P22 already rejected held-value-copy removal; P26 must not repeat
either experiment.  It will align Official `Inverse + Crepmod3` with GT
inverse9 ×12, main I16 ×6, tail I16, raw-to-ternary and wrapper/wipe, classify
the exact +3,740-instruction deficit by arithmetic, reduction, routing and
boundary work, and nominate a DAG only if it removes real work without adding
a memory pass.  Aggregate ToBytes remains second priority.  BaseMul Rinv's
retired-work excess is monitored but is not a positive cycle gap.

Machine-readable distributions are in `results.json` and
`event-results.json`; environment and linked symbols are in `environment.json`
and `symbols.txt`.
