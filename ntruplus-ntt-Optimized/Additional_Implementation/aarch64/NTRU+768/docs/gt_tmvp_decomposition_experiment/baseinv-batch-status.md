# GT batch baseinv status

Date: 2026-06-24

## Scope

This round adds a batched GT base inverse for the production GT layout that
was still using scalar quartic `baseinv()` in the KEM keygen path:

- `gt_production_opt`

The implementation is in:

- `poly_gt_baseinv_batch.c`
- `gt_test/test_gt_baseinv_batch.c`

## Contract

The block-major ABI is:

```text
coeff[branch * 384 + 4 * physical_j + lane]
lambda = gt_rowbitrev_lambda[branch][physical_j]
```

The batched variant computes the same mathematical inverse as the scalar
reference, but the residue representative may differ.  The contract test
compares modulo `q`, not exact signed representation.

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

The block-major path loads lambda with contiguous `vld1q_s16`.

## Wiring

`gt_production_opt` now uses `poly_gt_baseinv_batch.c` as the ABI
`poly_baseinv()` provider, while the GT basemul symbols are owned by
`asm/gt/basemul/poly_basemul.S` and
`asm/gt/basemul/poly_basemul_add.S`.  Both draw from the promoted
GT basemul body where applicable.

## Pi5 result

Standalone baseinv target, using the fixed-core run after build:

```text
make -B test_gt_baseinv_batch
taskset -c 3 ./build/test_gt_baseinv_batch

gt_baseinv_batch_correctness: ok
gt_scalar_block_baseinv_ticks: 758
gt_batch_block_baseinv_ticks: 112
```

Same KEM harness:

```text
target                                count  KEYGEN  ENCAP  DECAP
test_kem_stock                            0     946    924    791
test_kem_gt_production                    0    2257    899    771
test_kem_gt_production_opt                0     964    897    767
```

Compared with the pre-batch-baseinv numbers:

```text
target                                old KEYGEN  new KEYGEN
test_kem_gt_production_opt                  2255         964
```

Relative deltas:

```text
block-major baseinv kernel: 758 -> 112 ticks, -85.2%, 6.77x faster

gt_production_opt KEYGEN:   2255 -> 964 ticks, -57.3%, 2.34x faster

gt_production_opt vs stock: KEYGEN +1.9%, ENCAP -2.9%, DECAP -3.0%
```

## Interpretation

This confirms that scalar base inverse was the dominant keygen gap in the GT
path.

After this round, `gt_production_opt` is approximately stock-speed in KEYGEN
and still slightly faster in ENCAP/DECAP.

The current `test_kem_gt_production` target is useful as a scalar-baseinv
control: it still shows the same keygen-scale hole because it does not use the
new batched base inverse.

## Next work

- Inspect compiler output for `poly_gt_baseinv_batch.c` and decide whether the
  prepare phase should become symbolic ASM/Slothy.
