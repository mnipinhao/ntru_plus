# NTRU+ AArch64 GT-Optimized Release

This directory is the complete handoff package for the NTRU+768
Good-Thomas Optimized (GT-Optimized) AArch64 implementation.

```text
aarch64/
  NTRU+768/   implementation, tests, canonical KAT, and documentation
  benchmark/  reproducible GT-Optimized versus KPQC-final full-KEM benchmark
```

Start with:

- [`NTRU+768/README.md`](NTRU+768/README.md) for build and validation.
- [`NTRU+768/docs/OPTIMIZATION-SUMMARY.md`](NTRU+768/docs/OPTIMIZATION-SUMMARY.md)
  for the technical comparison with KPQC final.
- [`benchmark/README.md`](benchmark/README.md) to reproduce the Raspberry Pi 5
  cycle measurements.
- [`benchmark/results/pi5-reference-20260725/summary.md`](benchmark/results/pi5-reference-20260725/summary.md)
  for the included reference result and raw-run directory.

The implementation supports Linux/AArch64 ELF and macOS/AArch64 Mach-O.
Performance numbers in this release were measured on Linux/AArch64 using a
Raspberry Pi 5 Cortex-A76.

To verify the complete extracted archive:

```sh
shasum -a 256 -c SHA256SUMS
```
