# P19 — Should the serializer be written in assembly?

Branch `neon-1152`, parent `c76083a2`.  Pi 5 core 3, GCC 14.2.0, perf_event PMU.

The question was whether to hand-write the P18 serializer in assembly, as
NTRU+864 did with 7,751 Slothy-scheduled lines.  **Measurement answered no, and
redirected the target.**  The codec was already at 90% of its issue floor, and
the whole remaining serialize gap was in `frombytes`, not `tobytes`.  Cutting
instructions instead of scheduling them took serialize from +911 to **-1,034**
and the KEM from +1.8% to **+0.65%**, with encapsulation now 1.97% faster than
the official.

## 1. What the A76 actually costs (measured, not modelled)

`pipe2.c`, `pipe4.c`: twelve or eight independent chains, so latency never binds.

| operation | cycles/op |
|---|---:|
| `tbl`, 1 source | **0.500** |
| `tbl`, 2 sources | **0.500** |
| `tbl`, 3 sources | 1.000 |
| `tbl`, 4 sources | 1.500 |
| `trn1` / `zip1` / `uzp1` / `umin` / `add` / `and` / `cmhi` | 0.500 |
| `ushr` (and `ushll`, `ushll2`) | 1.000 |
| `umlal2` | 1.000 |

Two corrections to the Slothy Cortex-A76 model, which this repo would otherwise
schedule against:

- the model gives `(vtbl, vtbl_2): 1`; the hardware issues both at **0.5**, so
  the model is pessimistic about `tbl` by 2x.
- mixing a pipe-pinned op with a general one costs more than either alone:
  `umlal2` x12 with `trn1` x12 measures 0.708 per op where both pipes running
  freely would predict 0.5.  `ushr` x12 with `and` x12 gives the same 0.708.

## 2. The floor, measured rather than derived

`pipe3.c` issues the **exact per-pair instruction mix** of `tobytes_small` — same
mnemonics, same counts, all chains independent, loads and stores included.  That
is the issue-limited floor with scheduling made perfect by construction.

```
one pair, issue-limited floor    44.00 cycles   ->  792 for 18 pairs
measured tobytes_small                             878
utilisation                                      90.2%
```

An op-count estimate from the Slothy model had predicted 32 cycles/pair (576).
The hardware says 44.  **Scheduling the existing instruction mix, by hand or by
Slothy, is worth at most 86 cycles per call — under 10%.**

`pipe5.c` tests the most promising restructure: drop the 8x8 transpose entirely
and let one four-source `tbl` gather each lane's twelve bytes from four
component-combined registers, 40 vector ops instead of 64.

```
tbl4 scheme, one pair            41.00 cycles   ->  738
transpose scheme                 44.00 cycles   ->  792
```

Three cycles a pair.  `tbl` with four sources costs 1.5 where `trn` costs 0.5, so
removing 24 transpose ops and adding 8 expensive lookups very nearly cancels.
**Rejected**: it also forces four consecutive registers per lookup, and buys 7%.

So the combined ceiling on restructure *and* perfect scheduling was 878 -> 738,
16%.  Assembly was not the lever.

## 3. The profile said the target was wrong

Per entry point, from the component profiler rather than a fixed input:

| | GT | official |
|---|---:|---:|
| tobytes (3 entry points, 6 calls) | 7,022 | 8,037 (7 calls) |
| **frombytes (4 calls)** | **3,945** | **2,019** |
| total | 10,967 | 10,056 |

**`tobytes` was already 1,015 cycles ahead of the official.**  The entire +911
was `frombytes`, at 986 per call against 505.  Writing `tobytes` in assembly
would have optimised the half that was already winning.

## 4. What was done instead: four instruction-count cuts

**Canonical in two ops instead of three** (both tobytes paths, 8 vectors/pair).
`a + ((a>>15) & q)` became `umin(a, a+q)` read unsigned: every input is in
(-q, q), so `a+q` is in (0, 2q) and never wraps 16 bits; a negative `a` is huge
unsigned and `a+q` is the small correct one, a non-negative `a` is already the
small one, so an unsigned minimum picks the right representative either way.

**Widen, shift and combine in one op instead of three.**  `vmovl` + `vshll_high(x,12)`
+ `vorr` became `vmovl` + `vmlal_high_n(y, x, 4096)`: a widening
multiply-accumulate by 4096 *is* widen-and-shift-and-add, and the 24-bit
little-endian pair it produces is exactly the wire format.

