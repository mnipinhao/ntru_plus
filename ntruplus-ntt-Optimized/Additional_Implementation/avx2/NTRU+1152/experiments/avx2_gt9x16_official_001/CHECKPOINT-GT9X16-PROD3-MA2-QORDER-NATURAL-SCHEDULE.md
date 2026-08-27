# GT9X16-PROD3-MA2-QORDER-NATURAL-SCHEDULE

This checkpoint closes the Q-order search by lowering its two remaining
physical ABIs to the same caller-weighted static taxonomy. It emits exact
symbolic route plans but no assembly and runs no benchmark.

## Multiplicity and fixed boundary

Encapsulation executes two GT producers (`r` and `m`), one resident-`h`
projection, and one H1 reconstruction for the `r` hash fanout. The objective is
therefore:

```text
2 * producer(Q) + resident_h(Q) + H1(Q)
```

Every number is labeled `per_forward` or `per_encap`. MA2 arithmetic, scale
four, ranges, lambda identities, inverse-four, sign canonicalization, pack
bits, and 54 byte stores remain unchanged. Natural-Q lambda vectors are only
offline constant-table permutations and add no runtime instruction.

## Exact resident-h correction

The previous map artifact's 144-route resident-`h` field was a simplified
schedule count, not the linked implementation. The current linked MA2 audit is:

```text
data loads       144
vperm2i128       144
vpshufb           72
vpblendw          72
routing total    288
scratch            0
linked peak YMM   14
```

Natural-Q requires two source-half groups for every coefficient plane. Reusing
the same two loaded source vectors, an exact plan uses two
`vperm2i128`/`vpshufb` groups and one `vpor`:

```text
data loads       144
vperm2i128       144
vpshufb          144
vpor              72
routing total    360
scratch            0
peak upper bound  15
```

All 72 plans symbolically replay the exact semantic-q owners. Thus the true
resident-`h` delta is `+72 routes`, not `+16 instructions` and not extra data
loads.

## Exact H1 lowering

Natural-Q reconstructs the same 72 pinned Official pack vectors. The generated
word masks replay exactly, and the only changes are the expected coefficient
construction counts:

| H1 component | current-Q | natural-Q | delta |
| --- | ---: | ---: | ---: |
| data loads | 272 | 288 | +16 |
| coefficient routes | 336 | 360 | +24 |
| pack-transpose routes | 324 | 324 | 0 |
| intermediate stores/reloads | 0/0 | 0/0 | 0/0 |
| peak YMM | 16 | 16 | 0 |

No serializer, normalization, or packing redesign is introduced.

## Caller-weighted arbitration

| Cost | current-Q | natural-Q | natural-current |
| --- | ---: | ---: | ---: |
| producer routes per forward | 144 | 0 | -144 |
| producer routes per Encap | 288 | 0 | -288 |
| resident-h routes per Encap | 288 | 360 | +72 |
| H1 coefficient routes per Encap | 336 | 360 | +24 |
| H1 pack routes per Encap | 324 | 324 | 0 |
| resident-h + H1 data loads | 416 | 432 | +16 |

The final separated delta is:

```text
caller-weighted routing:  -192
caller-weighted loads:     +16
scratch/spill:               0
peak-YMM upper bound:       15 for MA2, 16 for H1
```

This is not converted to cycles and the 16 loads are not assigned the same
weight as 192 routes. It is nevertheless a clear machine-realization credit:
the two producer epilogues pay for the exact resident-`h` and H1 debts with
substantial margin and no new materialization boundary.

## H2 and decision

H2-v1 is formally rejected because its pair-locality model did not follow the
pinned physical-to-serialized ownership permutation. Its old 256-pair,
72-load-lower-bound, and 1086-route figures are excluded from this and all
future Q-order decisions. A future multi-vector serializer would be a new H2,
not a continuation of H2-v1.

The Q-order search is now closed. Natural-Q is selected for the next namespaced
machine realization; current-Q remains the control. The next checkpoint may
implement only the already scheduled lane ABI, resident-`h` projection, H1
masks, and offline lambda reindexing. It must first pass raw plane/H1 byte
differentials and a linked instruction/ABI audit. Benchmarking and native KEM
remain unauthorized until those gates pass.
