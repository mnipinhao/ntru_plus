# KEM production variant audit

Date: 2026-06-30

Scope: audit and benchmark only.  This pass does not change production
defaults, does not run Slothy, does not promote benchmark-only candidates, and
does not change Q31 behavior.

Benchmark host:

```text
Pi5: pi@100.99.191.9
bench repo: /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench
KPQC final source: /home/pi/ntruplus/ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768
```

The `aarch64-bench` generic KEM matrix below uses `CYCLES=PERF`, because the
generic `bench.c` `CYCLES=PMU` mode directly reads `pmccntr_el0` and traps as
an illegal instruction on the current Pi5 setup.  The project PMU component
harnesses continue to use Linux `perf_event_open`.

## Production linkage

Current `VARIANT=gt_production` in `aarch64-bench/Makefile` links:

```text
GT_PRODUCTION_KEM_SOURCES =
  ntruplus/ntt.c
  ntruplus/asm/slothy/support_kernels/support_kernels.n1.opt.S
  ntruplus/asm/cbd.s
  ntruplus/asm/my_ntt_phase123_n1.s
  ntruplus/asm/slothy/my_32ntt.opt.s
  ntruplus/asm/inv_my_ntt.s
  ntruplus/asm/inv_my_ntt_rminus1.S
  ntruplus/poly_gt_baseinv_batch.c
  ntruplus/asm/slothy/baseinv_batch_finish_loop_n1.S
  ntruplus/asm/gt_fqinv15.S
  ntruplus/asm/base_gt_opt_noadd_wrapper.S
  ntruplus/asm/base_gt_add32_full_pipeline_inline_wrapper.S
  ntruplus/asm/base_gt_scaled_r_input_opt_wrapper.S
  ntruplus/asm/base_gt_rminus1_opt_wrapper.S

VARIANT_CFLAGS =
  -DGT_PRODUCTION_USE_SCALED_KEYPAIR
  -DGT_PRODUCTION_USE_RMINUS1_DECAP
  -DGT_BASEINV_BATCH_USE_ASM_FINISH
  -DGT_BASEINV_USE_FQINV15_ASM
  -DBENCH_VARIANT_GT=1
```

Linked symbol evidence from the Pi5 `gt_production` KEM benchmark binary:

```text
poly_crepmod3 / _poly_crepmod3
poly_frombytes / _poly_frombytes
poly_tobytes / _poly_tobytes
poly_ntt / gt_block_major_poly_ntt / _poly_ntt / _gt_block_major_poly_ntt
poly_invntt / _poly_invntt
poly_invntt_from_rminus1 / gt_block_major_poly_invntt_from_rminus1
poly_baseinv_scaled_r
poly_basemul / _poly_basemul
poly_basemul_add / _poly_basemul_add
poly_basemul_scaled_r_input / _poly_basemul_scaled_r_input
poly_basemul_rminus1 / _poly_basemul_rminus1
```

The one-shot benchmark build does not retain separate `.o` files, so the
object column below is recorded as "linked binary only".

| function | production symbol | source file | linked? | gate | notes |
| --- | --- | --- | --- | --- | --- |
| Forward NTT | `poly_ntt`, `gt_block_major_poly_ntt` | `ntt.c`, `asm/my_ntt_phase123_n1.s`, `asm/slothy/my_32ntt.opt.s` | yes | none beyond `VARIANT=gt_production` | GT block-major row-bitrev output; not tuple, rowpack, BPQ, or TMVP |
| Generic InvNTT | `poly_invntt` | `asm/inv_my_ntt.s` | yes | none beyond `VARIANT=gt_production` | linked for generic ABI; decap production path uses rminus1 entry |
| rminus1 InvNTT | `poly_invntt_from_rminus1`, `gt_block_major_poly_invntt_from_rminus1` | `asm/inv_my_ntt_rminus1.S` | yes | `GT_PRODUCTION_USE_RMINUS1_DECAP` | production decap first product consumes rminus1 contract |
| Generic basemul | `poly_basemul` | `asm/base_gt_opt_noadd_wrapper.S` | yes | none beyond `VARIANT=gt_production` | arithmetic-correct GT block-major basemul |
| Basemul add | `poly_basemul_add` | `asm/base_gt_add32_full_pipeline_inline_wrapper.S` | yes | Q31 gate can bypass only the encap tobytes helper | generic symbol remains the production arithmetic-correct implementation |
| rminus1 basemul | `poly_basemul_rminus1` | `asm/base_gt_rminus1_opt_wrapper.S` | yes | `GT_PRODUCTION_USE_RMINUS1_DECAP` | paired only with `poly_invntt_from_rminus1` |
| Scaled keypair basemul | `poly_basemul_scaled_r_input` | `asm/base_gt_scaled_r_input_opt_wrapper.S` | yes | `GT_PRODUCTION_USE_SCALED_KEYPAIR` | keygen-only scaled-r input contract |
| Baseinv / polyinv path | `poly_baseinv_scaled_r` | `poly_gt_baseinv_batch.c`, `baseinv_batch_finish_loop_n1.S`, `gt_fqinv15.S` | yes | `GT_PRODUCTION_USE_SCALED_KEYPAIR`, `GT_BASEINV_BATCH_USE_ASM_FINISH`, `GT_BASEINV_USE_FQINV15_ASM` | closed-form/batch baseinv path used by current keygen |
| pack | `poly_tobytes`, `poly_frombytes` | `asm/slothy/support_kernels/support_kernels.n1.opt.S` | yes | none | stock support API replaced by Slothy support kernel in `gt_production` |
| crepmod3 | `poly_crepmod3` | `asm/slothy/support_kernels/support_kernels.n1.opt.S` | yes | none | separate decap recovery reduction; fused crep3 variants are not default |

