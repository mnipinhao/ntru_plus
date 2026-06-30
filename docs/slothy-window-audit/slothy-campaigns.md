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