**`frombytes`: one 16-byte load instead of two.**  The table lookup only reads
bytes 0..11, so a plain `ldr q` four bytes wider than the block is free.  Only
the last block, at offset 1716, would read past the 1728-byte input — it lives
at lane 7 of pair 17, the final iteration, so that one pair keeps the two-load
path.

**`frombytes`: three unpack ops instead of four.**  `y >> 12` is the odd
coefficient *exactly* (y < 2^24), needing no mask, so `ushr` + `uzp1` + one
`and` replaces `and` + `ushr` + `and` + `uzp1`.

**`frombytes`: a running maximum instead of a compare and an or per lane.**
Some coefficient is out of range exactly when the maximum is, so
`vmaxq_u16` accumulating and one `vmaxvq_u16(hi) >= Q` at the end replaces
`vcgeq` + `vorrq` in every lane.

Plus `#pragma GCC unroll 18` on the `tobytes` loop only — applied to all three
loops it had cost `tobytes_compare` 410 cycles to register pressure.

## 5. Measured

`bench.c` checks byte-identical agreement with the previous codec on all four
entry points, plus a corrupted-compare case, before timing.  `agreement: pass`.

| entry point | P18 as committed | **now** | saving |
|---|---:|---:|---:|
| `tobytes_full` | 1,471 | **1,333** | -138 |
| `tobytes_small` | 990 | **836** | -154 |
| `tobytes_compare` | 1,431 | **1,332** | -99 |
| `frombytes` | 956 | **723** | -233 |

`frombytes` is now essentially at its own issue floor.

## 6. Whole KEM

| operation | official | GT | delta | was |
|---|---:|---:|---:|---:|
| keygen | 64,073 | 64,764 | +1.08% | +1.7% |
| **encaps** | 59,498 | **58,325** | **-1.97%** | -1.0% |
| decaps | 52,538 | 54,171 | +3.11% | +5.2% |
| **total** | **176,109** | **177,260** | **+0.65%** | +1.8% |

| category | official | GT | delta | was |
|---|---:|---:|---:|---:|
| hash | 84,657 | 85,642 | +985 | +1,143 |
| forward | 28,881 | 26,262 | -2,618 | -2,605 |
| inverse | 6,299 | 7,433 | +1,134 | +1,135 |
| basemul | 16,134 | 15,974 | -160 | -168 |
| baseinv | 10,593 | 12,999 | +2,406 | +2,405 |
| **serialize** | 10,069 | 9,034 | **-1,034** | +911 |
| sample | 3,887 | 4,443 | +556 | +568 |
| **SUM** | 160,521 | 161,789 | **+1,268** | +3,389 |

Serialize is now a **win**, which is the property P17 identified as the reason
864 beat its official before any hash work.

## 7. Correctness

All seven oracle checks pass, and every package gate on the Pi: KAT sha256
`2ddfc810c4...64c3`, 64 round trips with tampered rejection, 13,824 canonical
cases, 11/11 ABI sentinel masks zero, 288/288 baseinv reject-and-clear,
zeroization `nonzero_after=0`, 44-file manifest.

## 8. Conclusions

1. **The serializer should not be written in assembly.**  It is at 90-100% of a
   *measured* issue floor; scheduling is worth under 10% on one entry point and
   nothing on the other.  Recorded so no later gate re-opens it on the
   assumption that 864's 7,751 assembly lines must be worth copying.
2. **The transpose-free `tbl4` restructure is rejected** at 3 cycles a pair.
3. **The Slothy A76 model under-rates `tbl` by 2x** and does not capture the
   pipe-mixing penalty.  Both matter for any future scheduling gate here.
4. Of the remaining +1,268, **baseinv is +2,406** — larger than the whole
   deficit, and the only item with a known, unexploited fix (no ILP split where
   864 uses 12x3).  Then hash +985 and inverse +1,134 against forward -2,618 and
   serialize -1,034.

Owed, and now badly stale: a fresh-date SUPERCOP run.  G9's +28.2% predates P12,
P13, P18 and this gate.

## Reproduce

```sh
gcc -O2 -march=native -D_DEFAULT_SOURCE pipeN.c -o pipeN && taskset -c 3 ./pipeN
# pipe2 operation throughput, pipe3 tobytes_small floor,
# pipe4 multi-source tbl, pipe5 the tbl4 restructure floor
```
