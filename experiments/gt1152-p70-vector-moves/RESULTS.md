# P70 — the 32 vector moves: 24 removed, and they were nearly free

P69 closed by noting that `invntt16_asm` carries 32 `orr vD.16B, vS.16B, vS.16B`
— pure vector moves, 256 dynamic instructions across the eight calls — and that
Slothy could never remove them because it preserves the instruction multiset by
design.  They are the residue of an in-place butterfly that is no longer in
place, and they come straight from NTRU+864's kernel, which has exactly 32 in
660 instructions.  `packed_i9` has none, at 864 or 1152.

**Taken: A76 5,774 -> 5,754 cycles, -0.35%.  M2 flat at -0.26%, best min
identical.**  Both hosts hold, so it promotes.

## The result that matters

24 of the 32 removed, 192 dynamic instructions, and the A76 gave back **20
cycles** — about 0.1 cycles per instruction removed.  M2 gave back nothing
measurable.

That is the second half of P69's lesson.  P69 found that reordering buys almost
nothing because the machine reorders anyway; P70 finds that removing *these*
instructions buys almost nothing because `orr vD, vS, vS` is a register move,
and both cores resolve moves at rename rather than executing them.  Removing
1,841 instructions in P68 was worth 13.9% on M2; removing 192 moves is worth
zero.  **Instruction count is not the cost model — what the instructions are
is.**

| | A76 cycles | M2 ns | instructions/call |
|---|---:|---:|---:|
| P69 | 5,774 | 476.5 | 433 |
| P70 | **5,754** | 475.2 | **409** |

A76: median of 201 rounds x 200 calls, `taskset -c 2`, `PERF_COUNT_HW_CPU_CYCLES`,
three repetitions agreeing to the cycle.  M2: median-of-medians over 30 runs;
best min 459.50 both.  Bit-identical over 5,000 M2 and 2,000 A76 trials; in the
KEM all gates pass and the KAT is byte-identical.

## Why 24 and not 32

A move `vD <- vS` is removable when every read of `vD` in `vD`'s live range
happens before `vS` is redefined.  The eight that remain fail exactly that
test:

```
line  36: v21 <- v2   (v2 reused at 38)     line 126: v14 <- v22  (v22 reused at 163)
line  41: v29 <- v15  (v15 reused at 42)    line 133: v3  <- v6   (v6  reused at 224)
line  47: v0  <- v24  (v24 reused at 49)    line 151: v13 <- v12  (v12 reused at 157)
line  99: v30 <- v7   (v7  reused at 108)   line 188: v11 <- v1   (v1  reused at 196)
```

Those are genuine value-preserving copies: the source really is overwritten
before the copy is read, so the old value has to live somewhere.  Removing them
needs a different register allocation, not a rewrite — and at the measured rate
the eight are worth about seven cycles, so they are not worth a Slothy
re-allocation round.

## Three bugs, one family, all caught by the differential test

The pass was wrong three times, and every version assembled cleanly and looked
right:

1. **The register scan missed `ldr q`.**  The kernel spells the same
   architectural register `v27`, `q27` or `d27` depending on the instruction; a
   `\bv\d+\b` scan sees none of the loads as definitions.  Wrong code, caught on
   the first trial.
2. **One scan limit used for two questions.**  The walk stopped when the
   *source* was redefined, so a move whose reader lay past that point looked
   dead and was deleted outright.  `vD`'s live range ends when `vD` is
   redefined; `vS`'s value survives until `vS` is redefined.  They are
   independent, and conflating them invented eight "dead" moves that were not.
3. **A blanket textual rewrite renamed the destination.**  `sub v0.8H, v0.8H,
   v9.8H` reads and writes the same register, so substituting `v0 -> v21`
   everywhere produced `sub v21, v21, v9` — correct-looking code that writes to
   the wrong place.  Only source operands may be rewritten.

All three are the family P60 documented: getting def/use or interval boundaries
wrong on an instruction that reads what it writes.  Each was found by bisecting
the number of moves applied until the differential test flipped, which located
the offending move in four builds.

## What is left

The inverse now stands at 5,754 against its 4,970-cycle multiply floor, 15.8%
above it.  P69 established that the gap is not schedulable; P70 establishes
that the vector moves were not it either.  What remains is the driver, the
rebase pass, `crepmod3`, and real dependency.
