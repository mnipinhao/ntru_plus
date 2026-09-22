# P103 — 1152's `frombytes` is 91% transpose, and that part is structural

P102 left item 1 as one kernel: `poly_frombytes`, **1.29x Official on M2 and
1.27x on A76**, called three times in decapsulation.  The ratio being the same
on both machines said it was a work difference, so this went looking for the
work.

## It is the Good-Thomas transpose, and almost nothing else

PMU retired instructions at the `-O3` the Makefile uses, 20,000 iterations,
empty-mode baseline subtracted:

| per call | instructions | A76 cycles |
|---|---:|---:|
| GT | **1,361** | 621 |
| Official | **888** | 488 |
| excess | **+473** | +133 |

`pack.c` runs one `transpose8` per pair, 24 instructions, over 18 pairs: **432**.
That is **91% of the 473**.  Everything else -- the wire gather, `unfold4`, the
range check, the stores -- accounts for 41 instructions across the whole call.

The transpose cannot be trimmed.  Only six of its eight output rows are used,
but the third stage's six live outputs still need all eight intermediate rows,
so a six-row variant saves 2 of 24.  Nor can it be moved to the store side:
it feeds `unfold4`, not memory -- transposing is precisely what makes the
3-halfword-to-4-coefficient unfold lane-parallel across eight wires.

So 1152's unpack deficit is the index permutation in the unpack direction,
priced at 0.375 instructions per coefficient, exactly the way the inverse pays
it in stores.  **Item 1's remainder is structural.**

## What was available, and landed

The range check was written as a loop:

```c
for (int i = 0; i < 8; i++) hi = vmaxq_u16(hi, v[i]);
```

Below `-O3`, gcc keeps `v[]` as a stack array for that loop, spills all eight
vectors and reloads them one at a time:

```
stp q19, q23, [sp, #128]      ... four more
2100:  ldr q26, [x2], #16
       umax v31.8h, v31.8h, v26.8h
       cmp x2, x7
       b.ne 2100
```

Every coefficient then makes three trips through memory instead of one.

| `frombytes`, one call, A76 | loop | tree |
|---|---:|---:|
| gcc `-O2` | 1,156 cyc | **876 (-24.2%)** |
| gcc `-O3` (the Makefile's) | 621 | **612 (-1.6%)** |

Clang was already unrolling it, so M2 is unchanged at 249.  Landed as
`8cc42ff8`: 10 cycles a call in this build, a 256-byte stack frame gone, and
24% of insurance for SUPERCOP, which compiles with whatever flags it likes.
Bit-identical output and range verdict over 65 inputs.

## A full unroll was tried and is much worse

`#pragma clang loop unroll(full)` on the 18-pair loop: **249 -> 424 cycles on
M2, +70%.**  Eighteen copies of a body holding sixteen live vectors does not
fit.  The wire offsets it would have constant-folded are only 8 `LDRH` a pair,
and `LDP` already merges the eight data loads into four.

## Where 1152 stands

| decapsulation, serialization | M2 | A76 |
|---|---:|---:|
| `frombytes` x3 | +165 cyc | +399 cyc |
| `tobytes` full x1 | +68 | +220 |
| `tobytes_small` x1 | -47 | -444 |

`tobytes_small` already wins by more than `tobytes` loses, on both machines.
What is left is the transpose, and the only way to remove it is to stop needing
the permutation -- which is the same open question the inverse leaves.
