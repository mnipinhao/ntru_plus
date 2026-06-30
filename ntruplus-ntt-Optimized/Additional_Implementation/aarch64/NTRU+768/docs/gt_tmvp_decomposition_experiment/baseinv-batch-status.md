# GT batch baseinv status

Date: 2026-06-24

## Scope

This round adds a batched GT base inverse for the two layouts that were still
using scalar quartic `baseinv()` in the KEM keygen path:

- `gt_production_opt`
- `candidate_a_direct_tuple`

The implementation is in:

- `poly_gt_baseinv_batch.c`
- `gt_test/test_gt_baseinv_batch.c`

## Contract

The block-major ABI is:

```text
coeff[branch * 384 + 4 * physical_j + lane]
lambda = gt_rowbitrev_lambda[branch][physical_j]
```

The tuple ABI is:

```text
coeff[branch][row][k32][lane]
physical_j = (32 * row + 3 * k32) mod 96
lambda = gt_rowbitrev_lambda[branch][physical_j]
```

Both variants compute the same mathematical inverse as the scalar reference,
but the residue representative may differ.  The contract test compares modulo
`q`, not exact signed representation.

## Algorithm

For each group of eight quartic leaves:

```text
ld4 a0,a1,a2,a3
compute t0,t1,t2 and determinant den
compute numerator n0,n1,n2,n3
st4 numerator
store den vector
```

Then:

```text
batch-invert 24 den vectors
reload numerator with ld4
multiply by den^{-1}, -den^{-1}, den^{-1}, -den^{-1}
st4 final inverse
```

The block-major path loads lambda with contiguous `vld1q_s16`.  The tuple path
now uses a fixed tuple-order lambda table, so the hot loop also uses a direct
`vld1q_s16` instead of building an 8-lane public lambda vector at runtime.

## Wiring

`gt_production_opt` now uses `poly_gt_baseinv_batch.c` as the ABI
`poly_baseinv()` provider, while `asm/base_gt.opt.s` still provides
`poly_basemul()` and `poly_basemul_add()`.

`candidate_a_direct_tuple` now compiles `poly_gt_baseinv_batch.c` with
`GT_BASEINV_BATCH_NO_ABI_WRAPPER` and calls
`poly_baseinv_gt_tuple_batch()` from its local `poly_baseinv()`.

## Pi5 result

Standalone baseinv target, using the fixed-core run after build:

```text
make -B test_gt_baseinv_batch
taskset -c 3 ./build/test_gt_baseinv_batch

gt_baseinv_batch_correctness: ok
gt_scalar_block_baseinv_ticks: 758
gt_batch_block_baseinv_ticks: 112
gt_scalar_tuple_baseinv_ticks: 772
gt_batch_tuple_baseinv_ticks: 127
```

Same KEM harness:

```text
target                                count  KEYGEN  ENCAP  DECAP
test_kem_stock                            0     946    924    791
test_kem_gt_production                    0    2257    899    771
test_kem_gt_production_opt                0     964    897    767
test_kem_gt_tmvp_candidate_a_direct_tuple 0    1012    921    861
```

Compared with the pre-batch-baseinv numbers:

```text
target                                old KEYGEN  new KEYGEN
test_kem_gt_production_opt                  2255         964
test_kem_gt_tmvp_candidate_a_direct_tuple   2309        1012
```

Relative deltas:

```text
block-major baseinv kernel: 758 -> 112 ticks, -85.2%, 6.77x faster
tuple baseinv kernel:       772 -> 127 ticks, -83.5%, 6.08x faster

gt_production_opt KEYGEN:   2255 -> 964 ticks, -57.3%, 2.34x faster
Candidate A tuple KEYGEN:   2309 -> 1012 ticks, -56.2%, 2.28x faster

gt_production_opt vs stock: KEYGEN +1.9%, ENCAP -2.9%, DECAP -3.0%
Candidate A vs gt_prod_opt: KEYGEN +5.0%, ENCAP +2.7%, DECAP +12.3%
```

## 2026-06-24 tuple lambda table update

The first follow-up removed the Candidate A direct-tuple runtime lambda gather.
`poly_gt_baseinv_batch.c` now has a fixed
`gt_tuple_baseinv_lambda[2][12][8]` table generated from:

```text
physical_j = (32 * row + 3 * k32) mod 96
lambda     = gt_rowbitrev_lambda[branch][physical_j]
```

So tuple batch baseinv no longer does:

```text
tuple_lambda8(lambda_buf, branch, block)
vld1q_s16(lambda_buf)
```

and instead does one direct table load:

```text
vld1q_s16(gt_tuple_baseinv_lambda[branch][block / 8])
```

Pi5 rebuild/run from `make -B test_gt_baseinv_batch`:

```text
gt_baseinv_batch_correctness: ok
gt_scalar_block_baseinv_ticks: 758
gt_batch_block_baseinv_ticks: 112
gt_scalar_tuple_baseinv_ticks: 773
gt_batch_tuple_baseinv_ticks: 112
```

This removes the previous tuple-specific gap:

```text
tuple batch baseinv: 127 -> 112 ticks, -11.8%
tuple vs block-major batch baseinv: 127 vs 112 -> 112 vs 112
```

Pi5 Candidate A direct-tuple KEM after the table update, on top of the current
stock-support and tuple-input inverse NTT wiring:

```text
target                                  count  KEYGEN  ENCAP  DECAP
test_kem_gt_tmvp_candidate_a_direct_tuple   0     963    896    765
```

Relative to the latest pre-table Candidate A direct-tuple row
`991 / 896 / 766`:

```text
KEYGEN: 991 -> 963 ticks, -2.8%
ENCAP : unchanged
DECAP : unchanged within noise
```

Relative to the older post-batch-baseinv row `1012 / 921 / 861`, the total
movement also includes the separate stock-support and tuple-input inverse NTT
wiring:

```text
KEYGEN: 1012 -> 963 ticks, -4.8%
ENCAP :  921 -> 896 ticks, -2.7%
DECAP :  861 -> 765 ticks, -11.1%
```

## Interpretation

This confirms that scalar base inverse was the dominant keygen gap in the GT
and Candidate A paths.

After this round, `gt_production_opt` is approximately stock-speed in KEYGEN
and still slightly faster in ENCAP/DECAP.  Candidate A direct tuple no longer
pays the tuple lambda gather cost in baseinv; the remaining gaps are now in
the transform/basemul/inverse pipeline rather than in this baseinv table lookup.

The current `test_kem_gt_production` target is useful as a scalar-baseinv
control: it still shows the same keygen-scale hole because it does not use the
new batched base inverse.

## Next work

- Inspect compiler output for `poly_gt_baseinv_batch.c` and decide whether the
  prepare phase should become symbolic ASM/Slothy.
- Consider connecting the same block-major batch baseinv to
  `gt_tmvp_asm_gtntt` if that route remains useful.
