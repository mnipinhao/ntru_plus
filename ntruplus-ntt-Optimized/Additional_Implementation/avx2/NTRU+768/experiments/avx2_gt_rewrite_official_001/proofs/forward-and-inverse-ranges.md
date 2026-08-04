# Forward and inverse int16 range argument

For the public coefficient-domain contract, every input is in `[-3,4]`.
The raw top split is deliberately not Montgomery-reduced:

```text
branch 0: low - 722*high = [-2891,2170]
branch 1: low + 723*high = [-2172,2896]
combined:                    [-2891,2896]
```

The preweight and every DFT3 output are reduced to centered canonical
`[-1728,1728]` before entering NTT32.  B1's initial even-half sum is therefore
in `[-3456,3456]`; its first cyclic16 butterfly can reach at most
`[-6912,6912]`.  Every butterfly immediately applies the fixed-count centered
reducer, so all later additions and subtractions are in `[-3456,3456]`.
B2 reduces the initial even-half sum too, and is strictly tighter.  The odd
half is reduced after its twist.  These intervals all fit signed int16.

The paired inverse loads centered data, reduces after every cyclic16
butterfly, normalizes each half before its merge, and stores centered outputs.
Its inverse DFT3, inverse preweight, top CRT, and coefficient-order store are
fused 8-lane signed-int32 AVX2 operations inside `gt_poly_invntt_avx2_b`.
Their largest products are below six million, are reduced before narrowing,
and have no standalone production untwist or normalization pass.

`tests/test_scalar_gt.c` checks these boundaries at every stage for zero,
impulses, `[-3,4]` extrema, alternating extrema, and deterministic random
inputs, and differentially checks the AVX2 B1/B2 rows against B1, B2, and C
scalar schedules.
