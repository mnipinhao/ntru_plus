# P61 — the dispatch loops were the gap, and GT's inverse now beats Official's

P61 is a candidate for promotion.  It improves both hosts and is byte-identical
to production over 20,000 x 864 coefficients.

## The occupancy argument

On Cortex-A76 mul-class instructions are pinned to one VEC0 pipe at two cycles
each, so the dynamic multiply count is a hard floor.  Counting it per stage:

| stage | dynamic mul | VEC0 floor | measured | idle |
|---|---:|---:|---:|---:|
| `packed_i9` x12 | 684 | 1,368 | 1,653 | 285 |
| `invntt16` main + tail | 1,055 | 2,110 | 2,356 | 246 |
| `crepmod3` (27 internal iterations) | 216 | 432 | 433 | **1** |
| driver address arithmetic | **0** | **0** | 378 | **378** |
| scratch wipe | **0** | **0** | 101 | **101** |
| total | 1,955 | **3,910** | 4,820 | 910 |

Official retires about 2,106 modular multiplies (P26: GT is 151 fewer), so its
floor is roughly 4,212 against a measured 4,755.

**Correction.**  An earlier version of this table credited `crepmod3` with 8
dynamic multiplies and therefore 417 idle cycles.  That was wrong: `crepmod3` is
the only kernel here with an internal loop, 27 iterations of 4 vectors, so it
retires 216.  Its floor is 432 cycles against a measured 433 -- it is exactly at
the multiply-pipe bound and there is nothing in it to recover.  The other three
kernels are straight-line, so their counts stand.

**GT's floor is 8% below Official's.**  GT was running 38% above its floor,
Official 25% above its.  The measured gap between them was only 65 cycles: GT's
transform is 269 cycles slower, and GT's `crepmod3` is 204 cycles faster.

Sixty-five cycles against 479 cycles of dispatch and wipe in which the multiply
pipe does nothing at all.

## The change

The i9 dispatch recomputed four pointers per iteration with `madd` chains, each
preceded by `mov x8, #const`:

```
    add x0, x25, x27, lsl #9        mov x8, #864
    add x0, x0, x28, lsl #7         madd x2, x26, x8, x20
    ...                             mov x8, #48
    mov x8, #6                      madd x2, x28, x8, x2
    madd x1, x26, x8, x1            ...
```

The loop bounds are fixed (2 tops x 3 components x 2 blocks), so all twelve
address quadruples are compile-time constants.  Both dispatch loops are fully
unrolled into immediate `add`s; the `madd` latency chains and the loop control
disappear.

## Measurement

| | A76 cycles | instructions | M2 ns |
|---|---:|---:|---:|
| production | 4,808–4,819 | 8,304 | 421.9 |
| **P61** | **4,636** | 8,015 | **414.7** |
| official | 4,755 | 4,861 | 315.1 |

Inverse: **-3.8% on A76, -1.7% on M2**, and **2.5% faster than Official on A76** —
the first time in this campaign that GT's inverse has beaten it there.

At the KEM boundary, where only decapsulation uses the inverse:

| | A76 dec | M2 dec |
|---|---:|---:|
| production | 34,703 / 34,709 | 4,185.5 |
| P61 | 34,513 / 34,521 | 4,176.4 |
| | **-0.54%** | **-0.22%** |

Keygen and encaps are unchanged, as expected.

## What is left

After the change, against the same 3,494-cycle floor:

| stage | idle | where it is |
|---|---:|---|
| `packed_i9` | 287 | inside Slothy-scheduled code |
| `invntt16` | 214 | inside Slothy-scheduled code |
| prologue, dispatch, epilogue | 112 | measured directly, all stages nop'd |
| scratch wipe | 102 | 56 stp against a 56-cycle store-pipe floor |
| `crepmod3` | 1 | at its bound |

Two things this rules out.  A call boundary costs **4.25 cycles** here -- twelve
extra `bl` to an empty leaf cost 51 cycles on A76 -- so all eighteen boundaries
are worth about 77 cycles and inlining is not worth 26KB of extra text.  And
`crepmod3` cannot be improved, in place or by fusion, because it already runs at
the multiply-pipe bound.

What is left sits mostly inside kernels Slothy has already scheduled, plus the
wipe and the SIMD-erasure epilogue, both of which are there for zeroization.

## Why this was missed

P58, P59 and P60 all chased the output scatter, which the decomposition had
already shown to be worth only 4.3% on A76.  The dispatch overhead sat in the
same decomposition, was larger, cost nothing in multiply-pipe terms, and was
never touched.
