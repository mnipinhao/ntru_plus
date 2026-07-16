# AVX2 GT prototype benchmark results

## 2026-07-15 Ryzen 7 9700X preliminary run

This run compares the verified intrinsic GT forward transform with the hybrid
stage-3+4+5 ASM SoA prototype and the existing production AVX2 implementation.
It is a development measurement, not a release claim.

Environment:

- CPU: AMD Ryzen 7 9700X, family 26 model 68, microcode `0xb40401c`.
- OS: Fedora, Linux `7.1.0-0.rc1.260501g26fd6bff2c050.13.fc45.x86_64`.
- Compiler: GCC 16.1.1 20260703.
- Flags: `-march=x86-64-v3 -mtune=znver5 -mprefer-vector-width=256`.
- Pinned CPU: 2; SMT sibling: 10.
- Governor: `performance`; frequency boost: enabled.
- Harness: 64 rotating input sets, 100 warmups, 1000 calls/sample,
  101 TSC samples, and 100000 calls/perf measurement.
- Timestamp: `20260715T050453Z`.

Correctness gates passed before measurement: production NTRU+768 KEM test,
GT boundary/differential/layout tests, benchmark NTT round-trip and schoolbook
polynomial multiplication validation, and AVX2 linked-binary audit.

### Forward NTT comparison

The TSC values are serialized invariant-TSC ticks per call.  Hardware cycles
and instructions are `perf stat` counts divided by 100000 calls.

| Implementation | TSC median | p10 | p90 | p99 | Hardware cycles/call | Instructions/call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Production AVX2 `ntt` | 444 | 441 | 448 | 454 | 663.44 | 2333.29 |
| GT intrinsic `gt-ntt` | 1476 | 1457 | 1483 | 1488 | 2146.75 | 9345.29 |
| GT hybrid ASM SoA | 983 | 980 | 989 | 1003 | 1451.39 | 6062.01 |

Relative to the GT intrinsic baseline, the hybrid ASM lowers median TSC ticks
by 33.4%, hardware cycles by 32.4%, and retired instructions by 35.1%.
It is still 2.21x the production forward NTT median, so the remaining intrinsic
frontend/stage-1+2 and the different GT decomposition are now the main work,
not evidence that this prototype should replace production.

### Existing production pipeline context

| Operation | TSC median | p10 | p90 | p99 |
| --- | ---: | ---: | ---: | ---: |
| Production basemul | 319 | 316 | 320 | 329 |
| Production inverse NTT | 436 | 434 | 442 | 447 |
| Production full polynomial multiplication | 1656 | 1646 | 1664 | 1676 |

At this timestamp there was no GT SoA basemul, inverse NTT, or full-polymul
number.  The 2026-07-16 section below adds the intrinsic SoA basemul baseline;
inverse and full-polymul remain open.

### Measurement limitations

- Boost was enabled, so invariant-TSC ticks and unhalted hardware cycles differ.
- The process was pinned to CPU 2, but sibling CPU 10 was not reserved or
  disabled.
- This result should be repeated with boost controlled and both SMT siblings
  isolated before making promotion or microarchitecture claims.

## 2026-07-16 SoA basemul intrinsic baseline

This run adds `gt-basemul-soa` to the same harness and host.  Its inputs are
prepared GT forward outputs; forward transforms, lambda generation, and layout
conversion are outside the measured region.  Correctness includes generated-
table checking, 192-lane mapping comparison, boundary and 200-random quartic
differential tests, and forward-NTT-to-basemul composition tests.

Environment differences from the previous run: timestamp
`20260716T013219Z`; all other relevant CPU, compiler, flags, core, governor,
boost, corpus, and sample settings are unchanged.

| Pointwise implementation | TSC median | p10 | p90 | p99 | Hardware cycles/call | Instructions/call | Branches/call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Production AVX2 basemul | 318 | 316 | 320 | 327 | 480.43 | 1839.52 | 24.19 |
| GT 16-block SoA intrinsic | 318 | 316 | 319 | 328 | 478.83 | 1662.35 | 18.19 |

The SoA intrinsic matches the production TSC median, lowers measured hardware
cycles by 0.3%, and retires 9.6% fewer instructions.  Cache references are
effectively equal in this run (72.58 versus 72.58 per call).

