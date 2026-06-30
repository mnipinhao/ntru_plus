# Slothy Campaigns

## INVNTT-RM1-ROW1-STAGE45-STRIPES-CAMPAIGN-001

Date: 2026-06-30

Scope: InvNTT rminus1 ROW1-STAGE45 stripe windows.  This campaign used the
benchmark-only materialized per-stripe Slothy input and did not change
production defaults.

Hosts:

- Slothy: `pinhao@172.25.166.141:51208`
- Pi5: `pi@100.99.191.9`

Source commits:

- source marker commit: `b44c5cd`
- materialization commit: `f13d41b1`
- generated candidate commit: this campaign commit

Slothy command template:

```sh
timeout 3600 env SLOTHY_PATH=/home/pinhao/slothy PYTHONPATH=/home/pinhao/slothy \
  /home/pinhao/slothy/venv/bin/python asm/slothy/optimize.py \
  --input window_inputs/invntt_rminus1_row1_stage45_stripes_marked.s \
  --output window_outputs/<candidate>.n1.slothy.candidate.s \
  --target n1 --stalls 256 \
  --region <start>:<end>
```

Candidate windows attempted:

| window | status | model result | wall time | kept |
| --- | --- | --- | ---: | --- |
| `STRIPES2-3` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 5.173500s | yes |
| `STRIPES4-5` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 10.624306s | no |
| `STRIPES0-1` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 14.457421s | no |
| `STRIPES6-7` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 8.408707s | no |

Best candidate:

`ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/window_outputs/invntt_rminus1_row1_stage45_stripes2_3.n1.slothy.candidate.s`

The other generated candidate outputs were not committed.

Pi5 validation commands:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_invntt_pmu SUDO= CORE=3
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

Correctness:

```text
bench_gt_invntt_pmu: correctness,total_mismatches=0
bench_gt_kem_component_profile_pmu: correctness,total_mismatches=0,valid_cases=64
```

PMU summary:

| variant | correctness | cycles/call | instr/call | notes |
| --- | --- | ---: | ---: | --- |
| production `poly_invntt_from_rminus1` | pass | 4144.795 | 5078 | production baseline, no candidate wiring |
| materialized canonical ROW1-STAGE45 row1 | pass | 624.673 | 357 | benchmark-only per-stripe source |
| materialized + Slothy `STRIPES2-3` | pass | 616.679 | 357 | benchmark-only, -7.994 cycles/call |
| KEM component `decap_invntt_rminus1` | pass | 4024.731 | 5074 | production component profile |

Decision:

Keep `STRIPES2-3` as the benchmark-only current best.  It improves the
materialized row1 canonical microbench by about 1.28%, but it is not a
production InvNTT improvement because the materialized per-stripe input is not
the production cross-stripe scheduled row.  Do not promote to production.

Next action:

Before extending to production, choose between building a combined materialized
row1 candidate that uses scheduled stripe-pairs for all row1 stripes, or cloning
the same materialized-window method to row0/row2.  The 337-instruction row-level
window remains split-heuristic-only and was not run in this campaign.

## INVNTT-RM1-STAGE45-SCALING-CAMPAIGN-002

Date: 2026-06-30

Scope: InvNTT rminus1 ROW1-STAGE45 scaling.  This campaign answers whether the
single `STRIPES2-3` materialized microbench win scales to all four canonical
row1 stripe-pairs, and whether the actual production-scheduled 337-instruction
ROW1-STAGE45 window can be handled by Slothy split heuristic.

This campaign is benchmark-only.  It does not change production defaults, Q31,
basemul-to-InvNTT fusion, polyinv, or hash/copy residuals.

Hosts:

- Slothy: `pinhao@172.25.166.141:51208`
- Pi5: `pi@100.99.191.9`

Source commits:

- source marker commit: `b44c5cd`
- materialization commit: `f13d41b1`
- previous campaign commit: `a5e34df6`
- generated candidate commit: this campaign commit

Canonical stripe command template:

```sh
/usr/bin/timeout 3600 env SLOTHY_PATH=/home/pinhao/slothy PYTHONPATH=/home/pinhao/slothy \
  /home/pinhao/slothy/venv/bin/python asm/slothy/optimize.py \
  --input window_inputs/invntt_rminus1_row1_stage45_stripes_marked.s \
  --output window_outputs/<candidate>.n1.slothy.candidate.s \
  --target n1 --stalls 256 \
  --region <start>:<end>
```

