# P49 — Keygen Full normalization specialization

P49 is complete and rejected at its static arithmetic gate. Production remains
P46 Full ToBytes for the Keygen `f` serialization. No assembly, Slothy or Pi 5
timing was warranted because no correct lower-instruction candidate survived.

## Exact boundary

The producer is not the original small ternary polynomial. It is:

```text
CBD1 -> multiply by 3 -> coefficient zero +1 -> production K1 Forward
```

The existing P3B40 correlation-aware proof gives 288 FR0 leaf intervals for
this exact K1 path:

- global enclosure: `[-28765,28258]`;
- leaf widths: `33164..56866`;
- leaves wholly inside `(-3457,3457)`: **0 / 288**.

Consequently, replacing Full with Small is invalid. `x=3457`, contained in all
288 interval contracts, is already a canonical-byte counterexample: its residue
is zero, whereas direct 12-bit packing emits 3457.

## Three-instruction search

P46 uses four arithmetic instructions per routed vector:

```asm
sqrdmulh quotient, x, reciprocal9
mls       residual, quotient, q
ushr      sign, residual, #15
mla       canonical, sign, q
```

For the narrower K1 enclosure, its centered residual tightens from the generic
`[-3291,3291]` to `[-3107,3107]`, but it still takes both signs. The machine
search checked fixed-constant three-instruction quotient/remainder families:

1. shifted input, then `SQRDMULH`, then `MLS`;
2. `SQRDMULH`, constant quotient bias, then `MLS`;
3. `SQRDMULH`, signed quotient shift, then `MLS`.

No uniform exact solution exists. The stronger diagnostic search also found no
shifted or biased solution even when each of the 288 leaf intervals was allowed
its own constants. Positive-control intervals produce solutions and are fully
enumerated by the test, preventing an always-empty search from passing.

## Other closed alternatives

- P42 already measured `CMLT+MLS`: it is exact but moves pressure onto the A76
  multiply pipeline and regresses complete Keygen by 26.625 cycles.
- Reducing in Forward and then using a two-instruction Small correction still
  totals four arithmetic instructions per vector, so moving the boundary alone
  has no static advantage.
- Changing the secret-key byte representation is outside the contract and would
  change the KAT.

## Decision and reopen condition

Reject P49 without assembly. Reopen only if a new Forward producer DAG can emit
canonical or centered leaves by absorbing reduction into arithmetic already
required by the transform; merely relocating P46's reduction is insufficient.
The next gate is a fresh P50 selected-Official profiler checkpoint after the P46,
P47 and P48 production promotions.
