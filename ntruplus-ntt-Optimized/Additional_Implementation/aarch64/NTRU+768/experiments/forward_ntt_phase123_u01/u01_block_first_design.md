# U01 Block-First Prototype Design

Date: 2026-07-09

## Scope

This is a separate forward-NTT pipeline experiment.  It is not part of the
S2/S2R rowspec Stage345 store-shape line.

Do not mix the S2 high-half `umov+str` transform into this prototype.  The
first question is whether the Phase123 shared-prefix route can produce the
layout that Stage345 wants early enough to be useful.

## Goal

Connect:

```text
Phase123 U01 shared-prefix output
  -> NTT32 Stage12 stripes0/1
  -> Stage345 block0 input
```

The first prototype keeps scratch.  It does not attempt all-row no-scratch,
because the register pressure for carrying all rows and all stripes directly
into Stage345 is too high for a first gate.

## Background

Production order:

```text
Phase123 emits row-local raw Q0..Q31
  -> store full row scratch
_gt_ntt32_batch8_to_blockmajor Stage12 reads row scratch by stripe
  -> stores post-Stage12 Q0..Q31 back to row scratch
Stage345 reads block0 Q0..Q7, block1 Q8..Q15, ...
```

The mismatch is:

```text
Phase123 emits consecutive Q slots per iteration:
  iter0 -> Q0,Q1,Q2,Q3
  iter2 -> Q8,Q9,Q10,Q11
  iter4 -> Q16,Q17,Q18,Q19
  iter6 -> Q24,Q25,Q26,Q27

Stage12 consumes stride-8 stripes:
  stripe0 -> Q0,Q8,Q16,Q24
  stripe1 -> Q1,Q9,Q17,Q25
```

U01 is the smaller Phase123 producer for slots0+1:

```text
U01 even iterations 0/2/4/6:
  produces Q0/Q1, Q8/Q9, Q16/Q17, Q24/Q25
  feeds Stage12 stripes0/1
```

## Why Block-First

Stage345 block0 wants:

```text
Q0,Q1,Q2,Q3,Q4,Q5,Q6,Q7
```

after Stage12, not before Stage12.  Stage12 stripe `s` produces four outputs:

```text
out0 -> Q[s]
out1 -> Q[s+8]
out2 -> Q[s+16]
out3 -> Q[s+24]
```

Therefore Stage345 block0 is:

```text
out0 from stripe0..7
```

The block-first experiment asks whether we can compute these `out0` values
early and let Stage345 start block0 before the entire row is forced through a
generic row scratch boundary.

## First Prototype Shape

The current source-order scaffold is:

```text
phase123_stage12_block0_first_allrows.sym.s
```

The current callable candidate is:

```text
asm/gt/experiment/forward_ntt/u01_block_first_candidate.S
```

It does:

```text
1. even U01 -> raw Q0,Q1,Q8,Q9,Q16,Q17,Q24,Q25
2. even U23 -> raw Q2,Q3,Q10,Q11,Q18,Q19,Q26,Q27
3. odd U01  -> raw Q4,Q5,Q12,Q13,Q20,Q21,Q28,Q29
4. odd U23  -> raw Q6,Q7,Q14,Q15,Q22,Q23,Q30,Q31
5. store raw Q0..Q31 to x13 row-major scratch
6. run Stage12 stripes0..7 for rows0/1/2
7. store post-Stage12 Q0..Q31 to x13 row-major scratch
8. expose block0 input as x13 row Q0..Q7
```

This is intentionally conservative.  It proves the layout and partial oracle
before attempting a lower-scratch or register-resident form.

## Output Contract

The correctness boundary for the first C/PMU harness is partial:

```text
row0 block0 input: x13 +   0 .. 112  = post-Stage12 Q0..Q7
row1 block0 input: x13 + 512 .. 624  = post-Stage12 Q0..Q7
row2 block0 input: x13 +1024 .. 1136 = post-Stage12 Q0..Q7
```

Later block outputs are also present in the source-order scaffold:

```text
block1 Q8..Q15
block2 Q16..Q23
block3 Q24..Q31
```

but the first PMU comparison should measure same-coverage block0 readiness,
not full `poly_ntt`.

## Correctness Gates

Existing Python partial oracle:

```sh
python3 experiments/forward_ntt_phase123_u01/verify_stage12_block0_first_symbolic.py --seeds 64
```

Expected result:

```text
phase123_stage12_block0_first_ok seeds=64 rows=3 outputs=96 block0_outputs=24 later_outputs=72
```

Current callable candidate gate on Pi 5:

```text
make test_u01_block_first
  u01_block_first_block0_mismatches=0
  mismatches = 0

make test_u01_block_first_oracle
  u01_block_first_block0_mismatches=0
  mismatches = 0

make test_u01v2_block_first_oracle
  u01_block_first_block0_mismatches=0
  mismatches = 0
```

C harness boundary:

```text
test_u01_block_first.c
  vector mode: generated production partial-oracle vectors
  oracle mode: callable production source-order same-coverage partial oracle
  compare block0 Q0..Q7 for rows0/1/2
```

Full `poly_ntt` differential is not a gate until the prototype is integrated
with Stage345 block0 and the remaining blocks.

## PMU Gate

Benchmark boundary:

```text
production source-order same-coverage partial path
vs
U01 block-first candidate path
```

Report:

```text
cycles
instructions
CPI
text size
register pressure notes
```

If this partial path does not beat the production same-coverage path, do not
expand it into a larger Slothy or production integration effort.

Current Pi 5 PMU, core 3, `NTESTS=61`, `NITERATIONS=10000`, `NWARMUP=200`:

```text
production_source_order_same_coverage:
  cycles median       1454
  instructions median 1830
  CPI                 0.794536

u01_block_first_candidate:
  cycles median       1568
  instructions median 1843
  CPI                 0.850787
  delta vs oracle     +114 cycles
```

Decision: do not expand this exact scaffold.  It proves the layout and
correctness boundary, but it does not create a speed signal.  A next U01 attempt
must first fix the ordering/locality issue, then re-pass this same PMU gate.

## U01v2 Update

U01v2 keeps each production Phase123 iteration intact and changes only the
order:

```text
iter0,2,4,6 -> Stage12 stripes0..3
iter1,3,5,7 -> Stage12 stripes4..7
```

Pi 5 PMU, core 3, `NTESTS=61`, `NITERATIONS=20000`, `NWARMUP=300`:

```text
production_source_order_same_coverage:
  cycles median       1454
  instructions median 1831

u01_block_first_candidate:
  cycles median       1564
  delta vs oracle     +110 cycles

u01v2_shared_prefix_evenodd:
  cycles median       1456
  instructions median 1872
  delta vs oracle     +2 cycles
```

Decision: U01v2 is the right baseline shape if this line continues, because it
preserves shared-prefix reuse.  It still should not be promoted: it is roughly
flat against the same-boundary source-order oracle, not faster.

## Store Boundary Diagnostic

A non-correctness diagnostic omits the 24 Stage12 `out0` stores for block0:

```text
3 rows * 8 stripes = 24 q stores
```

Pi 5 PMU, core 3, `NTESTS=61`, `NITERATIONS=20000`, second run:

```text
production_source_order_same_coverage:
  cycles median       1466

u01v2_shared_prefix_evenodd:
  cycles median       1458
  correctness         pass

u01v2_no_out0_store_diag:
  cycles median       1441
  correctness         skipped diagnostic
```

This is the first useful signal for a real next step: the boundary has enough
store-side cost to justify a U01v3 prototype, but only if U01v3 keeps Q0..Q7
live into Stage345 without exploding register pressure.