All-four artifact command:

```sh
/usr/bin/timeout 3600 env SLOTHY_PATH=/home/pinhao/slothy PYTHONPATH=/home/pinhao/slothy \
  /home/pinhao/slothy/venv/bin/python asm/slothy/optimize.py \
  --input window_inputs/invntt_rminus1_row1_stage45_stripes_marked.s \
  --output window_outputs/invntt_rminus1_row1_stage45_all4.n1.slothy.candidate.s \
  --target n1 --stalls 256 \
  --region slothy_start_invntt_rm1_row1_stage45_stripes0_1:slothy_end_invntt_rm1_row1_stage45_stripes0_1 \
  --region slothy_start_invntt_rm1_row1_stage45_stripes2_3:slothy_end_invntt_rm1_row1_stage45_stripes2_3 \
  --region slothy_start_invntt_rm1_row1_stage45_stripes4_5:slothy_end_invntt_rm1_row1_stage45_stripes4_5 \
  --region slothy_start_invntt_rm1_row1_stage45_stripes6_7:slothy_end_invntt_rm1_row1_stage45_stripes6_7
```

Canonical windows attempted:

| window | status | model result | wall time |
| --- | --- | --- | ---: |
| `STRIPES0-1` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 6.998595s |
| `STRIPES2-3` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 8.310964s |
| `STRIPES4-5` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 8.316333s |
| `STRIPES6-7` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 16.192300s |

All-four artifact run:

| region | status | model result | wall time |
| --- | --- | --- | ---: |
| `STRIPES0-1` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 11.624899s |
| `STRIPES2-3` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 8.802855s |
| `STRIPES4-5` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 7.512587s |
| `STRIPES6-7` | parse pass, OPTIMAL, selfcheck OK | 88 cycles, 67 stalls | 14.771695s |

Combined candidate:

`ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/window_outputs/invntt_rminus1_row1_stage45_all4.n1.slothy.candidate.s`

Pi5 validation commands:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_invntt_pmu SUDO= CORE=3
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

Correctness:

```text
bench_gt_invntt_pmu: correctness,total_mismatches=0
bench_gt_kem_component_profile_pmu: correctness,total_mismatches=0,valid_cases=64
```

Canonical row1 Stage45 PMU:

| variant | correctness | cycles/call | instr/call | p10 cycles | p90 cycles | decision |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| canonical row1 Stage45 baseline | pass | 543.266 | 357 | 491.609 | 545.260 | baseline |
| row1 + `STRIPES2-3` Slothy | pass | 612.778 | 357 | 608.972 | 616.264 | regressed |
| row1 + all-four Slothy stripes | pass | 625.327 | 357 | 611.851 | 629.409 | regressed |

The current InvNTT PMU harness reports `min/p10/median/p90`, not IQR.  A repeat
run showed the same direction:

| variant | cycles/call | instr/call |
| --- | ---: | ---: |
| canonical row1 Stage45 baseline | 542.135 | 357 |
| row1 + `STRIPES2-3` Slothy | 607.505 | 357 |
| row1 + all-four Slothy stripes | 625.103 | 357 |

Production-scheduled fullrow stress command:

```sh
/usr/bin/timeout 3600 env SLOTHY_PATH=/home/pinhao/slothy PYTHONPATH=/home/pinhao/slothy \
  /home/pinhao/slothy/venv/bin/python asm/slothy/optimize.py \
  --input invntt_opt.production.s \
  --output window_outputs/invntt_rminus1_row1_stage45.fullrow.n1.slothy.candidate.s \
  --target n1 --stalls 256 \
  --split-heuristic --split-stepsize 0.05 --split-factor 8.0 \
  --region slothy_start_invntt_block_row1_stage45:slothy_end_invntt_block_row1_stage45
```

Fullrow stress result:

```text
Instructions in body: 337
status: parser fail
first unsupported instruction: adr x3, invntt32_stage45_consts
candidate artifact: none
PMU claim: none
```

Projection from all-four row1 result:

```text
row1 saving = 543.266 - 625.327 = -82.061 cycles
projected 3-row saving = -82.061 * 3 = -246.183 cycles
projected full decap saving = -246.183 / 33285.358 = -0.74%
```