This is evidence that the four-vector SoA representation can feed quartic
basemul without a transpose penalty.  It is not yet a final schedule: GCC emits
a 773-byte symbol with a 72-byte frame and YMM spill/reload traffic.  A hand-
scheduled zero-spill kernel is the next pointwise comparison, and no GT full-
polymul claim is possible until the inverse consumes SoA directly.

## 2026-07-16 SoA direct-consumer inverse and full pipeline

This run adds an intrinsic inverse that consumes the pointwise SoA output
directly.  There is no row-bitrev buffer or standalone 768-coefficient layout
pass.  The measured inverse includes inverse NTT32, inverse DFT3, untwist,
normalization, branch merge, 4x8 coefficient-to-quartic transpose, and canonical
output stores.  The full GT operation includes two hybrid ASM SoA forward
transforms, SoA basemul, and this inverse.

Environment is the same Ryzen 7 9700X setup above.  Timestamp is
`20260716T021414Z`; CPU 2 is pinned, governor is `performance`, boost remains
enabled, and SMT sibling CPU 10 is not isolated.  Validation passed the scheme
test, generated-table checks, inverse differential and in-place tests,
forward/inverse round trips, schoolbook polynomial multiplication, and linked
AVX2-only audit.

| Operation | TSC median | p10 | p90 | p99 | Hardware cycles/call | Instructions/call | Branches/call | Cache refs/call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Production inverse | 432 | 432 | 438 | 441 | 651.01 | 2600.29 | 44.21 | 49.40 |
| GT SoA direct inverse | 1013 | 1012 | 1019 | 1024 | 1494.44 | 4621.31 | 42.21 | 49.23 |
| Production polynomial multiplication | 1652 | 1644 | 1659 | 1669 | 2413.69 | 8984.67 | 144.31 | 267.53 |
| GT SoA polynomial multiplication | 3323 | 3318 | 3328 | 3341 | 4827.90 | 18285.97 | 132.30 | 197.22 |

The direct inverse is 2.35x the production TSC median and 2.30x its hardware
cycles.  The full GT path is 2.01x the production TSC median and 2.00x its
hardware cycles.  Therefore the SoA representation now has a complete measured
pipeline, but it does not meet the promotion threshold.

The inverse development sequence also demonstrates why the reduction and
store schedule matter:

| Inverse prototype | TSC median | Full GT polynomial multiplication |
| --- | ---: | ---: |
| Correctness-first, widened Barrett after every layer | 4051 | 6342 |
| Five lazy layers, packed boundary checkpoints | 1465 | 3780 |
| Packed checkpoints plus 4x8 quartic block stores | 1013 | 3323 |

The final variant lowers inverse TSC by 75.0% relative to the first correct
version.  GCC 16 emits a 2681-byte inverse symbol.  It reserves 1480 bytes
explicitly and uses a 120-byte red-zone window; the semantic row scratch is
1536 bytes and two vector constants are spilled.  The next valid comparison is
a hand-scheduled inverse split into lazy NTT32, inverse DFT3 checkpoint, and
untwist/merge/final-store regions, not another layout conversion pass.

## 2026-07-16 hand-scheduled inverse NTT32 region

This run replaces only the direct-SoA inverse NTT32 region with handwritten
AVX2.  Inverse DFT3 and postprocess remain intrinsic.  Timestamp is
`20260716T030551Z`; the Ryzen 7 9700X environment, CPU 2 pinning, performance
governor, enabled boost, non-isolated sibling CPU 10, GCC 16.1.1, corpus, and
sample sizes match the preceding runs.

The ASM region uses all 16 YMM registers, has no stack access or calls, and is
955 bytes in the linked binary.  Its 1536-byte output scratch matches the
intrinsic boundary exactly for the full-range boundary input and 100 random
inputs.  Full inverse, in-place, round-trip, schoolbook polynomial
multiplication, scheme, benchmark validation, and linked AVX2-only gates pass.

