# NTRU+ GT Production

This package contains the publishable NTRU+768 implementations:

```text
Additional_Implementation/aarch64/NTRU+768/   AArch64 Neon
Additional_Implementation/avx2/NTRU+768/      x86-64 AVX2
```

Each parameter-set directory follows the same implementation-package shape as
KPQC final: it owns its Makefile, KEM source, polynomial interface, assembly,
SHAKE backend, and validation path.

Both packages copy their validation dependencies into the package rather than
linking to another implementation tree, so each one builds, tests, and checks
its known-answer vectors on its own.

Build and validate on AArch64:

```sh
cd Additional_Implementation/aarch64/NTRU+768
make check
```

Build and validate on x86-64:

```sh
cd Additional_Implementation/avx2/NTRU+768
make check
```

The package intentionally contains one selected production profile. Slothy
inputs, benchmark harnesses, rejected alternatives, and development selectors
remain outside this release tree.

## SUPERCOP leaves

`SUPERCOP/crypto_kem/ntruplus768/` holds a materialized SUPERCOP implementation
directory for each package, regenerated and drift-checked by the scripts under
`scripts/`. See [`SUPERCOP/README.md`](SUPERCOP/README.md) for how to verify a
leaf and for what a SUPERCOP measurement of it does and does not establish.
