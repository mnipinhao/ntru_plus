# M3 — GT transform-domain tile ABI search

## Bounded question

Which pure-permutation grouping of `(top,row,column)` leaves lets a future
GT NTT9 producer store the existing eight-leaf SoA BaseMul ABI with the least
structural routing burden?

This experiment compares ABI families only.  It does not implement or time an
NTT16-to-NTT9 serializer, does not carry a nontrivial phase, and does not change
Production.

## Common output invariant

Every legal candidate contains 36 tiles.  Tile `g` stores:

```text
j0[leaf(g,0)..leaf(g,7)]
j1[leaf(g,0)..leaf(g,7)]
j2[leaf(g,0)..leaf(g,7)]
```

The leaf order may change, but all three components, both operands, the
BaseMul zeta vector, BaseMulAdd, and the inverse map must use the same order.

## Candidate A — fixed-row column batches

```text
register/output = row
lane            = one of eight columns
```

Eight columns run through one NTT9 in SIMD parallel.  Nine input registers
`S_0..S_8` produce nine output registers, and each output register is already
one BaseMul tile component.  `P9` may reorder output registers and `P16` may
reorder lanes without changing this property.

This is the primary retained family.  Natural and paper-oriented/bit-reversed
examples are machine-checked, but they are one ABI family rather than two
different arithmetic algorithms.

## Candidate B — fixed-column row lanes

```text
register = column
lane     = row 0..7
tail     = row 8
```

It avoids the main-data transpose after NTT16, but it turns NTT9 into a
cross-lane transform, processes one column per vector transform, and must
repack sixteen row-8 results into two BaseMul tiles per top branch.  These are
real costs, but M3 does not know whether they exceed the fixed-row serializer.
The family is retained as a secondary candidate until a bounded within-lane
NTT9-plus-tail microkernel is compared with the fixed-row bridge and
across-register NTT9.

## Candidate C — lane-dependent row rotation

For each column choose a public `a_c` and represent its ninth-root preimage as:

```text
lambda'_c = lambda_c * eta^a_c
```

Then one physical output register may contain different logical rows in its
eight lanes while retaining the same across-register NTT9 structure.  This is
not an arbitrary shuffle: it is the exact row relabeling

```text
physical row p, lane c -> logical row (p+a_c) mod 9, column c.
```

No output shuffle is required, and BaseMul only needs the matching zeta lane.
The family is retained conditionally because choosing useful `a_c` depends on
the later column-specific twist/table cost study.  M3 makes no phase-carry
claim: changing the representative only relabels roots.

## Rejected mixed column stream

Flattening nine oriented rows for one column and chunking the stream by eight
causes every column boundary to cross a BaseMul tile boundary.  It loses the
stable eight-column SIMD batch and requires cross-output tile assembly, so it
is rejected before serializer work.

## Decision

Carry three ABI families into the next stage:

1. fixed-row, eight-column batches with arbitrary public `P9` and `P16`;
2. the same physical batching plus optional lane-dependent row rotations.
3. fixed-column row lanes as a secondary no-main-transpose alternative.

Candidate B/C memory bridge work should target the first family initially, but
the fixed-column family is not rejected until its cross-lane NTT9 and tail cost
is measured.  The rotation extension stays a table-generation option until
twist costs are known.  Only column-stream chunking is rejected by M3.
