# GT9X16-PROD3-MA2-HASH-DIRECT-MAP

## Scope

This checkpoint maps the materialized scale-4 PROD3/MA2 coefficient planes
directly to the 1,728 bytes required by pinned Official `poly_tobytes`. It is
a static ownership, range, and movement proof. It does not add serializer
assembly, change PROD3 or MA2 arithmetic, or run a benchmark.

The target boundary is deliberately bytes rather than an Official NTT array:

```text
MA2 scale-4 coefficient planes
  -> inv4/canonicalization
  -> exact 12-bit packing ownership
  -> 1728 bytes
```

Neither a generic-F0 array nor a 2,304-byte Official-order coefficient array
belongs in the target contract.

## Exact ownership result

`generated/gt9x16-prod3-ma2-hash-direct-map.json` joins the existing semantic
owner `(branch,p,q,terminal_coefficient)` from the MA2 plane map to its exact
Official coefficient index. It then expands every coefficient into the exact
bits it owns in the pinned two-coefficients/three-bytes format.

The mechanical proof closes all cardinalities:

| Object | Count |
| --- | ---: |
| MA2 cells | 1,152 |
| Official coefficient indices | 1,152 |
| serialized coefficient pairs | 576 |
| serialized bytes | 1,728 |
| MA2 vectors | 72 |
| serializer blocks | 9 |

Correction from ASM0 raw-byte closure: `official_coefficient` is a physical
Official NTT cell, not the linear serialized coefficient index. Pinned
`pack.s` transposes each eight-vector input block. A basis probe now records
that exact physical-to-serialized permutation before assigning byte ownership.
Under the corrected mapping, zero of the 576 true adjacent serialized pairs is
contained in one MA2 vector. The earlier same-vector H2 conclusion and its
72-load lower bound are withdrawn. The H1 physical-block construction remains
valid because it reconstructs exactly the vectors consumed by `pack.s`.

## Exact scale and range proof

The proof exhaustively evaluates every signed integer in the global proved
PROD3 MA2 envelope:

```text
input scale-4 representative: [-20751, 20753]
tested integers:               41505
inv4 Montgomery output:        [-1998, 1998]
direct canonical output:       [0, 3456]
```

For every tested value the AVX2 `vpmullw`/`vpmulhw` Montgomery identity using
`-901` and `16379` satisfies `4*y == x (mod 3457)`. The output lies strictly
inside `(-q,q)`, so one sign-mask add of `q` is sufficient. Exhaustive
comparison also proves that this direct sign canonicalization is bit-exact
with pinned Official `pack.s`, including its `vpmulhrsw` Barrett step. The
Official Barrett step is therefore redundant after this inv4 operation, and
the resulting `[0,3456]` values are safe for 12-bit packing.

This is a representative-level proof, not merely a modular differential.

## Movement ledger

The current H0 ledger is derived from the linked source shapes already used by
the hash bridge:

| Dynamic vector work | H0 current | H1 direct Official block | H2 packing-oriented |
| --- | ---: | ---: | ---: |
| initial MA2/source loads | 72 | 272 | withdrawn; redesign required |
| intermediate reloads | 416 | 0 | 0 |
| intermediate stores | 216 | 0 | 0 |
| routing before pack | 408 | 336 | withdrawn; exact open |
| inv4 Montgomery vectors | 72 | 72 | 72 |
| Official Barrett vectors | 72 | 0 | 0 |
| sign canonicalization vectors | 72 | 72 | 72 |
| pinned pack bit/transpose instructions | 468 | 468 | exact schedule open |
| final 32-byte stores | 54 | 54 | 54 target |
| coefficient temporary | 4,608 B | 0 | 0 |

H0 comprises:

```text
planes -> generic F0: 72 loads, 72 routes, 72 stores
generic F0 -> Official: 272 loads, 336 routes, 72 stores
inv4 array pass: 72 reloads, 72 Montgomery vectors, 72 stores
Official pack: 72 reloads, 72 Barrett vectors, 468 pack instructions, 54 stores
```

H1 independently re-derives the same 136 source-half groups as the existing
proved MA0 adapter. It can reconstruct each eight-vector Official serializer
block in registers and immediately apply inv4, sign-add-q, and the pinned pack
network. This supplies an exact construction upper bound with no coefficient
temporary. Relative to H0 it removes 216 vector loads/reloads, all 216
intermediate stores, 72 pre-pack routes, and the redundant 72-vector Barrett
stage.

H2 no longer has a proved 72-load bound. A future H2 must start from the probed
physical-to-serialized permutation and account for cross-vector pair formation
before any route, store, or register-pressure claim.

## Decision

The ownership, byte boundary, and range portions of the direct-hash map pass.
H1 is selected as the first realization to schedule because it already removes
all full-array materialization and has an exact, mechanically counted register
construction. The old H2 realization is invalidated and requires a new map.

No serializer assembly or benchmark is authorized by this checkpoint. The
next checkpoint is a static H1/H2 register schedule and linked instruction
budget. It must prove a spill-free schedule and exact 54-store byte geometry
before either realization is implemented.

The native interpretation remains unchanged: the approximately 530-cycle
excess hash tax is the recoverable target of this work, while the separate
approximately 182-cycle PROD3 producer debt remains open and cannot be erased
by a direct serializer claim.
