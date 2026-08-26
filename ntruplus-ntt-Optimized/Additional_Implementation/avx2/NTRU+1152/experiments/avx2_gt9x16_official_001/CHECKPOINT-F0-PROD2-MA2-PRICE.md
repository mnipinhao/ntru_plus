# Checkpoint F0-PROD2-MA2-PRICE

## Outcome

Consumer-native final materialization is validated at the exact 2,304-byte
MA2 coefficient-plane boundary. The serious SUPERCOP-derived comparison uses
one pinned P-core, the same SUPERCOP-selected O3 measure ELF, balanced order,
9 fresh processes, and 96 observations per named operation per launch. It
does not execute MA2 arithmetic and is not a native KEM result.

The timed paths are exactly:

```text
control:   coefficient -> P1-H generic F0 -> generic-to-MA2 projection
candidate: coefficient -> P2-B direct MA2 planes
boundary:  identical materialized MA2 plane buffer
```

Inputs and all scratch/output banks are aligned and resident before timing.
Input regeneration remains outside the timed intervals.

## Serious result

| region | control StQ2 | P2-B StQ2 | pooled delta |
| --- | ---: | ---: | ---: |
| one producer | 1834.2431 | 1814.4352 | -19.8079 |
| two producers back-to-back | 3499.8194 | 3385.0718 | -114.7477 |

The paired per-launch median deltas are `-20.0000` cycles for 1X and
`-115.1458` cycles for 2X. P2-B wins 9/9 launches in both comparisons. The 2X
headline is measured directly and includes consecutive `r`/`m` producer
geometry; it is not inferred by doubling the 1X result.

## Full linked movement attribution

The control projection intentionally reproduces the current generic MA2 input
geometry: each coefficient plane independently reloads its two generic-F0
source vectors. A linked object audit counts the whole producer plus
projection boundary.

| P2-B minus control | per operand | two operands |
| --- | ---: | ---: |
| aligned vector loads | -144 | -288 |
| aligned vector stores | -72 | -144 |
| `vperm2i128` | 0 | 0 |
| projection call / return | -1 / -1 | -2 / -2 |

P2-B adds 72 producer-local `vperm2i128` operations per forward, exactly
replacing the projection's 72 operations. Cross-lane work is relocated rather
than removed. At this materialized stop boundary, the durable movement credit
is removal of 144 reloads and 72 extra plane stores per operand. This is why
the result must not be described using only the prior consumer-side
`-144 vmovdqa -144 vperm2i128` ledger.

The projection is a 32-byte-aligned, frame-free AVX2 leaf with exactly 144
aligned loads, 72 `vperm2i128`, and 72 aligned stores. It contains no spills,
calls, branches, or `vzeroupper`. All benchmark wrapper and producer symbols
are also linked at 32-byte-aligned addresses.

## Decision

The machine-level hypothesis is accepted:

```text
F0 semantic transform may remain common,
but its final physical materialization should be MA2-consumer-native.
```

The next authorized checkpoint is a consumer-island comparison that appends
the unchanged MA2 arithmetic and serializer to both paths. It must retain the
same two-producer input residency and exact ciphertext differential. Native
encapsulation, KEM promotion, D1 output-orientation search, top-split fusion,
P2-C traversal, and plane-formation micro-optimization remain blocked until
that consumer-island result is reviewed.
