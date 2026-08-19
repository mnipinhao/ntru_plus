# GT32 streamed degree-8 bilinear contraction gate 020

This gate removes the persistent degree-8 ABI from the question.  It asks
whether the twelve rank terms can be produced, multiplied, and accumulated
directly into an inverse-entry basis without ever retaining the complete LHS,
RHS, product, or merge arrays.

## Exact input-liveness result

For each of the four quadratic roots the rank-3 product uses the forms
`E`, `O`, and `E+O`.  The twelve forms span all eight degree-8 input
coordinates.  More importantly, deleting **any one** of the twelve still
leaves rank eight.

Consequently no possible first product makes either source state smaller:

```text
remaining LHS information: 8 YMM
remaining RHS information: 8 YMM
first product/accumulator:  1 YMM
                             ------
minimum first cut:          17 YMM
```

The generator exhausts every possible first term and uses a 4096-state subset
DP to search all consumption orders.  Even under the optimistic fiction that
each product needs only one register and is then consumed for free, the best
peak is 17 YMM.  The selected QBM actually peaks at 11 YMM, so lowering it to
9 would not repair this first cut.

## Direct inverse accumulation

The exact degree-8 recombination matrix `W` is generated and checked against
all 64 monomial products for each of all 96 degree-8 leaves (6,144 checks).
The rank-eight and first-cut results are likewise checked for all leaves.
Composing `W` with a linear inverse-entry map is
algebraically valid:

```text
W' = T_inverse_entry * W
```

This does not add bilinear products and can avoid reconstructing a canonical
GT16 merge representation.  It does **not**, however, change the twelve input
forms or the 17-YMM first-product cut.  An inverse accumulator consumes a
register rather than freeing one.

## Escape costs and caller relevance

Re-evaluating four roots from memory adds 24 vector loads per operand/block,
or 288 vector loads for both operands over six blocks.  Materializing one
operand costs a complete 1536-byte store and reload (96 vector memory
operations).  Both violate the declared no-replay/no-materialization gate and
return to the already measured GT16-style boundary.

The Clean GT standard KEM call graph also has no multiplication of two freshly
Forward-produced operands: Encap is decoded-h times Forward-r, Decap uses
decoded/persistent operands, and Keygen is Forward-F0 times BaseInv-J1.  A
two-Forward coupled producer would therefore remain a synthetic primitive
unless decode and BaseInv gain matching typed contraction producers.

## Decision

No assembly is emitted.  The fixed four-quadratic rank-12 decomposition is
closed for no-replay, no-materialization streamed contraction on 16-register
AVX2.  This does not close a different bilinear decomposition whose early
term removal lowers the remaining source rank, a producer-specific
Decode/BaseInv contraction, or a wider-register ISA.

Before enumerating another rank-12 formula, experiment 021 tests the stronger
structural claim: the algebra's minimum nonzero multiplication-map rank is two,
which may forbid a single-term rank drop for every rank-1 decomposition.

## Reproduction

```sh
make check
```
