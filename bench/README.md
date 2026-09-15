# NTRU+ Bench Suite

`bench/` is the local entry point for comparing two implementation directories:

1. KAT-based correctness validation
2. Cycle benchmarking for the shared KEM/poly APIs
3. Auto-generated comparison reports under `bench/results/`

Formal NTRU+768 AVX2 performance qualification uses the SUPERcop workflow in
`ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/BENCHMARK.md`.
This directory remains useful for KAT and diagnostic cycle checks; its timing
output is not a replacement for the fixed-ELF SUPERcop result.

The compare flow accepts any two implementation directories that already ship a working `Makefile`, such as:

- `../third_party/NTRUplus-official-main/Additional_Implementation/aarch64/NTRU+768`
- `../ntruplus-ntt-Optimized/Optimized_Implementation/NTRU+768`
- `../third_party/NTRUplus-official-main/Reference_Implementation/NTRU+768`

## Core Commands

```bash
cd bench

# default: Official reference vs ntt-Optimized optimized for the selected PARAM_SET
make compare

# correctness only
make compare-kat

# explicit alias of compare
make cycles-compare
```

## Compare Arbitrary Implementations

```bash
cd bench

make impl-compare \
  IMPL_A=../third_party/NTRUplus-official-main/Additional_Implementation/aarch64/NTRU+768 \
  IMPL_B=../ntruplus-ntt-Optimized/Optimized_Implementation/NTRU+768 \
  LABEL_A=official_aarch64 \
  LABEL_B=ntt_opt
```

Reference vs optimized:

```bash
make impl-compare \
  IMPL_A=../third_party/NTRUplus-official-main/Reference_Implementation/NTRU+768 \
  IMPL_B=../ntruplus-ntt-Optimized/Optimized_Implementation/NTRU+768 \
  LABEL_A=official_ref \
  LABEL_B=ntt_opt
```

Correctness only for arbitrary paths:

```bash
make impl-compare-kat \
  IMPL_A=../third_party/NTRUplus-official-main/Additional_Implementation/aarch64/NTRU+768 \
  IMPL_B=../ntruplus-ntt-Optimized/Optimized_Implementation/NTRU+768
```

## Useful Knobs

```bash
make RUN_TAG=my_test compare
make PARAM_SET=NTRU+1152 compare
make CYCLE_ITERATIONS=3000 CYCLE_WARMUP=200 compare
```

## How It Works

`bench_impls.py` asks each implementation's own `Makefile` for the `test` and `PQCgenKAT_kem` compile commands via `make -n`, then reuses those commands to build:

- the implementation's KAT generator
- the shared `cycles/ntruplus_cycle_bench.c` harness

That keeps the bench flow aligned with each implementation's actual source list and compile flags instead of duplicating per-variant logic in `bench/Makefile`.

## Output Artifacts

For each run tag:

- `results/kat/<RUN_TAG>/<LABEL>.req`
- `results/kat/<RUN_TAG>/<LABEL>.rsp`
- `results/kat/<RUN_TAG>/status.txt`
- `results/kat/<RUN_TAG>/metadata.json`
- `results/cycles/<RUN_TAG>/raw_<LABEL>.json`
- `results/cycles/<RUN_TAG>/comparison.json`
- `results/cycles/<RUN_TAG>/summary.md`
- `results/cycles/<RUN_TAG>/metadata.json`

## What Is Measured

`cycles/ntruplus_cycle_bench.c` reports min/median/mean/stddev/max for:

- `poly_cbd1`
- `poly_sotp_encode`
- `poly_sotp_decode`
- `poly_ntt`
- `poly_baseinv`
- `keygen`
- `encap`
- `decap`

The comparison summary also reports aggregate KEM speedup over `keygen + encap + decap`.

## Constraints

- Both implementations must target the same parameter set, checked through `params.h`.
- Architecture-specific implementations still need a compatible host.
  For example, `aarch64` paths need an arm64/aarch64 machine, and `avx2` paths need an x86_64 host with AVX2 support.

## Historical one-off profilers

The February 2026 C profilers are preserved under `legacy/` for provenance but
are no longer active Makefile targets. They duplicate the portable comparison
flow, and one of them embeds machine-specific paths. Use `bench_impls.py`
through the commands above for current comparisons.
