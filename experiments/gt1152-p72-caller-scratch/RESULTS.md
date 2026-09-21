# P72 — caller-owned scratch: works, performance-neutral, not promoted

Opened to answer "can GT have no scratch at all, like mlkem-native?"  It
cannot, and the reason is not where I expected.

## The in-place idea is dead, and `rebase` is not what blocks it

The proposal was to make `p65_rebase` an in-place permutation so the chain
needs no scratch.  Checking the three stages:

| stage | in-place? | why |
|---|---|---|
| `rebase` | no | group 0 writes bytes 0..127; group 1 reads 64..127 |
| `packed_i9` | **yes** | reads `j*256+t*16`, writes `s*256+t*16` — the same nine addresses, all nine loads retiring 81 instructions before the first store (this is P71) |
| `invntt16` | **no** | **72 of 72** cross-call combinations overlap: call `s` writes at `8s + 72t + 1152h`, which lands inside `[s'*256, s'*256+256)` for every other `s'` |

So even a cycle-following in-place rebase would not remove the scratch —
`invntt16` needs its source and destination distinct regardless.  **The scratch
is structural.**  The gate was not worth building.

## What can be had: move the scratch to the caller

mlkem-native's property is not "no scratch" but "the assembly allocates nothing
the C caller cannot reach".  Its `intt` takes a 64-byte frame for the `d8-d15`
spill and works in place on a caller-owned buffer that `MLK_FREE` clears.

GT can have the same property by declaring the scratch in `api_glue.c` and
passing it in `x6`.  That works, all gates pass, and it makes the clear
**visible to the runtime zeroization audit** for the first time:
`clear_bytes` 34,000 -> 36,304.  Today the 1152 assembly wipe is checked by
nothing — there is no `check_zeroization.py` in this tree, and the runtime hook
cannot see stores emitted by assembly.

## Why it is not promoted

Decomposing the change on M2 (min of 200 samples):

| | M2 min |
|---|---:|
| P71: assembly-owned scratch, assembly wipe | 439.0 |
| C-owned scratch, assembly wipe | 438.5 |
| C-owned scratch, `secure_clear` | 441.5 |

**The ownership transfer is free** (-0.5ns).  The cost is entirely in the clear
method, and the two hosts disagree about it:

| | A76 | M2 |
|---|---:|---:|
| P71 | 5,609 | 439.0 |
| C-owned + `secure_clear` | **5,543** | 441.5 |
| C-owned + assembly wipe | 5,616 | **438.5** |

Neither variant wins on both, so neither meets the promotion criterion.  Held
as evidence rather than dropped: the ownership change is free and buys audit
coverage, so it is worth revisiting if the audit gap is closed deliberately
rather than by accident.

`caller_scratch.S` is the driver (no hidden allocation, no assembly wipe) and
`api_glue.diff` the caller side.  The five tree copies used for the A/B are
reproducible from those and are not kept.
