# GT baseinv flat k-way batch inversion PMU

Date: 2026-07-02

Scope: benchmark-only prototype.  Production `poly_baseinv` and
`poly_baseinv_scaled_r` remain unchanged.

## Source and symbol audit

Production GT base inversion for NTRU+768 is linked from:

| item | production symbol / file | status |
| --- | --- | --- |
| baseinv ABI | `poly_baseinv`, `poly_baseinv_scaled_r` in `poly_gt_baseinv_batch.c` | production default |
| batch denominator inverse | `poly_fqinv_batch_neon` in `poly_gt_baseinv_batch.c` | production internal |
| scalar-vector inverse chain | `gt_fqinv15_asm` in `asm/gt/gt_fqinv15.S` | production linked when `GT_BASEINV_USE_FQINV15_ASM` is set |
| batch finish | `baseinv_batch_finish24_n1_asm` in `asm/slothy/production/baseinv_batch_finish_loop_n1.S` | production linked when `GT_BASEINV_BATCH_USE_ASM_FINISH` is set |

Current `gt_production` already uses `gt_fqinv15_asm`, so the old assumption
that production `fqinv_neon` is a 16-step C chain is stale for this branch.
The new `fqinv_new_neon` helper is therefore a benchmark oracle for the
15-`fqmul_neon` C/NEON chain, not a production replacement.

## Prototype

New benchmark-only helpers, compiled only with
`GT_BASEINV_KWAY_BENCH_HELPERS`:

| helper | purpose |
| --- | --- |
| `gt_baseinv_fqinv_batch_old_24_for_bench` | current m=24 batch using linked production `fqinv_neon` / `gt_fqinv15_asm` |
| `gt_baseinv_fqinv_batch_new_24_for_bench` | m=24 k=1 using C/NEON `fqinv_new_neon` |
| `gt_baseinv_fqinv_kway_new_24_for_bench` | m=24 flat k-way using `fqinv_new_neon` |
| `gt_baseinv_fqinv_batch_new_36_for_bench` | m=36 k=1 isolated model |
| `gt_baseinv_fqinv_kway_new_36_for_bench` | m=36 flat k-way isolated model |
| `poly_baseinv_gt_batch_scaled_r_kway_new_for_bench` | benchmark-only scaled baseinv x2 candidate |

Flat k-way cost model:

```text
ordinary m-vector batch: 3*(m-1) fqmul + 1 fqinv
flat k-way batch:        3*(m-k) fqmul + k fqinv
```

Because production already uses a 15-multiply inverse ASM, the expected best
case is not obvious: increasing `k` saves `3*(k-1)` ordinary vector multiplies
but adds `k-1` full inversions.  The benchmark exists to measure that tradeoff
on Pi5 rather than assume it.

## Correctness plan

Target:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_baseinv_kway_pmu SUDO= CORE=3
```

Checks:

1. m=24: compare every `k in {1,2,3,4,6,8,12,24}` against current
   production m=24 batch output.
2. m=36: compare every `k in {1,2,3,4,6,9,12,18,36}` against m=36 k=1
   `fqinv_new_neon` output.
3. Product oracle: compare `fqmul(original, new_inverse)` against
   `fqmul(original, production_inverse)` for m=24.
4. Scaled baseinv x2: compare benchmark-only k-way output against
   production `poly_baseinv_scaled_r`.
5. Zero denominator failure behavior: check that a zero lane returns failure.

Required:

```text
correctness,total_mismatches=0
```

## PMU commands

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_baseinv_kway_pmu SUDO= CORE=3
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

Settings:

```text
NTESTS=31
NITERATIONS=5000
NWARMUP=100
NINPUTS=256 for k-way isolated PMU
NINPUTS=64 for KEM component profile
```

## Pi5 PMU result

Command:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_baseinv_kway_pmu SUDO= CORE=3
```

Correctness:

```text
correctness,total_mismatches=0,fqinv_mismatches=0,product_oracle_mismatches=0,baseinv_scaled_mismatches=0,exact_rep_mismatches=2360,valid_cases=256
```

Interpretation of `exact_rep_mismatches`: the C/NEON `fqinv_new_neon` path is
mod-q/product-equivalent to the linked production path in this harness, but it
does not preserve exact representative bytes versus `gt_fqinv15_asm`.  This is
acceptable for this benchmark-only arithmetic experiment, but it is not a
release-candidate representative contract.

Settings:

```text
NTESTS=31
NITERATIONS=5000
NWARMUP=100
NINPUTS=256
CORE=3
```

### Isolated m=24 denominator inversion

| variant | cycles/call p50 | IQR | instr/call p50 | delta vs current |
| --- | ---: | ---: | ---: | ---: |
| m24 old batch, linked `gt_fqinv15_asm` | 1410.176 | 0.341 | 1166.004 | baseline |
| m24 new k=1 | 1456.466 | 0.279 | 1210.004 | +46.290 |
| m24 new k=2 | 1629.462 | 1.106 | 1318.004 | +219.286 |
| m24 new k=3 | 1864.652 | 0.253 | 1426.004 | +454.476 |
| m24 new k=4 | 2076.652 | 0.340 | 1534.004 | +666.476 |
| m24 new k=6 | 2524.081 | 0.155 | 1750.004 | +1113.905 |
| m24 new k=8 | 3007.490 | 0.465 | 1966.004 | +1597.314 |
| m24 new k=12 | 4031.303 | 2.153 | 2398.004 | +2621.127 |
| m24 new k=24 | 7064.979 | 1.345 | 3598.004 | +5654.803 |

