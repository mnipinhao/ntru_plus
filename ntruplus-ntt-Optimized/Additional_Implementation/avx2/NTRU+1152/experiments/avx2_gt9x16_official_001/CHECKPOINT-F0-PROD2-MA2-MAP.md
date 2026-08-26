# Checkpoint F0-PROD2-MA2-MAP

## Outcome

This checkpoint maps every final F0-PROD1 D1 lane directly to the actual MA2
coefficient-plane consumer contract. It does not implement assembly or change
the top split, R2/D1 arithmetic, resident `h`, MA2 arithmetic, serializer, or
KEM caller.

The intended boundary remains materialized:

```text
coefficient domain
-> unchanged 2,304-byte top split
-> unchanged formation / R2 / D1
-> materialized MA2-native coefficient planes
-> MA2
```

There is no live-register D1-to-MA2 fusion objective.

## Exact ownership map

For every D1 lane, the generated oracle records:

```text
(branch, physical-p row, p, terminal pair, stream, packed lane)
-> (serializer chunk, tile A/B, coefficient plane, physical-q lane)
```

The proof closes all required sets:

| set | cardinality |
| --- | ---: |
| D1 source cells | 1,152 |
| MA2-native destination cells | 1,152 |
| semantic `(branch,p,q,coefficient)` owners | 1,152 |
| coefficient-plane vectors | 72 |
| semantic tiles | 18 |
| serializer chunks | 9 |

Each destination vector contains one fixed terminal coefficient in the exact
MA2 lane order `0,2,...,14,1,3,...,15`. Values are only permuted, so scale four,
Montgomery exponent zero, and the exact `[-20751,20753]` signed-i16 envelope
are unchanged. The existing MA2 preoperation range proof applies without an
extra reduction.

## Realization search

### P2-A: store-address-only redeposit

P2-A is impossible under the frozen D1 output geometry. Every D1 vector holds
two coefficient halves: eight q leaves from each of two terminal coefficients.
Every MA2 vector instead needs all sixteen q leaves for one coefficient. The
exhaustive owner-set comparison finds zero whole D1 vectors that equal one MA2
plane, so changing only store addresses cannot realize the consumer ABI.

### P2-B: local D1 epilogue

P2-B is exact and selected. For each tile and terminal pair, the two D1 output
vectors are both live. One `vperm2i128 0x20` forms the lower-coefficient plane
and one `vperm2i128 0x31` forms the upper-coefficient plane. This costs:

| item | per forward operand |
| --- | ---: |
| local `vperm2i128` | 72 |
| aligned MA2-native stores | 72 |
| extra temporary storage | 0 bytes |

The two generic stream slots of a terminal pair and its two destination
coefficient-plane slots have the same slot set. After both source registers are
live, P2-B can overwrite those slots in place. The existing 2,304-byte output
backing can therefore serve first as R2 transient storage and finally as
MA2-native materialization.

### P2-C: serializer-chunk traversal

Chunk-oriented traversal is algebraically feasible but removes no additional
movement relative to P2-B. It would change the heavily validated producer
schedule only to reorder when tiles are produced, so it is deferred.

## Movement accounting

The actual complete MA2 assembly reloads each pair of generic F0 vectors once
for each coefficient plane. Consequently it executes 144 generic-F0 aligned
loads and 72 plane-forming `vperm2i128` instructions per forward operand.

| boundary operation | P1-H -> current MA2 | PROD2 P2-B -> native MA2 | delta |
| --- | ---: | ---: | ---: |
| top-split loads | 144 | 144 | 0 |
| formation cross-lane operations | 576 | 576 | 0 |
| D1/native-plane stores | 72 | 72 | 0 |
| generic-F0 loads in MA2 | 144 | 0 | -144 |
| consumer F0-to-plane permutations | 72 | 0 | -72 |
| producer-local plane permutations | 0 | 72 | +72 |
| MA2-native plane reloads | 0 | 72 | +72 |

Thus P2-B removes 72 dynamic vector instructions per forward operand, all from
duplicated loads. Across the two encapsulation forward operands the static
credit is 144 loads. The 72 plane permutations are relocated from MA2 to the
D1 epilogue rather than eliminated.

This is a bounded movement credit, not a cycle claim and not evidence that it
can overcome the existing encapsulation deficit.

## Decision

`F0-PROD2-MA2-ASM0` is authorized only for the selected P2-B materialized
realization. It must preserve the current top-split and arithmetic DAG, add no
temporary buffer, and prove byte-exact producer/consumer behavior plus linked
load/store/permutation attribution before timing.

KEM benchmarking, resident-`h` changes, top-split fusion, live D1-to-MA2
handoff, and P2-C traversal changes remain unauthorized.
