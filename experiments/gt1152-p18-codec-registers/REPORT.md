# P18 — The serializer, with the permutation done in registers

Branch `neon-1152`, parent `aa933296`.  Pi 5 core 3, GCC 14.2.0, perf_event PMU.

P17 established that NTRU+864 beat its official before any hash work because its
serializer was a *win* (-2,234), and named the mechanism: 864 never materialises
natural order, it permutes inside the register file.  1152's P12 codec
materialises a `uint16_t nat[1152]` and runs two passes, costing +10,909.

This gate rewrites the codec 864's way.  **Serialize went from +10,909 to +911
and the whole KEM from +7.9% to +1.8%, with encapsulation now faster than the
official.**

## 1. The tiling that makes it possible

Verified exhaustively in `generate_pairs.py`, which fails the build if any part
of it stops holding:

- The 36 Good-Thomas groups pair as **(g, g+9)** — 18 pairs covering all 36
  exactly once.
- For **every** pair and **every** lane k, the two leaves are consecutive,
  `PERM[8(g+9)+k] == PERM[8g+k] + 1`, and the first is **even**.
- A leaf is 4 coefficients, so a pair's lane is 8 consecutive natural
  coefficients, which the 12-bit format writes as **exactly 12 contiguous wire
  bytes** at `6m`.  With m even every block is 12-byte aligned.
- The 144 blocks therefore **tile the 1728-byte output exactly** — no overlap,
  no gap, every store independent.

This is the degree-4 dividend the campaign plan predicted and P12 only partly
collected.  864's 3-coefficient leaves are 4.5 wire bytes and never align, which
is why its `pack_full_top` needs 54 `tbl` and 24 `ext` just to route them.

## 2. The kernel

Per pair: 8 loads, one 8x8 int16 transpose, 8 twelve-byte stores.  No scratch.

The 8 rows are loaded in the order `(c0, c2)` of group g, `(c0, c2)` of group
g+9, then `(c1, c3)` of each.  After the transpose a lane reads out as the four
**even** natural coefficients followed by the four **odd** ones, which is
exactly the operand order the 12-bit encoding wants — the reordering is free
because it is only the order the loads are issued in.

The transpose is 24 `trn` in three levels, verified symbolically against NEON
`trn1`/`trn2` semantics before any code was written.  A transpose is an
involution, so the same network serves both directions.

Encoding one lane is then four instructions:

```c
uint32x4_t e = vmovl_u16(vget_low_u16(x));   /* even coefficients      */
uint32x4_t o = vshll_high_n_u16(x, 12);      /* odd coefficients << 12 */
y = e | o;                                   /* four 24-bit LE values  */
b = vqtbl1q_u8(y, {0,1,2, 4,5,6, 8,9,10, 12,13,14, ...});
```

`vshll_high_n_u16(x, 12)` does the widen and the 12-bit shift in one instruction,
so the 24-bit little-endian pair `(c_even | c_odd << 12)` — which *is* the wire
format — falls out with no masking and no shifting of bytes.

`tobytes_compare` no longer serializes to a buffer first: the 12 bytes are
already in a register, so they are XORed into the accumulator directly.  Every
block is visited and no branch depends on data.

## 3. Measured, against P12, same inputs, byte-identical outputs

`bench.c` checks agreement on all four entry points plus a corrupted-compare
case before timing.  `agreement: pass`.

| entry point | P12 | **P18** | saving | official |
|---|---:|---:|---:|---:|
| `tobytes_full` | 2,376 | **1,471** | -905 | 1,147 |
| `tobytes_small` | 1,822 | **990** | -832 | 1,147 |
| `tobytes_compare` | 2,608 | **1,431** | -1,177 | - |
| `frombytes` | 2,219 | **956** | -1,263 | 509 |

`tobytes_small` is now **faster than the official's `poly_tobytes`**, while
still paying for a permutation the official never performs.

## 4. Whole-KEM effect

Component profiler re-run after integration, `correctness=pass`,
`cross_implementation_wire_differences=0`, `instrumentation_equivalence=pass`.

| operation | official | GT | delta | was |
|---|---:|---:|---:|---:|
| keygen | 64,082 | 65,195 | +1.7% | +5.6% |
| **encaps** | 59,438 | **58,855** | **-1.0%** | +3.5% |
| decaps | 52,533 | 55,245 | +5.2% | +15.7% |
| **total** | **176,054** | **179,294** | **+1.8%** | +7.9% |

| category | official | GT | delta | was |
|---|---:|---:|---:|---:|
| hash | 84,624 | 85,767 | +1,143 | +1,853 |
| forward | 28,882 | 26,277 | **-2,604** | -2,607 |
| inverse | 6,301 | 7,436 | +1,136 | +1,124 |
| basemul | 16,139 | 15,971 | -168 | -171 |
| baseinv | 10,595 | 13,000 | +2,405 | +2,400 |
| **serialize** | 10,056 | 10,967 | **+911** | +10,909 |
| sample | 3,895 | 4,463 | +568 | +565 |
| **SUM** | 160,492 | 163,883 | **+3,391** | +14,073 |

## 5. Correctness

Differential against the G1 declared oracle, all seven P09 checks, first run:

```
full_exact_bytes                    17 cases, every int16 extreme
full_model_agrees_with_oracle       mod-q model vs the reference serializer
small_matches_full_on_its_domain    8 cases over (-q, q)
round_trip                          6 canonical polynomials, decode reports 0
canonical_rejection                 3,456 cases, every position x {q, q+1, 4095}
canonical_accepted                  unmodified buffer decodes with 0
tobytes_compare                     256 single-bit corruptions all return 1
```

Package gates on the Pi after integration, all green:

```
KAT sha256  2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3
test_kem            64 round trips + tampered rejection
test_canonical      cases=13824 failures=0
test_abi            11/11 sentinel masks 0x00000
test_baseinv_fail   288/288 reject, clear, alias-clear
test_zeroization    clear_calls=26 clear_bytes=37526 nonzero_after=0
SOURCE-MANIFEST     44 files verify
```

## 6. What is left

Serialize's ratio is now 1.091 against 864's 0.796, so roughly **2,960 cycles
remain** in this component — 864 reached its figure with 7,751 lines of
Slothy-scheduled assembly, and this gate is NEON intrinsics C.  The ranking of
the remaining +3,391:

| | cycles |
|---|---:|
| baseinv | +2,405 |
| hash | +1,143 |
| inverse | +1,136 |
| serialize | +911 |
| sample | +568 |
| basemul | -168 |
| forward | -2,604 |

**baseinv is now the largest single item**, and its cause is on record from
G5/P11: no ILP split, where 864 uses a 12x3 decomposition.

Owed: a fresh-date SUPERCOP run.  The +28.2% in the G9 record predates P12, P13
and this gate and is now badly stale.

## Reproduce

```sh
make check                                  # oracle differential, 7 checks
# on the Pi:
gcc -O3 -march=native -D_DEFAULT_SOURCE -I. -c pack.c -o new.o
gcc ... bench.c new.o old.o -o bench && taskset -c 3 ./bench
```
