# M5U-CF0 Cortex-A76 benchmark

## Method

- Host: Raspberry Pi 5, Cortex-A76, core 3.
- Compiler: GCC 14.2.0, `-O3 -march=armv8-a+simd`.
- Variants in one binary: frozen M5R-D, M5U-CF0, and one-instruction noop.
- Linux grouped `perf_event_open`: cycles and instructions.
- Three repetitions, both `BCN` and `NCB` order per repetition.
- 61 samples/order, 20,000 calls/sample: 366 samples per variant.
- Every process passes 64 disjoint and 64 exact-alias differentials.
- `get_throttled=0x0` before and after every repetition.

## Result

| Metric | M5R-D FR-0 | M5U-CF0 FR-ISO2 | Delta |
| --- | ---: | ---: | ---: |
| cycles p50 | 4230.810 | 4629.088 | +398.279 by independent medians |
| measured instructions p50 | 4453.001 | 4745.001 | +292.000 |
| IPC at medians | 1.0525 | 1.0250 | -0.0275 |

The paired candidate-minus-baseline cycle distribution is:

| Percentile | cycles/Forward |
| --- | ---: |
| p10 | 397.999 |
| p25 | 398.180 |
| p50 | 398.678 |
| p75 | 398.989 |
| p90 | 399.174 |

The three repetition paired-p50 deltas are `398.043`, `396.685`, and
`398.678` cycles.  The exact 292-instruction dynamic delta matches the static
ledger.  Noop subtraction reports function-body counts 4445 and 4737 because
it also subtracts the noop's `ret`; the full function ledgers are 4446 and
4738.

## Operation budget

One polynomial product uses two Forwards:

```text
2 * 398.678 = 797.356 cycles
BaseMul saving = 334.194 cycles
remaining before Inverse = -463.162 cycles
```

The explicit live-out absorption consumes 2.386 times the complete BaseMul
saving before any Inverse absorption is charged.