Default current GT production does not contain any `q31` symbol.  The release
guard binary links both `poly_basemul_add` and
`poly_basemul_add_encap_direct32_q31_tobytes_contract_prototype`, and verifies
that the only Q31 call site is `gt_encap_basemul_add_tobytes_contract`.

## Gate and macro audit

| gate / macro | default in `gt_production` | affected path | status | changes KEM output path? | correctness guard |
| --- | ---: | --- | --- | --- | --- |
| `GT_PRODUCTION_USE_SCALED_KEYPAIR` | on | keygen `KEYPAIR_BASEINV`, `KEYPAIR_BASEMUL` | production default | yes, internal keygen contract only | full KEM correctness |
| `GT_PRODUCTION_USE_RMINUS1_DECAP` | on | decap `poly_basemul_rminus1` -> `poly_invntt_from_rminus1` | production default | yes, private decap temporary only | full KEM correctness |
| `GT_BASEINV_BATCH_USE_ASM_FINISH` | on | `poly_baseinv_scaled_r` finish loop | production default | no public ABI change | full KEM correctness |
| `GT_BASEINV_USE_FQINV15_ASM` | on | scalar inversion in baseinv batch | production default | no public ABI change | full KEM correctness |
| `GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP` | off | encap `gt_encap_basemul_add_tobytes_contract` | production-safe opt-in | yes, but byte-contract only and immediately consumed by `poly_tobytes` | `check_gt_direct32_q31_release_candidate` |
| `GT_DIRECT32_Q31_RELEASE_GUARD_NOINLINE` | off | release guard build only | check-only | no | nm/objdump call-site guard |
| `GT_USE_STOCK_BASEMUL_ADD_EXPERIMENTAL` | off | benchmark-only stock add drop-in | negative control | yes; correctness-incompatible on GT operands | gate harness reports mismatch |
| `GT_USE_DIRECT32_BASEMUL_ADD_EXPERIMENTAL` | off | benchmark-only direct32 C prototype | experimental | yes; not production | gate harness |
| `GT_PRODUCTION_USE_RMINUS1_CREP3_DECAP` | off | fused rminus1 InvNTT+crep3 decap | stopped experiment | yes | crep3 fused PMU/correctness docs |
| `GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_DECAP` | off | rminus1 stage123 scratch split | stopped experiment | yes | component/fusion docs |
| `GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_CREP3_DECAP` | off | scratch split plus crep3 fused | stopped experiment | yes | component/fusion docs |
| `GT_PRODUCTION_USE_TUPLE_DECAP` | off | tuple decap | experimental/dead | yes | historical tests only |
| `GT_PRODUCTION_USE_PACK_TUPLE_DECAP` | off | block-major to tuple adapter decap | experimental/dead | yes | historical tests only |
| `GT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_KEM` and related `GT_TMVP_USE_*` tuple flags | off | Candidate A direct tuple KEM | benchmark-only / experimental | yes | candidate-specific tests only |
| `GT_TMVP_ENABLE_CANDIDATE_B_BPQ_KEM` and BPQ/TMVP flags | off | BPQ/TMVP KEM candidates | experimental/dead | yes | candidate-specific tests only |

