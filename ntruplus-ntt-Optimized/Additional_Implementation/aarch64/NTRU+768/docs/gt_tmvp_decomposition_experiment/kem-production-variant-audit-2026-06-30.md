# KEM production variant audit

Date: 2026-06-30

Scope: production gate promotion plus focused audit/benchmark.  This pass
promotes only the existing Q31 direct32 encap byte-contract path into the
`gt_production` default.  It does not run Slothy, does not promote
benchmark-only candidates, does not touch `polyinv()`, and does not change Q31
assembly semantics.

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
GT_PRODUCTION_KEM_SOURCES + GT_PRODUCTION_Q31_ENCAP_ASM =
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
  ntruplus/asm/base_gt_add32_direct32_q31_tobytes_contract_prototype.S

VARIANT_CFLAGS =
  -DGT_PRODUCTION_USE_SCALED_KEYPAIR
  -DGT_PRODUCTION_USE_RMINUS1_DECAP
  -DGT_BASEINV_BATCH_USE_ASM_FINISH
  -DGT_BASEINV_USE_FQINV15_ASM
  -DGT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
  -DBENCH_VARIANT_GT=1
```

The previous no-Q31 production behavior is preserved as:

```text
VARIANT=gt_production_no_q31
```

It uses the same `GT_PRODUCTION_KEM_SOURCES` and production flags, but does not
link `GT_PRODUCTION_Q31_ENCAP_ASM` and does not define
`GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP`.

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
poly_basemul_add_encap_direct32_q31_tobytes_contract_prototype
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
| Basemul add | `poly_basemul_add` | `asm/base_gt_add32_full_pipeline_inline_wrapper.S` | yes | none | generic symbol remains the production arithmetic-correct implementation |
| Q31 encap byte-contract add | `poly_basemul_add_encap_direct32_q31_tobytes_contract_prototype` | `asm/base_gt_add32_direct32_q31_tobytes_contract_prototype.S` | yes in `gt_production`; absent in `gt_production_no_q31` | `GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP` | encap-only; output is immediately consumed by `poly_tobytes`; not a generic `poly_basemul_add` replacement |
| rminus1 basemul | `poly_basemul_rminus1` | `asm/base_gt_rminus1_opt_wrapper.S` | yes | `GT_PRODUCTION_USE_RMINUS1_DECAP` | paired only with `poly_invntt_from_rminus1` |
| Scaled keypair basemul | `poly_basemul_scaled_r_input` | `asm/base_gt_scaled_r_input_opt_wrapper.S` | yes | `GT_PRODUCTION_USE_SCALED_KEYPAIR` | keygen-only scaled-r input contract |
| Baseinv / polyinv path | `poly_baseinv_scaled_r` | `poly_gt_baseinv_batch.c`, `baseinv_batch_finish_loop_n1.S`, `gt_fqinv15.S` | yes | `GT_PRODUCTION_USE_SCALED_KEYPAIR`, `GT_BASEINV_BATCH_USE_ASM_FINISH`, `GT_BASEINV_USE_FQINV15_ASM` | closed-form/batch baseinv path used by current keygen |
| pack | `poly_tobytes`, `poly_frombytes` | `asm/slothy/support_kernels/support_kernels.n1.opt.S` | yes | none | stock support API replaced by Slothy support kernel in `gt_production` |
| crepmod3 | `poly_crepmod3` | `asm/slothy/support_kernels/support_kernels.n1.opt.S` | yes | none | separate decap recovery reduction; fused crep3 variants are not default |

Default current GT production contains both `poly_basemul_add` and
`poly_basemul_add_encap_direct32_q31_tobytes_contract_prototype` at distinct
addresses.  The promoted default binary has exactly one call into the Q31
symbol from the encap path (`crypto_kem_enc_derand.isra.0` after inlining the
contract helper).  The no-Q31 fallback binary contains no `q31` symbol.

The release guard binary keeps the helper non-inlined and verifies that the
only Q31 call site is `gt_encap_basemul_add_tobytes_contract`.

## Gate and macro audit

| gate / macro | default in `gt_production` | affected path | status | changes KEM output path? | correctness guard |
| --- | ---: | --- | --- | --- | --- |
| `GT_PRODUCTION_USE_SCALED_KEYPAIR` | on | keygen `KEYPAIR_BASEINV`, `KEYPAIR_BASEMUL` | production default | yes, internal keygen contract only | full KEM correctness |
| `GT_PRODUCTION_USE_RMINUS1_DECAP` | on | decap `poly_basemul_rminus1` -> `poly_invntt_from_rminus1` | production default | yes, private decap temporary only | full KEM correctness |
| `GT_BASEINV_BATCH_USE_ASM_FINISH` | on | `poly_baseinv_scaled_r` finish loop | production default | no public ABI change | full KEM correctness |
| `GT_BASEINV_USE_FQINV15_ASM` | on | scalar inversion in baseinv batch | production default | no public ABI change | full KEM correctness |
| `GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP` | on | encap `gt_encap_basemul_add_tobytes_contract` | production default encap byte-contract path | yes, but byte-contract only and immediately consumed by `poly_tobytes` | `check_gt_direct32_q31_release_candidate` |
| `GT_DIRECT32_Q31_RELEASE_GUARD_NOINLINE` | off | release guard build only | check-only | no | nm/objdump call-site guard |
| `GT_USE_STOCK_BASEMUL_ADD_EXPERIMENTAL` | off | benchmark-only stock add drop-in | negative control | yes; correctness-incompatible on GT operands | gate harness reports mismatch |
| `GT_USE_DIRECT32_BASEMUL_ADD_EXPERIMENTAL` | off | benchmark-only direct32 C prototype | experimental | yes; not production | gate harness |
| `VARIANT=gt_production_no_q31` | off unless selected | previous GT production behavior without Q31 | fallback / comparison path | yes, disables Q31 encap byte-contract | generic KEM bench correctness |
| `GT_PRODUCTION_USE_RMINUS1_CREP3_DECAP` | removed | fused rminus1 InvNTT+crep3 decap | removed experiment | yes | crep3 fused PMU/correctness docs |
| `GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_DECAP` | off | rminus1 stage123 scratch split | stopped experiment | yes | component/fusion docs |
| `GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_CREP3_DECAP` | removed | scratch split plus crep3 fused | removed experiment | yes | component/fusion docs |
| `GT_PRODUCTION_USE_TUPLE_DECAP` | off | tuple decap | removed experiment | yes | historical only |
| `GT_PRODUCTION_USE_PACK_TUPLE_DECAP` | off | block-major to tuple adapter decap | removed experiment | yes | historical only |

Non-macro benchmark-only paths visible in the Makefile include basemul oldstore
wrappers.  They are not part of `GT_PRODUCTION_KEM_SOURCES`.

## Candidate classification

| candidate | classification | linked to production? | correctness | PMU status | decision |
| --- | --- | ---: | --- | --- | --- |
| current `gt_production` | production default with Q31 encap byte-contract | yes | pass | fastest production default in this run | keep as default |
| `gt_production_no_q31` | fallback / comparison path | not default | pass | retained for no-Q31 comparison and rollback | keep available |
| Q31 direct32 encap | production default encap byte-contract path | yes in `gt_production`; absent in `gt_production_no_q31` | release guard pass; KEM gate pass | direct add -417.952 cycles; full encap -468.065 cycles in Q31 gate harness | keep default, but do not use as generic basemul replacement |
| KPQC final no-CE | historical comparison baseline | separate source, not GT production | pass in generic KEM bench | slower than current GT in all three KEM APIs | baseline only |
| legacy/original `VARIANT=gt` | historical GT baseline | not current production | pass in previous audit | not rebenchmarked in the Q31 promotion matrix | baseline only |
| `VARIANT=gt_opt` | unavailable historical variant in current tree | no | not buildable | GNU as rejects symbolic `base_gt.opt.s` macro forms | not a valid current linked comparison |
| InvNTT Stage45 all4 Slothy candidate | removed experiment | no | correctness pass in prior campaign | PMU regression/non-reproducible | removed from benchmark wiring |
| generic/rminus1 basemul one-loop Slothy | stopped/regression | no | correctness pass in prior campaign | PMU regression | needs new strategy, not active |
| Forward NTT local Slothy candidates | needs structural strategy | no | no promoted correctness-passing production candidate | no production PMU win | not production |
| rowspec NTT | removed experiment | no | historical | PMU regression / not production output route | do not use |
| oldstore basemul wrappers | benchmark-only | no | historical | oldstore comparison only | keep only for regression guard |
| `ldrtrn_noadd` basemul | removed experiment | no | correctness pass but slower | PMU regression | removed from benchmark wiring |
| rowpack / tuple / BPQ / TMVP candidates | removed experiments | no | historical only | not current fastest production | do not classify as production fastest |
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
# Previous GT production behavior without Q31.
make CYCLES=PERF VARIANT=gt_production_no_q31 \
  BENCH_MODE=<kem_keygen|kem_enc|kem_dec> \
  USE_SHAKE_ASM=0 NTESTS=31 NITERATIONS=5000 NWARMUP=100

# Current GT production default with Q31 promoted.
make CYCLES=PERF VARIANT=gt_production \
  BENCH_MODE=<kem_keygen|kem_enc|kem_dec> \
  USE_SHAKE_ASM=0 NTESTS=31 NITERATIONS=5000 NWARMUP=100

# KPQC final no-CE, from a /tmp dereferenced source copy plus bench-only ntt.h.
make CYCLES=PERF VARIANT=stock BENCH_MODE=<kem_keygen|kem_enc|kem_dec> \
  USE_SHAKE_ASM=0 \
  NTRUPLUS=/tmp/kpqc_final_aarch64_bench_src \
  NTESTS=31 NITERATIONS=5000 NWARMUP=100
```

