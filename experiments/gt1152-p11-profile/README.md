# GT1152-P11 — where the 28% actually goes

The question this gate was built to answer: **with the hash left unoptimized,
how much is polynomial multiplication actually worth?**

The answer is not what either of us expected. **Polynomial multiplication is
already at parity.** The deficit is serialization.

```sh
./build.sh && taskset -c 3 ./profile_harness 0 > profile.log
```

Pi 5 Cortex-A76 core 3, `perf_event` PMU cycles, 41 samples per point.
`correctness=pass`, `cross_implementation_wire_differences=0` — both
implementations produce byte-identical pk, sk and ct — and
`instrumentation_equivalence=pass`.

## Whole operations

| operation | official | GT | delta |
|---|---:|---:|---:|
| keygen | 64,092 | 77,276 | +13,184 (+20.6%) |
| encaps | 59,537 | 71,021 | +11,484 (+19.3%) |
| decaps | 52,487 | 71,925 | +19,438 (+37.0%) |
| **total** | **176,116** | **220,222** | **+44,106 (+25.0%)** |

## Where the 44,106 cycles go

| category | official | GT | delta | share of gap |
|---|---:|---:|---:|---:|
| **serialize** | 10,054 | 40,804 | **+30,750** | **69.7%** |
| sample/misc | 3,891 | 10,391 | +6,500 | 14.7% |
| hash | 84,781 | 90,636 | +5,855 | 13.3% |
| **polynomial multiplication** | **61,921** | **62,708** | **+787** | **1.8%** |

Polynomial multiplication here is forward NTT, inverse NTT, basemul and
baseinv combined.

## The Good-Thomas transform is winning

| component | official | GT | delta |
|---|---:|---:|---:|
| `poly_ntt` | 28,878 | 26,286 | **−2,592** |
| basemul family | 16,154 | 15,974 | −180 |
| inverse NTT | 6,294 | 7,439 | +1,145 |
| `poly_baseinv` | 10,595 | 13,009 | +2,414 |

**The forward transform is 2,592 cycles faster than the official's.** That is
the whole point of the Good-Thomas port, and it works. basemul is a wash. The
inverse and baseinv give a little back, and both have known causes — the C tail
at 4096 MACs (G6b) and the missing 12×3 ILP split (G5).

## What is actually slow

| component | official | GT | delta |
|---|---:|---:|---:|
| `poly_frombytes` | 2,021 | 16,820 | **+14,799** (8×) |
| `poly_tobytes_small` | — | 14,620 | +14,620 |
| `poly_tobytes_compare` | — | 3,175 | +3,175 |
| `poly_tobytes` | 8,033 | 6,189 | −1,844 |
| `poly_cbd1` | 1,966 | 4,986 | +3,020 |
| `poly_sotp_decode` | 508 | 3,277 | +2,769 |

Both are exactly the code Milestone 1 deliberately left as plain C: the codec
under decision **D5**, and `support.c`'s sampling leaves. The official has
`pack.s` and `cbd.s` in NEON.

Note `poly_tobytes` itself is *faster* than the official's — the slow paths are
`frombytes` (a per-coefficient table lookup plus the canonical check) and
`tobytes_small`, which the official has no equivalent of because it calls one
serializer everywhere.

## Reading the hash row honestly

GT's `hash_g_fr0` (25,808) serializes *inside* the hash boundary, so part of
that number is really serialization. Comparing hash paths as a whole: official
`hash_g` 39,629 against GT `hash_g` 19,713 + `hash_g_fr0` 25,808 = 45,521, so
+5,892. `hash_f` and `hash_h` are within noise of each other, as expected —
both implementations use a plain-C Keccak with identical transcript sizes.

## What this means for the plan

**Further polynomial-multiplication work buys almost nothing.** At +787 cycles
across four components, there is no meaningful headroom left there, and the
forward transform is already ahead.

The ordering that follows from the measurement:

1. **Codec** — +30,750, and it is plain C against NEON assembly. Nothing here
   requires new mathematics; G3a already measured the layout and G7 already has
   an exact byte oracle to check against.
2. **Sampling leaves** — +6,500, same situation, smaller.
3. **Hash fusion** — +5,855 here, but the 864 campaign showed the fixed-size
   specialization is worth far more than the GT-vs-official delta suggests: it
   removes work both implementations currently do.

## Limits

- Component sums do not reconcile exactly with whole-operation totals: about
  15,500 cycles per implementation sit in uninstrumented glue — `kem.c` itself,
  direct `shake256` calls, `verify`, `memcpy`, `randombytes`. The residual is
  nearly identical for both (15,469 official, 15,683 GT), which is why the
  attribution is trustworthy for comparison.
- Medians of 41 samples, single host, single run. No claim of reproducibility
  across reboots.
