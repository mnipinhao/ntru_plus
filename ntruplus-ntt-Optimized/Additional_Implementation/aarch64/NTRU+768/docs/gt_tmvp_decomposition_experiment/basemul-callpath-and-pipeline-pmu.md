# Basemul call-path audit and pipeline PMU

Date: 2026-06-27

Scope:

- Audit all production-relevant `poly_basemul*` call paths.
- Compare current `rminus1` / `scaled_r_input` final `st4` register contract
  against benchmark-only oldstore wrappers in the immediate KEM consumer
  pipelines.
- Do not change production defaults.

## Call-path audit

Current `aarch64-bench VARIANT=gt_production` enables:

```text
GT_PRODUCTION_USE_SCALED_KEYPAIR
GT_PRODUCTION_USE_RMINUS1_DECAP
GT_BASEINV_BATCH_USE_ASM_FINISH
```

Source: `aarch64-bench/Makefile`.

### Keypair

`kem.c` maps keypair baseinv/basemul through macros:

```c
#ifdef GT_PRODUCTION_USE_SCALED_KEYPAIR
#define KEYPAIR_BASEINV poly_baseinv_scaled_r
#define KEYPAIR_BASEMUL poly_basemul_scaled_r_input
#else
#define KEYPAIR_BASEINV poly_baseinv
#define KEYPAIR_BASEMUL poly_basemul
#endif
```

The keypair path then has two products:

```c
KEYPAIR_BASEMUL(&h, g, finv);
KEYPAIR_BASEMUL(&hinv, f, ginv);
poly_tobytes(pk, &h);
poly_tobytes(sk + NTRUPLUS_POLYBYTES, &hinv);
```

With `GT_PRODUCTION_USE_SCALED_KEYPAIR`, both products correctly use
`poly_basemul_scaled_r_input()`.  No missing normal `poly_basemul()` remains in
the active keypair path.

### Encapsulation

Encapsulation uses:

```c
poly_basemul_add(&c, &h, &r, &m);
poly_tobytes(ct, &c);
```

This is expected.  It is a product-plus-message accumulation and its output is
serialized as ciphertext.  It is not an `rminus1 -> InvNTT` consumer and it is
not a scaled-keypair product.

### Decapsulation first product

Current production decap uses:

```c
poly_basemul_rminus1(&m1, &c, &f);
poly_invntt_from_rminus1(&m1, &m1);
poly_crepmod3(&m1, &m1);
```

This is the intended paired ABI: `poly_basemul_rminus1()` leaves one extra
Montgomery `R^-1`, and `poly_invntt_from_rminus1()` consumes it.

The inactive fallback branches still contain normal `poly_basemul(&m1, &c, &f)`
followed by normal `poly_invntt()`.  Those are not active under
`gt_production`.

### Decapsulation r2 product

After `m1` recovery, decapsulation computes:

```c
poly_ntt(&m2, &m1);
poly_sub(&c, &c, &m2);
poly_basemul(&r2, &c, &hinv);
poly_tobytes(buf1, &r2);
```

This normal `poly_basemul()` is expected.  The consumer is `poly_tobytes()` /
hash verification, not `poly_invntt_from_rminus1()`, and `hinv` is not the
scaled-r keypair input contract.

### Bench and profiler mirrors

`aarch64-bench/bench.c` mirrors the same production flags:

- keypair component: `poly_basemul_scaled_r_input()`
- decap first product component: `poly_basemul_rminus1()`
- decap r2 component: normal `poly_basemul()`
- encap component: `poly_basemul_add()`

`gt_bench/kem_component_profiler.c` mirrors the same structure for component
profiling.  Candidate-A / candidate-B / unit-test call sites are separate
experimental harnesses and are not active `gt_production` call paths.

Audit conclusion: no production-relevant call path is missing
`rminus1` / `scaled_r_input`.  The remaining normal `poly_basemul()` in decap
`r2` is intentional.

## Pipeline PMU harness

New benchmark target:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  bench_gt_basemul_pipeline_pmu \
  GT_BASEMUL_PIPELINE_PMU_NTESTS=31 \
  GT_BASEMUL_PIPELINE_PMU_NITERATIONS=10000 \
  GT_BASEMUL_PIPELINE_PMU_NWARMUP=100 \
  SUDO=
```

Harness file:

```text
aarch64-bench/bench_gt_basemul_pipeline_pmu.c
```

It compares current production wrappers with benchmark-only oldstore wrappers:

- `poly_basemul_scaled_r_input`
- `poly_basemul_scaled_r_input_oldstore`
- `poly_basemul_rminus1`
- `poly_basemul_rminus1_oldstore`

Correctness:

```text
correctness,total_mismatches=0
```

Pi5 PMU note: `l1d_store_miss` is unavailable on the current kernel, so that
counter reports `na`.

## Pi5 PMU result

Host: `pi@100.99.191.9`

Samples: `NTESTS=31`, `NITERATIONS=10000`, pinned with `taskset -c 3`.

| Pipeline | Variant | cycles/call | instr/call | IPC |
|---|---:|---:|---:|---:|
| keypair scaled pair + tobytes | current | 5763.486 | 5380.000 | 0.9335 |
| keypair scaled pair + tobytes | oldstore | 5841.136 | 5524.000 | 0.9457 |
| decap rminus1 + InvNTT | current | 6370.552 | 7025.000 | 1.1027 |
| decap rminus1 + InvNTT | oldstore | 6387.432 | 7097.000 | 1.1111 |
| decap rminus1 + InvNTT + crep3 | current | 6774.874 | 7417.000 | 1.0948 |
| decap rminus1 + InvNTT + crep3 | oldstore | 6822.310 | 7489.000 | 1.0977 |

Delta, oldstore vs current:

| Pipeline | cycles delta | instr delta | Interpretation |
|---|---:|---:|---|
| keypair scaled pair + tobytes | +77.650 cycles (+1.35%) | +144 instr | current final-st4 contract wins clearly |
| decap rminus1 + InvNTT | +16.880 cycles (+0.26%) | +72 instr | current contract still wins after InvNTT consumer |
| decap rminus1 + InvNTT + crep3 | +47.436 cycles (+0.70%) | +72 instr | current contract still wins after crep3 is included |

The oldstore variants sometimes show slightly higher IPC, but that is because
they retire more instructions.  Wall cycles are worse in every measured
consumer pipeline.

## Decision

Keep the current `rminus1` / `scaled_r_input` final `st4` register contract.
Keep oldstore wrappers benchmark-only.  Do not extend the rejected
`ldrtrn_noadd` direction to `rminus1`, `scaled_r_input`, or `add32`.

## Experiment status

```text
oldstore:
  benchmark-only regression baseline; not a production path.

ldrtrn_noadd:
  correctness pass, Pi5 PMU slower, do not extend to rminus1/scaled/add32.

ntt32 rowspec:
  correctness pass, instruction count reduced, Pi5 PMU no cycle win,
  do not productionize.
```

Regression guard:

```text
aarch64-bench/scripts/write_gt_basemul_variant_stats.py
```

The stats script now checks the live PMU binary and fails if the current
`poly_basemul_rminus1` or `poly_basemul_scaled_r_input` symbol contains the old
final-store register-contract moves:

```text
mov v8.16b,  v5.16b
mov v9.16b,  v6.16b
mov v10.16b, v18.16b
```

The oldstore symbols are allowed to keep those moves because they are the
benchmark-only negative/regression baseline.
