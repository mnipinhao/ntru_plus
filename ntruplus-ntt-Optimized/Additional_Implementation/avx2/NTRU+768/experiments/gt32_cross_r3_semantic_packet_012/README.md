# GT32-CROSS-R3-SEMANTIC-PACKET-012

012 is the first executable-architecture screen selected by the AVX2 packing
superspace census.  It tests a Level-2 representation: low/high 128-bit halves
are independently typed semantic objects rather than two halves of the same
bit permutation.

GT Clean is not modified.  BaseMul is deliberately outside this first gate.

## Candidate

For the two Top objects `A/B` and each R3 row, the proposed packets are:

```text
ProwL = [ Arow.low128  | Brow.low128  ]
ProwH = [ Arow.high128 | Brow.high128 ]
```

Memory is iteration/packet-major:

```text
iteration 0: P0L P0H P1L P1H P2L P2H
iteration 1: P0L P0H P1L P1H P2L P2H
...
```

The intended advantage was not information compression.  It was to turn
`vperm2i128` into a whole-object exchange and remove an existing R3 routing
class.

## Exact production audit

The selected Forward executes two `GT_BLEND3` macros in each of eight
iterations.  Each macro contains six `vpblendd`:

```text
Forward: 2 * 8 * 6 = 96 vpblendd
```

The selected inverse tail executes two `BLEND3_OUT` macros in each of eight
groups:

```text
Inverse: 2 * 8 * 6 = 96 vpblendd
```

Therefore the current `2F+I` R3 routing class is exactly 288 `vpblendd`.

## Producer synthesis

`GT_BLEND3` is qword-granular.  For source rows `x/y/z`, its outputs own
qwords as follows:

```text
r0 = [x0,y1,z2,x3]
r1 = [z0,x1,y2,z3]
r2 = [y0,z1,x2,y3]
```

The generator symbolically verifies two natural two-layer forms.

Route first:

```text
12 vpblendd
+ 6 vperm2i128 to pair A/B halves
= 18 routing instructions / iteration
```

Pair A/B source halves first:

```text
6 vperm2i128
+ 6 qword mixes (vpblendd or vshufps)
= 12 routing instructions / iteration
```

The latter is exact and reconstructs all six target packets, but it only
changes the instruction family:

```text
current:   12 vpblendd
candidate: 6 vperm2i128 + 6 qword mixes
```

No operation class disappears.  The generated artifact does not claim a
global minimum across arbitrary deeper networks; it exactly covers the two
natural normal forms required by this packet contract.

## Complete R2 consumer blocker

The packet does not compress a pair of branch states:

```text
L stream: 8 YMM
H stream: 8 YMM
```

Running the streams independently omits the NTT32 butterfly bit formerly
represented by the original low/high-half selector.  The exact connectivity
check reaches only 16 of 32 leaves without that bit; all five R2 bits are
needed for a complete 32-point transform.

This is checked against `generated/gt32_3x32_mapping.json`, not inferred from
capacity alone.  TILE4 uses `qword = physical_Q mod 4`; since a qword contains
all four quartic degrees, the 128-bit-half selector is physical `Q bit 1`.
Separating L/H therefore removes a real NTT32 leaf bit.

At the required L/H join:

```text
16 data YMM + q + one Montgomery temporary = 18 YMM
```

AVX2 has only 16.  Therefore this persistent half ownership requires an
additional materialization cut, source replay, or a different ownership
evolution.  It cannot be a spill-free complete R2 consumer in the proposed
form.

## Inverse join

The symmetric exact construction first forms six routed cross packets, then
uses six `vperm2i128` to recover the `A/B` outputs:

```text
6 qword mixes + 6 vperm2i128 = 12 instructions / group
```

Current `BLEND3_OUT` is also 12 `vpblendd` for the two Top objects.  Again no
routing class is deleted.

## Memory

Packet-major order improves address regularity but not the information
volume:

```text
per Forward boundary: 48 stores + 48 loads = 3072 bytes
per inverse boundary: 48 stores + 48 loads = 3072 bytes
2F+I floor:           288 memory operations = 9216 bytes
```

This is allowed by the gate.  The failure is not “memory was not eliminated”;
it is that routing remains 288 instructions before charging the mandatory R2
join debt.

## Decision

```text
cross-R3 128-bit-half packet P0: static hard stop
assembly:                           not emitted
GT Clean:                           unchanged
```

Closed scope:

```text
i16 coefficient basis
ProwL=[A.low|B.low]
ProwH=[A.high|B.high]
persistent Top-A/Top-B half ownership
```

Not closed:

- qword-semantic R3 packets;
- half ownership that evolves and deletes the missing-bit join;
- BaseMul-selected pair packets;
- streamed evaluation packets.

The next gate is `GT32-CROSS-R3-QWORD-SEMANTIC-PACKET-013`, because the actual
runtime R3 route is qword-granular.  It should ask whether a qword is the
semantic R3 object, making `GT_BLEND3` part of the packet definition rather
than a runtime permutation.

## Reproduction

```sh
make check
```

Primary artifact:

- `generated/cross_r3_semantic_packet_gate.json`
