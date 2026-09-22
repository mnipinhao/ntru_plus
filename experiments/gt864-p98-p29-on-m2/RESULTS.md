# P98 — Slothy does not rescue the repack, and P29 was rejected on the wrong machine

Two questions, one session.  Neither of my P97 candidates survives; a design
already on disk does.

## Slothy cannot schedule the repack out

P97's repack pass was hand-written, and its 397 instructions recycle `x3`/`x5`
every group and issue the groups in strict order -- on A76's four-wide window
exactly the shape that cannot overlap.  Slothy's AArch64 model has no parser for
single-lane `ST3`, so the tail was rewritten as three `ST1 {v.h}[lane]` off a
register post-index, and the region was cut at four-group boundaries: this repo
has never asked Slothy for more than 164 instructions in one region (P10), and
397 in one region never reached a feasible schedule.

Four regions, 99 instructions each, all **OPTIMAL**: 63 cycles, **IPC 1.57**.

| repack, 864 coefficients | M2 Pro | Cortex-A76 |
|---|---:|---:|
| hand-written, single-lane `ST3` tail | 32.6 ns | 93.7 ns |
| the Slothy-parseable form (`ST1` tail) | 32.5 | 107.2 |
| **Slothy-scheduled** | 43.1 | **116.1** |

Slothy makes it **worse on both machines**, and its own IPC 1.57 says why: the
pass is store-issue bound, and scheduling does not change µop counts.  Making
the tail parseable cost 13.5 ns on A76 before the scheduler ran at all.

## The output stage cannot be repaired in place either

Each group's final register was measured to carry its four outputs in **both**
halves (32/32) -- the last step is an eight-lane reduction `x.lo + x.hi` written
as `ADD v, v, EXT(v)`, which is symmetric.  So P97's `16 STR Q` pricing was
invalid: a whole-vector store writes half redundant data.  As the kernel stands
the free layout costs 32 `STR D` per call, and the honest P97 net is **-40 ns on
M2, +35 on A76**, worse than reported.

Two groups' reductions merge with one `ZIP1 .2D` of their low halves, which
would make `STR Q` valid.  It cannot be retrofitted: Slothy allocated the
existing kernel for minimum pressure, every register is redefined immediately
after its last extraction, and **only 1 of the 16 pairings is feasible**.  It
needs the symbolic source, not a rewrite of the scheduled output.

## Which is exactly what P28/P29 already built

`gt864-p28-paired-i16` and `gt864-p29-direct-st3`, 14 and 7 days ago: paired
main I16, direct natural-order output through full-vector `ST3.4h`, no route
masks, full Slothy allocation, oracle 1,001/1,001, 4,096 inverse cases, KAT.
Both **rejected**, on Cortex-A76, at +76.8 cycles on the complete inverse.

P29 retires **1,042 fewer instructions and 748 fewer stores** than today's
production for the same work:

| | instructions | stores |
|---|---:|---:|
| production, 6x main + tail + `crepmod3` | ~5,362 | ~972 |
| P29, 3x paired + direct tail + `ST3` route | 4,320 | **224** |

Same harness, same buffers, both machines, main+tail+ternary:

| | M2 Pro | Cortex-A76 |
|---|---:|---:|
| production | 274.9 ns | 1,157.0 ns |
| **P29** | **236.3 (-14.1%)** | 1,289.3 (+11.4%) |

**P29 is worth -38.6 ns on M2.**  That is 36% of GT's whole +106 ns inverse
deficit against Official, from a design that has been sitting finished and
rejected.  It is the campaign's A76-only blind spot with a number on it: nine
gates rejected store-path redesigns on the one machine where stores hide in the
multiply-port shadow.

A76 is worse than P29's own record (+132 ns here against +32) because production
has been reworked several times since 15 September while P29 has not.

## Where this leaves 864's inverse

P29 still fails 兩台都不得退步, and its own next-gate note already said not to
reschedule it or optimise only its stores: its IPC falls from production's
1.7056 to 1.3872, so on A76 it loses more to the dependency shape than the
1,042 retired instructions win back.

The problem is now sharply posed, and it is not a store-addressing problem:
**keep P29's store shape, which M2 pays 14% for, without its issue-width
collapse, which A76 charges 11% for.**  That is a producer/consumer dependency
question, and both symbolic sources (`candidate-main.sym.S`,
`candidate-main-route.sym.S`) are on disk to start from.

Measurement caveat: the harness feeds plausible but unseeded buffers, so it
prices the instruction mix and memory traffic, not an end-to-end result.  Both
kernels are data-independent, and P29's correctness was gated separately.
