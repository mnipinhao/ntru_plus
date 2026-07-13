# Forward NTT Phase123 Slot Dependency Map

Date: 2026-07-08

Scope: analyze whether Phase123 can be rewritten in smaller units so its output
order is more suitable for NTT32 stage12 direct consumption.

This document is a design artifact only.  No assembly has been changed.

Source file:

```text
asm/slothy/inputs/ntt768_gt_frontend.sym.S
```

Related map:

```text
docs/gt_tmvp_decomposition_experiment/forward-ntt-phase123-stage12-tagged-map.md
```

## 1. Question

The question is not whether to make the existing Phase123 iteration even larger.
The useful question is:

```text
Can we split the current Phase123 iteration into smaller producer units, so the
producer units emit values closer to the NTT32 stage12 stripe order?
```

The current iteration emits four consecutive Q slots:

```text
iter i -> Q[4*i+0], Q[4*i+1], Q[4*i+2], Q[4*i+3]
```

NTT32 stage12 wants stride-8 stripes:

```text
stripe s -> Q[s], Q[s+8], Q[s+16], Q[s+24]
```

Therefore the interesting rewrite is not "full Phase123 iter + stage12".
It is "smaller Phase123 slot/slot-pair producers + stage12".

## 2. Current Phase123 iteration shape

One current symbolic Phase123 iteration has this structure:

```text
1. high-side loads
2. high-side multiply/reduction by constants in v0
3. low-side loads
4. combine low/high into B0 and B1 vectors
5. apply 12 vector twiddle/precompute pairs from x3
6. zip B0/B1 into 12 zip outputs
7. run 4 local DFT3 slots
8. store q9/q10/q11 to row0/row1/row2 scratch
```

The current iteration produces:

```text
4 Q slots * 3 GT rows = 12 Q-vector outputs
```

This is why the current body is register-heavy.  It materializes enough data to
produce all four local slots for all three rows.

## 3. Zip producer notation

After the B0/B1 vectors are multiplied by their twiddle/precompute pairs, the
iteration creates six B0/B1 pairs.  The names below are local to one iteration.

| Pair | B0 register before zip | B1 register before zip | Relative lane group from source comments |
| --- | --- | --- | --- |
| P0 | v4 | v10 | `[0..7]`, blocks `k=0,1` |
| P1 | v5 | v11 | `[8..15]`, blocks `k=2,3` |
| P2 | v6 | v12 | `[128..135]`, blocks `k=32,33` |
| P3 | v7 | v13 | `[136..143]`, blocks `k=34,35` |
| P4 | v8 | v14 | `[256..263]`, blocks `k=64,65` |
| P5 | v9 | v15 | `[264..271]`, blocks `k=66,67` |

The iteration then zips each pair:

| Zip symbol | Assembly |
| --- | --- |
| Z0e | `zip1 v22.2d, v4.2d, v10.2d` |
| Z0o | `zip2 v23.2d, v4.2d, v10.2d` |
| Z1e | `zip1 v24.2d, v5.2d, v11.2d` |
| Z1o | `zip2 v25.2d, v5.2d, v11.2d` |
| Z2e | `zip1 v26.2d, v6.2d, v12.2d` |
| Z2o | `zip2 v27.2d, v6.2d, v12.2d` |
| Z3e | `zip1 v28.2d, v7.2d, v13.2d` |
| Z3o | `zip2 v29.2d, v7.2d, v13.2d` |
| Z4e | `zip1 v30.2d, v8.2d, v14.2d` |
| Z4o | `zip2 v31.2d, v8.2d, v14.2d` |
| Z5e | `zip1 v4.2d, v9.2d, v15.2d` |
| Z5o | `zip2 v5.2d, v9.2d, v15.2d` |

The `e/o` naming here means the `zip1/zip2` half, not a secret-dependent
property.  All indices and table accesses are public.

## 4. Local DFT3 slot formula

Each slot is a three-input DFT3-like operation.  Write the inputs as:

```text
a, b, c
```

The output rows follow the same shape as the assembly:

```text
t    = zeta3 * (b - c)
row0 = a + b + c
row1 = a - c + t
row2 = a - b - t
```

In the assembly, `row0/row1/row2` are stored through:

```text
q9  -> row0 scratch
q10 -> row1 scratch
q11 -> row2 scratch
```

## 5. Slot dependency classes

The DFT3 input order changes with the Phase123 iteration.  There are three
classes.

### Type A: iterations 0, 3, 6

| Local slot | Q index | DFT3 inputs `(a,b,c)` | Required zip producers |
| ---: | --- | --- | --- |
| 0 | `Q[4*i+0]` | `Z0e, Z4e, Z2e` | P0, P4, P2 zip1 |
| 1 | `Q[4*i+1]` | `Z2o, Z0o, Z4o` | P2, P0, P4 zip2 |
| 2 | `Q[4*i+2]` | `Z5e, Z3e, Z1e` | P5, P3, P1 zip1 |
| 3 | `Q[4*i+3]` | `Z1o, Z5o, Z3o` | P1, P5, P3 zip2 |

### Type B: iterations 1, 4, 7

| Local slot | Q index | DFT3 inputs `(a,b,c)` | Required zip producers |
| ---: | --- | --- | --- |
| 0 | `Q[4*i+0]` | `Z2e, Z0e, Z4e` | P2, P0, P4 zip1 |
| 1 | `Q[4*i+1]` | `Z4o, Z2o, Z0o` | P4, P2, P0 zip2 |
| 2 | `Q[4*i+2]` | `Z1e, Z5e, Z3e` | P1, P5, P3 zip1 |
| 3 | `Q[4*i+3]` | `Z3o, Z1o, Z5o` | P3, P1, P5 zip2 |

