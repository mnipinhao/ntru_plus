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

| file | role |
|---|---|
| `kem.c` | key generation, encapsulation, decapsulation |
| `symmetric.c`, `hash_fixed.c`, `fips202.c` | SHAKE256 and the fixed-length hashes |
| `keccakf1600.S`, `keccakf1600_v84a.S` | Keccak-f[1600]: scalar AArch64, or FEAT_SHA3 when the compiler targets it (the same files as NTRU+768 and NTRU+1152) |
| `api_glue.c` | the C wrappers behind the `poly_*` API: tables and caller-owned scratch |
| `ntt.S`, `ntt_top.S`, `ntt9.S`, `ntt_tail.S` | forward Good-Thomas NTT |
| `base.c`, `base_tables.h` | pointwise products in the transform domain |
| `inverse.S`, `baseinv_*.S` | batch inversion (key generation) and the driver of the decapsulation inverse |
| `basemul_rinv.S` | decapsulation first product, `R^-1` boundary |
| `inverse9.S`, `inverse16_paired.S`, `inverse_tail_direct.S`, `inverse_route.S`, `inverse*_tables.h` | decapsulation inverse NTT with the ternary reduction fused in |
| `pack.c`, `pack6.h` | canonical serialization |
| `unpack.c` | canonical decoding and range check |
| `cbd.S`, `add.S`, `support_abi.S` | sampling, SOTP, `sub`, `triple`; `support_abi.S` gives the leaves that use v8-v15 an AAPCS64 boundary |
| `secure_clear.h` | clears and the SUPERCOP declassify annotation |

## Constant time and correctness

- SUPERCOP TIMECOP passes at `-O`, `-O2`, `-O3` and `-Os` (`TIMECOP=256`).
- The decapsulation inverse is proved overflow-free over the linked
  executable for every input the first product can produce, with the output in
  {-1, 0, 1} (interval analysis; `docs/VALIDATION.md`).

## Performance

Against SUPERCOP 20260831's `ntruplus864/aarch64` (2026-09-23; details in
`experiments/ROADMAP-m2-delivery.md` of the repository):

| | key generation | encapsulation | decapsulation |
|---|---:|---:|---:|
| M2 Pro, vs Official + CryptoExtension | -9.4% | -11.2% | -7.8% |
| M2 Pro, Keccak held equal | -6.0% | -6.4% | -4.2% |
| Cortex-A76, Keccak held equal | -10.8% | -12.1% | -9.4% |

"Keccak held equal" links Official's sponge against GT's permutation, so the
margin is the arithmetic alone.

The Forward kernel is restricted to the proven KEM input producers. Its
stage-one copy optimization is not valid for arbitrary input polynomials.
BaseInv consumes and produces FR0/R0 values. The first decapsulation product
uses an FR0/R^-1 boundary that the following inverse consumes directly.
Detailed bounds and historical optimization evidence are recorded in
`docs/OPTIMIZATION-ROADMAP.md` and `docs/VALIDATION.md`.

`SOURCE-MANIFEST.sha256` freezes the accepted source closure. Development
generators, Slothy inputs, benchmark harnesses, rejected candidates, and raw
performance logs remain outside this directory.
