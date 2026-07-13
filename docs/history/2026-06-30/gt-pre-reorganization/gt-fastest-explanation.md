# Current fastest GT implementation explanation

> Historical pre-reorganization note. Most paths below were retired when the GT
> assembly tree moved under `asm/gt/`; use the active production summary linked
> from `docs/README.md` for current source and benchmark evidence.

This note records the current fastest Good-Thomas implementation for
NTRU+768/AArch64.  It follows the same documentation shape as
`doc/gt_invntt_explanation.md`: source map, selected paths, dataflow, current
Pi 5 results, and next work.

The five implementation surfaces covered here are:

- `gt_my_ntt`: GT forward `poly_ntt`
- `invntt`: GT inverse `poly_invntt`
- `poly_mul`: GT `poly_basemul`
- `poly_mul_add`: GT `poly_basemul_add`
- `crepmod3`: shared `poly_crepmod3` used by the GT KEM path

## Source map

Current GT forward NTT:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/my_ntt.s
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/my_32ntt.opt.s
```

Current GT inverse NTT:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt.s
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/invntt_opt.s
```

Compatibility and regression wrappers:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt_stage123_stripescratch.s
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt_stage123_stripescratch_benchstages.s
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt_directstage123_branchfold.s
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt_directstage123_branchfold_benchstages.s
```

Current GT base multiplication:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/base_gt.opt.s
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/base_gt.n1.opt.s
```

`base_gt.opt.s` is byte-for-byte the promoted N1 schedule.  The `.n1` file is
kept as a named benchmark alias and for log provenance.

Shared KEM support used by GT:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/crepmod3.s
```

Benchmark and decision records:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/bench.md
ntruplus-ntt-Optimized/aarch64-bench/scripts/run_pi5_gt_pmu_attribution.sh
ntruplus-ntt-Optimized/aarch64-bench/scripts/run_pi5_gt_pipeline_pmu_attribution.sh
```

Latest local copies of the Pi 5 logs:

```text
/private/tmp/pi5-gt-pmu-20260611-221546-copy
/private/tmp/pi5-gt-pipeline-pmu-20260611-225318
```

## Current selected paths

Benchmark variant:

```text
VARIANT=gt_opt
```

`gt_opt` currently links:

```text
ntruplus/ntt.c
ntruplus/asm/base_gt.opt.s
ntruplus/asm/my_ntt.s
ntruplus/asm/slothy/my_32ntt.opt.s
ntruplus/asm/inv_my_ntt.s
```

For `kem_dec`, the GT variant also links the normal KEM support sources,
including `asm/add.s`, `asm/crepmod3.s`, `asm/pack.s`, `asm/cbd.s`, and the
selected SHAKE implementation.

The selected inverse gates are:

```asm
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.include "asm/slothy/invntt_opt.s"
```

The selected forward NTT has `NTT32_FUSED_SCATTER=1` by default:

```asm
.ifndef NTT32_FUSED_SCATTER
    .equ NTT32_FUSED_SCATTER, 1
.endif
```

This means `_ntt32_8way` reduces and scatters directly to the final `poly_ntt`
output layout, instead of returning a row buffer and using a separate scatter
pass.

## `gt_my_ntt`: forward `poly_ntt`

Function:

```text
poly_ntt / _poly_ntt
```

Main sources:

```text
asm/my_ntt.s
asm/slothy/my_32ntt.opt.s
```

High-level dataflow:

```text
natural coefficient input
  -> 3-point branch split and twist
  -> row buffers at sp + 32, sp + 544, sp + 1056
  -> three calls to _ntt32_8way
  -> fused final reduction + row-bitrev GT output scatter
  -> GT row-bitrev quartic block output
```

The 32-point Slothy kernel contract is intentionally narrow:

```text
input comes only from my_ntt.s phase123 row buffers
input order is row-local natural work order
output is bit-reversed/scattered to final GT row-bitrev layout
```

