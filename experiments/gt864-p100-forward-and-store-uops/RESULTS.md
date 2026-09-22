# P100 — roadmap item 4, and what a store actually costs

Item 4 said NTRU+864's forward transform was **+61 ns on key generation, +32 on
encapsulation, +25 on decapsulation**, never examined, the cheapest unknown
left.  Two of those three claims are wrong.

## The prize is 26 ns, and it is the same in all three operations

Both implementations call `poly_ntt` **exactly twice** in key generation,
encapsulation and decapsulation, and neither specialises it at 864.  Three
different figures for one function called the same number of times was the tell;
they came from the sampling profiler, which P91 showed disagrees with itself by
5% on a 2,000 ns bucket.

Measured in place against in place (`bench_fwd.c`), which is how `kem.c` calls
both:

| `poly_ntt`, one call | M2 Pro | Cortex-A76 |
|---|---:|---:|
| GT | 850 cyc | 3,376 cyc |
| Official | **804** | 3,740 |
| ratio | **1.058** | **0.903** |

**+46 cycles a call on M2, -364 on A76.**  Two calls an operation: **+26.4 ns on
M2** against Official, and a 304 ns cushion on A76.  Not +61/+32/+25.

The earlier decomposition had GT *winning* this row, because it gave GT the
out-of-place form and wrote `c = m;` before the official one.  That copy is 70
cycles on M2 and 119 on A76.  P92 caught the same fault in the inverse; it stood
in `ntt` until now.  `gt864-p99-vs-official-two-machines/RESULTS.md` is corrected:
GT's decapsulation arithmetic is **+9.8% on M2** and **-7.1% on A76**, not
+4.5%/-8.6%.

## A store costs per 16 bytes, not per instruction

P96 priced a store at about 0.45 cycles on M2 and left it ambiguous whether that
is per instruction or per byte.  `st.S` writes the same 1,024 bytes four ways:

| form | store instructions | M2 cyc |
|---|---:|---:|
| 64 x `STR Q` | 64 | 31.8 |
| 32 x `ST1 {2 regs}` | 32 | 31.8 |
| 21 x `ST1 {3 regs}` + 1 | 22 | 31.8 |
| 16 x `ST1 {4 regs}` | 16 | 31.8 |

Identical.  **The unit is the 16-byte store µop**; a multi-register `ST1` is n of
them, and M2 sustains two per cycle (32.2 B/cyc).  So merging stores into wider
`ST1` forms buys nothing, and the reason `invntt16`'s 128 `STRH` per call are
expensive is that each occupies a whole 16-byte µop to move two bytes -- **87.5%
of the bandwidth wasted**, not the instruction count.

Recounting both transforms in µops rather than instructions (864 coefficients is
1,728 bytes, so one full output pass is 108 µops):

| store µops | GT | Official | ratio | GT passes |
|---|---:|---:|---:|---:|
| forward | 257 | 220 | 1.17 | 2.4 |
| **inverse** | **1,152** | **220** | **5.24** | **10.7** |

| | excess µops | x 0.5 cyc | measured gap |
|---|---:|---:|---:|
| inverse | +932 | +466 | **+375** |
| forward | +37 | +18.5 | +46 |

**The inverse's store excess is larger than its entire performance gap** -- GT's
12% multiply saving claws part of it back.  The forward's explains 40% of a much
smaller gap; the rest is diffuse (loads +0.27, adds +0.21, lane moves +0.18,
stores +0.13 per coefficient) with no concentrated lever.

## Verdict on item 4

**Close it.**  GT's forward transform is within 17% of Official on store µops,
already has **better IPC than Official on both machines** (M2 4.77 against 4.34,
A76 1.20 against 0.93), and its 563 extra instructions are spread across four
classes.  There is no store-shaped win here, the prize is 26 ns rather than 61,
and it is now the smallest item on the roadmap rather than the cheapest.

Retired-instruction counts are PMU-exact (`pmu_fwd.c`, `perf stat -e
instructions`, 20,000 iterations, empty-mode baseline subtracted): GT forward
4,056 per call against Official's 3,493; GT inverse 7,883 against 4,581.  The
static censuses reproduce them to 0.2-0.6%.
