# GT32-ENCAP-DELIVERY-033A

032 proves that B3 final-store add-m removes 48 loads and 48 stores and wins
locally, but its saving disappears in full Encap. This experiment changes no
arithmetic. It asks whether executable address geometry participates in that
delivery loss.

## Controlled binaries

Eight non-PIE ELFs are generated. Each has the same 4096-byte B3 cage and the
same total ELF size (143720 bytes). Only `gt32_033_b3_addm` moves within its
page, to offsets:

```text
0 32 64 96 128 160 192 224
```

The inventory proves that all other selected hot addresses are identical
across all eight binaries, including the three callers, Decode, Frontend,
Forward, both Q24 boundaries, production B3, and hashes.

Every binary checks three byte-exact deterministic Encap paths before timing:

```text
A = current GT deterministic Encap
B = 031 four-polynomial Encap
C = 031 + 032 B3 final-store add-m
```

The final timing run uses the minimal (non-PMU) harness, one pinned core, 48
fresh launches per offset, rotating ABC/BCA/CAB order. Offset execution order
is also rotated every launch round so address is not aliased with wall-clock
drift.

## Fixed-address sweep

| B3 page offset | B-A median | C-B median | C-B favorable | C-B 95% CI |
|---:|---:|---:|---:|---:|
| 0 | -2.17 | +0.02 | 24/48 | [-42.46, +15.25] |
| 32 | +6.27 | +45.96 | 14/48 | [+23.79, +70.71] |
| 64 | +28.60 | +28.25 | 13/48 | [+12.83, +41.63] |
| 96 | -5.81 | +31.85 | 13/48 | [+12.60, +52.67] |
| 128 | +2.77 | +20.42 | 20/48 | [-8.08, +35.54] |
| 160 | +8.54 | +24.04 | 16/48 | [+1.75, +49.46] |
| 192 | +3.00 | +2.75 | 24/48 | [-25.50, +31.54] |
| 224 | +11.85 | +2.52 | 23/48 | [-14.48, +25.46] |

The same candidate ranges from neutral to about +46 core cycles solely as its
page offset changes. Offsets 32, 64, 96, and 160 are significantly worse.
No tested offset delivers the known local 032 saving through full Encap.

The B-A negative control is mostly neutral, as expected because neither path
executes the candidate. Its offset-64 anomaly is a warning that address alone
does not explain all launch/runtime variation. Therefore this gate establishes
address-sensitive delivery as a causal participant, not a complete DSB/I-cache
mapping model and not a production padding rule.

## Representative PMU

PMU uses separate instrumentation ELFs so its mode dispatch cannot perturb the
formal sweep. Each measurement performs 10000 calls; values below are median
candidate-minus-031 per call over eight paired launches.

| event | offset 0 | offset 128 |
|---|---:|---:|
| retired instructions | -131.00 | -131.00 |
| branches | -10.00 | -10.00 |
| branch misses | +1.83 | +1.94 |
| IDQ uops not delivered | +287.32 | +313.81 |
| L1I load misses | +0.078 | +0.050 |
| iTLB load misses | +0.001 | +0.001 |
| steady-state core cycles | +16.39 | -46.87 |

The workload deletion is real, but it comes with substantially worse IDQ
delivery and slightly more branch misses. L1I and iTLB misses do not explain
the effect. The steady-state cycle result does not reproduce the single-call
launch-level ordering, so PMU supports a frontend-delivery mechanism without
closing the exact event-to-latency attribution.

During methodology development, merely adding a dormant PMU mode to the
normal benchmark harness flipped the full-caller direction while arithmetic
and cage contents stayed unchanged. The final design therefore separates
minimal timing and PMU instrumentation into different ELFs. This observation
is further evidence that whole executable/harness shape can dominate a
20-cycle local optimization.

## Decision

- 032 remains a qualified local component, not production-selected.
- Simple B3 padding/alignment search is closed; there is no stable magic
  offset and no tested offset promotes the candidate.
- B3 arithmetic, M layout, Q24, and Forward remain frozen.
- If delivery work continues, the next bounded gate is 033B: explicitly split
  and order a small set of operation-hot sections (caller order versus shared
  transform cluster), with the minimal harness and the same A/B/C controls.
- `no-vzeroupper` remains deferred until section ordering is understood.

Evidence:

- `generated/address_inventory.json`
- `generated/benchmark.json`
- `generated/pmu.json`

Reproduce with `make check`, `make benchmark`, and `make pmu`.
