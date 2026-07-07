# True finish-to-h/hinv finalizer design

Date: 2026-07-07

Status: `design_ready`, no representative prototype emitted in this pass.

This document refines the finish-to-`h/hinv` route into the exact base_gt
finalizer contract required for a real benchmark-only prototype.  It is not a
wrapper plan.  Any prototype that calls the existing finish loop and then calls
`poly_basemul_scaled_r_input()` would repeat the measured floor model and is
not representative.

## Fixed oracle

All comparisons must use the current GT production default:

```text
VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
```

Generic `poly_baseinv_scaled_r`, `poly_basemul_scaled_r_input`, Q31, public
poly APIs, and production defaults must remain unchanged.

## Current dataflow

Current keygen computes:

```text
finv = poly_baseinv_scaled_r(f)
ginv = poly_baseinv_scaled_r(g)

h    = poly_basemul_scaled_r_input(g, finv)
hinv = poly_basemul_scaled_r_input(f, ginv)
```

`poly_baseinv_scaled_r()` uses:

```text
baseinv_8_prepare()
  input:  one GT block-major eight-quartic group from f or g
  output: numerator scratch, stored as st4 [n0,n1,n2,n3]
  output: one denominator vector den[i] with 8 scalar lanes

hier_k8 denominator tree
  input/output: den[24] int16x8_t
  output: the same scaled denominator-inverse convention consumed by the
          scaled baseinv finish loop

baseinv_batch_finish24_n1_asm()
  input:  numerator scratch poly
  input:  den[24]
  output: materialized scaled inverse poly
```

The finish loop is where the sign convention is applied:

```text
[n0,n1,n2,n3] and den_inv
  -> [fqmul(n0, den_inv),
      fqmul(n1, -den_inv),
      fqmul(n2, den_inv),
      fqmul(n3, -den_inv)]
```

So the conceptual inverse numerator for multiplication is:

```text
signed_num = [n0, -n1, n2, -n3]
```

The public arithmetic then reads the materialized scaled inverse as the second
operand to `poly_basemul_scaled_r_input`.

## Where numerator vectors are available

Numerator vectors are produced in `baseinv_8_prepare()` in
`poly_gt_baseinv_batch.c`:

```c
n.val[0] = reduce_mul2(...);
n.val[1] = reduce_mul2(...);
n.val[2] = reduce_mul2(...);
n.val[3] = reduce_mul2(...);
vst4q_s16(dst, n);
```

For the current production/hier_k8 path, these are available only as
materialized GT block-major numerator scratch after prepare:

```text
num_f.coeffs[64*i ... 64*i+63] = st4(n0,n1,n2,n3)
num_g.coeffs[64*i ... 64*i+63] = st4(n0,n1,n2,n3)
i = 0..23
```

A true fused prototype can reuse this scratch as its second base_gt operand,
but it must either:

```text
1. store signed numerator scratch from prepare, or
2. load normal numerator scratch with ld4 and negate coefficient vectors 1 and
   3 before the quartic product DAG.
```

The second option is lower-risk for this pass because it leaves
`baseinv_8_prepare()` unchanged and keeps the candidate local to the base_gt
body.

## Where den_inv_scaled is available

After the hier_k8 denominator tree, `den[24]` is still live in the caller that
would currently invoke `baseinv_batch_finish24_n1_asm()`.

Important: this document uses `den_inv_scaled` to mean exactly the values in
that `den[24]` buffer after the scaled hier_k8 inversion, not a newly
canonicalized mathematical inverse.

The true finalizer must load one vector per eight-quartic group:

```text
den_vec = den[i]  // 8 lanes, one scalar per physical quartic block
```

The same `den_vec` must be applied to all four output coefficient vectors for
that group.

## Required finalizer shape

The future experimental base_gt body must compute the normal quartic product
with the signed numerator as the second operand:

```text
raw = base_gt_raw(a, signed_num)
```

where:

```text
h path:    a = g, signed_num = signed_num_f, den_vec = den_f_inv_scaled
hinv path: a = f, signed_num = signed_num_g, den_vec = den_g_inv_scaled
```

Then, before the final `st4`, multiply every raw output vector by the matching
denominator-inverse vector:

```text
out0 = fqmul(raw0, den_vec)
out1 = fqmul(raw1, den_vec)
out2 = fqmul(raw2, den_vec)
out3 = fqmul(raw3, den_vec)
st4 {out0,out1,out2,out3}, [dst], #64
```

In the current `GT_BASEMUL_STORE_RMINUS1` final-store contract, the raw output
registers immediately before store are:

```text
v8  = raw0
v9  = raw1
v10 = raw2
v11 = raw3
```

A real prototype therefore needs a new experiment-only base_gt variant that
adds:

```text
ld1/ldr den_vec for the current group
four variable-vector Montgomery reductions raw_i * den_vec
st4 scaled outputs
```

It must not call `baseinv_batch_finish24_n1_asm()` and must not materialize
`finv/ginv`.

## Montgomery-domain note

`poly_basemul_scaled_r_input()` works because its second operand is already in
the scaled-R convention expected by the raw/rminus1 base_gt path.  If the
future fused body uses raw signed numerator as the second operand, the base_gt
raw result must be scaled by the same `den_vec` that the scaled finish loop
would have used.

