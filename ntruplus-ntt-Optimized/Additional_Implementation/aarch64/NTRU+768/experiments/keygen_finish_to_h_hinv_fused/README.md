# Keygen finish-to-h/hinv fused DAG audit

Date: 2026-07-07

Status: design audit only.  No benchmark-only ASM prototype was written in
this pass, because a representative prototype must modify the `base_gt` product
finalizer and any smaller wrapper would repeat the already measured floor
model.

Wave 3 refined this into an explicit finalizer body contract in
`true_finalizer_design.md`.  That file is the handoff for a future
benchmark-only `base_gt` variant; this README keeps the broader route history
and PMU floor context.

## Fixed oracle

All reasoning in this directory uses the current production default as oracle:

```text
VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
```

Production defaults are unchanged.  Generic `poly_baseinv_scaled_r`,
`poly_basemul_scaled_r_input`, Q31, and public poly APIs are not touched.

## Current DAG

The current keygen path computes:

```text
finv = poly_baseinv_scaled_r_hier_k8(f)
ginv = poly_baseinv_scaled_r_hier_k8(g)

h    = poly_basemul_scaled_r_input(g, finv)
hinv = poly_basemul_scaled_r_input(f, ginv)
```

For the scaled keypair base inverse, `baseinv_8_prepare()` computes a quartic
inverse numerator and one denominator vector per eight quartic blocks:

```text
num_f[j]  = numerator part for f_j, stored in GT block-major st4 layout
den_f[j]  = denominator scalar for f_j, as an int16x8_t lane vector
num_g[j]  = numerator part for g_j
den_g[j]  = denominator scalar for g_j
```

The hier_k8 tree inverts the denominator vectors.  The finish loop then
materializes the scaled inverse polynomial:

```text
finv_j = sign(num_f_j) * den_f_inv_scaled
ginv_j = sign(num_g_j) * den_g_inv_scaled
```

where `sign(num)` applies the production baseinv sign convention:

```text
[n0, n1, n2, n3] -> [n0, -n1, n2, -n3]
```

The finish loop is `baseinv_batch_finish24_n1_asm`.  Per eight-block group and
per polynomial it performs:

```text
ld4 numerator vectors
ldr denominator-inverse vector
4 vector Montgomery scalar multiplies
st4 scaled inverse vectors
```

The public arithmetic then calls `poly_basemul_scaled_r_input`, whose second
operand is already scaled by Montgomery `R`, so the `base_gt` body stores the
raw/rminus1 result directly:

```text
poly_basemul_scaled_r_input(h,    g, finv)
poly_basemul_scaled_r_input(hinv, f, ginv)
```

## Existing measured floor

The previous floor model is exact but still materializes `finv/ginv`:

```text
current_baseinv_plus_public_arith  13477 cycles, 12476 instr, IQR 10
direct_h_hinv_model_v1             13232 cycles, 12541 instr, IQR 5
finish_to_h_hinv_model             13233 cycles, 12542 instr, IQR 4
```

Correctness for that floor model:

```text
direct_h_exact_mismatches=0
direct_hinv_exact_mismatches=0
finish_h_exact_mismatches=0
finish_hinv_exact_mismatches=0
finish_h_bytes_mismatches=0
finish_hinv_bytes_mismatches=0
finish_to_h_hinv_correctness,total_mismatches=0
```

That model is useful as an oracle/floor, but it is not a fused finish-public
arithmetic DAG.

## Candidate fused DAG

For each quartic base ring:

```text
B_j = F_q[X] / (X^4 - lambda_j)
```

the algebraic target is:

```text
f^{-1}_j = sign(num_f_j) * den_f_j^{-1}
g^{-1}_j = sign(num_g_j) * den_g_j^{-1}

h_j      = g_j * f^{-1}_j
hinv_j   = f_j * g^{-1}_j
```

The fused candidate would compute:

```text
tmp_h_j    = g_j * sign(num_f_j)
h_j        = tmp_h_j * den_f_j^{-1}

tmp_hinv_j = f_j * sign(num_g_j)
hinv_j     = tmp_hinv_j * den_g_j^{-1}
```

For the current Montgomery-scaled implementation, the final denominator
multiply must use the same `den_inv_scaled` value produced by the scaled
baseinv path.  This preserves the current arithmetic-correct `h/hinv`
representative contract, not just a byte contract.

## Operation-count comparison

Counts are for both `h` and `hinv` over 24 eight-block groups per polynomial.

| item | current v1/floor | true fused DAG |
| --- | ---: | ---: |
| baseinv prepare blocks | 48 | 48 |
| combined hier_k8 denominator tree | same as v1 | same as v1 |
| fqinv15 calls | 1 in v1 | 1 |
| quartic products for public arithmetic | 48 group products | 48 group products |
| denominator scalar multiply groups | 48 groups x 4 vectors | 48 groups x 4 vectors |
| numerator scratch stores from prepare | 48 `st4` | 48 `st4` |
| finish numerator reloads | 48 `ld4` | removed |
| finish scaled-inverse stores | 48 `st4` | removed |
| public second-operand loads | 48 `ld4` of `finv/ginv` | 48 `ld4` of numerator scratch |
| denominator inverse loads | 48 vector loads | 48 vector loads, moved into fused product |
| extra sign work | finish uses `-den_inv` | either store signed numerator in prepare or negate lanes 1/3 before product |

The important point is that the fused DAG does not reduce the number of
quartic products.  Its plausible win comes from deleting the standalone finish
memory pass:

```text
removed per x2 keygen candidate:
  48 numerator ld4 groups
  48 scaled-inverse st4 groups
  finish-loop branch/control and ABI overhead

not removed:
  48 numerator/signed-numerator loads for the actual product
  48 denominator inverse loads
  192 vector denominator scalar multiplies
```

