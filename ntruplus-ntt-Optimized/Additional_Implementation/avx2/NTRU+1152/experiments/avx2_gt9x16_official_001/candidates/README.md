# NTRU+1152 AVX2 GT candidate sources

Flat SUPERCOP implementation trees preserved in Git so a candidate can be
rebuilt without a disposable SUPERCOP campaign.

## `avx2-gt9x16-wire-h3-pairunpack-serializer-v2-exp017-sc20260831`

Best NTRU+1152 GT candidate at the 2026-09-23 pause (Encap only; Keygen and
Decap use the Official path).

- Extracted from `supercop-campaign-unified-20260920-001/crypto_kem/ntruplus1152/avx2-gt9x16-wire-h3-pairunpack-serializer-v2-exp017-sc20260831`
  (local archive `/home/nuc/src/ntruplus-experiment-archive-20260922/supercop-campaigns/supercop-campaign-unified-20260920-001.tar.zst`).
- Byte-identical to the tree measured in the 2026-09-20 Native run:
  `SHA256SUMS` sha256 `285330f5c030ea59efe7b83714cfa74631b943543f7d219f6a6902aefc6e73c9`,
  `SOURCE-MANIFEST.json` sha256 `414f58f33e90cb804e4366202433600020b0b0e577772654b93e0944b3be66a5`
  (`results/ntruplus-avx2-768-864-1152-20260920/native/1152-exp017/metadata.json`).
  Run `sha256sum -c SHA256SUMS` inside the directory to verify.
- Gates (2026-09-20): 100/100 byte-exact frozen KAT, ASan/UBSan KAT, public API
  checks (`results/ntruplus-avx2-768-864-1152-20260920/{kat,sanitize,api}-1152-exp017.json`).
- Native SUPERCOP 20260831, Core Ultra 7 155H, StQ2 vs Official: keypair +308.00,
  enc +884.53 (+2.06%, 0/9 faster), dec +29.92
  (`docs/ntruplus-avx2-768-864-1152-benchmark-202609.md`). Not promoted.

To measure it again, copy the directory into a disposable SUPERCOP working copy
under `crypto_kem/ntruplus1152/`; never into a pristine snapshot.
