# Range argument for the AVX2 GT prototype

All statements below assume the explicit prototype precondition
`|a[i]| <= q-1`, where `q=3457`.  Congruences are modulo `q`; `R=2^16`.

1. The top-split Montgomery product is in `[-(q-1),q-1]`.  The two raw
   branch expressions are at most `2(q-1)` and `3(q-1)` respectively, which
   fit signed 16-bit lanes.
2. The branch twist is another Montgomery product.  Its input product obeys
   the scalar reducer precondition, and its output returns to a one-modulus
   residue bound.
3. A DFT3 output is a sum/difference of three one-modulus residues, hence is
   bounded by `3(q-1)=10368`.
4. Each radix-2 stage adds or subtracts one Montgomery-reduced term bounded
   by `q-1`.  With lazy additions, the bounds after stages 1 through 5 are
   `4(q-1)`, `5(q-1)`, `6(q-1)`, `7(q-1)`, and `8(q-1)`.
5. The largest bound is `8(q-1)=27648 < 32768`, so every lazy signed-int16
   add/sub remains representable.  The final vector Barrett step returns the
   reference-compatible rounded representative in `[-1729,1729]` before
   scatter.  At exact half-modulus boundaries it may choose `-1729` or
   `1729`; this is intentionally the same convention as the existing scalar
   reducer.

The proof deliberately stops at the forward transform boundary.  It does not
yet claim compatibility of the new layout with the existing AVX2 basemul or
inverse kernels; this prototype preserves the verified GT row-bitrev layout
instead.
