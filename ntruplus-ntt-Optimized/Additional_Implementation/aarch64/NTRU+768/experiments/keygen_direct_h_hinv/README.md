# Keygen direct h/hinv experiment

Date: 2026-07-07

Status: benchmark-only C/NEON model.  Production defaults are unchanged.

## Oracle

All checks in this experiment use the current production default as the frozen
oracle:

```text
VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
```

The model is not compared against the older flat baseinv path when deciding
promotion.  That path is only a historical fallback.

## Current production keygen dataflow

```text
finv = poly_baseinv_scaled_r_hier_k8(f)
ginv = poly_baseinv_scaled_r_hier_k8(g)

h    = poly_basemul_scaled_r_input(g, finv)
hinv = poly_basemul_scaled_r_input(f, ginv)

pk/sk include poly_tobytes(h), poly_tobytes(hinv)
```

Current PMU context:

```text
keygen_polyinv_scaled_x2     ~= 9408 cycles
keygen_public_arithmetic_x2  ~= 4075 cycles
combined ceiling             ~= 13483 cycles
```

## C model

The first model keeps the external output as `h/hinv` polynomials:

```c
int poly_keygen_compute_h_hinv_direct_model(poly *h, poly *hinv,
                                            const poly *f, const poly *g);
```

It still uses full internal `finv/ginv` scratch buffers, but it changes the
hier_k8 denominator recovery so `f` and `g` share one group-product batch
inversion:

```text
current hier_k8 x2:
  f: 8 groups of 3 denominator vectors -> invert 8 group products
  g: 8 groups of 3 denominator vectors -> invert 8 group products

direct model:
  f/g: 16 group products -> one batch inversion
```

Denominator-tree cost delta:

```text
+3 ordinary vector fqmul
-1 fqinv15 vector inverse
```

This is a C/NEON model, not ASM scheduling work.

## Pi5 command

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_direct_h_hinv_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

## Correctness

```text
oracle,oracle_current_hier_k8=1
correctness,valid_cases=4096
finv_exact_mismatches=0
ginv_exact_mismatches=0
finv_modq_mismatches=0
ginv_modq_mismatches=0
h_exact_mismatches=0
hinv_exact_mismatches=0
h_modq_mismatches=0
hinv_modq_mismatches=0
h_bytes_mismatches=0
hinv_bytes_mismatches=0
correctness,total_mismatches=0
```

This model is exact-representative equivalent to the current hier_k8 oracle for
the tested corpus.  It is not merely a byte-contract result.

## PMU

Run 1 with build identity printing `GT_BASEINV_USE_HIER_K8=1`:

| variant | cycles/call | instr/call | IQR |
| --- | ---: | ---: | ---: |
| current_hier_k8_baseinv_x2 | 9429 | 8659 | 1 |
| direct_model_baseinv_x2 | 9189 | 8712 | 1 |
| current_hier_k8_public_arithmetic_x2 | 4079 | 3858 | 2 |
| current_hier_k8_baseinv_plus_public_arithmetic | 13463 | 12476 | 1 |
| direct_h_hinv_model | 13237 | 12541 | 4 |

Run 2:

| variant | cycles/call | instr/call | IQR |
| --- | ---: | ---: | ---: |
| current_hier_k8_baseinv_x2 | 9423 | 8659 | 1 |
| direct_model_baseinv_x2 | 9191 | 8712 | 1 |
| current_hier_k8_public_arithmetic_x2 | 4080 | 3858 | 1 |
| current_hier_k8_baseinv_plus_public_arithmetic | 13465 | 12476 | 2 |
| direct_h_hinv_model | 13229 | 12541 | 4 |

Observed deltas:

```text
baseinv_x2 model delta: -232 to -240 cycles
baseinv_plus_public_arithmetic delta: -226 to -236 cycles
instruction count delta: +65 for direct_h_hinv_model
```

## Decision

The model is correct and useful as evidence, but it does not clear the
300-cycle promotion bar:

```text
promotion bar: direct_h_hinv_model <= current combined - 300 cycles
observed:      direct_h_hinv_model ~= current combined - 226 cycles
```

Do not write ASM for this exact C model yet.

The result does support one follow-up:

```text
hier_k8 x2 group-product combine is real and exact; if Task 6 continues,
the next model must remove more dataflow than only one fqinv15 chain.
```

Likely next routes:

1. Combine this x2 denominator tree with a fused finish/public-arithmetic DAG.
2. Audit whether `baseinv_batch_finish24_n1_asm` output can feed
   `poly_basemul_scaled_r_input` without materializing full `finv/ginv`.
3. Only consider direct bytes after a two-loop `base_gt` direct-pack DAG exists.

If no larger dataflow is planned, stop Task 6 at this model.

## Task 6D fused model start

`keygen_direct_h_hinv_fused_model.c` records the larger dataflow model that
would be needed before writing ASM.  It is not compiled into production or any
benchmark target yet.

The required v2 shape is:

```text
f^{-1} = num_f * den_f^{-1}
g^{-1} = num_g * den_g^{-1}

h    = (g * num_f) * den_f^{-1}
hinv = (f * num_g) * den_g^{-1}
```

This is only worth implementing if it removes more than the v1 model:

```text
remove full finv/ginv materialization
remove at least one full finv/ginv read pass in public basemul
fold or avoid the current finish-scale pass where algebraically valid
```

Stop condition:

```text
If the C model still performs two full quartic products plus two full
denominator-scale passes, expected savings are too close to v1 and ASM should
not be written.
```

Promotion threshold remains:

```text
direct_h_hinv_fused_model_v2
  <= current_hier_k8_baseinv_plus_public_arithmetic - 300 cycles
```

## Task B finish-to-h/hinv floor result

Command:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_finish_to_h_hinv_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Correctness:

```text
direct_h_exact_mismatches=0
direct_hinv_exact_mismatches=0
finish_h_exact_mismatches=0
finish_hinv_exact_mismatches=0
finish_h_bytes_mismatches=0
finish_hinv_bytes_mismatches=0
finish_to_h_hinv_correctness,total_mismatches=0
```

PMU:

| row | cycles/call | instr/call | IQR |
| --- | ---: | ---: | ---: |
| current_baseinv_plus_public_arith | 13477 | 12476 | 10 |
| direct_h_hinv_model_v1 | 13232 | 12541 | 5 |
| finish_to_h_hinv_model | 13233 | 12542 | 4 |

Decision:

```text
Task B C-floor delta vs current: about -244 cycles
Task B delta vs v1: no additional win
promotion bar: current - 300 cycles ~= 13177 cycles
decision: do not write ASM for this wrapper/floor model
```

The result means the next useful Task B attempt cannot be another wrapper.  It
must actually fuse finish denominator scaling into the quartic product DAG and
avoid materializing/loading full `finv/ginv`.
