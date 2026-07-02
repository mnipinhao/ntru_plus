# NTRU+768 AArch64 ASM Layout

This directory is production-only for the current GT path.

- `gt/`: public GT production wrappers, promoted GT assembly bodies, and GT
  support assembly used by the production KEM path.
- `slothy/production/`: Slothy-generated production assembly included by the
  GT wrappers.
- `slothy/inputs/`: symbolic sources and local Slothy drivers for regenerating
  selected production outputs.
- `slothy/support_kernels/`: production support-kernel replacements for
  packing, frombytes/tobytes, `poly_sub`, `poly_triple`, and `poly_crepmod3`.

Stock, baseline, benchmark-only, and rejected prototype assembly has been
removed from this active tree.  Use git history for those artifacts.
