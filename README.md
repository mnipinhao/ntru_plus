# NTRU+

This repository is an NTRU+ optimization workspace. It supports parameter sets 768, 864, and 1152 across
scalar, AVX2, AArch64, and preserved Cortex-M-oriented source lanes.

## Quick start

Run the portable scalar KAT comparison from the repository root:

```sh
make -C bench PARAM_SET=NTRU+768 compare-kat
```

Run the KAT-gated comparison and cycle harness:

```sh
make -C bench PARAM_SET=NTRU+768 compare
```

See [WORKFLOW.md](WORKFLOW.md) before editing an implementation, and see
[bench/README.md](bench/README.md) for arbitrary implementation comparisons.
The [documentation index](docs/README.md) separates current runbooks from dated
engineering records.

## Directory policy

- `ntruplus-ntt-Optimized/Reference_Implementation/`: active workspace reference lane.
- `ntruplus-ntt-Optimized/Optimized_Implementation/`: active scalar optimization lane.
- `ntruplus-ntt-Optimized/Cortex-M_Optimized_Implementation/`: preserved legacy/Cortex-M-oriented source lane; not a validated MCU build by itself.
- `ntruplus-ntt-Optimized/Additional_Implementation/`: AVX2 and AArch64 implementations.
- `bench/`: portable KAT and cycle comparison front door.
- `ntruplus-ntt-Optimized/aarch64-bench/`: Pi 5 and PMU-specific benchmark harnesses.

## Current optimization focus

The most developed architecture-specific path is the NTRU+768 AArch64
Good-Thomas implementation. Its current production status and comparison
evidence live in:

- `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt-new-vs-kpqc-final-optimization-summary.md`
- `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/optimization_scoreboard.md`

For AVX2 (768/864/1152), the current best is the Official-opt line on branch `avx2-official-opt`:
about 23–30% fewer cycles than the Official SUPERCOP `avx2` implementation. This is research status,
not yet a production package. See
[docs/ntruplus-avx2-official-opt-current-best.md](docs/ntruplus-avx2-official-opt-current-best.md).

Architecture-specific code must be built and timed on a compatible host.
Correctness must be established before performance results are used.
