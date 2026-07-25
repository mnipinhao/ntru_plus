# Keygen All-CQ Phase 2: Direct-BPQ NTT Endpoint

Date: 2026-07-22

Branch: `codex/aarch64-keygen-all-cq`

Status: correctness and Pi 5 performance gates pass; default-off serious
experiment candidate. Production default is unchanged.

## Scope

This phase changes only the production forward NTT's final memory endpoint.
Phase123, Stage12, Stage345 arithmetic, modular reduction, register allocation,
and scalar address stream are unchanged.

For each of the 96 complete Stage345 Q outputs, the old split stores:

```text
low D -> branch-0 block-major
high D -> branch-1 block-major
```

are replaced by one fixed-offset Q store in the existing keygen BPQ order.
The external block-major-to-BPQ conversion is then removed from the two keygen
NTT sites. BPQ-to-CQ remains, so this is not a direct-CQ endpoint yet.

The exact 96-site contract and source/output hashes are recorded in
`direct_bpq_endpoint_map.json`. The generator rejects a production source hash
or store shape it cannot map exactly.

## Correctness and ABI

Pi 5 differential against:

```text
production poly_ntt
  -> production block-major-to-BPQ oracle
```

Results:

```text
1000 differential cases
direct output mismatches = 0
in-place mismatches       = 0
ABI-sentinel mismatches   = 0
ABI mask                  = 0x0
full KEM count            = 0
```

The first generated map failed differential because textual store order is not
k32 order. A unique 8-lane record matcher recovered the actual schedule order:

```text
block0 BPQ slots: 0,1,3,2,4,5,6,7
block1 BPQ slots: 8..15
block2 BPQ slots: 16,17,18,19,20,22,21,23
block3 BPQ slots: 25,24,26,27,28,29,30,31
```

The same permutation holds for all three rows and is frozen in the generator.

## Direct Endpoint PMU

Pi 5 Cortex-A76, core 3 pinned, Linux grouped `perf_event_open`, 61 samples x
20000 calls. Values are medians from one same-binary three-way run.

| Endpoint | Cycles | Instructions | CPI |
|---|---:|---:|---:|
| production raw block-major NTT | 2592.03 | 3701 | 0.7004 |
| production NTT + block-major-to-BPQ | 3179.17 | 5555 | 0.5723 |
| direct-BPQ NTT | 2578.41 | 3521 | 0.7323 |

Direct BPQ is 13.62 cycles faster than the raw production NTT and 600.90
cycles faster than the equivalent production BPQ endpoint. It also retires
180 fewer instructions than the raw NTT, exactly matching the removed
high-half store instructions across three rows.

This corrects the phase-1 cost interpretation:

- approximately 163 cycles per polynomial was the separate BPQ-to-CQ step;
- approximately 601 cycles per polynomial is the block-major-to-BPQ step
  removed here.

## Keygen Components

Pi 5, portable NO_CE hash, 31 samples x 2000 calls. Values are medians.

| Component | Mixed production | Direct-BPQ all-CQ | Delta |
|---|---:|---:|---:|
| sample NTT f, including selected endpoint | 3305 | 2941 | -364 |
| sample NTT g, including selected endpoint | 3309 | 2922 | -387 |
| baseinv actual | 4043 | 3946 | -97 |
| basemul actual | 1662 | 1762 | +100 |
| baseinv + basemul | 5705 | 5708 | +3 |
| public pack | 566 | 566 | 0 |
| secret f pack | 605 | 566 | -39 |
| secret hinv pack | 568 | 566 | -2 |

The pointwise budget remains flat. The measured keygen gain is attributable to
the two NTT/layout endpoints and the CQ secret-f pack contract.

## Full Keygen

Replacement binaries use identical linker garbage collection, deterministic
inputs, core 3 pinning, 61 samples x 2000 keypairs, and 200 warmups.

| Variant | Median cycles |
|---|---:|
| mixed production, run 1 | 37712 |
| mixed production, run 2 | 37750 |
| direct-BPQ all-CQ | 36935 |

The candidate saves 777 to 815 cycles, or 2.06% to 2.16%. Using the midpoint
of the two production runs gives approximately 796 cycles / 2.11%.

Retired instructions:

| Variant | Instructions |
|---|---:|
| mixed production | 86069 |
| direct-BPQ all-CQ | 81942 |

The candidate retires 4127 fewer instructions, a 4.79% reduction.

## Code Size

With identical linker garbage collection:

| Replacement binary | Text bytes |
|---|---:|
| mixed production | 89737 |
| phase-1 all-CQ | 83425 |
| direct-BPQ all-CQ | 100497 |

The direct-BPQ replacement is 10760 bytes larger than production because the
binary still needs generic `poly_ntt` for encapsulation/decapsulation and adds
a second namespaced NTT body for the keygen BPQ endpoint. Both NTT symbols are
64-byte aligned in the measured binary:

```text
poly_ntt                         size 0x39b8
gt_experiment_poly_ntt_to_bpq   size 0x36e8
```

This is the current promotion blocker even though keygen cycles improve.

## Decision

Keep this as the audited direct-BPQ reference, default-off. Phase 3 direct-CQ
supersedes it as the selected serious all-CQ experiment candidate. Do not yet
replace GT production.

The next gate should address one of these without mixing both initially:

1. Direct-CQ register endpoint: completed in Phase 3.
2. Shared-core/code-size design: share Phase123/Stage12 and branch only into
   generic versus BPQ/CQ Stage345 endpoint tails, avoiding two full NTT bodies.

Direct CQ requires a liveness-aware four-output parking/transpose contract;
the current Stage345 schedule overwrites early output registers before each CQ
group is complete. Phase 3 implements and validates that contract.
