# NTRU+ AVX2 GT-Optimized Release

This directory is the source-only handoff package for the NTRU+768
Good-Thomas Optimized (GT-Optimized) AVX2 implementation.

```text
avx2/
  NTRU+768/   implementation, qualification contract, and source closure
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

Full validation additionally builds the functional test and the KAT
generator:

```sh
cd NTRU+768
make check
```

`make check` compiles the test and KAT harness from the upstream Official
AVX2 tree rather than from a copy inside this package. It resolves that tree
through `OFFICIAL_ROOT`, which defaults to
`../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768`.
Set `OFFICIAL_ROOT` explicitly when that tree is not present at the default
location.

This directory is limited to the production source closure and its
qualification material. Research experiments, rejected candidates, generators,
and benchmark harnesses remain outside this release tree.