Non-macro benchmark-only paths visible in the Makefile include NTT shadow-base
rowspec wrappers, basemul oldstore wrappers, and the `ldrtrn_noadd` wrapper.
They are not part of `GT_PRODUCTION_KEM_SOURCES`.

## Candidate classification

| candidate | classification | linked to production? | correctness | PMU status | decision |
| --- | --- | ---: | --- | --- | --- |
| current `gt_production` | production default | yes | pass | fastest production default in this run | keep as default |
| Q31 direct32 encap opt-in | production-safe opt-in | no by default; yes only when gate is enabled | release guard pass; KEM gate pass | direct add -429.575 cycles; full encap -467.385 cycles in Q31 gate harness | keep frozen as encap-only byte-contract opt-in |
| KPQC final no-CE | historical comparison baseline | separate source, not GT production | pass in generic KEM bench | slower than current GT in all three KEM APIs | baseline only |
| legacy/original `VARIANT=gt` | historical GT baseline | not current production | pass | keygen much slower than current production; encap/decap close but slower | baseline only |
| `VARIANT=gt_opt` | unavailable historical variant in current tree | no | not buildable | GNU as rejects symbolic `base_gt.opt.s` macro forms | not a valid current linked comparison |
| InvNTT Stage45 all4 Slothy candidate | stopped/regression | no | correctness pass in prior campaign | PMU regression/non-reproducible | not best, do not extend |
| generic/rminus1 basemul one-loop Slothy | stopped/regression | no | correctness pass in prior campaign | PMU regression | needs new strategy, not active |
| Forward NTT local Slothy candidates | needs structural strategy | no | no promoted correctness-passing production candidate | no production PMU win | not production |
| rowspec NTT | benchmark-only stopped | no | historical | PMU regression / not production output route | do not use |
| oldstore basemul wrappers | benchmark-only | no | historical | oldstore comparison only | keep only for regression guard |
| `ldrtrn_noadd` basemul | benchmark-only stopped | no | correctness pass but slower | PMU regression | do not extend |
| rowpack / tuple / BPQ / TMVP candidates | experimental/dead | no | candidate-local only | not current fastest production | do not classify as production fastest |
| stock basemul_add drop-in | benchmark-only negative control | no | fail on GT operands | diagnostic only | reject |

## Correctness and PMU commands

Q31 release guard and Q31 gate:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  check_gt_direct32_q31_release_candidate

make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_stock_basemul_add_gate_pmu SUDO= CORE=3 \
  GT_STOCK_BASEMUL_ADD_GATE_PMU_NINPUTS=4096
```

Current GT component profile:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

Generic KEM matrix:

```sh
# KPQC final no-CE, from a /tmp dereferenced source copy plus bench-only ntt.h.
make CYCLES=PERF VARIANT=stock BENCH_MODE=<kem_keygen|kem_enc|kem_dec> \
  USE_SHAKE_ASM=0 \
  NTRUPLUS=/tmp/kpqc_final_aarch64_bench_src \
  NTESTS=31 NITERATIONS=5000 NWARMUP=100

# Legacy GT baseline.
make CYCLES=PERF VARIANT=gt BENCH_MODE=<kem_keygen|kem_enc|kem_dec> \
  USE_SHAKE_ASM=0 NTESTS=31 NITERATIONS=5000 NWARMUP=100

# Current GT production default.
make CYCLES=PERF VARIANT=gt_production BENCH_MODE=<kem_keygen|kem_enc|kem_dec> \
  USE_SHAKE_ASM=0 NTESTS=31 NITERATIONS=5000 NWARMUP=100
