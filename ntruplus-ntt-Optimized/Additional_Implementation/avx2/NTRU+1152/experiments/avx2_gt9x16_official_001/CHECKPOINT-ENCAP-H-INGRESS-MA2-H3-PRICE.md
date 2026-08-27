# ENCAP-H-INGRESS-MA2-H3-PRICE

This checkpoint prices H3 at exactly the boundary it changes: valid public-key
bytes plus resident Natural-Q `r`/`m` states to the raw Natural-Q scale-4 MA2
output. Ciphertext serialization and native KEM execution are outside the
timed region.

## Direct controls

The fixed-ELF measure contains three aligned wrappers:

```text
current: PK bytes -> Official poly_frombytes -> cumulative h projection/MA2
H1:      PK bytes -> Natural-Q decode -> resident h -> preprojected MA2
H3:      PK bytes -> streaming decode/validate/MA2
```

Untimed preflight requires all three reject values to be zero and all 2304
output bytes to be raw bit-exact. Inputs are reset outside each timed batch.
The measure uses SUPERCOP `cpucycles()`, aligned allocation, source layout,
compiler pipeline, and machine detection, so this is SUPERCOP-derived rather
than native SUPERCOP KEM data.

## Serious fixed-ELF result

The campaign uses fixed-common O3GC, CPU 2, 96 observations per label per fresh
launch, balanced first/second order, and nine fresh launches for each
placement/ASLR setting. Normal placement was predeclared by
ENCAP-CALLER-ATTRIBUTION-V2; it was not selected from this campaign.

| Setting | H3 - current | H3 - H1 | launch direction |
| --- | ---: | ---: | --- |
| normal, ASLR off | -60.00 | -104.33 | 9/9, 9/9 |
| **normal, ASLR on (headline)** | **-58.23** | **-103.85** | **9/9, 9/9** |
| reversed, ASLR off | -59.96 | -107.46 | 9/9, 9/9 |
| reversed, ASLR on | -57.83 | -105.63 | 9/9, 9/9 |

All eight bootstrap 95% confidence intervals are below zero. ASLR-off has one
runtime-address tuple per placement; ASLR-on has nine.

H3 turns removal of 72 resident-h stores and 72 reloads into a real machine
win. H1 is about 46 cycles slower than the current Official-decode/projection
path at this boundary, so the formal caller credit is about 58 cycles, not the
full earlier h-side attribution. Remaining cost includes consumer-required
lane formation and must not be attributed to resident-h materialization.

This freezes H3 as the research PK-ingress/MA2 baseline. It does not promote a
KEM implementation and no native KEM number was produced.
