# Experiment 133 results

## Formal total

Experiment 132 remains the authoritative full-operation measurement.  In its
primary ASLR-on campaign QL2 Encap was `+87.26` cycles slower than Official,
with paired bootstrap 95% CI `[+42.21,+164.88]`.  The ASLR-off corroboration
was `+181.99`, CI `[+134.94,+218.35]`.

## Direct leaf intervals

The following values are medians of per-launch LBR call/return intervals over
128 balanced launches.  Deltas are `QL2 - Official` in core cycles.

| semantic region | Official | QL2 | delta |
|---|---:|---:|---:|
| Decode public key | 171.00 | 201.00 | **+30.00** |
| CBD(r) | 119.00 | 144.00 | **+25.00** |
| r producer | 726.00 | 677.25 | **-48.75** |
| serialize r-hat | 212.00 | 257.00 | **+45.00** |
| SOTP(m) | 126.00 | 139.00 | **+13.00** |
| m producer, including QL2 landing | 725.50 | 595.50 | **-130.00** |
| QL2 general BaseMul | 525.25 | 538.00 | **+12.75** |
| sum and final ciphertext serializer | 259.00 | 239.00 | **-20.00** |
| descriptive mapped-leaf total | 2863.75 | 2790.75 | **-73.00** |

The mapped total is descriptive and cannot be subtracted from the full Encap
delta to create a fictitious caller or Hash component.  LBR coverage, nested
calls, overlap, branch-history visibility, and sampling skid prevent additive
full-operation accounting.

## What QL2 changed

The comparison with the E0V profile in Experiment 127 is unusually clean:

| region | E0V delta vs Official | QL2 delta vs Official | QL2 movement |
|---|---:|---:|---:|
| m producer | -45.50 | -130.00 | **-84.50** |
| general BaseMul | -14.00 | +12.75 | +26.75 |
| final sum/serializer | +16.00 | -20.00 | **-36.00** |
| mapped-leaf total | +21.75 | -73.00 | **-94.75** |

This approximately 95-cycle movement matches the independently measured QL2
credit in Experiments 103/104.  It confirms that QL2 did exactly what it was
designed to do: move presentation work into producer/consumer-native places
and delete 144 dynamically executed convergence routes.  The gain is not a
faster quartic multiplication; the QL2 BaseMul interval is about 13 cycles
slower than Official and about 27 cycles less favorable than the previous M
BaseMul comparison.

The unaffected left side is also stable relative to Experiment 127: Decode,
CBD, r producer, r serializer, and SOTP move by only roughly 0--3 cycles.
This is evidence that the QL2 attribution is localized rather than a profiler
artifact spread across the whole caller.

## PMU pressure map

Sampling with LBR call-chain filtering produced:

| event | Official | QL2 | interpretation |
|---|---:|---:|---|
| visible cycle samples | 1808 | 2411 | coverage, not total operation cycles |
| estimated IDQ-not-delivered events/Encap | 420.41 | 373.37 | no broad QL2 frontend-delivery excess |
| L1D-pending samples | 22 | **103** | QL2 retains a strong data/load-pressure signal |
| estimated L1D-pending cycles/Encap | 3.58 | **16.76** | directional estimate, not a cycle budget |

QL2-side pending samples concentrate at:

| symbol | samples | share of QL2 pending samples |
|---|---:|---:|
| `ntruplus768_ntt_frontend_avx2` | 27 | 26.2% |
| `ntruplus768_unpack_m_body_avx2` | 25 | 24.3% |
| `ntruplus768_basemul_general_ql2_avx2` | 14 | 13.6% |
| `ntruplus768_ntt_m_avx2` | 12 | 11.7% |
| `ntruplus768_ntt_ql2_avx2` | 8 | 7.8% |

The frontend counter is lower for QL2, so Experiment 132's remaining loss
cannot be summarized as a broad DSB/MITE failure.  The persistent PMU clue is
data dependency/load pressure, especially Decode, frontend, and the two B3
input paths.  The absolute sample count is small and cannot justify assigning
dozens of exact cycles to any one symbol.

## Decision

QL2 remains the Encap research champion, and its convergence island should be
frozen.  The remaining direct leaf debts are r serialization (`+45`), Decode
(`+30`), CBD (`+25`), SOTP (`+13`), and QL2 BaseMul (`+12.75`).  None is a
new 90--180-cycle owner:

- r serialization and range-only simplifications were already bounded by the
  serializer and D1 campaigns;
- Decode residency did not qualify for Encap in the earlier load-to-compute
  campaign;
- CBD is byte-identical arithmetic whose stack-offset search was closed;
- virtual QL2 product materialization was closed by Experiment 105;
- Hash remains closed and is not implicated by this profile.

Therefore Experiment 133 identifies no honest next local rewrite capable of
claiming the full residual.  Reopening a component now requires a new
operation-class deletion or a concrete load-dependency mechanism, not another
schedule, range-only reducer, or placement sweep.  Production remains
unchanged.
