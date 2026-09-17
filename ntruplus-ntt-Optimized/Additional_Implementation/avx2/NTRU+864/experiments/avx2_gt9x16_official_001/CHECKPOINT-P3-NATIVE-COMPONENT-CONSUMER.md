# P3-A: NTRU+864 native-component consumer feasibility

## Outcome

The common `T_d = Q16 x I_d` abstraction is exact for `d=3`: every
`(branch,p)` macro-tile contains 48 words and occupies exactly three YMM
registers. The exact packed-to-plane and plane-to-packed networks are now
lowered and lane-proved. The currently executable 16-bit direct-packed
BaseMul families still do not justify assembly.

## Exact `T3` boundary

The native words are q-major and j-minor:

```text
(q0,j0), (q0,j1), (q0,j2), (q1,j0), ... , (q15,j2)
```

The exact packed-to-plane network uses:

```text
3 x vperm2i128
9 x vpshufb
6 x vpor
----------------
18 routes/tile
```

The three cross-half permutations form the source-half pairs `(S0,S3)`,
`(S1,S4)`, and `(S2,S5)`. Three masked byte shuffles then contribute to each
coefficient plane, with two ORs merging the disjoint byte owners. The inverse
network is also constructive in 18 routes: it builds `(S0,S3)`, `(S1,S4)`,
and `(S2,S5)` and reassembles the three packed vectors.

Both networks are exact for all 48 tile words and the generated ownership
table covers all 864 physical cells.

As with 1152, only the forward packed-to-plane network is actual baseline
debt. Official's coefficient-plane BaseMul output is already directly
consumable by its inverse. The constructible 18-route `P^-1` is not executed
and is not available as credit.

```text
actual P budget = 18 routes/tile x 18 tiles = 324 routes/forward
actual P^-1 budget = 0
```

## Candidate arbitration

The full-deinterleave wrapper is rejected because it performs the same
18-route `P` inside BaseMul and then runs the existing 11-chain cubic
arithmetic. A uniform q-local 16-bit schedule is also rejected: 48-bit
components cross AVX2 64/128-bit boundaries and the straightforward lowering
falls back to the same deinterleave.

The only remaining arithmetic-specific opportunity is `vpmaddwd` for:

```text
a1*b2 + a2*b1
a0*b1 + a1*b0
a0*b2 + a2*b0
```

This is real packed-d3 structure, but it changes the arithmetic domain. The
candidate still needs the three singleton products, two fixed-zeta products,
an exact signed-32 modular reduction, repacking to signed i16, and an inverse
entry schedule. Until all of that is priced, the three dot products are not a
machine-level win.

## Decision and reopen condition

No namespaced ASM and no benchmark are authorized. The `vpmaddwd` path is
recorded as a separate arithmetic research candidate, not as a continuation
of the rejected 16-bit wrapper. P2 remains closed.

Reopen only when an exact `vpmaddwd + signed32 reduction + repack` schedule
beats the real 18-route input boundary after all triple alignment and inverse
entry work is counted.

Machine-readable evidence:

```text
generated/p3-native-component-consumer.json
```

