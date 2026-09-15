# NTRU+

This repository keeps an upstream Official snapshot beside an active NTRU+
optimization workspace. It supports parameter sets 768, 864, and 1152 across
scalar, AVX2, AArch64, and preserved Cortex-M-oriented source lanes.

## Quick start

For the current NTRU+768 AVX2 work, install GT Clean into a SUPERcop tree and
use the production-owned layout audit/build recipe:

```sh
./ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/install-supercop.sh \
  /path/to/supercop
python3 /path/to/supercop/crypto_kem/ntruplus768/avx2-gt32-clean/qualified/build-supercop.py \
  --supercop-root /path/to/supercop
```

See the implementation's
[BENCHMARK.md](ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/BENCHMARK.md)
and
[QUALIFICATION.md](ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/QUALIFICATION.md)
for the fixed-ELF Official/GT protocol. The generic `bench/` harness remains
available for local correctness and diagnostic comparisons, but it is not the
formal performance authority.

Run a local portable KAT comparison against the Official snapshot with:

```sh
make -C bench PARAM_SET=NTRU+768 compare-kat
```

See [WORKFLOW.md](WORKFLOW.md) before editing an implementation, and see
[bench/README.md](bench/README.md) for arbitrary implementation comparisons.
The [documentation index](docs/README.md) separates current runbooks from dated
engineering records.

## Directory policy

- `third_party/NTRUplus-official-main/`: upstream Official comparison source.
- `ntruplus-ntt-Optimized/Reference_Implementation/`: active workspace reference lane.
- `ntruplus-ntt-Optimized/Optimized_Implementation/`: active scalar optimization lane.
- `ntruplus-ntt-Optimized/Cortex-M_Optimized_Implementation/`: preserved legacy/Cortex-M-oriented source lane; not a validated MCU build by itself.
- `ntruplus-ntt-Optimized/Additional_Implementation/`: AVX2 and AArch64 implementations.
- `bench/`: portable local KAT/diagnostic comparison harness; not the formal SUPERcop timing path.
- `ntruplus-ntt-Optimized/aarch64-bench/`: Pi 5 and PMU-specific benchmark harnesses.

## Current optimization focus

The most developed architecture-specific path is the NTRU+768 AArch64
Good-Thomas implementation. Its current production status and comparison
evidence live in:

- `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/docs/gt-new-vs-kpqc-final-optimization-summary.md`
- `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/optimization_scoreboard.md`

Architecture-specific code must be built and timed on a compatible host.
Correctness must be established before performance results are used.
