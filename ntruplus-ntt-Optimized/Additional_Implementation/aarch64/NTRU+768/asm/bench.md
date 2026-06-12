## Codex readout

2026-06-11 follow-up for requested steps 2, 5, 6, and 7.

### Promotion status

Step 2 is applied: `asm/base_gt.opt.s` now contains the N1 schedule from
`asm/base_gt.n1.opt.s`.  The `.n1` file is kept as a named benchmark alias for
older scripts and log provenance.

Step 5 is applied from the existing Pi 5 matrix: `asm/inv_my_ntt.s` and
`asm/inv_my_ntt_benchstages.s` now select
`INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH`.  The previous direct-stage123
branchfold path is preserved as:

- `asm/inv_my_ntt_directstage123_branchfold.s`
- `asm/inv_my_ntt_directstage123_branchfold_benchstages.s`

These wrappers are for regression and PMU attribution, not promotion.
`scripts/run_pi5_gt_post_branchfold_matrix.sh` now treats the no-override
`gt_opt` case as `gt_promoted_default` and uses the legacy wrapper for the
pre-promotion direct-stage123 baseline.

Step 6 is encoded as a reproducible Pi 5 PMU runner:

```sh
cd ntruplus-ntt-Optimized/aarch64-bench
PERF_RUNS=3 scripts/run_pi5_gt_pmu_attribution.sh
```

It writes `logs/pi5-gt-pmu-*/summary_pmu.csv` plus per-case `perf stat` logs
for these comparisons:

- `gt_promoted_default`
- `gt_legacy_directstage123_branchfold`
- `gt_post_branchfold_constgrp3`
- `gt_post_branchfold_consthalf`

The default event groups are:

- `core`: cycles, instructions, branches, branch misses
- `cache`: cache refs/misses plus L1D loads/stores/misses
- `front`: L1I miss and TLB miss probes

If the Pi kernel names events differently, override with:

```sh
PERF_GROUPS='core:cycles,instructions;cache:L1-dcache-loads,L1-dcache-load-misses' \
  scripts/run_pi5_gt_pmu_attribution.sh
```

If `perf` is installed at a non-standard path, use `PERF_BIN=/path/to/perf`.
The runner now preflights this before building the full matrix.
It also writes `perf_events_raw.csv`, which collects the raw per-event
`perf stat -x,` rows from every case/mode/group, and
`perf_events_summary.csv`, which pivots those rows into event values plus
ratios against `gt_promoted_default`.

### Current benchmark interpretation

This post-branchfold sweep does not justify promoting a new inverse-NTT post
candidate.  The useful result is negative: the branchfold post path is not
currently load-shape limited enough for the tested loop grouping or constant
compression tricks to pay for themselves.

Median cycles from the run:

| case | invntt | ntt_mul_pipeline | ntt_basemul_add_pipeline | kem_dec | decision |
| --- | ---: | ---: | ---: | ---: | --- |
| gt_opt_default | 4046 | 12576 | 16128 | 34187 | old baseline |
| base_n1 + stage123_stripescratch | 4039 | 12511 | 15977 | 34143 | promoted |
| post_branchfold_a72_1stripe | 4052 | 12602 | 16135 | 34189 | reject |
| post_branchfold_3stripe | 4044 | 12585 | 16152 | 34189 | reject; no pipeline/KEM win |
| post_branchfold_6stripe | 4045 | 12588 | 16079 | 34188 | reject; mixed/noisy |
| post_branchfold_constgrp3 | 4043 | 12562 | 16120 | 34184 | do not promote; tiny standalone win only |
| post_branchfold_6stripe_constgrp3 | 4045 | 12596 | 16075 | 34185 | reject; mixed/noisy |
| post_branchfold_consthalf | 4069 | 12617 | 16168 | 34197 | reject; extra ins cost loses |

Practical conclusion:

- Drop C1/d-half compression from the branchfold line.
- Do not spend more time on simple 3-stripe/6-stripe loop grouping.
- `ldp` pair adjacency is at best noise-level here; keep only if a larger
  Slothy-generated block later wants it structurally.
- The only promotion-quality result from this matrix is now production:
  base-N1 plus stage123 stripe scratch.
- Next useful work should move away from branchfold constant-load shape and
  toward PMU-guided post-friendly row scratch, bounded producer-consumer
  scheduling, or a wider forward/base/global pipeline target.

### Step 7 decision gate

Use the PMU run to choose the next branch as follows:

- Choose A, post-friendly row scratch, if `gt_promoted_default` still shows
  meaningful L1D/cache pressure in `invntt`, `ntt_mul_pipeline`, or
  `ntt_basemul_add_pipeline`, while `constgrp3` and `consthalf` do not turn
  lower cache pressure into lower cycles.  This keeps the stage45/post boundary
  separated but makes the post load stream more linear.
- Choose B, bounded producer-consumer v9, only if the PMU says the inverse path
  is still the arithmetic-pipeline limiter and the front-end counters do not
  punish the extra code shape.  Stop the first clean version if it lands above
  about 4050 cycles.
