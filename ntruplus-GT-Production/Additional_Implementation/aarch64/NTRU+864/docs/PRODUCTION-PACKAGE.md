# Production package contract

The package contains one selected NTRU+864 AArch64 implementation. File and
symbol names describe their algorithmic role; campaign identifiers and
parameter prefixes are kept only in the historical roadmap.

The authoritative layers are:

- public KEM API: `api.h`, `params.h`, `kem.c`;
- representation contracts: `poly.h`, `base.h`, `inverse.h`, `pack.h`,
  `unpack.h`, and the constant-table headers;
- accepted arithmetic: the ordered `KEM_OBJECTS` closure in `Makefile`;
- validation: `test/`, `kat/`, `scripts/check_release.py`, and
  `scripts/check_zeroization.py`;
- deterministic SUPERCOP materialization: `scripts/export_supercop.py`.

The default build links the KEM directly. `make shared` creates
`libntruplus.so` only for component profiling. Benchmark artifacts and
development inputs are not part of the production closure.

The hash backend is SHAKE256 without an Armv8.4 SHA3 requirement. Fixed-size
`hash_f` and `hash_g` paths share the scalar AArch64 Keccak permutation.

Promotion gate order is: source selection, arithmetic proof, full KEM,
ABI/alias checks, canonical rejection, zeroization, exact KAT, release hygiene,
deterministic SUPERCOP export, same-host performance, then commit.
