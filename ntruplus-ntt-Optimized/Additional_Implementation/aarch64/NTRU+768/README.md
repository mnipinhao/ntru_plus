# NTRU+768 AArch64 implementation

This directory is organized by lifecycle. Production builds must not consume
files from an `experiment` or `experiments` path.

| Path | Purpose |
| --- | --- |
| `kem.c`, `ntt.c`, `poly*.c`, headers | Scheme and production C sources |
| `asm/gt/` | GT production assembly |
| `asm/slothy/production/` | Promoted Slothy outputs linked by production |
| `gt_production_sources.mk` | Authoritative production source manifest |
| `gt_production_variants.mk` | Authoritative production feature flags |
| `make/production.mk` | KAT and production KEM targets |
| `make/tests.mk` | Correctness and ABI tests |
| `make/experiments.mk` | Experiment and profiling targets |
| `gt_test/` | Test harnesses and reference code |
| `gt_bench/` | Scheme-local PMU and profiling harnesses |
| `scripts/` | Analysis and repository guards |
| `experiments/` | Reproducible experiment sources and decisions |
| `docs/` | Design records and benchmark reports |

Run `make check-production-layout` after changing a production source or build
recipe. The guard follows assembler and C includes recursively and rejects any
production dependency under an experiment directory.
