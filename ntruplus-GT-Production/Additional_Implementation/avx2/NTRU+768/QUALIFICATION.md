# QL2 and direct-r-hash production qualification

The current Encap path promotes the QL2 convergence architecture qualified in
experiments 103 and 104. The prior E0V path remains the matched control and
its helper remains in the image as a geometry anchor.

The promoted Encap path uses the existing caller order and replaces only:

```text
poly_add(product, message) -> materialized sum -> Q24(sum)
```

with:

```text
two-source Q24(product, message)
```

The sum remains a semantic M/e0 value but is never stored as a polynomial.
The selected frame contains four polynomial slots and is 6592 bytes. The
message slot is reused for coefficient production before its final NTT-domain
value is written; the frontend call is the lifetime boundary.

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
- `ntruplus768_ntt_ql2_avx2`, `ntruplus768_basemul_general_ql2_avx2`, and
  `ntruplus768_pack_ql2_sum_avx2` occupy `.ql2_tail` in that fixed order.
- `.ql2_tail` is separately page-aligned RX. The production audit compares the
  frozen E0V and QL2 callers in identical 611-byte slots.
- `ntruplus768_hash_g_from_m_avx2` occupies `.rhash_tail`, a third
  page-aligned RX section. The QL2 control and promoted direct-r-hash caller
  also use identical 611-byte slots.
- Both transitions verify at least 80 unchanged pre-existing symbols plus
  identical rodata.

Run the production-owned audit inside this source directory or an installed
SUPERcop export:

```sh
python3 qualified/build-supercop.py \
  --supercop-root /home/nuc/supercop-20260627
```

The command builds matched E0V, QL2, and QL2+r-hash measure ELFs and writes
`qualified/build/layout-audit.json`. It fails on symbol, rodata, caller-slot,
tail-alignment, or RX/RWX contract drift.

## QL2 promotion result (2026-09-16)

The production-owned audit checked 86 pre-existing symbols with zero address,
size, or byte mismatches. Both caller reservations are 611 bytes; `.e0v_tail`
is 4,914 bytes and `.ql2_tail` is 6,226 bytes. Both are page-aligned RX, rodata
is byte-identical, and the ELF has no RWX segment. Functional testing,
ASan/UBSan, and the canonical KAT pass. The 948,402-byte KAT response SHA-256
remains `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

## Direct-r-hash promotion result (2026-09-16)

Experiment 143 removed the redundant 1152-byte copy at the `r` hash boundary.
The production audit checks 86 common symbols for both E0V-to-QL2 and
QL2-to-r-hash transitions with zero mismatches. All three caller reservations
are 611 bytes; the new helper is 120 bytes in a page-aligned RX-only tail.
KAT, deterministic/noncanonical testing, and sanitizer testing pass.

The matched production A/B improves Encap by about 57--92 core cycles while
Keypair and Decap remain neutral. The Official comparison in experiment 144
places Encap at statistical parity with ASLR enabled and about 127 cycles
behind with ASLR disabled. Promotion is therefore justified by the causal A/B
result, not by a claim that all three operations beat Official in every
placement regime.

The formal Official comparison is recorded in
`experiments/gt32_ql2_production_139`. QL2 is now the production GT Encap path;
promotion is an explicit policy choice even though Encap remains slower than
Official in the current image.

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

## Frame trim qualification (094)

The phase-controlled F0/FP/F1 campaign proved a four-polynomial lifetime
lower bound and reduced the frame from 8128 to 6592 bytes. In the
phase-matched comparison, Encap was `-19.375` cycles with ASLR enabled and
`+4.125` cycles with ASLR disabled; both bootstrap intervals crossed zero.
The trim is therefore promoted as a performance-neutral 1536-byte stack
reduction, not as a timing optimization.
