# P64 — degree-4 main-I16 output layout: static feasibility

Static study only.  No assembly was written and nothing was benchmarked.

## Why 1152 is not 864

The natural coefficient index is a mixed-radix number whose innermost digit is
the CRT component:

| | innermost radix | 4 components in bytes | natural store |
|---|---:|---:|---|
| 864 | **3** | 6 | none — `ST3` at best |
| **1152** | **4** | **8** | **one `STR D`** |

864 is `3 x 288`, 1152 is `4 x 288`, and `288 = 2 (half) x 9 (s) x 16 (t)` in
both.  Four halfwords is exactly a 64-bit store, so on 1152 a vector whose four
valid lanes are components 0-3 is delivered by a single `STR D`.

An earlier conclusion in this campaign — that no lane assignment can make the
inverse output contiguous — was derived on 864 and **does not carry to 1152**.

## The tail already does it; the main does not

| `inverse16_tail.S` | `umov` | `strh` | `str d` | instructions |
|---|---:|---:|---:|---:|
| 1152 | **0** | **0** | **32** | **430** |
| 864 | 96 | 96 | 0 | 592 |

Both main and tail read the same input shape (16 vectors from `x1`) and both
carry 32 `ext` folds, so each produces 32 vectors with four valid lanes.  The
only difference is what those four lanes mean:

| | four valid lanes are | memory stride | delivery |
|---|---|---:|---|
| tail | **components 0-3** | 1 | one `STR D` |
| main | s = 0..3 | 4 | 4 `UMOV` + 4 `STRH` |

## The counts line up exactly

There are `4 x 2 x 9 = 72` sixteen-point transforms.  The tail takes the eight
with `s = 8` (four components x two halves); the main takes the other 64.
Decoding the driver's call arguments:

| call | output base | component | s |
|---|---|---:|---:|
| main 0..7 | x19 + {0,32,2,34,4,36,6,38} | one per call | groups 0-3 and 4-7 |
| tail | x19 + 64 | all four | 8 |

Re-assigning the main to one call per `s`, eight lanes of (component, half),
gives exactly the eight existing call sites and exactly the tail's shape.

## But the tail's clean output is bought upstream

`packed_i9` writes two regions on every call:

```
x0 -> main scratch   x25+{0,128,512,640,...}   8 x STR D + 8 x ST1 {v.D}[1]   4 coefficients each
x1 -> tail region    x25+{2048,2050,2052,...}  8 x ST1 {v.H}[k]              1 coefficient each
                            ^ stride 2 bytes = the component stride
```

The scatter is not removed by the degree-4 layout; it moves from `invntt16` to
`packed_i9`.  Costing both sides per coefficient:

| path | `packed_i9` side | `invntt16` side | coefficients | instructions/coefficient |
|---|---:|---:|---:|---:|
| tail (component-contiguous) | 128 | 32 | 128 | **1.25** |
| main (current scatter) | 256 | 2,048 | 1,024 | **2.25** |

Extending the tail's scheme to the main predicts `1024 x 1.25 = 1,280` against
the current `2,304`: **about 1,024 fewer instructions**, roughly 11% of the
1152 inverse's dynamic instruction count.

## What this does and does not establish

Established: the layout exists, the call counts match, and the shape is already
implemented and correct in the tail.  The saving estimate is derived from the
tail's measured instruction shape rather than from an assumption.

Not established: that it is faster.  Every prior attempt in this campaign to
convert an instruction reduction in this kernel family into cycles has failed —
P29 (-1,378 instructions, +192 cycles), P40 (-137, +221), P60 (-1,016, +139),
all on 864, all lost to an IPC drop.  The tail proves the shape, not the speedup.

## Next step

Measure before authoring.  The cheapest decisive probe is to build a variant of
the 1152 main `invntt16` whose 128 `UMOV` + 128 `STRH` are deleted outright —
wrong output, valid timing — to bound what the delivery path is worth on this
parameter set, exactly as was done for 864 (where the answer was 4.3% on
Cortex-A76 and 19.6% on M2).  If that bound is small on A76, the redesign is not
worth authoring there either.

## Probe: what the degree-4 delivery is actually worth

Two variants of the 1152 main `invntt16`, both timing-only:

- **D4** — each group of four `UMOV` + four `STRH` replaced by one `STR D` of the
  folded vector, which is exactly the proposal's instruction mix;
- **NS** — the delivery path deleted outright, an idealised floor.

| | A76 cycles | instructions | M2 ns |
|---|---:|---:|---:|
| current | 6,012 | 10,296 | 535.2 |
| **D4 (`STR D`)** | **5,886 (-2.1%)** | 8,488 | **436.8 (-18.4%)** |
| NS (deleted, floor) | 5,812 (-3.3%) | 8,248 | 435.5 (-18.6%) |

**This is the first design in the campaign that improves both hosts.**  The 864
attempts (P29, P40, P60) all regressed Cortex-A76; the degree-4 layout does not,
because `STR D` delivers four coefficients in one instruction without the
producer restructuring that those designs needed.

