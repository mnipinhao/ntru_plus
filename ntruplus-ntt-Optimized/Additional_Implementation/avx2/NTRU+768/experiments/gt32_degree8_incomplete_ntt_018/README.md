# GT32 degree-8 incomplete-NTT gate 018

This generator-only gate tests the highest-priority decomposition gap from the
post-017 coverage audit.  GT Clean is not modified and no assembly is emitted.

The generated artifact also records a hash-pinned 011--017 coverage registry.
It preserves the important distinction that 011 is a representation census,
not executable closure of all 96 states.  Dynamic stage packets, streamed
evaluation/LHS-RHS coupling, and the untested pair-native packet families stay
open; 018 advances only the degree-8 branch.

## Coverage correction

The existing GT16 experiment does not persist a degree-8 ABI: it conjugates a
radix-2 split across the radix-3 dimension and materializes the same 384
quadratic CRT components.  Nevertheless it is stronger than merely adjacent
evidence.  It is one complete executable schedule for the same degree-8
factor algebra, including Forward, QBM, merge, and NTT16 inverse.  What remains
open is a *direct degree-8 packet schedule* that deletes work relative to that
measured conjugate rather than replaying its split/QBM/merge path.

## Exact degree-8 algebra

For every omitted-S5 pair, the selected quartic moduli are opposite:

```text
x^4 - lambda
x^4 + lambda
```

and therefore form one degree-8 quotient:

```text
(x^4-lambda)(x^4+lambda) = x^8-lambda^2.
```

The generator checks all 96 physical pairs.  Each `lambda` and `-lambda` is a
square but not a fourth power, so the degree-8 algebra factors into four
irreducible quadratic components.  All 64 monomial products are checked in all
four components for every leaf: 24,576 exact modular checks.

This also fixes the bilinear-rank accounting.  The dimension is eight and the
algebra has four maximal components, giving the Alder--Strassen lower bound
`2*8-4=12`.  Four rank-3 quadratic products attain 12.  Thus degree-8 does not
have a multiplication-rank advantage over the already known quadratic
factorization.

## Where a runtime win could still come from

The selected Forward S5 uses four nine-instruction Montgomery packet calls per
tile and six tiles: 216 instructions and 24 Montgomery chains per Forward.
Two Forward calls therefore expose 432 instructions and 48 chains before any
credit for terminal plane routing or inverse S5/entry work.

A degree-8 implementation is interesting only if a native rank-12 packet
schedule deletes that work.  Recreating two S5 evaluations inside BaseMul and
an inverse S5 afterward is not a new mechanism.

## Decision

The algebra passes, but assembly is not yet authorized.  The next bounded gate
must synthesize one 16-leaf degree-8 packet BM and its inverse entry, prove
range and liveness, and compare whole `2F+B+I` multiply uops after crediting the
deleted S5 chains.  It must use at most 15 YMM, spill nothing, add no global
checkpoint, and retain at least a 20-TSC-equivalent static margin.

## Reproduction

```sh
make check
```

Primary artifact:

- `generated/degree8_incomplete_ntt_gate.json`
