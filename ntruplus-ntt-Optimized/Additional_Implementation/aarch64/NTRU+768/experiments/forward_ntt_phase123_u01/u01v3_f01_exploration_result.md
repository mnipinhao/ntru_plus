# U01v3 F01 One-Pass Exploration Result

Date: 2026-07-09

Status: experiment-only.  Production default is unchanged.  This round does
not mix S2/S4, twiddle1 semantic changes, or Slothy.

## Goal

Explore whether the failed two-pass F01 shape can be replaced with a real
one-pass cumulative block0+block1 candidate:

```text
Stage12 computes block0 Q0..Q7 and block1 Q8..Q15 once
  -> Stage345 block0 consumes Q0..Q7
  -> Stage345 block1 consumes Q8..Q15
```

The hard constraints were:

```text
no raw q reloads
no duplicate Stage12
no production default change
```

## Main Liveness Result

The clobber analyzer checks Stage345 block0 handoff writes against block1
live-ins:

```text
block1 live-ins per row:              8
clobbered by Stage345 block0:         7
preserved in original regs:           1
usable parking regs without rewrite:  1
```

Stage345-only lower bound:

```text
min q spills with q21 parking: 6 per row
min q spills without parking:  7 per row
```

But this is only the Stage345 consumer lower bound.  The current Stage12
producer still reuses `q9` and `q21` while producing later stripes, so the
generated safe end-to-end spill candidate uses 8 q spills per row.

## A1 Result

A1 tried to rewrite/rename Stage345 block0 so it does not clobber any block1
live-in registers:

```text
preserved regs: q6 q9 q10 q20 q23 q24 q30 q31
raw q reloads:  0
spills:         0
duplicate Stage12: no
```

Validation:

```text
local AArch64 assemble: pass
static clobber scan:    pass
Pi5 ABI mask:           0x0
Pi5 correctness:        fail, mismatches=74568
PMU:                    not run
```

Decision:

```text
A1 is not a performance candidate yet.
```

The register-preservation goal was achieved statically, but the generated
renamed Stage345 block0 path is not semantically equivalent to the oracle.

## Spill-Budget Result

The concrete generated spill-budget candidates are:

```text
Bmin: current-generator minimum, same concrete shape as B8
B8:   explicit 8 q spills per row
B2:   infeasible
B4:   infeasible
```

Bmin/B8 shape:

```text
q spills total:     24
q restores total:   24
raw q reloads:       0
duplicate Stage12:   no
ABI mask:            0x0
correctness:         pass
```

B2/B4 are not emitted because the unpreserved block1 values are destroyed
before Stage345 block1.

## Integrated Pi5 Matrix

Settings:

```text
taskset -c 3
NTESTS=61
NITERATIONS=20000
NWARMUP=300
NINPUTS=64
NVALID_ORACLE=4096
```

Correctness:

```text
V/F0/F1/Bmin/B8 total_mismatches=0
A1 missing from PMU matrix because its standalone correctness failed
B2/B4 missing because they are infeasible
```

| variant | status | cycles | instructions | CPI | vs P | vs V | vs F0 | vs F1 | addr mod32/mod64 | text |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P | oracle | 2047 | 2850 | 0.718246 | 0 | -26 | -10 | -15 | 16 / 16 | 11288 |
| V | pass | 2073 | 2890 | 0.717301 | +26 | 0 | +16 | +11 | 0 / 32 | 11448 |
| F0 | pass | 2057 | 2842 | 0.723786 | +10 | -16 | 0 | -5 | 16 / 16 | 11256 |
| F1 | pass | 2062 | 2842 | 0.725545 | +15 | -11 | +5 | 0 | 0 / 0 | 11256 |
| A1 | correctness fail | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| Bmin | pass | 2057 | 2842 | 0.723786 | +10 | -16 | 0 | -5 | 16 / 48 | 11256 |
| B2 | infeasible | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| B4 | infeasible | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| B8 | pass | 2057 | 2842 | 0.723786 | +10 | -16 | 0 | -5 | 0 / 32 | 11256 |

## Decision

The one-pass F01 exploration did not find a new faster candidate.

```text
Bmin/B8 are correct, but they match F0 exactly in cycles and instructions.
A1 is the only no-spill direction, but it is currently incorrect.
```

Interpretation:

```text
The block1 scratch boundary can be removed, but with unchanged Stage345 block0
the cost reappears as stack spill/restore traffic.  That is why Bmin/B8 land on
the F0 envelope instead of improving over it.
```

The only F01 line that could still matter is fixing A1 or creating a new
Stage345 block0 allocator with a formally verified register-renaming map.  The
spill-budget line should stop for now because it replaced scratch traffic with
equivalent stack traffic.