### Does the probe understate the gain because the schedule was not redone?

The gap between D4 and the idealised floor bounds it: **74 cycles on A76 (1.2%)
and 1.3 ns on M2 (0.3%)**.  Rescheduling the delivery path cannot be worth more
than that, because the floor has no delivery at all.

Separately, the three failed 864 designs were not unscheduled.  P40's record
states all three allocations completed bounded Cortex-A76 timing windows; P29
ships `.alloc.S` with Slothy timing logs; P60 was scheduled in this session
(split 16 + naive interleaving, reorder-only, 342/351/331s), and scheduling was
worth 45 cycles there.  Their losses were IPC, not missing schedules.

### The probe is optimistic on the producer side

It changes only `invntt16`'s store instruction, not the scratch layout.  A real
implementation needs `packed_i9` to write components contiguously, and the tail
shows what that costs upstream: `packed_i9` writes the tail region with eight
`ST1 {v.H}[k]` per call (one coefficient each) instead of the main region's
`STR D` pairs (four each).

| path | `packed_i9` stores | per coefficient |
|---|---:|---:|
| main region (blocked) | 16 per call | 0.25 |
| tail region (component-contiguous) | 8 per row | 1.0 |

Extending that to all nine rows costs roughly **+768 instructions** in
`packed_i9` against the **-1,792** saved in `invntt16`, so the realistic net is
about **-1,024**, not -1,792.  How much of the producer's extra cost hides in
idle slots differs by host — Cortex-A76 has many, Apple has few — so the A76
gain will shrink more than the M2 gain.

The measured -2.1% / -18.4% are therefore an upper bound, not a forecast.

## The lane basis is the design that works

Three ways to reach the degree-4 output, all modelled as instruction-mix probes
on the real kernels:

| | A76 cycles | instructions | M2 ns |
|---|---:|---:|---:|
| current | 6,018 | 10,296 | 535.2 |
| `invntt16` side only (no producer cost) | 5,882 (-2.2%) | 8,488 | 436.8 (-18.4%) |
| **lane basis (+128 transpose ops)** | **5,970 (-0.8%)** | 8,616 | **445.3 (-16.8%)** |
| **lane basis (+176, conservative)** | **5,938 (-1.3%)** | 8,664 | **449.9 (-16.0%)** |
| tail's method extended naively | 6,705 (+11.5%) | 9,256 | 595.1 (+11.2%) |

The last row is the important negative.  Forcing component-contiguous output
while keeping `packed_i9`'s lane basis means writing it with single-lane `ST1`,
and a single-lane vector store occupies a vector pipe exactly as `UMOV` does.
`packed_i9` is already about 83% VEC0-occupied, so 768 extra vector-pipe
operations there cost more than the 1,792 saved in `invntt16`.  **The scatter is
not removed; it moves somewhere more expensive.**

Changing the lane basis instead replaces the scatter with a transpose, and a
transpose is much cheaper.  The prediction is insensitive to the transpose cost
model: +128 and +176 extra operations bracket to -0.8% and -1.3% on A76, the
difference being inside the noise there, and to -16.8% and -16.0% on M2.

## Register budget: ample, unlike 864

Physical live-range profile, one def to the last use before the next def of the
same register:

| kernel | peak live | free at peak |
|---|---:|---:|
| `packed_i9` (1152) | **21** | **11** |
| `invntt16` (1152) | 24 | 8 |
| 864's paired producer (P58) | 33 | over budget |

Every instruction of `packed_i9` has at least eight free registers and 99.5% have
at least twelve, so an eight-vector input transpose fits without spilling.  This
is the opposite of 864, where P58 found the producer already at the 32-register
ceiling and P60 had to spill pointers to the stack.

## What is still unproven

- The transpose structure itself.  Nine input indices over sixteen `t` gives 144
  vectors to rebase; amortised as 8x8 transposes that is `144/8 x 24 = 432`
  operations against the present 256 on the output side.  Both probe points are
  synthetic instruction mixes, not a real permutation.
- The call decomposition changes: one `packed_i9` call per `t` carrying all four
  components, instead of one per (component, half-group, t-group).  The count
  stays at sixteen.
- Constants must be rearranged to the new lane meaning and the range chain
  re-proven.
- Whether `basemul_rinv`'s output layout can stay as it is, with `packed_i9`
  absorbing the rebase, or whether the change propagates into the forward path.

## Verdict

The degree-4 layout is worth pursuing on 1152, by changing the lane basis and
not by extending the tail's single-lane stores.  Predicted **-0.8% to -1.3% on
Cortex-A76 and -16.0% to -16.8% on M2 Pro**, both hosts improving, which no
design in the 864 campaign achieved.

The next gate should settle the transpose structure and the call decomposition
before any kernel is authored, and must re-measure: every prediction in this
campaign that survived to assembly has been smaller than its probe.
