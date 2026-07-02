# NTRU+768 AArch64 ASM Layout

This directory is being split by role so production files do not sit next to
benchmark-only experiments.

Current top-level files are still production or stock paths unless noted
otherwise.  The first cleanup phase only moved files whose role is already
clear:

- `bench_only/`: benchmark harness inputs and negative/old-contract controls.
  These files are not production defaults.
- `variants/`: opt-in production-like variants behind explicit build gates.
  These files are not generic drop-in replacements.
- `slothy/`: Slothy-generated production files, symbolic sources,
  microkernels, and archived prototypes.

Do not delete files from `bench_only/` or `variants/` without also removing the
matching Makefile/aarch64-bench target and documentation reference.
