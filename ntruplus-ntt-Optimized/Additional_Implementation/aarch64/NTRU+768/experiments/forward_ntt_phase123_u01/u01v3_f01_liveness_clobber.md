# U01v3 F01 Liveness / Clobber Analyzer

Date: 2026-07-09

Status: analysis artifact only.  Production default is unchanged.  This
does not mix S2/S4, twiddle1 semantic changes, or Slothy.

## Scope

This analyzes the one-pass F01 shape:

```text
Stage12 computes block0 Q0..Q7 and block1 Q8..Q15 once
  -> Stage345 block0 consumes Q0..Q7 from registers
  -> block1 Q8..Q15 must survive until Stage345 block1
```

The analyzed consumer is the existing Stage345 block0 handoff body,
not the original scratch-load block0 body.

## Stage345 Block0 Write Set

Vector registers written by Stage345 block0 handoff:

```text
q1 q2 q3 q4 q5 q6 q7 q8 q10 q11 q12 q13 q14 q15 q16 q17 q18 q19 q20 q22 q23 q24 q25 q26 q27 q28 q29 q30 q31
```

Vector registers not written:

```text
q0 q9 q21
```

`q0` is reserved for constants, so the only usable parking register
without rewriting block0 register allocation is:

```text
q21
```

## Block1 Live-In Clobbers

| Q | live reg | Stage345 block1 reg | first block0 clobber |
|---|---|---|---|
| Q8 | q10 | q10 | `sqrdmulh v10.8H, v12.8H, v14.H[1]` |
| Q9 | q20 | q20 | `sqrdmulh v20.8H, v8.8H, v2.H[0]` |
| Q10 | q30 | q30 | `add v30.8H, v17.8H, v8.8H` |
| Q11 | q24 | q1 | `sub v24.8H, v18.8H, v20.8H` |
| Q12 | q9 | q9 | `not clobbered` |
| Q13 | q6 | q6 | `ldr q6, [x12], #16` |
| Q14 | q31 | q31 | `sqrdmulh v31.8H, v20.8H, v14.H[0]` |
| Q15 | q23 | q23 | `srshr v23.8H, v31.8H, #11` |

## Summary

```text
block1 live-ins per row:              8
clobbered by Stage345 block0:         7
preserved in original regs:           1
usable parking regs without rewrite:  1
min q spills with q21 parking:        6
min q spills without parking:         7
```

## A1 Feasibility

A1 is not feasible as a no-spill, no-raw-reload, no-duplicate-Stage12
candidate while keeping the current Stage345 block0 register allocation.

Reason: 7 of 8 block1 live-ins are clobbered by Stage345 block0.  The
only block1 live-in that survives in place is Q12 in `q9`.  Apart from
that already-occupied live register, only one non-reserved vector
register (`q21`) is not written by block0.  To make A1 possible without
spills, block0 itself would need a new register allocation that
explicitly avoids the block1 live-in set.

## Spill Budget Feasibility

This table is a Stage345-block0-only lower bound.  It assumes the block1
live-in registers already exist at the point where Stage345 block0 starts.
The current Stage12 producer may need a larger spill budget because it
reuses some of these registers while producing later stripes.

| candidate | memory q spills / row | parking regs | feasible under current block0? |
|---|---:|---:|---|
| B0 | 0 | 1 | no |
| B2 | 2 | 1 | no |
| B4 | 4 | 1 | no |
| B7 | 7 | 0 | yes |
| B8 | 8 | 0 | yes |
| Bmin | 6 | 1 | yes |

Interpretation:

```text
B2 and B4 cannot preserve all block1 live-ins under the unchanged block0
write set.  Bmin is 6 q spills per row if q21 is used as a parking
register; otherwise the straightforward safe budget is B7 or B8.
```

The generated end-to-end spill-budget prototype currently uses the safer
B8 shape for both Bmin and B8, because the present Stage12 producer reuses
`q9` and `q21` while producing later stripes.  A true 6-spill Bmin would
need a Stage12 producer with an explicit post-stripe liveness contract.