All reported generic KEM binaries passed the harness correctness gate.  The
Q31 gate reported:

```text
r1_q31_regression_pass=1
release_guard_pass=1
generic_poly_basemul_add_symbols=1
direct32_q31_symbols=1
direct32_q31_call_sites=1
direct32_q31_call_site=gt_encap_basemul_add_tobytes_contract
generic_poly_basemul_add_overwritten=0
decap_or_arithmetic_q31_callers=0
public_headers_with_q31_symbol=0
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
| `gt_production_no_q31` | 38931 | 38929 / 38942 | 37740 | 37733 / 37754 | 33107 | 33101 / 33116 | pass | previous GT production behavior retained as fallback |
| `gt_production` Q31 default | 38902 | 38892 / 38908 | 37740 | 37735 / 37744 | 33126 | 33122 / 33136 | pass | Q31 promoted; keygen/decap differences are measurement noise |
| KPQC final no-CE | 39961 | 39953 / 39971 | 39083 | 39080 / 39085 | 35197 | 35192 / 35211 | pass | actual KPQC final source copied to `/tmp`; NO_CE hash path |

Q31 gate harness, which directly compares no-Q31 vs Q31 in one binary:

| window | no-Q31 cycles/call | Q31 cycles/call | delta cycles | delta | no-Q31 instr/call | Q31 instr/call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| direct `poly_basemul_add` | 2893.655 | 2475.703 | -417.952 | -14.44% | 2799.001 | 2222.001 |
| full encap | 38795.993 | 38327.928 | -468.065 | -1.21% | 106452.001 | 105876.001 |

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
| production default | current `gt_production` with Q31 encap byte-contract enabled | fastest default linked KEM path against KPQC final no-CE; Q31 gate gives about 1.2% full-encap improvement over the no-Q31 path | Q31 affects encap only and is not a generic `poly_basemul_add` replacement |
| fallback / comparison | `gt_production_no_q31` | preserves previous GT production behavior for rollback and measurement | not the default |
| benchmark-only | no active local-window Slothy candidate | recent InvNTT, basemul, and Forward NTT local Slothy routes are stopped or need structural strategy | benchmark-only candidates are not production fastest |
| historical baseline | KPQC final no-CE | actual KPQC final source path measured through the shared bench harness | CE/f1600 is not used on this Pi5 run |

## Interpretation

Fastest production-default KEM path right now:

```text
current gt_production with GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
```

It is faster than the KPQC final no-CE baseline in this focused run:

| API | KPQC final no-CE | current GT production | delta | speedup vs KPQC |
| --- | ---: | ---: | ---: | ---: |
| keygen | 39961 | 38902 | -1059 | 2.65% |
| encap | 39083 | 37740 | -1343 | 3.44% |
| decap | 35197 | 33126 | -2071 | 5.88% |

Compared with the no-Q31 fallback, Q31 only has an intended semantic effect on
encap.  The generic full-KEM `CYCLES=PERF` p50 run did not resolve a difference
between no-Q31 and Q31 encap (`37740` vs `37740` cycles), while the direct
same-binary Q31 gate measured a full-encap win of `-468.065 cycles/call`
(`-1.21%`).  Treat keygen and decap differences in the focused matrix as
measurement noise.

The Q31 contract after promotion remains:

```text
scope: encap only
consumer: immediate poly_tobytes(ct, &c)
not generic poly_basemul_add replacement
not used by decap
not used by generic arithmetic callers
public header exposure: none
```

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
