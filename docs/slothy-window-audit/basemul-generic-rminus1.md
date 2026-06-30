# Generic/rminus1 Basemul Slothy Campaign Audit

Date: 2026-06-30

Scope: benchmark-only Slothy exploration for GT production basemul local
cleanup.  Production defaults were not changed.  Q31 was not reused because
this target requires arithmetic-correct output, including decap consumers.

## Production Entry Points

| function | caller API | implementation path | input layout | output layout / contract | baseline |
| --- | --- | --- | --- | --- | --- |
| `poly_basemul` | decap verify, generic arithmetic | `asm/base_gt_opt_noadd_wrapper.S` includes `asm/base_gt.opt.s` | GT block-major, 24 loop blocks, `ld4` quartic tuple load, `gt_rowbitrev_lambda` order | arithmetic-correct GT block-major output, final corrected representative | direct PMU 2910.593 cycles/call; decap verify component 2823.360 cycles |
| `poly_basemul_rminus1` | decap `c * f` before `poly_invntt_from_rminus1` | `asm/base_gt_rminus1_opt_wrapper.S` includes `asm/base_gt.opt.s` with `GT_BASEMUL_STORE_RMINUS1` | same GT block-major input | raw `R^-1`/rminus1 output for `poly_invntt_from_rminus1`; not generic output | direct PMU 2145.958 cycles/call; decap component 2028.196 cycles |
| `poly_basemul_scaled_r_input` | keygen public arithmetic / scaled input path | `asm/base_gt_scaled_r_input_opt_wrapper.S` includes `asm/base_gt.opt.s` with `GT_BASEMUL_STORE_RMINUS1` | same GT block-major `a`; second operand is pre-scaled by `R` | arithmetic-correct product through scaled-input plus raw-store contract | direct PMU 2131.955 cycles/call; keygen public arithmetic x2 4086.035 cycles |
| `poly_basemul_add` / `poly_basemul_add32` | encap ciphertext arithmetic | `asm/base_gt_add32_full_pipeline_inline_wrapper.S` | GT block-major plus addend `c` | generic arithmetic-correct add output; Q31 byte-contract helper is encap-only and not reusable here | encap component 2864.475 cycles |

## Candidate Windows

The first campaign intentionally used small one-loop windows:

| window | source used for Slothy input | instructions | memory shape | risk flags | recommendation |
| --- | --- | ---: | --- | --- | --- |
| `base_gt_rminus1_loop` | `asm/base_gt.S` after C preprocessing, one 8-quartic loop | 77 | `ld1 lambda`, two `ld4` operand loads, final raw `st4` | source-order extraction, not production-scheduled `base_gt.opt.s` | reject after PMU regression |
| `base_gt_generic_loop` | `asm/base_gt.S` after C preprocessing, one 8-quartic loop | 101 | same loads plus final Montgomery/reduction and corrected `st4` | source-order extraction, not production-scheduled `base_gt.opt.s` | reject after PMU regression |
| `poly_basemul_add` core | not run in this campaign | n/a | add32 full pipeline with accumulator/addend contract | distinct add32 dataflow; should not use Q31 outside byte-contract encap path | later audit only |

Boundary policy followed: no splits inside product/reduction chains, lane
transpose/store groups, lambda load immediate-use chains, or pointer updates.

## Slothy Runs

Slothy host: `pinhao@172.25.166.141:51208`

Commands:

```sh
/usr/bin/timeout 3600 env SLOTHY_PATH=/home/pinhao/slothy PYTHONPATH=/home/pinhao/slothy \
  /home/pinhao/slothy/venv/bin/python asm/slothy/optimize.py \
  --input window_inputs/base_gt_rminus1_loop_marked.s \
  --output window_outputs/base_gt_rminus1_loop.n1.slothy.candidate.s \
  --target n1 --stalls 256 \
  --region slothy_start_base_gt_rminus1_loop:slothy_end_base_gt_rminus1_loop

/usr/bin/timeout 3600 env SLOTHY_PATH=/home/pinhao/slothy PYTHONPATH=/home/pinhao/slothy \
  /home/pinhao/slothy/venv/bin/python asm/slothy/optimize.py \
  --input window_inputs/base_gt_generic_loop_marked.s \
  --output window_outputs/base_gt_generic_loop.n1.slothy.candidate.s \
  --target n1 --stalls 256 \
  --region slothy_start_base_gt_generic_loop:slothy_end_base_gt_generic_loop
```

Results:

| window | Slothy status | model cycles | minimum stalls | wall time |
| --- | --- | ---: | ---: | ---: |
| `base_gt_rminus1_loop` | OPTIMAL, selfcheck OK | 82 | 62 | 5.93s |
| `base_gt_generic_loop` | OPTIMAL, selfcheck OK | 121 | 95 | 6.66s |

## Pi5 PMU

Pi5 command:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_basemul_variants_pmu SUDO= CORE=3
```

Correctness:

```text
correctness,total_mismatches=0
```

PMU table:

| variant | cycles/call | instr/call | delta vs production | decision |
| --- | ---: | ---: | ---: | --- |
| `poly_basemul` | 2910.593 | 2489 | baseline | baseline |
| `poly_basemul_slothy_campaign` | 2963.068 | 2489 | +52.475 | reject |
| `poly_basemul_rminus1` | 2145.958 | 1913 | baseline | baseline |
| `poly_basemul_rminus1_slothy_campaign` | 2180.158 | 1913 | +34.200 | reject |
| `poly_basemul_scaled_r_input` | 2131.955 | 1913 | baseline | baseline |
| `poly_basemul_scaled_r_input_slothy_campaign` | 2170.086 | 1913 | +38.131 | reject |

Production KEM component baseline was also rerun:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

Correctness:

```text
correctness,total_mismatches=0,valid_cases=64
```

Relevant production components from that run:

| component | cycles/call | instr/call |
| --- | ---: | ---: |
| `decap_basemul_rminus1` | 2028.093 | 1909 |
| `decap_verify_basemul` | 2823.359 | 2485 |
| `encap_basemul_add` | 2864.627 | 2800 |
| `keygen_public_arithmetic_x2` | 4083.382 | 3822 |

## Projection

The candidates regress locally, so the projected API impact is negative:

| candidate | local delta | decap projection | encap projection | keygen projection |
| --- | ---: | ---: | ---: | ---: |
| generic verify basemul | +52.475 cycles | +0.16% decap | n/a | n/a |
| rminus1 basemul | +34.200 cycles | +0.10% decap | n/a | n/a |
| scaled-r input | +38.131 cycles | n/a | n/a | +0.10% keygen if used twice is about +0.19% |

## Decision

No candidate from this campaign is viable.  The generated outputs were
correct, but slower than production and are not committed as best artifacts.

The likely reason is that the attempted windows were canonical/source-order
one-loop slices, while production already uses `base_gt.opt.s`, a scheduled
body with the current final-store contract.  Do not continue this exact
source-order loop route.

Tracking status is now `needs_new_strategy`, not active immediate rerun.  Only
revisit this target with a wider production-scheduled multi-loop/window or a
structural DAG change.  Do not reuse Q31 for this target, because decap and
generic arithmetic consumers require arithmetic-correct polynomial output, not
only byte-equivalent `poly_tobytes` output.
