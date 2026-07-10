# U01v3 Block2 / Block012 Result

Date: 2026-07-09

Status: experiment-only.  Production default is unchanged.  This round does
not mix S2/S4 high-half store work, twiddle1 semantic changes, Slothy
rescheduling, or the failed two-pass cumulative shape.

## Goal

This round checks whether the Stage12 -> Stage345 scratch/load boundary is
still visible at block2:

```text
F2 = Stage12 out2 Q16..Q23 register handoff into Stage345 block2
```

It also adds a block012 same-coverage PMU matrix:

```text
P  = production source-order same coverage
V  = U01v2 scratch same coverage
F0 = block0 isolated fuse, block1/block2 scratch
F1 = block1 isolated fuse, block0/block2 scratch
F2 = block2 isolated fuse, block0/block1 scratch
```

This matrix does not revive the F01 two-pass cumulative design.  It compares
isolated fuses under the same block0..block2 coverage.

## F2 Contract

F2 keeps the same coverage as the block2 scratch baseline:

```text
U01v2/shared-prefix Stage12
  -> Stage12 out2 Q16..Q23
  -> no Q16..Q23 scratch stores
  -> Stage345 block2 reads Q16..Q23 from registers
```

The Stage345 block2 arithmetic, reductions, and scatter stores are unchanged.
Only the Stage12 output store / Stage345 input load boundary is replaced.

Layout summary:

```text
removed Stage12 Q stores:      24 q stores
removed Stage345 Q loads:      24 q loads
inserted vector moves:          0
extra Stage12 raw q loads:      0
```

The block2 handoff registers are:

```text
Q16 q15
Q17 q7
Q18 q6
Q19 q13
Q20 q27
Q21 q17
Q22 q29
Q23 q20
```

## Implementation Notes

Two correctness bugs were found and fixed while building F2:

```text
1. Stage345 initial scatter wrap
   row2 + block2 starts at 512 + 384 = 896, which must wrap to 128.
   The generator now wraps ROW_SCATTER[row] + BLOCK_SCATTER[block] modulo 768.

2. Stage12 out2 handoff clobber
   The first F2 attempt used future handoff registers as temporary vectors.
   Later stripes then overwrote earlier Q16..Q23 values before Stage345 block2
   consumed them.  The generator now uses non-handoff temps for out2 and keeps
   all Q16..Q23 live until the Stage345 load sites are replaced.
```

These fixes are in:

```text
generate_phase123_shared_prefix_v3_block1_block01_fuse.py
```

## Correctness

Pi5 correctness:

```text
make -B test_u01v3_block2_fuse
u01v3_block2_fuse_abi_mask=0x0
u01v3_block2_fuse_mismatches=0
mismatches = 0
```

The ABI sentinel passed:

```text
x19-x28 preserved
d8-d15 low 64-bit preserved
```

The block012 PMU harness also checked correctness before timing:

```text
P/V/F0/F1/F2 total_mismatches=0
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

Boundary:

```text
Stage12 block0+block1+block2 coverage
  + Stage345 block0+block1+block2 final scatter
```

| variant | cycles | instructions | CPI | vs P | vs V | vs F0 | addr mod32/mod64 | text |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P production same-coverage | 2383 | 3343 | 0.712833 | 0 | -21 | +4 | 0 / 32 | 13280 |
| V U01v2 scratch | 2404 | 3383 | 0.710612 | +21 | 0 | +25 | 16 / 48 | 13440 |
| F0 block0 fuse + block1/block2 scratch | 2379 | 3335 | 0.713343 | -4 | -25 | 0 | 0 / 32 | 13248 |
| F1 block1 fuse + block0/block2 scratch | 2387 | 3335 | 0.715742 | +4 | -17 | +8 | 16 / 16 | 13248 |
| F2 block2 fuse + block0/block1 scratch | 2384 | 3332 | 0.715486 | +1 | -20 | +5 | 0 / 0 | 13236 |

F2 signal:

```text
F2 vs V:  -20 cycles, -51 instructions
F2 vs P:   +1 cycle,  -11 instructions
F2 vs F0:  +5 cycles,  -3 instructions
```

## Interpretation

F2 confirms that block2's Stage12 -> Stage345 scratch/load boundary has a
real cost:

```text
F2 beats the U01v2 scratch baseline by 20 cycles in the block012 matrix.
```

However, F2 is not better than the best isolated fuse in this matrix:

```text
F0 remains best: 2379 cycles
F2:             2384 cycles
```

F2 is also effectively flat against production same-coverage:

```text
F2 vs P: +1 cycle
```

So the result is positive as a boundary diagnostic, but not enough by itself to
justify a production path.

## One-Pass Cumulative Decision

The old two-pass cumulative direction remains rejected:

```text
F01 correctness passed, but it added 96 raw q loads and regressed badly.
```

The new one-pass feasibility analysis says the current unchanged Stage345
register allocation cannot simply stack F0/F1/F2:

```text
Stage345 block0 clobbers all block1 handoff regs.
Stage345 block0 clobbers all block2 handoff regs.
Stage345 block1 clobbers most block2 handoff regs.
```

Therefore the next cumulative candidate needs a new explicit liveness contract,
not another mechanical two-pass construction.

Practical follow-ups:

```text
1. u01v3_stage345_block0_preserve_block1_liveins
2. u01v3_onepass_f01_with_spill_budget
3. stop U01v3 cumulative fusion if measured spills cost more than the removed
   scratch boundary
```

The current evidence says isolated block fuses expose a real boundary cost, but
stacking them requires changing Stage345 register allocation or accepting and
measuring explicit spills.
