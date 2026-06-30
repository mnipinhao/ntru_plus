# GT production KEM stage PMU breakdown

Date: 2026-06-27

Scope: production-only GT path.  This benchmark does not enable NTT32 rowspec,
basemul ldrtrn, fused crep3, InvNTT row-buffer/post fusion, branchfold ldp, or
lane-store variants.

## Production contract

The measured production path is the current `gt_production` KEM build:

```text
GT_PRODUCTION_USE_SCALED_KEYPAIR
GT_PRODUCTION_USE_RMINUS1_DECAP
GT_BASEINV_BATCH_USE_ASM_FINISH
```

Decap therefore stays on:

```text
poly_basemul_rminus1
poly_invntt_from_rminus1
poly_crepmod3
```

and does not use `poly_invntt_from_rminus1_crepmod3`.

## Benchmark added

New aarch64-bench files:

```text
bench_gt_kem_stage_pmu.c
scripts/write_gt_kem_stage_stats.py
```

New target:

```text
make bench_gt_kem_stage_pmu
```

Run used on Pi5:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  bench_gt_kem_stage_pmu \
  GT_KEM_STAGE_PMU_NTESTS=31 \
  GT_KEM_STAGE_PMU_NITERATIONS=500 \
  GT_KEM_STAGE_PMU_NWARMUP=50 \
  GT_KEM_STAGE_PMU_NINPUTS=64 \
  SUDO=
