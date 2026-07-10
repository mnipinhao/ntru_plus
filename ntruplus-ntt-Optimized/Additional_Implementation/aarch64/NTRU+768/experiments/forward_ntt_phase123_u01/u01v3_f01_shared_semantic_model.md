# U01v3 F01 Shared Semantic Model

Date: 2026-07-09

Status: shared analysis input for independent Track E and Track G.  Production
default is unchanged.  This model does not mix S2/S4, twiddle1, or Slothy.

## Scope

Only the F01 block0+block1 boundary is in scope:

```text
Stage12 block0 Q0..Q7
Stage12 block1 Q8..Q15
Stage345 block0 final scatter
Stage345 block1 final scatter
```

Full U01v3 and block2/block3 cumulative fusion are out of scope for this wave.

## Stage12 Producer Values

Current handoff registers:

```text
block0 Q0..Q7:  q29 q1 q28 q17 q26 q5 q18 q8
block1 Q8..Q15: q10 q20 q30 q24 q9 q6 q31 q23
```

Stage12 can produce block0 and block1 in one pass, but the current producer
uses temporaries that make the end-to-end minimum spill budget larger than the
Stage345-only lower bound.  This matters for Track G.

## Stage345 Block0 Facts

Current block0 handoff write set:

```text
q1 q2 q3 q4 q5 q6 q7 q8 q10 q11 q12 q13 q14 q15 q16 q17 q18 q19 q20 q22 q23 q24 q25 q26 q27 q28 q29 q30 q31
```

Block1 live-ins clobbered by current block0:

```text
q6 q10 q20 q23 q24 q30 q31
```

Block1 live-ins preserved in place:

```text
q9
```

Non-reserved parking register surviving current block0:

```text
q21
```

## Stage345 Block1 Facts

Current block1 handoff consumes:

```text
Q8  q10 -> q10
Q9  q20 -> q20
Q10 q30 -> q30
Q11 q24 -> q1  via one vector move
Q12 q9  -> q9
Q13 q6  -> q6
Q14 q31 -> q31
Q15 q23 -> q23
```

Across three rows, current block1 handoff requires three vector moves for Q11.

## Baseline Matrix

Pi5 PMU, block01 same-coverage, `NTESTS=61`, `NITERATIONS=20000`:

| variant | status | cycles | instructions | vs P | vs V | vs F0 | notes |
|---|---|---:|---:|---:|---:|---:|---|
| P | oracle | 2047 | 2850 | 0 | -26 | -10 | production same-coverage |
| V | pass | 2073 | 2890 | +26 | 0 | +16 | U01v2 scratch |
| F0 | pass | 2057 | 2842 | +10 | -16 | 0 | block0 isolated fuse |
| F1 | pass | 2062 | 2842 | +15 | -11 | +5 | block1 isolated fuse |
| Bmin | pass | 2057 | 2842 | +10 | -16 | 0 | current safe spill shape, same as B8 |
| B8 | pass | 2057 | 2842 | +10 | -16 | 0 | 24 q spills + 24 restores |

Negative results:

```text
F01 two-pass: correctness pass, performance regression due to raw q reloads.
A1 physical rename: assemble + ABI pass, correctness fail.
Bmin/B8 spill-budget: correctness pass, no gain over F0.
```

## Track Separation

Track E must prove the Stage345 semantic emitter by reproducing current behavior
before changing allocation.

Track G must first model whether changing producer granularity can reduce live
pressure enough to matter.  It should not depend on Track E in the first wave.

EG1 must not be built unless both E1 and G1 independently pass correctness.
