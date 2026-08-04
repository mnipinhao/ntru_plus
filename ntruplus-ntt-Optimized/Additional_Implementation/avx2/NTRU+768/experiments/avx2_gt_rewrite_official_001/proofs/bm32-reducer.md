# BM-A signed-32 reduction argument

Let `q = 3457`, `M = floor(2^32/q) = 1242397`, and let the signed
accumulator satisfy `|x| < 2^31`.  The AVX2 reducer first forms `u = |x|`;
the strict accumulator bound excludes `INT32_MIN`.

It computes

```text
qhat = floor(u*M/2^32).
```

Since `0 <= 1/q - M/2^32 < 1/2^32` and `u < 2^31`, `qhat` is either
`floor(u/q)` or one less.  Therefore `u - qhat*q` is in `[0,2q)`.  One
fixed comparison/subtraction puts it in `[0,q)`, and one fixed centered
correction puts it in `[-1728,1728]`.  The original sign is then restored;
all paths execute the same instruction sequence.

For BM-A, alpha-weighted inputs are reduced before `vpmaddwd`.  Each input
word is signed int16.  For every tested lazy candidate through `6q = 20742`,
each pair sum is bounded by `2B^2 < 2^31` and each four-term accumulator by
`4B^2 < 2^31`.  The implementation performs no lazy int16 add/sub before
the signed-32 products.  `7q` is excluded because its four-term bound is not
signed-32 safe.

Executable checks are in `tests/test_bm32.c`: fixed boundary values, one
million deterministic signed-32 reducer inputs, maximum/alternating quartic
patterns, random inputs for 3q/4q/5q/6q, scalar-int64 differential, aliasing,
and the final centered range.

BM-B is a 3q-only narrow Karatsuba control.  Its only unreduced int16
operation is a two-input sum/difference, bounded by `6q = 20742`.  Its widest
pre-reduction int32 expression is below `6B^2` for `B=3q`, hence below
`2^31`.  Products and cross terms are centered before alpha multiplication.
The paired benchmark rejects BM-B: it is slower and larger than BM-A.
