# P71 — the rebase buffer and the scratch are the same 2,304 bytes

Comparing the inverse against the official for the first time since P37 showed
the two hosts disagreeing: **A76 -15.4%, M2 +10.6%**.  Splitting the difference
showed the whole M2 deficit was the zeroization wipe, which the official does
not do at all — its `poly_invntt` is 553 instructions with zero clearing.

**Taken: A76 5,754 -> 5,607 (-2.55%), M2 474.75 -> 454.50 ns (-4.27%).**
Both hosts, by the widest margin of any gate since P68.

## What P68 got wrong

P68 added a 2,304-byte rebase buffer beside the 2,304-byte scratch and wiped
both, so the exit wipe went from 1,792 bytes to 4,608.  On A76 stores are free
filler and it cost nothing; on M2 it is 41.5 ns, and P68 never compared against
the official, only against its own predecessor.  That is how a change that
improved both hosts still moved GT further behind on one of them.

## The two buffers were never simultaneously live

`packed_i9` call `t` reads nine vectors at `j*256 + t*16` and writes nine at
`s*256 + t*16` — **the same nine addresses**.  The rebase buffer is read only by
the sixteen `packed_i9` calls and dead after them; the scratch is written by
those same calls.  They are one working set held in two places.

Overlaying them is safe exactly while every data load retires before the first
store.  P68 assumed Slothy's interleaving made that unsafe and allocated a
second buffer rather than check.  It holds, with room:

```
data loads from x2 : positions 1, 2, 4, 7, 8, 12, 14, 16, 18
stores to x0       : positions 99, 124, 129, 138, 140, 142, 144, 147, 148
                     margin: 81 instructions
```

That is a property of the schedule, not a guarantee, so `check_inplace.py`
asserts it and is wired into the Makefile as `check-inplace`.  A future Slothy
run that interleaves them fails the build instead of silently corrupting
coefficients.

## Not a security tradeoff

The buffer count drops from two to one, and all 2,304 bytes of it are still
wiped.  Nothing that was cleared before is left uncleared now — the previous
4,608-byte wipe was covering one working set twice.  `test_zeroization` reports
`nonzero_after=0` unchanged.

## Measurement

| | A76 cycles | M2 ns (best min) |
|---|---:|---:|
| P70, two buffers | 5,754 | 459.50 |
| P71, overlaid | **5,607** | **439.00** |
| | -2.55% | -4.27% |

A76: median of 201 rounds x 200 calls, `taskset -c 2`, `PERF_COUNT_HW_CPU_CYCLES`,
three repetitions agreeing to the cycle.  M2: median-of-medians over 30 runs.
Bit-identical over 5,000 M2 and 2,000 A76 trials; in the KEM every gate passes
and the KAT is byte-identical.

## Where the inverse now stands against the official

| | official | GT | |
|---|---:|---:|---|
| A76 cycles | 6,800 | **5,609** | **-17.5%** |
| M2 ns (min) | 415.5 | 439.5 | +5.8% |

The official figure is `poly_invntt` + `poly_crepmod3`, 6,205 + 599, because
GT's single `poly_invntt_ternary` does both — decaps calls the official's twice
and GT's once.  P37's "-4.91%" was against the 6,205 alone and understated the
A76 win by a factor of three.

The remaining M2 gap is 24 ns and the remaining wipe is 2,304 bytes, which at
P71's measured rate is about 20 ns.  **The inverse's entire M2 deficit is
zeroization the official does not perform.**  Removing it is not a performance
question but a security one, and it should be answered as such rather than
optimized around.
