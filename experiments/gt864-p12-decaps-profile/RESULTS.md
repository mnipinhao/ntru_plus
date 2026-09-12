# P12 — current GT864 versus selected Official residual audit

P12 closes the post-P11 re-profile gate.  Production is unchanged.  The exact
current production kernel is revision `dd8c3146`; control revision `1c790870`
only recorded the rejected P11 experiment and changed the package roadmap.

## Binding and correctness

- Target: Pi 5 Cortex-A76, core 3, Linux 6.18.33, GCC 14.2.0,
  `-O3 -march=armv8-a+simd`.
- Selected Official source:
  `/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.
  Its independent upstream-latest status remains unverified.
- Official `kem.c`, `symmetric.c`, and `api.h` hashes match the selected
  baseline.  Full copied-tree hash:
  `40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`.
- GT manifest, fresh build, `test_kem`, 100-case KAT and all six
  cross-implementation exact/tampered transcript processes pass.  KAT SHA-256:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- GT library SHA-256 is
  `c5fd7fd8753af19f0c5f7592c9e571ba17a79cbea9d4ef642f3c50e4481c5b0e`,
  identical to the P10/P11 production baseline.  Linked object lists are in
  `results.json`.
- Six balanced AB/BA processes produced 252 clean observations per
  implementation and operation.  All 12 cycle-profiler and 24 event-profiler
  instrumentation-equivalence checks pass.  Temperature was 58.2--61.5 C,
  throttling remained `0x0`, and no SUPERCOP `do-part` was active.

## Clean full-KEM PMU

| Operation | Official cycles | GT cycles | GT - Official | Instruction gap | Branch gap |
|---|---:|---:|---:|---:|---:|
| Keygen | 44304.625 | 43669.375 | -635.250 | +6799 | +379.0 |
| Encaps | 46436.925 | 45353.200 | -1083.725 | +3939 | -59.0 |
| Decaps | 40761.450 | 40918.950 | **+157.500** | **+9439** | **+152.5** |

GT therefore still wins Keygen and Encaps and trails selected Official Decaps
by 0.39%.  The old `+9437/+152` working figure was not stale-binary noise: the
fresh campaign reproduces it as `+9439/+152.5` within PMU path variation.

## Decaps call-site cycle localization

Call-site values are diagnostic net medians after subtracting measured counter
read overhead.  They do not add exactly to the clean end-to-end median.

| Consistent boundary | Official cycles | GT cycles | GT - Official |
|---|---:|---:|---:|
| Forward (two calls) | 7533.500 | 6795.000 | -738.500 |
| BaseMul R0 | 2439.000 | 2174.000 | -265.000 |
| BaseMul R^-1 | 1761.300 | 1762.250 | +0.950 |
| FromBytes checked (three calls) | 2263.625 | 2173.300 | -90.325 |
| ToBytes | 2217.000 | 1515 full + 1187 small = 2702.000 | **+485.000** |
| Inverse + ternary | 4131.500 + 488.000 = 4619.500 | 5435.175 | **+815.675** |

The two real cycle deficits remain the combined Inverse-to-ternary boundary and
the aggregate ToBytes boundary.  Forward, R0 BaseMul and FromBytes have more or
different work in places but are already faster.

## Decaps retired-instruction and branch reconciliation

| Consistent boundary | Instruction gap | Branch gap | Cycle interpretation |
|---|---:|---:|---|
| Inverse + ternary | **+4493** | **+171** | Dominant arithmetic/control target; P11 proves terminal-route deletion alone is not enough |
| ToBytes aggregate | **+2886** | -24 | Second real cycle target; routing/packing arithmetic, not branch overhead |
| BaseMul R^-1 | +770 | +73 | Cycles tied; do not prioritize from static count alone |
| Forward | +1110 | +22 | GT is 738.5 cycles faster; retain |
| FromBytes checked | +701 | -39 | GT is 90.3 cycles faster; retain |
| R0 BaseMul | -178 | +1 | GT is faster; retain |

The sum of instrumented call sites is `+9659 instructions/+179 branches`; the
clean caller is `+9439/+152.5`.  The difference is expected from inserted
profiling calls, counter reads, compiler code shape, and non-instrumented caller
logic.  It is not assigned to a kernel.  Clean PMU remains authoritative.

## Decision

P12 is complete as a measurement/selection gate; no assembly is promoted.

1. Reopen Inverse only below the rejected P11 terminal route.  The next gate
   must decompose the current post-P7-C1 interior and propose an arithmetic DAG
   with a substantial same-boundary reduction; merely removing UMOV/stores or
   branches is excluded by P11.
2. Keep ToBytes second.  A candidate must reduce the actual full+small composed
   route/normalize/pack boundary, not revive the P6 scratch-storage experiment.
3. Do not reopen BaseMul R^-1, Forward, or FromBytes from instruction count
   alone while their same-run cycles are tied or better than Official.

Reproduction artifacts are `prepare.py`, `pi_run.py`, `run_events.py`,
`summarize.py`, and `summarize_events.py`.  Curated results and source identity
are tracked; ignored `raw/` and `build/` hold all CSV, logs, copied Official
source, generated profiled KEMs, binaries and symbols.
