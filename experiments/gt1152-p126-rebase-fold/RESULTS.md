# P126 — fold 1152's p65_rebase into basemul_rinv

## Idea

The inverse wants its input in the (component, half) lane basis: for each
(j, t), one vector c0h0 c1h0 c2h0 c3h0 c0h1 c1h1 c2h1 c3h1.  basemul_rinv
produces components in separate registers with t in the lanes, and
`p65_rebase` transposed that in a separate pass (432 `trn`, 36+36 multi-register
loads/stores, 74 scalar).

The transpose has three levels, and basemul already does a permute per
component: the Montgomery narrowing `uzp2(lo, hi)`.  `trn2(c, c+1)` narrows two
components at once into (c, c+1) pairs of 32-bit lanes, so the first level is
free when one iteration holds both halves of a (j, tg).  The remaining two
levels are `zip.4s` + `zip.2d` (or `st4.4s`, or `st2.2d`).  packed_i9 and
invntt16 are untouched.

## Measurements (pair = basemul_rinv + inverse, `pair.c`; decaps `bench_min.c`)

| variant | M2 basemul / inverse / pair, ns | A76 basemul / inverse / pair, cycles |
|---|---|---|
| base (Slothy basemul + rebase) | 193 / 424 / 620 | 2,381 / 5,463 / 7,855 |
| base, C basemul | 214 / 424 / 640 | 2,514 / 5,463 / 7,989 |
| C, `st4.4s` | 233 / 382 / 617 | 2,689 / 5,190 / 7,890 |
| C, `zip` + `st2.2d` | 232 / 380 / 614 | 2,695 / 5,180 / 7,894 |
| C, `trn` transpose + `str q` | 233 / 409 / 660 | 2,725 / 5,180 / 7,925 |
| C, no transpose (wrong layout, cost probe) | 209 / - / - | 2,463 / - / - |
| Slothy, 2 groups/iter, zips, no pipelining (**shipped**) | 214-230 / 393-422 / 609-654 | 2,665 / 5,187 / 7,863 |
| Slothy, 1 group/iter, `str d` + `st1 {.d}[1]` | ~216 / ~394 / ~612 | 2,792-2,802 / 5,186 / 7,996 |

Decapsulation with the shipped kernel: **M2 4,990 -> 4,972 ns (-18.5 ns,
-0.37%)**, stable over four interleaved rounds; **A76 43,521 -> 43,540 cycles
(within noise)**.  A second SLOTHY run of the same source gave M2 -15 ns but
A76 +130 cycles, so the measured schedule is the one installed.

## Why the A76 does not gain

The inverse loses exactly the rebase: -283 cycles.  basemul is on its V0
multiply floor (52 widening multiplies + 7 `mul.8h` per group, 36 x 66 = 2,376
predicted, 2,381 measured), which suggested the zips would fill idle V1.  They
do not: **the A76 splits non-multiply ASIMD ops evenly over V0 and V1 at
dispatch** (`ubench_wide.c`: 16 `smull` = 16 cycles, 16 `zip` = 8, both
together 23, not 16), so each permute in multiply-bound code costs about half a
V0 cycle, and SLOTHY's model (perfect steering) over-promises.  Single-lane
`st1 {.d}[1]` costs about 2.9 cycles each.  The 208-instruction two-group body
does not pipeline within SLOTHY's limits (UNKNOWN at 128/256/512 stalls,
300 s each), so it is scheduled with `--no-pipeline`.

Also found: SLOTHY excludes the loop's own `subs`/`b.ne` from the body and
handed the counter x4 out as scratch (a segfault); counters are now reserved
per kernel in `optimize.py`.

## Verdict

Shipped for the M2 gain and the simpler inverse (one pass, one file and the
schedule-dependent `check-inplace` gate fewer); A76-neutral.  KAT (asm and C
fallback), M2 + Linux `make check`, TIMECOP (`-O`..`-Os`) and the P125 range
proof all pass.