### Type C: iterations 2, 5

| Local slot | Q index | DFT3 inputs `(a,b,c)` | Required zip producers |
| ---: | --- | --- | --- |
| 0 | `Q[4*i+0]` | `Z4e, Z2e, Z0e` | P4, P2, P0 zip1 |
| 1 | `Q[4*i+1]` | `Z0o, Z4o, Z2o` | P0, P4, P2 zip2 |
| 2 | `Q[4*i+2]` | `Z3e, Z1e, Z5e` | P3, P1, P5 zip1 |
| 3 | `Q[4*i+3]` | `Z5o, Z3o, Z1o` | P5, P3, P1 zip2 |

## 6. Main observation

The four local slots naturally split into two slot-pairs:

```text
slots 0 and 1 use only P0, P2, P4
slots 2 and 3 use only P1, P3, P5
```

More explicitly:

```text
slot0 uses zip1 of P0/P2/P4
slot1 uses zip2 of P0/P2/P4

slot2 uses zip1 of P1/P3/P5
slot3 uses zip2 of P1/P3/P5
```

This is the important result.  A rewrite does not have to produce all twelve zip
outputs before any DFT3 output.  It can potentially produce only the three
pairs needed for slots0/1, emit those two slots, then separately produce the
three pairs needed for slots2/3.

## 7. Candidate producer units

### Unit U01: slots0+1 producer

Produces:

```text
Q[4*i+0], Q[4*i+1]
```

Needs:

```text
P0, P2, P4
Z0e/Z0o, Z2e/Z2o, Z4e/Z4o
```

Potential benefit:

```text
roughly half the local B-pair live set
only six zip outputs instead of twelve
only six twiddle/precompute applications instead of twelve for this half
```

Cost:

```text
input loads may become less compact than the current ldp-heavy load pattern
two half-producers together may use more load instructions than the current full iteration
stage12 direct still needs outputs from iterations 0/2/4/6 or 1/3/5/7
```

### Unit U23: slots2+3 producer

Produces:

```text
Q[4*i+2], Q[4*i+3]
```

Needs:

```text
P1, P3, P5
Z1e/Z1o, Z3e/Z3o, Z5e/Z5o
```

Potential benefit and cost mirror U01.

### Unit U0/U1/U2/U3: single-slot producers

This is possible on paper, but it is less attractive as the first target.
Single-slot producers use only three zip outputs, but they leave the paired
`zip1/zip2` opportunity unused and make instruction scheduling narrower.  The
first realistic split should be U01/U23, not individual slots.

## 8. Stage12 compatibility

Stage12 stripes can be grouped against these producer units as follows.

| Stage12 stripes | Needed Phase123 outputs | Natural Phase123 producer |
| --- | --- | --- |
| stripes0+1 | slots0+1 from iters 0,2,4,6 | U01 over even Q groups |
| stripes2+3 | slots2+3 from iters 0,2,4,6 | U23 over even Q groups |
| stripes4+5 | slots0+1 from iters 1,3,5,7 | U01 over odd Q groups |
| stripes6+7 | slots2+3 from iters 1,3,5,7 | U23 over odd Q groups |

This suggests the first useful rewrite is not "one current iteration at a
time".  It is:

```text
U01(iter0), U01(iter2), U01(iter4), U01(iter6)
  -> stage12 stripes0+1

U23(iter0), U23(iter2), U23(iter4), U23(iter6)
  -> stage12 stripes2+3

U01(iter1), U01(iter3), U01(iter5), U01(iter7)
  -> stage12 stripes4+5

U23(iter1), U23(iter3), U23(iter5), U23(iter7)
  -> stage12 stripes6+7
```

## 9. Register pressure estimate

The rough live-set comparison is:

| Shape | Raw Phase123 slot outputs needed before stage12 | Extra local producers | Assessment |
| --- | ---: | --- | --- |
| current full iter | 12 row outputs per iter, then stores | all 12 zip outputs | known correct but high pressure |
| single row, one stripe | 4 raw Q vectors | one slot across four iters | good oracle/prototype only |
| single row, two stripes | 8 raw Q vectors | U01 or U23 across four iters | best first performance-shaped prototype |
| all rows, one stripe | 12 raw Q vectors | one slot across four iters | maybe possible, but tight |
| all rows, two stripes | 24 raw Q vectors | U01 or U23 across four iters | probably too much without scratch |

The U01/U23 split lowers local Phase123 pressure, but direct stage12 introduces
cross-iteration pressure.  For that reason, the first serious prototype should
carry only one row and two stripes, or use a tiny holding scratch to validate
the full-row mapping before attempting register carry.

## 10. Current conclusion

The idea is viable enough to continue, but the best first rewrite is more
specific than "rewrite from top split".

Recommended next target:

```text
Phase123 U01 producer:
  - compute only P0/P2/P4 for selected iterations
  - produce slots0+1
  - validate against current Phase123 store outputs for Q[4*i+0], Q[4*i+1]
  - then connect one-row stripes0+1 to NTT32 stage12
```

Do not start with a full three-row, all-stripe direct fuse.  The dependency map
shows that U01/U23 are the natural smaller units; a full direct fuse should only
come after U01/U23 correctness and register pressure are measured.