- Choose C, forward/base/global pipeline, if `basemul`, `basemul_add`, or full
  pipeline modes dominate the counter deltas more than `invntt`.  In that case,
  further inverse-only post variants are unlikely to move KEM enough.

True PMU readout from `logs/pi5-gt-pmu-20260611-221546/`:

| case | mode | insn ratio | L1D load ref ratio | L1D miss ratio | bench core delta | decision |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| gt_legacy_directstage123_branchfold | invntt | 0.9994 | 0.9998 | 0.9789 | -11 | regression baseline; cycle delta is noise-level |
| gt_legacy_directstage123_branchfold | kem_dec | 1.0000 | 1.0000 | 1.0531 | -4 | no evidence to unpromote stripe scratch |
| gt_post_branchfold_constgrp3 | invntt | 0.9657 | 0.9998 | 0.9731 | -14 | fewer inverse instructions, but not end-to-end useful |
| gt_post_branchfold_constgrp3 | kem_dec | 0.9974 | 1.0000 | 1.7189 | -1 | no KEM win; miss direction gets worse |
| gt_post_branchfold_consthalf | invntt | 1.1343 | 1.2857 | 0.9879 | +16 | reject |
| gt_post_branchfold_consthalf | ntt_mul_pipeline | 1.0486 | 1.1015 | 0.9963 | +88 | reject |
| gt_post_branchfold_consthalf | ntt_basemul_add_pipeline | 1.0383 | 1.0769 | 1.0021 | +130 | reject |
| gt_post_branchfold_consthalf | kem_dec | 1.0101 | 1.0206 | 0.9136 | +20 | reject |

The promoted `kem_dec` run has about 3,259,451,883 L1D load refs/cache refs
and only 187,959 L1D load misses, roughly 0.006%.  That is not an L1D miss
bottleneck.  The constant-compression hypothesis is now falsified for this
branch: `consthalf` reduces neither instruction count nor load pressure in the
pipeline modes, and `constgrp3` only helps standalone inverse instruction count
without producing a KEM/pipeline win.

Current step-7 choice from the true PMU data: C is the primary next target.
The inverse-only stripe-scratch promotion is real, but the pipeline/KEM deltas
are now small enough that another inverse-post-only constant-shape tweak is
unlikely to move end-to-end performance.  Keep A, post-friendly row scratch, as
a secondary scheduling/load-stream experiment only if it changes instruction
shape cheaply; do not justify it with an L1D miss story.  Do not start B unless
a small bounded prototype can beat about 4050 cycles immediately.

Next measurement should therefore be the C-line pipeline attribution runner:

```sh
cd ntruplus-ntt-Optimized/aarch64-bench
PERF_RUNS=3 scripts/run_pi5_gt_pipeline_pmu_attribution.sh
```

If `sudo perf` is blocked in a non-interactive SSH session but user-mode perf
works, run it as:

```sh
SUDO= PERF_RUNS=3 scripts/run_pi5_gt_pipeline_pmu_attribution.sh
```

This compares `stock_default`, `stock_opt_base`, `gt_ref_base`, and
`gt_promoted_default` across `ntt`, `basemul`, `basemul_add`,
`ntt_mul_pipeline`, `ntt_basemul_add_pipeline`, and `kem_dec`.  Use the
`gt_ref_base -> gt_promoted_default` delta to decide whether the next code
change belongs in `base_gt.opt.s` or in the forward NTT / pipeline boundary.

2026-06-11 Pi 5 C-line PMU run:
`logs/pi5-gt-pipeline-pmu-20260611-225318/`.

Benchmark median cycles from the `core` perf group:

| case | ntt | basemul | basemul_add | ntt_mul_pipeline | ntt_basemul_add_pipeline | kem_dec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stock_default | 3471 | 2646 | 2580 | 13665 | 17328 | 35184 |
| stock_opt_base | 3471 | 2599 | 2604 | 13621 | 17440 | 35085 |
| gt_ref_base | 2718 | 2919 | 2993 | 12605 | 16027 | 34300 |
| gt_promoted_default | 2725 | 2845 | 2928 | 12544 | 16017 | 34152 |

`gt_ref_base -> gt_promoted_default` deltas:

| mode | cycle delta | PMU cycle ratio | instruction ratio | L1D load ref ratio | note |
| --- | ---: | ---: | ---: | ---: | --- |
| ntt | +7 | 1.0027 | 1.0000 | 1.0000 | base swap should not affect forward NTT |
| basemul | -74 | 0.9750 | 1.0000 | 1.0000 | N1 base still wins by scheduling/latency |
| basemul_add | -65 | 0.9793 | 1.0000 | 1.0000 | same, no instruction-count story |
| ntt_mul_pipeline | -61 | 0.9942 | 1.0000 | 1.0000 | small propagation |
| ntt_basemul_add_pipeline | -10 | 0.9990 | 1.0000 | 1.0000 | essentially noise |
| kem_dec | -148 | 0.9956 | 1.0000 | 0.9999 | real but small end-to-end win |

