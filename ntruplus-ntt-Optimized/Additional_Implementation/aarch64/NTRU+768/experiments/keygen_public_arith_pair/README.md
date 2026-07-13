# Keygen public arithmetic pair experiment

Date: 2026-07-07

Status: benchmark-only model.  Production defaults are unchanged.

## Target

Current keygen public arithmetic runs two independent scaled basemul calls:

```c
h    = poly_basemul_scaled_r_input(g, finv);
hinv = poly_basemul_scaled_r_input(f, ginv);
```

The PMU ceiling is about:

```text
keygen_public_arithmetic_x2 ~= 4075 cycles
```

## First model

`poly_keygen_public_arith_pair_model()` is a semantic pair wrapper:

```c
void poly_keygen_public_arith_pair_model(poly *h, poly *hinv,
                                         const poly *f, const poly *g,
                                         const poly *finv,
                                         const poly *ginv);
```

Contract:

```text
h    == poly_basemul_scaled_r_input(g, finv)
hinv == poly_basemul_scaled_r_input(f, ginv)
```

This first model does not share the inner `base_gt` loop.  It is a negative
control for function-level pairing.  A real candidate would need a paired ASM
or C/NEON base_gt loop that processes the two products in the same
`physical_j` loop and shares lambda/table/loop control.

## Benchmark

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_public_arith_pair_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Promotion bar:

```text
pair_model <= current_public_arithmetic_x2 - 200 cycles
```

Kill rule:

```text
If this model saves <150 cycles, do not write ASM unless a separate operation
count shows a true paired base_gt loop can remove table/load/schedule work.
```

## Pi5 result

Command:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_public_arith_pair_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Correctness:

```text
h_exact_mismatches=0
hinv_exact_mismatches=0
h_bytes_mismatches=0
hinv_bytes_mismatches=0
keygen_public_arith_pair_correctness,total_mismatches=0
```

PMU:

| row | cycles/call | instr/call | IQR |
| --- | ---: | ---: | ---: |
| current_public_arithmetic_x2 | 4079 | 3858 | 10 |
| public_arith_pair_model | 4078 | 3869 | 1 |

Decision:

```text
local delta: about -1 cycle
promotion bar: -200 cycles
decision: stop C-wrapper route
```

This confirms that function-level pairing is not enough.  Any future Task A
candidate must be a real paired `base_gt` loop that shares lambda/table/loop
work inside the 24 block loop.  Do not write ASM for the current wrapper model.

## SubAgent-BASEGT ASM candidate

Date: 2026-07-07

Status: benchmark-only ASM prototype, correctness-pass, PMU-regression.
Production defaults are unchanged.

### Candidate

Added:

```text
asm/gt/experiment/keygen/poly_keygen_public_arith_pair.S
```

Symbol:

```c
void poly_keygen_public_arith_pair_asm(poly *h, poly *hinv,
                                       const poly *f, const poly *g,
                                       const poly *finv,
                                       const poly *ginv);
```

Contract:

```text
h    == poly_basemul_scaled_r_input(g, finv)
hinv == poly_basemul_scaled_r_input(f, ginv)
```

The candidate is a real pair-loop prototype, not a wrapper around two public
calls.  For each of the 24 GT block batches it:

```text
load lambda once from gt_rowbitrev_lambda
shadow lambda in v19
compute h    = g * finv  with the scaled-r final st4 contract
restore lambda from v19
compute hinv = f * ginv with the same final st4 contract
```

It keeps the current `ld4/st4` GT block-major layout and does not use the
previously rejected `ldp+uzp` load rewrite.

### Static notes

The production scaled basemul loop uses all vector registers except `v19` in
the `GT_BASEMUL_STORE_RMINUS1` path.  The prototype uses `v19` only as a
lambda shadow.  This avoids a second lambda table load per physical block, but
the product body itself remains the original single-product schedule duplicated
twice in one loop.  It is not a newly scheduled two-product DAG.

### Benchmark

Command:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_public_arith_pair_asm_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Correctness:

```text
h_exact_mismatches=0
hinv_exact_mismatches=0
h_bytes_mismatches=0
hinv_bytes_mismatches=0
h_asm_exact_mismatches=0
hinv_asm_exact_mismatches=0
h_asm_bytes_mismatches=0
hinv_asm_bytes_mismatches=0
keygen_public_arith_pair_correctness,total_mismatches=0
```

PMU:

| row | cycles/call | instr/call | IQR |
| --- | ---: | ---: | ---: |
| current_public_arithmetic_x2 | 4076 | 3858 | 0 |
| public_arith_pair_model | 4070 | 3869 | 1 |
| public_arith_pair_asm | 4179 | 3831 | 1 |

### Decision

```text
local delta vs current: +103 cycles
instruction delta vs current: -27 instr
decision: rejected for performance
```

The paired loop removed some instruction overhead but made the cycle schedule
worse.  This version should not be refined directly.  A future attempt would
need a fresh two-product symbolic DAG / register allocation instead of
duplicating the single-product Slothy schedule inside one loop.
