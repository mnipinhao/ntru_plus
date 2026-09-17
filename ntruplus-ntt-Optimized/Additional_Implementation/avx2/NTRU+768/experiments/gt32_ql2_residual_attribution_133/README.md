# 133 — QL2 residual Encap attribution

This is a read-only profile of the exact Official and QL2 binaries built by
Experiment 132.  No implementation is rebuilt, relinked, or instrumented.

The primary total remains Experiment 132's native SUPERCOP stabilized-Q2
comparison.  Intel LBR call/return intervals are used only to describe direct
leaf costs inside Encap; their medians are not additive reconstruction of the
complete operation.  PMU sampling supplies a separate pressure/PC map.

The main question is where the remaining QL2-versus-Official Encap debt lands
after QL2 deleted 144 dynamically executed convergence routes.

Recorded campaigns:

- 128 balanced ASLR-on LBR blocks, `cpu_core/cycles/u`, period 50,000;
- 32 repetitions per image for cycles, IDQ-not-delivered, and L1D-pending
  sampling with LBR call-chain filtering.

Large raw `perf.data` captures are ignored.  Parsed evidence is retained in
`results/`.

