# GT1152-P12 — the NEON codec

P11 measured serialization at 70% of the whole GT deficit. This replaces the
plain-C codec with NEON.

**Total gap against the official: 44,106 → 20,389 cycles. GT goes from +25.0%
to +11.6%.**

```sh
cc -O2 -std=c11 -march=armv8-a+simd -I. harness.c pack.c -o harness
python3 verify.py      # the same seven gates as G7
```

## Result

| operation | official | GT before | GT after | change | vs official |
|---|---:|---:|---:|---:|---:|
| keygen | 64,071 | 77,276 | 69,684 | −7,592 | +20.6% → **+8.8%** |
| encaps | 59,508 | 71,021 | 63,317 | −7,704 | +19.3% → **+6.4%** |
| decaps | 52,525 | 71,925 | 63,492 | −8,433 | +37.0% → **+20.9%** |
| **total** | **176,104** | **220,222** | **196,493** | **−23,729** | **+25.0% → +11.6%** |

Per call:

| | official | before | after |
|---|---:|---:|---:|
| `poly_tobytes` | 1,148 | 6,189 | **2,367** |
| `poly_tobytes_small` | — | 3,655 | **1,820** |
| `poly_tobytes_compare` | — | 3,175 | **2,593** |
| `poly_frombytes` | 505 | 4,205 | **2,189** |

All seven G7 gates still pass, including the 3,456-case canonical rejection
sweep; KAT is still byte-identical, and `test_kem`, `test_canonical`,
`test_abi` and `test_baseinv_fail` all pass on the Pi.

## What was actually wrong

A gather. The old code indexed the coefficient array through a permutation
table one coefficient at a time, and **AArch64 NEON has no gather** — so every
permuted access was a scalar load, 1,152 of them per call.

## The right primitive

A Good-Thomas group is 32 contiguous int16: four components by eight lanes at
`GT[32g .. 32g+31]`. In natural order a leaf is four *contiguous* coefficients.
So

```
LD4 {v0.h, v1.h, v2.h, v3.h}[k], [leaf]
```

reads one leaf's four components straight into lane `k` of the four component
vectors, and `ST4` does the reverse. **Eight of those move a whole group** — no
transpose, no TBL.

That is the degree-4 alignment advantage from G3a made concrete: four int16 is
exactly one lane-indexed LD4/ST4. NTRU+864's three would need LD3/ST3 and still
not align for 12-bit packing, which is why its codec is 7,751 lines.

The 12-bit codec itself is then sequential over natural order, with `LD3`/`ST3`
on bytes, exactly as the official lane does it.

## A fusion that bought nothing

Reduction was then folded into the scatter so the scratch is traversed twice
instead of three times. Measured: 196,109 before, 196,493 after — **neutral,
slightly worse, inside run-to-run noise**. The extra pass was never the
bottleneck. The fused form is kept because it is fewer passes, not because it
is faster.

## Where the remaining 20,389 goes

| category | official | GT | delta | share |
|---|---:|---:|---:|---:|
| serialize | 10,074 | 20,998 | +10,924 | 53.6% |
| sample/misc | 3,885 | 10,415 | +6,530 | 32.0% |
| baseinv | 10,595 | 13,004 | +2,409 | 11.8% |
| hash | 84,948 | 86,653 | +1,705 | 8.4% |
| inverse NTT | 6,294 | 7,412 | +1,118 | 5.5% |
| basemul | 16,136 | 15,971 | −165 | −0.8% |
| **forward NTT** | 28,886 | **26,275** | **−2,611** | **−12.8%** |

The forward transform is still ahead, and the hash gap has shrunk to 1,705 —
most of what P11 attributed to hash was really the serialization inside
`hash_g_fr0`.

Serialization remains the largest item. The floor is not zero: the official
performs **no permutation at all**, because its transform already leaves
coefficients in natural order. 288 lane-indexed LD4/ST4 per call is a cost GT
must pay and the official does not.

## Next, by measurement

1. **sampling leaves**, +6,530 — `poly_cbd1` and `poly_sotp_decode` are still
   bit-serial scalar loops against the official's `cbd.s`
2. **codec again**, +10,924 — but expect diminishing returns against a
   permutation-free baseline
3. **baseinv**, +2,409 — the missing 12×3 ILP split from G5
