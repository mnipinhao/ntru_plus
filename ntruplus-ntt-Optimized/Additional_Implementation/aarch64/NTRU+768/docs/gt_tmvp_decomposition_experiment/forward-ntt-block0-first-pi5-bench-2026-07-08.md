# Forward NTT Block0-First + Pi5 Bench Note

Date: 2026-07-08

## Local block0-first scaffold

Artifact:

```text
experiments/forward_ntt_phase123_u01/phase123_stage12_block0_first_allrows.sym.s
```

Local gates:

```text
check-kernel-contract: pass
clang -target aarch64-linux-gnu: pass
phase123_stage12_block0_first_ok seeds=64 rows=3 outputs=96 block0_outputs=24 later_outputs=72
```

Status:

```text
investigate
not Slothy-ready yet
```

Reason:

```text
The scaffold is still source-order and uses physical v1..v31/q* registers.
The physical-register leak gate fails by design until this is rewritten into
true symbolic registers or cut down to a smaller Stage12-out0 -> Stage345-block0
region.
```

## Pi5 KEM PERF matrix

Host:

```text
pi@100.99.191.9
/home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench
```

Command shape:

```text
make -B bench VARIANT=<variant> BENCH_MODE=<mode> CYCLES=PERF \
  USE_SHAKE_ASM=0 NTESTS=31 NITERATIONS=300 NWARMUP=50 SUDO= CORE=3
./bench
```

Results:

| variant | keygen | encap | decap |
|---|---:|---:|---:|
| `kpqc_final` | 39960 | 39088 | 35162 |
| `gt_production_default` | 37957 | 37746 | 33095 |
| `gt_production_no_q31` | 37940 | 37683 | 33092 |

Percent vs `kpqc_final`:

| variant | keygen | encap | decap |
|---|---:|---:|---:|
| `gt_production_default` | -5.0% | -3.4% | -5.9% |
| `gt_production_no_q31` | -5.1% | -3.6% | -5.9% |

Notes:

```text
- This run used NO_CE fips202 for both KPQC final and GT production.
- gt_production_default has Q31 encap enabled.
- In this run no_q31 was slightly faster than default in encap by 63 cycles;
  treat that as a retest item, not a conclusion by itself.
- Candidate A was not measured because this Pi5 aarch64-bench Makefile exposes
  kpqc_final and gt_production_* variants, but no candidate_a variant.
```

## GT production component profile

Command shape:

```text
make -B bench_gt_kem_component_profile_pmu VARIANT=gt_production_default \
  SUDO= CORE=3
```

Correctness:

```text
correctness,total_mismatches=0,valid_cases=64
```

Representative final run, cycles per call:

| component | cycles |
|---|---:|
| `keypair_total` | 38263.314 |
| `encap_total` | 37673.238 |
| `decap_total` | 33299.104 |
| `keygen_sample_prebaseinv_x2` | 11516.285 |
| `keygen_polyinv_scaled_x2` | 9414.619 |
| `keygen_public_arithmetic_x2` | 4074.698 |
| `keygen_hash_f_pk` | 11901.388 |
| `encap_hash_cbd_ntt_r` | 17681.923 |
| `encap_ntt_r` | 2705.598 |
| `encap_ntt_m` | 2704.433 |
| `encap_basemul_add` | 2864.511 |
| `decap_basemul_rminus1` | 2028.026 |
| `decap_invntt_rminus1` | 4023.567 |
| `decap_basemul_invntt_rminus1_pair` | 6124.693 |
| `decap_ntt_m1` | 2709.348 |
| `decap_ntt_sub` | 2902.325 |
| `decap_verify_basemul` | 2823.646 |

Forward-NTT relevance:

```text
The measured standalone NTT-sized pieces are around 2704-2709 cycles each.
The block0-first experiment is only relevant if it can reduce the hidden
Stage12 store -> Stage345 load boundary inside that forward NTT cost.
```
