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
