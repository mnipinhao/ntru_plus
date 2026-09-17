# Experiment 143 results

## Decision

`R_PACK_HASH_GEOMETRY_PRESERVING_PRODUCTION_PASS`

The direct `r_M -> WIRE12 -> hash_g` mechanism survives a production-shaped,
geometry-preserving integration.  Encap improves significantly with ASLR both
on and off.  Keypair and Decap remain statistically neutral.

This gate qualifies the implementation for a separate production promotion;
it does not modify the production source root.

## Static and correctness gates

- 86 shared control/candidate symbols: identical address, size, and bytes.
- 77 production-anchor KEM symbols: identical address, size, and bytes.
- Encap entry is unchanged; both input sections reserve 611 bytes.
- Existing E0V and QL2 tails remain at their production addresses.
- The new 120-byte helper occupies a page-aligned RX-only tail at `0x1e000` in
  both profiles; its machine bytes are identical.
- No RWX load segment.
- 1000 deterministic exact cases, 768 noncanonical public keys, immutable
  inputs, ASan/UBSan: PASS.
- KAT: 948402 bytes, SHA-256
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

## Formal SUPERcop-style benchmark

Candidate minus control, core cycles; 16 fresh paired launches:

| Regime | Operation | Mean delta | Median delta | 95% bootstrap CI | Candidate-faster blocks |
|---|---|---:|---:|---:|---:|
| ASLR on | Keypair | +11.06 | +1.00 | [-13.88, +39.95] | 8/16 |
| ASLR on | Encap | **-92.11** | **-68.75** | **[-190.00, -23.28]** | **14/16** |
| ASLR on | Decap | -5.38 | +5.25 | [-38.89, +28.36] | 8/16 |
| ASLR off | Keypair | +9.64 | +11.50 | [-6.45, +26.28] | 4/16 |
| ASLR off | Encap | **-57.06** | **-59.50** | **[-64.28, -50.17]** | **16/16** |
| ASLR off | Decap | +6.16 | +8.13 | [-11.55, +25.61] | 7/16 |

The Encap effect is the only stable operation-level change.  The large
ASLR-on outlier (`-710.25`) widens that CI, but the median, sign count, and the
ASLR-off result independently support the same conclusion.

## Mechanism

The control serializes `r` into the ciphertext buffer, then `hash_g` copies
those 1152 bytes into a private `1 || r` SHAKE input.  The candidate writes the
same canonical WIRE12 bytes directly to the private SHAKE input.  Ciphertext
serialization later in Encap remains unchanged.

Experiment 142 established the local/caller mechanism.  Experiment 143 adds
the missing production evidence: existing hot code and data do not move, and
unaffected KEM operations remain neutral.
