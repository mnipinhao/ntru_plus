# U01v3 Block1 / Block01 Fuse Result

Date: 2026-07-09

Status: experiment-only.  Production default is unchanged.  This round does
not mix S2/S4 high-half store work, twiddle1 semantic changes, or Slothy
rescheduling.

## Goal

This round continues the U01v3 block-first fusion line after the verified
block0 fuse:

```text
F0 = Stage12 out0 Q0..Q7 register handoff into Stage345 block0
```

The new questions are:

```text
F1:  can Stage12 out1 Q8..Q15 also hand off directly into Stage345 block1?
F01: can block0 and block1 fuse gains stack in one cumulative candidate?
```

## F1 Contract

F1 keeps the same coverage as the block1 scratch baseline:

```text
U01v2/shared-prefix Stage12
  -> Stage12 out1 Q8..Q15
  -> no Q8..Q15 scratch stores
  -> Stage345 block1 reads Q8..Q15 from registers
```

The Stage345 block1 arithmetic, reductions, and scatter stores are unchanged.
Only the Stage12 output store / Stage345 input load boundary is replaced.

Layout summary:

```text
removed Stage12 Q stores:      24 q stores
removed Stage345 Q loads:      24 q loads
inserted vector moves:          3
extra Stage12 raw q loads:      0
```

The three inserted moves are all for Q11, one per row:

```asm
mov v1.16b, v24.16b
```

Reason: Stage12 can safely keep Q11 in `q24`, while production Stage345 block1
expects Q11 in `q1`.  Block1 starts with a twiddle load into `q1`, so directly
producing Q11 in `q1` would collide with the original instruction stream.

## F01 Contract

F01 is correctness-first, not the final desired shape.  A true one-pass F01
would need to keep both block0 and block1 handoff values alive across two
Stage345 blocks:

```text
block0 live set: Q0..Q7 for 3 rows
block1 live set: Q8..Q15 for 3 rows
```

The current F01 avoids unsafe spilling by using two Stage12 passes:

```text
pass A:
  produce block0 handoff
  run Stage345 block0

pass B:
  reload the raw inputs
  produce block1 handoff
  store remaining scratch values
  run Stage345 block1
```

Layout summary:

```text
removed Stage12 Q stores:      48 q stores
removed Stage345 Q loads:      48 q loads
inserted vector moves:          6
extra Stage12 raw q loads:     96 q loads
```

The extra 96 raw q loads are the important cost.  They are not part of the
ideal block0+block1 fused pipeline; they are the cost of this conservative
two-pass proof-of-correctness shape.

## Correctness

Pi5 correctness tests:

```text
make -B test_u01v3_block1_fuse
u01v3_block1_fuse_abi_mask=0x0
u01v3_block1_fuse_mismatches=0

make -B test_u01v3_block01_fuse
u01v3_block01_fuse_abi_mask=0x0
u01v3_block01_fuse_mismatches=0
```

So F1 and F01 are semantically correct for the tested partial output boundary,
and both preserve the ABI sentinel:

```text
x19-x28 preserved
d8-d15 low 64-bit preserved
```

## Pi5 PMU

Settings:

```text
CYCLES=PMU
core pinned with taskset -c 3
NTESTS=61
NITERATIONS=20000
NWARMUP=300
NVALID_ORACLE=4096
```

### Block1 Isolated

Boundary:

```text
Stage12 block1 coverage + Stage345 block1 final scatter
```

| variant | cycles | instructions | CPI | vs P | vs V | addr mod32/mod64 | text |
|---|---:|---:|---:|---:|---:|---:|---:|
| P production same-coverage | 1797 | 2337 | 0.768935 | 0 | +5 | 16 / 48 | 9236 |
| V U01v2 scratch | 1792 | 2377 | 0.753891 | -5 | 0 | 0 / 0 | 9396 |
| F1 block1 fuse | 1776 | 2329 | 0.762559 | -21 | -16 | 16 / 48 | 9204 |

Interpretation:

```text
F1 beats V by 16 cycles.
F1 beats same-coverage production by 21 cycles.
F1 removes 48 instructions relative to V.
```

This means block1 is not just a block0 special case.  The Stage12 -> Stage345
scratch/load boundary has measurable cost for block1 too.

### Block0 + Block1 Cumulative

Boundary:

```text
Stage12 block0+block1 coverage + Stage345 block0+block1 final scatter
```

| variant | cycles | instructions | CPI | vs P | vs V | vs F0 | addr mod32/mod64 | text |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P production same-coverage | 2063 | 2845 | 0.725132 | 0 | -12 | +4 | 0 / 32 | 11288 |
| V U01v2 scratch | 2075 | 2885 | 0.719237 | +12 | 0 | +16 | 16 / 48 | 11448 |
| F0 block0 fuse + block1 scratch | 2059 | 2837 | 0.725767 | -4 | -16 | 0 | 0 / 32 | 11256 |
| F1 block0 scratch + block1 fuse | 2062 | 2837 | 0.726824 | -1 | -13 | +3 | 16 / 16 | 11256 |
| F01 block0+block1 fuse two-pass | 2300 | 3206 | 0.717405 | +237 | +225 | +241 | 0 / 0 | 12732 |

Interpretation:

```text
F0 and F1 each work in isolation.
F01 is correct but not useful in the current two-pass form.
```

F01 loses because it pays 96 extra raw q loads and duplicates Stage12 work.
The removed scratch boundary operations do not compensate for that cost.

## Decision

Keep F1 as a valid positive result:

```text
block1 boundary fuse is worth testing further
```

Do not continue with the current F01 two-pass shape:

```text
F01 correctness passes, but it is not a performance candidate
```

The next useful step is not "add block2 to this F01".  It is to design a
one-pass cumulative handoff strategy, or a smaller scheduling window, where
block0 and block1 values do not require reloading raw Stage12 inputs.

Practical next candidates:

```text
1. one-pass F01 with explicit spill budget measured separately
2. block2 isolated fuse, to see whether later block boundaries also win alone
3. Slothy scheduling only after choosing a one-pass candidate shape
```

The current evidence says the boundary is real, but naive cumulative fusion
can lose if register pressure forces duplicated producer work.
