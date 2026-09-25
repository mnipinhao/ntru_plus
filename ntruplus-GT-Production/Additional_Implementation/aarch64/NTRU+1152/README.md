# NTRU+1152 AArch64 production implementation

This directory is the self-contained source and validation package for the
selected NTRU+1152 AArch64 implementation. It exposes only the standard KEM API
from `api.h`; the internal `poly_*` entry points implement the fixed KEM data
flow and are not a general polynomial-multiplication API.

Build and validate (macOS/AArch64 or Linux/AArch64):

```sh
make check
```

The check covers release hygiene, the source manifest, the zeroization source
gate, KEM round trips with tampered-ciphertext rejection, 13,824 canonical-decode
boundary cases, AAPCS64 preservation of every entry point, per-leaf
non-invertibility (all 288 leaves), the zeroization audit, the byte-exact KAT
(`kat/expected/PQCkemKAT_3488.rsp`) and deterministic SUPERCOP export.
`docs/VALIDATION.md` describes each gate.

The build must keep the Makefile's `CFLAGS`: its three
`-DNTRUPLUS1152_ASM_*` flags select the assembly basemul and batch-inversion
kernels, and without them `inverse.c`'s C versions are used.

## Source map

| file | role |
|---|---|
| `kem.c` | key generation, encapsulation, decapsulation |
| `symmetric.c`, `hash_fixed.c`, `fips202.c` | SHAKE256 and the fixed-length hashes |
| `keccakf1600.S`, `keccakf1600_v84a.S` | Keccak-f[1600]: scalar AArch64, or FEAT_SHA3 when the compiler targets it (the same files as NTRU+768 and NTRU+864) |
| `api_glue.c` | the C wrappers behind the `poly_*` API: tables and caller-owned scratch |
| `ntt.S`, `ntt_top.S`, `ntt9.S`, `ntt_tail.S` | forward Good-Thomas NTT (eight banks) |
| `base.c`, `base_tables.h` | pointwise products in the transform domain |
| `inverse.c`, `baseinv_num.S`, `baseinv_finish.S` | batch inversion (key generation) |
| `basemul_rinv.S` | decapsulation first product, `R^-1` boundary, written in the inverse's (component, half) lane basis |
| `inverse_ntt.S`, `inverse9.S`, `inverse16.S`, `inverse16_tail.S`, `crepmod3_raw.S`, `inverse*_tables.h`, `invntt9_lane_tables.h` | decapsulation inverse NTT and the ternary reduction |
| `pack.c`, `codec_pairs.h` | canonical serialization |
| `unpack.S` | canonical decoding and range check, generated from `codec_pairs.h` |
| `support.c` | sampling, SOTP, `sub`, `triple` |
| `secure_clear.h` | clears and the SUPERCOP declassify annotation |

## Constant time and correctness

- SUPERCOP TIMECOP passes at `-O`, `-O2`, `-O3` and `-Os` (`TIMECOP=256`).
- The decapsulation inverse is proved overflow-free over the linked
  executable for every input the first product can produce, with the output in
  {-1, 0, 1} and every q-centering input within the range where the single
  correction is exact (interval analysis; `docs/VALIDATION.md`).

## Performance

Against the official implementation, `github.com/ntruplus/ntruplus` main at
3991b2a (2026-08-14), measured 2026-09-25: on Apple M2 Pro its default build
(SHA3 Keccak, `CE/`), on Cortex-A76 (Raspberry Pi 5, no FEAT_SHA3) its `NO_CE`
build.  SUPERCOP 20260831 carries the `NO_CE` build from an earlier snapshot
that differs from main only in `crepmod3.s`.  Both sides use the same harness
and compiler; medians of three sessions.  Details are in
`experiments/gt-p138-unified-margins/` on the development branch
`gt864-1152-cleanup`.

| | key generation | encapsulation | decapsulation |
|---|---:|---:|---:|
| M2 Pro, vs Official (default build) | -9.8% | -12.0% | -10.1% |
| Cortex-A76, vs Official (`NO_CE` build) | -15.0% | -22.2% | -18.8% |
| M2 Pro, Keccak permutation held equal | -6.1% | -6.9% | -6.6% |
| Cortex-A76, Keccak permutation held equal | -7.7% | -10.6% | -10.6% |

"Keccak permutation held equal" links Official's sponge against GT's
permutation (these two rows use the SUPERCOP revision of Official's code,
which times within 0.6% of main).  That margin is not the arithmetic alone: it
also contains GT's sponge code.  Separating the two (GT's arithmetic with
Official's sponge), the sponge is 69-97% of it on M2 and 42-69% on Cortex-A76;
the arithmetic is -15 to -130 ns an operation on M2 and -709 to -1,216 ns on
Cortex-A76.

## SUPERCOP leaf

```sh
python3 scripts/export_supercop.py DESTINATION
```

writes a leaf with a private namespace, `goal-constbranch` and
`goal-constindex`; `make export-check` confirms the export is deterministic.

`SOURCE-MANIFEST.sha256` freezes the accepted source closure. Development
generators, Slothy inputs, benchmark harnesses and raw performance logs remain
outside this directory.
