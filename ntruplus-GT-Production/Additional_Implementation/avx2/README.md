# NTRU+ AVX2 GT-Optimized Release

This directory is the source-only handoff package for the NTRU+768
Good-Thomas Optimized (GT-Optimized) AVX2 implementation.

```text
avx2/
  NTRU+768/   implementation, tests, canonical KAT, and source closure
```

Start with:

- [`NTRU+768/README.md`](NTRU+768/README.md) for the production source layout.
- [`NTRU+768/QUALIFICATION.md`](NTRU+768/QUALIFICATION.md) for the promoted
  Encap architecture and what it replaces.
- [`NTRU+768/IMPLEMENTATION.md`](NTRU+768/IMPLEMENTATION.md) and
  [`NTRU+768/LAYOUTS.md`](NTRU+768/LAYOUTS.md) for the transform and layout
  contracts.
- [`NTRU+768/BENCHMARK.md`](NTRU+768/BENCHMARK.md) for the recorded cycle
  comparison against the Official AVX2 implementation.

The implementation targets x86-64 with AVX2, BMI2, POPCNT, and AES-NI.

To verify the NTRU+768 production source closure:

```sh
cd NTRU+768
make check-hashes
```

Full validation additionally builds the functional test, regenerates the
known-answer files, and compares them against the Official NTRU+768 vectors
in `NTRU+768/kat/expected/`:

```sh
cd NTRU+768
make check
```

The test harness, the KAT generator, and `randombytes` are vendored into the
package, so validation does not link to another implementation tree. `LICENSE`
is the upstream NTRU+ MIT license covering that vendored material.

This directory is limited to the production source closure and its
qualification material. Research experiments, rejected candidates, generators,
and benchmark harnesses remain outside this release tree.
