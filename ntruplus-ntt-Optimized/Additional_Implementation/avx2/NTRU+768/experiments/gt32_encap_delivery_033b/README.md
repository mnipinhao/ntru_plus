# GT32 Encap Delivery 033B

This experiment freezes the 031 four-polynomial caller, current B3, and the
034 unsigned-min Q24 body. It changes only the order of selected hot text
sections. GT Clean is not modified.

The four predeclared policies are current linker order, transform island,
Q24-centered, and arithmetic-first. Each policy is a control/candidate
fixed-address ELF pair; the only pair-local difference is the Q24 canonical
tail (old three instructions versus 034 two instructions). The 5120-byte Q24
cage keeps every common symbol address unchanged.

## Linker-policy correction

The first draft linker scripts named function sections for `ntt.s`, `ntt_m.s`,
and `basemul.s`, but those selected assembly functions live in object-wide
`.text`. The address manifest exposed that the objects had not moved. Those
measurements were discarded. The final scripts use object-qualified `.text`,
and `tools/inventory.py --check` now also proves the intended semantic order.

Every final control/candidate pair has 101 common defined symbols and zero
moved symbols. The current pair is 134,640 bytes per ELF; each explicitly
ordered pair is 134,720 bytes. Deterministic ciphertext/shared-secret equality
passes for every pair.

## Corrected 48-launch result

Candidate minus control, using SUPERcop `default-perfevent` core cycles:

| order | median | favorable launches | bootstrap 95% CI | MAD | AB / BA |
|---|---:|---:|---:|---:|---:|
| current | -55.375 | 30/48 | [-128.458, +6.208] | 117.479 | -72.396 / -54.854 |
| **transform island** | **-35.292** | **36/48** | **[-52.000, -29.083]** | **37.563** | **-25.063 / -46.917** |
| Q24-centered | -14.729 | 30/48 | [-46.083, +16.521] | 57.083 | -12.521 / -27.771 |
| arithmetic-first | -1.375 | 26/48 | [-18.833, +27.042] | 61.813 | -9.417 / +0.625 |

Transform island is the only order with both AB and BA negative and a
bootstrap interval wholly below zero. No additional Order E/F/G was searched.

## 24-launch PMU confirmation

All orders retain the exact `-96` retired-instruction change. Median
candidate-minus-control values per Encap:

| order | core cycles | IDQ uops not delivered | L1I misses | iTLB misses |
|---|---:|---:|---:|---:|
| current | +58.012 | +118.346 | +0.033 | +0.0084 |
| **transform island** | **-60.882** | **+17.144** | **-0.010** | **-0.0004** |
| Q24-centered | +30.523 | +53.959 | +0.005 | +0.0004 |
| arithmetic-first | -42.146 | +14.276 | -0.015 | -0.0004 |

Arithmetic-first has a favorable aggregate PMU median but fails the 48-launch
paired gate. Transform island is the only policy that passes both bodies of
evidence; its small IDQ increase is not the hundreds-of-uops regression seen
in the prior delivery failure.

## Predeclared factorial confirmation

The selected transform policy was then applied to:

- A: current GT Clean Encap;
- B: 031 + 034 + transform island;
- C: B + 032 B3 final-store add-m.

A and B have identical addresses for every recorded hot symbol. Across 48
fresh launches, B-A is `-34.917` core cycles, 39/48 favorable, with 95% CI
`[-56.667,-26.042]`; 24-launch PMU reports `-76.893` cycles and `-96.000`
instructions per Encap. This confirms the selected B image.

The first separate-ELF C-B result was anomalously large (`-342.083` cycles).
The address manifest showed that C moved the remaining hot island by 32 bytes,
and PMU showed an implausibly large `-1109.994` IDQ-undelivered change. It is
therefore recorded as a geometry effect, not 032 arithmetic credit.

032 was rechecked in one fixed ELF with matched normal/reversed function cages
under the transform policy and the 034 Q24 body:

| placement | local B3+add+Q24 | favorable | full Encap | favorable | full 95% CI |
|---|---:|---:|---:|---:|---:|
| normal | -15.813 | 32/32 | -11.146 | 17/32 | [-40.021,+16.875] |
| reversed | -15.937 | 32/32 | -12.354 | 17/32 | [-66.438,+30.750] |

Thus 032 remains locally real but is not delivered through full Encap.

## Decision

`transform island` is the selected 033B policy, and B (`031 + 034`) is the
algorithmically and delivery-qualified experimental Encap image. 032 remains
closed for production. GT Clean is intentionally unchanged; promotion into a
clean production export requires a separate explicit step.

Machine-readable evidence is in `generated/address_manifest.json`,
`benchmark.json`, `pmu.json`, `factorial*.json`, and `correctness.json`.
Reproduce with `make check benchmark pmu factorial recheck032`.
