# Results

## Correctness

All gates pass:

- 768 impulse inputs;
- 1000 random centered polynomial pairs;
- raw `T -> M` Forward equality;
- byte-exact WIRE12 equality;
- raw 1536-byte B3 product-M equality;
- 1000 deterministic full Encap ciphertext/shared-secret comparisons;
- noncanonical public-key rejection equality.

No extra reduction or relaxed range contract was introduced.

## Executed-work ledger

| Region | Route delta | Retired-instruction delta | PMU core-cycle delta |
|---|---:|---:|---:|
| Forward M -> T | -144 | -144.0 | -85.5 |
| pack M -> pack T | -96 | -97.0 | -26.5 |
| B3 M,M -> M,T | +144 | +144.0 | +64.7 |
| Primitive sum | **-96** | **-97.0** | about **-47.3** |

The three generated leaves have zero stack references and zero push/pop
spills.  The T serializer retains the ordinary packet-store topology: 47
ordinary high-half stores and one safe final packet, with no per-tile
fragmented tail.  Packets must be emitted in increasing wire-offset order;
otherwise the intentional four-byte over-store corrupts a packet emitted
earlier.

## SUPERcop-style paired launch result

16 fresh ASLR-on launches per timing backend, pinned to CPU 1:

| Backend / region | Median candidate-control | 95% bootstrap CI | Favorable launches |
|---|---:|---:|---:|
| `default-perfevent` Forward | -85.55 | [-85.71, -85.39] | 16/16 |
| `default-perfevent` pack | -24.81 | [-25.26, -24.06] | 16/16 |
| `default-perfevent` B3 | +67.48 | [+67.04, +67.96] | 0/16 |
| `default-perfevent` primitive sum | **-42.91** | **[-43.64, -40.96]** | — |
| `default-perfevent` full Encap | **+37.94** | **[-6.06, +63.75]** | 5/16 |
| RDTSCP primitive sum | **-48.82** | **[-58.52, -46.13]** | — |
| RDTSCP full Encap | **+50.13** | **[-269.0, +423.38]** | 7/16 |

The independent fixed-process PMU corroboration reports full Encap
`+32.36` core cycles while retiring `-97.01` instructions.  Thus the
candidate really deletes the predicted movement work, but the deletion does
not survive the true caller context as a timing win.

## Decision

```yaml
GT32-ENCAP-PERSISTENT-T-101:
  correctness: PASS
  primitive_mechanism: PASS
  static_route_ledger: PASS
  primitive_cycle_sum: PASS
  full_encap: NO_CREDIT
  decision: CLOSED_FOR_SCOPE
  closed_scope:
    - Eh=M, Er=T
    - current-topology E0V Encap
    - immediate T-to-M conversion at B3 entry
    - current AVX2 target and production contracts
  production_modified: false
```

This is not an instruction-count rejection.  The candidate retires 97 fewer
instructions in complete Encap, yet measured core cycles are neutral-to-worse.
Reopening requires a new mechanism that absorbs the B3 conversion or changes
the consumer schedule; rescheduling the same persistent-T boundary is not
justified by these results.

