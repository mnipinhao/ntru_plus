# NTRU+ GT Production

This package contains the publishable NTRU+768 AArch64 Neon implementation:

```text
Additional_Implementation/aarch64/NTRU+768/
```

The parameter-set directory is self-contained: it owns its Makefile, KEM
source, polynomial interface, assembly, SHAKE backend, tests, and KAT path, with
validation dependencies copied into the package rather than linked to another
implementation tree.

Build and validate on AArch64:

```sh
cd Additional_Implementation/aarch64/NTRU+768
make check
```

## SUPERCOP

No SUPERCOP leaf is checked in.  Generate one from the package on AArch64 Linux:

```sh
cd Additional_Implementation/aarch64/NTRU+768
python3 scripts/export_supercop.py /tmp/ntruplus768-aarch64-gt-leaf
```

Copy the result to `crypto_kem/ntruplus768/<name>` in a SUPERCOP tree.  The leaf
is generated from the same sources that `make check` validates, declares
`goal-constbranch` and `goal-constindex`, and passes SUPERCOP's TIMECOP check.
See the package README for details.

The package intentionally contains one selected production profile. Slothy
inputs, benchmark harnesses, rejected alternatives, and development selectors
remain outside this release tree.
