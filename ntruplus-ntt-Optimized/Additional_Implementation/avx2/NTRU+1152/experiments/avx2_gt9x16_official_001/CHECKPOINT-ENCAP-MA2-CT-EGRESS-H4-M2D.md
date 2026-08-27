# H4-M2D exact physical-wire ownership and staging rerank

## Corrected semantic key

M2D fixes the serializer ownership key to the invariant implemented by
Official `poly_tobytes`/`poly_frombytes`:

```text
wire coefficient k = Official physical coefficient k, 0 <= k < 1152
```

The legacy `serialized_coefficient` field is not used in the semantic layer.
Replaying the old M2B artifact against this invariant finds 1134 mismatches in
1152 cells.  Consequently, all M1/M2/M2B/M2C conclusions derived from the old
cross-vector ownership model are rejected.  Scale-1, H3, terminal Barrett and
sign canonicalization, canonical coefficient semantics, and the alias/liveness
boundary remain valid.

## Exact vector ownership

All 576 true 12-bit wire pairs are local to one YMM:

```text
same-YMM pairs       576
cross-YMM pairs        0
adjacent lanes       320
non-adjacent lanes   256
```

The 72 vectors split by adjacent-pair count as follows:

| adjacent pairs in one vector | vectors |
| ---: | ---: |
| 0 | 8 |
| 2 | 16 |
| 4 | 16 |
| 6 | 16 |
| 8 | 16 |

An exact constructive lowering exists for every vector.  Eight vectors need
only `vpshufb`; eight add a pair32 `vpermd`; the remaining 56 use `vpermq`,
`vpshufb`, and pair32 `vpermd`.  Every vector then applies one
`vpmaddwd [1,4096]`.  The resulting structural ledger is:

```text
pair-orientation routes  192
pair Montgomery-free madd 72
```

This is not yet linked machine evidence.

## Reopened staging families

The corrected abstract instruction ledger is:

| family | terminal representation | total |
| --- | --- | ---: |
| S2-prime | canonical i16 scratch | 1452 |
| S1-prime | pair32 scratch | 1452 |
| S0-prime | packed24 scratch | **1236** |

S1-prime and S2-prime tie because the same vector-local orientation and
pair32 work merely moves across the scratch boundary.

S0-prime is 216 instructions lower in the exact abstract lowering.  Each
terminal vector becomes two independent four-pair/12-byte chunks:

```text
canonical vector
-> optional vpermq
-> vpshufb
-> vpmaddwd [1,4096]
-> optional pair32 vpermd
-> vpshufb pack24
-> low 12-byte store + high 12-byte store
```

The exact 12-byte store lowering is one `vmovq` plus one memory `vpextrd` per
half.  Across 72 vectors this is 288 stores plus 72 upper-half extracts.  It
uses the existing 2304-byte scratch allocation but only the first 1728 bytes.
After the final PK load, an alias-safe 54-load/54-store YMM copy emits the
ciphertext.

## Eight-vector / 192-byte block schedule

The ownership partitions exactly into nine identical-size blocks:

```text
8 terminal vectors
= 128 wire coefficients
= 64 pair32 values
= 16 exact 12-byte chunks
= 192 packed bytes
= 6 final YMM copies
```

Every generated block covers one non-overlapping 192-byte ciphertext interval;
the nine blocks cover all 1728 bytes.  The pair32 alternative also records the
eight `vperm2i128` half joins required to form eight consecutive pair vectors
per block.

## Permanent pair32 gate

For all 576 pairs, future schedules must independently replay:

```text
pair32[i] = c[2*i] + (c[2*i+1] << 12)
```

Expected `c[k]` is indexed directly by Official physical coefficient `k`, not
through any serializer mapping field.

## Decision

S0-prime packed24 is the new abstract winner, but ASM is not authorized yet.
The next checkpoint must replay the exact 12-byte stores against linked H3
def/use at every terminal hook and build one executable eight-vector/192-byte
block schedule.  No benchmark is authorized.