```

The harness first generates current-production KEM inputs with the renamed
`kem.c` wrapper and checks:

```text
correctness,total_mismatches=0,valid_cases=64
```

PMU events:

```text
cycles, instructions, branches, branch_misses,
L1I read miss, L1D load miss, L1D store miss if available, cache_miss
```

`l1d_store_miss` was not available on this Pi5 kernel.

The `text_size/static_insns` columns are wrapper-symbol sizes, not full
transitive kernel sizes.  The dynamic PMU counters include the called production
kernels.

## Totals

Pi5, `taskset -c 3`, 31 samples, 500 iterations/sample.

| path | cycles/call | instr/call | IPC | branches/call | L1I miss/call | L1D load miss/call |
|---|---:|---:|---:|---:|---:|---:|
| keypair_total | 39217.248 | 81899.006 | 2.0883 | 962.0 | 0.2620 | 10.9320 |
| encap_total | 38141.774 | 106450.006 | 2.7909 | 829.0 | 0.2560 | 11.5120 |
| decap_total | 33293.330 | 75190.006 | 2.2584 | 589.0 | 2.7340 | 46.9380 |

## Stage Table

| stage | cycles/call | instr/call | IPC | branches/call | branch misses/call | L1I miss/call | L1D load miss/call |
|---|---:|---:|---:|---:|---:|---:|---:|
| keypair_sample_ntt | 5924.778 | 13545.006 | 2.2862 | 105.0 | 0.0020 | 0.0340 | 14.1640 |
| keypair_baseinv_scaled_x2 | 10016.090 | 8813.006 | 0.8799 | 301.0 | 2.0060 | 0.0100 | 9.7540 |
| keypair_basemul_scaled_x2 | 4084.420 | 3823.006 | 0.9360 | 51.0 | 0.0020 | 0.0040 | 6.5200 |
| keypair_pack_hashf | 13194.916 | 41671.006 | 3.1581 | 258.0 | 0.0320 | 0.0360 | 35.2620 |
| encap_hash_cbd_ntt_r | 17718.024 | 52714.006 | 2.9752 | 314.0 | 0.0400 | 0.1060 | 42.5360 |
| encap_pack_hashg_sotp_ntt_m | 16628.194 | 48804.006 | 2.9350 | 261.0 | 0.0260 | 0.1080 | 37.1780 |
| encap_frombytes_pk | 329.448 | 564.006 | 1.7120 | 13.0 | 0.0020 | 0.0020 | 5.4180 |
| encap_basemul_add | 2866.952 | 2800.006 | 0.9766 | 25.0 | 0.0020 | 0.0000 | 4.4060 |
| encap_tobytes_ct | 411.282 | 779.006 | 1.8941 | 13.0 | 0.0020 | 0.0000 | 1.5600 |
| decap_frombytes | 1220.724 | 1689.006 | 1.3836 | 41.0 | 0.0020 | 0.0000 | 16.7780 |
| decap_basemul_rminus1 | 2029.458 | 1909.006 | 0.9406 | 25.0 | 0.0020 | 0.0020 | 2.7460 |
| decap_invntt_rminus1 | 4023.072 | 5074.006 | 1.2612 | 12.0 | 0.0020 | 0.0160 | 37.3260 |
| decap_crepmod3 | 382.758 | 393.006 | 1.0268 | 25.0 | 0.0020 | 0.0020 | 1.4520 |
| decap_ntt_sub | 2930.332 | 4214.006 | 1.4381 | 17.0 | 0.0020 | 0.0180 | 64.4420 |
| decap_verify_basemul | 2826.746 | 2485.006 | 0.8791 | 25.0 | 0.0020 | 0.0040 | 2.8240 |
| decap_pack_hashg_sotp | 13892.208 | 44829.006 | 3.2269 | 253.0 | 0.0280 | 0.0340 | 23.8900 |
| decap_hashh_cbd_ntt_pack_verify | 6350.462 | 14699.006 | 2.3146 | 183.0 | 0.0020 | 0.0300 | 46.2880 |

## Top Cycle Consumers

Top stage-level consumers among the measured breakdown:

| rank | stage | cycles/call | main content |
|---:|---|---:|---|
| 1 | encap_hash_cbd_ntt_r | 17718.024 | `hash_f`, `hash_h`, `poly_cbd1`, `poly_ntt(r)` |
| 2 | encap_pack_hashg_sotp_ntt_m | 16628.194 | `poly_tobytes(r)`, `hash_g`, `poly_sotp_encode`, `poly_ntt(m)` |
| 3 | decap_pack_hashg_sotp | 13892.208 | `poly_tobytes(r2)`, `hash_g`, `poly_sotp_decode` |
| 4 | keypair_pack_hashf | 13194.916 | three `poly_tobytes` plus `hash_f(pk)` |
| 5 | keypair_baseinv_scaled_x2 | 10016.090 | two scaled base inversions |

The main result is that current KEM cost is not dominated by one remaining NTT
or basemul kernel.  The largest blocks are mixed hash/packing/sampling/SOTP
stages.

## Decap Detail

Decap total:

```text
decap_total = 33293.330 cycles/call
```

Largest decap pieces:

```text
decap_pack_hashg_sotp              13892.208 cycles  (~41.7% of decap)
decap_hashh_cbd_ntt_pack_verify     6350.462 cycles  (~19.1%)
decap_invntt_rminus1                4023.072 cycles  (~12.1%)
decap_ntt_sub                       2930.332 cycles  (~8.8%)
decap_verify_basemul                2826.746 cycles  (~8.5%)
decap_basemul_rminus1               2029.458 cycles  (~6.1%)
decap_frombytes                     1220.724 cycles  (~3.7%)
decap_crepmod3                       382.758 cycles  (~1.1%)
```

This explains why fused crep3 is not attractive for production default:
`poly_crepmod3` is only about 383 cycles in the full decap context, and the
fused version already lost in the full-path PMU test.

## Encap Detail

Encap total:

```text
encap_total = 38141.774 cycles/call
```

Largest encap pieces:

```text
encap_hash_cbd_ntt_r               17718.024 cycles  (~46.5% of encap)
encap_pack_hashg_sotp_ntt_m        16628.194 cycles  (~43.6%)
encap_basemul_add                   2866.952 cycles  (~7.5%)
encap_tobytes_ct                     411.282 cycles  (~1.1%)
encap_frombytes_pk                   329.448 cycles  (~0.9%)
```

`poly_basemul_add` is real but not the dominant encap consumer.  A 10% win on
`encap_basemul_add` would save about 287 cycles, or less than 1% of encap.

## Keypair Detail

Keypair total:

```text
keypair_total = 39217.248 cycles/call
```

Measured keypair pieces:

```text
keypair_pack_hashf                 13194.916 cycles
keypair_baseinv_scaled_x2          10016.090 cycles
keypair_sample_ntt                  5924.778 cycles
keypair_basemul_scaled_x2           4084.420 cycles
```

This continues to show base inversion as the largest polynomial-only keypair
piece, but the mixed pack/hash stage is larger than base inversion.

## Already Tried / Rejected

These lines should remain out of production default based on prior PMU/full-path
results:

```text
NTT32 shadow-base rowspec
NTT32 rowspec Slothy
basemul ldrtrn_noadd expansion
oldstore final-store contract
InvNTT row-buffer/post fusion for now
poly_invntt_from_rminus1_crepmod3 production default
```

Accepted / keep:

```text
rminus1/scaled_r_input final st4 register contract
basemul old-contract regression guard
PMU benchmark infrastructure
```

## Next Target

The top-down result says the next production decision should not start from a
single attractive asm peephole.  First split the two large encap stages and the
large decap SOTP/hash stage into narrower PMU targets:

```text
encap_hash_cbd_ntt_r:
  hash_f + hash_h
  poly_cbd1
  poly_ntt(r)

encap_pack_hashg_sotp_ntt_m:
  poly_tobytes(r)
  hash_g
  poly_sotp_encode
  poly_ntt(m)

decap_pack_hashg_sotp:
  poly_tobytes(r2)
  hash_g
  poly_sotp_decode
```

If hash optimization is allowed, the highest-cycle blocks are hash-heavy and
should be studied with CE/NO_CE policy in mind.

If the work must stay inside polynomial asm, the most reasonable next candidate
is still `poly_basemul_add` / add32 in the encap full path, but the expected
ceiling is modest because the measured stage is only about 2867 cycles.  Before
writing another asm variant, split `poly_basemul_add` into load, multiply,
add/reduce, and store-pressure categories with PMU/static inspection.
