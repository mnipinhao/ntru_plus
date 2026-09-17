# P1-SHRUNK: NTRU+864 d3 packet arbitration and NTRU+1152 stage-order gate

## Decision

The shrunk P1 stops before assembly and timing. This is the intended high-risk
representation gate, not an incomplete benchmark campaign:

- NTRU+864 plane-major NTT9 is not authorized as a linked challenger. With
  the existing materialized top-split input and a coefficient-plane consumer,
  it moves the exact same packed-to-plane bijection from after NTT9 to before
  NTT9. It removes no load, store, permutation, multiplication, or reduction.
- The one NTRU+1152 NTT16-first/blocked challenger is not authorized yet. It
  has no exact <=16-YMM full-branch schedule that removes the NTT9/NTT16
  materialization. The closest existing exact early-plane network costs 792
  routes versus the selected C1's 576, a +216-route warning rather than proof
  that every NTT16-first realization must lose.
- P2 is not opened. NTRU+768 remains frozen.

No paired benchmark is run because P1 explicitly permits a linked kernel only
after structural credit exists. Timing two semantically identical schedules
that differ only in where the same unlowered permutation is placed would add a
new prototype without answering the research question.

## NTRU+864 exact packet map

For each top-split branch and logical GT row, the backing contains 48 words in
q-major, j-minor order:

```text
(q0,j0), (q0,j1), (q0,j2), (q1,j0), ... , (q15,j2)
```

This is exactly three YMM registers. There are no unused lanes. The apparent
problem with `d=3` is therefore ownership across the three vectors, not vector
capacity.

The packed control consumes those three vectors directly in NTT9. Its radix-3
row constants are lane-uniform. The plane-major challenger first permutes them
to:

```text
P0 = (q0,j0) ... (q15,j0)
P1 = (q0,j1) ... (q15,j1)
P2 = (q0,j2) ... (q15,j2)
```

and runs the same NTT9. Because the permutation changes only `(q,j)` and the
NTT9 changes only the row coordinate, they commute. The exhaustive generated
map covers all 864 physical cells and 7,776 input-row/output-row linear terms.
Both paths still need one three-vector packed-to-plane permutation per
`branch x row`, i.e. 18 semantic packet permutations per full transform.

| Full-transform structural item | packed control | plane-major challenger | delta |
|---|---:|---:|---:|
| top-split vector loads | 54 | 54 | 0 |
| semantic 3-vector packet permutations | 18 | 18 | 0 |
| NTT9 vector streams | 54 | 54 | 0 |
| final coefficient-plane stores | 54 | 54 | 0 |
| removed materialization | 0 | 0 | 0 |

The table deliberately does not invent an AVX2 instruction count for the
three-vector deinterleave. The decision does not depend on that count because
the same exact bijection occurs once on both sides.

Generated evidence:

```text
generated/p1-d3-packet-map.json
```

The artifact records every source word, packed vector/lane/half, destination
plane vector/lane, the pinned NTT/pack source hashes, and the shared-model hash.

## NTRU+1152 single challenger

The selected current path has the following exact generated ledger:

```text
NTT9-first persistent AoS C1
  data loads after top split   144
  data stores after top split  144
  routing                      576
  NTT9 -> NTT16 boundary        72 stores + 72 reloads
```

The only permitted challenger is coefficient-plane NTT16-first with blocked
row accumulation. Its only credible source of credit is eliminating some or
all of that boundary. It must, however, form four q-lane planes from each
`4q x 4j` input tile and retain enough row results for NTT9 without spilling,
recomputing the other planes, or materializing an equivalent boundary.

No such exact def/use schedule exists in the current evidence. The existing
fully specified early-plane C2 network is useful as a warning/control:

```text
C1 late live D1 -> transpose  576 routes
C2 early plane orientation    792 routes
delta                         +216 routes
```

This does not mathematically reject NTT16-first. It means assembly is allowed
only after a concrete full-branch schedule records the boundary it deletes,
peak live YMM <=16, constant operands, and every added route/load/store.

Generated evidence:

```text
NTRU+1152/experiments/avx2_gt9x16_official_001/generated/p1-ntt16-first-gate.json
```

## Reopen conditions

NTRU+864 plane-major may reopen only if an adjacent producer or consumer gives
the moved permutation a machine purpose, for example:

- top split deposits coefficient planes directly without an added pass;
- NTT16 consumes a live plane and deletes a store/reload boundary; or
- cubic BaseMul consumes packed NTT9 output directly, making the terminal
  plane conversion unnecessary.

NTRU+1152 NTT16-first may reopen only with an exact full-branch liveness and
movement schedule showing a net boundary deletion after entry formation.
Neither condition automatically opens P2.

## Reproduction

```sh
make p1-map
make p1-map-check
```

