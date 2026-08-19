# GT32-CROSS-R3-QWORD-B3-INVERSE-RANGE-014

This generator-only gate tests whether experiment 013's actual nonuniform
Forward representatives can be consumed by the selected production B3 and the
unchanged current inverse without a new runtime normalization pass.

## Result

The boundary is narrower than the old uniform `10788` contract suggested:

- B3 accepts the actual 013 representatives with no input normalization.
- Every variable Montgomery product, accumulator, lambda product, and B3
  output edge remains signed-int16 safe.
- The maximum B3 output bounds for `c0..c3` are
  `[6797, 11461, 16187, 2719]`.
- The unchanged inverse does **not** close: its zero-repair I1 terminal bound
  reaches `40334`.

A plane-wide repair would center `c0,c1,c2`, costing 108 instructions.  A
finer whole-YMM search finds a locally irreducible repair of 24 private-SoA
vectors, costing 72 instructions.  This repair closes the current inverse, but
it is not a global-minimum proof.

For the executable region `2F + B3 + current inverse`, the two Forward
candidates save 64 static instructions, while the known selective repair adds
72.  The net is therefore **+8 instructions**, with 144 new vector multiply
uops replacing 192 `vpblendd` operations.  The zero-extra-cost continuation
gate fails, so no assembly is emitted.

## Decision

`013` remains a valid semantic/routing oracle, but its current-inverse path is
stopped before ASM.  Reopen only if an exact search proves a substantially
cheaper selective repair, a conjugated inverse closes the representative
range without repair, or the consumer range contract changes.

This is deliberately a scope-specific stop.  It does not block Encap, whose
Forward outputs never feed InvNTT, nor the two post-inverse Forward callsites
in Decap.  Those real caller edges are evaluated separately by experiment 015.

GT Clean is not modified.

## Reproduce

```sh
make check
```

The full proof is emitted to
`generated/qword_b3_inverse_range_gate.json`.
