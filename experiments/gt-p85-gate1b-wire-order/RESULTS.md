# P85 — gate 1b: what a wire-order transform contract would cost and buy

Roadmap item 1 says the Good-Thomas permutation should move out of the
serializer and into the addressing of the transform that feeds it, the way
NTRU+768's decapsulation does it.  Gate 1b is the measurement that decides
whether the cost moves or doubles.  It does move.  It is still not the next
thing to do.

## The permutation, extracted rather than assumed

Feeding a polynomial whose value equals its index through each tree's packer and
decoding the 12-bit fields gives the GT-slot-to-wire map exactly.  It is **not**
an 8x8 transpose, which is what an earlier reading of the first sixteen slots
suggested.  It is an 8xL transpose where L is the leaf degree:

| set | unit | result | store width |
|---|---|---|---|
| 864 | 3 vectors | 8 runs of **3** consecutive wire positions | 6 bytes |
| 1152 | 4 vectors | 8 runs of **4** consecutive wire positions | 8 bytes, one `str d` |

864's degree-3 leaves are 4.5 wire bytes and never align, which is why its
`pack_small.S` needs 772 permutation instructions out of 1029.  1152's degree-4
leaves land on a `str d` every time, so **1152 is the structurally easier
target, not 864** -- the opposite of what the roadmap assumed.

1152's `pack.c` already exploits a stronger form of this: pairing groups `g` and
`g+9` gives eight *natural* coefficients per transposed lane, which is exactly
twelve wire bytes, so its 144 blocks tile the output with no overlap.

## What the transform would pay

`gate1b.c` gives both kernels the same four vectors per 32-coefficient group,
produced by a dependent chain, and differs only in how they reach memory:
four contiguous 128-bit stores, which is what `ntt9.S` does now, against an 8x4
transpose and eight 64-bit stores at the wire run-starts.

```
  A contiguous str q                33.3 ns   (33.6 on a repeat)
  B transpose + scattered 64-bit    68.1 ns   (65.7)
  cost to the transform            +34.8 ns   (+32.1)
```

Call it **+33 ns per forward pass over 1152 coefficients**.

## What the serializers would give back

If the NTT-domain layout *is* wire order, both ends become Official's shape.
Decapsulation, from the P84 profiles:

| | GT | Official | |
|---|---:|---:|---|
| pack, 2 calls | 259 | 150 | **-109** |
| unpack, 3 calls | 233 | 154 | **-79** |

Decapsulation runs two forward transforms and one inverse, so the transform side
pays about +99 against -188 saved: **roughly -89 ns, about 1.6% of the
operation.**  Real, and the largest single lever identified so far.

## Why it is still not next

**The final stage does not hold the right vectors together.**  `ntt9.S` leaves
its live values 64 slots apart -- 600-607, 664-671, 728-735 and so on.  The
transpose needs four *consecutive* vectors, and the stronger pairing needs
groups 288 slots apart.  Neither is co-resident, so this is not a change to
store addressing; it is a change to which values the bank schedule computes
together.

**The file is generated and the generator is gone.**  `ntt9.S` says "Generated
by generate_ntt9.py; do not edit", 872 lines of Slothy-scheduled assembly, and
`generate_ntt9.py` is not anywhere on this machine.

So the item is a restructuring of the transform's bank schedule, by hand, in
scheduled assembly, for 1.6%.

## What to do instead, first

1152's packer and unpacker are C intrinsics -- it has no `pack*.S` at all, which
is roadmap item 3.  That is where +109 and +79 currently sit, and writing them in
assembly in the *existing* layout is mechanical and low-risk.  864's
`pack_small.S`, `pack_full.S` and `pack_compare.S` are the model, and 1152's
degree-4 leaves make the job easier than the one 864 already solved.  A quarter
off those two numbers is -47 ns for a fraction of the risk.

**Item 3 moves ahead of item 1.**  Revisit item 1 afterwards, with the packer
cost known rather than assumed, and only if the bank schedule can be regenerated
rather than hand-edited.
