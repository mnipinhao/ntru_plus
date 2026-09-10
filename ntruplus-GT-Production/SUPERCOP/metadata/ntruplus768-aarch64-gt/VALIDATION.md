# Validation

Validation date: 2026-09-10.

## Identities

- GT Production source revision:
  `aad4167d66a1fab82ed39895cbd6729683c7f2b2`.
- Official source:
  `/home/pi/supercop-20260831/crypto_kem/ntruplus768/aarch64`.
- Official source tree hash:
  `6529e33b01163decbdb441a6b6b905a6ad66807c0f9da9ec924969847785cc03`.
- Materialized leaf tree hash used by the gate:
  `f12000cb930c9b5c00ca07b02a39b865fa9720d7305e1ec1a321bca7e5f9c23b`.
- KAT response SHA256 for both implementations:
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

`VALIDATION.md` is intentionally not covered by `SOURCE-MANIFEST.sha256` so
validation results can be appended without changing the executable leaf's
identity.

## Correctness and ABI

- The leaf built by compiling every top-level `.c` and `.s` with the current
  SUPERCOP cryptoint objects and supplied `crypto_kem.h`/`randombytes.h`.
- Required public symbols `crypto_kem_keypair`, `crypto_kem_enc`, and
  `crypto_kem_dec` were present.
- Retained NTRU+768 KAT request and response files matched byte-for-byte.
- Keygen, Encap, and Decap workloads completed with matching Official/GT sinks.
- Modified-ciphertext and noncanonical-public-key failure paths returned
  zeroed public outputs in both variants.
- The final package reproduced deterministically and every executable-leaf
  file passed `sha256sum -c SOURCE-MANIFEST.sha256`.
- Compiled Official and packaged CBD `.text` were byte-identical, SHA256
  `3ffab0818f8bf0fba8e764303fdbf85d39093d36070b2119f42134ce76a7ae4f`.
- Compiled Official and packaged centered-crepmod3 `.text` were byte-identical,
  SHA256
  `f0c07dddfad7113090f4bb77382dd5b670064295e6690c2cab198b797a7d4bea`.

## Raspberry Pi 5 performance gate

Host: `pi@100.99.191.9`, Linux AArch64 6.18.33+rpt-rpi-2712, GCC 14.2.0,
core 3. Each p50 uses 62 paired samples, 2,000 operations per sample and 100
warmups, in both execution orders. PMU values are medians of three alternating
100,000-operation runs. The host remained at `throttled=0x0`; temperature was
57.1 C to 65.3 C.

| Operation | Official p50 | GT-polynomial p50 | Cycles saved | Improvement |
|---|---:|---:|---:|---:|
| Keygen | 38,435 | 36,362 | 2,073 | 5.39% |
| Encap | 38,686 | 37,212 | 1,474 | 3.81% |
| Decap | 33,483 | 32,124 | 1,359 | 4.06% |

| Operation | Variant | Instructions | Loads | Stores | Backend stalls |
|---|---|---:|---:|---:|---:|
| Keygen | Official | 80,336.360 | 9,744.361 | 6,224.570 | 13,213.185 |
| Keygen | GT | 83,257.532 | 10,723.714 | 6,514.257 | 11,210.674 |
| Encap | Official | 103,956.661 | 14,557.247 | 8,627.460 | 8,820.744 |
| Encap | GT | 106,680.716 | 15,260.743 | 9,235.081 | 6,838.747 |
| Decap | Official | 72,248.661 | 9,141.428 | 5,524.146 | 11,124.070 |
| Decap | GT | 72,137.716 | 9,293.910 | 5,802.174 | 10,160.465 |

Linked workload text size is 21,617 bytes for Official and 81,529 bytes for
the materialized GT leaf. The speed improvement therefore trades roughly
59.9 KiB of additional text for lower backend stalls.

Full machine-readable results are retained in the E34 experiment record as
`materialized-gate-summary.json`. Raw build, KAT, paired-sample and PMU outputs
remain ephemeral on the Pi under
`/home/pi/gt768-official-shell-gt-poly-20260910-e34/materialized-gate-v1/raw/`.

## Header ownership cleanup revalidation

The internal transform declarations were consolidated into `ntt.h`, and the
unused C declaration of `gt_rowbitrev_lambda` was removed. The table has one
definition in `basemul_lambda.c`; `base.s` resolves that symbol at link time.

- Deterministic regeneration against the Official source above: pass.
- Mac and Pi release, KEM, ABI, canonical-boundary, small-input, zeroization,
  and KAT gates: pass.
- Pi baseline/candidate `.text` SHA256 (both):
  `eb05f6dea5ff904a5ef300f1b726a6b63f98bf4159c873ce9d968ed4c495f7db`.
- Pi baseline/candidate `.rodata` SHA256 (both):
  `ddd8fe041b3ec66891b3076b5de8e6aa84c371c150e4820797eda358bff524d7`.

Thus the cleanup changes header ownership and package structure only; linked
instructions and constant-table bytes are unchanged.