C-line conclusion: keep `base_gt.opt.s` promoted, but do not spend the next
iteration on another base-only micro-schedule unless it has a concrete pipeline
integration hypothesis.  The forward NTT is now the better target: stock to
GT-promoted improves `ntt` by 746 cycles and the full pipeline by about
1121-1311 cycles, while the base-N1 promotion only contributes about 61 cycles
to `ntt_mul_pipeline` and almost nothing to `ntt_basemul_add_pipeline`.
Next code work should inspect `my_ntt.s` and `slothy/my_32ntt.opt.s`, especially
the boundary between the hand-written outer transform and the 32-point Slothy
kernel.

### KPQC final comparison

In the benchmark harness, `VARIANT=stock` is the KPQC final AArch64 path:
`asm/base.s` plus `asm/ntt.s`.  `stock_opt_base` is only an ablation that swaps
in `asm/base.opt.s`; it is not the KPQC final default.  `gt_promoted_default`
is the current Good-Thomas path with promoted `base_gt.opt.s` and stage123
stripe-scratch inverse NTT.

Cycle comparison from `logs/pi5-gt-pipeline-pmu-20260611-225318/`:

| mode | KPQC final | KPQC base.opt ablation | GT promoted | GT vs KPQC final | GT vs KPQC base.opt |
| --- | ---: | ---: | ---: | ---: | ---: |
| ntt | 3471 | 3471 | 2725 | -746 / 0.785x | -746 / 0.785x |
| basemul | 2646 | 2599 | 2845 | +199 / 1.075x | +246 / 1.095x |
| basemul_add | 2580 | 2604 | 2928 | +348 / 1.135x | +324 / 1.124x |
| ntt_mul_pipeline | 13665 | 13621 | 12544 | -1121 / 0.918x | -1077 / 0.921x |
| ntt_basemul_add_pipeline | 17328 | 17440 | 16017 | -1311 / 0.924x | -1423 / 0.918x |
| kem_dec | 35184 | 35085 | 34152 | -1032 / 0.971x | -933 / 0.973x |

Interpretation:

- GT promoted is worse than KPQC final for standalone base multiply:
  `basemul` is +199 cycles and `basemul_add` is +348 cycles.  This is expected:
  Good-Thomas pays extra structure in the base layer.
- GT promoted wins the forward NTT heavily: `ntt` is -746 cycles.  That win is
  large enough to dominate both full pipeline modes and KEM decapsulation.
- KPQC `base.opt.s` helps standalone `basemul` (-47 vs KPQC final) but does not
  improve the larger pipeline consistently: `ntt_basemul_add_pipeline` is +112
  cycles worse than KPQC final in this run.
- PMU says the GT win is not from fewer instructions or fewer L1D accesses.  In
  `ntt_mul_pipeline`, GT promoted uses about 1.25x instructions and 2.30x L1D
  load refs versus KPQC final, but only 0.917x PMU cycles.  The effective win is
  throughput/scheduling/algorithm shape, not a memory-miss reduction story.
- End-to-end headline: current GT promoted beats KPQC final `kem_dec` by about
  1032 cycles, roughly 2.9%.

### Local verification after promotion

Completed in this workspace:

- `asm/base_gt.opt.s` is byte-for-byte equal to `asm/base_gt.n1.opt.s`.
- `bash -n scripts/run_pi5_gt_pmu_attribution.sh` passes.
- `bash -n scripts/run_pi5_gt_pipeline_pmu_attribution.sh` passes.
- PMU runner dry-run passes with
  `DRY_RUN=1 PMU_MODES=invntt PERF_GROUPS=core:cycles PERF_RUNS=1`.
- Pipeline PMU runner dry-run passes with
  `DRY_RUN=1 PMU_MODES=ntt,basemul PERF_GROUPS=core:cycles PERF_RUNS=1`.
- PMU runner postprocessing dry-run writes `perf_events_summary.csv`.
- `make verify_invntt_constants` passes.
- `make test_polyinvntt_asm && ./build/test_polyinvntt_asm` passes.
- `make test_invntt_representatives && ./build/test_invntt_representatives`
  passes.

Observed on Pi:

- The first `PERF_RUNS=3 scripts/run_pi5_gt_pmu_attribution.sh` attempt built
  the promoted `gt_opt` cases but failed every counter group with
  `sudo: perf: command not found`.
- After installing/providing `perf`, the 20260611-215539 run completed and
  produced raw logs under
  `logs/pi5-gt-pmu-20260611-215539/`.  The pasted stdout includes the benchmark
  cycle lines, but not the `*.perf.csv` counter contents.
- The later 20260611-221546 run includes 72 `*.perf.csv` files.  Reading those
  counters shows `consthalf` is a real regression, `constgrp3` is inverse-only
  and not KEM-useful, and the promoted default should stay production.

Blocked locally:

- `make test_gt_base_opt` does not assemble on macOS after the N1 promotion
  because `base_gt.n1.opt.s` uses Linux/GNU AArch64 relocations:
  `adrp lambda, gt_rowbitrev_lambda` plus
  `add lambda, lambda, :lo12:gt_rowbitrev_lambda`.  This needs final build and
  correctness confirmation on the Pi/Linux target where the benchmark was
  produced.
