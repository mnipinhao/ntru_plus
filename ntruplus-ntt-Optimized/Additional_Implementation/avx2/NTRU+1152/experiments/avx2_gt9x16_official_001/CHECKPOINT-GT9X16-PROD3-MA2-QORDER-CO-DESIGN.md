# GT9X16-PROD3-MA2-QORDER-CO-DESIGN

This checkpoint changes no arithmetic and produces no assembly. It asks only
whether a structured reassignment of the sixteen GT16 leaves to coefficient-
plane lanes can reduce movement across the complete PROD3 Encap fanout.

## Exact contracts

The immutable semantic owner remains
`(branch,p,q,terminal_coefficient)`. A candidate is recorded explicitly as
`lane_to_semantic_q[16]`; the corresponding lambda follows the same leaf.
Transform scale four, the GT leaf identity, MA2 formulas, inverse-four,
canonicalization, and final Official bytes do not change.

Two orders that were previously easy to conflate are now separate:

```text
C1 natural lane -> semantic q:
  0 8 4 12 2 10 6 14 1 9 5 13 3 11 7 15

frozen MA2 lane -> semantic q:
  0 4 2 6 1 5 3 7 8 12 10 14 9 13 11 15
```

The first is the live C1 transpose output before the final four `vpshufb` and
four `vpermq` per tile. The second is the exact materialized MA2 ABI consumed
by the current caller.

## Search and cost certainty

The first structured family contains every permutation of the four q-index
bits and every XOR orientation: `4! * 16 = 384` unique orders. This includes
natural Q, current packed Q, bit flips, half/quarter swaps, and the D1 output
orientations expressible by this affine family. No `16!` search was run.

The metrics intentionally remain separate:

- PROD3 routes are exact for identity, one-instruction, and proved
  `vpshufb`/`vpermq` two-instruction networks. More general candidates retain
  a conservative constructed upper bound.
- Resident-`h` reports exact source-half ownership groups. Candidate route and
  load counts are generic construction bounds, not claims about an optimized
  shared-load schedule. The linked current hand schedule is independently
  calibrated at 288 routes: 144 `vperm2i128`, 72 `vpshufb`, and 72 `vpblendw`.
- H1 reconstructs the exact pinned Official pack inputs, so its coefficient
  loads/routes are exact. The subsequent 324 pack-transpose routes are
  invariant under Q-order.
- H2 reports exact serialized-pair and 96-byte-block locality only. The old
  `256` cross-half and `1086` route figures came from the invalidated physical-
  equals-serialized model and are not reused.

## Result

The 33 nondominated permutations collapse to only two distinct cost profiles:

| Profile | Count | PROD3 routes | h source-half groups | H1 routes | H1 loads | H2 cross-vector pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| current-like orientations | 32 | 144 | 128 | 336 | 272 | 576 |
| C1 natural Q | 1 | 0 | 144 | 360 | 288 | 576 |

Current frozen Q is therefore Pareto-optimal inside the structured family. No
candidate simultaneously reduces producer, resident-`h`, and H1 ownership
cost. Natural Q is the only qualitatively different frontier point:

```text
producer:                 -144 exact routes
resident h:               +16 source-half groups
H1 coefficient reorder:   +24 exact routes
H1 coefficient loads:     +16 exact loads
H1 pack transpose:           0 change
H2 cross-vector pairs:       0 change (still 576/576)
```

These quantities must not be summed into cycles or even one instruction score:
the resident-`h` number is an ownership metric and its existing assembly shares
loads/routes in a way the generic construction does not price exactly.

## Decision

The checkpoint succeeds without selecting a new ABI. Current Q remains the
research baseline and is structurally Pareto-optimal in the searched family.
Natural Q remains one narrowly scoped schedule candidate because its 144-route
producer credit is exact, but it is not authorized for assembly or timing.

The next admissible step is map/schedule-only: lower the natural-Q resident-`h`
projection and H1 reconstruction far enough to replace ownership bounds with
exact instruction ledgers. If those ledgers cannot beat or plausibly offset the
current route geometry, freeze current Q and move to T0, corrected H2 redesign,
or a genuinely dual-output producer. Native KEM remains unauthorized.