The standalone finish loop costs about 2045 cycles in the decomposition
harness, but much of that cost is the 192 vector scalar multiplications that
the fused product still needs.  The realistic additional ceiling over v1 is
therefore smaller than 2045 cycles and likely comes from the deleted memory
pass and any scheduling overlap of the output denominator scaling.

## Representative and range contract

The candidate must return arithmetic-correct polynomials:

```text
h    == poly_basemul_scaled_r_input(g, finv_current)
hinv == poly_basemul_scaled_r_input(f, ginv_current)
```

Exact representative match is required for production consideration.  If a
future prototype only satisfies:

```text
poly_tobytes(h_candidate)    == poly_tobytes(h_current)
poly_tobytes(hinv_candidate) == poly_tobytes(hinv_current)
```

then it must be marked byte-contract only and must not replace the arithmetic
keygen path.

The fused product must preserve these contracts:

```text
input layout:  GT block-major row-bitrev, ld4/st4 quartic blocks
num layout:    same GT block-major numerator scratch from baseinv prepare
den layout:    24 int16x8_t denominator-inverse vectors in row-bitrev order
output layout: GT block-major row-bitrev arithmetic polys h/hinv
```

No secret-dependent branches or secret-dependent table indices are introduced.
The group index and lambda/denominator vector order are public loop state.

## Why no prototype was written in this pass

A representative prototype must add a new `base_gt` body variant:

```text
load a operand
load signed numerator operand
load lambda
run normal quartic product DAG
before final st4, multiply all four output vectors by den_inv_scaled
st4 h/hinv output
```

This is materially different from the existing wrappers:

```text
poly_basemul_scaled_r_input(...)
baseinv_batch_finish24_n1_asm(...)
```

Using those helpers would either:

1. materialize `finv/ginv` and repeat the floor model, or
2. materialize a temporary `g*num` / `f*num` poly and then run a finish-like
   scale pass over the result.

Neither path measures the intended optimization.  The smallest meaningful next
implementation is therefore a new benchmark-only `base_gt` finalizer variant,
not a C wrapper.

## Prototype contract for a future pass

Suggested internal helper:

```c
void poly_keygen_finish_to_h_hinv_fused_candidate(
    poly *h,
    poly *hinv,
    const poly *f,
    const poly *g);
```

Suggested implementation shape:

```text
prepare f -> signed numerator scratch + fden
prepare g -> signed numerator scratch + gden
combined x2 hier_k8 denominator inversion
fused_basegt_den_scale(h,    g, signed_num_f, fden_inv)
fused_basegt_den_scale(hinv, f, signed_num_g, gden_inv)
```

The `fused_basegt_den_scale` body should be generated from the production
`base_gt` DAG, not from the rejected duplicated pair-loop candidate.

Suggested gate:

```text
GT_EXPERIMENT_KEYGEN_FINISH_TO_H_HINV_FUSED
```

## Exact Makefile snippet for a future harness

Do not edit `aarch64-bench/Makefile` blindly; this is the snippet to add once a
real candidate symbol exists:

```make
.PHONY: bench_gt_keygen_finish_to_h_hinv_fused_pmu

GT_KEYGEN_FINISH_TO_H_HINV_FUSED_PMU_TARGET := bench_gt_keygen_finish_to_h_hinv_fused_pmu
GT_KEYGEN_FINISH_TO_H_HINV_FUSED_PMU_SOURCES := \
	bench_gt_keygen_finish_to_h_hinv_fused_pmu.c \
	../Additional_Implementation/aarch64/NTRU+768/experiments/keygen_finish_to_h_hinv_fused/finish_to_h_hinv_fused_candidate.c \
	../Additional_Implementation/aarch64/NTRU+768/asm/gt/experiment/poly_keygen_finish_to_h_hinv_fused.S

$(GT_KEYGEN_FINISH_TO_H_HINV_FUSED_PMU_TARGET): $(GT_KEYGEN_FINISH_TO_H_HINV_FUSED_PMU_SOURCES)
	$(CC) $(CFLAGS) $(GT_PRODUCTION_FLAGS) \
		-DGT_EXPERIMENT_KEYGEN_FINISH_TO_H_HINV_FUSED \
		-DGT_KEYGEN_DIRECT_H_HINV_MODEL_HELPERS \
		-DGT_BASEINV_HIER_K8_DECOMPOSE_HELPERS \
		-o $@ $(GT_KEYGEN_FINISH_TO_H_HINV_FUSED_PMU_SOURCES) $(LDFLAGS)

bench_gt_keygen_finish_to_h_hinv_fused_pmu: $(GT_KEYGEN_FINISH_TO_H_HINV_FUSED_PMU_TARGET)
	$(RUN_PMU) ./$(GT_KEYGEN_FINISH_TO_H_HINV_FUSED_PMU_TARGET)
```

Expected PMU rows:

```text
current_baseinv_plus_public_arith
direct_h_hinv_model_v1
finish_to_h_hinv_floor_model
finish_to_h_hinv_fused_candidate
full_keygen_current
full_keygen_candidate
```

## Commands

This pass is analysis-only:

```sh
git diff --check
```

No Pi5 PMU was run because there is no representative candidate symbol yet.

Future candidate command:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_finish_to_h_hinv_fused_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

## Decision

```text
decision: document_only / design_ready
prototype status: not written
reason: true fused DAG is plausible, but a valid prototype requires a new
        base_gt output-denominator-scale body.  A wrapper prototype would not
        measure the intended removed memory pass.
next action: generate a benchmark-only base_gt finalizer variant that keeps the
             production ld4/st4 layout, loads den_inv once per group, scales
             final out0..out3 before st4, and compares exact h/hinv.
```
