# NTRU+768 AVX2 benchmark harness

This directory benchmarks the existing production AVX2 pipeline and the GT SoA
forward, pointwise, inverse, and full-polynomial prototypes on an x86-64 host.
Correctness is a mandatory gate and setup work stays outside measured regions.

## Operations

| Name | Implementation | Included work |
| --- | --- | --- |
| `ntt` | production AVX2 | one forward NTT |
| `gt-ntt` | GT intrinsic prototype | one forward GT NTT |
| `gt-ntt-asm-soa` | GT hybrid ASM prototype | intrinsic frontend/stage 1+2, hand-scheduled stage 3+4+5, and fused 16-block SoA store |
| `basemul` | production AVX2 | one pointwise/base multiplication on prepared NTT inputs |
| `gt-basemul-soa` | GT AVX2 intrinsic prototype | 192 quartic products as 12 batches of 16 blocks; prepared SoA inputs and lambda-table generation are excluded |
| `invntt` | production AVX2 | one inverse NTT on a prepared valid NTT input |
| `gt-invntt32` | GT AVX2 intrinsic region | direct-SoA inverse NTT32 through the packed Barrett scratch boundary |
| `gt-invntt32-asm` | GT hand-scheduled ASM region | the same inverse NTT32 scratch boundary, using all 16 YMM registers and no stack |
| `gt-invntt-soa` | GT AVX2 intrinsic prototype | direct SoA inverse NTT32, inverse DFT3, untwist, normalization, branch merge, and canonical stores |
| `gt-invntt-soa-hybrid` | GT partial ASM inverse | hand-scheduled inverse NTT32 followed by intrinsic inverse DFT3 and postprocess |
| `polymul` | production AVX2 | two NTTs, basemul, and inverse NTT |
| `gt-polymul-soa` | GT hybrid/intrinsic prototype | two hybrid ASM SoA NTTs, SoA basemul, and direct SoA inverse |
| `gt-polymul-soa-hybrid` | GT partial ASM inverse pipeline | the same GT path with the hand-scheduled inverse NTT32 region |

The GT ASM prototype uses the candidate SoA mapping
`batch=4*k3+Q/8, lane=8*branch+Q%8`.  Its packed int16 Barrett checkpoint emits
a bounded `[0,q]` representative rather than the intrinsic path's centered
representative; validation therefore compares modulo `q` after applying the
mapping oracle.

The GT prototype now has matching intrinsic pointwise and inverse kernels, so
the harness measures the complete GT polynomial multiplication.  The isolated
SoA basemul, inverse NTT32, and full inverse operations use prepared inputs and
exclude their producers.  NTRU+768 also has no
scheme-level matrix-vector multiplication; `basemul_add` and KEM components are
the relevant future caller benchmarks.

## Build and validate

The default build is AVX2-only and tuned for the benchmark host without enabling
AVX-512:

```sh
make build
make asm-audit
make validate
```

Default target flags:

```text
-march=x86-64-v3 -mtune=znver5 -mprefer-vector-width=256
```

`make validate` runs the production AVX2 scheme test, the GT prototype's
boundary/differential tests, and the benchmark harness's round-trip,
schoolbook-polymul, and GT-reference checks.

## Reproducible benchmark run

```sh
CORE=2 PERF_PREFIX= ./run_bench.sh
```

If hardware counters require privilege:

```sh
CORE=2 PERF_PREFIX=sudo ./run_bench.sh
```

The runner records:

- CPU model and topology;
- pinned core and its SMT sibling list;
- governor and boost state;
- compiler, build flags, kernel, and perf version;
- internal serialized-TSC median and percentiles;
- `perf stat` cycles, instructions, branches, branch misses, and cache events.

Core and cache events run in separate `perf stat` passes so the target host does
not multiplex six general-purpose events.  Each pass still operates on the same
fixed input corpus and iteration count.

The benchmark uses `LFENCE/RDTSC` at the start and `RDTSCP/LFENCE` at the end.
Those are invariant-TSC ticks, not necessarily unhalted core cycles.  `perf`
provides the hardware-cycle measurement.

Defaults are 100 warmups, 1000 calls per sample, 101 samples, 64 rotating input
sets, and 100000 calls for each perf loop.  Override them at build time, for
example:

```sh
make clean
make build CFLAGS='-O3' TARGET_FLAGS='-march=x86-64-v3 -mtune=znver5 -mprefer-vector-width=256 -DBENCH_NTESTS=31'
```

The runner pins the process but cannot guarantee the SMT sibling is idle.  For
release numbers, disable SMT or reserve both sibling CPUs.  It also records
Turbo/boost state; use `STRICT_ENV=1` to reject an active boost setting instead
of merely warning.

Results are written under `results/<UTC timestamp>/` and are ignored by git.
