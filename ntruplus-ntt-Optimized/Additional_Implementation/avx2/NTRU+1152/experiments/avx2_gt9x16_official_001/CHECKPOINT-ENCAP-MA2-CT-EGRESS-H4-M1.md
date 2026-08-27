# ENCAP-MA2-CT-EGRESS-H4-M1

> **Ownership-derived conclusions rejected by H4-M2D.** This checkpoint used
> the legacy `serialized_coefficient` field as wire identity. Its pair graph,
> pending bound, presentation frontier, and serializer ranking must not
> authorize implementation. See
> `CHECKPOINT-ENCAP-MA2-CT-EGRESS-H4-M2D.md`.

H4-M1 searches the terminal presentation from live caller-wide scale-1 MA2
outputs to exact 12-bit serializer-pair ownership. It does not require or
create a complete Natural-Q `c[1152]` object, and it does not emit assembly.

## Exact pairing graph

The 72 live H3 terminal vectors form 576 exact serializer-pair edges. All
edges have the same shape:

```text
same MA2 vector:             0 / 576
same lane, different YMM:  576 / 576
different lane:              0 / 576
adjacent terminal time:     576 / 576
```

The low/high vector pairs are exactly `(c0,c1)` and `(c2,c3)` inside one
semantic tile. Thus the pair-join routing lower bound is zero: after Barrett
and sign canonicalization, the two vectors can participate directly in
lane-wise 12-bit pair packing. The old H1 count of 336 coefficient-reorder
routes is the price of reconstructing eight Official vectors, not an
unavoidable serializer-pair cost.

## Legal terminal freedom

The search distinguishes execution-order freedom from real data movement.

Free:

- emit the four independent semantic outputs in any legal order;
- swap the two independent MA2 tiles following one H3 decode block;
- relabel offline constants when a paid lane transformation is chosen.

Not free:

- renaming the semantic ownership of `c0..c3`;
- reinterpreting a YMM half or lane without moving its value;
- changing the frozen Natural-Q `r/m/h` input ABI;
- claiming a radix-butterfly output swap: the MA2 terminal sums are not an
  `A+B/A-B` butterfly.

This keeps every ciphertext coefficient owner exact while still allowing the
consumer to choose execution and paid presentation.

## Plane emission lower bound

All 24 permutations of `c0,c1,c2,c3` were exhausted. Eight orders keep each
pair of planes adjacent. They attain:

```text
minimum maximum pending coefficients: 16
minimum pending storage:               1 YMM
```

The existing `c0,c1,c2,c3` order is already one optimum. The 16-coefficient
bound follows from the current terminal atomicity: one hook produces a full
`16xi16` YMM before its partner vector exists. Reaching two or four pending
coefficients would require a new sub-vector arithmetic schedule, not a free
emission reorder.

The materialization lower bound remains zero because each pending vector can
flow directly into its adjacent partner.

## Tile emission order

Each of the nine H3 decode blocks feeds two complete MA2 tiles, and each tile
owns one contiguous 96-byte ciphertext span. The current order emits six of
the nine tile pairs high-span first. Exhausting all `2^9 = 512` within-block
swaps finds one order with all nine spans ascending and no change to semantic
ownership.

This is map-level legal. H4-M2 must still replay the exact 16-YMM H3 liveness
after exchanging the `h_a/h_b` roles.

## Lane-orientation Pareto frontier

The search evaluates all 384 structured bit-affine lane orders plus an exact
tile-specific serializer-sorted construction. The distinct frontier profiles
are `(terminal routes, pair-order runs, maximum pending coefficients)`:

| M2 representative | routes / 72 vectors | pair-order runs / 36 streams | pending |
| --- | ---: | ---: | ---: |
| Natural-Q identity | 0 | 512 | 16 |
| `bitperm-3210-xor-6` | 72 | 492 | 16 |
| `bitperm-0321-xor-e` | 144 | 376 | 16 |
| tile-specific serializer-sorted | 216 | 36 | 16 |

The tile-specific mapping has an exact three-route existence proof per vector:

```text
vpshufb -> vpermq -> vpshufb
```

For every tile and destination half, four requested words originate in each
source half, so the first shuffle can form qword groups, `vpermq` can deliver
one group from each source half, and the final shuffle can place the words.
Exact masks and 16-YMM scheduling are deferred to M2.

`pair-order runs` measures future byte-compaction regularity. It is not a
cycle estimate and does not alter the zero pair-join lower bound. Therefore
M1 does not select a lane winner: all four distinct profiles advance to M2.

## Shared r-hash implication

Under H4-M0, both the r-hash and ciphertext paths begin their terminal work
from scale-1 vectors and use Barrett plus the same canonical 12-bit encoding.
The four orientation profiles are consequently reusable on the r Forward
terminal. M2 will report that cost beside ciphertext, but it does not force
the two different producers to share one physical ABI.

## Decision

H4-M1 is complete with these hard lower bounds:

```text
R_pair_min = 0 routes
P_max_min  = 16 coefficients
Y_buffer   = 1 YMM
terminal materialization minimum = 0 bytes
```

H4-M2 must jointly lower live Barrett, sign canonicalization, same-lane pair
packing, byte compaction, and exact machine liveness for the four frontier
profiles. No H4 ASM, benchmark, native KEM run, or promotion is authorized.

Reproducible evidence is in
`generated/encap-h4-terminal-presentation-search.json`.
