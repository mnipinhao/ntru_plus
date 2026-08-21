# Checkpoint G0: consumer-edge representation design space

G0 adds no assembly and records no new cycle result. It turns the representation
choice into a reproducible design-space audit before any G1 prototype is
written. Official NTRU+ remains the production baseline; F-R3D D1 is only the
repository-local measured forward control.

## Representation and evidence schema

Every view is described as `R=(P,Q,B,g,s,O)`:

- `P`: physical NTT9 row to mathematical frequency;
- `Q`: physical NTT16 lane to mathematical frequency;
- `B`: degree-4 terminal basis and packing;
- `g`: component gauge or absorbed phase;
- `s`: arithmetic transform scale and Montgomery scale;
- `O`: transform orientation and network order.

The generator separates `official-audited`, `experiment-measured`,
`generated-algebraic`, and `new-hypothesis` evidence. Unknown costs stay null.
Static instruction counts are never interpreted as cycle predictions.

Every movement is classified mechanically as `unavoidable`,
`fusible-into-producer`, `fusible-into-consumer`, `free-by-table-change`, or
`paid-standalone`. A paid standalone full-array conversion is rejected before
assembly. The remaining views always expose Montgomery operations, routing,
loads/stores, constants, peak YMM pressure, range, conversions, and consumer
routing debt, even when a value is not known yet.

## Consumer graph

`generated/g0-consumer-graph.json` defines the three paths that later timing
must cover:

```text
F_E -> BMAdd -> actual encapsulation downstream
F_M + F_M -> BMScale -> I_M
F_I -> BaseInv -- den[18] side state --> I_I
```

The last edge is a research path, not a claim that the pinned Official caller
already has that exact edge. It requires the paper scale ledger's
BaseInv-output scale and a scale-correct adjusted inverse. Official's observed
`BMScale -> inverse` edge remains the audited control.

## Generated families and pruning

| Family | View | G0 decision | Reason |
| --- | --- | --- | --- |
| F0 | D1 persistent S/D | measured control | 683.5 cycles versus the 696-cycle contiguous Official body; no complete consumer path |
| F1 | terminal-major consumer-natural | G1 shortlist | zero arithmetic-side routing in Checkpoint E; final reconstruction must fuse into D1 stores |
| F2 | `p,-p` row pairing | deferred | only one of four nonzero pairs is physically adjacent; factor relation and ranges remain unproved |
| F3 | consumer-fused terminal basis | G1 shortlist | potentially moves basis work into real arithmetic, but needs symbolic identities and range proof |
| F4 | encapsulation terminal streams | G1 shortlist | dense layout is proved; the real BMAdd downstream contract still needs audit |
| F5 | inverse-feed hybrid | G1 shortlist | Checkpoint E estimates 144 store-side routing instructions; paired inverse is not implemented |
| X0 | universal natural-order ABI | rejected | requires a paid standalone full-array canonicalization |

The F1 estimate of 144 routing instructions is an explicit-schedule estimate
for reconstructing 18 rows inside the producer, not a measured cost. F5's 144
is likewise a store-side arithmetic estimate. F3/F4 unknowns are not treated
as zero.

## G1 order and gates

G1A first builds independent scalar/layout oracles for every shortlisted edge.
G1B measures F1's real producer-boundary tax, while the orthogonal G1C measures
F5 arithmetic-store/inverse-head debt and credit. G1D covers F4's real
encapsulation downstream, and G1E performs F3's cheap-basis algebraic search.
Each linked object must pass algebra, scale, signed-16 range, ABI, alias/canary,
and constant-time checks before timing.

Only same-ELF paired measurements of the three complete paths above may select
a view. A forward-only win, static routing estimate, or isolated BaseMul win
cannot select production. SUPERCOP/KEM work remains after a complete caller
path wins locally.

Run `make generate` to refresh the artifacts and `make check` to verify exact
reproduction plus the G0 pruning/shortlist test.
