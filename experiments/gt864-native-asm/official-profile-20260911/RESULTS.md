# GT864 versus selected SUPERCOP Official profiler

## Result

The current GT864 production candidate is faster in Encaps, but remains slower
in Keygen and Decaps:

| operation | selected Official | GT production | GT delta | GT instructions | instruction delta |
|---|---:|---:|---:|---:|---:|
| Keygen | 44,299.625 | 46,389.875 | +2,090.250 (+4.72%) | 99,097.0 | +9,777.0 (+10.95%) |
| Encaps | 46,423.100 | 45,748.075 | -675.025 (-1.45%) | 125,568.2 | +4,750.0 (+3.93%) |
| Decaps | 40,753.325 | 43,366.125 | +2,612.800 (+6.41%) | 99,000.2 | +12,354.0 (+14.26%) |

These are medians of 252 clean observations per implementation and operation.
They are the authoritative end-to-end numbers.  Each of six processes collected
42 samples, with both implementation orders balanced across the campaign.

## Component diagnosis

The table below reports median net cycles per complete KEM operation.  A row can
contain multiple calls; `calls` gives the calls per operation.  The measured
PMU read-pair cost was subtracted once per call.

### Keygen

| component | Official cycles (calls) | GT cycles (calls) | GT delta |
|---|---:|---:|---:|
| BaseInv | 8,324.750 (2) | 10,429.750 (2) | **+2,105.000** |
| ToBytes, all variants | 3,273.000 (3) | 4,549.000 (3) | **+1,276.000** |
| Forward | 7,511.000 (2) | 6,786.000 (2) | -725.000 |
| BaseMul R0 | 4,854.000 (2) | 4,349.000 (2) | -505.000 |
| SHAKE sampling | 5,499.750 (2) | 5,526.000 (2) | +26.250 |
| hash_f | 13,257.500 (1) | 13,231.500 (1) | -26.000 |

BaseInv is the largest Keygen-only gap.  The ToBytes aggregate is also slower,
but the GT Forward and R0 BaseMul together recover about 1,230 cycles.

### Encaps

| component | Official cycles (calls) | GT cycles (calls) | GT delta |
|---|---:|---:|---:|
| ToBytes, all variants | 2,181.000 (2) | 3,147.575 (2) | **+966.575** |
| Forward | 7,513.000 (2) | 6,799.800 (2) | -713.200 |
| BaseMulAdd | 2,896.000 (1) | 2,170.000 (1) | -726.000 |
| FromBytes checked | 742.000 (1) | 725.050 (1) | -16.950 |
| hash_f + hash_g + hash_h | 31,865.400 (3) | 31,762.950 (3) | -102.450 |

GT wins clean Encaps despite the ToBytes gap because Forward and BaseMulAdd are
both materially faster.

### Decaps

| component | Official cycles (calls) | GT cycles (calls) | GT delta |
|---|---:|---:|---:|
| Inverse | 4,118.050 (1) | 7,013.950 (1) | **+2,895.900** |
| ToBytes, all variants | 2,178.000 (2) | 3,155.575 (2) | **+977.575** |
| Forward | 7,511.000 (2) | 6,781.325 (2) | -729.675 |
| BaseMul R0 + R-inverse | 4,167.000 (2) | 3,932.150 (2) | -234.850 |
| FromBytes checked | 2,233.075 (3) | 2,163.600 (3) | -69.475 |
| center-to-ternary (`Crepmod3`) | 477.000 (1) | 463.150 (1) | -13.850 |

Inverse is the dominant Decaps gap.  BaseMul R-inverse is effectively tied
(GT is +16.15 cycles), while R0 BaseMul, Forward, and FromBytes are already
faster than the selected Official implementation.

## Interpreting ToBytes

Official exposes one `poly_tobytes` implementation for every call.  GT exposes
separate full-normalization and small-range paths, so comparing only the GT
`ToBytes_full` row would be incorrect.  The required same-boundary totals are:

| operation | Official total | GT full | GT small | GT total | GT delta |
|---|---:|---:|---:|---:|---:|
| Keygen | 3,273.000 | 1,771.750 | 2,777.250 | 4,549.000 | +1,276.000 |
| Encaps | 2,181.000 | 1,773.925 | 1,373.650 | 3,147.575 | +966.575 |
| Decaps | 2,178.000 | 1,775.575 | 1,380.000 | 3,155.575 | +977.575 |

P5 remains the fastest verified GT ToBytes implementation.  P6 zero-scratch is
still rejected.  A new ToBytes campaign should reopen only after a static route
DAG removes roughly the previously measured 829 instructions and 101 reads.

## What this changes in the roadmap

1. Keep **Inverse CT feasibility** as the next global hard gate.  It addresses
   the largest Decaps component gap directly.
2. Keep **raw-Inverse-to-ternary** second, evaluated at the combined
   Inverse-plus-conversion and complete-Decaps boundaries.
3. Keep **new ToBytes routing search** third.  It is the shared remaining gap,
   but the rejected P6 architecture is not reopened without the static gate.
4. Retain **BaseInv numerator/finish kernel redesign** as a visible Keygen-only
   work item.  It is not allowed to displace the Decaps critical path silently.

Forward is not currently a bottleneck: two GT calls cost about 725--730 fewer
profiled cycles than two selected-Official calls in every KEM operation.

## Baseline and correctness evidence

- Target: Raspberry Pi 5 Cortex-A76, CPU 3, `ondemand` governor.
- Temperature: 58.2 C before and 60.9 C after; throttling stayed `0x0`.
- Official source:
  `/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.
- Official source identity was checked before compilation:
  `kem.c acb888a4...937c`, `symmetric.c a9ab4afb...7053`, and
  `api.h 1912c6a3...865`.
- This selected snapshot uses SHAKE256.  Its independent status as the latest
  upstream revision has **not** been verified.
- Both implementations were freshly rebuilt; no old target binary was reused.
- GT `test_kem` passed 64 round trips plus tampered-ciphertext rejection.
- GT KAT SHA-256 remained
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Each of six clean processes passed 100 exact cross-implementation KEM
  transcripts and 100 tampered-ciphertext comparisons.
- All 12 clean-versus-instrumented equivalence checks passed.

The component profiler is intentionally diagnostic: instrumentation perturbs
the binary and call boundaries, so component medians are not assumed to add
exactly to the clean total.  Full-KEM conclusions use only the clean PMU table.

Machine-readable statistics are in `results.json`; raw CSV and build logs are
kept in the gitignored `raw/` and `build/` directories.
