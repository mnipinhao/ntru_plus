# GT32-QUARTIC-BILINEAR-TENSOR-059

This generator changes the quartic multiplication tensor rather than searching
another basis for the current K2/TMVP tensor.

For each effective GT lambda it constructs exact evaluation/interpolation
tensors for

```text
F_3457[x] / (x^4 - lambda).
```

The primary family evaluates two degree-three polynomials at six finite points
and infinity, performs seven variable-by-variable products, interpolates the
degree-six product, and folds `x^4=lambda` directly into a lambda-specific
output matrix.  A redundant rank-eight family and an asymmetric producer-row
scaling family are retained as controls.

## Result

- 84 small-point rank-seven sets were searched.
- Rank seven is exact on all 192 lambda entries and all 16 monomial input
  products per lambda.
- The rank-eight redundant control is exact on the same corpus; its
  one-dimensional interpolation freedom is exhaustively optimized over all
  3457 field values for every output and lambda.
- An asymmetric `U_h != V_r` row-scaled rank-seven tensor is also exact.

The rank-seven family changes the algebraic operation class:

```text
current quartic variable products: 9
rank-seven evaluation products:    7
bilinear-rank delta:               -2
```

The selected L01 implementation uses 12 physical full-width Montgomery chains,
but those chains already mix variable-product and lambda work.  Rank seven has
seven pointwise product chains **before** lowering `W_lambda`; the unresolved
interpolation/constant chains must be added before making a total physical-
chain or cycle comparison.

This is a research-continuation result, not a production claim.  Interpolation
constants, range checkpoints, register pressure, and producer formation may
still make the executable implementation slower.  They no longer justify a
static closure based only on total instruction count, because the tensor has
deleted a variable-product class and introduced a producer-native redundant
contract.

The next gate is an explicit AVX2 lowering and range/liveness analysis for the
selected rank-seven tensor.  GT Clean is unchanged.

## Reproduction

```sh
python3 tools/generate_gate.py
```
