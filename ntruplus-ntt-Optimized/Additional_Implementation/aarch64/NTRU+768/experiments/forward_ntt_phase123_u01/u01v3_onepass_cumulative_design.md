# U01v3 One-Pass Cumulative Feasibility Design

Date: 2026-07-09

Status: design only.  No production default change.  This document does not
propose reusing the failed F01 two-pass cumulative shape.

## Goal

Find out whether block0/block1/block2 fuse gains can be stacked without:

```text
extra raw q reloads
duplicated Stage12 computation
two-pass producer work
```

The desired shape is:

```text
Phase123 raw scratch
  -> Stage12 producer computes each stripe once
  -> Stage345 consumes block outputs block-by-block
```

## What Works Today

The isolated candidates prove the boundary cost is real:

```text
F0: Stage12 out0 Q0..Q7  -> Stage345 block0
F1: Stage12 out1 Q8..Q15 -> Stage345 block1
F2: Stage12 out2 Q16..Q23 -> Stage345 block2
```

Each isolated candidate can do:

```text
remove 24 q stores
remove 24 q loads
keep other blocks scratch-based
run Stage345 arithmetic/scatter unchanged
```

F2 is especially clean at the input boundary:

```text
inserted vector moves: 0
```

## Why The Previous F01 Failed

The previous F01 correctness candidate was safe because it used two Stage12
passes:

```text
pass A: produce block0 handoff, run Stage345 block0
pass B: reload raw values, produce block1 handoff, run Stage345 block1
```

That avoided keeping block1 values live across Stage345 block0, but it added:

```text
extra Stage12 raw q loads: 96
duplicated Stage12 computation: yes
```

So it was useful as a correctness proof, but not as a performance candidate.

## One-Pass Requirement

A real one-pass cumulative version must compute Stage12 once per row/stripe:

```text
raw Qs, Qs+8, Qs+16, Qs+24
  -> out0 Qs
  -> out1 Qs+8
  -> out2 Qs+16
  -> out3 Qs+24
```

Then it must either:

```text
1. keep multiple block outputs live until their Stage345 consumer runs, or
2. store future block outputs to memory and load them later.
```

Option 2 is exactly the scratch boundary we are trying to remove for those
future blocks.  Therefore stacking fuse gains requires option 1 or a new
Stage345 schedule that preserves future live values.

## Register Pressure

Per row, the direct handoff sets are:

```text
block0 Q0..Q7:
  q29 q1 q28 q17 q26 q5 q18 q8

block1 Q8..Q15:
  q10 q20 q30 q24 q9 q6 q31 q23

block2 Q16..Q23:
  q15 q7 q6 q13 q27 q17 q29 q20
```

The maximum simultaneous live Q registers would be:

```text
block0 only:              8
block0 + block1:         16
block0 + block1 + block2:24
```

That count does not include:

```text
v0 constants
q2/q3/q4 Stage12 twiddles
q14/q1/q11/q3 Stage345 twiddle stream
Stage345 temporary products/reductions
scatter scalar state
```

So a naive "compute block0+block1+block2 and keep all live" plan is beyond the
current unchanged Stage345 register budget.

## Consumer Clobber Problem

The larger problem is not only the count.  The unchanged Stage345 blocks write
almost all vector registers.  That destroys future handoff values.

Stage345 block0 writes every block1 handoff register:

```text
block1 handoff regs:
  q10 q20 q30 q24 q9 q6 q31 q23

clobbered by block0:
  all 8
```

Stage345 block0 also writes every block2 handoff register:

```text
block2 handoff regs:
  q15 q7 q6 q13 q27 q17 q29 q20

clobbered by block0:
  all 8
```

Stage345 block1 writes most block2 handoff registers:

```text
block2 handoff regs:
  q15 q7 q6 q13 q27 q17 q29 q20

clobbered by block1:
  q7 q6 q13 q27 q17 q20
not clobbered by block1:
  q15 q29
```

Therefore this sequence is not valid without spills or a rewritten Stage345
schedule:

```text
produce block0 + block1 live values
run Stage345 block0
run Stage345 block1 from still-live values
```

Stage345 block0 will have already overwritten block1's live values.

## Can Stage12 Producer And Stage345 Consumer Interleave?

With unchanged Stage345 block granularity, Stage345 block0 needs all:

```text
Q0 Q1 Q2 Q3 Q4 Q5 Q6 Q7
```

for one row before it can run.  That means the smallest current consumer unit is
an 8-vector block, not a single stripe.

A stripe-level interleave would require rewriting Stage345 itself into smaller
consumer windows.  That is a different experiment:

```text
Stage12 stripe s produces out0/out1/out2/out3
  -> smaller Stage345 partial consumer accepts only some Qs
```

The current production Stage345 block code is not structured that way.

## Feasibility Conclusion

Under these constraints:

```text
Stage345 arithmetic unchanged
Stage345 register allocation unchanged
no extra raw q reloads
no duplicated Stage12 computation
no scratch/spill for future handoff values
```

a true one-pass cumulative F0+F1 or F0+F1+F2 is not currently feasible.

The isolated fuse result is still useful.  It says the boundary cost exists.
But stacking the gains requires one of these follow-up directions:

```text
1. Rewrite/schedule Stage345 with explicit future-live register exclusions.
2. Allow a measured spill budget and compare it against the removed q load/store boundary.
3. Keep isolated block fuses as diagnostics and move to a larger Slothy region only after choosing a feasible liveness contract.
```

## Practical Next Step

Do not extend the failed two-pass cumulative design.

The next meaningful cumulative experiment should be marked separately, for
example:

```text
u01v3_onepass_f01_with_spill_budget
```

or:

```text
u01v3_stage345_block0_preserve_block1_liveins
```

The first measures whether explicit spills are cheaper than the current scratch
boundary.  The second asks Slothy or a hand schedule to avoid clobbering block1
handoff registers while running block0.
