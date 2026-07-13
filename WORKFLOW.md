# NTRU+ Repository Workflow

This document is the operational source of truth for the repository. Derive the
checkout root instead of using a machine-specific path:

```sh
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
```

## Repository roles

| Path | Role | Edit policy |
| --- | --- | --- |
| `ntruplus-KpqC-Final/` | Frozen comparison baseline | Do not edit during optimization work |
| `ntruplus-ntt-Optimized/` | Active implementation workspace | Edit the selected parameter/lane only |
| `bench/` | Portable KAT and cycle comparison front door | Keep implementation-neutral |
| `ntruplus-ntt-Optimized/aarch64-bench/` | Pi 5 and PMU harnesses | AArch64 host only |

The active and frozen roots contain `NTRU+768`, `NTRU+864`, and `NTRU+1152`
across scalar reference, scalar optimized, AVX2, and AArch64 lanes. The active
root also retains a Cortex-M-oriented legacy source lane. Do not assume that
similarly named lanes share a Makefile or source contract.

## Select a target before editing

Record all three values:

1. Parameter set: `NTRU+768`, `NTRU+864`, or `NTRU+1152`.
2. Lane: reference, optimized, Cortex-M-oriented, AVX2, or AArch64.
3. Contract: build, KAT, differential test, cycle benchmark, or PMU benchmark.

Inspect the selected Makefile before building:

```sh
make -C <implementation-directory> -n test
make -C <implementation-directory> -n PQCgenKAT_kem
```

In the submission-compatible Makefiles, `test` commonly means "build the test
binary" rather than "execute every correctness test". Use a KAT or an explicit
run/check target as the correctness gate.

## Portable scalar comparison

The default comparison is the frozen reference implementation versus the
active optimized implementation for the same parameter set:

```sh
make -C bench PARAM_SET=NTRU+768 compare-kat
make -C bench PARAM_SET=NTRU+768 compare
```

Compare arbitrary implementation directories with:

```sh
make -C bench impl-compare-kat \
  IMPL_A=../ntruplus-KpqC-Final/Reference_Implementation/NTRU+768 \
  IMPL_B=../ntruplus-ntt-Optimized/Optimized_Implementation/NTRU+768 \
  LABEL_A=frozen_ref \
  LABEL_B=active_opt
```

`IMPL_A` and `IMPL_B` must use the same parameter set. AVX2 and AArch64 lanes
still require a compatible host even when invoked through `bench/`.

## End-to-end validation wrapper

The wrapper runs the portable KAT-gated comparison with a short cycle sample:

```sh
PARAM_SET=NTRU+768 ./scripts/validate_optimization.sh
```

Optional overrides:

```sh
PARAM_SET=NTRU+864 \
IMPL_A="$REPO_ROOT/ntruplus-KpqC-Final/Reference_Implementation/NTRU+864" \
IMPL_B="$REPO_ROOT/ntruplus-ntt-Optimized/Optimized_Implementation/NTRU+864" \
CYCLE_ITERATIONS=500 \
./scripts/validate_optimization.sh
```

No setup script is required. `bench/Makefile` creates its build and result
directories on demand.

## AArch64 and GT work

Build architecture-specific implementations only on a compatible AArch64 host.
NTRU+768 Good-Thomas production work uses the active directory:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/
```

Pi 5 cycle and PMU work stays under:

```text
ntruplus-ntt-Optimized/aarch64-bench/
```

Before timing, verify the exact linked source set, hash policy, parameter set,
correctness result, and baseline/candidate labels. Do not compare timing across
different hosts or counter backends as if they were equivalent.

## Results and generated files

Portable comparison output is written under:

```text
bench/results/kat/<RUN_TAG>/
bench/results/cycles/<RUN_TAG>/
```

Keep machine-readable metadata and concise summaries when they are decision
evidence. Raw build output, solver logs, temporary binaries, and PMU replay logs
are local artifacts and should remain ignored.

## Correctness and security boundary

- Do not modify checked-in KAT vectors in either source root.
- A successful build is not a correctness result.
- KAT compatibility does not prove constant-time behavior, range safety,
  decryption-failure bounds, or parameter security.
- Changes to parameters, distributions, encoding, reductions, or
  secret-dependent control/data flow require the applicable security and range
  checks in addition to KATs.

## Command reference

```sh
make -C bench help
make -C bench PARAM_SET=NTRU+768 compare-kat
make -C bench PARAM_SET=NTRU+768 compare
./scripts/validate_optimization.sh
```
