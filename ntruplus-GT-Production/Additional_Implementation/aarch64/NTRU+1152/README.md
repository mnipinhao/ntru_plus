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

Against SUPERCOP 20260831's `ntruplus1152/aarch64` (2026-09-23; details in
`experiments/ROADMAP-m2-delivery.md` on the development branch
`gt864-1152-cleanup`):

| | key generation | encapsulation | decapsulation |
|---|---:|---:|---:|
| M2 Pro, vs Official + CryptoExtension | -9.5% | -11.9% | -9.6% |
| M2 Pro, Keccak held equal | -6.1% | -6.7% | -5.8% |
| Cortex-A76, Keccak held equal | -6.9% | -9.6% | -8.8% |

"Keccak held equal" links Official's sponge against GT's permutation, so the
margin is the arithmetic alone.  Three later codec changes are not
included: the store order of `tobytes` (0.4% on Cortex-A76, none on M2), its
`add` + `umin` canonicalisation (0.4-0.5% on Cortex-A76, 11 ns on M2), and the
two-register `tbl` decoder in `unpack.S` (decapsulation -0.9% on M2, -1.0% on
Cortex-A76).

## SUPERCOP leaf

```sh
python3 scripts/export_supercop.py DESTINATION
```

writes a leaf with a private namespace, `goal-constbranch` and
`goal-constindex`; `make export-check` confirms the export is deterministic.

`SOURCE-MANIFEST.sha256` freezes the accepted source closure. Development
generators, Slothy inputs, benchmark harnesses and raw performance logs remain
outside this directory.
