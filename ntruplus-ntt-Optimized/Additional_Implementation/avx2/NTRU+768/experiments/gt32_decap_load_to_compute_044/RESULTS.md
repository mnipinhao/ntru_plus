# GT32 Decap Load-to-Compute 044 Results

## Decision

The 043 Decap win is real for that exact image, but the proposed multiplicity
decomposition was only partly correct:

- Decode mask residency does **not** retain a measurable full-Decap benefit.
- Scale-B3 preload is directionally favorable but not independently significant.
- General-B3 preload is the only independently qualified Decap component.
- Combining both B3 preloads wins, but does not beat general-only within the
  precision needed to justify the extra selection.

The next production gate should therefore instantiate a Decap-private general-
B3 preload symbol and leave Encap on Clean general-B3.  The complete DB image is
not selected.

## Method

Profiles:

| Profile | Decode | Scale B3 | General B3 |
|---|---|---|---|
| A | Clean | Clean | Clean |
| D | resident mask | Clean | Clean |
| S | Clean | preload | Clean |
| G | Clean | Clean | preload |
| DS/DG/SG/DSG | corresponding combinations | | |

All eight profiles passed the canonical 100-vector KAT byte-exact.  The source
variants retain equal function sizes.  For the decisive gate, equal-length
machine-code ranges were transplanted into the frozen 043 DB ELF so that all
profiles have identical addresses, section sizes, non-code bytes, and caller
geometry.  `DSG` is byte-for-byte identical to the original 043 DB ELF.

An early 044 run used an incorrect parser that treated SUPERcop deviations as
absolute cycle values.  Those JSON files are quarantined under
`results/invalid-parser/` and are not evidence.  All results below use the
correct `base + deviation` decoding.

## 128-block full factorial diagnostic

Decap relative to A:

| Profile | Paired median cycles | Favorable blocks | Bootstrap 95% CI |
|---|---:|---:|---:|
| D | +4.50 | 57/128 | [-8.00, +16.00] |
| S | -9.50 | 79/128 | [-24.00, -5.00] |
| G | -22.25 | 77/128 | [-30.25, -2.75] |
| DS | -12.25 | 75/128 | [-31.75, +1.00] |
| DG | -31.75 | 82/128 | [-47.75, -14.50] |
| SG | -16.25 | 85/128 | [-30.25, -6.25] |
| DSG | -34.25 | 90/128 | [-42.75, -19.50] |

This first showed that B3, not Decode multiplicity, supplies the structural
credit.

## 256-block B3 adjudication

Decap relative to A:

| Profile | Paired median cycles | Favorable blocks | Bootstrap 95% CI |
|---|---:|---:|---:|
| S | -11.25 | 141/256 | [-22.00, +3.50] |
| G | **-28.00** | **169/256** | **[-40.00, -19.00]** |
| SG | -26.25 | 170/256 | [-33.50, -17.50] |

General-only is the smallest independently significant candidate.  Scale-only
does not pass, and adding Scale to General does not improve the median.

The same gate's negative controls show why tiny image-level differences must not
be overinterpreted: Keypair, which executes neither M scale nor M general B3,
still moved by medians around 8--10 cycles with confidence intervals crossing
zero.  The General Decap effect is substantially larger and its CI is wholly
negative.

## Decode decision

In a 256-block A/SG/DSG finalist gate:

- SG vs A Decap: -23.75 cycles, CI [-31.25, -18.00].
- DSG vs A Decap: -32.75 cycles, CI [-41.00, -24.00].
- Direct DSG vs SG: -4.25 cycles, CI [-16.00, +4.00].

Thus Decode cannot claim incremental credit once B3 is present.  Its local 041
win remains a mechanism result, but it is not selected for the Decap-specific
production image.

## Relation to 043

Re-running the original 043 three-way method reproduced approximately -44
Decap cycles for DB versus Clean.  A pure two-way A/DSG gate on the fixed 043 DB
mother image measured -32 cycles, CI [-40.5, -26.0].  The remaining difference
is whole-image/measurement interaction, not a reason to allocate it to Decode.

The conservative production claim is therefore:

> In the fixed 043 geometry, Decap-private general-B3 qinv preload contributes
> about 28 cycles and is the only independently qualified 044 component.

## Artifacts

- `generated/fixed043db_manifest.json`: exact patched-image ranges and hashes.
- `generated/fixed043db_geometry.json`: fixed-address audit.
- `results/fixed043db-factorial-128-corrected.json`: full factorial diagnostic.
- `results/fixed043db-b3-factorial-256.json`: decisive B3 gate.
- `results/fixed043db-finalists-256.json`: SG/DSG finalist gate.
- `results/fixed043db-pair-256-corrected.json`: pure A/DSG pair gate.
