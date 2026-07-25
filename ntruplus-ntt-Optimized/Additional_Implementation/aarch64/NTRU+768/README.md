# NTRU+768 AArch64 implementation

This directory is organized by lifecycle. Production builds must not consume
files from an `experiment` or `experiments` path.

| Path | Purpose |
| --- | --- |
| `kem.c`, `ntt.c`, `poly*.c`, headers | Scheme and production C sources |
| `asm/gt/{ntt,invntt,basemul,baseinv,support}/` | GT production assembly, grouped by operation family |
| `asm/slothy/inputs/` | Symbolic inputs, contracts, and regeneration drivers |
| `gt_production_sources.mk` | Authoritative production source manifest |
| `gt_production_variants.mk` | Authoritative production feature flags |
| `docs/gt-production-current-file-map.md` | Human-readable selected KEM path and profiler-only file map |
| `docs/gt-production-keygen-cq-promotion-audit-2026-07-23.md` | Mixed versus direct-CQ production decision and Pi 5 evidence |
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

Production assembly uses a uniform suffix convention: `.S` is a baseline or
wrapper, `.sym.S` is symbolic Slothy input, `.n1.opt.S` is a standalone
Neoverse-N1 optimized object, and `.n1.opt.inc` is an optimized include owned
by a wrapper.
