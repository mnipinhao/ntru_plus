# P30 — Survey of `poly_frombytes`

Branch `neon-1152`, parent `d7b10d40`.  Pi 5 core 3, GCC 14.2.0.

P19 called `frombytes` structural and at "~100% of its issue floor", and every
gate since has repeated that.  **Both halves were wrong.**  It was at 90%, and
one of its four per-lane operations was avoidable.

**723 -> 645 cycles.  `poly_frombytes` went from +895 to +599, decaps from
-1.67% to -2.21%, and the KEM from -2.29% to -2.51%.**

## 1. The permutation cannot be skipped at any call site

Four calls, and every consumer is a transform-domain operation:

| call | consumer |
|---|---|
| encaps, `frombytes(&h, pk)` | `poly_basemul` |
| decaps, `frombytes(&c, ct)` | `poly_basemul_rinv` |
| decaps, `frombytes(&f, sk)` | `poly_basemul_rinv` |
| decaps, `frombytes(&hinv, sk+PB)` | `poly_basemul` |

All read the Good-Thomas layout, so the permutation is needed every time.

P14's Option A — have the transform output natural order so the codec needs no
permutation — is now **more** firmly rejected than when P14 measured it.  Its
accounting credited 9,741 cycles of codec saving; after P18 and P19 the codec
is 9,033 against the official's 10,067, already a win, so that credit is gone
while the 8,130 it must pay is not.

## 2. Where the cycles are, measured

`floor.c` issues the exact per-pair instruction mix with every chain
independent, then removes one piece at a time.

| variant | cycles/pair | x18 |
|---|---:|---:|
| full mix | 36.50 | **657** |
| without the 24-op transpose | 25.50 | 459 |
| without the 8 V1-pinned `ushr` | 32.00 | 576 |
| without the 8 offset-table loads | 37.50 | 675 |

- **the permutation costs 198 cycles** — the 8x8 transpose
- **the shift costs 81** — `ushr` is V1-pinned on this core
- **the offset table costs nothing**; 675 against 657 is ordering noise

And 723 measured against a 657 floor is **90.4%**, not ~100%.

## 3. What was avoidable

The decode read each twelve-byte block as **four 24-bit values**, which needs a
shift to separate the two coefficients packed in each, then a `uzp1` to collect
them, then a mask: four operations a lane.

Read as **eight 16-bit windows** instead, the shift and the collection merge.
Lanes 0..3 take bytes `(3j, 3j+1)`, whose low twelve bits are the even
coefficient; lanes 4..7 take bytes `(3m+1, 3m+2)`, which hold the odd
coefficient shifted up by four.  One `ushl` with a per-lane count
`{0,0,0,0,-4,-4,-4,-4}` fixes both halves at once:

```c
uint16x8_t win = vreinterpretq_u16_u8(vqtbl1q_u8(raw, idx));
uint16x8_t u   = vandq_u16(vshlq_u16(win, sh), m12);
```

Three operations a lane, and the result is in the same
`[e0,e1,e2,e3,o0,o1,o2,o3]` order the transpose already wanted.  The table index
is `{0,1, 3,4, 6,7, 9,10, 1,2, 4,5, 7,8, 10,11}` — still inside the twelve
bytes, so the sixteen-byte over-read the fast path uses is unaffected.

Floor 657 -> 576, measured 723 -> 645, the same 90% utilisation.

## 4. What is left

| | cycles |
|---|---:|
| measured now | 645 |
| issue floor | 576 |
| official `poly_frombytes` | 509 |

- **The 198-cycle transpose is minimal.**  An 8x8 transpose of 16-bit elements
  built from two-input shuffles needs `log2(8) x 8 = 24` operations, and that is
  what it uses.  `st4` cannot substitute: it writes `x[4i+j] = v[j][i]` where
  the layout needs `x[8c+k] = u[k][c]`, which does not factor.
- **~69 cycles of scheduling headroom** remain, 645 against 576.  That is the
  same class as the kernels in `dev/`, and `frombytes` is a candidate for the
  clean/opt tree if it is ever worth another solve.

The 150 cycles a call that still separate GT from the official are the
permutation, and 198 of the 645 is exactly that.  Nothing else in the kernel is
above its floor by more than scheduling noise.

## 5. Whole KEM

| operation | official | GT | delta | was |
|---|---:|---:|---:|---:|
| keygen | 64,087 | 62,042 | -3.19% | -3.09% |
| encaps | 59,483 | 58,264 | -2.05% | -1.98% |
| **decaps** | 52,516 | **51,353** | **-2.21%** | -1.67% |
| **total** | **176,086** | **171,660** | **-2.51%** | -2.29% |

Every package gate green, `frombytes` ABI sentinel included, and the codec's
seven oracle checks pass unchanged — including the 3,456-case canonical
rejection sweep, which is what a wrong unpack index would break first.

## Reproduce

```sh
gcc -O2 -march=native -D_DEFAULT_SOURCE floor.c -o floor && taskset -c 3 ./floor
cd ../gt1152-p18-codec-registers && make check
```
