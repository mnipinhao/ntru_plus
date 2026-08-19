# GT32 degree-8 first-cut impossibility proof 021

020 found a 17-YMM first cut for the selected four-quadratic rank-12
decomposition.  This gate proves that changing to another rank-12 formula
cannot provide the requested single-term rank drop.

## Algebra certificate

For every one of the 96 degree-8 leaves,

```text
A = F_q[x]/(x^8-mu) ~= K0 x K1 x K2 x K3,
Ki = F_q[z]/(z^2-ri).
```

The four roots are distinct nonsquares and their factors multiply exactly to
`z^4-mu`.  Multiplication by `u+v*z` in a component has matrix

```text
[[u, ri*v],
 [v, u]]
```

with determinant `u^2-ri*v^2`.  Since `ri` is nonsquare, every nonzero
component multiplication is invertible and has rank two.  Therefore a
nonzero element of the product algebra has multiplication-map rank in
`{2,4,6,8}`, never rank one.

## Arbitrary rank-1 decomposition theorem

Let any rank-1 decomposition, of any length, be

```text
T = sum_j ell_j tensor r_j tensor w_j.
```

If removing `ell_j` reduced the remaining left span from eight to seven,
there would be a nonzero `a` annihilated by every other `ell_i` but not by
`ell_j`.  Fixing that input gives

```text
M_a(b) = ell_j(a) * r_j(b) * w_j,
```

a map of rank at most one.  This contradicts the rank-two minimum above.  The
same proof applies on the right.  Thus removing any one rank-1 term leaves
both source spans at rank eight, independent of the particular decomposition
or whether it has exactly twelve terms.

The one-term streaming first cut is consequently structural:

```text
8 LHS + 8 RHS + 1 product/accumulator = 17 YMM.
```

Brute-forcing alternative rank-12 decompositions for a single-term 8-to-7
drop is therefore closed.

## Why two-term hardware remains open

For the current twelve forms, 12 of the 66 term pairs reduce the remaining
input rank from eight to seven; they are precisely pairs inside one quadratic
component.  Atomic removal on both operands leaves 14 source dimensions.

However, the corresponding output-recombination columns are not
proportional.  The existing Karatsuba terms therefore cannot simply be added
into one scalar accumulator without losing output information.  The next
gate must test a genuinely rank-2 hardware contraction: pair-native
schoolbook or lane-separated `vpmaddwd`, i32 range, preweight cost, and final
reduction—not merely fuse two current rank-1 terms on paper.

## Decision

No assembly is emitted.  Single-rank-1-term streaming is structurally closed
for this algebra on AVX2.  `GT32-QBM-PAIR-MADDWD-022` is the next generator-only
gate.

## Reproduction

```sh
make check
```
