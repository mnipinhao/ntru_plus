# GT1152-P13 — NEON sampling leaves

P12 left sampling at 32% of the remaining gap. This closes it.

**Total gap against the official: 20,434 → 14,154 cycles. GT goes from +11.6%
to +8.0%.**

```sh
cc -O2 -std=c11 -march=armv8-a+simd -I. diff.c support.c support_scalar.c -o diff && ./diff
```

## Result

| operation | official | original | +codec | +sampling | vs official |
|---|---:|---:|---:|---:|---:|
| keygen | 64,038 | 77,276 | 69,684 | 67,666 | +20.6% → **+5.7%** |
| encaps | 59,543 | 71,021 | 63,317 | 61,676 | +19.3% → **+3.6%** |
| decaps | 52,478 | 71,925 | 63,492 | 60,872 | +37.0% → **+16.0%** |
| **total** | **176,059** | **220,222** | **196,493** | **190,214** | **+25.0% → +8.0%** |

Per call:

| | official | before | after |
|---|---:|---:|---:|
| `poly_cbd1` | 491 | 1,248 | **451** ✓ faster |
| `poly_sotp_encode` | 507 | 1,275 | **483** ✓ faster |
| `poly_sotp_decode` | 508 | 3,286 | 1,343 |
| `poly_sub` | 276 | 286 | 276 |
| `poly_triple` | 317 | 288 | **285** ✓ faster |

`poly_cbd1` and `poly_sotp_encode` are now **faster than the official's
assembly**. `poly_sotp_decode` is still 2.6×, and is the one place left.

## The trick: broadcast the byte, not the bit plane

The old code was bit-serial with a carried dependency:

```c
for (j = 0; j < 8; j++) { r[8*i+j] = (t1 & 1) - (t2 & 1);
                          t1 >>= 1; t2 >>= 1; }
```

The obvious vectorisation — extract bit plane `j` across sixteen bytes at once —
**is wrong for this layout**. Output coefficient `8i+j` needs byte `i`'s bits
consecutive, so the bit planes would have to be interleaved eight ways, and NEON
stops at ST4.

Broadcasting the other way avoids the interleave entirely:

```c
vandq_u16(vtstq_u16(vdupq_n_u16(b), {1,2,4,...,128}), one)
```

One byte duplicated across eight lanes, tested against the bit mask, gives
exactly the eight consecutive output coefficients of byte `i`. No transpose, no
interleave — three instructions per eight coefficients.

## Why `sotp_decode` is still 2.6×

It needs the reverse: pack eight 0/1 lanes back into one message byte, which is
`vaddvq_u16(vmulq_u16(bits, mask))` — a **cross-lane horizontal reduction** per
output byte, 144 of them, each with the latency that implies. The official's
`cbd.s` presumably batches this differently. It costs +835 cycles on one decaps
call, so it is now a small item.

## Verification

- 200-case differential against the plain-C originals, covering `cbd1`,
  `sotp_encode`, `sotp_decode` in both its success and arbitrary-input modes,
  `sub` and `triple`.
- On the Pi: KAT still byte-identical, `test_kem`, `test_canonical` (13,824
  cases), `test_abi` and `test_baseinv_fail` (288/288) all pass.

## Where the remaining 14,154 goes

| category | official | GT | delta | share |
|---|---:|---:|---:|---:|
| serialize | 10,086 | 21,024 | +10,938 | 77.3% |
| baseinv | 10,599 | 12,998 | +2,399 | 16.9% |
| hash | 84,764 | 86,660 | +1,896 | 13.4% |
| inverse NTT | 6,299 | 7,415 | +1,116 | 7.9% |
| sample/misc | 3,906 | 4,475 | +569 | 4.0% |
| basemul | 16,130 | 15,964 | −166 | −1.2% |
| **forward NTT** | 28,882 | **26,286** | **−2,596** | **−18.3%** |

The attribution now reconciles to within 2 cycles of the whole-operation
measurement, so nothing material is hiding in uninstrumented glue.

Serialization is still 77% of what is left, and its floor is not zero: the
official performs **no permutation at all**, because its transform already
leaves coefficients in natural order. That is a structural cost GT pays and the
official does not.
