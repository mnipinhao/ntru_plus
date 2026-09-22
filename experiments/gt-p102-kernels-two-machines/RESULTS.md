# P102 — the kernel comparison, fixed in both directions, for 864 and 1152

Item 1's **+157 ns** came from the sampling profiler and had never been timed
directly.  P100 established that such figures have been wrong by 2x, so this
re-measures it -- and, on the way, corrects P100 itself.

## The harness was wrong twice, in opposite directions

`kem.c` is the only authority on aliasing, and both sides must be given exactly
what it gives them.

- P92 caught the first fault: the harness wrote `c = m;` before Official's
  `poly_invntt_scale`, which its `kem.c` never does -- it calls it in place.
- P100 then removed the copy before Official's **first decapsulation
  `poly_ntt`**, which its `kem.c` **does** do.  Official has no out-of-place
  form and `m` is still needed by `poly_sotp_decode`, so its code reads
  `f = m; poly_ntt(&f);`.  GT's `poly_ntt(&f, &m)` genuinely saves that copy.

So the forward transform has to be priced **twice**: in place, as key generation
and encapsulation call it on both sides, and as decapsulation's first call,
where only Official copies.  `bench_kernels.c` does that.

**P100's claim that "three different figures for one function was the tell" was
wrong.**  The profiler's keygen/encaps/decaps split was real; only its
magnitudes were off.  The corrected M2 figures for `poly_ntt`: **1.06 in key
generation and encapsulation, 0.94 in decapsulation.**

Net effect on 864's decapsulation arithmetic, M2: P99 said +4.5%, P100 "fixed"
it to +9.8%, and the truth before P29 was **+7.2%**.  The two errors had been
roughly cancelling.

## NTRU+1152, cycles per call

| kernel | calls in decap | GT M2 | Off M2 | x | GT A76 | Off A76 | x |
|---|---:|---:|---:|---:|---:|---:|---:|
| **frombytes** | **3** | **250** | **194** | **1.29** | **618** | **485** | **1.27** |
| basemul_rinv / scale | 1 | 742 | 693 | 1.07 | 2,525 | 2,534 | 1.00 |
| invntt (+crepmod3) | 1 | 1,472 | 1,421 | 1.04 | 5,486 | 6,231 | **0.88** |
| ntt in place | 1 | 1,109 | 1,068 | 1.04 | 4,352 | 4,785 | **0.91** |
| ntt, decap's first | 1 | 1,109 | 1,184 | **0.94** | 4,353 | 4,940 | **0.88** |
| sub | 1 | 114 | 112 | 1.01 | 191 | 259 | **0.74** |
| basemul | 1 | 694 | 837 | **0.83** | 3,125 | 3,391 | **0.92** |
| tobytes_small | 1 | 229 | 276 | **0.83** | 694 | 1,138 | **0.61** |
| tobytes (full) | 1 | 344 | 276 | 1.24 | 1,358 | 1,138 | 1.19 |
| sotp_decode | 1 | 195 | 207 | **0.94** | 473 | 482 | 0.98 |
| cbd1 | 1 | 170 | 178 | **0.95** | 427 | 471 | **0.91** |
| verify | 1 | 77 | 77 | 1.00 | 222 | 222 | 1.00 |
| **decapsulation** | | **7,004** | **6,912** | **+1.3%** | **25,060** | **27,046** | **-7.3%** |

## Item 1 is +54 ns, and it is not the compare

| 1152 decapsulation, serialization only | M2 | A76 |
|---|---:|---:|
| `frombytes` x3 | **+168 cyc (+48 ns)** | **+399 cyc (+166 ns)** |
| `tobytes` full x1 | +68 | +220 |
| `tobytes_small` x1 | -47 | -444 |
| **total** | **+189 cyc (+54 ns)** | **+175 cyc (+73 ns)** |

**Not +157, and the compare is already gone** (`ecb6d5e1`).  What is left is
almost entirely **`poly_frombytes`**, which the roadmap never named.

Its ratio is **1.29 on M2 and 1.27 on A76** -- nearly identical.  Everything
else in this campaign flips sign between the machines; a ratio that does not is
a work difference, not a microarchitectural one, so fixing it helps **both**.

PMU retired instructions (`pmu_fb.c`, 20,000 iterations, empty-mode baseline
subtracted): **GT 3,098 per call against Official's 885, a factor of 3.5.**  The
cause is visible in `pack.c`: GT does an **8x8 `transpose8` per 64 coefficients**
to place the bytes in Good-Thomas order, which Official never needs.  It is the
index permutation again, this time in the unpack direction -- the same cost the
inverse pays on output.

`tobytes_small` is a GT win of the same size in the other direction (0.83/0.61),
so the serializer rewrite did land; it is the *reader* that was never done.

## NTRU+864, after P29

| kernel | GT M2 | Off M2 | x | GT A76 | Off A76 | x |
|---|---:|---:|---:|---:|---:|---:|
| frombytes | 286 | 274 | 1.04 | 708 | 730 | 0.97 |
| **invntt (+crepmod3)** | **1,264** | **1,050** | **1.20** | **4,768** | **4,572** | **1.04** |
| ntt in place | 852 | 804 | 1.06 | 3,387 | 3,739 | 0.91 |
| ntt, decap's first | 851 | 909 | 0.94 | 3,383 | 3,854 | 0.88 |
| tobytes (full) | 340 | 274 | 1.24 | 1,155 | 1,084 | 1.07 |
| tobytes_small | 244 | 274 | 0.89 | 620 | 1,084 | 0.57 |
| **decapsulation** | **5,816** | **5,565** | **+4.5%** | **20,454** | **21,811** | **-6.2%** |

P29 shows up exactly where predicted: 864's inverse was 1,416 cycles on M2 and
is now 1,264 (**-152**), and 4,466 on A76 and is now 4,768 (**+302**).

864's `frombytes` is 1.04/0.97 -- 1152's 1.29/1.27 is specific to 1152.
