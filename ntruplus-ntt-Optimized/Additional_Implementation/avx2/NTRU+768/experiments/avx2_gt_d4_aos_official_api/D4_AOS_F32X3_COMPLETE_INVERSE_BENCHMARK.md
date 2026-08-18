# Complete F32X3 inverse same-binary benchmark

Host: Intel Core Ultra 7 155H, CPU 3. Command:
`make d4-aos-f32x3-complete-inverse-bench`. The binary uses 10,001 paired samples,
balanced rotating order, 32 deterministic fixtures and 2,048 warmups. Inputs and the
Official in-place copy are prepared outside each timed kernel interval.

Representative post-repair run (median/p10/p90 invariant TSC):

| Endpoint | TSC |
| --- | ---: |
| Official | 498 / 490 / 506 |
| GT SoA ALGPOST-001 | 830 / 816 / 844 |
| Y1 complete | 876 / 866 / 888 |
| Y2 complete | 868 / 856 / 880 |

Paired medians were Y1-SoA +46, Y2-SoA +38, and Y2-Y1 -8 TSC. Across three additional
runs, Y1 medians were 874-886 and Y2 medians 868-880; Official remained 498.

The one bounded repair replaced the materialized CRT-difference chain with direct P/Q
factors. Pre-repair Y1/Y2 were about 1,084/1,082 TSC; post-repair representative values
are 876/868, saving about 208/214 TSC. It also reduced each symbol by 187 bytes.

The attempted `perf stat` run exposed hybrid `cpu_core`/`cpu_atom` aggregate counts for
the whole four-kernel process, not reliable isolated per-kernel PMU data. Retired
instructions, loads, stores and IPC are therefore recorded as unavailable rather than
attributed falsely. Static instruction and exact semantic-traffic counts are in the ASM
report.

Y2 remains in the specified 851-898 TSC band: insufficient return for this backend
rewrite. It is default-off and is not promoted.
