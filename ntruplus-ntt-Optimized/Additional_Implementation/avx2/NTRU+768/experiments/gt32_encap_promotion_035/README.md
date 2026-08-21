# GT32 Encap Promotion 035

This gate exports the selected 033B image independently, validates the
canonical KAT, and compares complete Keypair/Encap/Decap operations against
Official with the established fixed-ELF SUPERcop method.

Candidate source export:

```text
/home/nuc/src/exports/crypto_kem/ntruplus768/avx2-gt32-clean-033b-transform
```

The candidate is GT Clean table-GC plus 031 Encap, 034 Q24, and the explicitly
linked transform-island policy. GT Clean itself is not modified.

## Decision

**Do not promote 033B. GT Clean remains the production candidate.**

The small same-ELF transform-island gate measured a real local saving, but the
independent production-shaped export did not retain it.  In a direct fixed-ELF
comparison against freshly rebuilt GT Clean, 033B made Encap slower and also
slowed the source-identical Decap path.  That is decisive evidence that the
selected whole-image ordering perturbs executable delivery by more than the
local transform-island saving.

033B therefore remains a local scheduling reference only.  Do not continue
with linker padding, address sweeps, or hot-order tuning for this candidate.

## Correctness

- 100,000 deterministic functional trials: pass.
- canonical request SHA-256:
  `36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa`
- canonical response SHA-256:
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`

## Formal benchmark

Method: CPU 1, fixed prebuilt measure ELFs, 16 palindromic ABBA/BAAB blocks,
96 observations per operation per block.  Delta is second ELF minus first ELF;
negative is favorable to the second ELF.

### 033B versus Official

| ASLR | Operation | Delta cycles | Favorable blocks | Bootstrap median 95% CI |
|---|---:|---:|---:|---:|
| off | Keypair | -306.771 (-1.427%) | 16/16 | [-331.479, -282.063] |
| off | Encap | +189.135 (+0.675%) | 0/16 | [+173.479, +300.688] |
| off | Decap | -72.406 (-0.376%) | 16/16 | [-107.771, -34.083] |
| on | Keypair | -281.813 (-1.313%) | 16/16 | [-349.375, -260.104] |
| on | Encap | +180.458 (+0.644%) | 2/16 | [+89.646, +251.479] |
| on | Decap | -157.938 (-0.816%) | 15/16 | [-209.000, -56.458] |

### 033B versus fresh GT Clean

This is the causal control.  Both ELFs were built on the same day; GT Clean is
the first ELF and 033B is the second.

| ASLR | Operation | Delta cycles | Favorable blocks | Bootstrap median 95% CI |
|---|---:|---:|---:|---:|
| off | Keypair | -0.479 (-0.002%) | 9/16 | [-29.479, +38.438] |
| off | Encap | +93.833 (+0.333%) | 6/16 | [-23.896, +130.625] |
| off | Decap | +131.000 (+0.686%) | 1/16 | [+84.729, +174.708] |
| on | Keypair | -10.719 (-0.051%) | 9/16 | [-34.188, +21.146] |
| on | Encap | +34.198 (+0.121%) | 6/16 | [-33.740, +154.708] |
| on | Decap | +93.729 (+0.490%) | 3/16 | [+35.688, +131.635] |

The Encap confidence intervals include zero in the direct control, so there is
no production-level Encap win.  Decap is source-identical but regresses with a
strictly positive confidence interval in both address modes.  This isolates the
failure to whole-image delivery rather than the mathematical transform island.

## Fixed ELF identities

| ELF | SHA-256 | text bytes | rodata bytes |
|---|---|---:|---:|
| Official | `c7c1d482a0357fba85d14060196dccd08a616bbf1404ae5a72b24e86df91b217` | 42,007 | 5,384 |
| GT Clean | `2f2bf04b64bb023a2b2d6f44faaa3d1123991e3e96b9d87ce8cf4bfcfc458d88` | 64,343 | 21,576 |
| 033B | `2f9f8fc29ecd80d3a0a892400a11e9752887a3a2cb14714a931b61d5d1bcf3a0` | 64,119 | 21,704 |

Raw and analyzed evidence is in `results/`.  The 033B text total includes the
16,160-byte `.text.gt32.encap.transform` section plus 47,959 bytes of ordinary
`.text`.
