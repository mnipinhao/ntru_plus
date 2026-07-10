# U01v3 F01 One-Pass Spill-Budget Variants

Status: experiment-only.  Production defaults are unchanged.

Budget definition: the budget is the number of block1 handoff vectors per row
that may be preserved across the current one-pass Stage12 producer and
unchanged Stage345 block0 by spilling to stack.

The Stage345-only lower bound is smaller, because Q12 in `q9` is not written by
block0 and `q21` is not used by block0.  The current end-to-end producer still
uses `q9` and `q21` while producing later stripes, so this concrete generator
uses the conservative safe shape: spill all eight block1 handoff registers:

```text
q10 q20 q30 q24 q9 q6 q31 q23
```

Therefore the minimum feasible budget for this current generated producer is
eight vectors per row.  Bmin and B8 are concrete assembly candidates with 24
vector spills and 24 vector restores across the three rows.  They compute
Stage12 once, do not reload raw q inputs, and do not duplicate Stage12.

B2 and B4 are intentionally not emitted as performance candidates.  With only
two or four preserved block1 live-ins, unchanged Stage345 block0 would destroy
the remaining block1 handoff values before Stage345 block1.  Repairing that
would require raw q reloads, duplicate Stage12, or a Stage345 block0 rewrite,
which are outside this task's constraints.