```

For Q31 generic KEM, a `/tmp/kem_q31_standard.c` wrapper was used to enable
only `GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP` while preserving the
current GT production source list.  This wrapper was not committed and does not
change the repo default.

All reported generic KEM binaries passed the harness correctness gate.  The
Q31 gate reported:

```text
r1_q31_regression_pass=1
release_guard_pass=1
direct32_q31_correctness,total_mismatches=0,valid_cases=4096
stock_dropin_correctness,total_mismatches=4832702,valid_cases=4096
layout_incompatibility=1,reason=stock_poly_basemul_add_output_differs_on_GT_operands
```

Current GT component profile reported:

```text
correctness,total_mismatches=0,valid_cases=64
```

## KEM PMU comparison

These full KEM rows are from the same generic `bench.c` harness using
`CYCLES=PERF`.  Percentiles are cycle counts per call.

| variant | keygen p50 | keygen p10/p90 | encap p50 | encap p10/p90 | decap p50 | decap p10/p90 | correctness | notes |
| --- | ---: | --- | ---: | --- | ---: | --- | --- | --- |
| KPQC final no-CE | 39968 | 39967 / 39969 | 39097 | 39095 / 39099 | 35198 | 35196 / 35212 | pass | actual KPQC final source copied to `/tmp`; NO_CE hash path |
| original GT (`VARIANT=gt`) | 98138 | 98137 / 98139 | 37980 | 37978 / 37990 | 34230 | 34229 / 34233 | pass | legacy Makefile GT path using `base_gt.S` and reference baseinv ABI |
| current GT production default | 38898 | 38890 / 38912 | 37800 | 37791 / 37804 | 33129 | 33126 / 33135 | pass | `VARIANT=gt_production` |
| current GT + Q31 opt-in | 38915 | 38913 / 38922 | 37690 | 37687 / 37698 | 33072 | 33071 / 33076 | pass | benchmark-only tmp wrapper; only encap path is semantically changed |

Q31 gate harness, which directly compares current vs opt-in in one binary:

| window | current cycles/call | q31 cycles/call | delta cycles | delta | current instr/call | q31 instr/call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| direct `poly_basemul_add` | 2913.430 | 2483.855 | -429.575 | -14.75% | 2799.001 | 2222.001 |
| full encap | 38803.357 | 38335.972 | -467.385 | -1.20% | 106452.001 | 105876.001 |

Current GT component context:

| component | cycles/call | instr/call |
| --- | ---: | ---: |
| `keypair_total` | 39191.888 | 81927.000 |
| `encap_total` | 38104.289 | 106454.000 |
| `decap_total` | 33278.455 | 75190.000 |
| `keygen_polyinv_scaled_x2` | 10023.884 | 8832.000 |
| `encap_basemul_add` | 2864.564 | 2800.000 |
| `decap_basemul_rminus1` | 2028.085 | 1909.000 |
| `decap_invntt_rminus1` | 4024.582 | 5074.000 |
| `decap_verify_basemul` | 2823.372 | 2485.000 |

## Fastest by category

| category | fastest variant | reason | caveat |
| --- | --- | --- | --- |
| production default | current `gt_production` | fastest default linked KEM path in keygen, encap, and decap against KPQC final no-CE and legacy `gt` | Q31 is not default |
| production-safe opt-in | current `gt_production` + Q31 encap gate | Q31 release guard passes; full encap improves by about 1.2% in the direct gate harness | encap-only byte contract; not a generic `poly_basemul_add` replacement |
| benchmark-only | no active local-window Slothy candidate | recent InvNTT, basemul, and Forward NTT local Slothy routes are stopped or need structural strategy | benchmark-only candidates are not production fastest |
| historical baseline | KPQC final no-CE | actual KPQC final source path measured through the shared bench harness | CE/f1600 is not used on this Pi5 run |

## Interpretation

Fastest production-default KEM path right now:

```text
current gt_production
```

It is faster than the KPQC final no-CE baseline in this run:

| API | KPQC final no-CE | current GT production | delta | speedup vs KPQC |
| --- | ---: | ---: | ---: | ---: |
| keygen | 39968 | 38898 | -1070 | 2.68% |
| encap | 39097 | 37800 | -1297 | 3.32% |
| decap | 35198 | 33129 | -2069 | 5.88% |

Fastest production-safe opt-in:

```text
current gt_production + GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
```

This is an encap-only byte-contract opt-in.  It is not connected to production
by default, not exposed through public headers, and not used by decap or generic
arithmetic callers.

Current GT production compared with the legacy `VARIANT=gt` baseline:

| API | legacy `gt` | current GT production | delta | speedup vs legacy GT |
| --- | ---: | ---: | ---: | ---: |
| keygen | 98138 | 38898 | -59240 | 60.36% |
| encap | 37980 | 37800 | -180 | 0.47% |
| decap | 34230 | 33129 | -1101 | 3.22% |

The keygen change is dominated by the production scaled/batch baseinv path.
Encap is now mostly hash-dominated, so even a real local Q31 basemul-add win
only moves full encap by about 1.2% in the direct gate harness.

No Slothy candidate is connected to production.  The stopped candidates that
should no longer be considered active fastest paths are:

```text
InvNTT Stage45 canonical stripes / all4
generic/rminus1 basemul source-order one-loop
Forward NTT local Slothy candidates
rowspec
oldstore
ldrtrn_noadd
rowpack
tuple
BPQ/TMVP routes
stock poly_basemul_add drop-in
```

