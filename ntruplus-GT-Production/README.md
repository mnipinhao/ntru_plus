# NTRU+ GT Production

NTRU+864 now has a separate KEM-only K1 integration at
[`Additional_Implementation/aarch64/NTRU+864`](Additional_Implementation/aarch64/NTRU+864/README.md).
Read its `VALIDATION.md` for Pi 5 correctness, KAT and integration PMU evidence.
Its Linux build and internal compatibility sources are distinct from the
NTRU+768 release profile described below; NTRU+768 is unchanged.

This package contains the publishable NTRU+768 AArch64 Neon implementation:

```text
Additional_Implementation/aarch64/NTRU+768/
```

The parameter-set directory follows the same implementation-package shape as
KPQC final: it owns its Makefile, KEM source, polynomial interface, assembly,
SHAKE backend, tests, and KAT path. Unlike KPQC final, validation dependencies
are copied into the package rather than linked to another implementation tree.

Build and validate on AArch64:

```sh
cd Additional_Implementation/aarch64/NTRU+768
make check
```

The package intentionally contains one selected production profile. Slothy
inputs, benchmark harnesses, rejected alternatives, and development selectors
remain outside this release tree.
