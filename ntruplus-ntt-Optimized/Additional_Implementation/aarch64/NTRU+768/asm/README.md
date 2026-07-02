# NTRU+768 AArch64 ASM Layout

This directory is split by role so stock, GT production, opt-in variants, and
benchmark-only experiments are not mixed together.

- `stock/`: KPQC-final stock AArch64 support, NTT, and base multiplication
  assembly.
- `gt/`: GT production wrappers, promoted GT assembly bodies, and GT support
  assembly used by the production KEM path.
- `baseline/`: retained GT non-production baseline wrappers/bodies used by
  comparison tests and profiling targets.
- `archive/`: readable historical/reference assembly that is not wired into
  production defaults.
- `bench_only/`: benchmark harness inputs and negative/old-contract controls.
  These files are not production defaults.
- `variants/`: opt-in production-like variants behind explicit build gates.
  These files are not generic drop-in replacements.
- `slothy/`: Slothy-generated production files, symbolic sources,
  microkernels, and archived prototypes.

Top-level files are limited to documentation and legacy notes.  New assembly
should go into one of the role directories above.

Do not delete files from `bench_only/`, `variants/`, `baseline/`, `archive/`,
`stock/`, or `gt/` without also removing or updating the matching
Makefile/aarch64-bench target and documentation reference.
