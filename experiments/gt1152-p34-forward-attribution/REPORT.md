# P34 — the forward transform's missing 16 points, and where its cycles go

Branch `neon-1152`, parent `503eb440`.  Pi 5 core 3, GCC 14.2.0 `-march=native
-O3`, `taskset -c 3`.

P33's follow-up analysis claimed the forward transform had a **25.4% static
multiply advantage that only cashed out as 8.9% measured**, and called that "the
only item with a clear ceiling and no explanation".

**There was nothing to explain.  The 25.4% was my arithmetic error.**  The true
static advantage is **9.96%** and the measured one is **9.04%**; the remaining
0.9 points is 16 cycles of overhead, and this gate accounts for it to the cycle.

## 1. The error

I counted the official's multiply operations by slicing line ranges out of
`ntruplus-ntt-Optimized/.../NTRU+1152/asm/ntt.s` on the assumption that
`_looptop_012` began immediately after `mov counter, #128`.  Two things were
wrong at once:

- **wrong file** — the implementation actually benchmarked is the SUPERCOP leaf
  `crypto_kem/ntruplus1152/aarch64/ntt.s`.  It is the in-place
  `poly_ntt(poly *r)`; the local tree's copy has an out-of-place signature and
  differing line offsets.  (The instruction bodies are the same; only the
  offsets I sliced by were not.)
- **wrong bounds** — in the real file the label is at line 34 and `mov counter`
  at 32, with a 19-line preamble before it that my slice swallowed, and the
  slice also ran past `b.ne` into the next stage's setup.

With the labels read rather than assumed:

| | body | ×iters | multiply ops |
|---|---|---:|---:|
| `_looptop_012` (l.34–393) | 36 sqrdmulh + 45 mul + 36 mls = **117** | 8 | 936 |
| `_looptop_3456` (l.400–586) | 24 sqrdmulh + 16 mul + 24 mls = **64** | 18 | 1,152 |
| outside both loops | — | — | 0 |
| **official `poly_ntt`** | | | **2,088** |

which is the figure the earlier session had recorded correctly, before I
"re-derived" it to 2,520.

GT, with its bounds read the same way:

| | body | ×iters | multiply ops |
|---|---|---:|---:|
| `ntt9` `.Lntt_one_bank` (l.234–744) | 75 × (sqrdmulh, mul, mls) = **225** | 8 banks | 1,800 |
| `ntt_top` `.Ltop_split_loop` (l.55–111) | 5 `mul` | 16 | 80 |
| `ntt_tail` (straight line) | 0 | 1 | 0 |
| **GT forward** | | | **1,880** |

```
1,880 / 2,088 = 0.9004   →  static advantage 9.96%
```

## 2. Measured, on one core in one session

`bench_fwd.c` + `probes.S`.  Every candidate is min-over-30-interleaved-passes,
so a frequency excursion cannot land on one candidate only.  Three consecutive
runs agreed to the last printed digit on every line except `memcpy`.

```
  official poly_ntt (in place)                          4780.0
  official poly_ntt + memcpy                            4934.0
  GT ntt_asm (whole)                                    4347.7
  GT   ntt_top_asm                                       447.0
  GT   ntt_tail_asm                                       32.7
  GT   ntt9_asm (via d8-d15 trampoline)                 3872.5
  floor: GT multiply multiset (1880 ops)                3757.0
  floor: official multiply multiset (2088 ops)          4173.0
  floor: ntt_top instruction mix (16 iters)              428.0
```

The two multiply floors land on their predictions — 1,880 × 2.000 = 3,760
against 3,757 measured, 2,088 × 2.000 = 4,176 against 4,173 — which
independently re-confirms the campaign's 2.000-cycle single-pipe VEC0 cost for
`sqrdmulh`/`mul`/`mls` at 8H.

## 3. The delta, accounted for