The projection is negative, so it is a projected regression rather than a
saving.

Decision:

Stop the canonical InvNTT rminus1 ROW1-STAGE45 stripe route for now.  The
all-four materialized candidate is correct but slower, and the production
fullrow split-heuristic route is blocked by parser support for `adr`.  Do not
extend this canonical stripe route to row0/row2.  If InvNTT is revisited, the
next useful work is either parser/model support for the production fullrow
addressing pattern or a different window contract; do not promote any candidate
from this campaign.

## BASEMUL-GENERIC-RMINUS1-CAMPAIGN-001

Date: 2026-06-30

Scope: generic/rminus1 basemul local cleanup.  This campaign was
benchmark-only, kept production defaults unchanged, did not touch Q31, did not
start InvNTT fusion, did not touch polyinv, and did not optimize hash/copy
residuals.

Hosts:

- Slothy: `pinhao@172.25.166.141:51208`
- Pi5: `pi@100.99.191.9`

Source commits:

- previous campaign commit: `6be645e2`
- generated candidate commit: n/a, candidates were rejected and not committed

Target audit:

- `poly_basemul`: generic arithmetic-correct output, used by decap verify.
- `poly_basemul_rminus1`: raw rminus1 output consumed by
  `poly_invntt_from_rminus1`.
- `poly_basemul_scaled_r_input`: same raw-store body as rminus1, with the
  second operand pre-scaled by `R`; used by keygen public arithmetic.
- `poly_basemul_add`: separate add32/full-pipeline dataflow; Q31 byte-contract
  helper remains encap-only and was not reused.

Slothy commands:

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

Candidate windows attempted:

| window | source shape | instructions | status | model cycles | wall time |
| --- | --- | ---: | --- | ---: | ---: |
| `base_gt_rminus1_loop` | `base_gt.S` preprocessed one-loop raw-store window | 77 | OPTIMAL, selfcheck OK | 82 | 5.93s |
| `base_gt_generic_loop` | `base_gt.S` preprocessed one-loop corrected-output window | 101 | OPTIMAL, selfcheck OK | 121 | 6.66s |

Pi5 commands:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_basemul_variants_pmu SUDO= CORE=3
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

Correctness:

```text
bench_gt_basemul_variants_pmu: correctness,total_mismatches=0
bench_gt_kem_component_profile_pmu: correctness,total_mismatches=0,valid_cases=64
```

PMU:

| variant | cycles/call | instr/call | delta vs production | decision |
| --- | ---: | ---: | ---: | --- |
| `poly_basemul` | 2910.593 | 2489 | baseline | baseline |
| `poly_basemul_slothy_campaign` | 2963.068 | 2489 | +52.475 | reject |
| `poly_basemul_rminus1` | 2145.958 | 1913 | baseline | baseline |
| `poly_basemul_rminus1_slothy_campaign` | 2180.158 | 1913 | +34.200 | reject |
| `poly_basemul_scaled_r_input` | 2131.955 | 1913 | baseline | baseline |
| `poly_basemul_scaled_r_input_slothy_campaign` | 2170.086 | 1913 | +38.131 | reject |

Production KEM component baseline from the same Pi5 pass:

| component | cycles/call | instr/call |
| --- | ---: | ---: |
| `decap_basemul_rminus1` | 2028.093 | 1909 |
| `decap_verify_basemul` | 2823.359 | 2485 |
| `encap_basemul_add` | 2864.627 | 2800 |
| `keygen_public_arithmetic_x2` | 4083.382 | 3822 |

Projected API impact:

| candidate | local delta | projected impact |
| --- | ---: | --- |
| generic verify basemul | +52.475 cycles | +0.16% decap if mapped to verify basemul |
| rminus1 basemul | +34.200 cycles | +0.10% decap |
| scaled-r input | +38.131 cycles | about +0.19% keygen if used twice |

Decision:

No viable basemul candidate was found.  Both candidates passed correctness but
regressed on Pi5 PMU.  The generated candidate outputs and temporary benchmark
harness wiring are not committed as best artifacts.  Set
`generic_rminus1_basemul` to `needs_new_strategy`, not active immediate rerun.
Only revisit it with a wider production-scheduled multi-loop/window or a real
structural DAG change; do not continue this source-order one-loop Slothy route.
