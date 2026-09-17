# NTRU+864 AArch64 production implementation

This directory is the self-contained source and validation package for the
selected NTRU+864 AArch64 implementation. It exposes only the standard KEM API
from `api.h`; the internal `poly_*` entry points implement the fixed KEM data
flow and are not a general polynomial-multiplication API.

Build and validate on Linux/AArch64:

```sh
make check
```

The check covers release hygiene, the source manifest, KEM correctness,
AAPCS64 preservation, canonical decoding and rejection, zeroization, exact KAT
comparison, and deterministic SUPERCOP export.

## Source map

- `kem.c`, `symmetric.c`, `fips202.c`, `hash_fixed.c`: KEM and SHAKE256.
- `ntt_api.c`, `ntt.S`, `ntt_top.S`, `ntt_tail.S`, `ntt9.S`: forward NTT.
- `base.c`, `base_tables.h`: transform-domain multiplication.
- `inverse_api.c`, `inverse.S`, `baseinv_*.S`, `basemul_rinv.S`,
  `inverse9.S`, `inverse16.S`, `inverse16_tail.S`: inversion and inverse NTT.
- `pack.c`, `pack_{full,small,compare}.S`: canonical serialization.
- `unpack_api.c`, `unpack.c`: canonical decoding and layout conversion.
- `support_abi.S`: AAPCS64 wrappers around legacy leaf helpers.

The Forward kernel is restricted to the proven KEM input producers. Its
stage-one copy optimization is not valid for arbitrary input polynomials.
BaseInv consumes and produces FR0/R0 values. The first decapsulation product
uses an FR0/R^-1 boundary that the following inverse consumes directly.
Detailed bounds and historical optimization evidence are recorded in
`docs/OPTIMIZATION-ROADMAP.md` and `docs/VALIDATION.md`.

`SOURCE-MANIFEST.sha256` freezes the accepted source closure. Development
generators, Slothy inputs, benchmark harnesses, rejected candidates, and raw
performance logs remain outside this directory.
