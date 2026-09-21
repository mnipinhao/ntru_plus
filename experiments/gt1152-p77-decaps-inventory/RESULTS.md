# P77 — decaps re-inventory: the deficit is 98% serialization

P21 last took this apart, many gates ago, and two of its findings are now
obsolete: it reported `poly_sotp_decode` at 2.6x the official (P23 fixed it to
parity) and P25 called the inverse "level with the official" (it is now -17.5%).
This measures every component of both decaps chains on the same host.

A76, `taskset -c 2`, `PERF_COUNT_HW_CPU_CYCLES`, median of 65 rounds x 300
calls, real decapsulation state.

| component | GT | Official | delta |
|---|---:|---:|---:|
| `frombytes` x3 | 1,923 | 1,464 | **+459** |
| final serialize + compare | 1,274 | 904 | **+370** |
| serialize `buf1` | 831 | 685 | **+146** |
| `sub` | 268 | 254 | +14 |
| `sotp_decode` | 466 | 457 | +9 |
| `cbd1` | 436 | 455 | -19 |
| `basemul` (hinv) | 3,114 | 3,961 | -847 |
| invntt (+`crepmod3`) | 5,610 | 6,804 | -1,194 |
| `ntt` | 4,345 | 5,664 | -1,319 |
| `hash_h` | 3,917 | 5,263 | -1,346 |
| `basemul` (first) | 2,379 | 3,961 | -1,582 |
| `hash_g` | 14,303 | 19,554 | -5,251 |
| **sum** | **38,866** | **49,426** | **-10,560 (-21.4%)** |

The component sum tracks the whole-operation measurement (43,706 against
55,130, -20.7%); the difference is call overhead, the failure path, the
`msg` copy and the `secure_clear` calls, none of which are attributed here.

## Everything GT still loses is serialization

**998 cycles, and 975 of them — 98% — are `frombytes`, `tobytes` and the
comparison.**  Every piece of arithmetic is ahead, and so is every hash.

`sub` and `sotp_decode` are ties at +14 and +9, inside the measurement's own
spread.

## The fusion is costing, not saving

The sharpest item is the final step.  The official serializes and then compares:

```c
poly_tobytes(buf2, &r1);
fail |= verify(buf1, buf2, NTRUPLUS_POLYBYTES);     /* 685 + 219 = 904 */
```

GT fuses both into one pass:

```c
fail |= poly_tobytes_compare(buf1, &f);             /* 1,274 */
```

**The fused version is 370 cycles slower than doing it in two passes.**  The
official's `verify` is a plain byte loop over 1,728 bytes that the compiler
vectorizes to 219 cycles, 7.9 bytes per cycle; fusing it into the serializer
apparently costs more than the extra pass over 1,728 bytes saves.  That is a
concrete target worth about 0.85% of decaps, and the first thing to try is
simply un-fusing it.

`frombytes` at +459 for three calls, +153 each, is the larger total.  P30 last
touched it (723 -> 645 for one call) and concluded the remaining gap was
structural; that conclusion is worth re-testing now that it is the single
biggest item left.

## Method

`prof.c` builds against either tree — `-DGT` selects the GT entry points — and
times each component in isolation from state produced by a real keypair and
encapsulation.  The official's `verify` is `static inline` in `common/kem.c` and
cannot be linked against, so the profiler carries a copy, which is why it is
attributed separately rather than folded into `tobytes`.
