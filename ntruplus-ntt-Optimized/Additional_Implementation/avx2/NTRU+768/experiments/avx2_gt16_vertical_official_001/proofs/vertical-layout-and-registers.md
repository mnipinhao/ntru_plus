# Vertical layout and register proof

There are 48 independent cyclic NTT16 transforms: four branches, four quartic
degrees, and three GT rows.  V1 partitions them into three full batches by
`k3`; lane `4*branch+degree` is bijective over the remaining 16 transforms.
Butterflies operate between coefficient-position vectors, so the NTT16 body
requires no cross-lane permutation.

The generated execution trace contains exactly 1,884 AVX2 instructions:

| Region | Instructions |
| --- | ---: |
| 48 R2 packs plus explicit preweight | 1,104 |
| 16 optimistic vector DFT3 groups | 176 |
| Three vertical NTT16 arithmetic schedules | 396 |
| Four-vector tile materialization | 208 |

One NTT16 batch has 17 nontrivial and 15 light butterflies.  A nontrivial
butterfly is charged four packed Montgomery instructions plus add/sub; a light
one is charged add/sub.  This is 132 instructions per batch.

The highest-pressure frontend point has three retained positions, three live
DFT inputs, and three temporaries: nine YMM registers.  A four-position NTT tile
uses four data registers and one Montgomery temporary.  The generated allocator
uses only YMM0--YMM8 at peak, leaves YMM9--YMM14 available, reserves YMM15, and
never spills.

The schedule remains optimistic.  The 11-op DFT3 is inherited from Round 4's
floor, constants are assumed to be aligned memory operands, and loop/control,
address setup, and any missing range checkpoint are omitted.  Consequently a
failure after adding the consumer bridge is a valid stop; the producer pass is
not a cycle-performance claim.
