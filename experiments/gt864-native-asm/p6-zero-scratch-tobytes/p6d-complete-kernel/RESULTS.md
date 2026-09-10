# P6-D complete-kernel gate

## Outcome

P6-D is **active**, not yet eligible for production.  Its first two hard
subgates pass:

- **P6-D1 saved-pair producer:** both symbolic regions allocate `OPTIMAL`
  with spills disabled.  Pair 0 is 407 semantic instructions with vector
  peak 25 and 27 data GPRs; pair 1 is 475 instructions with vector peak 27
  and all 28 available data GPRs.
- **P6-D2 all-row layout:** the exact 13-Q plus 28-GPR state reconstructs all
  nine rows in physical store order.  The 648-byte top output is exactly 40
  `STR Q` plus one `STR D`; no lane `ST3` is part of the proposed boundary.

P6-D3 still has to connect these states to packed-A production, B
normalization and all nine merge rows inside one public full/small wrapper.
Production and Pi 5 timing remain intentionally unchanged.

## D1 physical allocation

The pair-0 state is 27 consecutive 64-bit chunks.  During pair 1, the first
26 chunks of the combined row-major state become thirteen Q registers and the
remaining 28 chunks occupy every usable data GPR:

```text
dense D positions  0..25  -> saved_q0..saved_q12
dense D positions 26..53  -> 28 allocated data GPRs
```

`x18` is never used.  `x29` is the fixed coefficient base and `x30` is the
fixed combined public-table base.  Reusing `x30` is legal only after the outer
wrapper has saved the incoming link register.  The stores at the end of the
allocation slices are synthetic live-out observations for Slothy and the
oracle; they are not proposed coefficient scratch.

The physical audit checks every TBL source group, rejects non-consecutive
groups, unresolved symbolic registers, `x18`, and non-stack writes.  It reports
36 TBL instructions per producer, including 18 three-register TBLs, and no
failure.

The arm64 executable oracle compares the allocated regions to the production
`byte_pair_block`:

```text
PASS producer_cases=4107 pair0_bytes=216 pair1_dense_bytes=432
```

This includes signed-int16 edge patterns and 4,096 deterministic random
polynomials.

## D2 row schedule

The consumer must run in this order:

```text
physical row: 0 1 2 3 4 5 6 7 8
logical row:  0 3 6 1 4 7 2 5 8
```

Each physical row consumes six consecutive D chunks.  Rows 0--3 are entirely
Q-resident; row 4 consumes `saved_q12.d[0..1]` followed by the first four GPR
chunks; rows 5--8 are entirely GPR-resident.  `complete-model-results.json`
records every exact source, packed-A low/high source, B vector and output byte
range.  A 4,096-case model proves the reconstructed stream equals direct
three-pair packing.

## Why D3 remains a hard gate

At the pair-1 frontier there is no disposable scalar register.  Therefore:

- Q and reciprocal constants must be vector-loaded through `x30`, not created
  through a temporary `wN`;
- `x29` cannot become the final output pointer until the last pair-2
  coefficient load has completed;
- each consumed GPR chunk must die before it can be reused for address or
  wrapper work;
- allocation must preserve consecutive TBL2/TBL3 source groups across the
  actual cross-stage register map.

Separate producer and row proofs do not establish those properties.  D3 must
produce a single assembling, byte-exact full/small implementation with no
coefficient scratch or spill before a Cortex-A76 timing run is meaningful.