Modulo q, this is the intended algebra:

```text
current:
  finv = fqmul(signed_num_f, den_f_inv_scaled)
  h    = basegt_scaled_input(g, finv)

fused:
  raw  = basegt_raw(g, signed_num_f)
  h    = fqmul(raw, den_f_inv_scaled)
```

The two paths are mathematically equivalent modulo q because the denominator is
a scalar in each quartic base ring and commutes with the quartic product.

However, exact int16 representative equality is not guaranteed by algebra
alone, because the Montgomery reductions happen in a different order.  A future
prototype must compare both:

```text
h_exact_mismatches
hinv_exact_mismatches
h_bytes_mismatches
hinv_bytes_mismatches
```

If exact representatives differ but bytes match, the candidate is byte-contract
only and cannot replace the arithmetic keygen path.

## Removed and retained traffic

For the x2 keygen path (`h` and `hinv`):

Removed if the true finalizer is implemented:

```text
48 finish-loop numerator ld4 groups
48 finish-loop scaled-inverse st4 groups
finish-loop branch/control and ABI overhead
```

Retained:

```text
48 numerator ld4 groups, now as the second base_gt operand
48 den_inv vector loads, now inside the fused finalizer
48 full quartic product groups
192 vector denominator scalar multiplications/reductions
```

So the route does not delete public arithmetic.  Its realistic win is the
standalone finish memory pass plus any scheduling overlap gained by moving
denominator scaling into the base_gt finalizer.

## Range contract

The new finalizer must prove:

```text
1. signed_num vectors are valid int16 inputs to the base_gt product DAG.
2. raw0..raw3 remain valid int16 outputs of the existing raw/rminus1 base_gt
   path before denominator scaling.
3. den_vec values are the same scaled denominator-inverse values accepted by
   baseinv_batch_finish24_n1_asm.
4. raw_i * den_vec uses the same variable-variable Montgomery reduction class
   as the finish loop and stores int16 outputs.
```

The raw output is already stored by the production rminus1/scaled base_gt path,
so it is a signed int16 value by construction.  The additional
`fqmul(raw_i, den_vec)` still needs a differential test because the raw product
range differs from the numerator range in the original finish loop.

## Why no prototype was emitted in this pass

No representative candidate can be built by composing existing public or
benchmark helpers:

```text
poly_basemul_scaled_r_input()
  requires the second operand to already be scaled by R.  Passing normal
  numerator scratch would only compute the wrong raw product.

baseinv_batch_finish24_n1_asm()
  only scales a materialized numerator poly into finv/ginv.  Calling it
  recreates the materialization pass this route is supposed to remove.

poly_keygen_compute_h_hinv_direct_model()
  still materializes finv/ginv and therefore measures the floor model, not the
  true finalizer.
```

The exact blocker for this pass is therefore the absence of an experiment-only
base_gt body variant with all three required changes in one loop:

```text
1. load normal numerator scratch and apply the [+, -, +, -] sign convention
   before the product DAG,
2. compute the raw base_gt product with the signed numerator,
3. apply den_vec to raw0..raw3 before the final st4.
```

Writing only part of this would produce either the wrong Montgomery-domain
contract or the already-measured temp-poly/floor route.

## Future prototype contract

Suggested symbol:

```c
int poly_keygen_finish_to_h_hinv_true_finalizer(
    poly *h,
    poly *hinv,
    const poly *f,
    const poly *g);
```

Suggested implementation outline:

```text
prepare f -> num_f scratch, den_f
prepare g -> num_g scratch, den_g
hier_k8 invert den_f/den_g, preferably using the existing x2/direct model tree
fused_basegt_den_scale(h,    g, num_f, den_f)
fused_basegt_den_scale(hinv, f, num_g, den_g)
```

Suggested internal body:

```text
fused_basegt_den_scale(dst, a, num, den)
  for i in 0..23:
    ld4 a0..a3, [a]
    ld4 n0..n3, [num]
    n1 = -n1
    n3 = -n3
    ld1 den_vec, [den]
    run production raw base_gt quartic product DAG
    raw0..raw3 = output vectors
    out0 = fqmul(raw0, den_vec)
    out1 = fqmul(raw1, den_vec)
    out2 = fqmul(raw2, den_vec)
    out3 = fqmul(raw3, den_vec)
    st4 out0..out3, [dst]
```

Future PMU rows:

```text
current_baseinv_plus_public_arith
direct_h_hinv_model_v1
finish_to_h_hinv_floor_model
finish_to_h_hinv_true_finalizer
full_keygen_current
full_keygen_candidate
```

Decision bar:

```text
>=150 cycles over current_baseinv_plus_public_arith: keep_and_refine
>=300 cycles over current_baseinv_plus_public_arith: serious candidate
full keygen regression: no promotion
```

## Current pass decision

```text
decision: document_only / design_ready
prototype: not written
PMU: not run
reason: no representative candidate exists without a new experiment-only
        base_gt finalizer body.  Wrapper/temp-poly prototypes are invalid.
```
