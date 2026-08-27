# H4-M2C Natural-Q exact wire egress schedule

## Outcome

M2C lowers the frozen 2304-byte canonical Natural-Q scale-1 scratch to exact
1728-byte ciphertext order.  Every ownership decision is keyed by serialized
`wire_coefficient`; Official physical coefficient IDs are not used for pair
formation.

The schedule covers:

```text
18 tiles
576 wire pairs
1152 canonical coefficients
1728 output bytes
13824 output bits
```

All pairs, bytes, and byte-bit owners replay exactly against M2B.

## Pair32 formation

Each tile reads its four canonical terminal vectors.  Planes 0/1 and 2/3 are
the two low/high wire-endpoint pairs.  All 16 endpoints occupy identical lanes
in adjacent vectors, so each endpoint pair uses:

```text
vpunpcklwd low,high
vpunpckhwd low,high
vpmaddwd [1,4096]
vpmaddwd [1,4096]
```

For canonical `0 <= low,high <= 3456`:

```text
pair32 = low + (high << 12)
0 <= pair32 <= 14159232 < 2^24 < 2^31
```

The low three little-endian bytes are exactly the NTRU+ 12-bit pair encoding.
No pre-pair routing is required.

## Per-tile lowering

The four pair32 vectors are independently sorted with exact generated
`vpermd` indices.  Even/odd parity companions are then joined using two
`vpunpck*dq` and two `vperm2i128` instructions per companion pair.  This yields
four YMM vectors containing 32 consecutive wire pairs.

Two fixed 48-byte compaction networks convert those four vectors into six XMM
chunks.  Three `vinserti128` operations form the three exact 32-byte stores:

```text
A0 | A1
A2 | B0
B1 | B2
```

Tiles are executed in wire order, with store offsets:

```text
0,32,64
96,128,160
...
1632,1664,1696
```

The ciphertext stores remain unaligned because the public output pointer has
no strengthened alignment contract.

## Exact ledger

Scratch-to-wire:

| class | instructions |
| --- | ---: |
| canonical scratch loads | 72 |
| pair unpack + `vpmaddwd` | 144 |
| `vpermd` index loads | 26 |
| pair32 `vpermd` sorting | 72 |
| parity interleave | 144 |
| 24-bit compaction | 486 |
| ciphertext stores | 54 |
| **total** | **998** |

Including the already validated terminal:

| class | instructions |
| --- | ---: |
| Barrett | 216 |
| sign canonicalization | 216 |
| canonical scratch stores | 72 |
| scratch-to-wire | 998 |
| **terminal-to-wire total** | **1502** |

This independently reconciles the historical M2 symbolic count.  It does not
turn that count into machine evidence; only the next linked ASM can do that.

## Register and ABI plan

The per-tile streaming allocation has an abstract peak of ten YMM registers:

1. form four pair32 vectors;
2. sort them in place with one reusable index register;
3. form four wire-group vectors;
4. pack the first two and store the first 32 bytes, retaining only `A2`;
5. pack the second two and store the final 64 bytes.

Expected frame and spill are zero.  This remains a schedule proof rather than
a linked def/use proof; the ASM gate must replay actual machine liveness.

## Decision

The exact schedule is complete and authorizes one namespaced H4-M3B ASM
prototype.  Benchmarking remains unauthorized.

The ASM must change only the current H1 correctness-control egress:

```text
keep scale-1 producer
keep H3 decode/MA2
keep terminal Barrett/sign canonicalization
keep 2304-byte scratch and alias behavior
replace H1 fallback with exact M2C scratch-to-wire schedule
```

It must first pass exact bytes, linked instruction attribution, liveness,
alignment, spill/frame, overlap, sanitizer, and full repository checks.
