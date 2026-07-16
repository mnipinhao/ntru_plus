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
   add/sub remains representable.

The transform argument stops at the forward boundary.  The separate SoA
basemul argument below extends the prototype through pointwise multiplication;
it does not yet cover a matching inverse kernel.

## Final reducers

The intrinsic row-bitrev comparison path sign-extends each value to int32 and
uses the reference-compatible rounded Barrett reduction.  Its output is in
`[-1729,1729]`; at an exact half-modulus boundary it may choose either signed
representative.

The stage-3+4+5 ASM path instead keeps the checkpoint packed in int16 lanes:

```text
t = (signed_mulhi(a, 19412)) >> 10
r = a - t*3457
```

Here `>>` is an arithmetic right shift.  Every integer input in the proven lazy
interval `[-27648,27648]` was exhaustively checked to satisfy both
`r == a (mod 3457)` and `0 <= r <= 3457`.  The multiply by 3457 and subtraction
remain representable in the int16 operations used by the implementation.  The
different representative convention is intentional; differential tests compare
modulo q.

The final 8x8 transpose and SoA store are a pure permutation and therefore do
not change bounds or residues.  For DFT3 row `k3`, NTT32 index `Q`, branch `b`,
and quartic coefficient `c`, the output word is
`64*(4*k3+Q/8) + 16*c + 8*b + Q%8`.  Both directions of this 768-word mapping
are tested against the verified GT row-bitrev reference.

## SoA quartic basemul

The intrinsic pointwise prototype accepts normal-domain representatives
`|a_i|,|b_i| <= q`.  Define

```text
p_ij = Mont(a_i*b_j)
```

for each of the 16 runtime products.  Since `|a_i*b_j| <= q^2` and
`q^2 < q*2^15`, the scalar Montgomery precondition holds and every `p_ij` is
in `[-(q-1),q-1]` in the `R^-1` domain.

The quartic wrap accumulators are:

| Value | Expression | Bound before lambda |
| --- | --- | ---: |
| `w0` | `p13+p22+p31` | `3(q-1)` |
| `w1` | `p23+p32` | `2(q-1)` |
| `w2` | `p33` | `q-1` |

Each `lambda` is a centered Montgomery-form constant with magnitude at most
1728.  Therefore the largest fixed-factor input product is bounded by
`3(q-1)*1728 < q*2^15`; `Mont(w_i*lambda)` returns to one modulus in the same
`R^-1` domain.  Adding the non-wrapped products gives these conservative
bounds:

| Output accumulator | Bound before finalization |
| --- | ---: |
| `u0` | `2(q-1)` |
| `u1` | `3(q-1)` |
| `u2` | `4(q-1)` |
| `u3` | `4(q-1)` |

The maximum packed addition magnitude is therefore
`4(q-1)=13824 < 32768`, so no `vpaddw` wraps.  Finally, `R^2=867` in centered
Montgomery form and `4(q-1)*867 < q*2^15`; `Mont(u_i*R^2)` returns a normal-
domain representative in `[-(q-1),q-1]`.

All 12 batch iterations and table addresses depend only on public indices.
There are no value-dependent branches, corrections, or memory accesses.  The
three API arrays are required not to overlap; this is an optimization contract,
not a secret-dependent condition.
