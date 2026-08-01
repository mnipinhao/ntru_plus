# NTRU+ AArch64 GT-Optimized Release

This directory is the source-only handoff package for the NTRU+768
Good-Thomas Optimized (GT-Optimized) AArch64 implementation.

```text
aarch64/
  NTRU+768/   implementation, tests, canonical KAT, and implementation contract
```

Start with:

- [`NTRU+768/README.md`](NTRU+768/README.md) for build and validation.
- [`../../../bench/aarch64/gt-production/reports/OPTIMIZATION-SUMMARY.md`](../../../bench/aarch64/gt-production/reports/OPTIMIZATION-SUMMARY.md)
  for the technical comparison with KPQC final.
- [`../../../bench/aarch64/gt-production/README.md`](../../../bench/aarch64/gt-production/README.md)
  to reproduce the Raspberry Pi 5
  cycle measurements.
- [`../../../bench/aarch64/gt-production/results/pi5-reference-20260728-fqinv15-fixed/summary.md`](../../../bench/aarch64/gt-production/results/pi5-reference-20260728-fqinv15-fixed/summary.md)
  for the curated reference result.

The implementation supports Linux/AArch64 ELF and macOS/AArch64 Mach-O.
Performance numbers in this release were measured on Linux/AArch64 using a
Raspberry Pi 5 Cortex-A76.

To verify the complete extracted archive:

```sh
shasum -a 256 -c SHA256SUMS
```

The repository does not track a generated zip. From the repository root,
create a release artifact from the selected commit with:

```sh
git archive --format=zip \
  --prefix=ntruplus-GT-Production/ \
  --output=/tmp/ntruplus768-Optimized-aarch64.zip \
  HEAD:ntruplus-GT-Production
```

Benchmark harnesses, reports, and result archives are maintained outside this
release tree under
[`../../../bench/aarch64/gt-production/`](../../../bench/aarch64/gt-production/).
This directory remains limited to the production source closure and its
validation material.