Best m=24 k-way setting: k=1, but it is still slower than the linked current
batch path by 46.290 cycles/call.

### Isolated m=36 denominator inversion

This is an isolated model only; NTRU+768 production uses m=24.

| variant | cycles/call p50 | IQR | instr/call p50 |
| --- | ---: | ---: | ---: |
| m36 new k=1 | 2030.481 | 1.896 | 1692.004 |
| m36 new k=2 | 2204.406 | 0.504 | 1800.004 |
| m36 new k=3 | 2439.030 | 4.495 | 1908.004 |
| m36 new k=4 | 2664.792 | 0.361 | 2016.004 |
| m36 new k=6 | 3113.286 | 0.232 | 2232.004 |
| m36 new k=9 | 3825.730 | 0.229 | 2556.004 |
| m36 new k=12 | 4494.934 | 0.743 | 2880.004 |
| m36 new k=18 | 6013.300 | 28.230 | 3528.004 |
| m36 new k=36 | 10585.304 | 0.251 | 5328.004 |

m=36 shows the same shape: k=1 is best, and extra groups are progressively
more expensive.

### Scaled baseinv x2 benchmark-only candidate

This measures the keygen-relevant shape `poly_baseinv_scaled_r` twice, but
with a benchmark-only k-way replacement for the denominator inversion step.

| variant | cycles/call p50 | IQR | instr/call p50 | delta vs current |
| --- | ---: | ---: | ---: | ---: |
| baseinv_scaled_x2 current | 10126.591 | 1.728 | 8902.004 | baseline |
| baseinv_scaled_x2 new k=1 | 10259.515 | 1.949 | 8994.004 | +132.924 |
| baseinv_scaled_x2 new k=2 | 10595.925 | 1.470 | 9210.004 | +469.334 |
| baseinv_scaled_x2 new k=3 | 11055.506 | 3.142 | 9426.004 | +928.915 |
| baseinv_scaled_x2 new k=4 | 11495.209 | 1.429 | 9642.004 | +1368.618 |
| baseinv_scaled_x2 new k=6 | 12424.710 | 1.449 | 10074.004 | +2298.119 |
| baseinv_scaled_x2 new k=8 | 13359.312 | 1.736 | 10506.004 | +3232.721 |
| baseinv_scaled_x2 new k=12 | 15331.155 | 2.032 | 11370.004 | +5204.564 |
| baseinv_scaled_x2 new k=24 | 21482.671 | 1.611 | 13770.004 | +11356.080 |

Best scaled-baseinv k-way setting: k=1, but it regresses by 132.924 cycles for
the x2 keygen shape.

## Keygen component profile

Command:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

Correctness:

```text
correctness,total_mismatches=0,valid_cases=64
```

Relevant rows:

| component | cycles/call p50 | instr/call p50 | share |
| --- | ---: | ---: | ---: |
| keypair_total | 39197.236 | 81927.000 | 100.0% |
| keygen_baseinv_scaled_f | 4996.257 | 4415.000 | 12.7% |
| keygen_baseinv_scaled_g | 4996.143 | 4414.000 | 12.7% |
| keygen_polyinv_scaled_x2 | 10023.626 | 8832.000 | 25.6% |
| keygen_public_arithmetic_x2 | 4078.901 | 3822.000 | 10.4% |

Note: this existing component-profile target still directly compiles the
component harness and should be treated as the current component-profile
baseline.  The isolated k-way harness explicitly compares against the linked
`gt_fqinv15_asm` path.

Benchmark-helper symbol guard:

```sh
nm bench_gt_kem_component_profile_pmu_bin | grep -E 'gt_baseinv_fqinv|kway_new_for_bench|GT_BASEINV_KWAY'
```

Output: no matches.  The k-way helper symbols are not present when
`GT_BASEINV_KWAY_BENCH_HELPERS` is not enabled.

## Decision

Flat k-way batch inversion should not be pursued for NTRU+768 baseinv:

1. Production already has a 15-multiply `gt_fqinv15_asm` inverse core.
2. The requested C/NEON `fqinv_new_neon` k=1 path is slower than the linked
   current m=24 batch by 46.290 cycles.
3. Increasing `k` saves ordinary multiplications but adds full inversions; on
   Pi5 this is a strict regression for all tested k.
4. The keygen-relevant scaled x2 shape also regresses, with best k=1 slower by
   132.924 cycles.
5. The prototype is mod-q/product-correct but not exact-representative
   equivalent to the linked ASM path, so it is not a production-ready contract.

Next baseinv work should remain at the algorithm level, not flat k-way batch
inversion.  A future route would need a different polyinv/baseinv algorithm or
a real reduction/representative contract improvement; this k-way split does
not move the keygen bottleneck in the right direction.
