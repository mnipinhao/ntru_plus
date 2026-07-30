# NTRU+768 AVX2 TSC diagnostic on Core Ultra 7 155H

Date: 2026-07-30

This run compares KPQC Final, Official Main, and the Good–Thomas (GT)
prototype on the same x86 host.  It is a development diagnostic, not a
performance benchmark or adoption gate: hardware `cycles` were unavailable
(`perf_event_paranoid=4`), the host used the `powersave` governor, and the
measurements below use invariant-TSC ticks.

## Reproducibility

- Host: Intel Core Ultra 7 155H, Linux, process pinned to P-core CPU 3
  (SMT sibling CPU 4).
- Compiler: Clang 22.1.8 (Fedora builder).
- Common flags:
  `-O3 -march=x86-64-v3 -mtune=generic -mprefer-vector-width=256`.
- GT source: branch `avx2-gt-ntt-prototype`, commit `e9d99541`.
- Official source: `ntruplus/ntruplus` Main commit `0c249d5828b90e8d`.
- Microbench: 100 warmups, 1,000 calls/sample, 101 samples/process,
  seven order-balanced process runs.
- KEM bench: 300 warmups, 3,001 samples/process, seven rotated-order runs.
- Paired keygen bench: KPQC and GT alternated inside one process, 500 warmups,
  5,001 samples/run, seven runs.

All three KEM binaries passed an encapsulate/decapsulate shared-secret
self-check before timing.  The GT native island additionally passed 128
deterministic keypair comparisons, 16 full-KEM/public-stream comparisons, and
the exhaustive native-pack checks.  Both AVX2 microbench binaries passed their
full validation suites.

The numbers below are serialized invariant-TSC ticks.  Each main number is the
median of seven process medians.  Percentage comparisons use the median of
same-round ratios to reduce cross-process frequency drift.  They are retained
for bottleneck attribution only; all rankings must be rerun with hardware
`cycles` before making an optimization decision.

## Forward NTT

| Forward producer | Output/consumer contract | TSC ticks | Relative to KPQC |
| --- | --- | ---: | ---: |
| KPQC Final `ntt` | production NTT layout | 528 | baseline |
| Official Main `ntt` | Official in-place production layout | 492 | 7.1% faster |
| GT native lazy | GTN-L3, direct native keygen/baseinv consumer | 508 | 3.8% faster |
| GT native centered | centered native contract | 561 | 6.2% slower |

The Official in-place call is timed without an adapter copy.  The GT lazy row
is the selected keygen producer
`gt-ntt-wide-fused-delayed-row2q2-native-lazy-pipelined-asm`; it is not a
drop-in production-layout NTT.  Its advantage is therefore real only when the
next consumer remains in the GT native island.

## Full polynomial multiplication

| Pipeline | TSC ticks | Relative |
| --- | ---: | ---: |
| KPQC Final | 1,907 | baseline |
| Official Main | 1,735 | 8.5% faster than KPQC |
| GT U2 centered/queued/fused | 2,453 | 27.9% slower than KPQC; 43.9% slower than Official |

All complete pipelines were validated against the canonical schoolbook
product.  Official Main uses its native `poly_basemul_scale` plus
`poly_invntt_scale` contract; no standalone format conversion is included.

The GT full-path component medians were:

| GT component | TSC ticks |
| --- | ---: |
| One centered SoA Forward | 592 |
| SoA basemul | 337 |
| Fused SoA inverse | 1,016 |

Using `2*Forward + basemul + inverse` as an approximate decomposition, the two
forwards account for 47%, basemul 13%, and inverse 40%.  The inverse is now the
largest single kernel and the clearest blocker to making GT competitive for
full polymul.  The 508-tick lazy Forward cannot be substituted into this row:
it has the GTN-L3 keygen contract, whereas this complete pipeline consumes the
centered SoA contract.

## KEM and native GT keygen island

Independent three-binary KEM runs produced these median-of-medians:

| Binary | Keygen | Encap | Decap |
| --- | ---: | ---: | ---: |
| KPQC Final | 15,234 | 19,619 | 12,040 |
| Official Main | 15,240 | 19,242 | 12,289 |
| GT native-keygen binary | 15,578 | 19,057 | 12,270 |

The independent-process results are noisy enough that these small differences
must be treated as ties.  Same-round paired ratios put Official/KPQC at 0.992
for keygen, 1.001 for encap, and 1.003 for decap.

The GT binary replaces only keypair generation.  Its encapsulation and
decapsulation remain the branch's production path and are controls, not GT
encap/decap implementations.  The decisive same-process, alternating-order
keygen run measured:

| Keygen implementation | TSC ticks |
| --- | ---: |
| production/KPQC | 14,814 |
| GT native island | 14,846 |

The median GT/KPQC ratio was 1.0022: GT is 0.22% slower.  This is effectively a
tie, but it means the current native island has not yet earned adoption on this
host despite its faster lazy Forward.

## Provisional interpretation

1. The GT lazy Forward remains the most promising GT keygen producer in this
   diagnostic.
2. The paired TSC keygen result is too close to justify replacing production;
   rerun KPQC and GT with hardware `cycles`.
3. Official Main is the next production-layout Forward/full-polymul reference
   to compare using hardware `cycles`.
4. If the hardware-cycle breakdown confirms this attribution, GT inverse
   should precede further basemul scheduling work.

Raw artifacts are under the ignored directory
`results/nuc-core-ultra-7-155h-20260730-e9d99541/`.
