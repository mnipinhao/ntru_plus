# P60 result — the fusion is correct, and it still does not win

P60 is **not promoted**.  Production is unchanged.

## What was built

Every inserted chain carries the raw-to-ternary reduction and the delivery:

```
ldr  q{C}, [x4, #CONST]        cmgt v{B}, v{n}, v{C}
ldr  q{C}, [x4, #CONST+16]     cmgt v{C}, v{C}, v{n}
add  v{A}, v{n}, v{B}          sub  v{A}, v{A}, v{C}
ldr  q{C}, [x4, #CONST+32]     sqrdmulh v{B}, v{A}, v{C}
ldr  q{C}, [x4, #CONST+48]     mls  v{A}, v{B}, v{C}
ldr  x17, [sp, #8]             ldr  q{C}, [x17, #b2]
ext  v{B}, v{A}, v{A}, #8      ldr  x17, [sp, #0]
add  x17, x17, #base           st3  {v{A}.4h, v{B}.4h, v{C}.4h}, [x17]
```

`A,B,C` are a consecutive triple, because `ST3` requires one.  Nine of the 32
store points have no consecutive triple free, and one more was lost once the
liveness model was corrected, so 22 of 32 fuse per bank and ten fall to a
203-instruction residual pass — against `p29_main_route`'s 873.

Only `x17` is genuinely free: the producer materialises constants with
`mov w2, #9` and `mov w3, #9`, and a 32-bit write clobbers the whole 64-bit
register.  Both pointers are therefore spilled at entry and reloaded through
`x17` inside each chain.

## Correctness

Byte-identical to production over 20,000 x 864 coefficients, before and after
scheduling, with zero non-ternary outputs.

Four defects had to be found first, all the same family — an instruction that
**reads** its destination being modelled as defining it:

| misclassification | symptom |
|---|---|
| `ldr q, [x3]` treated as defining x3 | pointer liveness wrong throughout |
| `mov w2, #9` not matched by an `\bx2\b` scan | x2 clobbered, SIGSEGV |
| `mls`'s def sorted before its use at the same index | interval closed early, non-ternary output |
| `mov v31.d[1], v21.d[0]` treated as a full define | it writes one lane; four groups wrong |

`verify_regs.py` now checks this independently and reports zero violations.

## Measurement

| variant | instructions | A76 cycles | IPC | M2 ns |
|---|---:|---:|---:|---:|
| production | 8,304 | **4,820** | 1.72 | 422.5 |
| P29 direct ST3 | 6,926 | 5,012 | 1.38 | **380.9** |
| P60 fused, unscheduled | 7,288 | 5,004 | 1.46 | 388.7 |
| **P60 fused, scheduled** | 7,288 | **4,959** | 1.47 | 389.3 |
| official | 4,861 | 4,755 | 1.02 | 314.5 |

Phase 2 is worth 45 cycles on A76 (5,004 -> 4,959) and nothing on M2.

## Why it does not win

The premise was that the route's instructions could issue in the producer's idle
slots.  P58 showed the registers were there, P59 showed Slothy could schedule it,
and both were right — but the slots are not there on the real machine.

Slothy's Cortex-A76 model reports 292 cycles for `fused_bank0`'s 1,176
instructions, IPC 4.03.  Measured, the whole inverse runs at IPC 1.47.  The model
counts issue slots; the hardware is bound by something it does not model, which
is the same gap P59 recorded (model 4.00 against a measured 1.7).

The result is the campaign's recurring one, now confirmed once more with the
instructions actually moved rather than merely removed: **on Cortex-A76 every
instruction taken out of this kernel costs more IPC than it saves.** P29 removed
1,378 and lost 192 cycles.  P60 removes 1,016, interleaves them into the
producer, and still loses 139.

## What this settles

- The fused design is buildable, correct and schedulable.  It is not faster.
- P29 remains the best Apple-side variant at 380.9 ns, and still costs +4.2% on
  Cortex-A76.
- Nothing here beats production on both hosts, which was the standing criterion.
- Reordering alone is the right shape for phase 2: asking Slothy to re-allocate
  as well made a window infeasible after 728s, because the fused code sits at the
  producer's own 32/32 with no slack — exactly what P58 predicted.