The kernel deliberately does not normalize the loaded row-buffer vectors at
entry.  The caller's phase123 bounds are part of the contract, and the final
stage345 blocks reduce before storing.

Current Pi 5 median:

```text
gt_promoted_default ntt = 2725 cycles
KPQC final stock ntt    = 3471 cycles
delta                   = -746 cycles
```

This is the largest standalone GT win.  It is also why GT wins the full
pipeline even though GT base multiplication is slower than KPQC final base
multiplication.

## `invntt`: inverse `poly_invntt`

Function:

```text
poly_invntt / _poly_invntt
```

Main sources:

```text
asm/inv_my_ntt.s
asm/slothy/invntt_opt.s
```

Compatibility alias:

```text
asm/inv_my_ntt_stage123_stripescratch.s
```

Legacy regression baseline:

```text
asm/inv_my_ntt_directstage123_branchfold.s
```

High-level dataflow:

```text
GT row-bitrev NTT input
  -> direct physical-layout row loads
  -> direct inverse row stage123
  -> stripe-major scratch layout for stage45 input
  -> Slothy-scheduled stage45 + row-end Barrett reduction fusion
  -> inverse DFT3 with post-DFT3 reductions removed
  -> branch-constant folded untwist + final merge + scaling
  -> final output reductions
  -> natural coefficient output
```

Current Pi 5 read:

```text
promoted invntt median       = about 4039 to 4055 cycles
legacy direct-stage123 path  = noise-level around the same range
```

Decision:

- Keep the stripe-scratch path promoted in `asm/inv_my_ntt.s`.
- Keep the direct-stage123 branchfold wrapper only for regression and PMU
  attribution.
- Do not continue the row-stage45-to-post fusion line.
- Do not continue the `consthalf` or `constgrp3` post-branchfold line.

The inverse path is no longer the best next target.  The latest PMU data points
to forward NTT / pipeline-boundary work.

## `poly_mul`: GT `poly_basemul`

Function:

```text
poly_basemul / _poly_basemul
```

Main source:

```text
asm/base_gt.opt.s
```

Alias for the promoted schedule:

```text
asm/base_gt.n1.opt.s
```

High-level dataflow:

```text
GT row-bitrev quartic blocks a, b
  -> ld4 physical blocks for eight consecutive physical_j values
  -> load gt_rowbitrev_lambda[branch][physical_j]
  -> widening quartic base multiply
  -> Montgomery reduction
  -> st4 GT row-bitrev quartic output
```

The lambda table is already stored in GT physical row-bitrev order:

```text
coeff[branch * 384 + 4 * physical_j + lane]
```

Current Pi 5 median:

```text
gt_promoted_default basemul = 2845 cycles
KPQC final basemul          = 2646 cycles
delta                       = +199 cycles
```

Decision:

- Keep `base_gt.opt.s` promoted because it is the fastest GT base schedule.
- Do not spend the next iteration on base-only scheduling: the standalone base
  win from N1 mostly disappears in `ntt_basemul_add_pipeline`.
- Any future base work needs a concrete pipeline integration hypothesis.

## `poly_mul_add`: GT `poly_basemul_add`

Function:

```text
poly_basemul_add / _poly_basemul_add
```

Main source:

```text
asm/base_gt.opt.s
```

High-level dataflow:

```text
GT row-bitrev quartic blocks a, b, c
  -> ld4 a and b physical blocks
  -> load c accumulator block
  -> load gt_rowbitrev_lambda[branch][physical_j]
  -> widening quartic base multiply
  -> Montgomery reduction
  -> add accumulator
  -> st4 GT row-bitrev quartic output
```

Current Pi 5 median:

```text
gt_promoted_default basemul_add = 2928 cycles
KPQC final basemul_add          = 2580 cycles
delta                           = +348 cycles
```

Full pipeline context:

