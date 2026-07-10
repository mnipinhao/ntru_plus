# GT production variant identity

Date: 2026-07-06

Purpose: keep local scheme builds and `aarch64-bench` builds from silently
measuring different GT production contracts.

## Source of truth

Production GT feature macros are defined in:

```text
Additional_Implementation/aarch64/NTRU+768/gt_production_variants.mk
```

Both build systems include this file:

```text
Additional_Implementation/aarch64/NTRU+768/Makefile
aarch64-bench/Makefile
```

## Variants

| Variant | Meaning |
| --- | --- |
| `gt_production_no_q31` | scaled keypair + rminus1 decap + fqinv15/baseinv finish asm, without Q31 encap byte-contract |
| `gt_production_q31` | same as no-q31, plus `GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP` and Q31 encap asm |
| `gt_production_default` | alias controlled by `GT_PRODUCTION_DEFAULT_VARIANT`; currently resolves to `gt_production_q31` |

Current default:

```text
GT_PRODUCTION_DEFAULT_VARIANT ?= gt_production_q31
```

## Local scheme Makefile targets

```sh
make test_kem_gt_production_default
make test_kem_gt_production_q31
make test_kem_gt_production_no_q31
```

Compatibility targets:

```text
test_kem_gt_production
test_kem_gt_production_opt
test_kem_gt_production_opt_rminus1
```

These now route to the default variant, so they no longer mean "no Q31".

## aarch64-bench variants

```sh
make VARIANT=gt_production_default BENCH_MODE=kem_enc CYCLES=PERF
make VARIANT=gt_production_q31 BENCH_MODE=kem_enc CYCLES=PERF
make VARIANT=gt_production_no_q31 BENCH_MODE=kem_enc CYCLES=PERF
```

`VARIANT=gt_production` is intentionally not a supported benchmark identity.
Use one of the three explicit names above.

## Runtime build identity

The generic KEM benchmark and the GT KEM PMU profilers print:

```text
build_config,GT_PRODUCTION_VARIANT=...
build_config,GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=...
build_config,GT_PRODUCTION_USE_RMINUS1_DECAP=...
build_config,GT_PRODUCTION_USE_SCALED_KEYPAIR=...
build_config,GT_BASEINV_USE_FQINV15_ASM=...
build_config,GT_BASEINV_BATCH_USE_ASM_FINISH=...
```

Use these lines as the benchmark identity when copying numbers into reports.

## Release Guards

`aarch64-bench` checks both Q31-enabled and no-Q31 identities:

```sh
make -C aarch64-bench check_gt_direct32_q31_release_candidate
```

The enabled guard expects:

```text
q31_guard_mode=enabled
direct32_q31_symbols=1
direct32_q31_call_sites=1
generic_poly_basemul_add_overwritten=0
decap_or_arithmetic_q31_callers=0
public_headers_with_q31_symbol=0
release_guard_pass=1
```

The no-Q31 guard expects:

```text
q31_guard_mode=disabled
direct32_q31_symbols=0
direct32_q31_call_sites=0
generic_poly_basemul_add_overwritten=0
decap_or_arithmetic_q31_callers=0
public_headers_with_q31_symbol=0
release_guard_pass=1
```

## Non-goal

This change does not optimize cycles.  It only prevents comparing a Q31 encap
binary against a no-Q31 binary while both are called "GT production".
