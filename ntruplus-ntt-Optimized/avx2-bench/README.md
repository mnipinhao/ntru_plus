# NTRU+768 AVX2 benchmark harness

This directory benchmarks the existing production AVX2 pipeline and the new GT
forward-NTT intrinsic prototype on an x86-64 host.  Correctness is a mandatory
gate and setup work stays outside measured regions.

## Operations

| Name | Implementation | Included work |
| --- | --- | --- |
| `ntt` | production AVX2 | one forward NTT |
| `gt-ntt` | GT intrinsic prototype | one forward GT NTT |
| `basemul` | production AVX2 | one pointwise/base multiplication on prepared NTT inputs |
| `invntt` | production AVX2 | one inverse NTT on a prepared valid NTT input |
| `polymul` | production AVX2 | two NTTs, basemul, and inverse NTT |

The GT prototype does not yet have a matching pointwise or inverse kernel, so
there is intentionally no GT full-polymul number.  NTRU+768 also has no
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