| Operation | TSC median | p10 | p90 | p99 | Hardware cycles/call | Instructions/call | Branches/call | Cache refs/call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Production inverse | 433 | 430 | 437 | 447 | 650.63 | 2600.29 | 44.21 | 48.83 |
| GT inverse NTT32 intrinsic region | 537 | 535 | 541 | 568 | 801.49 | 1967.65 | 21.19 | 50.83 |
| GT inverse NTT32 ASM region | 422 | 419 | 430 | 436 | 633.95 | 2051.74 | 21.19 | 52.45 |
| GT full inverse intrinsic | 998 | 998 | 1007 | 1024 | 1478.51 | 4645.33 | 46.21 | 49.51 |
| GT hybrid inverse | 886 | 885 | 892 | 898 | 1313.82 | 4731.42 | 46.21 | 49.64 |
| Production polynomial multiplication | 1648 | 1639 | 1655 | 1672 | 2411.13 | 8984.67 | 144.31 | 267.25 |
| GT polynomial multiplication, intrinsic inverse | 3301 | 3296 | 3308 | 3327 | 4814.06 | 18309.98 | 136.31 | 197.15 |
| GT polynomial multiplication, hybrid inverse | 3179 | 3175 | 3184 | 3220 | 4646.74 | 18396.07 | 136.31 | 200.88 |

The scheduled region lowers median TSC by 21.4% and hardware cycles by 20.9%.
It retires 4.3% more instructions, while IPC rises from 2.45 to 3.24; the gain
comes from the explicit dependency schedule rather than a smaller instruction
count.  At pipeline level, the hybrid lowers inverse TSC by 11.2% and full GT
polynomial multiplication by 3.7%.  The hybrid full path is still 1.93x the
production TSC median, so the next region is inverse DFT3 plus its packed
checkpoint.

## 2026-07-16 hand-scheduled inverse DFT3 region

This run adds a second handwritten AVX2 inverse region: the in-place inverse
DFT3 plus three packed Barrett checkpoints.  The preceding inverse NTT32 region
remains ASM; untwist, normalization, branch merge, 4x8 transpose, and final
stores remain intrinsic.  Performance conclusions in this and subsequent runs
use only `perf stat -e cycles` hardware cycles.

The environment is the same Ryzen 7 9700X, CPU 2 pinning, performance governor,
enabled boost, non-isolated sibling CPU 10, GCC 16.1.1, 64 rotating inputs, 100
warmups, and 100000 measured calls.  `perf stat -r 5` reports the mean counter;
the run is stored as `results/20260716-invdft3-asm` on the benchmark host.

| Operation | Hardware cycles/call | perf variation |
| --- | ---: | ---: |
| Inverse DFT3/checkpoint intrinsic | 131.62 | 0.57% |
| Inverse DFT3/checkpoint ASM | 125.09 | 0.80% |
| GT inverse, inverse-NTT32 ASM only | 1315.90 | 0.04% |
| GT inverse, inverse-NTT32 + DFT3 ASM | 1306.74 | 0.05% |
| Production inverse | 651.27 | 0.06% |
| GT polynomial multiplication, inverse-NTT32 ASM only | 4671.29 | 0.09% |
| GT polynomial multiplication, inverse-NTT32 + DFT3 ASM | 4640.95 | 0.10% |
| Production polynomial multiplication | 2414.32 | 0.04% |

The 230-byte linked DFT3 symbol uses YMM0..YMM14, has no stack access or calls,
and matches the intrinsic 768-word scratch output exactly for boundary and 100
random cases.  It lowers the isolated region by 4.96%, full inverse by 0.70%,
and full GT polynomial multiplication by 0.65%.  The two-region GT path remains
1.92x production in hardware cycles, so the next inverse ASM boundary is the
untwist/merge/4x8 final-store postprocess.

## 2026-07-16 hand-scheduled inverse postprocess region

This run adds the third handwritten inverse region: fixed-factor untwist,
branch merge, normalization, lane-local 4x8 transpose, public CRT block lookup,
and canonical 64-bit stores.  The three regions remain separate calls from a C
wrapper that owns the 1536-byte aligned row scratch.  All performance results
below use only `perf stat -e cycles` hardware cycles.

The environment remains the Ryzen 7 9700X with CPU 2 pinned, performance
governor, enabled boost, non-isolated sibling CPU 10, GCC 16.1.1, 64 rotating
inputs, 100 warmups, and 100000 measured calls.  `perf stat -r 5` reports the
mean counter; the run is stored as `results/20260716-invpost-asm` on the host.