```
  GT ntt_asm        4347.7        stages sum 4352.2 (top 447.0 + tail 32.7 + ntt9 3872.5)
  official          4780.0        wrapper cost -4.5, i.e. free
  measured delta     432.3        -9.04%

  overhead above own multiply floor:   GT 590.7    official 607.1
  predicted delta from multiply count alone        416.0
  416.0 + (607.1 - 590.7) = 432.4   vs   measured 432.3
```

**The whole difference is the multiply count, plus 16 cycles by which GT happens
to be the better-scheduled of the two.**  Both implementations sit at the same
distance above their own issue floor — GT 86.4%, official 87.3% — so there is no
structural inefficiency on either side to find.

This also matches the KEM profiler exactly.  `run-fwd.csv` records **2 calls per
operation on both sides** (keygen, encaps, decaps alike), so the boundary figure
was never diluted by call-count asymmetry, which had been the other hypothesis:

```
  per call   GT 4,382   official 4,813   -8.95%
  boundary   GT 26,322  official 28,878  -8.85%   (6 calls each)
  standalone GT 4,347.7 official 4,780.0 -9.04%
```

## 4. Headroom: there is none worth taking

| stage | measured | issue floor | of floor | headroom/call |
|---|---:|---:|---:|---:|
| `ntt_top` | 447.0 | **428.0** | **95.7%** | 19.0 |
| `ntt_tail` | 32.7 | ~0 | — | ~33 |
| `ntt9` | 3,872.5 | 3,597.1 | **92.9%** | 275.4 |

I expected `ntt_top` to be latency-bound: 39 instructions per iteration, only 5
of them multiplies, everything downstream of two `ld4 {4 × 8H}`, no software
pipelining across iterations, and 447/16 = 27.9 cycles per iteration against a
single-resource bound near 10.  **That was wrong.**  Issuing the identical
instruction mix with every chain independent still costs 428, because the three
binding resources do not overlap on this core: 10 `str q` per iteration on the
one 128-bit store pipe, 5 `mul` at 2.000 on VEC0, and two 4-register `LD4`
de-interleaves.  `ntt_top` is throughput-bound and already at 95.7%.

`ntt9`'s 92.9% reproduces P16's 93% independently, and P16 rejected scheduling
it at that figure — as P18 rejected the codec at 90% and P30 found `frombytes`
at 90%.  Nothing here clears the bar.

**So the forward transform is closed.**  Its total attackable headroom is
~294 cycles per call, all of it behind a schedule already at 93–96% of floor,
against 4,348 spent.  The only lever left would be a decomposition that issues
fewer than 1,880 multiplies or fewer than 160 stores, not a better schedule of
these ones.

## 5. Two harness bugs worth recording

- **`ntt9_asm` clobbers `d8`–`d15` without saving them.**  That is legitimate —
  `ntt.S` exists to wrap it and does the save — but calling it directly from C
  violates AAPCS.  The first run of this bench did exactly that, and GCC had
  spilled the harness's live `double` into the callee-saved half of the vector
  file, so three candidates came back as ~6e252 rather than a time.  The floor
  probes had the same defect by construction.  `probes.S` now gives each one a
  prologue.  **A measurement that reads as absurd is more often an ABI
  violation in the harness than a surprise in the code.**
- Appending `floor_top_asm` to the end of `probes.S` put it *after* the
  `.section .note.GNU-stack` directive, so it assembled into a non-executable
  section and the binary took `SIGILL`.

## Reproduce

```sh
G=<gt1152-p10-kem>; OFF=<supercop>/crypto_kem/ntruplus1152/aarch64
cp $OFF/ntt.s off_ntt.s
gcc -O3 -march=native -D_DEFAULT_SOURCE -I. bench_fwd.c probes.S off_ntt.s \
    $G/ntt.S $G/ntt_top.S $G/ntt_tail.S $G/ntt9.S -o bench_fwd
taskset -c 3 ./bench_fwd
```
