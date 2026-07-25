# Keygen Early-CQ Experiment

This directory contains a default-off experiment for keeping the NTRU+768
key-generation pointwise path in coefficient-major quartic (CQ) layout.

## Phase 1

The first candidate intentionally keeps the production forward NTT and its
block-major-to-BPQ endpoint:

```text
poly_ntt block-major
  -> production block-major-to-BPQ adapter
  -> one BPQ-to-CQ transpose
  -> CQ-input hierarchical base inversion
  -> scaled-R CQ inverse
  -> CQ x CQ quartic multiplication
  -> production CQ canonical pack
```

This isolates the value of an early persistent CQ boundary. It does not yet
claim the direct-CQ NTT store win; that requires a later NTT epilogue candidate.

The CQ lane order is the production transpose order:

```text
P0, P2, P4, P6, P1, P3, P5, P7
```

The existing `gt_keygen_bpq_lambda8` table already follows that order.

Production remains selected unless `GT_EXPERIMENT_USE_KEYGEN_ALL_CQ` is set.

See [phase1-results.md](phase1-results.md) for correctness, Pi 5 component
cycles, full-keygen replacement results, and the phase-2 decision gate.

## Phase 2

Phase 2 adds an independently selectable direct-BPQ forward-NTT endpoint:

```text
complete production Stage345 arithmetic
  -> one fixed-offset Q store per quartic pair
  -> BPQ-to-CQ transpose
  -> phase-1 CQ baseinv/basemul/pack
```

It removes the block-major-to-BPQ adapter, but it is not yet a direct-CQ
register endpoint. Enable it only together with the phase-1 backend:

```text
GT_EXPERIMENT_USE_KEYGEN_ALL_CQ
GT_EXPERIMENT_USE_KEYGEN_DIRECT_BPQ_ENDPOINT
```

The generated endpoint is namespaced and production remains unchanged. See
[phase2-direct-bpq-results.md](phase2-direct-bpq-results.md).

## Phase 3

Phase 3 eliminates the remaining BPQ-to-CQ memory boundary:

```text
complete production Stage345 arithmetic
  -> park 9 early outputs across 24 CQ groups
  -> in-register 4x8 transpose
  -> fixed-offset CQ stores
  -> CQ baseinv/basemul/pack
```

The liveness analyzer unifies `D/Q/V` aliases, preserves future CQ outputs as
semantic uses, and requires zero spill, zero reload, and zero recomputation.
All 24 groups pass. Enable the candidate only with:

```text
GT_EXPERIMENT_USE_KEYGEN_ALL_CQ
GT_EXPERIMENT_USE_KEYGEN_DIRECT_CQ_ENDPOINT
```

Direct-CQ is the selected serious all-CQ experiment candidate. It remains
default-off because the full binary still contains both generic and keygen CQ
NTT bodies. See [phase3-direct-cq-results.md](phase3-direct-cq-results.md).

## Phase 4

Phase 4 removes most of that duplicate NTT body without changing either
endpoint contract:

```text
generic entry OR direct-CQ entry
  -> one shared Phase123 body
  -> generic or CQ row suffix
  -> one shared epilogue/table copy
```

It removes 8,432 bytes of linked text relative to the separate-body all-CQ
binary. The shared direct-CQ entry costs four extra retired instructions and
about five cycles per NTT in the endpoint harness; full keygen remains about
2.57% faster than current production in the measured run. See
[phase4-shared-core-results.md](phase4-shared-core-results.md).

The current end-to-end route, production/candidate file ownership, KEM call
graph, and uniform-GC three-way KPQC/GT/CQ profile are consolidated in
[current-cq-route-status-and-benchmark.md](current-cq-route-status-and-benchmark.md).