| Operation | Hardware cycles/call | perf variation |
| --- | ---: | ---: |
| Inverse postprocess intrinsic | 580.83 | 0.19% |
| Inverse postprocess ASM | 521.51 | 0.02% |
| GT inverse, NTT32 + DFT3 ASM | 1307.52 | 0.05% |
| GT inverse, all three regions ASM | 1254.70 | 0.01% |
| Production inverse | 651.82 | 0.06% |
| GT polynomial multiplication, NTT32 + DFT3 ASM | 4645.01 | 0.08% |
| GT polynomial multiplication, all three inverse regions ASM | 4584.06 | 0.05% |
| Production polynomial multiplication | 2426.09 | 0.02% |

The 781-byte linked postprocess symbol uses 15 YMM registers, has no stack
access or calls, and contains no AVX-512 registers.  Generated untwist and
public output-block tables are the only data-dependent address sources, and all
indices are public loop state.  Direct `[0,q]` boundary scratch, 100 random
valid scratch inputs, in-place full inverse, round trip, schoolbook polynomial
multiplication, scheme validation, and linked-object audits pass.

The scheduled postprocess lowers the isolated region by 10.21%, full inverse
by 4.04%, and full GT polynomial multiplication by 1.31%.  The three-region GT
path remains 1.89x production in hardware cycles.  The next inverse milestone
is to fuse the three ASM regions and remove intermediate call/`vzeroupper`
boundaries while preserving the same scratch and exact-output contracts.

## 2026-07-16 fused inverse and KPQC Final AVX2 comparison

The three inverse regions are now also exposed through one fused ASM entry.
The 1968-byte linked symbol owns one 1536-byte, 32-byte-aligned scratch frame,
contains no `call`, `push`, or `pop`, and issues one terminal `vzeroupper`.
Standalone region symbols remain available for exact boundary regression tests;
both paths are generated from the same region macros.  Exact full inverse,
`out == in`, round trip, and schoolbook polynomial multiplication tests pass.

`make kpqc-audit` verifies that the active production `asm/ntt.s`,
`asm/invntt.s`, `asm/basemul.s`, `consts.c`, and `poly.c` are byte-identical to
the corresponding KPQC Final NTRU+768 AVX2 files.  Consequently the existing
production operations are also a same-compiler, same-flags KPQC Final arithmetic
baseline; no differently built executable is being compared.

The first comparison is stored as `results/20260716-fused-kpqc`.  It uses the
same Ryzen 7 9700X, CPU 2 pinning, performance governor, enabled boost,
non-isolated sibling CPU 10, GCC 16.1.1, 64 rotating inputs, 100 warmups, 100000
measured calls, and five `perf stat -e cycles` repetitions as the preceding
runs.

| Operation | KPQC Final / production cycles | GT cycles | GT / KPQC Final |
| --- | ---: | ---: | ---: |
| Forward NTT | 667.04 | 1454.02 | 2.18x |
| Pointwise multiplication | 480.64 | 479.75 | 1.00x |
| Inverse NTT | 651.61 | 1252.94 fused | 1.92x |
| Full polynomial multiplication | 2420.73 | 4585.62 fused | 1.89x |

The fused and three-call inverse paths were then checked in both benchmark
orders.  Positive deltas below mean that fusion is faster.  Each row reports
hardware cycles/call from `perf stat -e cycles`; the ten-repeat runs are stored
as `results/20260716-fused-confirm` and
`results/20260716-fused-confirm-reversed`.

| Run | Three-call inverse | Fused inverse | Delta | Three-call polymul | Fused polymul | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 repeats | 1253.86 | 1252.94 | +0.07% | 4583.48 | 4585.62 | -0.05% |
| 10 repeats | 1254.38 | 1252.57 | +0.14% | 4611.15 | 4588.97 | +0.48% |
| 10 repeats, reversed order | 1254.91 | 1252.96 | +0.16% | 4599.58 | 4590.99 | +0.19% |

Fusion therefore succeeds as an ABI and scheduling boundary, but removing the
calls is performance-neutral at full-pipeline scale.  It saves only about one
to two inverse cycles, and the full-polymul delta is smaller than 0.5%.  The
next optimization priority is the GT forward frontend and stage-1+2 schedule:
pointwise multiplication already matches KPQC Final, while forward NTT is the
largest relative gap.  Further inverse call-overhead tuning is not a priority.
