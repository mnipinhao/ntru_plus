# E0V production qualification

The promoted Encap path uses the existing caller order and replaces only:

```text
poly_add(product, message) -> materialized sum -> Q24(sum)
```

with:

```text
two-source Q24(product, message)
```

The sum remains a semantic M/e0 value but is never stored as a polynomial.
The existing five-polynomial, 8128-byte frame is deliberately unchanged.

## Executable-layout contract

- `ntruplus768_enc_derand_impl` starts at the pre-E0V address.
- Its input-section reservation remains 611 bytes. The E0V function symbol is
  596 bytes and 15 unreachable padding bytes remain in that reservation.
- `ntruplus768_pack_m_sum_highrange12699_avx2` is isolated in `.e0v_tail`.
- `.e0v_tail` is page-aligned and executable/read-only, never writable.
- Pre-existing hot text symbols and `.rodata` must remain address- and
  byte-identical to the geometry reference.
- The helper's exact byte size is not a permanent invariant; isolation,
  alignment, permissions, and non-movement of the existing image are.

Run the production-owned audit inside this source directory or an installed
SUPERcop export:

```sh
python3 qualified/build-supercop.py \
  --supercop-root /home/nuc/supercop-20260627
```

The command builds matched pre-E0V and E0V measure ELFs and writes
`qualified/build/layout-audit.json`. It fails on symbol, rodata, caller-slot,
tail-alignment, or RX/RWX contract drift.

## Promotion result (2026-08-27)

The independently installed export `avx2-gt32-clean-e0v-093` reproduced the
82-symbol layout audit and canonical KAT. A 16-block, fixed-ELF, ABBA/BAAB
SUPERcop-style comparison produced these paired-block median deltas:

| Mode | Keypair | Encap | Decap |
|---|---:|---:|---:|
| ASLR on | +11.750 | **-32.375** | +1.125 |
| ASLR off | -1.625 | **-42.500** | +2.750 |

Median-bootstrap 95% confidence intervals were:

| Mode | Keypair | Encap | Decap |
|---|---:|---:|---:|
| ASLR on | [-18.25, +40.75] | **[-82.125, -0.75]** | [-17.25, +26.25] |
| ASLR off | [-13.75, +8.75] | **[-57.0, -15.5]** | [-6.25, +17.5] |

Thus only Encap has a stable improvement; Keypair and Decap remain neutral.
The canonical 948,402-byte response SHA-256 is
`22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.
