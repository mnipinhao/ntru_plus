# F32X3 five-layer NTT32 diagnostic benchmark

Boundary measured: native F32X3 input to exact post-L4/pre-DFT3 state. This is not a
full inverse and is not directly comparable with Official or GT SoA inverse results.

- Host: Intel Core Ultra 7 155H, CPU 3 affinity.
- Profile: same binary, 32 deterministic fixtures, alternating fixture order, 4,096
  warmups and 20,001 paired invariant-TSC samples.
- Stable runs: median 960/962 TSC, p10 950/950, p90 972/974.
- Initial run: median 964, p10 952, p90 1386; retained as system-noise evidence.
- Symbol size: 19,643 bytes; semantic state: 1,536 bytes.
- Compact variant: not created; size is below 20 KiB and repeated warm runs do not show
  persistent frontend dispersion.
- PMU: unavailable. `perf_event_paranoid=2` rejected CPU events and hybrid-PMU routing;
  retired instructions, loads/stores and IPC are therefore not claimed as measurements.

Reproduce with `make d4-aos-f32x3-ntt32-ct-merged-bench`.

## Matched Y0/Y1/Y2 attribution

Same binary, CPU 3, 10,001 paired/interleaved samples:

| Boundary | Median | p10 | p90 |
| --- | ---: | ---: | ---: |
| empty control | 24 | 22 | 24 |
| 1536-byte copy | 38 | 36 | 52 |
| Y0 L0-L2 only | 626 | 618 | 634 |
| Y0 L3-L4 only | 386 | 378 | 394 |
| Y0 full | 960 | 948 | 978 |
| Y1 Yang full | 456 | 448 | 472 |
| Y2 compact Yang | 460 | 452 | 472 |
| matched GT SoA NTT32 | 480 | 468 | 494 |

Paired Y1-Y0 is median -504 TSC (p10 -520, p90 -486). Paired Y2-Y1 is median
+4 TSC (p10 -14, p90 +18). Separate L0-L2/L3-L4 calls include two call/control
boundaries and do not sum directly to the fused measurement.

The measured NTT32 ceiling remains 650-700 TSC. Y1 leaves approximately 194-244 TSC
inside that stage budget for compact DFT3 and fixed terminal work, and is 24 TSC faster
than the closest exposed GT SoA pre-DFT3 boundary.