```text
gt_promoted_default ntt_basemul_add_pipeline = 16017 cycles
KPQC final ntt_basemul_add_pipeline          = 17328 cycles
delta                                        = -1311 cycles
```

Decision:

- Standalone GT `poly_basemul_add` is slower than KPQC final.
- The full GT pipeline still wins because forward `poly_ntt` is much faster.
- The next optimization target should be the forward NTT / 32-point boundary,
  not another isolated `poly_basemul_add` schedule.

## `crepmod3`: shared `poly_crepmod3`

Function:

```text
poly_crepmod3 / _poly_crepmod3
```

Main source:

```text
asm/crepmod3.s
```

High-level dataflow:

```text
int16 coefficient input
  -> load 32 coefficients per loop
  -> approximate divide by 3 with sqdmulh and srshr
  -> subtract 3 * quotient with mls
  -> store centered representatives modulo 3
```

Loop shape:

```asm
ld1     {v2.8h - v5.8h}, [src], #64
sqdmulh v6.8h, v2.8h, v1.8h
srshr   v6.8h, v6.8h, #1
mls     v2.8h, v6.8h, v0.8h
st1     {v2.8h - v5.8h}, [dst], #64
```

Current status:

- There is no GT-specific `crepmod3` fork.
- The fastest GT KEM path uses the shared KPQC AArch64 `asm/crepmod3.s`.
- Current PMU work did not isolate `crepmod3`; it is included in `kem_dec`.
- Do not fork `crepmod3` for GT unless a dedicated KEM attribution run shows it
  is a material limiter.

## Current Pi 5 benchmark summary

Latest C-line PMU run:

```text
logs/pi5-gt-pipeline-pmu-20260611-225318/
```

Median cycles from the `core` perf group:

| mode | KPQC final | KPQC base.opt ablation | GT promoted | GT vs KPQC final |
| --- | ---: | ---: | ---: | ---: |
| ntt | 3471 | 3471 | 2725 | -746 / 0.785x |
| basemul | 2646 | 2599 | 2845 | +199 / 1.075x |
| basemul_add | 2580 | 2604 | 2928 | +348 / 1.135x |
| ntt_mul_pipeline | 13665 | 13621 | 12544 | -1121 / 0.918x |
| ntt_basemul_add_pipeline | 17328 | 17440 | 16017 | -1311 / 0.924x |
| kem_dec | 35184 | 35085 | 34152 | -1032 / 0.971x |

End-to-end headline:

```text
current GT promoted beats KPQC final kem_dec by about 1032 cycles
current GT promoted is about 2.9% faster for kem_dec
```

PMU interpretation:

- GT promoted wins despite using more instructions and more L1D load refs in
  the full pipeline.
- In `ntt_mul_pipeline`, GT promoted uses about 1.25x instructions and 2.30x
  L1D load refs versus KPQC final, but only 0.917x PMU cycles.
- The win is throughput, scheduling, and algorithm shape.  It is not a
  memory-miss reduction story.

## What to work on next

Primary next target:

```text
asm/my_ntt.s
asm/slothy/my_32ntt.opt.s
```

Focus:

```text
hand-written phase123 outer transform
  -> row-buffer handoff
  -> _ntt32_8way stage12/stage345 Slothy regions
  -> fused scatter to final GT row-bitrev output
```

Do not prioritize:

- inverse post-branchfold constant compression
- row-stage45-to-post inverse fusion
- base-only micro-scheduling
- GT-specific `crepmod3` fork

Benchmark command for the current GT/KPQC comparison:

```sh
cd /home/pi/ntruplus-ntt-Optimized/aarch64-bench
SUDO= PERF_RUNS=3 scripts/run_pi5_gt_pipeline_pmu_attribution.sh
```

Focused correctness checks:

```sh
cd /home/pi/ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768

make clean
make test_gt_base_opt
./build/test_gt_base_opt

make clean
make test_polyinvntt_asm
./build/test_polyinvntt_asm
```
